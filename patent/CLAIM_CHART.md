# DecisionSphere — Claim-by-Claim Prior-Art Differentiation Chart

**Document ID:** `DSP-CLAIM-CHART-001`  
**Date:** 2026-10-24  
**Drafting Standard:** Section 3(k) Indian Patents Act (2017 CRI Guidelines), USPTO 35 U.S.C. § 102/103/112, EPO Art. 52/56.  
**Governing Protocol:** [AGENTS.md](file:///d:/Projects/DecisionSphere/AGENTS.md)  

---

## 1. Statutory Scope & Claim Construction Rules

1. **Non-Statutory Disclaimers:** Business logic, commercial promotional strategy, subjective utility, and simple managerial accounting equations are explicitly unpatentable per se under Section 3(k) IPA and the *Alice* framework.
2. **Defensible Technical Core:** The claimed subject matter is strictly directed to the **computer-implemented technical system**:
   - Cryptographic integrity verification of heterogeneous model weights prior to execution;
   - Translation of disparate operational domains into a contiguous 24-dimensional continuous state vector in $\mathbb{R}^{24}$;
   - A Directed Acyclic Graph (DAG) state-space propagation operator with topological Kahn sequencing preventing cyclic divergence;
   - Post-hoc Platt sigmoid probability calibration error-bounding, proving mathematically and empirically that calibration reduces Expected Calibration Error (ECE) by $72.7\%$ and eliminates tens of thousands of dollars in step-loss penalty distortion.

---

## 2. Claim-by-Claim Analysis: Independent Claim 1 (Method)

### Preamble: A computer-implemented method for calibrated multi-domain state propagation and non-linear operational risk evaluation across heterogeneous machine learning estimators
- **DecisionSphere Implementation:** End-to-end Python 3.13 pipeline executing across `src/scenario/state.py`, `src/scenario/graph.py`, and `src/scenario/propagation.py`.
- **Prior-Art References:** o9 Solutions (US 12,051,026 B2; PA-01), Kinaxis (US 10,956,858 B2; PA-03), Palantir (US 9,892,372 B2; PA-04), Quantellia (US 10,643,152 B2; PA-10).
- **Does Prior Art Contain Element?** Yes (in high-level concept).
- **Distinguishing Feature:** Prior art couples database measures (o9), in-memory ERP graphs (Kinaxis), or manual ontologies (Palantir); DecisionSphere couples independently trained statistical machine learning estimators (XGBoost) through a unified continuous state-space vector and probability calibration pipeline.
- **Evidence:** `tests/test_patent_core.py`, `src/scenario/propagation.py`.
- **Patentability Concern:** Abstract idea risk if characterized merely as "analyzing business scenarios." Must be claimed as a specific computer-implemented data transformation pipeline.

---

### Element 1.1: Cryptographic hash digest verification of serialized model artifacts
- **DecisionSphere Implementation:** Computes runtime SHA-256 digests on `.joblib` model binaries prior to inference execution; execution halts if digest deviates from registered manifest.
- **Prior-Art References:** Palantir (US 9,892,372 B2), DataRobot (US 11,170,311 B2; PA-21).
- **Does Prior Art Contain Element?** Partially (standard cryptographic hashing exists in OS security and data pipelines, but not as an execution gate for state-space scenario propagation).
- **Distinguishing Feature:** Cryptographic gate binds specific frozen empirical model weights to the scenario state vector to prevent silent model drift during multi-domain simulation.
- **Evidence:** `tests/test_research_suite.py::test_frozen_analytical_core_invariance`, `research/REPRODUCIBILITY.md`.
- **Patentability Concern:** Cryptographic hashing per se is a standard technique (Grade A). It cannot serve as the sole inventive step; it serves as a structural integrity limitation.

---

### Element 1.2: Ingestion of strongly typed scenario intervention vector bounded by compile-time numerical constraints
- **DecisionSphere Implementation:** `ScenarioLevers` schema in `src/scenario/schema.py` enforced via Pydantic v2 validation ($\delta_d \in [-50\%, +100\%]$, $u_{\text{ot}} \in [0\%, 100\%]$).
- **Prior-Art References:** Anaplan (US 9,268,813 B2; PA-09), o9 Solutions (US 11,816,620 B2; PA-02).
- **Does Prior Art Contain Element?** Yes (schema validation is standard engineering).
- **Distinguishing Feature:** Integration directly into continuous state-space operator bounding solver search intervals during bisection tipping-point discovery.
- **Evidence:** `src/scenario/schema.py`, `tests/test_scenario_engine.py`.
- **Patentability Concern:** Routine programming practice (ordinary engineering). Must be claimed as part of the pipeline combination.

---

### Element 1.3: Instantiating an immutable baseline state vector representing historical enterprise operational observations
- **DecisionSphere Implementation:** `ScenarioStateVector` captures baseline values ($Y_0$, $p_{\text{late}, 0}$, $p_{\text{att}, 0}$) alongside scenario values to guarantee non-divergent delta calculation without mutating historical benchmark records.
- **Prior-Art References:** Kinaxis (US 10,956,858 B2), SAP (US 10,204,319 B2; PA-06).
- **Does Prior Art Contain Element?** Yes (versioning/delta tracking is known).
- **Distinguishing Feature:** Continuous mathematical state-space formulation in $\mathbb{R}^{24}$ supporting Euclidean distance and finite-difference Jacobian operations.
- **Evidence:** `src/scenario/state.py:state_distance()`, `tests/test_patent_core.py`.
- **Patentability Concern:** Standard state tracking unless tied to mathematical operator.

---

### Element 1.4: Forward demand forecasting via an autoregressive gradient boosted decision tree
- **DecisionSphere Implementation:** Autoregressive recursive XGBoost regressor trained on chronological Rossmann sales data (WAPE 8.12%).
- **Prior-Art References:** Blue Yonder / JDA (US 7,389,205 B2; PA-05), Chen & Guestrin (2016).
- **Does Prior Art Contain Element?** Yes (XGBoost is a known statistical algorithm).
- **Distinguishing Feature:** Generates baseline and perturbed demand projections feeding a downstream temporal cycle normalization operator.
- **Evidence:** `models/demand/train_demand.py`, `research/experiments/EXP-001-model-comparison/results/demand_metrics.json`.
- **Patentability Concern:** XGBoost per se is unpatentable prior art.

---

### Element 1.5: Normalizing demand forecast into operational order throughput volume using temporal cycle and volume scaling factors
- **DecisionSphere Implementation:** Translates daily retail sales run rate into 30-day logistics order throughput $N_{\text{orders}}$ via constants `ASM-007` ($\gamma = 0.5$) and `ASM-008` ($\tau = 30$).
- **Prior-Art References:** Blue Yonder (US 7,389,205 B2), Coupa / LLamasoft (US 10,489,729 B2; PA-23).
- **Does Prior Art Contain Element?** Partially (volume scaling is common in supply chain MRP).
- **Distinguishing Feature:** Explicit mathematical coupling bridging disparate open benchmark datasets into a standardized enterprise testbed.
- **Evidence:** `src/scenario/propagation.py`, `src/scenario/graph.py` (Node N3).
- **Patentability Concern:** High risk of being categorized as an arbitrary business heuristic. Must be claimed as an operational dimension alignment operator.

---

### Element 1.6: Generating uncalibrated late-delivery decision margins and transforming into calibrated probabilities via parametric logistic sigmoid scaling
- **DecisionSphere Implementation:** DataCo XGBoost classifier generates raw margins $z_i$, which are mapped via Platt scaling $\hat{p}_{\text{late}, i} = \sigma(A_s z_i + B_s)$ ($A_s = 0.8124, B_s = 0.1412$).
- **Prior-Art References:** Platt (1999; PA-13), Guo et al. (ICML 2017; PA-12), Niculescu-Mizil & Caruana (ICML 2005; PA-24), DataRobot (US 11,170,311 B2).
- **Does Prior Art Contain Element?** Platt scaling is known in ML literature, but NO prior art patent couples post-hoc calibrated probabilities into non-linear enterprise step penalties to eliminate financial penalty distortion.
- **Distinguishing Feature:** Proves analytically and experimentally that Platt scaling drops ECE from $0.0521$ to $0.0142$ ($-72.74\%$), directly eliminating **$\$27,052.48$** in contractual penalty distortion.
- **Evidence:** `research/patent_experiments/results/exp_p05_calibration_analysis.csv`, `research/experiments/EXP-002-probability-calibration/`.
- **Patentability Concern:** Core technical strength. Shows a concrete technical solution to an error-compounding technical problem in machine learning pipeline execution.

---

### Element 1.7: Deterministic workforce overtime allocation, ordinal burnout decrement, and calibrated employee attrition probability calculation
- **DecisionSphere Implementation:** Maps scenario overtime percentage $u_{\text{ot}}$ across employee cohort, adjusts `WorkLifeBalance` ordinal score (`ASM-006`), and evaluates Platt-calibrated IBM HR XGBoost model.
- **Prior-Art References:** Accenture (US 8,135,607 B2; PA-19).
- **Does Prior Art Contain Element?** Accenture models workforce capacity via queueing theory; it does NOT model employee attrition via calibrated gradient boosted decision trees conditioned on logistics overtime strain.
- **Distinguishing Feature:** First integrated cross-domain coupling linking commercial demand volume $\rightarrow$ logistics fulfillment strain $\rightarrow$ workforce overtime $\rightarrow$ calibrated attrition risk $\rightarrow$ financial replacement penalties.
- **Evidence:** `src/models/workforce/`, `src/scenario/propagation.py` (Node N5).
- **Patentability Concern:** Moderate risk under Section 3(k) if characterized as human resource management. Must be framed strictly as computational resource strain modeling.

---

### Element 1.8: Propagating states through a topologically ordered Directed Acyclic Graph (DAG) state-space operator into a continuous 24-dimensional state vector
- **DecisionSphere Implementation:** 11-node, 18-edge DAG in `src/scenario/graph.py` executed via Kahn topological sort into `ScenarioStateVector` in $\mathbb{R}^{24}$.
- **Prior-Art References:** o9 Solutions (US 12,051,026 B2; PA-01), Pearl (2009).
- **Does Prior Art Contain Element?** DAGs and topological sorting are standard computer science (Kahn 1962).
- **Distinguishing Feature:** Specific 11-node canonical enterprise topology formalizing the coupling between heterogeneous ML estimators, epistemic tiers, and continuous state vectors.
- **Evidence:** `src/scenario/graph.py:topological_sort()`, `tests/test_patent_core.py::test_dependency_graph_acyclicity`.
- **Patentability Concern:** Topological sort is an established algorithm. The inventive claim lies in the combination of the 11-node domain topology with continuous state serialization.

---

### Element 1.9: Deterministic managerial accounting engine computing net operating profit delta ($\Delta \Pi$) and Composite Risk Score ($\text{CRS}$)
- **DecisionSphere Implementation:** 64-bit IEEE-754 arithmetic in `src/business/impact.py` computing revenue, COGS, SLA penalties, and turnover replacement costs.
- **Prior-Art References:** Anaplan (US 9,268,813 B2), SAP (US 10,204,319 B2).
- **Does Prior Art Contain Element?** Yes (financial formulas are ubiquitous).
- **Distinguishing Feature:** Strict epistemic demarcation (Tier 5: CALCULATED) decoupling deterministic accounting from statistical ML inferences and preventing LLM hallucination.
- **Evidence:** `src/business/impact.py`, `tests/test_business_impact.py`.
- **Patentability Concern:** High Section 3(k) vulnerability if claimed in isolation. Must be claimed as an internal numerical transform of the continuous state vector.

---

### Element 1.10: Lexicographic decision gating controller assigning mutually exclusive strategic decision categories
- **DecisionSphere Implementation:** Tri-state governance in `src/recommendation/engine.py` (`REJECT_RESTRUCTURE`, `PROCEED`, `PROCEED_WITH_MITIGATIONS`) based on profit delta sign and CRS threshold.
- **Prior-Art References:** Quantellia (US 10,643,152 B2), Blue Yonder (US 8,583,471 B2; PA-25).
- **Does Prior Art Contain Element?** Threshold rule gating is known in business rules engines.
- **Distinguishing Feature:** Inversion of commercial planning bias: halts promotional approval when downstream operational friction yields $\Delta \Pi \le 0$, saving $\$642,716.18$ in executive capital misallocation.
- **Evidence:** `research/patent_experiments/results/exp_p01_baseline_comparison.csv`, `tests/test_recommendation_engine.py`.
- **Patentability Concern:** Business decision logic. Must be drafted as a system state classification rule.

---

## 3. Summary of Core Inventive Moat

The primary patentable differentiation of DecisionSphere resides in:
1. **The Technical Problem:** Uncalibrated model output compounding causing extreme distortion when predictive models are coupled into downstream non-linear penalty and physical capacity constraints.
2. **The Technical Solution:** A computer-implemented state-space dependency DAG executing calibrated probability transformations that mathematically and empirically bound error propagation across continuous multi-domain enterprise state vectors.
3. **The Technical Effect:** Elimination of $\$27,052.48$ in artificial penalty distortion ($-72.7\%$ ECE) and prevention of $\$642,716.18$ in catastrophic executive capital misallocation, executing with sub-second steady-state latency ($\approx 275 - 945\text{ ms}$).
