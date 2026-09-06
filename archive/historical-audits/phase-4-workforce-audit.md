# DecisionSphere — Phase 4 Implementation & Empirical Audit Report
## Workforce / HR Attrition Classification Pipeline

**Status:** COMPLETED & FROZEN  
**Date:** September 5, 2026  
**Document Type:** Formal Empirical Audit & Phase Deliverable  
**Domain:** Workforce / Human Resources Risk  
**Target Variable:** $P(\text{Attrition} = 1 \mid \mathbf{X}_{\text{employee\_operational\_config}})$  
**Authoritative Dataset:** IBM HR Analytics Employee Attrition & Performance (`reference/archive (7).zip`)

---

## 1. Executive Summary

This report documents the implementation, validation, and empirical evaluation of the **Phase 4: Workforce / HR Attrition Classification Pipeline (`src/models/workforce/`)**.

Key achievements and empirical findings:
1. **Dataset Integrity:** Verified exact dimensions (1,470 employee records, 35 columns, 0 nulls) extracted from `reference/archive (7).zip`.
2. **Feature Timing & Exclusion:** Exactly 30 legitimate employee-state predictors retained; 3 zero-variance constants (`EmployeeCount`, `StandardHours`, `Over18`) and 1 database surrogate identifier (`EmployeeNumber`) strictly excluded.
3. **Partitioning Protocol:** Rigorous stratified splitting (70% Train, 15% Validation, 15% Test Holdout) guaranteeing zero sample overlap and preserving ~16.1% minority target prevalence across all partitions. Zero preprocessing leakage.
4. **Discrimination vs Baseline:** Base rate PR-AUC = 0.1629. Balanced Logistic Regression achieved PR-AUC = **0.6190** and ROC-AUC = **0.8330**. Class-weighted XGBoost achieved PR-AUC = **0.5030** and ROC-AUC = **0.8045**.
5. **Probability Calibration:** Fitting a Sigmoid calibrator via scikit-learn 1.9 `FrozenEstimator` strictly on the validation partition substantially improved probability quality on the holdout test set (Brier score dropped from 0.1415 to **0.1086**; ECE dropped from 0.1723 to **0.0537**).
6. **Decision Threshold Selection:** Selected threshold $\tau^* = 0.2100$ strictly on Validation calibrated probabilities to maximize validation $F_1$. Evaluated once on test holdout, yielding $F_1 = 0.4706$, Precision = 0.4082, Recall = 0.5556, and Specificity = 0.8432.
7. **Explainability & Stability:** Empirical TreeSHAP attribution on test holdout ($N=221$) ranked `OverTime` as the #1 predictive feature (mean absolute SHAP = 0.4450), followed by equity/compensation (`StockOptionLevel` 0.3434, `MonthlyIncome` 0.2698), `Age` (0.2413), and `JobRole` (0.2398).
8. **Inference & Scenario Simulation:** Production inference service benchmarked at **19.1 ms / 1,000 employees** (0.019 ms/employee). Scenario simulation verifies baseline invariance (non-mutation), mathematical delta precision, and strictly non-causal epistemic labeling (`PREDICTED`).
9. **Full Test Suite:** 14 dedicated workforce tests passed; full test suite (33 tests) passing with 0 regressions.

---

## 2. Dataset Audit & Provenance

The IBM HR dataset was extracted from the authoritative archive `reference/archive (7).zip` (`WA_Fn-UseC_-HR-Employee-Attrition.csv`).

| Metric / Attribute | Value | Verification Status |
|---|---|---|
| **Archive Source** | `reference/archive (7).zip` | Verified Authoritative |
| **Row Count** | 1,470 | Verified Exact |
| **Column Count** | 35 | Verified Exact |
| **Missing Values** | 0 nulls across all 35 columns (100% complete) | Verified Exact |
| **Target Column** | `Attrition` (`str`: `'Yes'`, `'No'`) | Mapped to $\{0, 1\}$ |
| **Class Distribution (Raw)** | `No`: 1,233 (83.88%), `Yes`: 237 (16.12%) | Verified Exact |
| **Temporal Data** | None present (cross-sectional survey snapshot) | Stratified Protocol Required |

