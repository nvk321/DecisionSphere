# DecisionSphere: Mathematical Lineage & End-to-End Number Provenance

**Every Number Traced: UI Element → API Endpoint → Schema → Service → Formula → Training Benchmark**  
*Academic Standard: TRL 4 / IEEE & Scopus Research Protocol*  
*Analytical Core Status: FROZEN & INVARIANT*

---

## 1. Lineage Architecture & Overview

DecisionSphere adheres to the principle of **Deterministic Analytical Accountability**:
> *Every integer, currency figure, percentage, and risk score displayed on the user interface must be directly traceable to an authoritative backend calculation, an explicit scenario lever, or an offline-trained model artifact. No frontend component is permitted to invent, interpolate, or extrapolate numerical values.*

```
┌─────────────────────────────────────────────────────────┐
│              FRONTEND PRESENTATION LAYER                │
│  (Next.js 14, React Components, MetricCards, Waterfall) │
└────────────────────────────▲────────────────────────────┘
                             │ JSON over HTTP REST
┌────────────────────────────┴────────────────────────────┐
│                  FASTAPI SERVICE LAYER                  │
│       (app.api.v1.endpoints: simulations, scenarios)    │
└────────────────────────────▲────────────────────────────┘
                             │ Pydantic v2 Models
┌────────────────────────────┴────────────────────────────┐
│            AUTHORITATIVE ANALYTICAL ENGINES             │
│    (src.scenario, src.business, src.recommendation)     │
└────────────────────────────▲────────────────────────────┘
                             │ Model Inferences & Formulas
┌────────────────────────────┴────────────────────────────┐
│            FROZEN MODEL ARTIFACTS & DATASETS            │
│   (models/demand, models/supply_chain, models/workforce)│
└─────────────────────────────────────────────────────────┘
```

---

## 2. Master Number Lineage Rosetta Table

The following master table connects every major metric on the DecisionSphere frontend to its precise analytical origin:

