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

Same dashboard, zero connectivity: everything comes from
`dashboard/source_extract.xlsx` in this repo (regenerate anytime with
`python make_dashboard_extract.py`). Exact steps:

**B1. Get the repo onto this machine**
```
git clone https://github.com/SomaiUmair/fraud-analytics.git
```
(or GitHub → Code → Download ZIP → extract)

**B2. Load the workbook**
1. Power BI Desktop → blank report
2. Home → **Get Data** → **Excel workbook** → pick
   `fraud-analytics/dashboard/source_extract.xlsx` → Open
3. Navigator: tick **all six sheets** — totals, monthly, by_state, hour_dow,
   by_category, age_bands → **Load** (instant — it's 13 KB)

**B3. One column setting**
Data pane (right side) → expand **by_state** → click `state` →
Column tools ribbon → **Data category → State or Province**

**B4. Five measures** (Home → New measure, one at a time; after each, use
Measure tools to format the rates as Percentage, 2 decimals)
```
Overall Fraud Rate = DIVIDE(SUM(totals[fraud_count]), SUM(totals[transactions]))
State Rate  = DIVIDE(SUM(by_state[fraud_count]),  SUM(by_state[transactions]))
Time Rate   = DIVIDE(SUM(hour_dow[fraud_count]),  SUM(hour_dow[transactions]))
Cat Rate    = DIVIDE(SUM(by_category[fraud_count]), SUM(by_category[transactions]))
Age Rate    = DIVIDE(SUM(age_bands[fraud_count]), SUM(age_bands[transactions]))
```
(Counts ride along in every sheet so rates always recompute as
SUM(fraud)/SUM(n) — never averaged percentages.)

**B5. Page 1 — rename the tab "Overview"**
- 3 **Card** visuals: `totals[transactions]` · `totals[fraud_count]` ·
  `totals[fraud_dollars]`
- 1 **Card**: the `Overall Fraud Rate` measure
- **Line chart**: X = `monthly[month]`, Y = `monthly[fraud_count]`

**B6. Page 2 — "Geography"**
- **Filled map**: Location = `by_state[state]`, Color saturation = `State Rate`
  (if map visuals are greyed out: File → Options → Security → enable Map
  visuals → restart)
- **Table**: state · transactions · fraud_count · `State Rate` → click the
  State Rate header to sort descending

**B7. Page 3 — "Patterns"**
- **Matrix**: Rows = `hour_dow[trans_dow]`, Columns = `hour_dow[trans_hour]`,
  Values = `Time Rate` → Format (paint roller) → **Cell elements →
  Background color → On** — the night-fraud stripe appears
- **Bar chart**: Y = `by_category[category]`, X = `Cat Rate`, sorted descending
- **Column chart**: X = `age_bands[age_band_start]`, Y = `Age Rate`
  (already binned to decades — no grouping needed)

**B8. Ship** — save `fraud.pbix`, screenshot each page (`Win+Shift+S`) as
`overview.png`, `geography.png`, `patterns.png`, drop them in
`dashboard/screenshots/` inside the clone, then:
```
git add dashboard/screenshots
git commit -m "Add dashboard screenshots"
git push
```

## Troubleshooting
- **SSL/cert error:** download the CA cert from the Aiven console and install
  it for Current User. Do not disable encryption.
- **Slow first import:** normal (~400MB over the wire); it caches in the file.
- **Map shows wrong locations:** the `state` data-category step was skipped.