---

## 3. Feature Exclusion Matrix & Operational Timing

Every column in `WA_Fn-UseC_-HR-Employee-Attrition.csv` was audited and categorized:

| Column Name | Type | Missing | Role / Category | Final Action & Academic Rationale |
|---|---|---|---|---|
| `Attrition` | `str` | 0 | **TARGET VARIABLE** | Binary target: mapped to `target_attrition` (`Yes` $\rightarrow 1$, `No` $\rightarrow 0$). Excluded from $X$. |
| `EmployeeCount` | `int64` | 0 | **ZERO-VARIANCE INVARIANT** | **STRICTLY EXCLUDED.** Invariant constant: all 1,470 rows equal $1$. |
| `StandardHours` | `int64` | 0 | **ZERO-VARIANCE INVARIANT** | **STRICTLY EXCLUDED.** Invariant constant: all 1,470 rows equal $80$. |
| `Over18` | `str` | 0 | **ZERO-VARIANCE INVARIANT** | **STRICTLY EXCLUDED.** Invariant constant: all 1,470 rows equal `'Y'`. |
| `EmployeeNumber` | `int64` | 0 | **SURROGATE IDENTIFIER** | **STRICTLY EXCLUDED.** Database key (1 to 2,068). Memorization risk. |
| `OverTime` | `str` | 0 | **CORE SCENARIO LEVER** | **RETAINED.** Active overtime (`Yes`/`No`). Primary operational workload lever. |
| `Age` | `int64` | 0 | Demographic | **RETAINED.** Employee age (18 to 60). Numerical predictor. |
| `BusinessTravel` | `str` | 0 | Operational Travel | **RETAINED.** `Non-Travel`, `Travel_Rarely`, `Travel_Frequently`. Categorical predictor. |
| `DailyRate` | `int64` | 0 | Compensation Metric | **RETAINED.** Daily compensation rate. Numerical predictor. |
| `Department` | `str` | 0 | Organizational Unit | **RETAINED.** `Sales`, `Research & Development`, `Human Resources`. Categorical predictor. |
| `DistanceFromHome` | `int64` | 0 | Operational Commute | **RETAINED.** Commute distance (1 to 29 miles). Numerical predictor. |
| `Education` | `int64` | 0 | Qualification Level | **RETAINED.** Education tier (1 to 5). Ordinal numerical predictor. |
| `EducationField` | `str` | 0 | Discipline | **RETAINED.** `Life Sciences`, `Medical`, `Marketing`, etc. Categorical predictor. |
| `EnvironmentSatisfaction`| `int64` | 0 | Pulse Survey Rating | **RETAINED.** Workplace rating (1 to 4). Ordinal numerical predictor. |
| `Gender` | `str` | 0 | Demographic | **RETAINED.** `Female`, `Male`. Categorical predictor. |
| `HourlyRate` | `int64` | 0 | Compensation Metric | **RETAINED.** Hourly compensation rate. Numerical predictor. |
| `JobInvolvement` | `int64` | 0 | Engagement Survey | **RETAINED.** Involvement rating (1 to 4). Ordinal numerical predictor. |
| `JobLevel` | `int64` | 0 | Hierarchy Tier | **RETAINED.** Seniority tier (1 to 5). Ordinal numerical predictor. |
| `JobRole` | `str` | 0 | Organizational Role | **RETAINED.** 9 discrete job roles. Categorical predictor. |
| `JobSatisfaction` | `int64` | 0 | Pulse Survey Rating | **RETAINED.** Role satisfaction rating (1 to 4). Ordinal numerical predictor. |
| `MaritalStatus` | `str` | 0 | Demographic | **RETAINED.** `Single`, `Married`, `Divorced`. Categorical predictor. |
| `MonthlyIncome` | `int64` | 0 | Base Compensation | **RETAINED.** Base monthly salary ($1,009 to $19,999). Numerical predictor. |
| `MonthlyRate` | `int64` | 0 | Compensation Metric | **RETAINED.** Monthly metric. Numerical predictor. |
| `NumCompaniesWorked` | `int64` | 0 | Mobility History | **RETAINED.** Prior employers (0 to 9). Numerical predictor. |
| `PercentSalaryHike` | `int64` | 0 | Compensation Growth | **RETAINED.** Last raise percentage (11% to 25%). Numerical predictor. |
| `PerformanceRating` | `int64` | 0 | Review Rating | **RETAINED.** Last review rating (3 to 4). Ordinal numerical predictor. |
| `RelationshipSatisfaction`| `int64` | 0 | Workplace Survey | **RETAINED.** Team relationship rating (1 to 4). Ordinal numerical predictor. |
| `StockOptionLevel` | `int64` | 0 | Equity Incentive | **RETAINED.** Equity tier (0 to 3). Ordinal numerical predictor. |
| `TotalWorkingYears` | `int64` | 0 | Career Experience | **RETAINED.** Cumulative working years (0 to 40). Numerical predictor. |
| `TrainingTimesLastYear`| `int64` | 0 | Professional Dev | **RETAINED.** Training events (0 to 6). Numerical predictor. |
| `WorkLifeBalance` | `int64` | 0 | Wellbeing Survey | **RETAINED.** Balance rating (1 to 4). Ordinal numerical predictor. |
| `YearsAtCompany` | `int64` | 0 | Firm Tenure | **RETAINED.** Company tenure (0 to 40). Numerical predictor. |
| `YearsInCurrentRole` | `int64` | 0 | Role Tenure | **RETAINED.** Role tenure (0 to 18). Numerical predictor. |
| `YearsSinceLastPromotion`| `int64` | 0 | Promotion Velocity | **RETAINED.** Years since promotion (0 to 15). Numerical predictor. |
| `YearsWithCurrManager` | `int64` | 0 | Manager Stability | **RETAINED.** Manager tenure (0 to 17). Numerical predictor. |

