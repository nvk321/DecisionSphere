# DecisionSphere — Phase 6 Scenario Engine Pre-Implementation Audit Report
## Cross-Domain Parameter Propagation, Epistemic Boundaries & Governance

**Status:** APPROVED WITH CLARIFICATIONS (RESOLVED PRE-IMPLEMENTATION)  
**Date:** September 5, 2026  
**Document Type:** Formal System Architecture, Epistemic Demarcation & Assumptions Audit  
**Governing Core Principle:**  
*"The Scenario Engine computes consequences under explicitly declared assumptions; it does not manufacture causal relationships that were not identified by the empirical models."*

---

## 1. Executive Summary & Phase 5 Status Clarification

In accordance with the **Phase 4 Approval + Phase 6 Pre-Implementation Audit Directive** and subsequent **Phase 6 Review Comments**, this document provides the finalized, comprehensive architecture audit for **Phase 6: Scenario Engine (`src/scenario/`)**.

### Formal Phase 5 Status Statement
> "Phase 5 is not currently represented as an independent implementation phase in the frozen project architecture. No Phase 5 predictive artifact, model, or mandatory implementation dependency is assumed by Phase 6. Phase 6 therefore proceeds as the next approved implementation stage following the completion and freezing of the applicable predictive modules."

Domain-specific Explainable AI (TreeSHAP feature attributions and stability analyses) was integrated and serialized directly within the respective predictive phases:
- Phase 2 Demand: `models/demand/feature_importance.json`
- Phase 3 Supply Chain: `models/supply_chain/feature_importance.json`
- Phase 4 Workforce: `models/workforce/feature_importance.json`

Phase 3 (Supply Chain Delivery Risk) and Phase 4 (Workforce Attrition Risk) are **COMPLETED AND FROZEN**. The Scenario Engine operates strictly as an external, non-mutating orchestrator.

---

## 2. Section A: Current Scenario Architecture

In the existing codebase:
- **Phase 2 Demand Pipeline:** Provides recursive multi-step forecasting with promotional campaign overrides (`promo_schedule`, `promo_override_flag`) in `src/models/demand/inference.py`.
- **Phase 3 Supply Chain Pipeline:** Provides single-order and batch delivery risk scoring with `shipping_mode_override` and `scheduled_days_offset` in `src/models/supply_chain/inference.py`.
- **Phase 4 Workforce Pipeline:** Provides single-employee and batch attrition risk scoring with `overtime_override` and `salary_hike_override` in `src/models/workforce/inference.py`.
- **Current State of `src/scenario/`:** The directory does not exist yet. No code has been written. All three domain models currently operate as independent, frozen components.

---

## 3. Section B: Authoritative ASM Registry Location & Phase Boundaries

The permanent source of truth for operational coupling assumptions is:
**`docs/assumptions-and-open-questions.md` (Table 1: The Parametric Registry)**.

### Strict Phase Segregation
To prevent architectural contamination and ensure callers cannot accidentally pass financial assumptions into the scenario engine, assumptions are strictly segregated into phase-specific contracts:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             USER CONFIGURATION                              │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
       ┌───────────────────────────────┴───────────────────────────────┐
       ▼                                                               ▼
