# DecisionSphere — Scenario Engine Architecture & Parameter Propagation

**Status:** COMPLETED — FROZEN  
**Phase:** Phase 6: Scenario Engine & Cross-Domain Parameter Propagation  
**Handoff Target:** Phase 7: Business Impact Analysis Engine (`src/business/`)  

---

## 1. Role of the Scenario Engine
The **Scenario Engine** (`src/scenario/`) is the core cross-domain integration module of DecisionSphere. It translates user-defined hypothetical interventions into structured feature adjustments across individual analytical modules, orchestrates independent model inferences, and strictly preserves the boundary between observed historical facts, hypothetical assumptions, and computed business outcomes.

### Architectural Invariants & Governance (Frozen Status):
- **ScenarioEngine is FROZEN:** Source implementation in `src/scenario/engine.py` and `src/scenario/schema.py` is completed and regression-locked.
- **ScenarioSweepEngine is FROZEN:** Discrete parameter sweep functionality in `src/scenario/sweep.py` is completed and regression-locked.
- **Zero Financial Accounting:** Phase 6 contains zero dollar values, revenue figures, penalties, or cost computations.
- **Strict Assumption Segregation:**
  - **Phase 6 Operational Assumptions:** Consumes strictly `ASM-006` ($\Delta \text{WLB} = -1$), `ASM-007` ($\gamma_{\text{volume}} = 1.0$), and `ASM-008` ($\tau_{\text{cycle}} = 30\text{ days}$).
  - **Phase 7 Financial Assumptions:** Rejects `ASM-001` through `ASM-005` via strict Pydantic validation (`extra="forbid"`).
- **Formal Handoff Interface:** Phase 6 produces the immutable, strongly typed `ScenarioRunResult`. Phase 7 is strictly a downstream consumer of `ScenarioRunResult` and must never alter Phase 6 behavior or reload predictive models.

---

## 2. Parameter Mapping & Non-Causal Execution Architecture

In accordance with Section 13.2 of `AGENTS.md`, the Scenario Engine does not execute a causal cascade (`Demand → Logistics → Workforce`). Instead, it executes independent parallel inferences conditioned on declared operational translations:

```
                  User Scenario Inputs (Levers)
                             │
                             ▼
             Scenario Engine (src/scenario/engine.py)
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
[Demand Translation]   [Supply Translation]  [HR Translation]
 - Promo active flag    - Scheduled days adj. - Deterministic overtime
 - Sales scaling (%)    - Mode override       - WLB decrement (ASM-006)
        │                    │                    │
        ▼                    ▼                    ▼
   Demand Model        Supply Model           HR Model
(Rossmann - Frozen)   (DataCo - Frozen)   (IBM HR - Frozen)
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                             ▼
              Deterministic Aggregation & Provenance
                             │
                             ▼
               ScenarioRunResult (Immutable)
                             │
                             ▼ [Formal Handoff]
         Phase 7: Business Impact Analysis Engine (src/business/)
```

### 2.1 Demand Parameter Mapping
- **Input Levers:** `growth_percentage` ($\Delta D$), `promotion_active` (boolean).
- **Operational Transformation:**
  - Sets promotion feature flag $x_{\text{promo}} = 1$.
  - Scales incoming forecast baseline:
    $$\hat{y}_{\text{sim}}(t) = \hat{y}_{\text{base}}(t) \times \left(1 + \frac{\Delta D}{100}\right)$$

### 2.2 Supply Chain Parameter Mapping
- **Input Levers:** `delay_offset_days` ($\Delta S$), `shipping_mode_override`.
- **Operational Transformation:**
  - Adjusts scheduling feature vector:
    $$x_{\text{scheduled\_days}} = x_{\text{scheduled\_days}} - \Delta S$$
  - Applies discrete volume normalization via `ASM-007` and `ASM-008`:
    $$\bar{y}_{\text{daily}} = \frac{\sum_{t=1}^H \hat{y}_{\text{sim}}(t)}{H}, \quad Y_{\text{cycle}} = \bar{y}_{\text{daily}} \times \tau_{\text{cycle}}, \quad N_{\text{orders}} = Y_{\text{cycle}} \times \gamma_{\text{volume}}$$
  - Evaluates conditional delivery delay risk under scenario order volume.

### 2.3 Workforce / HR Parameter Mapping
- **Input Levers:** `overtime_workforce_pct` ($\Delta O$), `salary_hike_override`.
- **Operational Transformation:**
  - Deterministic index sorting assigns overtime strictly to target headcount proportions without disturbing baseline 'Yes' records.
  - Applies heuristic WorkLifeBalance decrement (`ASM-006`):
    $$x_{\text{WorkLifeBalance}} = \max(1, \min(4, x_{\text{WorkLifeBalance}} - 1)) \quad \text{for overtime employees}$$
  - Evaluates updated conditional attrition probabilities across the workforce cohort.

---

## 3. Preservation of Epistemic Boundaries
In accordance with Section 13.3 of `AGENTS.md` and the DecisionSphere research mandate, the Scenario Engine enforces the strict **6-tier Epistemic Hierarchy**:
1. **Tier 1 — OBSERVED:** Measured historical ground truth from benchmark datasets.
2. **Tier 2 — PREDICTED:** Statistical machine learning inferences conditioned on input feature vectors.
3. **Tier 3 — ASSUMED:** User-specified scenario shock parameters and baseline operational constants (`ASM-006`, `ASM-007`, `ASM-008`).
4. **Tier 4 — PROPAGATED:** Algorithmic downstream translations across operational domains (e.g., volume normalization, overtime cohort assignment).
5. **Tier 5 — CALCULATED:** Deterministic mathematical accounting equations for financial and risk metrics (Phase 7).
6. **Tier 6 — RECOMMENDED:** Explicit rule-grounded strategic actions synthesized from risk triggers (Phase 8).

*Rule: Under no circumstances may Tier 3 (assumptions), Tier 4 (propagations), or Tier 5 (calculations) be represented as empirical facts or causal interventions.*
