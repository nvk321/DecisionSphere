# DecisionSphere — Implementation Roadmap & Milestones

This roadmap establishes the phased engineering strategy from project foundation through the target Review 2 milestone (60–75% completion) and onward to the final review.

---

## Phase Overview

```
Phase 0: Foundation & Governance (COMPLETED)
   ↓
Phase 1: Dataset Inventory, Extraction & Audit
   ↓
Phase 2: Retail Demand Forecasting Pipeline
   ↓
Phase 3: Supply Chain Risk Classification Pipeline
   ↓
Phase 4: Workforce / HR Attrition Risk Pipeline
   ↓
Phase 5: Explainable AI (SHAP) Module
   ↓
Phase 6: Scenario Engine & Parameter Propagation
   ↓
Phase 7: Business Impact Analysis Engine
   ↓
Phase 8: Recommendation Engine
   ↓
Phase 9: FastAPI Backend Services
   ↓
Phase 10: React + TypeScript Dashboard
   ↓
Phase 11: End-to-End System Integration & PostgreSQL
   ↓
Phase 12: Automated Testing & Verification
   ↓
Phase 13: Review 2 Demonstration & Academic Deliverables (TARGET)
   ↓
Phase 14: Final Review & Research Optimization (Future Scope)
```

---

## Detailed Milestone Descriptions

### Phase 0: Project Initialization & Governance (Current Status: COMPLETED)
- Inspect complete repository and reference assets.
- Establish `AGENTS.md` and lock project title.
- Establish comprehensive architectural and data contracts in `docs/`.
- Document academic review requirements and rubrics.

### Phase 1: Dataset Inventory, Extraction & Audit
- Extract candidate datasets from `reference/` archives into `data/raw/`.
- Execute automated profiling scripts across Retail Demand, DataCo Supply Chain, and IBM HR datasets.
- Check row/column counts, missing values, cardinality, target distributions, and lookahead leakage risks.
- Select the primary demand forecasting dataset based on empirical audit criteria.
- Produce `docs/data-audit-report.md`.

### Phase 2: Retail Demand Forecasting Module
- Implement time-series feature engineering (calendar attributes, rolling lag windows).
- Enforce strict chronological train/validation/test split.
- Benchmark Level 0 (naive/historical mean) vs. Level 1 (Ridge/ARIMA) vs. Level 2 (XGBoost/LightGBM).
- Evaluate on MAE, RMSE, and WAPE; serialize best model to `models/demand_model.joblib`.

### Phase 3: Supply Chain Risk Classification Module
- Filter DataCo dataset to order-placement features, dropping lookahead columns (`Days for shipping (real)`).
- Implement preprocessing (categorical encoders, scalers) fitted strictly on training data.
- Benchmark Logistic Regression vs. Random Forest vs. XGBoost on `Late_delivery_risk`.
- Evaluate ROC-AUC, PR-AUC, F1, Recall, Precision; serialize best model to `models/supply_chain_model.joblib`.

### Phase 4: Workforce / HR Attrition Risk Module
- Clean IBM HR dataset, removing invariant constants (`EmployeeCount`, `StandardHours`).
- Address ~16% class imbalance using class-weighting and probability threshold tuning.
- Benchmark Logistic Regression vs. Random Forest vs. Gradient Boosting.
- Evaluate PR-AUC, ROC-AUC, Recall, Brier score; serialize best model to `models/hr_model.joblib`.

### Phase 5: Explainable AI (SHAP) Integration
- Fit `TreeExplainer` on trained tree models.
- Generate global feature importance summaries and local waterfall explanation objects.
- Integrate serialized explainer functions into model inference modules.

### Phase 6: Scenario Engine Implementation
- Implement `src/scenario/` orchestrator.
- Map user scenario parameters ($\Delta D, \Delta S, \Delta O$) to domain model feature deltas.
- Unit test parameter boundary enforcement and feature propagation.

### Phase 7: Business Impact Analysis Engine
- Implement traceable formulas for gross revenue, delay penalties, expedite fees, turnover costs, and net margin.
- Implement Composite Risk Index calculation.
- Write deterministic unit tests validating all financial and operational equations.

### Phase 8: Recommendation Engine
- Implement rule-based trigger matrix evaluating computed risks and margins.
- Synthesize actionable mitigations and trade-off statements.
- Provide structured prompt interface for optional LLM narrative synthesis.

### Phase 9: FastAPI Backend Development
- Define Pydantic v2 schemas for requests and responses.
- Implement simulation endpoints (`/api/scenarios/simulate`, `/api/scenarios`, `/api/explain`).
- Configure CORS, error handling middleware, and model startup caching.

### Phase 10: React + TypeScript Dashboard Development
- Build clean, modern UI components with responsive layout:
  - Scenario Builder (sliders, presets).
  - Demand Forecast Chart (historical vs. baseline vs. simulated).
  - Supply Chain & HR Risk Gauge/Heatmaps.
  - Financial KPI Cards & Cost Breakdown Charts.
  - XAI Feature Importance Waterfall Panels.
  - Actionable Strategic Recommendations Cards.

### Phase 11: End-to-End Integration & PostgreSQL
- Configure PostgreSQL models via SQLAlchemy (Scenarios, SimulationRuns, ImpactLogs).
- Connect frontend API client to FastAPI backend.
- Verify full workflow: Slider Adjustment $\rightarrow$ Simulation $\rightarrow$ Database Save $\rightarrow$ UI Render.

### Phase 12: Automated Verification & Testing
- Execute comprehensive test suite:
  - Data preprocessing integrity tests.
  - ML model inference sanity checks.
  - Business formula deterministic math tests.
  - Backend API endpoint integration tests.

### Phase 13: Review 2 Demonstration & Academic Deliverables (Target: 60–75%)
- Prepare Review 2 PowerPoint presentation following official template.
- Compile draft project report adhering to BCSE497J formatting guidelines.
- Record local demo walkthrough and verify guide approval.
