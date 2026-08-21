"""Load both fraud CSVs into transactions_raw, in chunks.

Streams the ~480MB of source data through memory 50k rows at a time and
bulk-loads each batch with PostgreSQL's COPY - the fast path, roughly 50x
quicker than row-by-row INSERTs. Zero-signal columns are dropped in pandas
before they ever reach the database (the free-tier disk is ~1GB, so every
stored byte has to earn its place). Aborts if the table already has rows,
so an accidental rerun can't create duplicates.
"""

import os
from io import StringIO

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

FILES = ["data/fraudTrain.csv", "data/fraudTest.csv"]
CHUNK_SIZE = 50_000

# CSV columns we never store: row index, names, street address (zero
# analytical signal) and unix_time (duplicate of the timestamp).
DROP_COLS = ["Unnamed: 0", "first", "last", "street", "unix_time"]

# Kept columns, renamed to schema order. COPY maps CSV fields to table
# columns positionally, so this order must match 01_schema.sql exactly.
KEEP_ORDER = [
    "trans_date_trans_time", "cc_num", "merchant", "category", "amt",
    "gender", "dob", "job", "city", "state", "zip", "city_pop",
    "lat", "long", "merch_lat", "merch_long", "trans_num", "is_fraud",
]

COLUMNS = (
    "trans_time, cc_num, merchant, category, amt, gender, dob, job, city, "
    "state, zip, city_pop, lat, long, merch_lat, merch_long, trans_num, is_fraud"
)

COPY_SQL = f"COPY transactions_raw ({COLUMNS}) FROM STDIN WITH CSV"


def load_file(path: str, cursor) -> int:
    """Stream one CSV into the raw table in CHUNK_SIZE batches."""
    total = 0
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE, dtype={"zip": str, "cc_num": str}):
        slim = chunk.drop(columns=DROP_COLS)[KEEP_ORDER]
        buffer = StringIO()
        # No header (COPY expects pure data) and no index (pandas would
        # invent an extra first column and shift everything right).
        slim.to_csv(buffer, header=False, index=False)
        buffer.seek(0)
        cursor.copy_expert(COPY_SQL, buffer)
        total += len(chunk)
        print(f"  {path}: {total:,} rows staged", flush=True)
    return total


def main() -> None:
    conn = psycopg2.connect(
        os.getenv("DATABASE_URL"),
        keepalives=1, keepalives_idle=30,
        keepalives_interval=10, keepalives_count=5,
    )
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM transactions_raw")
    existing = cur.fetchone()[0]
    if existing:
        print(f"transactions_raw already holds {existing:,} rows - aborting "
              "so a rerun can't duplicate data.")
        return

    # One transaction for the whole load: either all 1.85M rows land or none
    # do, so a failed run leaves the table clean for a simple retry.
    grand_total = 0
    for path in FILES:
        grand_total += load_file(path, cur)
    conn.commit()
    print(f"Done - {grand_total:,} rows committed to transactions_raw")


if __name__ == "__main__":
    main()
