# DecisionSphere — Patent Technical Audit & Codebase Verification Report

**Authoritative System Audit for Patent-Readiness, Novelty Analysis, and Technical Strengthening**  
**Project:** `DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform`  
**Audit Date:** 2026-10-24  
**Audit Standard:** Forensic Source Verification (Every assertion grounded in verified code on disk, `.joblib` model binaries, passing unit tests, and empirical JSON logs).

---

## 1. Executive Summary & Verification Methodology

This technical audit performs a forensic examination of the **DecisionSphere** repository to establish an unassailable baseline of:
1. What is **actually implemented** in executable code.
2. What is **partially implemented**.
3. What is **only proposed** in documentation or design notes.
4. What is **experimental** (e.g., in Jupyter notebooks or research scripts).
5. What is **documented but not implemented**.
6. What is **implemented but undocumented**.
7. The exact mathematical equations, algorithms, data contracts, and experimental evidence currently verified.

**Strict Audit Protocol:**
- No feature is declared "implemented" unless supported by working Python code, Pydantic schemas, or passing automated unit tests (201/201 passing tests verified via `pytest`).
- Model artifacts are audited against their cryptographic SHA-256 digests.
- Assumptions and coupling constants are tracked to their authoritative code registry (`src/scenario/assumptions.py`).

---

## 2. Inventory of Current Implementation Status

### 2.1 What Is Actually Implemented

| Component | Code Location | Primary Classes / Functions | Verification Artifact | Status |
|---|---|---|---|---|
| **Multi-Domain Data Loaders & Preprocessors** | `src/data/` | `load_rossmann_raw()`, `create_rossmann_features()`, `load_dataco_raw()`, `create_dataco_features()`, `load_ibm_hr_raw()`, `create_ibm_hr_features()` | `data/dataset_manifest.json`, unit tests in `tests/` | **Fully Implemented** |
| **Retail Demand Forecaster** | `src/models/demand/` | `DemandForecaster`, `predict_horizon()` | `models/demand/demand_model.joblib` (816 KB, SHA-256 verified) | **Fully Implemented** |
| **Supply Chain Delivery Risk Classifier** | `src/models/supply_chain/` | `SupplyChainInferenceService`, `predict_batch()` | `models/supply_chain/supply_chain_model.joblib` (210 KB) + `calibration.json` | **Fully Implemented** |
| **Workforce Attrition Risk Classifier** | `src/models/workforce/` | `WorkforceInferenceService`, `predict_batch()` | `models/workforce/workforce_model.joblib` (132 KB) + `calibration.json` | **Fully Implemented** |
| **Probability Calibration (Platt Sigmoid)** | `src/models/*/train.py`, `inference.py` | `CalibratedClassifierCV(method='sigmoid')`, `predict_proba()` | `models/*/calibration.json` (Platt parameters $A, B$, Brier, ECE) | **Fully Implemented** |
| **Explainable AI (TreeSHAP)** | `src/models/*/explain.py` | `TreeExplainer`, `explain_instance()`, `explain_cohort()` | `models/*/feature_importance.json`, shap plots | **Fully Implemented** |
| **Scenario Engine Orchestrator** | `src/scenario/engine.py` | `ScenarioEngine`, `run_scenario()` | 13-stage deterministic pipeline, `tests/test_scenario_engine.py` | **Fully Implemented** |
| **Scenario Data Contracts & Levers** | `src/scenario/schema.py` | `ScenarioLevers`, `ScenarioAssumptions`, `ScenarioRunResult` | Pydantic v2 schemas with strict bounds | **Fully Implemented** |
| **Assumptions Registry (ASM-001 to ASM-008)** | `src/scenario/assumptions.py` | `ASM_REGISTRY`, `AssumptionMetadata` | Immutable dataclasses, range validation | **Fully Implemented** |
| **Deterministic Overtime Assignment** | `src/scenario/engine.py:355-378` | Deterministic index slicing for overtime cohorts | Verified deterministic index sorting | **Fully Implemented** |
| **Managerial Accounting Engine** | `src/business/engine.py` | `BusinessImpactEngine`, `evaluate()` | Deterministic line-item formulas, `tests/test_business_impact.py` | **Fully Implemented** |
| **Financial Data Contracts** | `src/business/schema.py` | `BusinessAssumptions`, `FinancialLineItem`, `BusinessImpactResult` | IEEE-754 64-bit precision, no premature rounding | **Fully Implemented** |
| **Composite Risk Score (CRS)** | `src/recommendation/crs.py` | `CompositeRiskEngine`, `evaluate()` | Multi-criteria operational strain index $[0, 100]$ | **Fully Implemented** |
| **Deterministic Recommendation Rules** | `src/recommendation/rules.py` | `RuleEvaluator`, `evaluate_all()` | 7 condition-action trigger rules (RULE-01 to RULE-07) | **Fully Implemented** |
| **Lexicographic Decision Gating** | `src/recommendation/engine.py` | `RecommendationEngine`, `evaluate()` | $\Delta \Pi \le 0 \rightarrow \text{REJECT}$; $\text{CRS} \le \tau \rightarrow \text{PROCEED}$; else $\text{MITIGATE}$ | **Fully Implemented** |
| **FastAPI REST API Service** | `backend/app/` | Endpoints: `/scenarios`, `/simulations`, `/policies`, `/sensitivity` | Complete Pydantic request/response validation | **Fully Implemented** |
| **Cryptographic Runtime Integrity** | `src/scenario/engine.py:36-44`, `verify_artifact_integrity()` | Re-hashing `.joblib` files on disk prior to inference | Raises `RuntimeError` on hash mismatch | **Fully Implemented** |
| **Six-Tier Epistemic Demarcation** | Throughout `src/` | Strong typing of `OBSERVED`, `PREDICTED`, `ASSUMED`, `PROPAGATED`, `CALCULATED`, `RECOMMENDED` | Every result schema includes `epistemic_tier` | **Fully Implemented** |
| **Automated Regression Suite** | `tests/`, `backend/tests/` | 201 automated unit and integration tests | All 201 tests passing | **Fully Implemented** |