┌──────────────────────────────────────────────┐ ┌──────────────────────────────────────────────┐
│  Phase 6: ScenarioAssumptions (Operational)  │ │   Phase 7: BusinessAssumptions (Financial)   │
├──────────────────────────────────────────────┤ ├──────────────────────────────────────────────┤
│ • ASM-006: ΔWLB decrement = -1 {-2, -1, 0}   │ │ • ASM-001: Late penalty = $25.00 [$10, $60]  │
│ • ASM-007: Volume scaling γ = 1.0 [0.5, 2.0] │ │ • ASM-002: Expedite fee = $15.00 [$5, $35]   │
│ • ASM-008: Cycle length τ = 30d [14, 90d]    │ │ • ASM-003: Cancellation churn = 0.15 [0.05,.4]│
│                                              │ │ • ASM-004: Replacement = $30,000 [$15k, $60k]│
│ (Strictly non-financial operational factors) │ │ • ASM-005: Overtime wage = $45/hr [$30, $75] │
└──────────────────────────────────────────────┘ └──────────────────────────────────────────────┘
```

Phase 6 schemas accept **ONLY ASM-006, ASM-007, and ASM-008**. Passing `ASM-001` through `ASM-005` into Phase 6 is prohibited and rejected by validation.

---

## 4. Section C: Exact Cross-Domain Coupling Functions & Dimensional Integrity

Every cross-domain translation in Phase 6 is governed by one of four explicit categories:
1. User-specified scenario lever
2. Declared ASM parameter
3. Explicit deterministic mathematical formula
4. Independent model inference

### 4.1 Demand Normalization & Temporal Synchronization (`ASM-008`)
- **Input:** Baseline forecast $\hat{y}_{\text{base}}(t)$ and scenario forecast $\hat{y}_{\text{sim}}(t)$ over horizon $H$ days (Sales units).
- **Transformation:**
  $$\bar{y}_{\text{daily}} = \frac{1}{H} \sum_{t=1}^H \hat{y}(t) \quad [\text{Sales units / day}]$$
  $$\text{Normalized Volume } Y_{\text{cycle}} = \bar{y}_{\text{daily}} \times \tau_{\text{cycle}} \quad [\text{Sales units / cycle}]$$
- **Parameter:** `ASM-008` ($\tau_{\text{cycle}} = 30\text{ days}$, range: $[14, 90\text{ days}]$, unit: days).
- **Units:** $\frac{\text{Sales units}}{\text{day}} \times \text{days} = \text{Sales units / cycle}$.

### 4.2 Order Volume Scaling Bridge (`ASM-007`)
- **Language:**
  *"ASM-007 provides a synthetic normalization bridge between the demand model's predicted retail volume and the scenario engine's operational order-volume representation. It is not an empirically learned sales-to-order conversion coefficient."*
- **Transformation:**
  $$N_{\text{orders}} = Y_{\text{cycle}} \times \gamma_{\text{volume}} \quad [\text{orders / cycle}]$$
- **Parameter:** `ASM-007` ($\gamma_{\text{volume}} = 1.0$, range: $[0.5, 2.0]$, unit: dimensionless order-to-sales scaling factor, orders / sales unit).

### 4.3 Supply Chain SLA Shift & Shipping Mode Override
- **Input Levers:**
  - `scheduled_days_offset` ($\Delta S \in [-3, +3]$, unit: days).
  - `shipping_mode_override` ($\in \{\text{'Standard Class'}, \text{'Second Class'}, \text{'First Class'}, \text{'Same Day'}, \text{None}\}$).
- **Transformation:** Applied to isolated copies of the order cohort:
  $$x_{\text{scheduled\_days, scen}} = \max(0, x_{\text{scheduled\_days, base}} + \Delta S)$$
  If `shipping_mode_override` is specified:
  $$x_{\text{shipping\_mode, scen}} = \text{shipping\_mode\_override}$$
- **Inference:** Frozen DataCo Calibrated XGBoost evaluates $P(\text{Late} = 1 \mid \mathbf{x}_{\text{order, scen}})$.

### 4.4 Workforce Population & Deterministic Overtime Assignment ($\Delta O$ and `ASM-006`)
- **Workforce Population Contract:** Evaluated on a declared cohort (defaulting to the 221-employee test holdout or full 1,470-employee benchmark).
- **Input Lever:** `overtime_workforce_pct` ($L \in [0.0, 100.0]$, unit: percentage, target mandated overtime rate).
- **Deterministic Assignment Mapping:**
  1. Let $N$ be total cohort size. Target overtime headcount is $K_{\text{target}} = \lceil N \times (L / 100) \rceil$.
  2. Baseline overtime headcount is $K_{\text{base}} = \sum_{i=1}^N \mathbb{I}(\text{OverTime}_i = \text{'Yes'})$.
  3. If $K_{\text{target}} > K_{\text{base}}$, exactly $K_{\text{target}} - K_{\text{base}}$ employees currently at `OverTime == 'No'` are switched to `OverTime = 'Yes'` in deterministic order (sorted stably by `EmployeeNumber` / index).
  4. If $K_{\text{target}} \le K_{\text{base}}$, existing baseline overtime assignments remain intact (no random stripping).
- **Heuristic WorkLifeBalance Decrement (`ASM-006`):**
  For every employee assigned `OverTime = 'Yes'` under the scenario, their `WorkLifeBalance` survey score is decremented:
  $$x_{\text{WLB, scen}} = \max(1, \min(4, x_{\text{WLB, base}} + \Delta \text{WLB}))$$
  where `ASM-006` defaults to $\Delta \text{WLB} = -1$ (sensitivity range: $\{0, -1, -2\}$).
- **Cohort Risk Aggregation:**
  $$\bar{P}_{\text{att, scen}} = \frac{1}{N} \sum_{i=1}^N \hat{P}_i(\text{Attrition} = 1 \mid \mathbf{x}_{i, \text{scen}})$$
  $$\Delta \bar{P}_{\text{att}} = \bar{P}_{\text{att, scen}} - \bar{P}_{\text{att, base}} \quad [\text{unrounded IEEE 754 float}]$$

### 4.5 Salary Hike Override Semantics
- **Input Lever:** `salary_hike_override` (Optional float $\in [0.0, 35.0\%]$).
- **Transformation:** In accordance with Phase 4's implementation in `src/models/workforce/inference.py` (line 176), modifies feature `PercentSalaryHike` on the scenario copy:
  $$x_{\text{PercentSalaryHike, scen}} = \text{salary\_hike\_override}$$
  If `None`, original employee compensation hikes remain untouched.

---

## 5. Section D: Hard-Bounded Epistemic Dependency Graph

To eliminate any visual or conceptual misinterpretation of cross-domain causality, the execution graph enforces a hard epistemic decoupling:

```
                            USER SCENARIO
  [demand_growth_pct, promo_active, scheduled_days_offset, overtime_workforce_pct]
                                  │
                                  ▼
                   ASSUMED OPERATIONAL TRANSLATIONS
     ┌────────────────────────────┼────────────────────────────┐
     ▼                            ▼                            ▼
