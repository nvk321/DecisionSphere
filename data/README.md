# DecisionSphere — Data Directory Structure & Governance

This directory manages the data assets for DecisionSphere. To adhere to Git best practices, raw and processed large datasets are excluded from version control via `.gitignore`.

---

## Directory Organization

```
data/
├── raw/            # Extracted, unaltered benchmark datasets (gitignored)
├── processed/      # Model-ready, cleaned, encoded, and split datasets (gitignored)
└── README.md       # Data provenance, schemas, and download instructions
```

---

## Dataset Provenance & Attribution

### 1. Demand Forecasting Benchmark Candidates
- **Option A: Store Sales - Time Series Forecasting (Corporación Favorita)**
  - *Source:* Kaggle Competition (`store-sales-time-series-forecasting`)
  - *Archive in repo:* `reference/store-sales-time-series-forecasting (1).zip`
  - *License:* Kaggle Competition / Open Data
  - *Key Tables:* `train.csv`, `stores.csv`, `oil.csv`, `holidays_events.csv`
- **Option B: Walmart Recruiting Store Sales Forecasting**
  - *Source:* Kaggle Competition (`walmart-recruiting-store-sales-forecasting`)
  - *Archive in repo:* `reference/archive (1).zip`, `reference/walmart-recruiting-store-sales-forecasting.zip`
- **Option C: Rossmann Store Sales**
  - *Source:* Kaggle Competition (`rossmann-store-sales`)
  - *Archive in repo:* `reference/rossmann-store-sales.zip`

### 2. Supply Chain Risk Benchmark
- **DataCo Smart Supply Chain for Big Data Analysis**
  - *Source:* Kaggle / Fabian Constante et al.
  - *Archive in repo:* `reference/archive (2).zip`, `reference/archive (3).zip`
  - *File:* `DataCoSupplyChainDataset.csv` (~95.9 MB, 180,519 records, 53 attributes)
  - *Primary Target:* `Late_delivery_risk` (Binary: 1 = Late, 0 = On-time)

### 3. Workforce / HR Attrition Benchmark
- **IBM HR Analytics Employee Attrition & Performance**
  - *Source:* Kaggle / IBM Watson Analytics
  - *Archive in repo:* `reference/archive (7).zip`, `reference/IBM-HR-Analytics-Employee-Attrition-and-Performance-Prediction-main.zip`
  - *File:* `WA_Fn-UseC_-HR-Employee-Attrition.csv` (1,470 records, 35 attributes)
  - *Primary Target:* `Attrition` (Binary: Yes / No)

---

## Data Governance Rules
1. **Never commit files in `data/raw/` or `data/processed/` to Git.**
2. **Never modify files in `reference/`.** `reference/` serves as an immutable local archive.
3. Automated extraction and profiling scripts in `scripts/` or `src/data/` will populate `data/raw/` and `data/processed/` reproducibly.
