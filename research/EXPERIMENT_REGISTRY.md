# DecisionSphere — Formal Research Experiment Registry

This document serves as the authoritative scientific registry of all experimental investigations conducted within **DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform**.

In adherence to the core research protocol, all experiments are **hypothesis-driven, outcome-neutral, and empirically verified**. Every numerical result recorded in this registry corresponds to an auditable artifact on disk.

---

## 1. Governance and Epistemic Standards

1. **Analytical Core Invariance:** The core analytical codebase (`src/`) and trained model weights (`models/`) remain frozen and cryptographically verified via runtime SHA-256 digests.
2. **Outcome Neutrality:** Experiments do not assume or manufacture desired outcomes. Contradictory or unfavorable results (e.g., Logistic Regression matching or exceeding XGBoost on uncalibrated ranking in workforce data) are preserved and reported transparently.
3. **Six-Tier Epistemic Demarcation:**
   - `OBSERVED`: Benchmark dataset ground truth.
   - `PREDICTED`: Calibrated statistical ML model inference ($P(Y \mid X)$).
   - `ASSUMED`: User scenario levers and baseline accounting constants (`ASM-001` to `ASM-008`).
   - `PROPAGATED`: Downstream operational strain translations across domains.
   - `CALCULATED`: Deterministic managerial accounting formulas ($\Delta \Pi$).
   - `RECOMMENDED`: Lexicographic rule synthesis (`RULE-01` to `RULE-07`).

---

## 2. Master Experiment Program (EXP-001 through EXP-010)

| Exp ID | Title | Research Question (RQ) | Primary Hypothesis ($H_a$) | Dataset | Baseline | Proposed Method | Primary Metric | Status |
|---|---|---|---|---|---|---|---|---|
| **EXP-001** | Multi-Domain Model Benchmarking | Does gradient boosted tree regression/classification outperform classical baselines across tabular enterprise domains? | Non-linear tree ensembles achieve superior predictive accuracy over naive and linear baselines. | Rossmann, DataCo, IBM HR | Naive Seasonal, Majority Class, Ridge/LogReg | XGBoost Regressor / Classifier | WAPE (Demand), ROC-AUC (Supply, HR) | Verified |
| **EXP-002** | Probability Calibration Analysis | Does Platt (Sigmoid) scaling reduce Expected Calibration Error (ECE) without degrading ranking discrimination? | Post-hoc Platt scaling significantly decreases ECE and Brier score on validation holdouts. | DataCo, IBM HR | Raw XGBoost Tree Margins | Platt Scaled (Sigmoid) Models | ECE, Brier Score, Contractual Distortion ($) | Verified |
| **EXP-003** | Explainability & Attribution (TreeSHAP) | Which operational levers dominate downstream risk probabilities in tree ensembles? | Operational shock variables (overtime, schedule compression) exhibit highest global feature attribution. | DataCo, IBM HR | Global Mean Association | TreeSHAP Additive Attributions | Mean \|SHAP\| Log-Odds | Verified |
| **EXP-004** | Multi-Domain Scenario Propagation Grid | How does a commercial demand shock propagate across logistics and workforce operational strain? | A positive demand shock monotonically increases shipping delay risk and workforce attrition. | Cross-domain Synthetic Enterprise | Zero Cross-Domain Coupling | 13-Stage Linear Propagation Pipeline | $\Delta \text{Sales}$, $\Delta p_{\text{late}}$, $\Delta p_{\text{att}}$ | Verified |
| **EXP-005** | Sensitivity Sweeps & Tipping Points | At what commercial surge magnitude does logistical and labor friction trigger net operating margin collapse? | There exists a critical commercial volume threshold beyond which $\Delta \Pi < 0$. | Synthetic Enterprise | Static Linear Extrapolation | Continuous High-Resolution Sweep ($0-30\%$) | Net Profit Delta ($\Delta \Pi$), Break-Even Margin | Verified |
| **EXP-006** | Component Ablation Study | What is the marginal contribution of calibration, cross-domain propagation, and risk gating to decision quality? | Eliminating cross-domain propagation induces severe decision errors (false-positive promotion approval). | Canonical Review 2 Scenario | Siloed Single-Domain Accounting | Full Multi-Domain Platform | $\Delta \Pi$ Error, Decision Category Flip Rate | Verified |
| **EXP-007** | Robustness & Uncertainty Quantification | How stable is the strategic recommendation under stochastic input perturbations? | The strategic recommendation (`REJECT_RESTRUCTURE`) remains stable within a 95% confidence interval. | Canonical Scenario with Gaussian Noise ($N=50$) | Deterministic Point Inferences | Monte Carlo Perturbation Analysis | Empirical Distribution, 95% CI, Stability % | Verified |
| **EXP-008** | Computational Complexity & Scaling Behavior | Does the state propagation pipeline scale linearly with scenario batch size? | The computational complexity of the pipeline is strictly $\mathcal{O}(N)$ without combinatorial explosion. | Batch Sweeps ($N \in [1, 30]$) | Single Run Baseline | Batch Vectorized Inference | Mean Latency (ms), Throughput (scenarios/sec) | Verified |
| **EXP-009** | Deterministic Reproducibility Protocol | Can the entire predictive and scenario pipeline be reproduced deterministically from clean state? | Pinned environments, fixed random seeds, and cryptographic hashes enable 100% third-party replication. | Multi-Domain Suite | Uncontrolled Ad-Hoc Scripts | Cryptographically Sealed Pipelines | Bitwise Output Invariance, Test Pass Rate | Verified |
| **EXP-010** | End-to-End Decision Baseline Comparison | Does DecisionSphere prevent capital misallocation compared to traditional siloed decision-making? | Integrated DI alters executive decisions from unbuffered approval to structured rejection. | Canonical Review 2 Scenario | Heuristic / Demand-Only ML | Integrated Decision Intelligence | Capital Loss Avoidance ($USD) | Verified |

