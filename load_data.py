"""Load both fraud CSVs into transactions_raw, in chunks.

Streams the ~480MB of source data through memory 50k rows at a time and
bulk-loads each batch with PostgreSQL's COPY — the fast path, roughly 50x
quicker than row-by-row INSERTs. Aborts if the table already has rows, so
an accidental rerun can't create duplicates.
"""

import os
from io import StringIO

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

FILES = ["data/fraudTrain.csv", "data/fraudTest.csv"]
CHUNK_SIZE = 50_000

# Target columns in schema order; COPY maps incoming CSV fields to these
# positionally, so this list must match both the table and the CSV layout.
COLUMNS = (
    "row_id, trans_time, cc_num, merchant, category, amt, first_name, "
    "last_name, gender, street, city, state, zip, lat, long, city_pop, "
    "job, dob, trans_num, unix_time, merch_lat, merch_long, is_fraud"
)

COPY_SQL = f"COPY transactions_raw ({COLUMNS}) FROM STDIN WITH CSV"


def load_file(path: str, cursor) -> int:
    """Stream one CSV into the raw table in CHUNK_SIZE batches."""
    total = 0
    for chunk in pd.read_csv(path, chunksize=CHUNK_SIZE):
        buffer = StringIO()
        # No header (COPY expects data only) and no index (the CSV's own
        # row_id column is already the first field).
        chunk.to_csv(buffer, header=False, index=False)
        buffer.seek(0)
        cursor.copy_expert(COPY_SQL, buffer)
        total += len(chunk)
        print(f"  {path}: {total:,} rows staged", flush=True)
    return total


def main() -> None:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM transactions_raw")
    existing = cur.fetchone()[0]
    if existing:
        print(f"transactions_raw already holds {existing:,} rows — aborting "
              "so a rerun can't duplicate data.")
        return

    # One transaction for the whole load: either all 1.85M rows land or none
    # do, so a failed run leaves the table clean for a simple retry.
    grand_total = 0
    for path in FILES:
        grand_total += load_file(path, cur)
    conn.commit()
    print(f"Done — {grand_total:,} rows committed to transactions_raw")


if __name__ == "__main__":
    main()
