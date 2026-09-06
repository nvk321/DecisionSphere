# DecisionSphere: Assumptions, Open Questions, and Scientific Limitations

**Transparent Epistemic Boundary Registry, Theoretical Bounds, and Threat-to-Validity Analysis**  
*Academic Standard: TRL 4 / IEEE & Scopus Research Protocol*  
*Analytical Core Status: FROZEN & INVARIANT*

---

## 1. Epistemic Posture & Academic Honesty

Scientific credibility requires transparent articulation of experimental boundaries and operational assumptions. DecisionSphere is a decision-support and scenario-evaluation platform at **Technology Readiness Level 4 (TRL 4)** (laboratory-validated system prototype).

This document establishes the explicit boundary between what DecisionSphere **demonstrates empirically** versus where it relies on **operational modeling assumptions**.

---

## 2. Dataset Boundaries & Benchmark Limitations

### 2.1 Multi-Source Benchmark Separation (The "Synthetic Enterprise" Testbed)
- **Nature of the Data:** DecisionSphere utilizes three distinct public benchmark datasets:
  - *Rossmann Store Sales* (Germany, European retail pharmacy chain).
  - *DataCo Smart Supply Chain* (Latin America / USA, multi-category e-commerce and logistics).
  - *IBM HR Analytics Employee Attrition* (Global corporate software/tech benchmark).
- **Limitation:** These three datasets do **not** originate from a single physical enterprise. DecisionSphere does not claim that Rossmann stores dispatch via DataCo freight or employ IBM HR personnel.
- **Scientific Defense:** The platform integrates these datasets into a **normalized enterprise scenario environment** to evaluate cross-domain coupling dynamics under realistic empirical variance, noise, and distribution shapes that cannot be simulated via purely synthetic random generators.

### 2.2 Temporal and Granularity Constraints
- **Demand Data:** Tracks daily aggregated store-level turnover. It lacks SKU-level basket transaction details and real-time inventory on hand.
- **Logistics Data:** Spans historical orders between 2015 and 2018. Changes in post-pandemic carrier economics, fuel surcharges, and maritime supply chains are not reflected in historical DataCo weights.
- **Workforce Data:** IBM HR is a cross-sectional dataset without longitudinal timestamped attrition events, meaning that employee departure timing within a fiscal year is not directly observable.

### 2.3 Synthetic Nature of IBM HR Benchmark
- **Limitation:** The IBM HR dataset is an artificial benchmark created by IBM data scientists and Watson analytics teams to simulate employee attrition characteristics. While structurally realistic and widely cited in literature, it is not an exhaustive record of real human labor transactions.

---

## 3. Machine Learning & Statistical Limitations

### 3.1 Causal Inference vs Observed Associations (The Anti-Causality Rule)
- **Limitation:** DecisionSphere's machine learning models are predictive ($P(Y \mid X)$), not structural causal models ($P(Y \mid \text{do}(X))$).
- **Specific Boundary:**
  - The observed $+82.5\%$ sales lift associated with `Promo=1` in Rossmann is a **statistical association**, not an experimental randomized controlled trial (RCT) treatment effect.
  - The $3.0\times$ higher attrition rate observed among `OverTime='Yes'` workers does not prove that overtime alone caused employee resignations; confounding variables such as management friction or workplace toxicity may be co-present.
- **Rule:** DecisionSphere strictly prohibits claiming that promotions *cause* sales lifts or that SHAP values represent *physical causal mechanisms*.

### 3.2 Lookahead Leakage Prevention & Excluded Predictors
- **Limitation:** In the DataCo supply chain dataset, variables such as `Days for shipping (real)`, `Delivery Status`, and `Order Item Profit Ratio` are recorded *after* an order has been shipped.
- **Mitigation:** These variables are strictly quarantined in `PROHIBITED_LOOKAHEAD_COLUMNS` (`src/data/dataco_features.py`) and excluded from model training. The classifier relies solely on features known at order checkout time. While this reduces apparent test accuracy from $99\%$ (leaky) to $77\%$ (realistic), it ensures valid inference.

### 3.3 Probability Calibration Bounds
- **Limitation:** Sigmoid (Platt) scaling assumes a monotonic logistic transformation of decision scores. In regions of extreme feature space sparsity, calibrated probabilities carry wider confidence bounds.
- **Mitigation:** Evaluated using Brier Score ($\text{BS} \le 0.10$) and reliability curve inspection across 10 probability bins.

---

## 4. Cross-Domain Coupling Assumptions Registry

To enable cross-domain simulation, DecisionSphere defines eight formal operational coupling parameters (`ASM-001` to `ASM-008`):

