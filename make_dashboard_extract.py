"""Build dashboard/source_extract.xlsx — pre-aggregated tables for Power BI.

Lets the dashboard be built from a small local workbook instead of a live
database connection (useful when Power BI can't reach the server). Each sheet
is at the exact grain its visual uses; counts are kept alongside fraud counts
so rates can always be recomputed correctly as SUM(fraud)/SUM(n).
"""

import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))

OUT = "dashboard/source_extract.xlsx"

sheets = {
    "totals": """
        SELECT COUNT(*) AS transactions,
               SUM(is_fraud) AS fraud_count,
               SUM(amt) FILTER (WHERE is_fraud = 1) AS fraud_dollars
        FROM transactions
    """,
    "monthly": """
        SELECT DATE_TRUNC('month', trans_time)::date AS month,
               COUNT(*) AS transactions,
               SUM(is_fraud) AS fraud_count
        FROM transactions GROUP BY 1 ORDER BY 1
    """,
    "by_state": """
        SELECT state, COUNT(*) AS transactions, SUM(is_fraud) AS fraud_count
        FROM transactions GROUP BY 1 ORDER BY 1
    """,
    "hour_dow": """
        SELECT trans_dow, trans_hour,
               COUNT(*) AS transactions, SUM(is_fraud) AS fraud_count
        FROM transactions GROUP BY 1, 2 ORDER BY 1, 2
    """,
    "by_category": """
        SELECT category, COUNT(*) AS transactions, SUM(is_fraud) AS fraud_count
        FROM transactions GROUP BY 1 ORDER BY 1
    """,
    "age_bands": """
        SELECT (FLOOR(customer_age / 10) * 10)::int AS age_band_start,
               COUNT(*) AS transactions, SUM(is_fraud) AS fraud_count
        FROM transactions GROUP BY 1 ORDER BY 1
    """,
}

with pd.ExcelWriter(OUT, engine="openpyxl") as writer:
    for name, sql in sheets.items():
        df = pd.read_sql(sql, conn)
        df.to_excel(writer, sheet_name=name, index=False)
        print(f"{name}: {len(df)} rows", flush=True)

size_kb = os.path.getsize(OUT) / 1024
print(f"\nwrote {OUT} ({size_kb:.0f} KB)")
