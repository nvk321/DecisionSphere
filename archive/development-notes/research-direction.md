# DecisionSphere — Academic Research Blueprint & Scientific Foundation

## 1. Executive Research Statement

**Project Title (Locked):** `DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform`  
**Target Academic Venues:** IEEE Access / Elsevier *Computers & Industrial Engineering* / *Decision Support Systems* / Scopus-Indexed Conferences (e.g., IEEE TEMSCON, IEEE ICDEW, Springer LNBIP).

### The Core Research Problem
Modern enterprise decision-makers face a fundamental dilemma: while operational reality is deeply interconnected, enterprise predictive analytics remains fragmented into departmental silos. Sales and marketing optimize promotional demand in isolation; supply chain managers forecast logistics delays independently; and human resources monitors employee attrition in isolation. When strategic interventions occur (e.g., a promotional surge or an expedited delivery push), the cascading cross-functional impacts—such as supplier delays, warehouse overtime, worker burnout, and contractual penalties—remain unmodeled until financial losses materialize.

### The Central Thesis
> **A scenario-driven cross-functional decision intelligence framework that explicitly couples heterogeneous predictive models with parameterized operational propagation and deterministic financial accounting reveals critical business trade-offs that isolated predictive models systematically fail to detect, while preserving end-to-end computational auditability.**

---

## 2. The Twelve Foundational Research Inquiries

### Q1: Can this project support a genuine academic research paper?
**Yes.** DecisionSphere transitions from a standard engineering software project to a publishable research contribution by focusing on **decision intelligence, cross-functional risk propagation, and methodological rigor**. Rather than claiming an algorithmic breakthrough, the research evaluates the *systemic integration, epistemic demarcation, trade-off discovery, and parametric sensitivity* of cross-domain scenario modeling.

### Q2: What is genuinely novel in DecisionSphere?
1. **The Cross-Functional Scenario Propagation Architecture:** A mathematical and algorithmic mechanism that transforms an operational shock in one domain ($\Delta D$) into downstream volume pressure, logistics delay probability shifts, overtime workload spikes, and attrition risk.
2. **The 6-Tier Epistemic Architecture:** Clean separation of empirical observations, statistical ML predictions, scenario hypotheses, operational propagations, deterministic accounting calculations, and rule-based recommendations—preventing ungrounded causal claims and LLM hallucinations.
3. **Cross-Domain Trade-Off Discovery:** Quantitative demonstration that localized optimizations (e.g., maximizing demand revenue) can produce global sub-optimality (net negative margin) once cascading fulfillment penalties and workforce replacement costs are computed.
4. **Assumption-Aware Sensitivity Analysis:** Systematic empirical stress-testing of coupling parameters (`ASM-001`–`ASM-008`), mapping the exact stability regions where strategic recommendations hold true.

### Q3: What is already established (and therefore NOT claimed as novelty)?
- **Algorithm Implementations:** Gradient boosted decision trees (XGBoost, LightGBM), Random Forests, Ridge Regression.
- **Explainability Formulations:** Shapley Additive Explanations (TreeSHAP).
- **Domain Tasks:** Retail store sales forecasting, binary delivery delay classification, binary employee attrition classification.
- **Single-Domain Web Interfaces:** Standard forecasting dashboards or isolated prediction endpoints.

### Q4: What is our precise research gap?
The absence of a lightweight, data-grounded, and fully auditable framework that bridges the divide between **predictive machine learning** (calibrated on real transactional benchmarks) and **cross-functional scenario simulation** (evaluating downstream operational, workforce, and financial ripple effects). Existing solutions are either siloed predictive models (no cross-domain ripple), rigid closed-source ERP digital twins (cost-prohibitive, opaque simulation rules), or generative AI tools (unreliable, prone to numerical hallucination).

### Q5: What are the primary and secondary Research Questions?
- **Primary RQ (RQ1 - Cross-Domain Information Gain):**  
  *Can an integrated scenario-driven cross-functional framework reveal operational and financial trade-offs that isolated predictive models fail to expose?*
