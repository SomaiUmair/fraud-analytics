-- 02_clean.sql — the clean layer as a VIEW, plus indexes on the base table.
-- A view stores nothing: derivations are computed when queried, which is the
-- deliberate trade on a ~1GB free tier — compute on read instead of storing
-- the 1.85M rows twice. Filters on indexed base columns (time, category,
-- state, fraud flag) still use the indexes through the view.

CREATE OR REPLACE VIEW transactions AS
SELECT
    trans_num,
    trans_time,
    EXTRACT(HOUR FROM trans_time)::smallint AS trans_hour,
    EXTRACT(DOW  FROM trans_time)::smallint AS trans_dow,   -- 0 = Sunday
    cc_num,
    -- Strip the simulator's meaningless "fraud_" prefix from merchant names.
    REGEXP_REPLACE(merchant, '^fraud_', '') AS merchant,
    category,
    amt,
    gender,
    -- Age AT the time of the transaction, not age today.
    DATE_PART('year', AGE(trans_time, dob))::smallint AS customer_age,
    job,
    city,
    state,
    zip,
    city_pop,
    lat  AS cust_lat,
    long AS cust_long,
    merch_lat,
    merch_long,
    is_fraud
FROM transactions_raw;

-- Indexes AFTER the load: write fast once, then optimize for reading.
-- Only two, deliberately: index builds cost disk (temp sort space + WAL),
-- and on this ~1GB instance the category/state indexes aren't worth it —
-- one-off EDA scans of a 400MB table take seconds, and Power BI imports
-- the data once. Index what gets filtered constantly, scan the rest.
CREATE INDEX IF NOT EXISTS idx_raw_time ON transactions_raw (trans_time);
-- Partial index: fraud is 0.5% of rows and "show me the fraud" is the most
-- common filter — indexing only those ~9.6k rows is tiny and fast.
CREATE INDEX IF NOT EXISTS idx_raw_is_fraud ON transactions_raw (is_fraud) WHERE is_fraud = 1;