---

### 2.2 What Is Partially Implemented

1. **Parameter Sensitivity Sweeps (`src/scenario/sweep.py`, `src/business/sensitivity.py`)**:
   - *Implemented:* Discrete 1D grid sweeps over demand growth $[-50\%, +100\%]$ and overtime $[0\%, 100\%]$; 2D grid generation; break-even point calculation.
   - *Missing / Partial:* Does not compute continuous analytical gradient matrices $\nabla_{U} \Pi$ or higher-order Jacobian tensors; sensitivity is evaluated via discrete brute-force evaluation rather than an integrated state-space sensitivity operator.
2. **Frontend Decision Dashboard (`frontend/`)**:
   - *Implemented:* Next.js 15 + TypeScript UI structure with waterfall charts, scenario lever sliders, and summary cards.
   - *Missing / Partial:* Visual UI runs against mock/local API; real-time interactive multi-dimensional sensitivity exploration requires manual backend trigger.
3. **Multi-Store & Cohort Partitioning**:
   - *Implemented:* Single-store (Store 1) canonical demand baseline with 100-order DataCo holdout and 221-employee IBM HR holdout.
   - *Missing / Partial:* Multi-store aggregate enterprise roll-up is not parallelized.

---

### 2.3 What Is Only Proposed (Documented but Not Yet Implemented)

1. **ERP Database Live Ingestion Connectors (SAP / Oracle / Salesforce)**:
   - Mentioned in `docs/DECISIONSPHERE_MASTER_PROJECT_DOCUMENT.md` as the path to TRL 5/6.
   - Zero code exists for live enterprise connectors; data ingestion is strictly CSV-based from `data/raw/`.
2. **Stochastic Monte Carlo Convergence Controller**:
   - Documented in EXP-008 / EXP-009 as an asymptotic $\mathcal{O}(1/\sqrt{N})$ estimator.
   - Executed as standalone experimental scripts, but not encapsulated as an active runtime service in `backend/app/services/`.
3. **Automated Multi-Objective Pareto Optimization**:
   - Proposed as an extension to recommendation rules in Review 2 notes.
   - Not implemented: the recommendation engine uses deterministic lexicographic threshold rules, not a multi-objective Pareto solver.