[Demand Translation]     [Supply Translation]         [Workforce Translation]
Promo schedule override  Lead time shift (ΔS)         Target overtime % (L)
Scaling factor (ASM-008) Mode override (if set)       Deterministic assignment
Order scaling (ASM-007)                               WLB decrement (ASM-006)
     │                            │                            │
     ▼                            ▼                            ▼
┌──────────────────┐     ┌──────────────────┐         ┌──────────────────┐
│  Demand Domain   │     │   Supply Chain   │         │    Workforce     │
│  (Frozen Model)  │     │  (Frozen Model)  │         │  (Frozen Model)  │
├──────────────────┤     ├──────────────────┤         ├──────────────────┤
│ Independent Pred │     │ Independent Pred │         │ Independent Pred │
│ y_base vs y_scen │     │ P(Late)_base vs  │         │ P(Att)_base vs   │
│                  │     │ P(Late)_scen     │         │ P(Att)_scen      │
└────────┬─────────┘     └────────┬─────────┘         └────────┬─────────┘
         │                        │                            │
         └────────────────────────┼────────────────────────────┘
                                  │
                                  ▼
                DETERMINISTIC AGGREGATION / PROPAGATION
           - Exact unrounded probability deltas (ΔP)
           - Per-field cryptographic provenance metadata
           - Zero financial calculations (No dollars / revenue / cost)
                                  │
                                  ▼ (Strict hand-off boundary)
                  Phase 7: Business Impact Analysis
                  [ASM-001, ASM-002, ASM-003, ASM-004, ASM-005]
