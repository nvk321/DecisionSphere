# DecisionSphere: Frontend ↔ Backend ↔ Research Rosetta Stone

**Complete Architectural Mapping: UI Elements → REST Endpoints → Backend Source → Governing Mathematics → Research Notebooks**  
*Academic Standard: TRL 4 / IEEE & Scopus Research Protocol*  
*Analytical Core Status: FROZEN & INVARIANT*

---

## 1. Architectural Purpose & Overview

The DecisionSphere user interface is not a disconnected dashboard; it is a direct presentation of an underlying scientific inference and deterministic accounting pipeline.

This document serves as the authoritative **Rosetta Stone** linking every screen, component, metric card, and interactive control in the Next.js frontend to its:
1. **Business & Operational Meaning**
2. **FastAPI REST Endpoint & JSON Field**
3. **Backend Service & Implementation File**
4. **Governing Formula or Machine Learning Model**
5. **Epistemic Tier** (`OBSERVED`, `PREDICTED`, `ASSUMED`, `PROPAGATED`, `CALCULATED`, `RECOMMENDED`)
6. **Explanatory Jupyter Notebook & Documentation Source**

---

## 2. Master Rosetta Stone Mapping Table

| Frontend UI Element | Component File | Meaning & Business Interpretation | API Endpoint & Response JSON Path | Backend Source Implementation | Governing Formula / ML Model | Epistemic Tier | Research Notebook & Doc Link |
|:---|:---|:---|:---|:---|:---|:---:|:---|
| **Decision Hero (Main Banner)** | `components/dashboard/DecisionHero.tsx` | High-level executive synthesis indicating whether a simulated scenario is safe to approve, needs restructuring, or should be halted. | `POST /api/v1/simulations/run`<br>`data.recommendation.decision_category` | `src/recommendation/engine.py`<br>`RecommendationEngine.evaluate()` | Deterministic Decision Rule Tree (`RULE-01` to `RULE-07`) | `RECOMMENDED` | `notebooks/11_risk_and_recommendation_engine.ipynb`<br>`docs/DecisionSphere-Complete-Project-Guide.md#section-18` |
| **Composite Risk Score (CRS)** | `components/dashboard/DecisionHero.tsx` | Normalized aggregate operational risk score spanning all three domains ($0-100$). | `POST /api/v1/simulations/run`<br>`data.recommendation.composite_risk.composite_risk_score` | `src/recommendation/engine.py`<br>`_compute_composite_risk()` | $\text{CRS} = \sum_{d} w_d R_d$<br>$w=(0.40, 0.40, 0.20)$ | `CALCULATED` | `notebooks/11_risk_and_recommendation_engine.ipynb`<br>`artifacts/figures/risk_decomposition.png` |
| **Net Profit Delta** | `components/dashboard/DecisionHero.tsx`<br>`components/dashboard/FinancialCard.tsx` | Incremental change in net operating margin after accounting for sales, COGS, delivery penalties, and turnover replacement. | `POST /api/v1/simulations/run`<br>`data.impact.net_profit_delta` | `src/business/engine.py`<br>`BusinessImpactEngine._compute_financials()` | $\Delta \Pi = \Delta R_{\text{realized}} - (\Delta \text{COGS} + \Delta C_{\text{log}} + \Delta C_{\text{wf}})$ | `CALCULATED` | `notebooks/10_financial_accounting.ipynb`<br>`docs/DecisionSphere-Number-Lineage.md#step-34` |
| **Demand Domain Card** | `components/dashboard/DomainCard.tsx` | Projected store sales volume over the 14-day planning horizon under promotional shock vs baseline. | `POST /api/v1/simulations/run`<br>`data.scenario.demand_result` | `src/models/demand/inference.py`<br>`DemandForecaster.predict_horizon()` | Recursive multi-step XGBoost Regressor with autoregressive lag feedback | `PREDICTED` | `notebooks/05_demand_model.ipynb`<br>`artifacts/figures/demand_feature_importance.png` |
| **Supply Chain Domain Card** | `components/dashboard/DomainCard.tsx` | Calibrated probability of customer order shipping delays under selected freight mode and lead time offset. | `POST /api/v1/simulations/run`<br>`data.scenario.supply_chain_result` | `src/models/supply_chain/inference.py`<br>`SupplyChainClassifier.predict_proba()` | Calibrated XGBoost Classifier with Sigmoid scaling ($\tau^* = 0.1700$) | `PREDICTED` | `notebooks/06_supply_chain_model.ipynb`<br>`artifacts/figures/supply_chain_confusion_matrix.png` |
| **Workforce Domain Card** | `components/dashboard/DomainCard.tsx` | Calibrated employee attrition probability resulting from operational workload pressure and overtime fatigue. | `POST /api/v1/simulations/run`<br>`data.scenario.workforce_result` | `src/models/workforce/inference.py`<br>`WorkforceClassifier.predict_proba()` | Calibrated XGBoost Classifier with Sigmoid scaling ($\tau^* = 0.1650$) | `PREDICTED` | `notebooks/07_workforce_model.ipynb`<br>`artifacts/figures/workforce_feature_importance.png` |
| **Financial Waterfall Chart** | `components/charts/FinancialWaterfallChart.tsx` | Visual decomposition of value creation vs margin destruction across revenue, COGS, logistics penalties, and turnover drag. | `POST /api/v1/simulations/run`<br>`data.impact` (revenue, cogs, supply_chain_cost, workforce_cost) | `src/business/engine.py`<br>`BusinessImpactEngine.evaluate()` | Deterministic Managerial Accounting Model (`ASM-001` to `ASM-005`) | `CALCULATED` | `notebooks/10_financial_accounting.ipynb`<br>`artifacts/figures/financial_waterfall.png` |
| **Strategic Recommendations Panel** | `components/dashboard/RecommendationsPanel.tsx` | Itemized operational actions, actionable levers, and trade-off rationales. | `POST /api/v1/simulations/run`<br>`data.recommendation.recommended_actions` | `src/recommendation/engine.py`<br>`_generate_recommendations()` | Evidence-grounded policy rule engine mapping risk triggers to mitigations | `RECOMMENDED` | `notebooks/11_risk_and_recommendation_engine.ipynb`<br>`docs/DecisionSphere-Complete-Project-Guide.md#section-18` |
| **Scenario Builder Levers** | `components/scenario/ScenarioBuilderForm.tsx` | Interactive controls allowing users to configure hypothetical shocks (Demand %, Promo, Lead Time, Overtime %). | `POST /api/v1/scenarios`<br>`ScenarioLevers` schema | `backend/app/schemas/scenario.py`<br>`ScenarioLevers` Pydantic model | Parameterized user input validated against domain bounds | `ASSUMED` | `notebooks/00_project_orientation.ipynb`<br>`docs/DecisionSphere-Complete-Project-Guide.md#section-6` |
| **Simulation Stepper / Progress** | `components/scenario/SimulationProgress.tsx` | Step-by-step visual execution pipeline showing data loading, ML inference, propagation, accounting, and gating. | `POST /api/v1/simulations/run`<br>`data.metadata.execution_metrics` | `src/scenario/engine.py`<br>`ScenarioEngine.run_scenario()` | 13-stage deterministic execution pipeline | `OBSERVED` | `docs/research-system-map.md`<br>`notebooks/13_end_to_end_decision_walkthrough.ipynb` |
| **Provenance & Model Integrity** | `components/audit/ModelIntegrityCard.tsx` | Cryptographic verification badges showing offline model file SHA-256 digests and dataset versions (Gate H). | `GET /api/v1/models/integrity`<br>`data.model_hashes` | `src/scenario/engine.py`<br>`get_artifact_fingerprints()` | $\text{SHA256}(\text{read}(\text{model\_file}))$ cryptographic hash comparison | `OBSERVED` | `notebooks/01_data_inventory_and_provenance.ipynb`<br>`docs/research-system-map.md#stage-11` |
| **Sensitivity Analysis Charts** | `components/charts/SensitivitySweepChart.tsx` | Interactive curve sweeps evaluating how net profit and CRS change across varying demand shocks and lead times. | `POST /api/v1/sensitivity/sweep`<br>`data.points` | `src/business/sensitivity.py`<br>`SensitivityEngine.run_sweep()` | Automated parameter sweep evaluating multi-dimensional grid | `CALCULATED` | `notebooks/12_sensitivity_analysis.ipynb`<br>`artifacts/figures/financial_sensitivity_sweep.png` |
| **Policy Governance Controls** | `components/policy/PolicyEditor.tsx` | Sliders allowing executives to tune risk tolerance thresholds and domain weights ($w_d$). | `POST /api/v1/policy/update`<br>`data.policy_config` | `src/recommendation/policy.py`<br>`PolicyGovernanceEngine` | Weighted Minkowski distance aggregation with configurable bounds | `ASSUMED` | `notebooks/11_risk_and_recommendation_engine.ipynb`<br>`artifacts/figures/crs_weight_stability.png` |