---

### 2.4 What Is Experimental (In Notebooks / Research Scripts)

1. **16 Pedagogical Research Notebooks (`notebooks/00_...ipynb` through `15_...ipynb`)**:
   - Complete exploratory data analysis, model benchmarking, calibration curve generation, SHAP summary plots, waterfall visualization scripts, and worked number lineage examples.
2. **Experimental Result Logs (`research/experiments/EXP-001` to `EXP-009`)**:
   - Persisted CSV and JSON outputs verifying model comparisons, calibration error drops, tipping-point curves ($+18.4\%$), component ablation drops, and Monte Carlo confidence intervals.

---

### 2.5 What Is Implemented but Undocumented

1. **Dynamic Threadpool Offloading (`backend/app/services/simulation_service.py`)**:
   - Uses `asyncio.to_thread` to execute synchronous CPU-bound XGBoost inferences without blocking the FastAPI event loop (recorded in ADR-006).
2. **Deterministic Overtime Boundary Rounding**:
   - Specific implementation in `src/scenario/engine.py:363` uses `np.ceil(np.round(target_count_float, 9))` to eliminate floating-point rounding ambiguities in cohort headcounts.

---

## 3. Mathematical Formulations & Execution Data Flow

### 3.1 Domain 1: Retail Demand Forecasting Model
The demand forecasting pipeline uses an autoregressive recursive XGBoost regressor:
$$\hat{D}_{t} = f_d(X_t^{\text{temporal}}, X_t^{\text{store}}, X_t^{\text{promo}}, D_{t-1}, D_{t-7}; \theta_d)$$
For a forecast horizon $H = 14$ days under promotional lever $u_{\text{promo}} \in \{0, 1\}$ and shock $\delta_d \in [-0.50, +1.00]$:
$$Y_{\text{sales}}^{\text{base}} = \sum_{t=1}^{H} \hat{D}_t(u_{\text{promo}}=0)$$
$$Y_{\text{sales}}^{\text{scen}} = \left( \sum_{t=1}^{H} \hat{D}_t(u_{\text{promo}}=\text{levers.promo\_active}) \right) \times (1 + \delta_d)$$
$$\Delta Y_{\text{sales}} = Y_{\text{sales}}^{\text{scen}} - Y_{\text{sales}}^{\text{base}}$$

### 3.2 Enterprise Cross-Domain Volume Coupling (ASM-007, ASM-008)
To synchronize daily retail demand with monthly operational throughput:
$$\text{Daily Rate} = \frac{Y_{\text{sales}}^{\text{scen}}}{H}$$
$$\text{Normalized Cycle Volume } V_{\text{cycle}} = \text{Daily Rate} \times \tau_{\text{cycle}} \quad (\text{ASM-008: } \tau_{\text{cycle}} = 30 \text{ days})$$
$$\text{Normalized Order Volume } N_{\text{orders}} = V_{\text{cycle}} \times \gamma_{\text{volume}} \quad (\text{ASM-007: } \gamma_{\text{volume}} = 1.0 \text{ orders/unit})$$

### 3.3 Domain 2: Supply Chain Delivery Risk Model
The late-delivery risk model evaluates an order cohort $\mathcal{O}$ ($|\mathcal{O}| = N_{\text{cohort}}$).  
Raw tree ensemble margin $z_i = g_s(X_{s, i}; \theta_s)$.  
Platt (Sigmoid) probability calibration:
$$\hat{p}_{\text{late}, i} = \sigma(A_s z_i + B_s) = \frac{1}{1 + \exp(-(A_s z_i + B_s))}$$
Cohort mean late delivery risk:
$$\bar{p}_{\text{late}} = \frac{1}{|\mathcal{O}|} \sum_{i \in \mathcal{O}} \hat{p}_{\text{late}, i}$$
$$\Delta p_{\text{late}} = \bar{p}_{\text{late}}^{\text{scen}} - \bar{p}_{\text{late}}^{\text{base}}$$
Binary classification at optimal threshold $\tau_s^* = 0.50$:
$$C_{\text{late}} = \mathbb{I}(\bar{p}_{\text{late}} \ge \tau_s^*)$$