```

*Rule: The Scenario Engine does NOT infer cross-domain causality (e.g., high demand does not cause late delivery; late delivery does not cause attrition). The models are independent predictors evaluating distinct feature spaces under declared operational assumptions.*

---

## 6. Section E: Per-Field Epistemic Provenance Architecture

Rather than relying on unvalidated, generic dictionaries, Phase 6 defines structured Pydantic models with explicit per-field provenance tracking:

```python
class DomainProvenance(BaseModel):
    source_model: str = Field(..., description="Name of the predictive module")
    model_artifact: str = Field(..., description="Path to serialized joblib artifact")
    artifact_sha256: str = Field(..., description="Cryptographic fingerprint of model file")
    epistemic_tier: str = Field(..., description="6-tier epistemic classification")
    input_modifications: Dict[str, Any] = Field(default_factory=dict)
    assumptions_applied: List[str] = Field(default_factory=list)
    causal_claim: bool = Field(False, description="Strictly False: non-causal association")
    calculation_description: str = Field(..., description="Explicit mathematical basis")

class DomainPredictionResult(BaseModel):
    domain: str
    unit: str
    baseline_value: float = Field(..., description="Unrounded IEEE 754 baseline prediction")
    scenario_value: float = Field(..., description="Unrounded IEEE 754 scenario prediction")
    delta_value: float = Field(..., description="scenario_value - baseline_value")
    decision_threshold: Optional[float] = None
    baseline_class: Optional[int] = None
    scenario_class: Optional[int] = None
    provenance: DomainProvenance
