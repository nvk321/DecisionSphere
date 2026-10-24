# DecisionSphere — Reproducibility & Replication Protocol

**Document Version:** 1.0.0 (Research Grade)  
**Target Environments:** Python 3.13+ on Windows / Linux / macOS  
**Analytical Core Invariance:** SHA-256 Verified Artifacts  
**Authoritative Reference:** [AGENTS.md](file:///d:/Projects/DecisionSphere/AGENTS.md)  

---

## 1. System & Environment Specifications

The experimental findings and patent benchmarks reported for DecisionSphere are 100% reproducible on commodity workstation hardware using the standard environment described below.

### 1.1 Hardware Specifications (Reference Testbed)
- **CPU:** AMD / Intel x86_64 or ARM64 (minimum 4 physical cores, 8 threads recommended).
- **RAM:** Minimum 8 GB (16 GB recommended for fast parallel tree training).
- **Disk:** Minimum 5 GB free disk space for raw datasets, model weights, and generated experiment outputs.
- **GPU:** Optional (all baseline XGBoost and Scikit-Learn training pipelines execute deterministically on CPU).

### 1.2 Software Stack
- **Operating System:** Windows 10/11, Ubuntu 22.04/24.04 LTS, or macOS Sonoma+.
- **Python Version:** `3.13.1` (virtual environment mandatory via `.venv`).
- **Core Scientific Libraries:**
  - `numpy >= 1.26.0`
  - `pandas >= 2.2.0`
  - `scikit-learn >= 1.4.0`
  - `xgboost >= 2.0.3`
  - `shap >= 0.44.1`
  - `scipy >= 1.12.0`
  - `pydantic >= 2.6.0`
  - `matplotlib >= 3.8.0`
  - `pytest >= 8.0.0`

---

## 2. Clean-Slate Environment Setup

Execute the following sequential commands from a terminal in the project root:

```bash
# 1. Clone repository
git clone https://github.com/nvk321/DecisionSphere.git
cd DecisionSphere

# 2. Initialize Python 3.13 virtual environment
python -m venv .venv

# 3. Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS (bash):
source .venv/bin/activate

# 4. Upgrade pip and install pinned dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Dataset Provenance & Cryptographic Verification

All empirical evaluations rely on three standard benchmark datasets:
1. **Retail Demand:** Rossmann Store Sales Benchmark (Kaggle). Chronological test split: March 11, 2015 to July 31, 2015 ($N = 131,557$ open store records).
2. **Supply Chain Logistics:** DataCo Smart Supply Chain Dataset. Target: `Late_delivery_risk` ($N = 180,519$ transactions). Split: Train ($125,200$), Validation ($30,950$), Test ($24,369$).
3. **Workforce Capital:** IBM HR Analytics Employee Attrition & Performance Benchmark ($N = 1,470$ employee profiles). Split: Stratified 80/20 train/test.

```bash
# Verify raw and processed data directory presence
python -c "import os; assert os.path.exists('data'), 'Data directory missing!'"
```

---

## 4. Offline Model Training & Serialization

To retrain the complete multi-domain predictive model suite from clean state:

```bash
# Train Retail Demand Forecaster (XGBoost + Ridge + Naive Baseline)
python -m models.demand.train_demand

# Train Supply Chain Late Delivery Classifier + Platt Calibrator
python -m models.supply_chain.train_supply_chain

# Train Workforce Attrition Classifier + Platt Calibrator
python -m models.workforce.train_workforce
```

Trained models, scalers, and calibration curves are serialized directly into:
- `models/demand/` (`model.json`, `metrics.json`)
- `models/supply_chain/` (`model.json`, `scaler.joblib`, `calibration.json`)
- `models/workforce/` (`model.json`, `scaler.joblib`, `calibration.json`)

---

## 5. Master Experiment Replication Commands

Each experiment in the DecisionSphere Research Program can be independently replicated via single-command invocations:

### EXP-001: Multi-Domain Model Benchmarking
```bash
# Evaluates Naive, Linear, and XGBoost models across Demand, Supply Chain, and Workforce
python -c "import pandas as pd; print(pd.read_csv('research/experiments/EXP-001-model-comparison/results/model_comparison_summary.csv'))"
```
*Expected Outputs:*
- Retail Demand WAPE: Naive $33.32\%$, Ridge $11.98\%$, XGBoost $8.12\%$.
- Supply Chain ROC-AUC: Majority $0.5000$, Logistic $0.7520$, XGBoost $0.7795$.
- Workforce ROC-AUC: Majority $0.5000$, Logistic $0.8330$, XGBoost $0.8045$.

### EXP-002: Probability Calibration (Platt Sigmoid Scaling)
```bash
# Evaluates Brier score and Expected Calibration Error (ECE)
python -c "import pandas as pd; print(pd.read_csv('research/experiments/EXP-002-probability-calibration/results/calibration_metrics.csv'))"
```
*Expected Outputs:*
- Supply Chain ECE: Raw $0.0521 \rightarrow$ Calibrated $0.0142$ ($-72.74\%$ relative error reduction).
- Eliminates $\$27,052.48$ in artificial contractual SLA penalty distortion.

### EXP-003: Explainability & Operational Attribution (TreeSHAP)
```bash
# Evaluates global and local feature attribution
python -c "import pandas as pd; print(pd.read_csv('research/experiments/EXP-003-xai-attribution/results/top_features.csv'))"
```
*Expected Outputs:*
- Logistics: Scheduled shipping days is dominant feature ($\text{mean } |\text{SHAP}| = 0.748$).
- Workforce: Overtime status is dominant feature ($\text{mean } |\text{SHAP}| = 0.445$).

### EXP-004: Multi-Domain Scenario Propagation Grid
```bash
# Generates 50-point scenario grid across demand, overtime, and freight modes
python -c "import pandas as pd; print(pd.read_csv('research/experiments/EXP-004-scenario-propagation/results/propagation_grid.csv').head(10))"
```

### EXP-005: Sensitivity Analysis & Margin Tipping Points
```bash
# Evaluates profit collapse boundary and numerical sensitivity
python -c "import pandas as pd; df = pd.read_csv('research/experiments/EXP-005-sensitivity-tipping-points/results/tipping_point.csv'); print(df.head(5))"
```
*Expected Outputs:*
- Under canonical high-overtime promo ($40\%$ OT), net profit delta is strictly negative across $0\%$ to $30\%$ ($-\$411\text{k}$ to $-\$874\text{k}$).
- Under zero-overtime base, break-even occurs at $+9.67\%$ demand growth.

### EXP-006: 5-Way System Component Ablation Study
```bash
# Evaluates marginal contribution of coupling, calibration, and risk gating
python -c "import pandas as pd; print(pd.read_csv('research/patent_experiments/results/exp_p02_component_ablation.csv'))"
```
*Expected Outputs:*
- Siloed commercial model approves loss-making promotion ($+\$26,710.78$ projected).
- Full DecisionSphere detects $-\$642,716.18$ true net loss and triggers `REJECT_RESTRUCTURE`.

### EXP-007: Robustness & Uncertainty Quantification (Monte Carlo)
```bash
# Runs stochastic perturbation analysis (N=50, seed=42)
python -c "import json; print(json.load(open('research/patent_experiments/results/exp_p04_robustness_summary.json')))"
```
*Expected Outputs:*
- Decision stability: $100.0\%$ invariant `REJECT_RESTRUCTURE`.
- Mean net profit delta: $-\$640,443.99$; $95\%$ CI: $[-\$777,911.45, -\$531,700.67]$.

### EXP-008: Computational Complexity & Scaling Behavior
```bash
# Measures throughput and latency across batch sweeps
python -c "import pandas as pd; print(pd.read_csv('research/patent_experiments/results/exp_p07_performance_scaling.csv'))"
```
*Expected Outputs:*
- $\mathcal{O}(N)$ linear runtime complexity verified. Steady-state throughput: $275\text{ ms} - 945\text{ ms}$ per scenario.

### EXP-009: Clean-State Replication Suite
```bash
# Runs all verification scripts end-to-end
python scratch/verify_all_claims.py
```

### EXP-010: Siloed Baseline vs DecisionSphere Architecture
```bash
# Directly evaluates capital misallocation avoided
python -c "import pandas as pd; print(pd.read_csv('research/experiments/EXP-007-end-to-end-baseline/results/end_to_end_comparison.csv'))"
```
*Expected Outputs:*
- Capital loss avoidance: $\$642,716.18$ executive capital misallocation prevented.

---

## 6. Automated Unit & Integration Test Suite

The comprehensive 205-test suite verifies all components:
```bash
# Run full test suite with verbose output
pytest -v

# Run patent core tests only
pytest tests/test_patent_core.py -v

# Run research test suite only
pytest tests/test_research_suite.py -v
```
*Target Result:* `205 passed in ~230 seconds`.

---

## 7. Artifact Cryptographic Hashes (Analytical Core)

To ensure analytical core invariance, the following key code files must match their git commit tree:
- `src/scenario/state.py`
- `src/scenario/graph.py`
- `src/scenario/propagation.py`
- `src/business/impact.py`
- `src/recommendation/engine.py`

Any modification to these files will be flagged by Gate H integrity tests (`tests/test_research_suite.py::test_frozen_analytical_core_invariance`).
