# DecisionSphere — Patent Go/No-Go Decision & Strategy Assessment

**Document ID:** `DSP-PAT-GONO-002`  
**Execution Date:** 2026-10-24  
**Auditing Persona:** Lead Research Engineer, Systems Architect & Patent-Readiness Analyst  
**Governing Standard:** Section 3(k) Indian Patents Act (2017 CRI Guidelines); USPTO 35 U.S.C. § 101/102/103 (*Alice* / *Mayo*); EPO Art. 52/56 (*Comvik*).  
**Authoritative Protocol:** [AGENTS.md](file:///d:/Projects/DecisionSphere/AGENTS.md)  

---

## Final Statutory Classification

```
================================================================================
FINAL CLASSIFICATION:
PATENT-CANDIDATE — TECHNICAL CORE DEFENSIBLE
(Subject to Strict Exclusion of Business Logic and Review by Institutional IPR Cell)
================================================================================
```

---

## The 16 Authoritative Statutory Questions

### 1. What exactly is the invention?
A computer-implemented decision intelligence system and method that couples heterogeneous, independently trained statistical machine learning estimators (time-series regression and tabular tree classifiers) into an integrated state-space dependency graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ with an explicit 24-dimensional continuous state vector $S_t \in \mathbb{R}^{24}$, wherein uncalibrated decision margins from risk classifiers are transformed via parametric logistic sigmoid calibration to bound expected calibration error prior to ingestion into downstream non-linear step-loss penalty functions, and wherein state transitions are executed deterministically along topological sort sequences with cryptographic model digest verification, discovering operational margin collapse boundaries and enforcing lexicographic solvency feasibility gating without generative hallucination.

### 2. What is already known?
- **Gradient Boosted Decision Trees:** The XGBoost algorithm (Chen & Guestrin, 2016) is established prior art.
- **Platt Sigmoid Scaling:** Logistic calibration mapping raw margins to posterior probabilities (Platt, 1999; Niculescu-Mizil & Caruana, 2005) is an established mathematical technique.
- **Explainability (TreeSHAP):** Polynomial-time Shapley feature attribution for tree models (Lundberg & Lee, 2017) is established prior art.
- **Standard Directed Acyclic Graphs & Topological Sorting:** Kahn's algorithm (1962) and DAG acyclicity checking are standard computer science.
- **Basic Managerial Accounting Formulas:** Gross revenue, cost of goods sold, and overtime hourly pay calculations are standard business practices.
- **Web App Architecture:** FastAPI REST backends and React frontends are ordinary engineering implementations.

### 3. What is potentially new?
- **Unified 24-Dimensional State-Space Tensor ($S_t \in \mathbb{R}^{24}$):** A continuous mathematical state representation tracking physical sales run rates, logistics delivery risks, workforce attrition risks, accounting balances, and multi-criteria operational strain with IEEE-754 continuous precision and exact Euclidean state distance metrics.
- **11-Node Canonical Dependency Topology:** The specific graph architecture $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ formalizing the operational coupling between retail demand shocks, logistics throughput strain, workforce overtime schedules, and employee burnout attrition.
- **Automated Margin Tipping-Point Discovery Operator:** A bisection search algorithm operating directly over the state propagation operator $\mathcal{F}$ to identify the exact commercial shock threshold where downstream operational friction collapses net operating margin.
- **Compile-Time Epistemic Boundary Control:** Strict architectural enforcement across 6 epistemic tiers (`OBSERVED`, `PREDICTED`, `ASSUMED`, `PROPAGATED`, `CALCULATED`, `RECOMMENDED`), preventing causal overreach and financial hallucination.

### 4. What is potentially inventive?
The inventive step resides in the **specific technical mechanism of coupling post-hoc calibrated probabilities into non-linear enterprise penalty and operational capacity constraints**. Prior art either utilizes raw, uncalibrated classifier outputs (which we prove cause massive error amplification) or models enterprise relationships as static database links without formal statistical uncertainty bounds. The synergistic combination of Platt calibration, topological DAG sequencing, and continuous state-space modeling solves a concrete computer-implemented technical problem in error propagation.

### 5. What technical problem is solved?
1. **Uncalibrated Error Compounding in Downstream Coupling:** Raw tree classifier margins exhibit severe overconfidence or underconfidence, which compounds into tens of thousands of dollars in estimation error when multiplied by non-linear operational penalties.
2. **State Divergence & Cyclic Deadlock Across Chained Models:** Chaining disparate multi-domain ML models frequently induces circular dependency loops, stack overflows, or numerical divergence.
3. **Generative Epistemic Laundering:** Generative AI tools invent financial figures and assert unjustified causal relationships from observational data.

### 6. What technical effect is demonstrated?
- **Calibration Error Bounding:** Platt scaling reduces Expected Calibration Error (ECE) from $0.0521$ to $0.0142$ (a **$72.74\%$ relative error reduction**), directly eliminating **$\$27,052.48$** in contractual SLA penalty calculation distortion (verified on DataCo holdout).
- **Acyclic State Convergence:** Zero circular dependencies; Kahn topological sort length 11; guaranteed non-divergent execution (verified in `tests/test_patent_core.py`).
- **Computational Scalability:** Linear $\mathcal{O}(N)$ runtime complexity scaling with steady-state throughput of $275\text{ ms} - 945\text{ ms}$ per scenario evaluation; pure state vector memory footprint of $304\text{ bytes}$ ($192\text{ KB}$ for 1,000 scenarios).
- **Invariant Decision Stability:** $100.0\%$ invariant `REJECT_RESTRUCTURE` classification across $N=50$ stochastic Gaussian perturbation simulations.
- **Capital Misallocation Avoidance:** Prevents **$\$642,716.18$** in catastrophic enterprise capital loss compared to siloed commercial planning.

### 7. What falls under Section 3(k)?
Under Section 3(k) of the Indian Patents Act, 1970, the following elements are **non-statutory and cannot be claimed**:
- Business methods per se (promotional campaign strategies, commercial discounting rules, customer retention planning).
- Mathematical algorithms in the abstract (Platt calibration equations, XGBoost tree split equations, Kahn topological sorting per se).
- Financial accounting equations per se (calculating net operating profit delta, deducting COGS from revenue).
- Mental acts or human workforce management rules (shift scheduling policies).

### 8. What prior art is closest?
1. **o9 Solutions (US 12,051,026 B2; 2024):** Computational Unified Graph Hierarchy Model. Models enterprise planning measures in a graph database, but lacks statistical probability calibration error bounding and state-space ML operators.
2. **Kinaxis Inc. (US 10,956,858 B2; 2021):** Cognitive Network Graph for Concurrent Supply Chain Planning. Propagates demand shocks into bill-of-materials and supply constraints, but does not model workforce attrition dynamics or calibrated tree classifiers.
3. **Quantellia LLC (US 10,643,152 B2; 2020):** Automated Decision Intelligence and Strategy Optimization. Conceptual causal decision diagrams, but lacks concrete mathematical state tensors and calibration error bounding.
4. **Palantir Technologies (US 9,892,372 B2; 2018):** Dynamic Ontology and Scenario Simulation. General-purpose semantic data integration platform, lacking domain-specific sensitivity Jacobians and tipping-point bisection.

### 9. What differentiates DecisionSphere?
DecisionSphere is differentiated by:
- Decoupling models from rigid database schemas into a unified continuous mathematical state-space vector $S_t \in \mathbb{R}^{24}$.
- Rigorous integration of Platt probability calibration to eliminate contractual penalty calculation distortion.
- First-of-a-kind cross-domain operational coupling linking commercial demand volume $\rightarrow$ logistics fulfillment delay risk $\rightarrow$ mandatory workforce overtime $\rightarrow$ calibrated employee turnover risk.
- Cryptographic runtime model digest verification guaranteeing bit-for-bit reproducibility.

### 10. What evidence supports the differentiation?
- **EXP-P01 / EXP-010:** Empirically proves DecisionSphere prevents $\$642,716.18$ in capital misallocation vs siloed commercial planning.
- **EXP-P02 / EXP-006:** Proves that ablating cross-domain coupling or calibration flips the strategic decision into a false-positive approval.
- **EXP-P05 / EXP-002:** Measures exact $72.74\%$ ECE reduction and $\$27,052.48$ penalty distortion elimination.
- **EXP-P07 / EXP-008:** Empirically demonstrates $\mathcal{O}(N)$ linear computational scaling.
- **Automated Tests:** 205/205 tests passing, including dedicated patent core tests (`tests/test_patent_core.py`).

### 11. What remains weak?
- **Cross-Dataset Coupling Limitations:** The testbed couples Rossmann (Germany), DataCo (Global), and IBM HR (US) datasets via heuristic normalization constants (`ASM-001` to `ASM-008`). While mathematically sound, an aggressive patent examiner may argue this represents an artificial synthetic benchmark rather than a unified production enterprise environment.
- **Section 3(k) Sensitivity:** Because the downstream output includes a financial metric (Net Profit Delta $\Delta \Pi$), the application is highly vulnerable to knee-jerk rejection as a business method unless the claims are strictly framed around the computer-implemented data transformation pipeline.

### 12. What should be filed?
A **Provisional Patent Application** should be prepared focusing exclusively on:
1. The computer-implemented method for state-space scenario propagation across heterogeneous ML estimators.
2. The calibrated probability-to-penalty error-bounding pipeline.
3. The topological DAG state transition operator.
4. The cryptographic runtime model integrity controller.

### 13. What should NOT be claimed?
- Commercial marketing strategies, discount policies, or promotional campaigns.
- Mathematical profit calculation formulas or financial statements.
- General "decision support" or "business intelligence" dashboards.
- Generic XGBoost or Platt scaling algorithms in the abstract.

### 14. What should remain confidential?
Prior to filing a provisional application:
- The exact proprietary source code of `src/scenario/propagation.py`, `src/scenario/graph.py`, and `src/scenario/state.py`.
- The specific mathematical claim wording and claim dependency hierarchy.
- The precise architectural interaction between Platt calibration constants and step-loss penalty curves.

### 15. Is provisional filing reasonable?
**YES, highly reasonable.** A provisional filing establishes an immediate priority date (protecting the technical core before conference/journal publication) at very low filing cost, providing a 12-month window to either complete the formal PCT/complete application or pivot entirely to academic publication without loss of priority.

### 16. What must a patent agent verify?
1. Formal compliance of claim language with Indian Patent Office CRI Guidelines (2017) to ensure Section 3(k) exclusion is overcome.
2. Validation that the technical effects recited in `patent/TECHNICAL_EFFECT_EVIDENCE.md` are integrated into the independent claim limitations.
3. Freedom-to-operate (FTO) review against the 27 identified prior art references in `patent/PRIOR_ART_MATRIX.csv` (especially o9 Solutions and Kinaxis).
4. Review of institutional IP ownership policies under VIT SCOPE regulations.