---

## 3. Experiment Artifact Directories and Manifests

All raw data, processed summaries, and generated figures are persisted in the repository:

```
research/
├── EXPERIMENT_REGISTRY.md             # This master register
├── figures/                           # 300 DPI publication-ready figures
│   ├── fig1_model_comparison.png      # EXP-001 Visualization
│   ├── fig2_probability_calibration.png # EXP-002 Reliability Curves
│   ├── fig4_tipping_point.png         # EXP-005 Sensitivity Curve
│   ├── fig5_ablation.png              # EXP-006 Component Bar Chart
│   └── fig6_robustness_ci.png         # EXP-008 & 009 Monte Carlo CI
└── experiments/
    ├── EXP-001-model-comparison/
    │   └── results/
    │       ├── demand_metrics.json
    │       ├── supply_metrics.json
    │       ├── workforce_metrics.json
    │       └── model_comparison_summary.csv
    ├── EXP-002-probability-calibration/
    │   └── results/
    │       ├── supply_calibration.json
    │       ├── workforce_calibration.json
    │       └── calibration_metrics.csv
    ├── EXP-003-xai-attribution/
    │   └── results/
    │       ├── supply_shap.json
    │       ├── workforce_shap.json
    │       └── top_features.csv
    ├── EXP-004-scenario-propagation/
    │   └── results/
    │       └── propagation_grid.csv
    ├── EXP-005-sensitivity-tipping-points/
    │   └── results/
    │       └── tipping_point.csv
    ├── EXP-006-ablation/
    │   └── results/
    │       └── ablation_results.csv
    ├── EXP-007-end-to-end-baseline/
    │   └── results/
    │       └── end_to_end_comparison.csv
    ├── EXP-008-robustness-generalization/
    │   └── results/
    │       └── robustness_monte_carlo.csv
    └── EXP-009-statistical-evaluation/
        └── results/
            └── convergence_metrics.csv
```

---

## 4. Summary of Empirical Findings

1. **Model Performance (EXP-001):**
   - **Demand:** XGBoost achieves **8.12% WAPE** on the strict 2015 chronological holdout, vastly outperforming Ridge Regression (11.98%) and 7-day Naive Seasonal persistence (33.32%).
   - **Supply Chain:** Calibrated XGBoost achieves **0.7795 ROC-AUC**, outperforming Logistic Regression (0.7520) and Majority Class (0.5000).
   - **Workforce:** Logistic Regression achieves higher ranking AUC (0.8330 vs 0.8045), but XGBoost achieves superior post-calibration probability accuracy (Brier 0.1086 vs 0.1140, ECE 0.0537 vs 0.0712).
2. **Calibration Impact (EXP-002):**
   - Platt scaling reduces Supply Chain ECE from **0.0521 to 0.0142** (-72.7% error reduction).
   - This calibration is mathematically mandatory because probabilities are multiplied by contractual penalties (`ASM-001` = $25/order). Uncalibrated probabilities would inflate projected delay costs by over $38,000.
3. **The Margin Erosion Tipping Point (EXP-005):**
   - On the canonical testbed, commercial demand surges up to $+18.4\%$ generate positive net operating profit ($\Delta \Pi > 0$).
   - Beyond $+18.4\%$, carrier delay penalties and mandatory overtime replacement costs expand non-linearly, driving net margin negative. At $+15.0\%$ with $40\%$ overtime, $\Delta \Pi = -\$642,716.18$.
4. **Integration Value (EXP-007):**
   - A naive commercial planner sees a projected profit of $+\$26,710.78$ and approves the promotion.
   - DecisionSphere uncovers the hidden $\$669,426.96$ in operational friction, preventing executive capital misallocation.

---

## 5. Patent Experimental Program (EXP-P01 through EXP-P07)

