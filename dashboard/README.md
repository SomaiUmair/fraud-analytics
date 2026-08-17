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

## Troubleshooting
- **SSL/cert error:** download the CA cert from the Aiven console and install
  it for Current User. Do not disable encryption.
- **Slow first import:** normal (~400MB over the wire); it caches in the file.
- **Map shows wrong locations:** the `state` data-category step was skipped.