- **Secondary RQ (RQ2 - Epistemic Traceability & Auditability):**  
  *Can explicit separation between predictive inference, scenario propagation assumptions, and deterministic business-impact calculations improve end-to-end traceability and auditability compared to monolithic or generative approaches?*
- **Secondary RQ (RQ3 - Explainability & Decision Defensibility):**  
  *Can local model explanations (TreeSHAP) be connected to scenario interventions and recommendation rules to improve decision defensibility without making unsupported causal claims?*
- **Secondary RQ (RQ4 - Parametric Sensitivity & Decision Robustness):**  
  *How robust are integrated strategic recommendations when the assumptions and coupling parameters connecting demand, supply chain, workforce, and financial impact are varied?*

### Q6: What formal hypotheses should be tested?
- **$H_1$ (Trade-Off Discovery):** In high-magnitude promotional scenarios ($\Delta D \ge +30\%$), the integrated framework identifies net negative profit margins ($\Delta \text{Profit} < 0$) in at least $25\%$ of test store configurations that single-domain demand models classify as profitable.
- **$H_2$ (Deterministic Preservation):** Decoupling statistical prediction from deterministic business equations guarantees $100\%$ computational reproducibility, zero numerical variance across repeated runs, and zero hallucinatory output drift.
- **$H_3$ (Attribution Monotonicity):** TreeSHAP feature attributions for scenario levers (e.g., `Promo`, lead time shifts, overtime flags) exhibit monotonic directional alignment with scenario shock intensity, providing an empirical basis for recommendation rule triggers.
- **$H_4$ (Decision Invariance Window):** Recommended strategic mitigations remain structurally invariant across a $\pm 20\%$ perturbation window of operational coupling constants, establishing clear tipping points where logistics mitigation dominates workforce mitigation.

### Q7: What experiments will prove or disprove them?
- **Experiment A (Isolated vs. Integrated Decision Support):** Directly tests $H_1$ by benchmarking single-domain demand optimization against integrated cross-functional evaluation.
- **Experiment B (Scenario Magnitude & Inflection Analysis):** Sweeps operational shocks across multiple scales ($\Delta D \in [-20\%, +50\%]$, $\Delta S \in [0, 7\text{ days}]$, $\Delta O \in [0\%, 50\%]$) to map capacity bottlenecks and non-linear risk inflections.
- **Experiment C (Explainability & Attribution Fidelity):** Tests $H_3$ by analyzing TreeSHAP attribution matrices, stability under perturbation, and alignment with generated recommendations.
- **Experiment D (Parametric Sensitivity Analysis):** Tests $H_4$ via One-At-A-Time (OAT) and Morris screening on assumptions `ASM-001`–`ASM-008`.
- **Ablation Suite:** Evaluates performance degradation when removing individual modules (Demand-only $\rightarrow$ Demand+Supply $\rightarrow$ Full Integration).

### Q8: What datasets are actually necessary?
1. **Rossmann Store Sales (Demand Benchmark):** 1,115 stores, 1,017,209 daily records. Necessary for empirical baseline demand calibration and testing promotional shocks (`Promo` lever).
2. **DataCo Smart Supply Chain (Logistics Risk Benchmark):** 180,519 order transactions. Necessary for empirical late delivery risk classification conditioned on shipping modes, geographic routes, and scheduling constraints.
3. **IBM HR Analytics (Workforce Risk Benchmark):** 1,470 employee records. Necessary for modeling employee attrition risk conditioned on operational overtime, job roles, and working conditions.

### Q9: What assumptions are unavoidable?
Because public benchmark datasets are collected independently across different firms and time periods, **cross-domain coupling parameters cannot be learned directly from observational data without introducing false causal claims**. Unavoidable assumptions include:
- `ASM-001`: Contractual late delivery penalty default ($\$25.00$).
- `ASM-002`: Expedited freight shipping surcharge default ($\$15.00$).
- `ASM-003`: Late order cancellation elasticity ($\kappa_{\text{stockout}} = 0.15$).
- `ASM-004`: Cost of employee turnover replacement ($50\%$ annualized median salary $\approx \$30,000$).
- `ASM-005`: Overtime wage premium ($1.5\times$ base hourly rate).
- `ASM-006`: Overtime-induced satisfaction decrement ($\Delta \text{WorkLifeBalance} = -1$).
- `ASM-007`: Normalized enterprise transaction volume scaling.
- `ASM-008`: Temporal baseline alignment across heterogeneous datasets.