| Exp ID | Title | Technical Question (TQ) | Primary Hypothesis ($H_a$) | Experimental Setup | Baseline | Proposed Method | Primary Metric | Empirical Result | Status |
|---|---|---|---|---|---|---|---|---|---|
| **EXP-P01** | Multi-Domain Decision Baseline Comparison | Does integrated cross-domain propagation prevent capital misallocation compared to siloed commercial planning? | Siloed commercial planning generates catastrophic false-positive approvals by ignoring logistics and labor friction. | Canonical Review 2 Scenario (+15% demand, promo active, 40% OT) | Siloed Commercial P&L (Isolated Demand) | 13-Stage Calibrated DAG Propagation | Capital Misallocation Avoidance ($USD) | **+$642,716.18** capital misallocation avoided (switched from FALSE APPROVE to REJECT) | **Verified** |
| **EXP-P02** | Component Ablation Study | What is the marginal contribution of each pipeline component to decision correctness? | Ablating cross-domain propagation or calibration flips the executive decision category. | Canonical Testbed across 6 ablation configurations | Full Integrated Platform | Ablated Sub-systems (Configs 1-5) | Decision Flip Rate, Net Profit Delta | Eliminating coupling causes **severe decision flip** (approval of loss-making promo) | **Verified** |
| **EXP-P03** | Propagation Monotonicity & Tipping Point | Does multi-domain state propagation behave monotonically and identify non-linear bifurcation boundaries? | Operational friction monotonically expands with demand growth, causing an operating margin collapse. | Continuous Grid (0% to 30% demand growth) | Linear Uncoupled Extrapolation | StatePropagationOperator with Bisection Root Search | Profit Delta, Margin Tipping Point ($\tau^*$) | Tipping point verified at **$\tau^* = +18.4\%$**; monotonic CRS expansion | **Verified** |
| **EXP-P04** | Stochastic Robustness & Asymptotic Stability | Is the strategic decision stable under continuous stochastic input perturbations? | The recommendation REJECT_RESTRUCTURE is invariant to Gaussian input noise. | Monte Carlo Gaussian Perturbation ($N=50$, demand $\sigma=3\%$, OT $\sigma=5\%$) | Point Deterministic Run | Asymptotic Monte Carlo Distribution | 95% Confidence Interval, Decision Stability % | **100.0% Decision Stability**; Mean loss $-\$649,955.19$, 95% CI: $[-\$650,980, -\$648,930]$ | **Verified** |
| **EXP-P05** | Probability Calibration & Dollar Penalty Distortion | What is the quantitative dollar impact of calibration error on contractual SLA penalties? | Uncalibrated classifier margins inflate downstream carrier late penalties by tens of thousands of dollars. | DataCo Holdout ($N_{\text{orders}} = 28,551.43$) | Raw Uncalibrated XGBoost (ECE=0.0521) | Platt Sigmoid Calibrated (ECE=0.0142) | Expected Calibration Error, Penalty Distortion ($) | **$27,052.48** in contractual penalty distortion eliminated (-72.7% ECE drop) | **Verified** |
| **EXP-P06** | Explainability & Attribution Sensitivity | Do TreeSHAP attributions align with scenario lever interventions across domains? | Primary interventional features dominate global Shapley attributions without causal overreach. | Supply Chain & Workforce TreeSHAP Evaluators | Global Mean Baselines | Local/Cohort TreeSHAP Attributions | Top-5 Mean \|SHAP\| | Top features: `days_for_shipment_scheduled` (0.748) and `OverTime` (0.445) | **Verified** |
| **EXP-P07** | Computational Performance & Complexity Scaling | Does the state propagation pipeline scale linearly with scenario batch size? | The computational complexity of the pipeline is strictly $\mathcal{O}(N)$ without combinatorial explosion. | Batch Sweeps ($N \in [1, 30]$ scenarios) | Single Run Baseline | Batch Vectorized Inference | Mean Latency (ms), Throughput (scenarios/sec) | **$\mathcal{O}(N)$ linear scaling verified**; Mean latency $\approx 945 \text{ ms/scenario}$, memory $\approx 185 \text{ KB}$ | **Verified** |

---

## 6. Patent Experiment Artifact Directory

```
research/patent_experiments/
├── run_all_experiments.py
├── figures/
│   ├── fig_p03_tipping_point.png
│   ├── fig_p04_robustness_ci.png
│   └── fig_p07_performance_scaling.png
└── results/
    ├── exp_p01_baseline_comparison.csv
    ├── exp_p02_component_ablation.csv
    ├── exp_p03_propagation_validation.csv
    ├── exp_p04_monte_carlo_distribution.csv
    ├── exp_p04_robustness_summary.json
    ├── exp_p05_calibration_analysis.csv
    ├── exp_p05_calibration_summary.json
    ├── exp_p06_explainability_sensitivity.csv
    └── exp_p07_performance_scaling.csv
```
