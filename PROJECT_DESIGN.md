# Project Design — Fraud Analytics

One project, three deliverables, ~3 weekends. Every file must earn an
interview talking point; anything not on this map is scope creep.

## Architecture

```
CSV (1.85M rows) -> PostgreSQL (load + clean) -> Python notebook (EDA, features, model) -> Power BI
```

## Dataset

Sparkov simulated credit-card transactions: `fraudTrain.csv` + `fraudTest.csv`,
~1.85M rows spanning 2019–2020. Label: `is_fraud` (~0.5% positive). Business
columns: merchant, category, amount, customer demographics + geography,
customer AND merchant lat/long. Simulated data — always disclosed as such.

## Deliverables

1. **Load + clean in SQL** — chunked loader into `transactions_raw`, then a
   cleaned `transactions` table with derived columns (hour, day-of-week,
   customer age) and indexes. Story: "1.85M rows — Excel caps at 1.05M."
2. **One analysis notebook** — EDA (fraud rate by category/hour/amount) →
   haversine distance between customer and merchant → logistic-regression
   baseline vs XGBoost → precision/recall with a time-based split. Story:
   "accuracy is a lie at 0.5% fraud."
3. **Power BI dashboard, 3 pages** — KPI overview, state map, category/time
   patterns. Screenshots committed; story: stakeholder communication.

## Build plan

- [ ] Phase 0 — scaffold, `fraud` database on Neon, GitHub repo + first push
- [ ] Phase 1 (weekend 1): `sql/01_schema.sql` → `load_data.py` (chunked) →
      verify counts → `sql/02_clean.sql` → commit
- [ ] Phase 2 (weekend 2): notebook — EDA → distance feature → baseline vs
      XGBoost → honest evaluation → commit
- [ ] Phase 3 (weekend 3): Power BI on Neon → 3 pages → screenshots → commit
- [ ] Phase 4: real README (3 findings + screenshots), pin repo, resume v3

## Guardrails

- No API, no scheduler, no economics join.
- Time-based split only (train 2019, test 2020) — no look-ahead.
- No accuracy claims without the imbalance context (precision/recall).
- Data files never committed; secrets never committed (`.env` ignored).
