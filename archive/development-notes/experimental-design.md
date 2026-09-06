# DecisionSphere — Experimental Design Suite & Empirical Validation Protocol

## 1. Overview & Research Philosophy

This document defines the formal experimental protocols designed to test the hypotheses ($H_1$ to $H_4$) and answer the research questions (RQ1 to RQ4) formulated in `docs/research-direction.md`.

To establish a defensible Scopus/IEEE-calibre contribution, **DecisionSphere must be evaluated not merely as a software utility, but as an empirical scientific artifact**. The evaluation suite spans four core experiments (Experiments A–D) and a systematic component ablation study.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        EXPERIMENTAL SUITE                              │
├───────────────────┬───────────────────┬────────────────────────────────┤
│ Experiment A      │ Experiment B      │ Experiment C                   │
│ Isolated vs.      │ Scenario Shock    │ Explainability & Attribution   │
│ Integrated        │ Response Curves   │ Fidelity (TreeSHAP)            │
├───────────────────┴───────────────────┴────────────────────────────────┤
│ Experiment D: Parametric Sensitivity Analysis (Stress Testing)        │
├────────────────────────────────────────────────────────────────────────┤
│ Ablation Study: Progressive Component Deprivation (M0 through M4)      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Experiment A: Isolated vs. Integrated Decision Support

### 2.1 Scientific Objective
To directly test **Hypothesis $H_1$** (Trade-Off Discovery): verify whether single-domain predictive optimization (e.g., maximizing promotional demand) creates systematic blind spots by ignoring downstream logistics delay penalties and workforce attrition replacement costs.

### 2.2 Independent Variables & Treatments
- **Scenario Shock Space:** Evaluated across a standardized test cohort of 50 representative retail stores across 5 shock tiers:
  1. *Shock 0 (Baseline):* Normal operations ($\Delta D = 0\%$, no promo override, normal lead times).
  2. *Shock 1 (Mild Promotion):* $\Delta D = +10\%$, `Promo = 1`.
  3. *Shock 2 (Moderate Promotion):* $\Delta D = +25\%$, `Promo = 1`.
  4. *Shock 3 (Aggressive Promotion):* $\Delta D = +40\%$, `Promo = 1`.
  5. *Shock 4 (Extreme Disruption):* $\Delta D = +50\%$, $\Delta S = +3\text{ days}$ supplier delay.

- **Experimental Treatments:**
  - **Treatment 1 (Isolated Predictive Silo - Baseline Practice):**  
    - The Demand module forecasts sales volume $\hat{y}_{\text{base}}$ or $\hat{y}_{\text{promo}}$.
    - Financial evaluation is based purely on projected gross revenue:  
      $$\Delta \text{Revenue}_{\text{isolated}} = \sum (\hat{y}_{\text{sim}} - \hat{y}_{\text{base}}) \times \bar{P}$$
    - Supply chain delay risk and employee attrition are held constant at their unshocked historical averages.
    - *Decision Rule:* If $\Delta \text{Revenue}_{\text{isolated}} > 0$, the decision is approved as optimal.

  - **Treatment 2 (Integrated DecisionSphere Framework):**  
    - Demand shock propagates downstream:
      - Scaled order volume shifts logistics fulfillment pressure.
      - Scheduled delivery windows compress ($\Delta S$), increasing $P(\text{Late Delivery})$.
      - Unfulfilled demand penalty $\kappa_{\text{stockout}}$ degrades realized revenue.
      - Warehouse overtime ratio scales by $\Delta O$, shifting $P(\text{Attrition})$ and triggering replacement costs.
    - Financial evaluation computes the true Net Incremental Margin:  
      $$\Delta \text{Profit} = \Delta \text{Revenue}_{\text{realized}} - (\Delta \text{Cost}_{\text{COGS}} + \Delta \text{Cost}_{\text{delay}} + \Delta \text{Cost}_{\text{workforce}})$$
    - *Decision Rule:* Decision approved only if $\Delta \text{Profit} > 0$ and $\text{CRS} \le \tau_{\text{risk}}$.

### 2.3 Dependent Variables & Metrics
1. **Decision Divergence Rate (DDR):** Percentage of test scenarios where Isolated says "PROCEED" but Integrated says "REJECT / MITIGATE".
2. **Hidden Financial Loss (HFL):** Magnitude of uncaptured operational costs overlooked by the isolated system:  
   $$\text{HFL} = (\Delta \text{Cost}_{\text{delay}} + \Delta \text{Cost}_{\text{workforce}}) - \Delta \text{Cost}_{\text{isolated\_assumed}}$$