---

## 3. Screen-by-Screen Viva & Inspection Guide

### 3.1 The Dashboard Screen (`/dashboard`)
- **Key Question Answered:** *"Is this scenario commercially and operationally viable?"*
- **Primary Metrics (Canonical Review 2 Run):** `DecisionHero` badge (`REJECT_RESTRUCTURE`), Net Profit Delta (`-$642.7K` / `-$642,716.18`), Composite Risk Score (`37.5/100` / `37.48`).
- **Research Explanation:** Point to `notebooks/10_financial_accounting.ipynb` and `docs/DecisionSphere-Number-Lineage.md#section-4`. Explain that while commercial sales expand, downstream logistical delay penalties (`+$469.2K`) and workforce burnout/turnover drag (`+$184.2K`) wipe out operating margin, triggering `RULE-04`.

### 3.2 The Scenario Builder Screen (`/scenarios/new`)
- **Key Question Answered:** *"What operational levers am I adjusting, and what are their valid ranges?"*
- **Primary Controls:** Demand Growth slider ($-50\%$ to $+100\%$), Promo Toggle (`True/False`), Lead Time Offset ($-3$ to $+3$ days), Overtime % ($0\%$ to $100\%$).
- **Research Explanation:** Point to `src/scenario/schema.py`. Emphasize that levers are typed, bounded Pydantic fields. Adjusting them does **not** alter the underlying frozen models.