### 3.4 Domain 3: Workforce Attrition Risk Model
Workforce cohort $\mathcal{W}$ ($|\mathcal{W}| = N_{\text{headcount}} = 221$).  
Target overtime percentage $u_{\text{ot}} \in [0.0, 1.0]$. Target overtime headcount $k_{\text{target}} = \lceil N_{\text{headcount}} \cdot u_{\text{ot}} \rceil$.  
Deterministic assignment: If $k_{\text{target}} > k_{\text{base}}$, select the first $k_{\text{target}} - k_{\text{base}}$ non-overtime employees ordered by primary index and set $\text{OverTime}_j = \text{"Yes"}$.  
Apply ASM-006: $\text{WorkLifeBalance}_j \leftarrow \text{clip}(\text{WorkLifeBalance}_j - 1, 1, 4)$.  
Raw tree margin $z_j = g_w(X_{w, j}; \theta_w)$.  
Platt calibration:
$$\hat{p}_{\text{att}, j} = \sigma(A_w z_j + B_w) = \frac{1}{1 + \exp(-(A_w z_j + B_w))}$$
Cohort mean attrition risk:
$$\bar{p}_{\text{att}} = \frac{1}{|\mathcal{W}|} \sum_{j \in \mathcal{W}} \hat{p}_{\text{att}, j}$$
$$\Delta p_{\text{att}} = \bar{p}_{\text{att}}^{\text{scen}} - \bar{p}_{\text{att}}^{\text{base}}$$

### 3.5 Managerial Accounting Engine (Phase 7)
All financial line items are deterministic transformations without premature rounding:

1. **Gross Revenue:**
   $$\text{GrossRev} = Y_{\text{sales}} \times P_{\text{unit}} \quad (P_{\text{unit}} = \$10.00)$$
2. **Fulfillment Loss & Realized Revenue:**
   $$L_{\text{fulfillment}} = \bar{p}_{\text{late}} \times \kappa_{\text{stockout}} \quad (\text{ASM-003: } \kappa = 0.15)$$
   $$\text{RealizedRev} = \text{GrossRev} \times (1 - L_{\text{fulfillment}})$$
   $$\Delta \text{RealizedRev} = \text{RealizedRev}^{\text{scen}} - \text{RealizedRev}^{\text{base}}$$
3. **Cost of Goods Sold (COGS):**
   $$\text{COGS} = Y_{\text{sales}} \times C_{\text{unit}} \quad (C_{\text{unit}} = \$4.00, \text{ margin} = 60\%)$$
   $$\Delta \text{COGS} = \text{COGS}^{\text{scen}} - \text{COGS}^{\text{base}}$$
4. **Supply Chain Disruption Costs:**
   $$C_{\text{delay}} = N_{\text{orders}} \times \bar{p}_{\text{late}} \times C_{\text{penalty}} \quad (\text{ASM-001: } C_{\text{penalty}} = \$25.00/\text{order})$$
   $$C_{\text{expedite}} = N_{\text{orders}} \times C_{\text{fee}} \quad (\text{ASM-002: } C_{\text{fee}} = \$15.00 \text{ if expedited else } \$0)$$
   $$C_{\text{supply}} = C_{\text{delay}} + C_{\text{expedite}}$$
5. **Workforce Operational Costs:**
   $$N_{\text{turnover}} = N_{\text{headcount}} \times \bar{p}_{\text{att}}$$
   $$C_{\text{turnover}} = N_{\text{turnover}} \times C_{\text{replace}} \quad (\text{ASM-004: } C_{\text{replace}} = \$30,000.00)$$
   $$\text{OT Headcount } k_{\text{ot}} = N_{\text{headcount}} \times u_{\text{ot}}$$
   $$C_{\text{overtime}} = k_{\text{ot}} \times H_{\text{ot}} \times R_{\text{ot}} \quad (H_{\text{ot}} = 40 \text{ hrs/month}, \text{ASM-005: } R_{\text{ot}} = \$45.00/\text{hr})$$
   $$C_{\text{workforce}} = C_{\text{turnover}} + C_{\text{overtime}}$$
