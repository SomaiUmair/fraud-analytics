-- 01_schema.sql — raw landing table for the Sparkov CSVs.
-- A faithful, typed copy of the source files. No cleaning, no derived
-- columns, no indexes here: cleaning happens in 02_clean.sql, and loading
-- 1.85M rows is much faster into an index-free table. Run once.

CREATE TABLE IF NOT EXISTS transactions_raw (
    row_id      INTEGER,          -- CSV "Unnamed: 0" leftover index; dropped in cleaning
    trans_time  TIMESTAMP,        -- trans_date_trans_time in the CSV
    cc_num      TEXT,             -- identifier, not a quantity: no arithmetic, and TEXT
                                  -- can never silently eat a leading zero
    merchant    TEXT,
    category    TEXT,
    amt         NUMERIC(10,2),    -- money is exact decimal, never float
    first_name  TEXT,             -- CSV "first"
    last_name   TEXT,             -- CSV "last"
    gender      TEXT,
    street      TEXT,
    city        TEXT,
    state       TEXT,
    zip         TEXT,             -- New Jersey zips start with 0; a numeric type
                                  -- would turn 07001 into 7001
    lat         DOUBLE PRECISION, -- customer home coordinates
    long        DOUBLE PRECISION,
    city_pop    INTEGER,
    job         TEXT,
    dob         DATE,
    trans_num   TEXT,             -- unique transaction id (hex string)
    unix_time   BIGINT,           -- same instant as trans_time, epoch seconds; redundant
    merch_lat   DOUBLE PRECISION, -- merchant coordinates (distance feature later)
    merch_long  DOUBLE PRECISION,
    is_fraud    SMALLINT          -- the label: 0 legitimate, 1 fraud
);
