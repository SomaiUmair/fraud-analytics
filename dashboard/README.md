# Dashboard Build Guide (Power BI)

Three pages built over the fraud data. The committed report is `Fraud.pbix`,
built from the local workbook (Option B below), so it opens anywhere with no
database connection.

## Option A: connect to the live database

1. Get Data, then PostgreSQL database
2. Server: `pg-25a20f3f-somaiumair-f5b2.g.aivencloud.com:14750`
   Database: `defaultdb`. Mode: Import
3. Credentials: Database tab, user `avnadmin` plus the password from the Aiven
   console (never stored in this repo)
4. Navigator: check `public.transactions` (the view, not transactions_raw),
   then Load. The import takes a few minutes (1.85M rows)
5. Measures (New measure, one per line):

```
Total Transactions = COUNTROWS(transactions)
Fraud Count = SUM(transactions[is_fraud])
Fraud Rate = DIVIDE([Fraud Count], [Total Transactions])
Fraud Dollars = CALCULATE(SUM(transactions[amt]), transactions[is_fraud] = 1)
```

Format Fraud Rate as a percentage (2 decimals) and Fraud Dollars as currency.
Select the `state` column, then Column tools, then set Data category to State
or Province (needed for the map).

## Option B: build from the local workbook (no database needed)

Everything comes from `dashboard/source_extract.xlsx` in this repo. Regenerate
it anytime with `python make_dashboard_extract.py`.

1. Get the repo: `git clone https://github.com/SomaiUmair/fraud-analytics.git`
2. Power BI Desktop, blank report. Home, Get Data, Excel workbook, pick
   `dashboard/source_extract.xlsx`
3. Navigator: tick all six sheets (totals, monthly, by_state, hour_dow,
   by_category, age_bands), then Load
4. Data pane: expand `by_state`, click `state`, Column tools, Data category,
   State or Province
5. Five measures (New measure, one at a time; format each rate as a
   percentage with 2 decimals). If a pasted formula errors, type it by hand
   and let autocomplete insert the field names:

```
Overall Fraud Rate = SUM('totals'[fraud_count]) / SUM('totals'[transactions])
State Rate = SUM('by_state'[fraud_count]) / SUM('by_state'[transactions])
Time Rate = SUM('hour_dow'[fraud_count]) / SUM('hour_dow'[transactions])
Cat Rate = SUM('by_category'[fraud_count]) / SUM('by_category'[transactions])
Age Rate = SUM('age_bands'[fraud_count]) / SUM('age_bands'[transactions])
```

Counts ride along in every sheet so rates always recompute as
SUM(fraud)/SUM(n), never as averaged percentages.

## The three pages

Overview
- Card visuals: `totals[transactions]`, `totals[fraud_count]`,
  `totals[fraud_dollars]`, and the Overall Fraud Rate measure
- Line chart: X = `monthly[month]`, Y = `monthly[fraud_count]`

Geography
- Filled map: Location = `by_state[state]`, fill color as a gradient based on
  State Rate (Format, Fill colors, fx). If map visuals are greyed out: File,
  Options, Security, enable Map visuals, then restart
- Table beside it: state, transactions, fraud_count, State Rate, sorted by
  State Rate descending

Patterns
- Matrix: Rows = `hour_dow[trans_dow]`, Columns = `hour_dow[trans_hour]`,
  Values = Time Rate. Format, Cell elements, Background color On. The
  night-fraud stripe shows itself. If not all 24 hour columns fit, reduce the
  Grid global font size or turn off Row subtotals
- Bar chart: Y = `by_category[category]`, X = Cat Rate, sorted descending
- Column chart: X = `age_bands[age_band_start]`, Y = Age Rate (already binned
  to decades)

## Ship

1. Save the .pbix
2. Screenshot each page (Win+Shift+S) as `overview.png`, `geography.png`,
   `patterns.png`
3. Put the PNGs in `dashboard/screenshots/`, then commit and push
4. Commit the .pbix too if it is under about 95MB (GitHub's limit is 100MB).
   The extract-based build is around 100 KB

## Troubleshooting

- SSL or certificate error on connect: download the CA certificate from the
  Aiven console and install it for the current user. Do not disable
  encryption.
- Slow first import in Option A: normal. It is about 400MB over the wire and
  caches in the file afterward.
- Map puts states in the wrong places: the state data-category step was
  skipped.
- A DAX formula errors on a pasted table name: type the formula by hand and
  pick fields from the autocomplete dropdown.
