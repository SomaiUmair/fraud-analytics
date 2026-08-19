# Dashboard Build Guide (Power BI)

Three pages over the `transactions` view. Data connection is **Import** mode —
one pull into the .pbix, then everything is local and fast.

## 1. Prerequisites
- Power BI Desktop (Microsoft Store, free)
- The database password — from the Aiven console → your PostgreSQL service →
  **Connection information** (never stored in this repo)

## 2. Connect
1. Get Data → **PostgreSQL database**
2. Server: `pg-25a20f3f-somaiumair-f5b2.g.aivencloud.com:14750`
   Database: `defaultdb` · Mode: **Import**
3. Credentials → **Database** tab → user `avnadmin` + password
4. Navigator → check **public.transactions** (the view, not transactions_raw) → Load
5. Import takes a few minutes (1.85M rows)

## 3. Measures (New measure, one per line)
```
Total Transactions = COUNTROWS(transactions)
Fraud Count = SUM(transactions[is_fraud])
Fraud Rate = DIVIDE([Fraud Count], [Total Transactions])
Fraud Dollars = CALCULATE(SUM(transactions[amt]), transactions[is_fraud] = 1)
```
Format Fraud Rate as % (2 dp), Fraud Dollars as currency. Then select the
`state` column → Column tools → **Data category → State or Province** (needed
for the map).

## 4. Pages

**Overview** — 4 cards (the measures above) · line chart of Fraud Count by
`trans_time` (month level) · date-range slicer.

**Geography** — Filled map: Location = `state`, color = Fraud Rate. (If map
visuals are disabled: File → Options → Security → enable Map visuals.)
Beside it: table of state / Total Transactions / Fraud Count / Fraud Rate,
sorted by Fraud Rate desc.

**Patterns** — Matrix: rows `trans_dow`, columns `trans_hour`, values Fraud
Rate, with background-color conditional formatting (the night-fraud stripe
shows itself). Bar chart: Fraud Rate by `category`, sorted. Column chart:
Fraud Rate by `customer_age` binned to 10-year groups.

## 5. Ship
1. Save as `fraud.pbix`
2. Screenshot each page → `overview.png`, `geography.png`, `patterns.png`
3. From this repo cloned on any machine:
   put the PNGs in `dashboard/screenshots/`, then
   `git add dashboard/screenshots && git commit -m "Add dashboard screenshots" && git push`
4. Commit the .pbix too if it is under ~95MB (GitHub's limit is 100MB)

## Option B — build from the local workbook (no database connection)

If Power BI can't reach the database (DNS/SSL issues on some networks), use
the committed extract instead — same dashboard, zero connectivity required:

1. Get Data → **Excel workbook** → `dashboard/source_extract.xlsx` (in this
   repo) → check **all six sheets** → Load
   (Regenerate it anytime with `python make_dashboard_extract.py`.)
2. Measures become per-sheet rates — create these instead of section 3's:
   ```
   Overall Fraud Rate = DIVIDE(SUM(totals[fraud_count]), SUM(totals[transactions]))
   State Rate  = DIVIDE(SUM(by_state[fraud_count]),  SUM(by_state[transactions]))
   Time Rate   = DIVIDE(SUM(hour_dow[fraud_count]),  SUM(hour_dow[transactions]))
   Cat Rate    = DIVIDE(SUM(by_category[fraud_count]), SUM(by_category[transactions]))
   Age Rate    = DIVIDE(SUM(age_bands[fraud_count]), SUM(age_bands[transactions]))
   ```
   (Counts and fraud counts are kept per sheet so rates always recompute as
   SUM(fraud)/SUM(n) — never averaged percentages.)
3. Page mapping: cards ← `totals` columns + Overall Fraud Rate · line chart ←
   `monthly` (month, fraud_count) · map/table ← `by_state` + State Rate (set
   the state column's data category as in section 3) · matrix ← `hour_dow`
   (rows trans_dow, columns trans_hour, values Time Rate) · bar ← `by_category`
   + Cat Rate · column ← `age_bands` (age_band_start is pre-binned to decades,
   so skip the grouping step)

## Troubleshooting
- **SSL/cert error:** download the CA cert from the Aiven console and install
  it for Current User. Do not disable encryption.
- **Slow first import:** normal (~400MB over the wire); it caches in the file.
- **Map shows wrong locations:** the `state` data-category step was skipped.