*Modeling Matrix Total:* **Exactly 30 input predictors** (23 continuous/ordinal numerical, 7 nominal categorical).

---

## 4. Actual Stratified Partition Counts & Class Prevalences

Partitioning executed via `split_stratified_ibm_hr(df_feat, random_state=42)` prior to fitting any transformer:

| Partition | Total Rows | Negative (`Attrition=0`) | Positive (`Attrition=1`) | Target Prevalence | Partition Role |
|---|---|---|---|---|---|
| **TRAIN** | **1,029** (70.0%) | 863 (83.87%) | 166 (16.13%) | **16.13%** | Preprocessing fit & base model training |
| **VALIDATION** | **220** (15.0%) | 185 (84.09%) | 35 (15.91%) | **15.91%** | Sigmoid calibration fit & threshold $\tau^*$ selection |
| **TEST HOLDOUT**| **221** (15.0%) | 185 (83.71%) | 36 (16.29%) | **16.29%** | Untouched final evaluation (evaluated once) |
| **TOTAL** | **1,470** (100.0%) | 1,233 (83.88%) | 237 (16.12%) | **16.12%** | Complete dataset census |

*Empirical Class Weight:*
$$\text{scale\_pos\_weight} = \frac{N_{\text{neg, train}}}{N_{\text{pos, train}}} = \frac{863}{166} = \mathbf{5.1988}$$

---

## 5. Untouched Test Holdout Evaluation Results

All metrics below were evaluated **strictly once** on the holdout test partition ($N=221$, positive prevalence = 16.29%):