3. **Net Profit Delta ($\Delta \text{Profit}$):** True bottom-line financial change in currency units.
4. **Composite Risk Score ($\text{CRS}$):** Multi-domain risk index $\in [0, 100]$.

### 2.4 Experimental Protocol & Failure Criteria
- **Execution:** Automated headless Python script iterating over the test cohort, executing both Treatment 1 and Treatment 2, and logging outcome vectors to JSON/CSV.
- **Success Criteria:** Decision divergence occurs in $\ge 20\%$ of high-shock scenarios ($\Delta D \ge +30\%$), confirming $H_1$.
- **Falsification / Failure Criteria:** If $\Delta \text{Profit}$ perfectly correlates with $\Delta \text{Revenue}$ across all shock tiers (correlation $r > 0.98$), then cross-functional propagation provides no additional decision-relevant information, falsifying $H_1$.

---

## 3. Experiment B: Baseline vs. Multi-Magnitude Scenario Shocks

### 3.1 Scientific Objective
To evaluate the **non-linear response dynamics** and identify operational capacity inflection points (tipping points where incremental demand surges transition from profitable to value-destroying).

### 3.2 Parameter Sweep Space
Execute a fine-grained grid sweep across three operational dimensions:
1. **Demand Shock:** $\Delta D \in [-30\%, +60\%]$ at step size $5\%$ (19 levels).
2. **Logistics Delay Offset:** $\Delta S \in [0, 6\text{ days}]$ at step size $1\text{ day}$ (7 levels).
3. **Overtime Shift:** $\Delta O \in [0\%, 50\%]$ at step size $10\%$ (6 levels).
- Total evaluated grid configurations: $19 \times 7 \times 6 = 798$ scenario states.

### 3.3 Dependent Variables & Output Curves
1. **Demand Trajectory:** Forecasted sales units $\hat{y}_{\text{sim}}$.
2. **Logistics Failure Frontier:** Shift in mean predicted late delivery probability $P(\text{Late Delivery} = 1 \mid \Delta D, \Delta S)$.
3. **Workforce Burnout Frontier:** Shift in mean predicted attrition probability $P(\text{Attrition} = 1 \mid \Delta O)$.
4. **Profit Optimization Inversion:** The exact point $\Delta D^*$ where $\frac{\partial (\Delta \text{Profit})}{\partial (\Delta D)} = 0$, beyond which logistics penalties and overtime costs exceed marginal sales revenue.

### 3.4 Visualization & Deliverables
- Multi-dimensional response surface plots ($\Delta D \times \Delta S \rightarrow \Delta \text{Profit}$).
- Inflection point identification table documenting maximum sustainable promotional scale per store tier.

---

## 4. Experiment C: Explainability & Attribution Fidelity

### 4.1 Scientific Objective
To directly test **Hypothesis $H_3$** (Attribution Monotonicity & Defensibility): verify that TreeSHAP feature attributions reliably track scenario levers and provide an empirical justification for triggered recommendations without causal overreach.

### 4.2 Independent Treatments
- For a fixed store and time window, perturb individual scenario levers:
  - `Promo` state: $\{0, 1\}$.
  - Scheduled shipping days: $\{2, 3, 4, 5\text{ days}\}$.
  - Overtime status: $\{0, 1\}$.

### 4.3 Dependent Metrics
1. **Attribution Directional Concordance (ADC):**  
   Measures whether the sign of the SHAP attribution matches the operational direction of the lever:  
   $$\text{ADC} = \text{sign}(\phi_i(\mathbf{x}_{\text{shocked}}) - \phi_i(\mathbf{x}_{\text{base}})) \cdot \text{sign}(\Delta x_i)$$
   Target: $\text{ADC} = +1.0$ across 100% of tested levers.
2. **Attribution Monotonicity (AM):**  
   As $\Delta D$ increases incrementally, the magnitude of positive SHAP attribution $\phi_{\text{demand\_features}}$ must increase monotonically.
3. **Recommendation-Attribution Concordance:**  
   Verify that an operational mitigation (e.g., "Expedite freight shipping") is triggered *if and only if* the SHAP value for logistics lead time exceeds the 75th percentile of risk-inducing features.

