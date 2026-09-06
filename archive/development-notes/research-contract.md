# DecisionSphere — Final Research Governance Contract

**Document Status:** FROZEN RESEARCH CONTRACT (PHASE 9+)  
**Date:** September 5, 2026  
**Governing Authority:** DecisionSphere Engineering Protocol (`AGENTS.md`)  
**Target Milestone:** BCSE497J Review 2 / TRL 4 Functional Prototype  

---

## 1. Research Problem Statement
Strategic business planning requires anticipating cross-domain ripple effects before capital commitments are made. However, modern enterprise analytics systems operate in functional silos: demand forecasting models in commercial sales, delivery risk classifiers in logistics, and attrition predictors in human resources. Cross-domain interactions—such as a promotional sales surge causing logistics carrier delays, stockout order cancellations, operational overtime spikes, and employee burnout—are typically evaluated post-hoc. Enterprise decision-makers lack an open, auditable, and scientifically defensible decision-support architecture capable of coupling heterogeneous predictive models with managerial accounting to evaluate these multi-domain trade-offs.

---

## 2. Research Gap
1. **Siloed Benchmark Optimization:** Prior literature optimizes isolated machine learning benchmarks ($R^2$, ROC-AUC, PR-AUC) without modeling downstream operational friction or financial consequences.
2. **Proprietary & Opaque Simulators:** Enterprise digital twins and ERP simulation suites typically require invasive proprietary enterprise integrations and lack open, auditable coupling between statistical model inferences and accounting identities.
3. **Generative AI Hallucination:** Recent attempts to use generative AI / LLMs as corporate decision agents suffer from numerical hallucination, non-deterministic outputs, and an inability to enforce mathematical accounting identities.

---

## 3. Research Questions

### Primary Research Question
> **RQ-Primary:**  
> *Can heterogeneous machine learning models across demand forecasting, logistics delivery risk, and workforce attrition be coupled with deterministic managerial accounting into an auditable scenario-based decision-support system that exposes operational trade-offs and capital-destructive scenarios that isolated commercial models fail to detect?*

### Secondary Research Questions
- **RQ-1 (Cross-Domain Information Gain):** Under what conditions and shock intensities does multi-domain integrated evaluation diverge from single-domain commercial forecasts?
- **RQ-2 (Decoupled Risk-Return Evaluation):** Does evaluating operational execution strain (CRS) independently from net incremental profit ($\Delta \text{Profit}$) within a lexicographic decision framework prevent the approval of profitable yet operationally volatile scenarios?
- **RQ-3 (Parametric Invariance & Sensitivity):** Over what tolerance margins do strategic recommendations remain stable when cross-domain coupling parameters (`ASM-001` to `ASM-010`) undergo systematic perturbation?
- **RQ-4 (Attribution Concordance):** Can pre-computed local TreeSHAP feature attributions be directionally aligned with condition-action rule triggers to provide an empirical rationale for recommended strategic interventions?

---

## 4. Core Novelty & Contributions

### 4.1 Defensible Novelty Formulation
> **Defensible Novelty:**  
> *"A decision-support architecture that couples calibrated machine learning models across demand, logistics, and workforce domains with parameterized operational propagation, deterministic managerial accounting, an operational execution risk index, and lexicographic decision gating to evaluate cross-domain trade-offs in scenario-based planning."*

### 4.2 Demarcation of Contributions
- **Methodological Contribution:**
  1. A transparent **6-Tier Epistemic Hierarchy** (`OBSERVED`, `PREDICTED`, `ASSUMED`, `PROPAGATED`, `CALCULATED`, `RECOMMENDED`) preventing statistical inferences from masquerading as empirical facts.
  2. A **Centralized Parametric Assumption Registry** (`ASM-001` to `ASM-010`) establishing transparent coupling constants.
  3. A **Lexicographic Multi-Objective Decision Framework** that strictly prioritizes capital preservation ($\Delta \text{Profit} > 0$) before evaluating operational strain ($\text{CRS} \le 50.0$).
- **Engineering Contribution:**
  1. A decoupled, high-throughput **Modular Monolith** (FastAPI + React + PostgreSQL) executing complete multi-domain simulations in $<500\text{ms}$.
  2. An **8-Tuple Provenance Signature** ($\Sigma_{\text{run}}$) guaranteeing bitwise-verifiable historical execution.
- **Non-Novel Elements (Explicitly Declared):**
  XGBoost, Logistic Regression, Scikit-learn, FastAPI, React, PostgreSQL, Docker, Alembic, standard TreeSHAP algorithms.

---

## 5. Research Assumptions & Limitations

