# DecisionSphere — Phase 7 Business Impact Analysis Pre-Implementation Audit Report
## Deterministic Financial Modeling, Epistemic Demarcation & Assumptions Governance

**Status:** PRE-IMPLEMENTATION AUDIT COMPLETED / IMPLEMENTATION NOT YET STARTED  
**Date:** September 5, 2026  
**Document Type:** Formal System Architecture, Financial Accounting & Epistemic Audit  
**Governing Core Principle:**  
*"Business Impact Analysis converts scenario-derived model outputs into transparent financial calculations under explicitly declared assumptions; it does not convert statistical predictions into claims about guaranteed real-world outcomes."*

---

## 1. Executive Summary

In accordance with the **Phase 6 Approval Directive**, Phase 6 (Scenario Engine & Cross-Domain Parameter Propagation) is **COMPLETED AND FROZEN**. 

This document performs an exhaustive pre-implementation audit for **Phase 7: Business Impact Analysis Engine (`src/business/`)** before any source code is written.

Phase 7 sits strictly downstream of the Scenario Engine. It consumes `ScenarioRunResult` and applies deterministic, transparent mathematical accounting equations—parameterized by `ASM-001` through `ASM-005`—to calculate scenario-based financial impacts ($\Delta \text{Revenue}$, $\Delta \text{Cost}$, $\Delta \text{Profit}$) and multi-domain risk indices.

---

## 2. Epistemic Hierarchy & Non-Causal Grounding in Business Impact

In accordance with Section 13.3 of `AGENTS.md` and the DecisionSphere research mandate:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          THE EPISTEMIC CHAIN IN BIA                         │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
                Tier 2: PREDICTED      │ Conditional ML model inferences:
                                       │ - Projected Sales Volume (Rossmann)
                                       │ - Mean Late Delivery Probability P(Late) (DataCo)
                                       │ - Mean Attrition Probability P(Att) (IBM HR)
                                       │
                Tier 3: ASSUMED        │ Explicit financial parameters:
                                       │ - ASM-001: Delay Penalty ($25.00)
                                       │ - ASM-002: Expedited Surcharge ($15.00)
                                       │ - ASM-003: Cancellation Churn (0.15)
                                       │ - ASM-004: Turnover Replacement ($30,000)
                                       │ - ASM-005: Overtime Wage Premium ($45.00/hr)
                                       │
                Tier 4: PROPAGATED     │ Operational bridges:
                                       │ - ASM-007: Volume Scaling Factor (1.0)
                                       │ - ASM-008: Cycle Synchronization (30 days)
                                       │ - Deterministic Overtime Cohort Assignment
                                       │
                Tier 5: CALCULATED     │ Deterministic Financial Accounting:
                                       │ - Realized Gross Revenue
                                       │ - Disruption & Overtime Costs
                                       │ - Net Incremental Profit (ΔProfit)
                                       │ - Composite Risk Score (CRS)