---

## 5. Experiment D: Parametric Sensitivity Analysis (Stress Testing)

### 5.1 Scientific Objective
To directly test **Hypothesis $H_4$** (Decision Invariance Window): determine how sensitive strategic recommendations and profit calculations are to uncertainty in cross-domain coupling parameters (`ASM-001` through `ASM-008`).

### 5.2 Perturbation Space (One-At-A-Time & Morris Screening)

| Parameter ID | Parameter Name | Baseline Value | Test Range (Low, High) | Perturbation Steps |
|---|---|---|---|---|
| **ASM-001** | Late Delivery Penalty ($C_{\text{delay\_penalty}}$) | $\$25.00$ | $[\$10.00, \$60.00]$ | 6 steps |
| **ASM-002** | Expedited Shipping Fee ($C_{\text{expedite\_fee}}$) | $\$15.00$ | $[\$5.00, \$35.00]$ | 6 steps |
| **ASM-003** | Order Cancellation Elasticity ($\kappa_{\text{stockout}}$) | $0.15$ | $[0.05, 0.40]$ | 8 steps |
| **ASM-004** | Attrition Replacement Cost ($C_{\text{replacement}}$) | $\$30,000$ | $[\$15,000, \$60,000]$ | 6 steps |
| **ASM-005** | Overtime Wage Rate ($R_{\text{overtime}}$) | $\$45.00/\text{hr}$ | $[\$30.00, \$75.00]$ | 6 steps |
| **ASM-006** | Stress Decrement ($\Delta \text{WLB}$) | $-1$ | $[0, -2]$ | Discrete $\{0, -1, -2\}$ |

### 5.3 Dependent Evaluation Metrics
1. **Elasticity of Net Profit:**  
   $$\epsilon_P(\theta) = \frac{\% \Delta \text{Profit}}{\% \Delta \theta}$$
   Identifies which operational assumptions dominate financial outcomes.
2. **Recommendation Flip Threshold ($\theta_{\text{flip}}$):**  
   The critical value of parameter $\theta$ at which the primary recommendation flips (e.g., from "Maintain standard shipping" to "Trigger expedited air freight").
3. **Recommendation Stability Index (RSI):**  
   Percentage of the parameter uncertainty space $[\theta_{\min}, \theta_{\max}]$ over which the recommended action remains invariant. Target: $\text{RSI} \ge 70\%$.

### 5.4 Visualization & Deliverables
- **Tornado Diagrams:** Ranking parameters from highest to lowest influence on Net Profit Delta.
- **Sensitivity Heatmaps:** Mapping recommendation boundaries across 2D parameter slices (e.g., $C_{\text{delay\_penalty}}$ vs. $\kappa_{\text{stockout}}$).

---

## 6. Systematic Component Ablation Study

To evaluate the exact contribution of each architectural layer, DecisionSphere is subjected to a 5-stage progressive component ablation:

| Model ID | Configuration Name | Demand Model | Supply Chain Model | Workforce Model | Business Impact Formulas | SHAP / Rec Engine | Evaluated Capability |
|---|---|---|---|---|---|---|---|
| **M0** | *Siloed Demand Baseline* | XGBoost | Excluded | Excluded | Excluded | Excluded | Pure sales volume forecasting (Standard practice) |
| **M1** | *Demand + Logistics* | XGBoost | DataCo Classifier | Excluded | Delay penalty only | Excluded | Evaluates fulfillment bottlenecks; ignores labor constraints |
| **M2** | *Demand + Workforce* | XGBoost | Excluded | IBM HR Classifier | Overtime cost only | Excluded | Evaluates labor strain; ignores logistics delays |
| **M3** | *Integrated Unweighted* | XGBoost | DataCo Classifier | IBM HR Classifier | Basic linear sum | Heuristic rules | Basic cross-functional coupling without calibrated BIA |
| **M4** | *Full DecisionSphere* | XGBoost | DataCo Classifier | IBM HR Classifier | Calibrated BIA Formulas | TreeSHAP + Grounded Recs | Full scenario-driven cross-functional decision intelligence |

### Ablation Evaluation Metric: Information Blindness Score (IBS)
Measures the percentage of downstream operational and financial risk variance that remains uncaptured by the configuration relative to the full system (M4).
