# DecisionSphere — Implementation Roadmap & Milestones

This roadmap establishes the phased engineering strategy from project foundation through the target Review 2 milestone (60–75% completion) and onward to the final review.

---

## Phase Overview

```
Phase 0: Documentation & Foundation (COMPLETED)
   ↓
Phase 1: Dataset Inventory & Audit (COMPLETED)
   ↓
Phase 2: Retail Demand Forecasting Pipeline (COMPLETED)
   ↓
Phase 3: Supply Chain Delivery Risk Pipeline — FROZEN (COMPLETED)
   ↓
Phase 4: Workforce / HR Attrition Risk Pipeline — FROZEN (COMPLETED)
   ↓
Phase 5: Governance Status Clarification — NOT AN IMPLEMENTATION PHASE
   ↓
Phase 6: Scenario Engine & Cross-Domain Parameter Propagation — FROZEN (COMPLETED)
   ↓
Phase 7: Business Impact Analysis Engine — PRE-IMPLEMENTATION / APPROVED (AWAITING IMPLEMENTATION)
   ↓
Phase 8+: Recommendation Engine and application/full-stack layers — PENDING
   (Phase 8: Recommendation Engine, Phase 9: FastAPI Backend, Phase 10: React Frontend,
    Phase 11: System Integration & PostgreSQL, Phase 12: Full Automated Testing,
    Phase 13: Review 2 Deliverables & Demonstration, Phase 14: Final Review Scope)
```

---

## Detailed Milestone Descriptions

### Phase 0: Documentation & Foundation (Status: COMPLETED)
- Inspect complete repository and reference assets.
- Establish `AGENTS.md` and lock project title.
- Establish comprehensive architectural, epistemic, and data contracts in `docs/`.
- Document academic review requirements, rubrics, and research protocols.

### Phase 1: Dataset Inventory & Audit (Status: COMPLETED)
- Extract candidate datasets from `reference/` archives into `data/raw/`.
- Profile Retail Demand (Rossmann), DataCo Supply Chain, and IBM HR datasets.
- Check row/column counts, missing values, cardinality, target distributions, and lookahead leakage risks.
- Enforce strict feature exclusion rules and produce `docs/data-audit-report.md` and `data/dataset_manifest.json`.

### Phase 2: Retail Demand Forecasting Pipeline (Status: COMPLETED)
- Implement time-series feature engineering (calendar attributes, rolling lag windows).
- Enforce strict chronological train/validation/test split.
- Benchmark Level 0 (naive seasonal) vs. Level 1 (Ridge) vs. Level 2 (XGBoost Regressor).
- Achieve verified test performance: WAPE = 8.12%, MAE = 584.49 Sales units, RMSE = 838.83.
- Integrate TreeSHAP feature attributions (`models/demand/feature_importance.json`); serialize to `models/demand/demand_model.joblib`.

### Phase 3: Supply Chain Delivery Risk Pipeline (Status: COMPLETED — FROZEN)
- Filter DataCo dataset strictly to order-placement features, dropping lookahead leakage (`Days for shipping (real)`).
- Implement preprocessing (categorical encoders, scalers) fitted strictly on training data.
- Benchmark Level 0 (majority class) vs. Level 1 (Logistic Regression) vs. Level 2 (XGBoost Classifier).
- Achieve verified test performance: ROC-AUC = 0.7795, PR-AUC = 0.8423, Brier = 0.1807.
- Calibrate probabilities via `FrozenEstimator` Sigmoid on validation; threshold $\tau^*=0.17$ yields F1 = 0.7224, Recall = 1.0000.
- Integrate TreeSHAP feature attributions (`models/supply_chain/feature_importance.json`); serialize to `models/supply_chain/supply_chain_model.joblib`.