```

### Critical Epistemic Distinctions to Enforce:
1. **Model Probability $\ne$ Realized Future Event:** $\bar{P}(\text{Late})$ and $\bar{P}(\text{Attrition})$ are statistical conditional probabilities, not guarantees that specific orders will be late or specific employees will resign.
2. **Expected Events $\ne$ Counted Realizations:** Quantities such as $N_{\text{orders}} \times \bar{P}(\text{Late})$ are *model-implied expected event counts under the declared scenario*.
3. **Calculated Impact $\ne$ Realized Accounting Outcome:** Dollar figures calculated in Phase 7 are *scenario-derived financial estimates conditioned on explicit assumptions*, not financial statements or forecasted earnings.
4. **Non-Causal Terminology:** Statements must state: *"Under the declared scenario assumptions, the model-implied net profit shift is calculated as..."* (never *"high demand caused a profit reduction"*).

---

## 3. Exact Traceable Financial Formulas

Phase 7 enforces baseline vs scenario vs delta accounting for every financial metric:
$$\Delta M = M_{\text{scen}} - M_{\text{base}} \quad [\text{unrounded IEEE 754 64-bit float}]$$

### 3.1 Gross Revenue, Fulfillment Loss & Realized Revenue Accounting
Due to delivery delays, late shipments risk customer cancellations and stockouts.
- **Sales Quantity vs Monetary Revenue:**
  - $Y_{\text{sales}}$ is the model-projected sales quantity from `demand_result.scenario_value` (unit: `Sales units`).
  - Unit selling price $\bar{P}$ (`unit_price`, default $\$1.00/\text{unit}$, sensitivity range $[\$0.50, \$50.00/\text{unit}]$ in `BusinessAssumptions`):
    $$\text{Gross Revenue} = Y_{\text{sales}} \times \bar{P} \quad (\text{USD / planning cycle})$$
- **Fulfillment Loss Rate:**
  $$L_{\text{fulfillment}} = \min\left(1.0, \bar{P}(\text{Late Delivery}) \times \kappa_{\text{stockout}}\right)$$
  where $\kappa_{\text{stockout}}$ is `ASM-003` ($0.15$ baseline, range $[0.05, 0.40]$, dimensionless churn ratio).
- **Realized Revenue:**
  $$\text{Realized Revenue} = \text{Gross Revenue} \times (1 - L_{\text{fulfillment}}) \quad (\text{USD / planning cycle})$$
- **Revenue Delta:**
  $$\Delta \text{Revenue} = \text{Realized Revenue}_{\text{scen}} - \text{Realized Revenue}_{\text{base}}$$

### 3.2 Operational Cost Accounting
Total operational cost is the deterministic sum of three mutually exclusive components:
$$\text{Cost} = \text{Cost}_{\text{cogs}} + \text{Cost}_{\text{supply\_chain}} + \text{Cost}_{\text{workforce}}$$

#### A. Cost of Goods Sold (COGS) — Option B: Realized Sales
In accordance with standard managerial accounting, cancelled or unfulfilled customer demand does not incur cost of goods sold. COGS is calculated strictly on **realized sales revenue**:
- Governed by declared baseline COGS ratio $c_{\text{cogs}} = 0.60$ (gross margin $40\%$, sensitivity range: $[0.30, 0.90]$ in `BusinessAssumptions`):
  $$\text{Cost}_{\text{cogs}} = \text{Realized Revenue} \times c_{\text{cogs}} \quad (\text{USD / planning cycle})$$
  $$\Delta \text{Cost}_{\text{cogs}} = \text{Cost}_{\text{cogs, scen}} - \text{Cost}_{\text{cogs, base}}$$
- **Gross Contribution Margin:**
  $$\text{Gross Margin} = \text{Realized Revenue} - \text{Cost}_{\text{cogs}} = \text{Realized Revenue} \times (1 - c_{\text{cogs}})$$

#### B. Supply Chain Disruption Cost (Non-Overlapping Delay Penalty & Expedited Freight)
Composed of contractual SLA delay penalties on delivered shipments and optional expedited freight shipping fees:
$$\text{Cost}_{\text{supply\_chain}} = \text{Cost}_{\text{delay\_penalty}} + \text{Cost}_{\text{expedited\_freight}}$$

1. **Contractual Late Delivery Penalty (Delivered-Delayed Orders Only):**
   To prevent double-counting between the revenue loss mechanism ($\kappa_{\text{stockout}}$) and carrier delivery penalties, penalty charges apply **strictly to orders that are delivered late**, not to cancelled orders:
   - Expected delayed orders:
     $$N_{\text{delayed\_expected}} = N_{\text{orders}} \times \bar{P}(\text{Late Delivery})$$
   - Expected cancelled/lost orders (already accounted for in $L_{\text{fulfillment}}$ revenue deduction):
     $$N_{\text{lost\_expected}} = N_{\text{delayed\_expected}} \times \kappa_{\text{stockout}}$$
   - Expected delivered-and-delayed orders:
     $$N_{\text{delivered\_delayed\_expected}} = N_{\text{delayed\_expected}} - N_{\text{lost\_expected}} = N_{\text{orders}} \times \bar{P}(\text{Late Delivery}) \times (1 - \kappa_{\text{stockout}})$$
   - Late delivery contractual penalty:
     $$\text{Cost}_{\text{delay\_penalty}} = N_{\text{delivered\_delayed\_expected}} \times C_{\text{delay\_penalty}}$$
     where $C_{\text{delay\_penalty}}$ is `ASM-001` ($\$25.00$ baseline, range $[\$10.00, \$60.00]$, unit: `USD / delayed order`).
   - Baseline calculation is identical:
     $$N_{\text{delivered\_delayed\_base}} = N_{\text{orders\_base}} \times \bar{P}(\text{Late Delivery})_{\text{base}} \times (1 - \kappa_{\text{stockout}})$$
     $$\text{Cost}_{\text{delay\_penalty\_base}} = N_{\text{delivered\_delayed\_base}} \times C_{\text{delay\_penalty}}$$

2. **Expedited Freight Surcharge ($N_{\text{expedited}}$ Mapping):**
   Deterministic mapping from `ScenarioRunResult.levers.shipping_mode_override`:
   - Categorical groups:
     $$\text{EXPEDITED\_MODES} = \{\text{'First Class'}, \text{'Same Day'}\}$$
     $$\text{REGULAR\_MODES} = \{\text{'Standard Class'}, \text{'Second Class'}\}$$
   - Baseline expedited order fraction: $f_{\text{expedite\_base}} = 0.05$ (historical baseline proportion in DataCo benchmark; configurable in `BusinessAssumptions.baseline_expedited_fraction`).
   - Scenario expedited order count ($N_{\text{expedited, scen}}$):
     - If `shipping_mode_override in EXPEDITED_MODES`: $N_{\text{expedited, scen}} = N_{\text{orders}} \times 1.0$ ($100\%$ expedited).
     - If `shipping_mode_override in REGULAR_MODES`: $N_{\text{expedited, scen}} = 0.0$ ($0\%$ expedited).
     - If `shipping_mode_override is None`: $N_{\text{expedited, scen}} = N_{\text{orders}} \times f_{\text{expedite\_base}}$.
   - Baseline expedited order count ($N_{\text{expedited, base}}$):
     $$N_{\text{expedited, base}} = N_{\text{orders\_base}} \times f_{\text{expedite\_base}}$$
   - Expedited freight surcharge:
     $$\text{Cost}_{\text{expedited\_freight}} = N_{\text{expedited}} \times C_{\text{expedite\_fee}}$$
     where $C_{\text{expedite\_fee}}$ is `ASM-002` ($\$15.00$ baseline, range $[\$5.00, \$35.00]$, unit: `USD / expedited order`).

#### C. Workforce Disruption & Overtime Cost
Composed of turnover re-hiring costs and overtime labor wages:
$$\text{Cost}_{\text{workforce}} = \text{Cost}_{\text{turnover\_replacement}} + \text{Cost}_{\text{overtime\_labor}}$$
- **Turnover Replacement Cost:**
  Model-implied expected employee departures across the cohort:
  $$N_{\text{departures}} = N_{\text{workforce}} \times \bar{P}(\text{Attrition})$$
  $$\text{Cost}_{\text{turnover\_replacement}} = N_{\text{departures}} \times C_{\text{replacement}}$$
  where $C_{\text{replacement}}$ is `ASM-004` ($\$30,000$ baseline, range $[\$15,000, \$60,000]$, unit: `USD / departed employee`).
- **Overtime Hourly Labor Rate:**
  Active overtime headcount: $K_{\text{ot}} = \text{workforce\_cohort\_summary.scenario\_overtime\_count}$ (from Phase 6).
  Overtime hours per worker per planning cycle: $h_{\text{ot}} = 20.0\text{ hours}$ (baseline, sensitivity range: $[5.0, 60.0\text{ hours}]$ in `BusinessAssumptions`).
  $$\text{Total Overtime Hours} = K_{\text{ot}} \times h_{\text{ot}}$$
  $$\text{Cost}_{\text{overtime\_labor}} = \text{Total Overtime Hours} \times R_{\text{overtime}}$$
  where $R_{\text{overtime}}$ is `ASM-005` (**Overtime hourly labor rate**, $\$45.00/\text{hr}$ baseline, range $[\$30.00, \$75.00/\text{hr}]$, unit: `USD / overtime hour`).

### 3.3 Net Incremental Profit ($\Delta \text{Profit}$)
$$\Delta \text{Profit} = \Delta \text{Revenue} - \Delta \text{Cost}$$
$$= \Delta \text{Revenue} - \left(\Delta \text{Cost}_{\text{cogs}} + \Delta \text{Cost}_{\text{supply\_chain}} + \Delta \text{Cost}_{\text{workforce}}\right)$$

### 3.4 Operational Composite Risk Score (CRS) — Deferral to Phase 8
The **Composite Risk Score (CRS)** is an operational multi-criteria priority index rather than a financial dollar accounting line item. To maintain clean architectural boundaries:
- **Phase 7 Boundary:** Strictly confined to deterministic financial accounting ($\Delta \text{Revenue}$, $\Delta \text{COGS}$, $\Delta \text{Cost}_{\text{supply}}$, $\Delta \text{Cost}_{\text{workforce}}$, $\Delta \text{Profit}$, and break-even sensitivities).
- **Phase 8 Boundary:** Evaluates multi-criteria condition triggers, normalizes cross-domain risk probabilities, computes priority ranking indices (including Composite Risk Score), and synthesizes actionable recommendations.

---

## 4. Authoritative Assumptions Registry: Phase 7 Financial Parameters

Phase 7 consumes strictly `ASM-001` through `ASM-005` from Table 1 of `docs/assumptions-and-open-questions.md`:

| ID | Parameter Name | Symbol | Baseline | Sensitivity Range (Exp D) | Dimensional Unit | Justification & Grounding |
|---|---|---|---|---|---|---|
| **ASM-001** | Contractual late-delivery penalty | $C_{\text{delay\_penalty}}$ | **$\$25.00$** | $[\$10.00, \$60.00]$ | `USD / delayed order` | 3PL carrier SLA late delivery contractual charge on delivered goods. |
| **ASM-002** | Expedited freight shipping surcharge | $C_{\text{expedite\_fee}}$ | **$\$15.00$** | $[\$5.00, \$35.00]$ | `USD / expedited order` | Commercial courier air cargo surcharge over ground freight. |
| **ASM-003** | Late-order cancellation factor | $\kappa_{\text{stockout}}$ | **$0.15$ ($15\%$)** | $[0.05, 0.40]$ | `dimensionless churn ratio` | E-commerce industry fulfillment delay churn benchmark. |
| **ASM-004** | Employee replacement / turnover cost | $C_{\text{replacement}}$ | **$\$30,000$** | $[\$15,000, \$60,000]$ | `USD / departed employee` | SHRM benchmark ($50\%$ to $75\%$ of median annual salary). |
| **ASM-005** | Overtime hourly labor rate | $R_{\text{overtime}}$ | **$\$45.00/\text{hr}$** | $[\$30.00, \$75.00/\text{hr}]$ | `USD / overtime hour` | Standard US FLSA $1.5\times$ overtime rate on an annualized $\$60,000$ base wage. |

Operational parameters (`ASM-006`, `ASM-007`, `ASM-008`) remain strictly upstream in Phase 6.

---

## 5. Prevention of Double-Counting Between Domains

Phase 7 prevents double-counting by enforcing strict mathematical boundary separation:
1. **Fulfillment Loss vs Delay Penalty Fee:**
   - Late delivery cancellation factor ($\kappa_{\text{stockout}}$) reduces *realized gross revenue* (lost sales from cancelled orders).
   - Contractual late penalty ($C_{\text{delay\_penalty}}$) applies *strictly to delivered-delayed orders* ($N_{\text{delivered\_delayed}} = N_{\text{delayed}} \times (1 - \kappa_{\text{stockout}})$).
   - Cancelled orders are never double-charged with delivery carrier penalties.
2. **COGS on Realized Revenue:**
   - Cost of Goods Sold is calculated on *realized revenue*, ensuring the business is never charged production costs for orders cancelled prior to fulfillment.
3. **Turnover Replacement vs Overtime Wage:**
   - Overtime wage rate ($R_{\text{overtime}}$) pays for active productive labor hours worked during surge operations.
   - Replacement cost ($C_{\text{replacement}}$) covers administrative onboarding, recruiting, and vacancy drag for departed employees.
   - Separate cost centers with zero overlapping headcount.

---

## 6. Phase 7 Data Contracts (Pydantic v2)

Phase 7 schemas will be implemented in `src/business/schema.py`:

```python
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class BusinessAssumptions(BaseModel):
    """
    Strictly Phase 7 financial coupling parameters.
    Rejects Phase 6 operational parameters and extra fields via extra='forbid'.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    asm_001_delay_penalty: float = Field(25.00, ge=10.00, le=60.00, description="USD / delayed order")
    asm_002_expedite_fee: float = Field(15.00, ge=5.00, le=35.00, description="USD / expedited order")
    asm_003_cancellation_factor: float = Field(0.15, ge=0.05, le=0.40, description="Dimensionless churn ratio")
    asm_004_replacement_cost: float = Field(30000.00, ge=15000.00, le=60000.00, description="USD / departed employee")
    asm_005_overtime_rate: float = Field(45.00, ge=30.00, le=75.00, description="USD / overtime hour")
    cogs_ratio: float = Field(0.60, ge=0.30, le=0.90, description="COGS as a percentage of realized revenue")
    unit_price: float = Field(1.00, ge=0.50, le=50.00, description="Monetary selling price per sales unit (USD/unit)")
    overtime_hours_per_worker: float = Field(20.0, ge=5.0, le=60.0, description="Overtime hours per worker per cycle")
    baseline_expedited_fraction: float = Field(0.05, ge=0.0, le=1.0, description="Baseline fraction of expedited orders")


class FinancialLineItemProvenance(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    epistemic_tier: Literal["CALCULATED"] = "CALCULATED"
    formula: str
    assumptions_applied: List[str]
    unit: str = "USD"
    calculation_statement: str


class FinancialLineItem(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    name: str
    baseline_value: float
    scenario_value: float
    delta_value: float
    unit: str = "USD"
    provenance: FinancialLineItemProvenance


class BusinessImpactResult(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    scenario_id: str
    scenario_name: str
    revenue_impact: FinancialLineItem
    cogs_impact: FinancialLineItem
    supply_chain_impact: FinancialLineItem
    workforce_impact: FinancialLineItem
    net_profit_delta: float
    epistemic_tier: Literal["CALCULATED"] = "CALCULATED"
    is_profitable_scenario: bool
    break_even_summary: Dict[str, Any]
    statement: str
```

---

## 7. Proposed Phase 7 Test Matrix (20 Points)

The automated test suite (`tests/test_business_impact.py`) will cover:
1. `test_business_assumptions_baseline_integrity`: Default values match Table 1 ($25, $15, 0.15, $30k, $45/hr).
2. `test_business_assumptions_bounds_integrity`: Sensitivity bounds enforced by Pydantic.
3. `test_business_assumptions_phase_segregation`: Rejects Phase 6 operational assumptions (`ASM-006`, `ASM-007`, `ASM-008`).
4. `test_exact_revenue_fulfillment_loss_calculation`: Verifies $L_{\text{fulfillment}} = \min(1, \bar{P}_{\text{late}} \times \kappa_{\text{stockout}})$ and Realized Revenue = Gross Revenue $\times (1 - L_{\text{fulfillment}})$.
5. `test_exact_cogs_calculation`: Verifies Option B: $\text{COGS} = \text{Realized Revenue} \times c_{\text{cogs}}$.
6. `test_exact_supply_chain_disruption_cost`: Verifies delivered-delayed penalty ($N_{\text{delayed}} \times (1 - \kappa_{\text{stockout}}) \times C_{\text{delay\_penalty}}$) and expedited surcharge.
7. `test_exact_turnover_replacement_cost`: Verifies $N_{\text{departures}} \times C_{\text{replacement}}$.
8. `test_exact_overtime_wage_cost`: Verifies $K_{\text{ot}} \times h_{\text{ot}} \times R_{\text{overtime}}$ using overtime hourly labor rate.
9. `test_exact_net_profit_delta_accounting`: Verifies $\Delta \text{Profit} = \Delta \text{Revenue} - \Delta \text{Cost}$.
10. `test_baseline_scenario_invariance`: Zero shock produces exact $\Delta \text{Profit} = 0.0$.
11. `test_unrounded_float_precision`: Verifies IEEE 754 precision preserved across all intermediate calculations.
12. `test_field_level_epistemic_provenance`: Verifies every financial line item is tagged `CALCULATED` with formula and assumption traceability.
13. `test_break_even_sensitivity_analysis`: Identifies parameter thresholds where promotional scenario becomes net negative.
14. `test_no_double_counting_between_domains`: Verifies penalty cost applies strictly to delivered-delayed orders and does not overlap with cancelled revenue loss.
15. `test_non_causal_disclaimer_preservation`: Asserts all statement fields contain non-causal epistemic wording.
16. `test_expedited_shipping_surcharge_trigger`: Verifies expedite fee only applies when shipping mode is expedited, with deterministic baseline fraction fallback.
17. `test_invalid_assumption_override_rejection`: Out-of-bounds parameter raises `ValidationError`.
18. `test_reproducibility_contract`: Bitwise-identical financial outputs on identical inputs.
19. `test_zero_mutation_of_scenario_result`: Asserts `ScenarioRunResult` is unchanged before and after financial evaluation.
20. `test_financial_result_serialization`: Verifies `BusinessImpactResult` serializes cleanly to JSON and dictionary without precision truncation.

---

## 8. Implementation Boundary & Next Steps

Phase 7 implementation will be strictly confined to:
- `src/business/`
  - `src/business/__init__.py`
  - `src/business/schema.py`: Pydantic v2 data contracts.
  - `src/business/engine.py`: `BusinessImpactEngine` executing deterministic financial accounting on `ScenarioRunResult`.
  - `src/business/sensitivity.py`: `BusinessSensitivityEngine` for break-even and parametric sensitivity analysis (Experiment D).
- `tests/test_business_impact.py`: Full 20-point test suite.

**What Phase 7 Will NOT Implement (Deferred to Phases 8–11):**
- No Composite Risk Score (CRS), multi-criteria condition ranking, or recommendation synthesis $\rightarrow$ Phase 8.
- No REST API endpoints or route controllers $\rightarrow$ Phase 9.
- No React UI or dashboard widgets $\rightarrow$ Phase 10.
- No database tables or SQL migrations $\rightarrow$ Phase 11.

---

### Audit Status: PRE-IMPLEMENTATION AUDIT COMPLETED / AWAITING IMPLEMENTATION APPROVAL
Pre-implementation audit is complete. Awaiting explicit user approval before initiating Phase 7 source code implementation. Zero Phase 7 source files or test files have been created.
