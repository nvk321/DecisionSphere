# DecisionSphere: Research Paper — Chapter 10: Experimental Design & Setup

**Section:** 9. Experimental Design & Computational Setup  
**Context:** Hardware Configuration, Baseline Models, Parameter Sweeps, and Validation Protocol

---

### 9.1 Experimental Environment & Hardware
All experiments were executed on a dedicated laboratory testbed:
- **Processor:** Intel Core i7 / AMD Ryzen multi-threaded processor.
- **Memory:** 16 GB DDR4 RAM.
- **Operating System:** Microsoft Windows 11 Pro (x64) with PowerShell 7.
- **Runtime Environment:** Python 3.13.5 (CPython) within an isolated virtual environment (`.venv`).
- **Core Dependencies:** `xgboost==2.1.4`, `scikit-learn==1.6.1`, `pandas==2.2.3`, `numpy==2.2.3`, `shap==0.46.0`, `matplotlib==3.10.0`, `seaborn==0.13.2`.

---

### 9.2 Baseline Model Formulations
To validate the efficacy of DecisionSphere's gradient-boosted architectures, we benchmarked each against standard traditional baselines:

1. **Retail Demand Baselines:**
   - *Naive Historical Mean:* Predicts the global historical mean sales for each store.
   - *7-Day Moving Average:* Predicts the mean of the preceding 7 calendar days.
   - *Linear Ridge Regressor:* L2-regularized linear model trained on one-hot calendar features.

2. **Supply Chain Classification Baselines:**
   - *Majority Class Dummy:* Predicts the empirical majority class ($1=\text{Late}$).
   - *Logistic Regression:* L2-regularized linear logistic regression on standardized order-time features.
   - *Uncalibrated Random Forest:* 100-tree uncalibrated ensemble.

3. **Workforce Classification Baselines:**
   - *Zero-Rule Baseline:* Always predicts non-attrition ($0=\text{Retained}$).
   - *Weighted Logistic Regression:* Logistic regression with inverse class frequency reweighting.
   - *Uncalibrated XGBoost:* Raw gradient-boosted trees without post-hoc calibration.

---

### 9.3 Scenario Evaluation Test Suite
To answer RQ1 through RQ4, we executed three primary experimental suites:
1. **The Canonical Scenario Sweep (RQ1 & RQ3):**
   Fixed parameters: Baseline Rossmann store sales, DataCo order distributions, IBM HR workforce demographics.
   Perturbation: Swept commercial demand shocks from $-50\%$ to $+100\%$ in increments of $10\%$, evaluating resulting dispatch orders, carrier late delivery risk, employee attrition rate, and net profit delta.
2. **The Probabilistic Calibration Study (RQ2):**
   Evaluated Brier scores, reliability diagrams, and expected calibration errors (ECE) across 10 probability bins for both raw and Sigmoid-calibrated models on held-out test splits.
3. **The Multi-Dimensional Sensitivity Grid (RQ3 & RQ4):**
   Executed a 2D parameter grid sweep ($11 \times 11 = 121$ simulation runs) crossing demand shock ($\Delta_{\text{demand}} \in [-50\%, +100\%]$) against contractual delay penalty ($C_{\text{penalty}} \in [\$10, \$60]$) to map the non-linear profitability surface and tipping-point boundaries.
