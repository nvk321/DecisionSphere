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

## 2. Master Experiment Program (EXP-001 through EXP-009)

| Exp ID | Title | Research Question (RQ) | Primary Hypothesis ($H_a$) | Dataset | Baseline | Proposed Method | Primary Metric | Status |
|---|---|---|---|---|---|---|---|---|
| **EXP-001** | Multi-Domain Model Benchmarking | Does gradient boosted tree regression/classification outperform classical baselines across tabular enterprise domains? | Non-linear tree ensembles achieve superior predictive accuracy over naive and linear baselines. | Rossmann, DataCo, IBM HR | Naive Seasonal, Majority Class, Ridge/LogReg | XGBoost Regressor / Classifier | WAPE (Demand), ROC-AUC (Supply, HR) | Verified |
| **EXP-002** | Probability Calibration Analysis | Does Platt (Sigmoid) scaling reduce Expected Calibration Error (ECE) without degrading ranking discrimination? | Post-hoc Platt scaling significantly decreases ECE and Brier score on validation holdouts. | DataCo, IBM HR | Raw XGBoost Tree Margins | Platt Scaled (Sigmoid) Models | ECE, Brier Score | Verified |
| **EXP-003** | Explainability & Attribution (TreeSHAP) | Which operational levers dominate downstream risk probabilities in tree ensembles? | Operational shock variables (overtime, schedule compression) exhibit highest global feature attribution. | DataCo, IBM HR | Global Mean Association | TreeSHAP Additive Attributions | Mean \|SHAP\| Log-Odds | Verified |
| **EXP-004** | Multi-Domain Scenario Propagation Grid | How does a commercial demand shock propagate across logistics and workforce operational strain? | A positive demand shock monotonically increases shipping delay risk and workforce attrition. | Cross-domain Synthetic Enterprise | Zero Cross-Domain Coupling | 13-Stage Linear Propagation Pipeline | $\Delta \text{Sales}$, $\Delta p_{\text{late}}$, $\Delta p_{\text{att}}$ | Verified |
| **EXP-005** | Sensitivity Sweeps & Tipping Points | At what commercial surge magnitude does logistical and labor friction trigger net operating margin collapse? | There exists a critical commercial volume threshold beyond which $\Delta \Pi < 0$. | Synthetic Enterprise | Static Linear Extrapolation | Continuous High-Resolution Sweep ($0-30\%$) | Net Profit Delta ($\Delta \Pi$), Break-Even Margin | Verified |
| **EXP-006** | Component Ablation Study | What is the marginal contribution of calibration, cross-domain propagation, and risk gating to decision quality? | Eliminating cross-domain propagation induces severe decision errors (false-positive promotion approval). | Canonical Review 2 Scenario | Siloed Single-Domain Accounting | Full Multi-Domain Platform | $\Delta \Pi$ Error, Decision Category Flip Rate | Verified |
| **EXP-007** | End-to-End Decision Baseline Comparison | Does DecisionSphere prevent capital misallocation compared to traditional siloed decision-making? | Integrated DI alters executive decisions from unbuffered approval to structured rejection. | Canonical Review 2 Scenario | Heuristic / Demand-Only ML | Integrated Decision Intelligence | Capital Loss Avoidance ($USD) | Verified |
| **EXP-008** | Robustness & Uncertainty Quantification | How stable is the strategic recommendation under stochastic input perturbations? | The strategic recommendation (`REJECT_RESTRUCTURE`) remains stable within a 95% confidence interval. | Canonical Scenario with Gaussian Noise ($N=200$) | Deterministic Point Inferences | Monte Carlo Perturbation Analysis | Empirical Distribution, 95% CI | Verified |
| **EXP-009** | Statistical Convergence Evaluation | Does the Monte Carlo estimator converge asymptotically as sample size $N$ increases? | The standard error of the mean profit estimator decreases as $\mathcal{O}(1/\sqrt{N})$, stabilizing by $N \ge 100$. | Perturbation Grid ($N \in [10, 200]$) | Small Sample ($N=10$) | Asymptotic Sample Sweeps | Standard Error (SE), Confidence Interval Width | Verified |

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