6. **Net Operating Profit Delta ($\Delta \Pi$):**
   $$\Delta \Pi = \Delta \text{RealizedRev} - \Delta \text{COGS} - \Delta C_{\text{supply}} - \Delta C_{\text{workforce}}$$

### 3.6 Composite Risk Score & Lexicographic Decision Engine (Phase 8)
1. **Supply Chain Sub-Index:**
   $$S_{\text{supply}} = 100 \times \left( 0.70 \cdot \bar{p}_{\text{late}}^{\text{scen}} + 0.30 \cdot \text{clamp}\left(\frac{\Delta p_{\text{late}}}{0.30}, 0, 1\right) \right)$$
2. **Workforce Sub-Index:**
   $$S_{\text{workforce}} = 100 \times \left( 0.60 \cdot \text{clamp}\left(\frac{\bar{p}_{\text{att}}^{\text{scen}}}{0.40}, 0, 1\right) + 0.40 \cdot u_{\text{ot}} \right)$$
3. **Demand Execution Sub-Index:**
   $$S_{\text{demand}} = 100 \times \left( 0.50 \cdot \text{clamp}\left(\frac{\delta_d}{0.50}, 0, 1\right) + 0.50 \cdot L_{\text{fulfillment}} \right)$$
4. **Aggregate Composite Risk Score:**
   $$\text{CRS} = 0.40 \cdot S_{\text{supply}} + 0.40 \cdot S_{\text{workforce}} + 0.20 \cdot S_{\text{demand}}$$
5. **Lexicographic Gating Rule:**
   $$\mathcal{D}(\Delta \Pi, \text{CRS}) = \begin{cases}
   \text{REJECT\_RESTRUCTURE}, & \text{if } \Delta \Pi \le 0 \\
   \text{PROCEED}, & \text{if } \Delta \Pi > 0 \text{ and } \text{CRS} \le \tau_{\text{risk}} \quad (\tau_{\text{risk}} = 50.0) \\
   \text{PROCEED\_WITH\_MITIGATIONS}, & \text{if } \Delta \Pi > 0 \text{ and } \text{CRS} > \tau_{\text{risk}}
   \end{cases}$$

---

## 4. Cross-Domain Dependencies & Architectural Bottlenecks

### 4.1 Coupling Graph
```
[User Scenario Levers U]
       │
       ├─────────────────────────────────┬──────────────────────────────┐
       ▼                                 ▼                              ▼
Retail Demand Shock               Logistics Offsets              Overtime Target
(Promo, Demand Growth)            (Scheduled Offset, Mode)       (Overtime %, Salary Hike)
       │                                 │                              │
       ▼                                 ▼                              ▼
Demand Forecaster (XGBoost)       Supply Chain Model (XGBoost)   Workforce Model (XGBoost)
       │                                 │                              │
       ▼                                 ▼                              ▼
Sales Forecast Y_sales            Calibrated p_late              Calibrated p_att
       │                                 │                              │
       ├─────────────────┐               │                              │
       ▼                 ▼               │                              │
Gross Revenue       ASM-007, ASM-008     │                              │
       │                 │               │                              │
       │                 ▼               │                              │
       │           Order Volume N_orders │                              │
       │                 │               │                              │
       │                 ├───────────────┤                              │
       │                 │               ▼                              ▼
       │                 │       Carrier Penalties              Burnout / Turnover
       │                 │       (ASM-001, ASM-002)             (ASM-004, ASM-005, ASM-006)
       ▼                 ▼               │                              │
Realized Revenue ◄── Fulfillment Loss    │                              │
       │                                 │                              │
       └────────────────────────┬────────┴──────────────────────────────┘
                                ▼
                   Managerial Accounting Engine
                                ▼
                     Net Profit Delta (ΔΠ)
                                │
                                ▼
                     Composite Risk Score (CRS)
                                │
                                ▼
                   Lexicographic Decision Gating
```

### 4.2 Identified Technical Limitations in Current Code
1. **Ad-Hoc Propagation Flow:**
   The cross-domain propagation currently executes sequentially within a single imperative function (`ScenarioEngine.run_scenario()` in `src/scenario/engine.py`). While correct, it is not formalized as a reified **State-Space Dependency Graph** $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ or a mathematical state-transition operator $S_{t+1} = \mathcal{F}(S_t, U_t, \hat{P}_t)$.