### Phase 4: Workforce / HR Attrition Risk Pipeline (Status: COMPLETED — FROZEN)
- Clean IBM HR dataset, removing invariant constants (`EmployeeCount`, `StandardHours`, `Over18`) and surrogate ID (`EmployeeNumber`).
- Address ~16% class imbalance using class-weighting and probability threshold tuning.
- Benchmark Level 0 (majority class) vs. Level 1 (Logistic Regression) vs. Level 2 (XGBoost Classifier).
- Achieve verified test performance: PR-AUC = 0.5030, ROC-AUC = 0.8045, Calibrated Brier = 0.1086, Calibrated ECE = 0.0537 (preserving Level 1 benchmark PR-AUC = 0.6190 honestly).
- Calibrate probabilities via `FrozenEstimator` Sigmoid on validation; threshold $\tau^*=0.21$ yields F1 = 0.4706, Recall = 0.5556, Specificity = 0.8432.
- Integrate TreeSHAP feature attributions (top feature: `OverTime` 0.4450); serialize to `models/workforce/workforce_model.joblib`.

### Phase 5: Governance Status Clarification (Status: GOVERNANCE STATUS ONLY — NOT AN IMPLEMENTATION PHASE)
- Clarify architectural status: Phase 5 is not an independent implementation phase in the frozen project architecture.
- Explainable AI (TreeSHAP) was integrated directly into predictive Phases 2, 3, and 4.
- No Phase 5 predictive model, artifact, or mandatory implementation dependency exists.

### Phase 6: Scenario Engine & Cross-Domain Parameter Propagation (Status: COMPLETED — FROZEN)
- Implement `src/scenario/` orchestrator, cryptographic model artifact hashing, deterministic overtime mapping, and discrete sweeps (`ScenarioSweepEngine`).
- Map user scenario parameters ($\Delta D, \Delta S, \Delta O$) across domain models while enforcing strict parallel non-causal execution.
- Accept operational coupling assumptions only: `ASM-006` ($\Delta \text{WLB} = -1$), `ASM-007` ($\gamma_{\text{volume}} = 1.0$), `ASM-008` ($\tau_{\text{cycle}} = 30\text{ days}$).
- Strictly exclude all financial accounting and reject `ASM-001` through `ASM-005`.
- Produce the immutable, strongly typed `ScenarioRunResult` handoff artifact.
- Automated verification: 20 unit tests passing; full regression suite: 53 passed, 0 failed.

### Phase 7: Business Impact Analysis Engine (Status: PRE-IMPLEMENTATION AUDIT COMPLETED / READY FOR APPROVAL)
- Pre-implementation audit completed (`docs/phase-7-business-impact-audit.md`); implementation not yet started.
- Downstream consumer of `ScenarioRunResult` without reloading models or modifying Phase 6 behavior.
- Implements deterministic, transparent mathematical formulas for gross revenue, delay penalties, expedite surcharges, turnover replacement, overtime expenses, and net incremental profit ($\Delta \text{Profit}$).
- Governed strictly by financial assumptions: `ASM-001` through `ASM-005`.
- Outputs epistemically classified as CALCULATED; enforces non-causal scenario interpretation.
- Proposed modules: `src/business/__init__.py`, `src/business/schema.py`, `src/business/engine.py`, `src/business/sensitivity.py`, `tests/test_business_impact.py`.

### Phase 8+: Recommendation Engine and Application/Full-Stack Layers (Status: PENDING)
- **Phase 8 (Recommendation Engine):** Rule-based trigger matrix evaluating computed risks and margins; synthesized actionable mitigations and trade-off statements.
- **Phase 9 (FastAPI Backend Services):** Pydantic v2 schemas, endpoints (`/api/scenarios/simulate`, `/api/scenarios`, `/api/explain`), CORS, error handling.
- **Phase 10 (React + TypeScript Dashboard):** Scenario Builder, Demand Visualizer, Risk Gauges, Financial KPI Cards, and Recommendation Cards.
- **Phase 11 (End-to-End Integration & PostgreSQL):** SQLAlchemy database models, scenario/run logging, and full system integration.
- **Phase 12 (Automated Verification & Testing):** Complete integration test suite, API tests, and UI verification.
- **Phase 13 (Review 2 Demonstration & Deliverables):** Presentation deck adhering to `4 Review 2 PPT Template.pptx`, draft report, live demo walkthrough.
- **Phase 14 (Final Review & Research Optimization):** Full system evaluation, manuscript drafting, and project wrap-up.