### 5.1 The Synthetic Coupling Testbed
Rossmann (Retail Sales, 2013–2015), DataCo (Logistics, 2015–2018), and IBM HR (Workforce Survey) originate from different organizations and time periods.
- **Mandatory Statement:** These datasets serve as a **Normalized Synthetic Coupling Testbed** demonstrating computational and methodological viability; they do not represent an observed historical single company.

### 5.2 Strict Anti-Causality Principle
- Predictive models estimate statistical conditional expectations ($P(Y \mid X)$).
- Scenario parameter shocks represent parameterized assumptions, not natural experiments.
- SHAP values represent local statistical feature importances, not causal mechanisms.
- All system text, documentation, APIs, and UI elements must use non-causal language.

---

## 6. Primary Hypotheses & Evaluation Metrics

| Hypothesis | Independent Variable (IV) | Dependent Variable (DV) | Primary Metric | Success Criterion | Falsification Criterion |
|---|---|---|---|---|---|
| **$H_1$ (Decision Divergence)** | Commercial shock intensity ($\Delta D_{\text{pct}}$) | Final Strategic Decision Category | Decision Divergence Rate ($\text{DDR}$) | $\text{DDR} \ge 20\%$ for high-shock scenarios ($\Delta D \ge +30\%$) | $\text{DDR} < 20\%$, meaning integrated evaluation rarely changes decisions relative to sales forecasts. |
| **$H_2$ (Profit Inversion Point)** | Demand sales uplift ($\Delta D$) | Net Incremental Profit ($\Delta \text{Profit}$) | Net Marginal Profit $\frac{\partial (\Delta \text{Profit})}{\partial (\Delta D)}$ | Detection of critical inflection threshold $\Delta D^*$ where marginal profit turns negative | $\Delta \text{Profit}$ is strictly monotonically increasing across all $\Delta D \in [0, 100\%]$. |
| **$H_3$ (Decision Invariance)** | Coupling parameters (`ASM-001` to `ASM-010`) | Strategic Recommendation Invariance | Distance to boundary $\delta_{\text{boundary}} = \min \|\theta - \theta_{\text{flip}}\|$ | Primary decision stable across baseline operational tolerance margin | Erratic recommendation flipping under trivial parameter variations ($<5\%$). |
| **$H_4$ (Attribution Concordance)** | User scenario levers (Promo, SLA offset, Overtime) | Directional shift of TreeSHAP attributions ($\Delta \overline{\text{SHAP}}_j$) | Directional Agreement Ratio ($\text{DAR}$) & Spearman's $\rho$ | $\text{DAR} \ge 85\%$ and $\rho > 0.70$ across perturbed scenario feature vectors | $\text{DAR} < 85\%$ or $\rho \le 0.70$, indicating attributions fail to directionally track scenario levers. |

---

## 7. Comparator Baselines

1. **`BASE-1` (Isolated Commercial Forecast / Demand-Only):** Evaluates strictly $\Delta \text{Revenue} > 0 \implies \mathbf{PROCEED}$. Completely blind to delivery failures and employee turnover.
2. **`BASE-2` (Isolated Supply Chain Risk / Logistics-Only):** Evaluates strictly $\bar{P}(\text{Late}) \le 0.50 \implies \mathbf{PROCEED}$. Ignores whether commercial margins easily absorb delay penalties.
3. **`BASE-3` (Isolated HR Workforce / Workforce-Only):** Evaluates strictly $\bar{P}(\text{Att}) \le 0.20 \implies \mathbf{PROCEED}$. Ignores commercial necessity of temporary overtime surges.
4. **`BASE-4` (Unweighted Linear Scalarization):** Evaluates composite utility $U = \Delta \text{Profit} - \lambda \cdot \text{CRS}$. Fails to preserve non-compensatory capital preservation boundaries.

---

## 8. Experimental Protocol Suite

- **Experiment A (Cross-Domain Information Gain):** 500 randomized scenarios evaluated against `BASE-1` to measure Decision Divergence Rate ($H_1$).
- **Experiment B (Response Surface Dynamics):** 798-point grid sweep across demand growth, SLA offset, and overtime to map profit inversion and marginal returns ($H_2$).
- **Experiment C (Explainability Concordance):** Directional agreement analysis between TreeSHAP values and recommendation rule triggers ($H_4$).
- **Experiment D (Parametric Sensitivity Analysis):** Systematic perturbation sweeps across `ASM-001` through `ASM-010` to map decision flip thresholds ($H_3$).
- **Experiment E (Domain Ablation Study):** Sequential removal of individual analytical domains to quantify the information loss and decision failure modes of ablated architectures.
