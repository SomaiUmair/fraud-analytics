# Project Design: Fraud Analytics

One project, three deliverables. Every file must earn an interview talking
point. Anything not on this map is scope creep.

## Architecture

```
CSV (1.85M rows) -> PostgreSQL (load + clean) -> Python notebook (EDA, features, model) -> Power BI
```

## Dataset

Sparkov simulated credit-card transactions: `fraudTrain.csv` plus
`fraudTest.csv`, about 1.85M rows spanning 2019 to 2020. Label: `is_fraud`
(about 0.5% positive). Business columns: merchant, category, amount, customer
demographics and geography, and both customer and merchant coordinates.
Simulated data, always disclosed as such.

## Deliverables

1. Load and clean in SQL: a chunked loader into `transactions_raw`, then a
   clean `transactions` layer with derived columns (hour, day of week,
   customer age) and indexes. The story: 1.85M rows, and Excel caps at 1.05M.
2. One analysis notebook: EDA (fraud rate by category, hour, and amount), the
   customer-to-merchant distance feature, a logistic-regression baseline vs
   XGBoost, and precision/recall with a time-based split. The story: accuracy
   is a lie at 0.5% fraud.
3. Power BI dashboard, 3 pages: KPI overview, state map, and time/category
   patterns. Screenshots committed. The story: stakeholder communication.

## Build plan

- [x] Phase 0: scaffold, database, GitHub repo and first push
- [x] Phase 1: `sql/01_schema.sql`, `load_data.py` (chunked), verify counts,
      `sql/02_clean.sql`, commit
- [x] Phase 2: notebook. EDA, distance feature, baseline vs XGBoost, honest
      evaluation, commit
- [x] Phase 3: Power BI, 3 pages, screenshots, commit
- [x] Phase 4: final README with findings and screenshots

## Guardrails

- No API, no scheduler, no economics join.
- Time-based split only (train on 2019 to mid-2020, test on the rest). No
  look-ahead.
- No accuracy claims without the imbalance context (precision/recall).
- Data files never committed. Secrets never committed (`.env` is ignored).

## Notes from the build

- The database moved from Neon (512MB cap, too small for the data) to Aiven
  during Phase 1. The clean layer became a view instead of a second table to
  fit the disk. Constraints shaped the design.
- The dashboard was built from a small pre-aggregated workbook
  (`make_dashboard_extract.py`) after the direct database connection failed on
  one machine. Same visuals, no connectivity required.
