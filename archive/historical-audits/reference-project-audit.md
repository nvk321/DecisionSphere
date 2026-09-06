# DecisionSphere — Reference Projects & Baseline Implementations Audit

## 1. Executive Summary & Purpose

The `reference/` directory contains legacy student projects, external notebooks, and codebases provided as initial references. In accordance with project governance, **reference implementations must never be assumed to be correct, academically sound, or authoritative**. 

This document provides a thorough audit of the code, feature engineering, validation strategies, and modeling choices in these reference repositories. It documents specific methodological flaws—including target leakage, improper time-series splitting, and evaluation metric errors—and records the architectural safeguards established in DecisionSphere to prevent these errors.

---

## 2. Audited Reference Projects

| Archive / Repository | Domain / Dataset | Stated Objective | Core Model(s) | Key Methodological Flaws Identified |
|---|---|---|---|---|
| `Rossmann-Store-Sales-Prediction-master.zip` | Demand (Rossmann) | Predict daily store sales | Linear Regression, Random Forest, GBDT | **Fatal contemporaneous target leakage** (`Customers` feature); **Random time split**; Arbitrary 70k row truncation |
| `rossman-store-sales-main.zip` | Demand (Rossmann) | End-to-end sales prediction with Flask API | XGBoost Regressor | Isolated single-domain API; No scenario simulation; No supply chain/workforce coupling |
| `IBM-HR-Analytics-Employee-Attrition-and-Performance-Prediction-main.zip` | Workforce (IBM HR) | Predict employee attrition & performance | Logistic Regression, Random Forest, XGBoost, CatBoost | **Incorrect ROC-AUC evaluation** (passed binary predictions `0/1` instead of probabilities); No PR-AUC despite 16% class imbalance |
| `Project4_Store_Sales_Forecasting-master.zip` | Demand (Walmart) | Weekly store sales forecasting | Random Forest Regressor | Weekly granularity (insufficient for daily operational ripple); Non-temporal index slicing across multi-store panel |
| `tp2-walmart-sales-forecast.ipynb` | Demand (Walmart) | Exploratory sales forecasting | Linear / Tree baselines | Exploratory script; High missingness in markdowns (>50%); No cross-functional integration |

---

## 3. Deep Dive: Technical Findings & Flaws

### 3.1 `Rossmann-Store-Sales-Prediction-master.zip`
- **Code Inspected:** `Final_submission.py`, `Final_submission.ipynb`
- **Flaw 1: Contemporaneous Target Leakage (`Customers`)**
  - The implementation explicitly included `Customers`, `AvgCustomers`, and `MedCustomers` in the feature matrix $X$:
    ```python
    X = ['Customers', 'AvgCustomers', 'MedCustomers', ...]
    ```
  - It additionally engineered `SalesPerCustomer = train['Sales'] / train['Customers']`, directly leaking the ground-truth target `Sales`.
  - *Academic Critique:* In an operational deployment, daily customer footfall is unknown in advance. Conditioned on actual customer count, sales prediction becomes trivial ($R^2 \approx 0.85$ correlation), masking true demand forecasting performance.
  - *DecisionSphere Safeguard:* Strictly excluded `Customers` from feature matrices (`src/data/rossmann_features.py`). Demand is predicted solely from calendar, store metadata, promo schedules, and historical lagged/rolling sales.
- **Flaw 2: Temporal Shuffling Leakage (`train_test_split`)**
  - Shuffled time-series rows randomly across time:
    ```python
    X_train, X_test, y_train, y_test = train_test_split(merge[X], merge['Sales'], test_size=0.1, random_state=10)
    ```
  - *Academic Critique:* Randomly shuffling panel time series mixes past and future observations, causing massive data leakage and generating artificially inflated test performance that collapses in production.
  - *DecisionSphere Safeguard:* Strict chronological boundary splitting (Train: 2013-01-01 to 2014-10-19; Validation: 2014-10-20 to 2015-03-10; Test: 2015-03-11 to 2015-07-31). Lags and rolling statistics are computed with strict forward temporal causality.
- **Flaw 3: Arbitrary Truncation**
  - Truncated the training dataset with `nrows = 70000`, discarding 93% of the 1,017,209 historical observations without scientific justification.
  - *DecisionSphere Safeguard:* Processed the full historical timeline (1,017,209 observations across 1,115 stores).

---

### 3.2 `IBM-HR-Analytics-Employee-Attrition-and-Performance-Prediction-main.zip`
- **Code Inspected:** `CODE/File-4-Data-Modeling.ipynb`
- **Flaw 1: Invalid ROC-AUC Calculation (Hard Binary Inputs)**
  - In Cell 28, model evaluation was implemented as:
    ```python
    scores_dict = {
        'Logistic Regression': {
            'Train': roc_auc_score(y_train, lr_clf.predict(X_train)),
            'Test': roc_auc_score(y_test, lr_clf.predict(X_test)),
        }
    }
    ```
  - Notice `lr_clf.predict(X_test)` returns discrete integer class predictions $\{0, 1\}$, NOT predicted continuous probabilities (`predict_proba(X_test)[:, 1]`).
  - *Academic Critique:* Passing hard binary thresholds to `roc_auc_score` reduces the area under the ROC curve to a single-point trapezoid, equivalent to balanced accuracy $\frac{\text{Sensitivity} + \text{Specificity}}{2}$. It fails to evaluate discrimination across decision thresholds.
  - *DecisionSphere Safeguard:* Model scoring always uses continuous calibrated posterior probabilities $P(\text{Attrition} = 1 \mid \mathbf{x}) \in [0, 1]$ via `predict_proba`.