```

---

## 7. Section F: Reproducibility & Immutability Contracts

1. **Deterministic Scenario ID:**
   `scenario_id` is either caller-specified or deterministically generated via SHA-256 digest of canonicalized JSON levers + assumptions:
   $$\text{scenario\_id} = \text{SHA256}(\text{canonical\_json})[:12]$$
2. **Execution Timestamp Exclusion:**
   `execution_timestamp` is logged for audit trails, but is strictly excluded from scenario computation, hashing, and equality assertions.
3. **Artifact Integrity Fingerprinting:**
   At Scenario Engine instantiation, SHA-256 hashes of all three serialized models (`models/demand/demand_model.joblib`, `models/supply_chain/supply_chain_model.joblib`, `models/workforce/workforce_model.joblib`) are computed and stored. An automated integrity check ensures byte hashes remain invariant throughout execution.
4. **Data Immutability:**
   All scenario feature mutations operate on deep copies (`df.copy(deep=True)`). Original benchmark data and loaded model structures are strictly invariant.

---

## 8. Section G: Threshold Semantics vs Continuous Probabilities

- In accordance with Phase 3 ($\tau^* = 0.17$) and Phase 4 ($\tau^* = 0.21$), the decision threshold $\tau^*$ is an operational classification boundary, **NOT a probability transformation**.
- All risk reporting and downstream deltas preserve the continuous, calibrated probability:
  $$\Delta P = P_{\text{scenario}} - P_{\text{baseline}}$$
- When binary class states shift, the output statement uses explicit non-causal language:
  *"Classification changed from below threshold to above threshold at $\tau^* = 0.21$"* (never *"employee became high risk"*).

---

## 9. Section H: Sensitivity Sweep Semantics (`sweep.py`)

- `ScenarioSweepEngine` performs deterministic grid evaluation across discrete points within the audited ranges:
  - `ASM-006` $\in \{0, -1, -2\}$
  - `ASM-007` $\in \{0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0\}$
  - `ASM-008` $\in \{14, 21, 30, 45, 60, 90\}$
- Sweeps evaluate declared parameter values deterministically. They **do not assign unsupported probability distributions** (e.g., uniform or Gaussian priors).
- Sweeps **never retrain, refit, or recalibrate models**.

---

## 10. Section I: Acceptance Criteria Verification & Test Matrix

The Phase 6 test suite (`tests/test_scenario_engine.py`) covers all required acceptance points:

| # | Test Name | Purpose / Assertion |
|---|---|---|
| 1 | `test_asm_registry_completeness` | Verifies `ASM-006`, `ASM-007`, `ASM-008` are present with correct metadata. |
| 2 | `test_asm_baseline_value_integrity` | Verifies baselines match Table 1 exactly (-1, 1.0, 30). |
| 3 | `test_asm_sensitivity_bounds_integrity` | Verifies sensitivity ranges match Table 1 bounds. |
| 4 | `test_frozen_model_artifact_integrity` | Verifies SHA-256 byte hashes of all 3 models are unchanged before/after inference. |
| 5 | `test_reproducibility_contract` | Identical inputs produce bitwise-identical numerical results; timestamp does not affect computation. |
| 6 | `test_baseline_scenario_invariance` | Zero shock ($\Delta D=0, \Delta S=0, \Delta O=0$) produces exact delta = 0.0. |
| 7 | `test_no_financial_values_in_phase6` | Asserts no dollar signs, revenue, cost, or profit fields exist in Phase 6 output schemas. |
| 8 | `test_phase6_phase7_assumption_segregation`| Asserts passing `ASM-001` to `ASM-005` to Phase 6 raises `ValidationError`. |
| 9 | `test_cross_domain_isolation` | Changing `ASM-006` does not alter Demand or Supply Chain outputs. |
| 10 | `test_deterministic_overtime_assignment` | Target % mandates exact headcount via stable sorting; preserves baseline 'Yes' cases. |
| 11 | `test_asm006_wlb_clamping` | $x_{\text{WLB}}$ scores are decremented by $\Delta \text{WLB}$ and strictly clamped in $[1, 4]$. |
| 12 | `test_asm007_asm008_volume_normalization` | Verifies dimensional calculation $\frac{\text{Sales}}{H} \times \tau_{\text{cycle}} \times \gamma_{\text{volume}}$. |
| 13 | `test_exact_unrounded_delta_precision` | Confirms $\Delta P$ is calculated using native 64-bit float subtraction before formatting. |
| 14 | `test_per_field_epistemic_provenance` | Confirms every domain result contains structured `DomainProvenance` with non-causal flags. |
| 15 | `test_threshold_semantics_preservation` | Confirms continuous probabilities are preserved alongside binary classifications. |
| 16 | `test_invalid_parameter_rejection` | Out-of-bounds levers (e.g. demand shock > 100% or offset > 3) raise `ValidationError`. |
| 17 | `test_shipping_mode_override_semantics` | Setting valid shipping mode modifies `shipping_mode` feature; invalid modes rejected. |
| 18 | `test_salary_hike_override_semantics` | Setting salary hike modifies `PercentSalaryHike` feature; out-of-range values rejected. |
| 19 | `test_raw_data_immutability` | Baseline DataFrames pass `assert_frame_equal` before and after scenario runs. |
| 20 | `test_sensitivity_sweep_deterministic_execution` | Sweep evaluates grid points without model mutation or retraining. |

---

## 11. Section K: Implementation Plan & File Boundary

Implementation will strictly write:
1. `src/scenario/__init__.py`
2. `src/scenario/schema.py`: Pydantic v2 contracts (`ScenarioLevers`, `ScenarioAssumptions`, `DomainProvenance`, `DomainPredictionResult`, `ScenarioRunResult`).
3. `src/scenario/assumptions.py`: Code-level `AssumptionRegistry` for `ASM-001` through `ASM-008` with phase segregation.
4. `src/scenario/engine.py`: `ScenarioEngine` orchestrating independent domain runs, cryptographic artifact hashing, deterministic overtime mapping, and unrounded delta tracking.
5. `src/scenario/sweep.py`: `ScenarioSweepEngine` for discrete parameter sensitivity sweeps.
6. `tests/test_scenario_engine.py`: Full 20-point test suite.

**Status:** ALL ACCEPTANCE CRITERIA RESOLVED. PROCEEDING WITH PHASE 6 IMPLEMENTATION.