| Parameter ID | Parameter Name | Default Baseline Value | Epistemic Status | Sensitivity Bounds | Methodological Justification |
|:---:|:---|:---:|:---:|:---:|:---|
| `ASM-001` | `unit_price_usd` | $\$25.00$ | `ASSUMED` | $\$15.00 - \$50.00$ | Normalized average selling price per retail merchandise unit. |
| `ASM-002` | `cogs_ratio` | $0.60$ ($60\%$) | `ASSUMED` | $0.40 - 0.75$ | Standard retail gross margin benchmark ($40\%$ gross margin). |
| `ASM-003` | `base_logistics_cost_per_order` | $\$8.50$ | `ASSUMED` | $\$5.00 - \$15.00$ | Ground freight packaging and carrier handling cost per standard shipment. |
| `ASM-004` | `turnover_replacement_cost` | $\$30,000.00$ | `ASSUMED` | $\$15,000 - \$60,000$ | Society for Human Resource Management (SHRM) benchmark for recruiting, onboarding, and productivity loss (approx. $50\%$ of annual salary). |
| `ASM-005` | `carrier_late_penalty` | $\$25.00$ | `ASSUMED` | $\$10.00 - \$50.00$ | Contractual customer concession credit and return handling fee for SLA breach. |
| `ASM-006` | `wlb_decrement_overtime` | $-1.0$ level | `ASSUMED` | $-0.5 \text{ to } -2.0$ | WorkLifeBalance scale reduction (from 4-point Likert scale) induced by mandatory sustained overtime. |
| `ASM-007` | `baseline_cycle_volume` | $10,000$ units | `ASSUMED` | Fixed Testbed | Normalized 14-day operational cycle volume for the enterprise testbed. |
| `ASM-008` | `baseline_dispatch_orders` | $1,000$ orders | `ASSUMED` | Fixed Testbed | Normalized batch shipment scale mapping units to discrete parcels. |

---

## 5. Managerial Accounting & Financial Limitations

### 5.1 Linear Scaling Assumptions
- **Limitation:** Costs are modeled via linear piece-wise accounting functions. Non-linear step-function costs (e.g., leasing an entire additional warehouse when capacity exceeds $110\%$) are not modeled in the baseline engine.
- **Scientific Rationale:** Linear accounting guarantees complete mathematical traceability and satisfies managerial accounting standards for short-term operational horizons (14 to 30 days).

### 5.2 Capital Structure & Fixed Overheads
- **Limitation:** DecisionSphere focuses strictly on **Operating Margin Delta** ($\Delta \Pi$). It does not model corporate tax, interest expense, capital depreciation (EBITDA adjustments), or long-term brand equity depreciation.

---

## 6. Strategic Recommendation & Policy Threshold Limitations

### 6.1 Rule Engine Heuristics
- **Limitation:** Recommendations (`PROCEED`, `PROCEED_WITH_MITIGATIONS`, `REJECT_RESTRUCTURE`) are synthesized via 7 deterministic rule triggers (`RULE-01` to `RULE-07`), not by solving an unconstrained multi-objective Pareto optimization problem.
- **Defense:** In enterprise strategic planning, executives reject black-box optimization whose constraints are opaque. Rule-grounded synthesis provides explicit, auditable rationales that reference specific policy violations (e.g., Margin Erosion under `RULE-04`).

### 6.2 Composite Risk Score Weights
- **Limitation:** The default weighting scheme under `ASM-009` is:
  $$\text{CRS} = 0.40 R_{\text{supply}} + 0.40 R_{\text{workforce}} + 0.20 R_{\text{demand}}$$
- **Sensitivity:** If an organization prioritizes customer delivery above employee turnover, supply chain risk weight can be tuned via policy controls (enforcing the simplex constraint $w_s + w_w + w_d = 1.0$). Notebook 12 (`12_sensitivity_analysis.ipynb`) confirms that the CRS is stable under $\pm 20\%$ weight perturbations.

---

## 7. Operational & Production Limitations

- **Offline Training / Inference Only:** Models are trained offline and serialized (`.joblib`). DecisionSphere does not support online continuous streaming gradient updates during user simulation requests.
- **Single-Node Containerization:** Designed for single-node Docker / docker-compose deployment at TRL 4. It does not require or implement distributed cluster orchestration (Kubernetes/Kafka).
- **Browser Compatibility:** Web interface is optimized for modern desktop viewports ($\ge 1280\text{px}$) for complex multi-chart decision intelligence displays.

---

## 8. Summary of Threats to Validity

| Threat Type | Identified Risk | Architectural Mitigation in DecisionSphere |
|:---|:---|:---|
| **Construct Validity** | Cross-domain metrics may not capture all operational nuances. | 6-tier epistemic hierarchy cleanly separates measured data from operational assumptions. |
| **Internal Validity** | Lookahead leakage in logistics features. | Comprehensive exclusion registry quarantines post-order columns (`PROHIBITED_LOOKAHEAD_COLUMNS`). |
| **Statistical Conclusion Validity** | Overconfident probabilities on imbalanced classes. | Sigmoid calibration verified via Brier Score and reliability diagrams. |
| **External Validity** | Benchmark data may not generalize to arbitrary companies. | Full sensitivity analysis suite evaluates model robustness across assumption boundaries. |
