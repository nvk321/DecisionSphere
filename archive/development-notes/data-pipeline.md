# DecisionSphere — Data Pipeline & Dataset Audit Strategy

## 1. Overview
DecisionSphere integrates three distinct operational domains, requiring a disciplined, leakage-free data processing pipeline. Raw datasets reside in reference archives and must be processed systematically into reproducible, model-ready artifacts.

```
Raw Archives (reference/)
           ↓
   [Extraction & Validation]
           ↓
Raw Data Cache (data/raw/)
           ↓
[Exploratory Data Audit & Profiling]
           ↓
[Preprocessing & Feature Engineering]
  - Chronological splits (Demand)
  - Featurization after train/test split
  - Encoding, Scaling, Outlier Handling
           ↓
Model-Ready Datasets (data/processed/)
           ↓
  Offline Model Training & Validation
```

---

## 2. Candidate Datasets Inventory

### 2.1 Demand Forecasting Candidates
1. **Corporación Favorita Store Sales - Time Series Forecasting** (`reference/store-sales-time-series-forecasting (1).zip`):
   - **Files:** `train.csv` (116 MB), `test.csv`, `stores.csv`, `oil.csv`, `holidays_events.csv`, `transactions.csv`.
   - **Characteristics:** Rich daily grocery store sales across 54 stores and 33 product families in Ecuador, including promotional flags, national/local holidays, and oil price macroeconomic indicators.
2. **Walmart Recruiting Store Sales Forecasting** (`reference/walmart-recruiting-store-sales-forecasting.zip`, `reference/archive (1).zip`):
   - **Files:** `train.csv` (12.8 MB), `features.csv`, `stores.csv`, `test.csv`.
   - **Characteristics:** Weekly sales for 45 Walmart stores across various departments, including Markdown promotional variables, CPI, unemployment, and temperature.
3. **Rossmann Store Sales** (`reference/rossmann-store-sales.zip`, `reference/rossman-store-sales-main.zip`):
   - **Files:** `train.csv` (36.3 MB), `store.csv`, `test.csv`.
   - **Characteristics:** Daily sales across 1,115 European drug stores, including promotional cycles, competitor distance, and school holidays.

*Audit Task:* The initial data audit will compare these candidates on temporal granularity, presence of explicit promotional indicators, file size/memory footprint, and ease of cross-domain integration to select the single primary demand dataset.

### 2.2 Supply Chain Risk Dataset
1. **DataCo Smart Supply Chain for Big Data Analysis** (`reference/archive (2).zip`, `reference/archive (3).zip`):
   - **Files:** `DataCoSupplyChainDataset.csv` (~95.9 MB, ~180,519 rows, 53 columns).
   - **Key Fields:** `Days for shipping (real)`, `Days for shipment (scheduled)`, `Delivery Status`, `Late_delivery_risk`, `Order Status`, `Shipping Mode`, `Customer Segment`, `Department Name`, `Order Item Total`, `Sales per customer`.
   - **Characteristics:** Highly realistic multi-year global e-commerce supply chain dataset tracking order fulfillment, delivery delay indicators, and shipment logistics.
   - **Target Variable Candidates:** `Late_delivery_risk` (binary: 0 = On time/Ahead, 1 = Late) or `Delivery Status` (multi-class: Advance shipping, Late delivery, Shipping on time, Shipping canceled).

### 2.3 Workforce / HR Attrition Dataset
1. **IBM HR Analytics Employee Attrition & Performance** (`reference/archive (7).zip`, `reference/IBM-HR-Analytics-Employee-Attrition-and-Performance-Prediction-main.zip`):
   - **Files:** `WA_Fn-UseC_-HR-Employee-Attrition.csv` (~0.23 MB, 1,470 rows, 35 columns).
   - **Key Fields:** `Attrition` (Yes/No), `Age`, `BusinessTravel`, `DailyRate`, `Department`, `DistanceFromHome`, `EnvironmentSatisfaction`, `JobInvolvement`, `JobLevel`, `JobRole`, `JobSatisfaction`, `MonthlyIncome`, `OverTime`, `TotalWorkingYears`, `WorkLifeBalance`, `YearsAtCompany`.
   - **Characteristics:** The gold-standard benchmark dataset for employee turnover analysis, containing rich organizational, compensation, and operational workload features.
   - **Target Variable:** `Attrition` (Binary: Yes = 1, No = 0, with ~16.1% positive class imbalance).

---

## 3. Data Leakage Prevention Rules

1. **Time-Series Horizon Preservation:**
   - For retail sales: Validation and test sets must strictly represent subsequent chronological periods relative to the training split. Never shuffle time series data.
2. **Preprocessing Isolation:**
   - Numerical scalers (`StandardScaler`, `RobustScaler`) and categorical encoders (`OneHotEncoder`, `TargetEncoder`) must be fitted **exclusively** on the training partition and applied downstream to validation/test partitions.
3. **Feature Availability Validation (Lookahead Prevention):**
   - No features generated or observed after the prediction event (e.g., actual delivery date in a pre-dispatch risk model) may be used as input variables.

---

## 4. Phase 1 Data Audit Protocol
Before writing model code, Phase 1 requires executing an automated profiling script that computes:
- Exact row and column counts.
- Memory usage across standard datatypes.
- Missing values count and percentage per column.
- Cardinality of categorical columns.
- Skewness and distribution of target variables.
- Duplicate record count.
- Identification of non-predictive identifiers (`EmployeeNumber`, `Order Id`, etc.).
- Summary output committed to `docs/assumptions-and-open-questions.md`.