| Metric | Level 0b (Prevalence Baseline) | Level 1 (Logistic Regression) | Level 2 (XGBoost Raw @ 0.50) | Level 2 (XGBoost Calibrated @ 0.50) | Level 2 (XGBoost Calibrated @ $\tau^*=0.21$) |
|---|---|---|---|---|---|
| **PR-AUC** (Primary) | 0.1629 | **0.6190** | 0.5030 | 0.5030 | 0.5030 |
| **ROC-AUC** (Secondary)| 0.5000 | **0.8330** | 0.8045 | 0.8045 | 0.8045 |
| **Brier Score** (lower=better)| 0.1364 | 0.1578 | 0.1415 | **0.1086** | **0.1086** |
| **Expected Cal. Error (ECE)**| 0.0016 | 0.1929 | 0.1723 | **0.0537** | **0.0537** |
| **Decision Threshold ($\tau$)** | 0.5000 | 0.5000 | 0.5000 | 0.5000 | **0.2100** (Tuned on Val) |
| **$F_1$-Score** | 0.0000 | 0.4587 | **0.4878** | 0.3404 | **0.4706** |
| **Precision** | 0.0000 | 0.3425 | 0.4348 | **0.7273** | 0.4082 |
| **Recall** | 0.0000 | **0.6944** | 0.5556 | 0.2222 | 0.5556 |
| **Specificity** | **1.0000** | 0.7405 | 0.8595 | 0.9838 | 0.8432 |
| **Accuracy** | 0.8371 | 0.7330 | 0.8100 | **0.8597** | 0.7964 |

### Honest Empirical Trade-Off Assessment:
1. **Discrimination:** Balanced Logistic Regression achieved higher PR-AUC (0.6190 vs 0.5030) and ROC-AUC (0.8330 vs 0.8045) than XGBoost on this small dataset ($N=1,470$). Linear L2 regularization provides effective constraint on small tabular sample sizes, while XGBoost captures non-linear interactions and produces localized TreeSHAP values. We report this trade-off honestly without forcing XGBoost to dominate.
2. **Probability Quality:** Sigmoid calibration on validation via `FrozenEstimator` produced dramatic probability improvements on the test holdout:
   - Brier score dropped from 0.1415 (Raw) to **0.1086** (Calibrated).
   - Expected Calibration Error (ECE) dropped from 0.1723 (Raw) to **0.0537** (Calibrated).
3. **Threshold Selection ($\tau^* = 0.21$):** Because the base positive rate is ~16%, the standard 0.50 threshold yields low recall (0.2222) after calibration. Tuning $\tau^*$ strictly on validation F1 selected $\tau^* = 0.2100$. On the test holdout, this restores balanced classification performance: $F_1 = 0.4706$, Recall = 0.5556, Precision = 0.4082, and Specificity = 0.8432.

---

## 6. TreeSHAP Attribution & Stability Analysis

TreeSHAP values computed on the holdout test set ($N=221$) revealed the following empirical rankings:

| Rank | Feature | Mean Absolute SHAP ($I_j$) | Operational Domain | Directional Finding |
|---|---|---|---|---|
| 1 | `OverTime` | **0.4450** | Operational Workload | Active overtime is the strongest statistical contributor to model log-odds. |
| 2 | `StockOptionLevel` | **0.3434** | Equity Compensation | Low stock options correlate with elevated predicted attrition. |
| 3 | `MonthlyIncome` | **0.2698** | Base Compensation | Lower monthly compensation elevates predicted attrition risk. |
| 4 | `Age` | **0.2413** | Demographic / Life Stage | Younger employees exhibit higher baseline mobility in the dataset. |
| 5 | `JobRole` | **0.2398** | Organizational Role | Sales Representatives and Lab Technicians exhibit elevated predicted risk. |
| 6 | `TotalWorkingYears`| **0.2120** | Career Tenure | Cumulative experience acts as a retention buffer. |
| 7 | `YearsAtCompany` | **0.1754** | Organizational Tenure | Early-tenure employees exhibit higher churn propensity. |
| 8 | `YearsInCurrentRole`| **0.1685** | Role Stagnancy | Low role tenure elevates attrition probability. |
| 9 | `WorkLifeBalance` | **0.1412** | Employee Wellbeing | Poor work-life balance ratings correlate with elevated risk. |
| 10 | `JobInvolvement` | **0.1387** | Employee Engagement | Low engagement ratings elevate predicted turnover probability. |