*Rule:* All assumptions are transparently cataloged in `docs/assumptions-and-open-questions.md`, exposed to user configuration in the UI, and subjected to rigorous sensitivity testing in Experiment D.

### Q10: What are the major threats to validity?
1. **Internal Validity (Data Leakage):** Addressed by strict chronological splitting in time-series forecasting, complete exclusion of contemporaneous features (`Customers` dropped in Rossmann), and exclusion of realized outcome variables (`Days for shipping (real)` dropped in DataCo).
2. **Construct Validity (Cross-Domain Proxy Coupling):** Public datasets do not originate from a single corporate ledger. Threat mitigated by formalizing the system as a **Normalized Enterprise Archetype** and conducting global sensitivity analysis to demonstrate that conclusions do not collapse under parameter shifts.
3. **Epistemic Validity (Causal Overreach):** Machine learning models learn conditional correlations, not causal relationships (Shmueli 2010). Threat mitigated by strict language protocols: scenarios are designated as "conditional predictions under hypothetical feature states," never "proved causal interventions."
4. **External Validity (Generalizability):** Evaluated by testing the framework across diverse store types, product categories, and shipping modes.

### Q11: What is the current canonical phase progress and what must be implemented next?
- **Phase 0 (Documentation & Foundation):** COMPLETED.
- **Phase 1 (Dataset Inventory & Audit):** COMPLETED.
- **Phase 2 (Demand Forecasting Pipeline):** COMPLETED (Rossmann XGBoost Regressor; WAPE = 8.12%).
- **Phase 3 (Supply Chain Delivery Risk Pipeline):** COMPLETED — FROZEN (DataCo Calibrated XGBoost; ROC-AUC = 0.7795, PR-AUC = 0.8423).
- **Phase 4 (Workforce Attrition Risk Pipeline):** COMPLETED — FROZEN (IBM HR Calibrated XGBoost; PR-AUC = 0.5030, ROC-AUC = 0.8045).
- **Phase 5 (Governance Status Clarification):** GOVERNANCE STATUS ONLY (TreeSHAP XAI integrated directly into predictive models; not an independent implementation phase).
- **Phase 6 (Scenario Engine & Parameter Propagation):** COMPLETED — FROZEN (Cross-domain operational propagation; 20 tests passing, 53 full suite passing; zero financial calculations; `ScenarioRunResult` handoff).
- **Phase 7 (Business Impact Analysis Engine):** PRE-IMPLEMENTATION AUDIT COMPLETED / READY FOR APPROVAL (`src/business/`; consumes `ScenarioRunResult`; evaluates financial consequences via `ASM-001` through `ASM-005`; implementation awaiting approval).
- **Phase 8+ (Recommendation Engine & Full-Stack Application):** PENDING (Rule-grounded mitigations, FastAPI backend, React dashboard, PostgreSQL persistence, headless experimental runners for Experiments A–D).

### Q12: What evidence would be required before making a publication claim?
1. **Audit Evidence:** Clean, verified feature sets with zero leakage across all three benchmark pipelines.
2. **Predictive Baselines:** Empirically verified metrics on holdout test partitions (e.g., Rossmann WAPE $\le 8.2\%$; DataCo ROC-AUC $\ge 0.75$, PR-AUC reported; IBM HR PR-AUC reported against naive majority baselines).
3. **Experiment A Results Table:** Documented delta between isolated and integrated decisions demonstrating trade-off discovery.
4. **Experiment B Curves:** Plotted response curves showing non-linear inflection points in risk and cost under varying scenario shock magnitudes.
5. **Experiment C Attribution Matrices:** TreeSHAP waterfall and summary plots confirming that scenario interventions directly drive model attributions.
6. **Experiment D Tornado Plots:** Systematic sensitivity tables and tornado plots demonstrating the invariance boundaries of strategic recommendations.