| Frontend Display Label | UI Component | API Route & JSON Path | Backend Service & Function | Governing Mathematical Formula | Epistemic Tier |
|:---|:---|:---|:---|:---|:---:|
| **Composite Risk Score** | `DecisionHero`, `RiskDecompositionCard` | `POST /simulations/run`<br>`recommendation.composite_risk.composite_risk_score` | `RecommendationEngine._compute_composite_risk()` | $\text{CRS} = \sum_{d} w_d R_d$<br>$w = (0.40, 0.40, 0.20)$ | `CALCULATED` |
| **Risk Level** | `DecisionHero`, `Badge` | `recommendation.composite_risk.risk_level` | `RecommendationEngine._compute_composite_risk()` | $\text{CR} \ge 80 \to \text{CRITICAL}$, $\ge 60 \to \text{HIGH}$, $\ge 30 \to \text{MED}$, else $\text{LOW}$ | `CALCULATED` |
| **Decision Category** | `DecisionHero` | `recommendation.decision_category` | `RecommendationEngine.evaluate()` | Deterministic Rule Engine (`RULE-01` to `RULE-07`) | `RECOMMENDED` |
| **Net Profit Delta** | `DecisionHero`, `FinancialCard` | `impact.net_profit_delta` | `BusinessImpactEngine._compute_financials()` | $\Delta \Pi = \Delta R_{\text{realized}} - (\Delta \text{COGS} + \Delta C_{\text{logistics}} + \Delta C_{\text{wf}})$ | `CALCULATED` |
| **Realized Revenue Delta** | `FinancialCard`, `Waterfall` | `impact.realized_revenue.delta_value` | `BusinessImpactEngine._compute_revenue()` | $\Delta R_{\text{realized}} = \Delta R_{\text{gross}} \times (1 - \Delta p_{\text{late}} \times 0.05)$ | `CALCULATED` |
| **COGS Delta** | `FinancialCard`, `Waterfall` | `impact.cogs.delta_value` | `BusinessImpactEngine._compute_cogs()` | $\Delta \text{COGS} = \Delta V_{\text{realized}} \times P_{\text{unit}} \times 0.60$ | `CALCULATED` |
| **Logistics Cost Delta** | `FinancialCard`, `Waterfall` | `impact.supply_chain_cost.delta_value` | `BusinessImpactEngine._compute_logistics_costs()` | $\Delta C_{\text{log}} = \Delta O \cdot \$8.50 + O_{\text{scen}} p_{\text{late}} \$25 - O_{\text{base}} p_{\text{base}} \$25$ | `CALCULATED` |
| **Workforce Cost Delta** | `FinancialCard`, `Waterfall` | `impact.workforce_cost.delta_value` | `BusinessImpactEngine._compute_workforce_costs()` | $\Delta C_{\text{wf}} = \Delta C_{\text{ot}} + \Delta C_{\text{turnover}} + \Delta C_{\text{hike}}$ | `CALCULATED` |
| **Turnover Replacement Drag**| `WorkforceDrawer`, `Waterfall`| `impact.workforce_cost.breakdown.turnover_cost` | `BusinessImpactEngine._compute_workforce_costs()` | $W_{\text{headcount}} \times \Delta p_{\text{att}} \times \$30,000$ (`ASM-004`) | `CALCULATED` |
| **Demand Forecast (Units)** | `DemandDomainCard` | `scenario.demand_result.scenario_value` | `DemandForecaster.predict_horizon()` | $\hat{y}_{t} = f_{\text{XGB}}(\mathbf{x}_t)$, recursive multi-step lag update | `PREDICTED` |
| **Demand Delta (%)** | `DemandDomainCard` | `scenario.demand_result.percentage_change` | `ScenarioEngine._evaluate_demand()` | $(\hat{V}_{\text{scenario}} - \hat{V}_{\text{baseline}}) / \hat{V}_{\text{baseline}} \times 100$ | `CALCULATED` |
| **Late Delivery Risk (%)** | `SupplyChainDomainCard` | `scenario.supply_chain_result.scenario_value` | `SupplyChainClassifier.predict_proba()` | $\hat{P}(\text{Late}=1 \mid \mathbf{x}) = \sigma(A \cdot s(\mathbf{x}) + B)$ | `PREDICTED` |
| **Late Delivery Risk Delta**| `SupplyChainDomainCard` | `scenario.supply_chain_result.percentage_change` | `ScenarioEngine._evaluate_supply_chain()` | $(p_{\text{scen}} - p_{\text{base}}) / p_{\text{base}} \times 100$ | `CALCULATED` |
| **Attrition Risk (%)** | `WorkforceDomainCard` | `scenario.workforce_result.scenario_value` | `WorkforceClassifier.predict_proba()` | $\hat{P}(\text{Attrition}=1 \mid \mathbf{x}) = \sigma(A \cdot s(\mathbf{x}) + B)$ | `PREDICTED` |
| **Attrition Risk Delta** | `WorkforceDomainCard` | `scenario.workforce_result.percentage_change` | `ScenarioEngine._evaluate_workforce()` | $(p_{\text{att\_scen}} - p_{\text{att\_base}}) / p_{\text{att\_base}} \times 100$ | `CALCULATED` |
| **Model SHA-256 Hash** | `AuditView`, `ModelIntegrityCard`| `metadata.provenance.model_hashes` | `ScenarioEngine.get_artifact_fingerprints()` | $\text{SHA256}(\text{read}(\text{filepath}))$ | `OBSERVED` |

---

## 3. Canonical Worked Example: Step-by-Step Numerical Walkthrough

To eliminate any ambiguity, we trace the exact execution of our canonical benchmark scenario:
- **Scenario Configuration:**
  - `demand_growth_pct = 15.0%`
  - `promo_active = True`
  - `scheduled_days_offset = 0` (Standard Class SLA preserved)
  - `shipping_mode_override = None`
  - `overtime_workforce_pct = 40.0%`
  - `salary_hike_override = None`

---

### Step 3.1: Commercial Demand Forecasting
1. **Input Vector:** Historical 35-day window for Store 1, with `Promo=1` activated across the 14-day forecast horizon.
2. **Execution:** `DemandForecaster.predict_horizon(horizon=14, promo_override=1)` runs recursive 14-step autoregressive inference.
3. **Calculated Demand Outputs:**
   - Baseline Demand ($V_{\text{base}}$): $6,855.00$ units.
   - Scenario Demand ($V_{\text{scen}}$): $7,009.25$ units.
   - Demand Growth Delta ($\Delta V$): $+154.25$ units ($+2.25\%$).
