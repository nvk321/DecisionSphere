# DecisionSphere — Business Impact Analysis (BIA)

## 1. Overview
The **Business Impact Analysis (BIA)** module combines the outputs of the analytical modules into transparent, understandable, and quantifiable business-level consequences. 

**Critical Rule:** Business Impact Analysis does **not** rely on opaque machine learning models. It uses deterministic, traceable mathematical formulas and clearly documented business parameters. Every dollar figure and percentage risk score must be completely auditable.

---

## 2. Traceable Mathematical Formulas

### 2.1 Projected Gross Revenue
$$\text{Revenue}_{\text{sim}} = \sum_{t=1}^{H} \hat{y}_{\text{sim}}(t) \times \bar{P} \times (1 - L_{\text{fulfillment}})$$
Where:
- $\hat{y}_{\text{sim}}(t)$: Simulated product volume forecasted on day $t$.
- $\bar{P}$: Average unit selling price (from dataset / benchmark constants).
- $L_{\text{fulfillment}}$: Unfulfilled demand rate due to supply chain disruption:
  $$L_{\text{fulfillment}} = \max(0.0, P(\text{Late Delivery}) \times \kappa_{\text{stockout}})$$
  where $\kappa_{\text{stockout}}$ is the cancellation factor for late orders (default: $0.15$).

### 2.2 Operational Supply Chain Disruption Cost
$$\text{Cost}_{\text{supply\_chain}} = (\text{Delayed Orders}) \times C_{\text{delay\_penalty}} + (\text{Expedited Orders}) \times C_{\text{expedite\_fee}}$$
Where:
- $\text{Delayed Orders} = N_{\text{orders}} \times P(\text{Late Delivery})$.
- $C_{\text{delay\_penalty}}$: Standard contractual penalty per delayed shipment (default: $\$25.00$).
- $C_{\text{expedite\_fee}}$: Surcharge applied if expedited shipping mode is toggled (default: $\$15.00$ per unit).

### 2.3 Workforce Overtime & Attrition Replacement Cost
$$\text{Cost}_{\text{workforce}} = N_{\text{attrition\_cases}} \times C_{\text{replacement}} + N_{\text{overtime\_hours}} \times R_{\text{overtime}}$$
Where:
- $N_{\text{attrition\_cases}} = N_{\text{headcount}} \times P(\text{Attrition})$.
- $C_{\text{replacement}}$: Cost to re-hire and onboard an employee (industry standard: $50\%$ of annualized median salary $\approx \$30,000$).
- $R_{\text{overtime}}$: Premium rate per overtime hour incurred during simulated demand spikes.

### 2.4 Net Incremental Business Margin
$$\Delta \text{Profit} = (\text{Revenue}_{\text{sim}} - \text{Revenue}_{\text{base}}) - (\Delta \text{COGS} + \Delta \text{Cost}_{\text{supply\_chain}} + \Delta \text{Cost}_{\text{workforce}})$$

---

## 3. Composite Organizational Risk Index
To summarize multi-domain risk for executive dashboards, DecisionSphere calculates a normalized **Composite Risk Score (CRS)** $\in [0, 100]$:
$$\text{CRS} = w_1 \cdot \text{Risk}_{\text{Demand\_Volatility}} + w_2 \cdot P(\text{Late Delivery}) \times 100 + w_3 \cdot P(\text{Attrition}) \times 100$$
Default weights: $w_1 = 0.25$, $w_2 = 0.45$, $w_3 = 0.30$ (sum to $1.0$).

---

## 4. Documentation of Assumptions
Any operational parameter not present in public benchmark datasets (such as specific SLA penalty clauses or onboarding costs) is treated as a **Parametric Assumption** and logged transparently in `docs/assumptions-and-open-questions.md`. Users can configure these cost parameters through the application settings.
