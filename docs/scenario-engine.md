# DecisionSphere — Scenario Engine Architecture & Parameter Propagation

## 1. Role of the Scenario Engine
The **Scenario Engine** is the core integration module of DecisionSphere. It translates user-defined hypothetical interventions into structured feature adjustments across individual analytical modules, orchestrates model inferences, and preserves the boundary between observed historical facts, hypothetical assumptions, and computed business outcomes.

---

## 2. Parameter Mapping & Cross-Domain Propagation

When a user defines a scenario (e.g., *"Promotional Demand Surge of +30% with a 5-day Shipping Delay"*), the Scenario Engine executes deterministic parameter translations:

```
                  User Scenario Inputs
                            │
                            ▼
                  Scenario Engine (src/scenario/)
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
[Demand Translation] [Supply Chain Trans.] [HR Translation]
 - Apply promo flag   - Shift scheduled days - Increase overtime
 - Scale order vol.   - Constrain mode       - Scale churn shock
         │                  │                  │
         ▼                  ▼                  ▼
   Demand Model        Supply Model         HR Model
```

### 2.1 Demand Parameter Mapping
- **Input Lever:** `growth_percentage` ($\Delta D$), `promotion_active` (boolean).
- **Transformation:**
  - Sets promotion feature flag $x_{\text{promo}} = 1$.
  - Scales incoming forecast baseline:
    $$\hat{y}_{\text{sim}}(t) = \hat{y}_{\text{base}}(t) \times \left(1 + \frac{\Delta D}{100}\right)$$

### 2.2 Supply Chain Parameter Mapping
- **Input Lever:** `delay_offset_days` ($\Delta S$), `shipping_mode` selection.
- **Transformation:**
  - Adjusts scheduling feature vector:
    $$x_{\text{scheduled\_days}} = x_{\text{scheduled\_days}} - \Delta S$$
    *(Reflecting compressed delivery windows or extended supplier lead times)*.
  - Re-evaluates order volume scaling from demand module to calculate delivery delay probability under heightened warehouse load.

### 2.3 Workforce / HR Parameter Mapping
- **Input Lever:** `overtime_workforce_pct` ($\Delta O$), `attrition_rate_shock`.
- **Transformation:**
  - Increases the proportion of employees with $x_{\text{OverTime}} = 1$.
  - Models satisfaction degradation: for departments experiencing extreme volume surges, satisfaction scores are heuristically decremented:
    $$x_{\text{WorkLifeBalance}} = \max(1, x_{\text{WorkLifeBalance}} - 1)$$
  - Evaluates updated attrition risk scores across the workforce sample.

---

## 3. Preservation of Epistemic Boundaries
The Scenario Engine enforces a strict 4-tier data demarcation:
1. **Tier 1 — Observed Data:** Historical data records stored in benchmark datasets.
2. **Tier 2 — Model Predictions:** Statistical/ML model inferences conditioned on input feature vectors.
3. **Tier 3 — Scenario Assumptions:** User-specified hypothetical levers and documented operational constants.
4. **Tier 4 — Business Impact Inferences:** Deterministic calculations derived by combining Tier 1, 2, and 3.

*Rule: Under no circumstances may Tier 3 (assumptions) or Tier 4 (business calculations) be disguised as Tier 1 ground-truth data.*