4. **Displayed UI Value:** `7,009 Units (+2.3%)` on `DemandDomainCard`.

---

### Step 3.2: Logistics Cross-Domain Propagation & Late Delivery Classification
1. **Cross-Domain Translation:**
   - Under `ASM-007` and `ASM-008`, the normalized cycle volume scales dispatch orders:
     $$\Delta O = O_{\text{baseline}} \times \frac{\Delta V}{V_{\text{baseline}}} = 1,000 \times \frac{154.25}{6,855.00} \approx +23 \text{ orders}$$
   - Total Scenario Dispatched Orders: $O_{\text{scen}} = 1,023$ orders (Baseline: $1,000$ orders).
2. **Execution:** `SupplyChainClassifier.predict_proba()` evaluates order feature vectors under `scheduled_days_offset=0`.
3. **Calculated Logistics Outputs:**
   - Baseline Late Delivery Probability ($p_{\text{base}}$): $0.5480$ ($54.8\%$).
   - Scenario Late Delivery Probability ($p_{\text{scen}}$): $0.5480$ ($54.8\%$).
   - Absolute Late Deliveries: Baseline $= 548$ late orders; Scenario $= 560$ late orders ($\Delta = +12$ late orders).
4. **Displayed UI Value:** `54.8% Late Risk` on `SupplyChainDomainCard`.

---

### Step 3.3: Workforce Cross-Domain Propagation & Attrition Classification
1. **Cross-Domain Translation:**
   - Under `ASM-006`, shifting $40\%$ of employees to mandatory overtime reduces their average `WorkLifeBalance` by $-1.0$ level.
2. **Execution:** `WorkforceClassifier.predict_proba()` evaluates employee vectors under `OverTime='Yes'` and reduced `WorkLifeBalance`.
3. **Calculated Workforce Outputs:**
   - Baseline Attrition Probability ($p_{\text{att\_base}}$): $0.1610$ ($16.1\%$).
   - Scenario Attrition Probability ($p_{\text{att\_scen}}$): $0.2715$ ($27.2\%$).
   - Attrition Risk Delta ($\Delta p_{\text{att}}$): $+0.1105$ ($+68.6\%$ relative increase).
4. **Displayed UI Value:** `27.2% (+68.6%)` on `WorkforceDomainCard`.

---

### Step 3.4: Managerial Financial Accounting
The financial engine applies deterministic accounting equations to compute the net monetary impact:

1. **Revenue Calculation:**
   $$\Delta R_{\text{gross}} = \Delta V_{\text{cycle}} \times P_{\text{unit}} = 154.25 \times \$25.00 = +\$3,856.25$$
   Fulfillment penalty adjustment:
   $$\Delta R_{\text{realized}} = +\$3,856.25 \times (1 - 0.0) = +\$3,856.25$$

2. **Cost of Goods Sold (COGS):**
   $$\Delta \text{COGS} = \Delta R_{\text{realized}} \times 0.60 = +\$3,856.25 \times 0.60 = +\$2,313.75$$

3. **Logistics Cost Breakdown:**
   - Dispatch freight cost: $\Delta O \times \$8.50 = 23 \times \$8.50 = +\$195.50$.
   - Late delivery penalty: $\Delta \text{Late Orders} \times \$25.00 = 12 \times \$25.00 = +\$300.00$.
   - Total Logistics Cost Delta: $+\$495.50$.

4. **Workforce Cost Breakdown:**
   - Overtime payroll: $W_{\text{headcount}} \times \Delta r_{\text{ot}} \times \text{Salary}_{\text{monthly}} \times 0.25 = 100 \times 0.40 \times \$5,000 \times 0.25 = +\$50,000.00$.
   - Turnover replacement drag: $W_{\text{headcount}} \times \Delta p_{\text{att}} \times \$30,000 = 100 \times 0.1105 \times \$30,000 = +\$331,500.00$.
   - Total Workforce Cost Delta: $+\$381,500.00$.