2. **Coupling Parameters are Constant Scalars:**
   `ASM-007` (volume scaling = 1.0) and `ASM-008` (cycle days = 30) are static configuration values. While stress-tested via sweeps in `sweep.py`, they are not dynamically parameterized as node transformation functions.
3. **Absence of Closed-Form State Sensitivity:**
   To evaluate sensitivity, the system performs repetitive brute-force scenario evaluations. There is no analytic Jacobian matrix $\frac{\partial S}{\partial U}$ tracking how an incremental shock $\partial u_i$ propagates through intermediate state vectors to final profit and risk.

---

## 5. Verified Experimental Evidence on Disk

The following empirical findings from Review 2 experiments are verified on disk:

1. **EXP-001 (Model Benchmarking):**
   - Demand XGBoost achieves **8.12% WAPE** on the strict 2015 holdout, outperforming Ridge (11.98%) and 7-day Naive persistence (33.32%).
   - Supply Chain XGBoost achieves **0.7795 ROC-AUC**, outperforming Logistic Regression (0.7520) and Majority Class (0.5000).
   - Workforce XGBoost achieves **0.8045 ROC-AUC** and **0.1086 Brier score** post-calibration.
2. **EXP-002 (Probability Calibration):**
   - Platt scaling reduces Supply Chain Expected Calibration Error (ECE) from **0.0521 to 0.0142** (-72.7% reduction).
   - Workforce ECE reduced from **0.0712 to 0.0537**.
3. **EXP-005 (Sensitivity Sweeps & Margin Tipping Point):**
   - Operating margin tipping point identified at **$+18.4\%$ demand growth**. Beyond $+18.4\%$, operational friction (penalties + turnover) exceeds gross margin, driving $\Delta \Pi < 0$.
4. **EXP-006 & EXP-007 (Canonical Scenario & Integration Value):**
   - Canonical Scenario ($+15\%$ demand, promo active, $40\%$ overtime): Gross revenue $+\$26,710.78$, carrier penalties $+\$469,188.49$, labor disruption $+\$184,212.00$, yielding net operating loss **$-\$642,716.18$**.
   - Naive uncoupled planning approves the campaign; DecisionSphere halts it with **`REJECT_RESTRUCTURE`**, avoiding capital misallocation.
5. **EXP-008 & EXP-009 (Monte Carlo Stability):**
   - 200 stochastic runs: Mean loss $= -\$649,955.19$, standard error $\text{SE} = \$3,955.49$. Recommendation stability $= 100.0\%$ `REJECT_RESTRUCTURE`.

---

## 6. Audit Conclusion & Patent Implications

1. **The Core ML Algorithms are NOT Novel:**
   XGBoost, Platt scaling, and TreeSHAP are standard, established machine learning techniques. Any patent claim directed to using these algorithms in isolation will be rejected under 35 U.S.C. § 102/103 and Section 3(k) of the Indian Patents Act.
2. **The Business Formulas are NOT Patentable Subject Matter:**
   Equations for Gross Revenue, Realized Revenue, COGS, and Overtime Wages are standard cost accounting principles. Framing the invention as "a system for calculating promotional profitability" is a non-statutory business method.
3. **The Potentially Patentable Subject Matter Lies in:**
   The specific **computer-implemented technical architecture** that solves the technical problem of **uncalibrated error propagation, non-divergent state transitions, and cryptographic epistemic boundary enforcement across heterogeneous tabular model inferences**.
   Specifically:
   - Formalizing the execution pipeline as a **State-Space Dependency Graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$** with an explicit **Dynamic Scenario Propagation Operator $\mathcal{F}$**.
   - The **Calibrated Probability Coupling Pipeline** that guarantees bounded propagation error when mapping statistical model outputs into non-linear step-loss penalty functions.
   - The **Six-Tier Epistemic Boundary Control & Cryptographic Provenance Engine** preventing model mutation and data contamination.

This audit forms the factual, verified foundation for the prior-art investigation and patentability assessment that follows.
