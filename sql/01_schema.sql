-- 01_schema.sql - raw landing table for the Sparkov CSVs.
-- Slim by design: the free-tier disk (~1GB) cannot hold the data twice, so
-- zero-signal columns (names, street, CSV row index, duplicate epoch
-- timestamp) are dropped at load time and never stored. The clean layer is
-- a view (02_clean.sql) - computed on read, zero storage. No indexes here;
-- they come after loading (02), because inserts into indexed tables crawl.

CREATE TABLE IF NOT EXISTS transactions_raw (
    trans_time  TIMESTAMP,        -- trans_date_trans_time in the CSV
    cc_num      TEXT,             -- identifier, not a quantity: no arithmetic,
                                  -- and TEXT never eats a leading zero
    merchant    TEXT,             -- still carries the simulator's "fraud_" prefix
    category    TEXT,
    amt         NUMERIC(10,2),    -- money is exact decimal, never float
    gender      TEXT,
    dob         DATE,             -- kept so the view can compute age-at-transaction
    job         TEXT,
    city        TEXT,
    state       TEXT,
    zip         TEXT,             -- New Jersey zips start with 0; numeric types
                                  -- would turn 07001 into 7001
    city_pop    INTEGER,
    lat         DOUBLE PRECISION, -- customer home coordinates
    long        DOUBLE PRECISION,
    merch_lat   DOUBLE PRECISION, -- merchant coordinates (distance feature later)
    merch_long  DOUBLE PRECISION,
    trans_num   TEXT,             -- unique transaction id (hex string)
    is_fraud    SMALLINT          -- the label: 0 legitimate, 1 fraud
);
