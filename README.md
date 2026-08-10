# Fraud Analytics

Detecting fraudulent card transactions in 1.85M simulated records — SQL,
Python, and Power BI, end to end.

**Status: in progress.** The build plan lives in
[PROJECT_DESIGN.md](PROJECT_DESIGN.md).

## Architecture

```
CSV (1.85M rows) -> PostgreSQL (load + clean) -> Python (EDA, features, model) -> Power BI
```

## Data

Sparkov simulated credit-card transactions (`fraudTrain.csv` + `fraudTest.csv`,
~1.85M rows, 2019–2020, labeled `is_fraud`). The files exceed GitHub's size
limit and are not committed — download from Kaggle and place both CSVs in
`data/`.
