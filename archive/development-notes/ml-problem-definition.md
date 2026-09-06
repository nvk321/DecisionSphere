# DecisionSphere — Machine Learning Problem Definition

To adhere to rigorous academic ML standards, each machine learning component in DecisionSphere is formally defined with problem formulations, target definitions, timing windows, input spaces, and leakage guardrails.

---

## 1. Domain A: Retail Demand Forecasting

### 1.1 Problem Formulation
- **Type:** Multi-horizon, supervised regression / time-series forecasting.
- **Objective:** Given historical daily sales, store attributes, calendar cycles, and promotional status up to time $t$, predict sales volume $\hat{y}_{t+1}, \dots, \hat{y}_{t+H}$ over a forecast horizon $H$ (typically 14 to 30 days).

### 1.2 Target Variable
- Primary Target: `unit_sales` (or `sales` in USD/local currency) at the store-family or store-item level.
- Transformation: Log1p transformation $\log(y + 1)$ evaluated to stabilize variance across volatile volume categories.

### 1.3 Input Feature Space
- **Temporal & Calendar:** Day of week, day of month, month, year, weekend flag, holiday indicator, days until next holiday.
- **Promotional & Economic:** On-promotion indicator, promo intensity, oil price / macroeconomic index (where available).
- **Lag & Rolling Window Features:** Lagged sales ($t-1, t-7, t-14, t-28$), rolling mean ($7, 14, 30$ days), rolling standard deviation ($7, 30$ days).
- **Categorical Encoders:** Store type, cluster, department / product family.

### 1.4 Temporal Integrity & Anti-Leakage
- **Split Strategy:** Strict chronological split. Training on earlier time window, validation on intermediate window, testing on final holdout window.
- **Rolling Feature Guardrail:** Rolling aggregations must strictly use historical shift ($t - 1$ or earlier); never include current time $t$ in rolling calculations.

---

## 2. Domain B: Supply Chain Delivery Risk Analysis

### 2.1 Problem Formulation
- **Type:** Supervised tabular binary (and multi-class) classification.
- **Objective:** At order placement and shipment scheduling time $t_{\text{order}}$, predict whether the shipment will experience delivery failure / late delivery ($\hat{y} \in \{0, 1\}$).

### 2.2 Target Variable
- In DataCo dataset: `Late_delivery_risk` (1 = Late delivery, 0 = On-time or Ahead of schedule).
- Secondary Target: `Delivery Status` (4 classes: *Late delivery, Advance shipping, Shipping on time, Shipping canceled*).

### 2.3 Input Feature Space
- **Scheduling Attributes:** `Days for shipment (scheduled)`, `Shipping Mode` (Standard, First Class, Second Class, Same Day).
- **Customer & Geography:** `Customer Segment`, `Customer Country`, `Customer State`, `Order Region`, `Order Country`.
- **Product & Order:** `Order Item Quantity`, `Order Item Product Price`, `Category Name`, `Department Name`.
- **Temporal Attributes:** Order hour, order day of week, order month.

### 2.4 Leakage Prevention Guardrail
- **Prohibited Lookahead Features:**
  - `Days for shipping (real)` must **NOT** be used as a predictive feature, as it is only known after delivery occurs.
  - `Delivery Status` must be excluded from feature vectors when predicting `Late_delivery_risk`.
  - Any post-fulfillment tracking timestamps must be dropped.

---

## 3. Domain C: Workforce / HR Attrition Risk Analysis

### 3.1 Problem Formulation
- **Type:** Supervised imbalanced tabular binary classification.
- **Objective:** Predict whether an employee has a high probability of voluntarily leaving the organization within the evaluation cycle ($\hat{y} \in \{0, 1\}$).

### 3.2 Target Variable
- In IBM HR dataset: `Attrition` (encoded as `Yes` $\rightarrow 1$, `No` $\rightarrow 0$).
- Baseline Class Distribution: ~16.1% positive class (83.9% negative), necessitating imbalanced handling strategies (class weighting, threshold tuning).

### 3.3 Input Feature Space
- **Demographics & Experience:** `Age`, `TotalWorkingYears`, `YearsAtCompany`, `YearsInCurrentRole`, `YearsSinceLastPromotion`, `YearsWithCurrManager`.
- **Workload & Burnout Indicators:** `OverTime` (Yes/No), `BusinessTravel` (Non-Travel, Travel_Rarely, Travel_Frequently), `DistanceFromHome`.
- **Satisfaction & Engagement:** `JobSatisfaction` (1–4), `EnvironmentSatisfaction` (1–4), `WorkLifeBalance` (1–4), `JobInvolvement` (1–4), `RelationshipSatisfaction` (1–4).
- **Role & Compensation:** `Department`, `JobRole`, `JobLevel`, `MonthlyIncome`, `PercentSalaryHike`, `StockOptionLevel`.

### 3.4 Feature Cleansing Guardrail
- Drop zero-variance non-informative constants: `EmployeeCount` (=1 for all), `StandardHours` (=80 for all), `Over18` (=Y for all).
- Exclude unique surrogate keys: `EmployeeNumber`.
- Fit scaling and encoding exclusively on training fold.
