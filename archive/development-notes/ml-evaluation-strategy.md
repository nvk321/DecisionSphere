# DecisionSphere — Machine Learning Evaluation Strategy

To avoid common academic pitfalls (such as reporting only raw accuracy on imbalanced data or relying on uncalibrated probabilities), DecisionSphere establishes a disciplined, evidence-based evaluation protocol.

---

## 1. Domain-Specific Evaluation Metrics

### 1.1 Demand Forecasting
| Metric | Formula | Justification / Role |
|---|---|---|
| **MAE** (Mean Absolute Error) | $\frac{1}{N}\sum |y_i - \hat{y}_i|$ | Interpretable linear scale penalty in actual product unit sales. |
| **RMSE** (Root Mean Squared Error) | $\sqrt{\frac{1}{N}\sum (y_i - \hat{y}_i)^2}$ | Strongly penalizes catastrophic stockout under-predictions or severe over-orders. |
| **WAPE / sMAPE** | $\frac{\sum |y_i - \hat{y}_i|}{\sum y_i}$ / $\frac{100\%}{N}\sum \frac{|y_i - \hat{y}_i|}{(|y_i|+|\hat{y}_i|)/2}$ | Scale-independent percentage error suitable for comparing across heterogeneous product categories. |

### 1.2 Supply Chain Risk Classification (Late Delivery)
| Metric | Justification / Role |
|---|---|
| **ROC-AUC** | Evaluates ranking capability across all probability thresholds. |
| **PR-AUC** (Average Precision) | Critical for assessing precision-recall trade-offs when identifying delayed orders. |
| **Recall (Class 1 - Late)** | Maximizing detection of late shipments before dispatch to allow proactive routing. |
| **Precision (Class 1 - Late)** | Prevents false alarms that waste expensive expedited shipping resources. |
| **F1-Score** | Harmonic balance between delay detection and false intervention warnings. |

### 1.3 Workforce / HR Attrition Classification
| Metric | Justification / Role |
|---|---|
| **PR-AUC (Precision-Recall AUC)** | Essential because positive attrition cases comprise only ~16% of observations. |
| **ROC-AUC** | Measures discriminative power between staying and leaving employees. |
| **Recall (Class 1 - Attrition)** | Critical in organizational retention: missing an employee about to resign is costly. |
| **F1-Score** (Macro & Class 1) | Replaces raw accuracy to avoid naive majority-class guessing. |
| **Brier Score / Calibration Curve** | Ensures predicted probabilities reflect empirical likelihoods when propagated to business cost calculations. |

---

## 2. Validation & Splitting Methodology

### 2.1 Time Series (Demand)
- **Chronological Window Validation:**
  - Training Window: Earliest $70\%$ of time period.
  - Validation Window: Subsequent $15\%$ of time period (hyperparameter tuning).
  - Test Window: Final $15\%$ of time period (unseen holdout evaluation).
- No random k-fold cross-validation is permitted on time series data.

### 2.2 Tabular Classification (Supply Chain & HR)
- **Stratified Split:**
  - Preserves target class ratio across Train ($70\%$), Validation ($15\%$), and Test ($15\%$) splits.
  - 5-Fold Stratified Cross-Validation on the training partition for hyperparameter tuning.

---

## 3. Candidate Algorithm Hierarchy & Baselines

For every domain, models must be compared systematically from simple baselines to competitive estimators:

1. **Level 0 (Naive Baseline):**
   - Demand: Historical mean, last observed value ($t-7$ seasonal persistence).
   - Classification: Majority class assignment, Stratified random baseline.
2. **Level 1 (Linear / Regularized Statistical Baseline):**
   - Demand: Ridge / Lasso Regression with time/calendar features, ARIMA.
   - Classification: Logistic Regression with L2 regularization.
3. **Level 2 (Non-Linear Ensemble Models):**
   - Random Forest Classifier / Regressor.
   - LightGBM / XGBoost with early stopping.
4. **Model Selection Criterion:**
   - Final model selection is driven by validation metrics, inference latency ($<50\text{ms}$ per batch), and model size, rather than chasing marginal score differences with unwieldy architectures.
