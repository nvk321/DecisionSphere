# DecisionSphere — Business Impact Analysis (BIA)

**Status:** PRE-IMPLEMENTATION AUDIT COMPLETED / IMPLEMENTATION NOT YET STARTED  
**Phase:** Phase 7: Business Impact Analysis Engine (`src/business/`)  
**Upstream Interface:** Consumes `ScenarioRunResult` from Phase 6 (`src/scenario/`, FROZEN)  
**Governing Audit Document:** [`docs/phase-7-business-impact-audit.md`](file:///d:/Projects/DecisionSphere/docs/phase-7-business-impact-audit.md)  

---

## 1. Overview
The **Business Impact Analysis (BIA)** module (`src/business/`) combines scenario-propagated model outputs into transparent, auditable, and quantifiable business-level consequences.

**Critical Epistemic & Accounting Invariants:**
- **Deterministic Math:** Business Impact Analysis does **not** train or alter machine learning models. It applies transparent, deterministic accounting formulas.
- **Epistemic Classification:** All outputs are strictly Tier 5 (`CALCULATED`) scenario consequences under explicitly declared assumptions (`ASM-001` through `ASM-005`). They are never presented as real-world financial statements or causal claims.
- **Strict Upstream Decoupling:** Consumes immutable `ScenarioRunResult` from Phase 6. Does not reload raw datasets or modify frozen predictive models.
- **Assumption Ownership:** Governed strictly by financial assumptions `ASM-001` through `ASM-005`. Operational assumptions (`ASM-006`, `ASM-007`, `ASM-008`) remain quarantined in Phase 6.

---

## 2. Traceable Mathematical Formulas

### 2.1 Projected Gross Revenue, Fulfillment Loss & Realized Revenue
- **Gross Revenue:**
  $$\text{Revenue}_{\text{gross}} = Y_{\text{sales}} \times \bar{P}$$
  where $Y_{\text{sales}}$ is the model-projected sales quantity from `demand_result` (Sales units), and $\bar{P}$ is the unit selling price (default $\$1.00/\text{unit}$, configurable via `BusinessAssumptions.unit_price`).
- **Fulfillment Loss Rate:**
  $$L_{\text{fulfillment}} = \min\left(1.0, \bar{P}(\text{Late Delivery}) \times \kappa_{\text{stockout}}\right)$$
  where $\kappa_{\text{stockout}}$ is the late-order cancellation factor (`ASM-003`, default: $0.15$).
- **Realized Revenue:**
  $$\text{Realized Revenue} = \text{Revenue}_{\text{gross}} \times (1 - L_{\text{fulfillment}})$$
  $$\Delta \text{Revenue} = \text{Realized Revenue}_{\text{sim}} - \text{Realized Revenue}_{\text{base}}$$

### 2.2 Cost of Goods Sold (COGS) — Option B: Realized Sales
COGS applies strictly to realized sales (cancelled/unfulfilled orders do not incur manufacturing/fulfillment COGS):
$$\text{Cost}_{\text{cogs}} = \text{Realized Revenue} \times c_{\text{cogs}}$$
where $c_{\text{cogs}}$ is the baseline COGS percentage (default $0.60$, or $60\%$, yielding $40\%$ contribution margin).

### 2.3 Operational Supply Chain Disruption Cost
$$\text{Cost}_{\text{supply\_chain}} = \text{Cost}_{\text{delay\_penalty}} + \text{Cost}_{\text{expedited\_freight}}$$
1. **Contractual Late Delivery Penalty (Delivered-Delayed Shipments Only):**
   To prevent double-counting with cancelled revenue loss, carrier delay penalties apply only to delivered-delayed orders:
   $$N_{\text{delayed\_expected}} = N_{\text{orders}} \times \bar{P}(\text{Late Delivery})$$
   $$N_{\text{lost\_expected}} = N_{\text{delayed\_expected}} \times \kappa_{\text{stockout}}$$
   $$N_{\text{delivered\_delayed}} = N_{\text{delayed\_expected}} - N_{\text{lost\_expected}} = N_{\text{orders}} \times \bar{P}(\text{Late Delivery}) \times (1 - \kappa_{\text{stockout}})$$
   $$\text{Cost}_{\text{delay\_penalty}} = N_{\text{delivered\_delayed}} \times C_{\text{delay\_penalty}}$$
   where $C_{\text{delay\_penalty}}$ is `ASM-001` (default: $\$25.00/\text{delayed order}$).
2. **Expedited Freight Surcharge ($N_{\text{expedited}}$ Mapping):**
   - If `shipping_mode_override in {"First Class", "Same Day"}`: $N_{\text{expedited}} = N_{\text{orders}} \times 1.0$ ($100\%$ expedited).
   - If `shipping_mode_override in {"Standard Class", "Second Class"}`: $N_{\text{expedited}} = 0.0$ ($0\%$ expedited).
   - If `shipping_mode_override is None`: $N_{\text{expedited}} = N_{\text{orders}} \times f_{\text{expedite\_base}}$ (baseline fraction: $5\%$).
   $$\text{Cost}_{\text{expedited\_freight}} = N_{\text{expedited}} \times C_{\text{expedite\_fee}}$$
   where $C_{\text{expedite\_fee}}$ is `ASM-002` (default: $\$15.00/\text{expedited order}$).

### 2.4 Workforce Overtime & Attrition Replacement Cost
$$\text{Cost}_{\text{workforce}} = \text{Cost}_{\text{turnover\_replacement}} + \text{Cost}_{\text{overtime\_labor}}$$
- **Turnover Replacement Cost:**
  $$N_{\text{departures}} = N_{\text{workforce}} \times \bar{P}(\text{Attrition})$$
  $$\text{Cost}_{\text{turnover\_replacement}} = N_{\text{departures}} \times C_{\text{replacement}}$$
  where $C_{\text{replacement}}$ is `ASM-004` (default: $\$30,000/\text{departed employee}$).
- **Overtime Hourly Labor Cost:**
  Active overtime headcount: $K_{\text{ot}} = \text{workforce\_cohort\_summary.scenario\_overtime\_count}$.
  Overtime hours per worker per planning cycle: $h_{\text{ot}} = 20.0\text{ hours}$.
  $$\text{Cost}_{\text{overtime\_labor}} = (K_{\text{ot}} \times h_{\text{ot}}) \times R_{\text{overtime}}$$
  where $R_{\text{overtime}}$ is `ASM-005` (**Overtime hourly labor rate**, default: $\$45.00/\text{hr}$).

### 2.5 Net Incremental Business Margin ($\Delta \text{Profit}$)
$$\Delta \text{Profit} = \Delta \text{Revenue} - (\Delta \text{Cost}_{\text{cogs}} + \Delta \text{Cost}_{\text{supply\_chain}} + \Delta \text{Cost}_{\text{workforce}})$$

---

## 3. Operational Composite Risk Score (CRS) — Deferral to Phase 8
The **Composite Risk Score (CRS)** is an operational multi-criteria index rather than a financial dollar accounting line item.
- **Phase 7 Scope:** Strictly confined to deterministic financial accounting ($\Delta \text{Revenue}$, $\Delta \text{COGS}$, $\Delta \text{Cost}_{\text{supply}}$, $\Delta \text{Cost}_{\text{workforce}}$, $\Delta \text{Profit}$, and break-even sensitivities).
- **Phase 8 Scope:** Evaluates multi-criteria condition triggers, normalizes cross-domain operational risk probabilities, computes composite priority indices (including CRS), and synthesizes actionable recommendations.

---

## 4. Documentation of Assumptions
Financial parameters are treated as **Parametric Assumptions** (`ASM-001` through `ASM-005`) and logged transparently in `docs/assumptions-and-open-questions.md`. Users can configure these cost parameters through the application settings within their declared sensitivity bounds.