5. **Net Operating Profit Delta ($\Delta \Pi$):**
   $$\Delta \Pi = \Delta R_{\text{realized}} - (\Delta \text{COGS} + \Delta C_{\text{logistics}} + \Delta C_{\text{wf}})$$
   $$\Delta \Pi = +\$3,856.25 - (+\$2,313.75 + +\$495.50 + +\$381,500.00) = -\$380,453.00$$

6. **Displayed UI Value in Pedagogical Single-Facility Trace:** `-$380.5K Net Profit Delta` in red on `DecisionHero` and `FinancialCard`.

---

### Step 3.5: Composite Risk Scoring & Strategic Action Synthesis
1. **Domain Risk Normalization:**
   - Demand Risk ($R_{\text{demand}}$): Low ($15.0/100$) — sales grew modestly.
   - Supply Chain Risk ($R_{\text{supply}}$): Elevated ($54.8/100$) — persistent delivery delays.
   - Workforce Risk ($R_{\text{workforce}}$): High ($72.4/100$) — severe turnover spike.
2. **Composite Risk Calculation:**
   $$\text{CRS} = (0.20 \times 15.0) + (0.40 \times 54.8) + (0.40 \times 72.4) = 53.88 / 100 \quad (\text{HIGH RISK})$$
3. **Policy Engine Evaluation:**
   - Rule Check `RULE-04` (Margin Erosion):
     $$\Delta \Pi < 0 \quad \text{AND} \quad \Delta \text{Revenue} > 0 \implies \text{TRIGGERED}$$
   - Trigger Output: `REJECT_RESTRUCTURE`.
   - Explanatory Rationale: *"Sales expansion produces severe margin destruction due to workforce turnover replacement costs and overtime premiums."*
4. **Displayed UI Value:** `REJECT_RESTRUCTURE` with red hazard badge on `DecisionHero`.

---

## 4. Authoritative Canonical Review 2 Scenario vs. Other Numerical Scenarios

Examiners or reviewers frequently ask why different documentation reports mention different negative profit numbers (e.g. `-$642.7K`, `-$380.5K`, or `-$823.2K`). In DecisionSphere, **every number traces directly to a specific cohort scope and lever configuration**:

### 1. Authoritative Canonical Review 2 Scenario: `-$642.7K` (`-$642,716.18`)
- **Configuration:** Demand Shock = `+15.0%`, Promo = `Active`, Scheduled Lead Time Offset = `0 days`, Freight Override = `Standard Class`, Overtime Target = `40.0%`, Salary Hike = `None`.
- **Cohort Scope:** Full multi-store test cohort ($V_{\text{base}} = 55,666.31$ units, $V_{\text{scen}} = 84,217.35$ units, $\Delta V = +28,551.04$ units; full DataCo test order cohort; full IBM HR test employee cohort).
- **Backend-Generated System-of-Record Financials:**
  - Realized Revenue Delta: `+$26,710.78`
  - COGS Delta: `+$16,026.47`
  - Logistics Disruption Cost Delta: `+$469,188.49`
  - Workforce Overtime & Turnover Cost Delta: `+$184,212.00`
  - **Net Operating Profit Delta:** `-$642,716.18` (Display: `-$642.7K`)
  - **Composite Risk Score (CRS):** `37.48 / 100` (`MODERATE RISK`)
  - **Decision Category:** `REJECT_RESTRUCTURE`
  - **Triggered Action:** `[RULE-04] ACT-FIN-001: Margin Erosion Warning (CRITICAL)`

### 2. Pedagogical Worked-Example Trace (Section 3 above): `-$380.5K` (`-$380,453.00`)
- **Scope:** Simplified 1-facility educational model evaluated over Store 1 alone with a normalized cycle batch ($V_{\text{base}} = 6,855$ units, $W = 100$ employees, $1,000$ baseline orders). Designed for easy mental math and manual step-by-step auditing during technical examination.

### 3. Exploratory UI Stress-Testing Runs: up to `-$823.2K`
- **Scope:** Generated during Milestone 10 edge-case testing under extreme operational shocks (e.g. $60-80\%$ overtime cohorts or expedited air freight surcharges), demonstrating that unchecked operational strain exponentially increases financial penalties.

This demonstrates the core thesis of Decision Intelligence: **Commercial decisions cannot be evaluated in isolation from operational capacity constraints.**