- **Flaw 2: Omission of PR-AUC on Imbalanced Dataset**
  - The IBM HR dataset exhibits an approximate 16.1% positive attrition rate (237 positive / 1,470 total). The reference project relied exclusively on accuracy and the distorted binary ROC-AUC.
  - *Academic Critique:* Accuracy is misleading on imbalanced datasets (a dummy majority classifier achieves 83.9% accuracy with zero recall). Precision-Recall AUC (PR-AUC) and cost-weighted F-scores are necessary.
  - *DecisionSphere Safeguard:* Mandated reporting of PR-AUC, ROC-AUC, Precision, Recall, and Brier calibration score. Tree models use `scale_pos_weight` to address class distribution.
- **Flaw 3: Invariant Constant Columns Retained**
  - Failed to drop constant zero-variance features: `EmployeeCount` (all 1), `Over18` (all 'Y'), and `StandardHours` (all 80), wasting dimensionality and model memory.
  - *DecisionSphere Safeguard:* Programmatically prune zero-variance columns during pipeline ingestion.

---

### 3.3 `rossman-store-sales-main.zip`
- **Code Inspected:** `api/handler.py`, `api/rossmann/Rossmann.py`, `notebooks/cicle1_sales_prediction.ipynb`
- **Strengths Observed:**
  - Implemented chronological test split (`date >= '2015-06-19'`).
  - Organized inference logic into an object-oriented `Rossmann` class with preprocessing scalers.
  - Deployed a lightweight REST API handler.
- **Limitations & Architectural Gaps:**
  - **Siloed Single-Domain Scope:** The API only outputs raw store-level sales forecasts. It lacks any mechanism to evaluate what a sales surge means for inventory, fulfillment delays, or warehouse staffing.
  - **Static Feature Scaling:** Relies on serialized MinMax/Robust scalers on temporal features (e.g., `year_scaler`), which fail to generalize if evaluating future years beyond the training distribution.
  - **Zero Cross-Domain Propagation:** No scenario parameters, no business impact formulas, and no explainability integration.

---

### 3.4 `Project4_Store_Sales_Forecasting-master.zip` (Walmart)
- **Code Inspected:** `STEP1_Cleaning_and_EDA.ipynb`, `STEP2_Random_Forest_Regressor.ipynb`
- **Limitations & Gaps:**
  - **Weekly Aggregation:** Walmart data is recorded at weekly intervals (`Weekly_Sales`). Weekly buckets mask sharp daily demand volatility and intraday operational shocks.
  - **Severe Missingness in Promotional Levers:** Over 50% of the markdown features (`MarkDown1` to `MarkDown5`) are missing. In contrast, Rossmann contains complete daily records with explicit binary `Promo` schedules.
  - **Index-Based Train-Test Split:** Used simple index slicing `df[:int(0.7*len(df))]`. Because the DataFrame was stacked by store and department, slicing rows by positional index can split across stores at inconsistent dates.

---

## 4. Key Lessons & Architectural Safeguards for DecisionSphere

| Domain / Issue | Reference Project Error | DecisionSphere Engineering Safeguard | Research Implication |
|---|---|---|---|
| **Demand Feature Set** | Contemporaneous footfall (`Customers`) included in feature matrix | Strictly exclude `Customers`; use only pre-period historical sales lags and scheduled operational levers | Prevents artificial inflation of model accuracy; aligns with real-world forecasting boundaries |
| **Time Series Splitting** | Random `train_test_split` shuffling future into past | Strict chronological holdout splits across all temporal pipelines | Eliminates lookahead bias; ensures defensible out-of-time evaluation |
| **Imbalanced Metrics** | Discrete binary inputs passed to ROC-AUC; PR-AUC omitted | Continuous probability scoring (`predict_proba`); evaluate PR-AUC, ROC-AUC, Recall | Accurately evaluates rare-event operational risks (delays, attrition) |
| **System Scope** | Isolated prediction script or single-endpoint web app | Unified scenario propagation engine linking demand $\rightarrow$ logistics $\rightarrow$ workforce $\rightarrow$ finances | Bridges the gap between predictive ML and cross-functional strategic decision intelligence |
| **Coupling Logic** | None (models operate in complete isolation) | Formally parameterized scenario engine with explicit sensitivity testing (`ASM-001`–`ASM-008`) | Replaces ungrounded causal claims with transparent, auditable scenario simulation |
