# DecisionSphere: Research Paper — Chapter 6: Machine Learning Model Architecture & Calibration

**Section:** 5. Predictive Machine Learning Architecture  
**Context:** Mathematical Formulations, Hyperparameters, Loss Functions, Calibration, and TreeSHAP

---

### 5.1 Extreme Gradient Boosting (XGBoost) Rationale
For all three domain models, DecisionSphere implements Extreme Gradient Boosting (Chen & Guestrin 2016). Tree-based gradient boosting was selected over deep neural architectures due to its established superiority on tabular datasets (Grinsztajn et al. 2022), sub-millisecond inference latency, robustness to extreme value distributions, and native support for exact polynomial-time TreeSHAP ($O(TLD^2)$).

---

### 5.2 Model Formulations & Specifications

#### 5.2.1 Retail Demand: Autoregressive Multi-Step Regressor
- **Architecture:** `XGBRegressor` with squared error loss $\mathcal{L}(y, \hat{y}) = \frac{1}{2}(y - \hat{y})^2$.
- **Hyperparameters:** `n_estimators=300`, `max_depth=6`, `learning_rate=0.05`, `subsample=0.8`, `colsample_bytree=0.8`.
- **Feature Set (18 features):** DayOfWeek, Month, DayOfMonth, WeekOfYear, Promo, StateHoliday, SchoolHoliday, StoreType, Assortment, LogCompetitionDistance, Promo2, Promo2Active, plus autoregressive lag features ($y_{t-1}, y_{t-7}, y_{t-14}$) and rolling statistics (7-day and 14-day rolling means).
- **Multi-Step Recursive Inference:**
  For a 14-day planning horizon, future true sales are unobserved. The model performs recursive autoregressive forecasting:
  $$\hat{y}_{t+k} = f_{\text{XGB}}(\mathbf{x}_{\text{calendar}}, \hat{y}_{t+k-1}, \dots, \hat{y}_{t+k-7})$$
  dynamically updating the historical lag buffer at each forward step.

#### 5.2.2 Supply Chain: Order-Time Delivery Risk Classifier
- **Architecture:** `XGBClassifier` with binary logistic loss wrapped in `CalibratedClassifierCV(method='sigmoid')`.
- **Hyperparameters:** `n_estimators=250`, `max_depth=5`, `learning_rate=0.08`, `scale_pos_weight=1.0`.
- **Feature Set (14 order-time features):** Scheduled Days for Shipment, Shipping Mode, Order Item Quantity, Benefit per order, Sales per customer, Customer Segment, Delivery Region, Order Month, Order DayOfWeek.
- **Discrimination Threshold:** $\tau^* = 0.1700$ (optimized for balanced recall).

#### 5.2.3 Workforce Retention: Turnover Risk Classifier
- **Architecture:** `XGBClassifier` with binary logistic loss wrapped in `CalibratedClassifierCV(method='sigmoid')`.
- **Hyperparameters:** `n_estimators=200`, `max_depth=4`, `learning_rate=0.05`, `scale_pos_weight=2.5`.
- **Feature Set (28 organizational features):** OverTime, MonthlyIncome, Age, YearsAtCompany, TotalWorkingYears, JobRole, JobLevel, WorkLifeBalance, JobSatisfaction, EnvironmentSatisfaction, DistanceFromHome, NumCompaniesWorked.
- **Discrimination Threshold:** $\tau^* = 0.1650$ (calibrated for minority class sensitivity).

---

### 5.3 Post-Hoc Probability Calibration
Tree ensemble margins produce posterior score distributions that cluster away from the extreme probabilities. To enable valid financial calculation ($P \times \$C$), DecisionSphere implements post-hoc **Sigmoid (Platt) Scaling**:
$$\hat{P}(Y=1 \mid s) = \frac{1}{1 + \exp(A \cdot s + B)}$$
where parameters $A$ and $B$ are estimated via maximum likelihood on a held-out temporal validation split.

**Empirical Calibration Performance:**
- Supply Chain Classifier: Raw Brier Score $= 0.1012 \to$ Calibrated Brier Score $= 0.0886$ ($12.5\%$ improvement).
- Workforce Classifier: Raw Brier Score $= 0.1203 \to$ Calibrated Brier Score $= 0.0988$ ($17.9\%$ improvement).

---

### 5.4 Explainable AI via TreeSHAP
Local feature contributions are calculated using exact TreeSHAP (Lundberg et al. 2020):
$$f(\mathbf{x}) = \phi_0 + \sum_{i=1}^M \phi_i(f, \mathbf{x})$$
- In demand forecasting, `Promo` and `Lag_7` provide the largest positive SHAP attributions during promotional cycles.
- In supply chain risk, `Days for shipment (scheduled)` is the dominant negative feature (short lead times massively elevate late delivery probability).
- In workforce attrition, `OverTime` and `MonthlyIncome` dominate local feature attributions.