### 3.3 The Simulation Results Screen (`/simulations/[id]`)
- **Key Question Answered:** *"How did each domain behave, and where is money being lost?"*
- **Primary Elements:** 3 Domain Cards, Financial Waterfall, Rule Violation Alert (`[RULE-04] Margin Erosion Warning`).
- **Research Explanation:** Point to `notebooks/09_cross_domain_decision_pipeline.ipynb` and `docs/DecisionSphere-Number-Lineage.md`. In the canonical Review 2 test cohort, $+15\%$ demand with promo produces $+28,551$ demand delta $\to$ $47.11\%$ late delivery risk $\to$ $18.85\%$ workforce attrition $\to$ $-\$642.7\text{K}$ profit delta (or $-\$380.5\text{K}$ in the pedagogical single-facility worked example).

### 3.4 The Sensitivity Analysis Screen (`/sensitivity`)
- **Key Question Answered:** *"At what point does this decision tip from profitable to loss-making?"*
- **Primary Charts:** 2D Sweep Curve, Tipping Point Threshold.
- **Research Explanation:** Point to `notebooks/12_sensitivity_analysis.ipynb`. Highlight the **Tipping Point Analysis**: at exactly $+18.4\%$ demand surge without logistics expansion, late delivery penalties and turnover costs overwhelm gross margin gains.

### 3.5 The Audit & Provenance Screen (`/audit`)
- **Key Question Answered:** *"Can an external auditor verify that these calculations were produced by audited models without data drift?"*
- **Primary Badges:** SHA-256 Checksums for `demand_model.joblib`, `supply_chain_model.joblib`, and `workforce_model.joblib`; Gate G/H/I compliance status.
- **Research Explanation:** Point to `notebooks/01_data_inventory_and_provenance.ipynb`. Demonstrate that the SHA-256 digest displayed on screen matches the exact cryptographic hash of the serialized file on disk.