---

## 3. The 6-Tier Epistemic Architecture

To prevent academic ambiguity, ensure regulatory auditability, and eliminate generative hallucination, DecisionSphere enforces a strict 6-tier epistemic hierarchy:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. OBSERVED GROUND TRUTH (Historical Benchmark Datasets)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ Input Feature Vectors
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PREDICTED ESTIMATIONS (Offline-Trained ML Models)        │
│    - Conditional Sales Forecasts (XGBoost Regressor)        │
│    - Late Delivery Probabilities (Calibrated Classifier)    │
│    - Employee Attrition Probabilities (Weighted Classifier) │
└──────────────────────────────┬──────────────────────────────┘
                               │ Baseline Predictions
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. ASSUMED SCENARIO LEVERS (User Hypotheses & Constants)    │
│    - Demand growth shock (ΔD), Promo overrides              │
│    - Lead-time offsets (ΔS), Overtime policy (ΔO)           │
│    - Documented Cost Constants (ASM-001 through ASM-008)    │
└──────────────────────────────┬──────────────────────────────┘
                               │ Parameterized Translation
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. PROPAGATED OPERATIONAL IMPACTS (Scenario Engine)         │
│    - Simulated Demand: y_sim(t) = y_base(t) * (1 + ΔD/100)  │
│    - Logistics Load: Scheduled shipping days shifted by ΔS  │
│    - Workforce Strain: Overtime ratio scaled by ΔO          │
└──────────────────────────────┬──────────────────────────────┘
                               │ Input to Accounting Equations
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. CALCULATED BUSINESS IMPACT (Deterministic Formulas)      │
│    - Gross Revenue Delta (ΔRev = Σ y_sim * P * (1 - L_loss))│
│    - Logistics Penalty Delta (ΔCost_SC = Delayed * Penalty) │
│    - Workforce Cost Delta (ΔCost_HR = Churn * Repl + OT)    │
│    - Net Incremental Profit: ΔProfit = ΔRev - ΔCosts        │
│    - Composite Risk Index (CRS ∈ [0, 100])                  │
└──────────────────────────────┬──────────────────────────────┘
                               │ Trigger Thresholds + SHAP
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. RECOMMENDED ACTIONS (Rule-Grounded Decision Engine)      │
│    - Strategic trade-off synthesis                          │
│    - Prioritized mitigations (e.g., Expedite vs Temp Staff) │
│    - Optional LLM executive summary (restricted strictly to │
│      narrative rendering of calculated metrics)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Dataset Governance: The "Normalized Enterprise Archetype"

### Scientific Boundaries on Multi-Dataset Integration
A critical review question will inevitably ask: *"How can you justify combining retail data from Germany (Rossmann), global shipping logs from Latin America (DataCo), and corporate HR survey data from the US (IBM)?"*

### The Defensible Methodological Framing
1. **Never claim physical unity:** We do not claim that these three datasets represent observations from a single real-world corporation.
2. **The "Normalized Enterprise Archetype":** We frame the environment as a **synthetically coupled enterprise scenario testbed**. The three independent benchmarks serve as empirical calibrators for their respective operational archetypes:
   - Rossmann calibrates the *retail demand volatility and promotional response distribution*.
   - DataCo calibrates the *e-commerce multi-echelon freight delivery delay distribution*.
   - IBM HR Analytics calibrates the *corporate workforce attrition and overtime vulnerability distribution*.
3. **Explicit Cross-Domain Coupling:** The translation between domains is governed strictly by explicit, parameter-tunable equations (`ASM-001`–`ASM-008`). If an organization has private, interconnected operational data, the DecisionSphere architecture can be re-calibrated on their internal data with zero structural modifications.
4. **Sensitivity Testing as Scientific Validation:** By subjecting all cross-domain coupling parameters to global sensitivity analysis (Experiment D), we prove that the system's conclusions and recommendations do not depend on narrow, arbitrary parameter values.