**Stability Analysis:** Evaluating TreeSHAP attributions across two deterministic test halves ($N_1 = 110$, $N_2 = 111$) demonstrated **5/5 concordance** in top-5 feature membership (`OverTime`, `StockOptionLevel`, `MonthlyIncome`, `Age`, `JobRole`), confirming statistical robustness across the holdout partition.

---

## 7. Scenario Simulation & Epistemic Framing

### 7.1 Scenario Simulation Contract
The inference service exposes `simulate_scenario(employees_df, overtime_override, salary_hike_override)`:
- Baseline invariance verified: input DataFrame is not mutated.
- Numerical delta precision verified: $\Delta P = P_{\text{scenario}} - P_{\text{baseline}}$.
- Epistemic tier tagged strictly as `"PREDICTED"`.

### 7.2 Empirical Scenario Example
Evaluating a single employee record with `OverTime` toggled from `'No'` to `'Yes'`:
- Baseline predicted attrition probability: **4.9%**
- Scenario predicted attrition probability (`OverTime = 'Yes'`): **6.8%**
- Conditional probability delta ($\Delta P$): **+2.0%**
- Phrasing: *"Model-predicted mean attrition probability shifted from 4.9% to 6.8% (+2.0%) under the assumed feature modification. The scenario modification represents an assumed change to an input feature and is not evidence of a causal effect."*

---

## 8. Automated Test Suite & Regression Verification

Automated test execution via Python 3.13:
```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```
**Result: 33 passed, 0 failed in 14.34s**
- `tests/test_demand_pipeline.py`: 5 passed
- `tests/test_demand_inference.py`: 3 passed
- `tests/test_supply_chain_pipeline.py`: 5 passed
- `tests/test_supply_chain_inference.py`: 6 passed
- `tests/test_workforce_pipeline.py`: 5 passed
- `tests/test_workforce_inference.py`: 9 passed

**Inference Latency Benchmarks:**
- Single-employee prediction: **53.7 ms** (cold init), **4.2 ms** (warm).
- Batch prediction (1,000 employees): **19.1 ms** (0.019 ms/employee).

---

## 9. Serialized Artifacts Inventory (`models/workforce/`)

| File Name | File Size | Description |
|---|---|---|
| [`workforce_model.joblib`](file:///d:/Projects/DecisionSphere/models/workforce/workforce_model.joblib) | 0.13 MB | Preprocessor, base XGBoost, Sigmoid calibrator, threshold $\tau^*=0.21$, feature names, metadata. |
| [`metrics.json`](file:///d:/Projects/DecisionSphere/models/workforce/metrics.json) | 8.89 KB | Complete validation and test holdout evaluation across Level 0, Level 1, Level 2 Raw, and Level 2 Calibrated. |
| [`confusion_matrix.json`](file:///d:/Projects/DecisionSphere/models/workforce/confusion_matrix.json) | 0.62 KB | Confusion matrices for validation and test evaluations. |
| [`calibration.json`](file:///d:/Projects/DecisionSphere/models/workforce/calibration.json) | 1.94 KB | 10-bin calibration curves for all evaluated models. |
| [`feature_importance.json`](file:///d:/Projects/DecisionSphere/models/workforce/feature_importance.json) | 4.88 KB | Empirical TreeSHAP attributions and 5/5 concordance stability analysis. |
| [`experiment_metadata.json`](file:///d:/Projects/DecisionSphere/models/workforce/experiment_metadata.json) | 2.12 KB | Reproducibility metadata, split counts, random seeds, and software versions. |

---

## 10. Research Integrity & Epistemic Compliance

1. **Non-Causal Demarcation:** The model predicts conditional probabilities $P(\text{Attrition}=1 \mid \mathbf{X})$. It does NOT claim to identify causal mechanisms of resignation or prove that overtime causes attrition.
2. **Decoupled Business Impact:** Operational assumptions (`ASM-004` replacement cost, `ASM-005` overtime wage premium) remain strictly quarantined for Phase 7 and are not claimed as learned parameters of the ML model.
3. **No Retrofitting:** The test partition was evaluated strictly once using the threshold tuned on the validation set. Discrepancies between models (Logistic Regression vs. XGBoost) are reported with complete empirical transparency.
