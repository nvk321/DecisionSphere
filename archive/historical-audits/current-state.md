# DecisionSphere — Current State & Progress Tracking

**Last Updated:** September 6, 2026  
**Current Milestone:** Milestone 11 (Research, Explainability, EDA, ML Documentation, and Publication Suite) COMPLETED & VERIFIED  
**Current Active Work:** Complete scientific research and explanation layer implemented. 16 executable Jupyter notebooks in `notebooks/` (all 16 passing with 0 errors), 15 publication figures at 300 DPI in `artifacts/figures/`, comprehensive 24-section master project guide (`docs/DecisionSphere-Complete-Project-Guide.md`), complete technical glossary (`docs/DecisionSphere-Glossary.md`), number lineage trace (`docs/DecisionSphere-Number-Lineage.md`), design rationale (`docs/DecisionSphere-Design-Rationale.md`), assumptions & limitations (`docs/DecisionSphere-Assumptions-and-Limitations.md`), frontend-to-research mapping (`docs/Frontend-to-Research-Mapping.md`), reproducibility guide (`docs/reproducibility.md`), four-track learning path (`docs/DecisionSphere-Learning-Path.md`), and 14 academic paper chapters (`docs/research-paper-materials/`). 236 automated tests passing (35 frontend + 101 backend + 100 analytical core/research). TRL 4 validated. Frozen core (`src/` and `models/`) 100% invariant.  
**Target Goal:** Review 2 (Scheduled September 2026 — 60–75% Demonstrable Prototype) — FULLY VERIFIED, DEFENDED, AND DEMO-READY  

---

## 1. Executive Status Summary

| Workstream | Status | Details |
|---|---|---|
| **Project Identity & Title** | **LOCKED & FINAL** | *DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform* approved in Review 1. |
| **Review 1 Deliverables** | **COMPLETED** | Review 1 PPT completed, presented 29-07-2026. Literature survey, research gap, objectives, SDG 9, TRL 2 formulated. |
| **Phase 0: Documentation & Foundation** | **COMPLETED** | `AGENTS.md`, full `docs/` architecture suite, review tracking docs, and data contracts established. |
| **Phase 1: Dataset Inventory & Audit** | **COMPLETED** | Exhaustive audit of all 16 archives in `reference/`. Selected Rossmann (Demand), DataCo (Supply Chain), IBM HR (Workforce). Documented in `docs/data-audit-report.md` and `data/dataset_manifest.json`. |
| **Phase 2: Demand Forecasting Pipeline** | **COMPLETED** | Rossmann pipeline implemented (`src/data/`, `src/models/demand/`). Level 0 (33.32% WAPE) -> Level 1 (11.98% WAPE) -> Level 2 XGBoost (8.12% WAPE, MAE: 584.49 Sales units). TreeSHAP integrated; serialized to `models/demand/demand_model.joblib`. |
| **Research Foundation & Governance** | **COMPLETED** | Formulated research blueprint (`docs/research-direction.md`), 14-paper literature gap matrix (`docs/literature-gap-matrix.md`), experimental design suite (`docs/experimental-design.md`), reference project audit (`docs/reference-project-audit.md`), and Section 13 in `AGENTS.md`. |
| **Phase 3: Supply Chain Delivery Risk Pipeline** | **COMPLETED (FROZEN)** | DataCo pipeline implemented (`src/data/dataco_*`, `src/models/supply_chain/`). Strict anti-leakage exclusion, chronological split (Train: 125.2k, Val: 30.95k, Test: 24.37k). Level 0 (ROC-AUC 0.50) -> Level 1 (ROC-AUC 0.7520) -> Level 2 XGBoost (ROC-AUC **0.7795**, PR-AUC **0.8423**, Brier 0.1807). Calibrated via `FrozenEstimator` Sigmoid on Val; validation threshold $\tau^*=0.17$ ($F_1=0.7224$, Recall 1.0). TreeSHAP integrated; serialized to `models/supply_chain/supply_chain_model.joblib`. |
| **Phase 4: Workforce / HR Attrition Pipeline** | **COMPLETED (FROZEN)** | IBM HR pipeline implemented (`src/data/ibm_hr_*`, `src/models/workforce/`). Invariants/surrogates dropped (30 final predictors). Stratified split (Train: 1029, Val: 220, Test: 221). Level 0 (PR-AUC 0.1629) -> Level 1 (PR-AUC 0.6190, ROC-AUC 0.8330) -> Level 2 XGBoost (PR-AUC **0.5030**, ROC-AUC **0.8045**, Calibrated Brier **0.1086**, Calibrated ECE **0.0537**). Calibrated via `FrozenEstimator` Sigmoid on Val; validation threshold $\tau^*=0.21$ ($F_1=0.4706$, Recall 0.5556, Specificity 0.8432). TreeSHAP integrated (top feature: `OverTime` 0.4450); serialized to `models/workforce/workforce_model.joblib`. |
| **Phase 5: Governance Status Clarification** | **GOVERNANCE STATUS ONLY** | Phase 5 is not an independent implementation phase. No Phase 5 predictive artifact, model, or mandatory implementation dependency exists. Explainable AI (TreeSHAP) was integrated directly into predictive Phases 2, 3, and 4. |
| **Phase 6: Scenario Engine & Parameter Propagation** | **COMPLETED (FROZEN)** | Multi-domain orchestrator implemented (`src/scenario/`). Pydantic v2 data contracts, code-level AssumptionRegistry (`ASM-006`, `ASM-007`, `ASM-008`), cryptographic artifact integrity verification, deterministic overtime mapping, per-field epistemic provenance, discrete parameter sweeps (`ScenarioSweepEngine`), and 20 unit tests. |
| **Phase 7: Business Impact Analysis Engine** | **COMPLETED (FROZEN)** | Pure deterministic financial accounting engine implemented (`src/business/`). Pydantic v2 data contracts (`BusinessAssumptions`, `FinancialLineItem`, `BusinessImpactResult`), non-overlapping cost accounting (delivered-delayed penalty separated from cancellation churn, realized-sales COGS), `ASM-001` through `ASM-005` coupling, 1D sensitivity sweeps and break-even engine (`BusinessSensitivityEngine`), and 20 unit tests. |
| **Phase 8: Recommendation Engine & Trade-Off Analysis** | **COMPLETED (FROZEN)** | Rule-based condition triggers, multi-criteria trade-off evaluation, and actionable recommendation synthesis implemented (`src/recommendation/`). Purely operational Composite Risk Score (`ASM-009`, `ASM-010`), 7 deterministic trigger rules, lexicographic decision categorization (`PROCEED`, `PROCEED_WITH_MITIGATIONS`, `REJECT_RESTRUCTURE`), severity/exposure sorting, and 20 unit tests. Full repository regression: **93 passed, 0 failed**. |
| **Phase 9: FastAPI REST Backend Service** | **COMPLETED (All Milestones 9.0–9.7 Verified)** | Milestones 9.0 through 9.7 complete. All REST endpoints mounted under `/api/v1/` with full Gate J, Gate F (atomicity/rollback), Gate I (model integrity failure refusal), Gate D (database constraints/cascades), and containerized live E2E simulation verified. 101 backend tests passing. Total backend & core suite: **194 passed, 0 failed**. |
| **Milestone 10: DecisionSphere Frontend & Decision Intelligence UI** | **COMPLETED & VERIFIED** | Production-quality Next.js 15 App Router + React 19 decision-support application (`frontend/`). All 11 application feature routes (+ 1 built-in `not-found` route = 12 Next.js static build routes) implemented and verified. 35 frontend tests passing. |
| **Milestone 11: Research, Explainability, EDA & Publication Suite** | **COMPLETED & VERIFIED** | 16-part Jupyter suite (all 16 executed with 0 errors), 15 publication figures (300 DPI), comprehensive project guide, glossary, number lineage trace, design rationale, assumptions/limitations, frontend-to-research mapping, reproducibility guide, 4-track learning path, and 14 academic paper draft chapters. 7 research regression tests passing. Test count breakdown: 93 core analytical + 7 research (100 total in `tests/`) + 101 backend (`backend/tests/`) + 35 frontend (`frontend/`) = **236 passed, 0 failed**. |
| **Review 2 Deliverables (Report, PPT, Demo)** | **READY (TRL 4 Validated)** | Fully working end-to-end laboratory prototype with live backend inference, scenario creation, simulation run, risk evaluation, sensitivity sweeps, and complete research explanation layer ready for faculty presentation. |


---

## 2. Completed Milestones

### Phase 0: Project Initialization & Foundation
- [x] Comprehensive repository inspection (reference archives, old student projects, university guidelines).
- [x] Extraction and analysis of official Review 1 PPT, Review 2 Guidelines, Review 2 Report Template, and Review 2 PPT Template.
- [x] Authored core engineering protocol: `AGENTS.md`.
- [x] Authored architectural, ML, and business specifications across 16 `docs/` files.
- [x] Formally accepted `docs/architecture-decisions/ADR-001-initial-architecture.md`.
- [x] Authored university reviews master records (`reviews-overview.md`, `review-1.md`, `review-2.md`).
- [x] Normalized repository configuration, UTF-8 dependencies, and `.gitignore`.

### Phase 1: Dataset Inventory, Understanding & Audit
- [x] Programmatically profiled all candidate datasets via `scripts/audit_datasets.py`.
- [x] Audited Demand candidates: compared Rossmann vs. Walmart vs. Corporación Favorita on granularity, promotional levers, data quality, and compute footprint.
- [x] Selected **Rossmann Store Sales** for demand forecasting (daily granularity, explicit $+82.5\%$ `Promo` lift, 0 missing values).
- [x] Audited Supply Chain candidates: confirmed **DataCo Smart Supply Chain** (180k orders, balanced $54.8\%$ late risk).
- [x] Discovered and documented critical lookahead leakage in DataCo (`Days for shipping (real)` must be dropped at order-time prediction).
- [x] Audited Workforce candidate: confirmed **IBM HR Analytics** (1,470 records, identified `OverTime` triples attrition risk from $10.4\%$ to $30.5\%$).
- [x] Quarantined legacy and synthetic reference files (`archive (8).zip`, legacy student projects).
- [x] Authored comprehensive audit documentation: `docs/data-audit-report.md`.
- [x] Created machine-readable manifest: `data/dataset_manifest.json`.

### Phase 2: Retail Demand Forecasting Pipeline
- [x] Extracted and verified Rossmann raw data (1,017,209 train records, 1,115 stores, 942 days).
- [x] Implemented modular loader and metadata merger: `src/data/rossmann_loader.py`.
- [x] Implemented causally valid feature engineering with strict anti-leakage: `src/data/rossmann_features.py` (calendar, holiday, promo, store, store-grouped lags and shifted rolling stats; excluded `Customers`).
- [x] Implemented chronological split (Train: 2013-01-01 to 2014-10-19 [712,574 rows], Val: 2014-10-20 to 2015-03-10 [145,190 rows], Test: 2015-03-11 to 2015-07-31 [159,445 rows]).
- [x] Trained baseline hierarchy:
  - **Level 0 (Naive Seasonal):** MAE = 2,398.31 Sales units, RMSE = 3,275.60 Sales units, WAPE = 33.32%.
  - **Level 1 (Ridge Regression):** MAE = 862.57 Sales units, RMSE = 1,205.38 Sales units, WAPE = 11.98%.
  - **Level 2 (XGBoost Regressor):** MAE = 584.49 Sales units, RMSE = 838.83 Sales units, WAPE = **8.12%** (Open stores); MAE = 482.44, RMSE = 763.75, WAPE = 8.12% (All stores).
- [x] Integrated TreeSHAP explainability (`src/models/demand/explain.py`): computed empirical feature ranking on test data (top features: `Sales_lag_14`, `Promo`, `Sales_lag_28`, `Sales_lag_1`, `Sales_rolling_mean_14`).
- [x] Serialized artifact bundle: `models/demand/demand_model.joblib` (0.78 MB).
- [x] Implemented production inference service (`src/models/demand/inference.py`) supporting single-step and recursive multi-step forecasting without future actual sales.
- [x] Authored automated unit test suite (`tests/test_demand_pipeline.py`, `tests/test_demand_inference.py`): 8 tests passing.

### Phase 3: Supply Chain Delivery Risk Classification Pipeline
- [x] Extracted and verified raw DataCo dataset (180,519 line items, 65,752 unique orders, 53 columns).
- [x] Conducted exhaustive 53-column pre-implementation audit (`docs/phase-3-supply-chain-plan-audit.md`), rigorously establishing feature eligibility and anti-leakage boundary (excluding 8 target leaks, PII, and surrogate identifiers).
- [x] Implemented modular loader: `src/data/dataco_loader.py`.
- [x] Implemented order-time feature construction (22 predictors: 12 numerical, 10 categorical): `src/data/dataco_features.py`.
- [x] Enforced strict chronological train/val/test splitting without time overlap:
  - Train: 2015-01-01 to 2016-12-31 (125,200 rows, 69.36%, Late: 54.97%)
  - Validation: 2017-01-01 to 2017-06-30 (30,950 rows, 17.15%, Late: 54.05%)
  - Test Holdout: 2017-07-01 to 2018-01-31 (24,369 rows, 13.50%, Late: 55.11%)
- [x] Trained baseline hierarchy evaluated on out-of-time test holdout:
  - **Level 0 (Naive Majority / Prevalence):** ROC-AUC = 0.5000, PR-AUC = 0.5511, Brier = 0.2474, F1 = 0.7106
  - **Level 1 (Logistic Regression):** ROC-AUC = 0.7520, PR-AUC = 0.8216, Brier = 0.1949, F1 = 0.6661
  - **Level 2 (XGBoost Raw @ 0.50):** ROC-AUC = **0.7795**, PR-AUC = **0.8423**, Brier = **0.1807**, ECE = 0.0128, F1 = 0.7078
  - **Level 2 (XGBoost Calibrated @ 0.50):** ROC-AUC = 0.7795, PR-AUC = 0.8423, Brier = 0.1818, ECE = 0.0324, F1 = 0.7079
  - **Level 2 (XGBoost Calibrated @ Optimal Validation $\tau^*=0.17$):** F1 = **0.7224**, Precision = 0.5654, Recall = **1.0000**, Specificity = 0.0563
- [x] Implemented scikit-learn 1.9 compatible calibration using `from sklearn.frozen import FrozenEstimator` (strictly on validation set; test set never participates in calibration).
- [x] Extracted empirical TreeSHAP feature attributions on test holdout (`src/models/supply_chain/explain.py`): top features are `days_for_shipment_scheduled` (0.7476), `shipping_mode` (0.6780), `type` (0.3842), `order_hour` (0.1641), `order_country` (0.0778).
- [x] Serialized comprehensive research bundle:
  - `models/supply_chain/supply_chain_model.joblib` (0.20 MB)
  - `models/supply_chain/metrics.json`
  - `models/supply_chain/confusion_matrix.json`
  - `models/supply_chain/calibration.json`
  - `models/supply_chain/feature_importance.json`
  - `models/supply_chain/experiment_metadata.json`
- [x] Implemented production inference & scenario simulation service (`src/models/supply_chain/inference.py`) with empirical monotonicity diagnostic and strict epistemic tier labeling (`PREDICTED`).
- [x] Authored comprehensive unit & integration tests (`tests/test_supply_chain_pipeline.py`, `tests/test_supply_chain_inference.py`): 11 tests passing; entire test suite (19 tests) passing.

### Phase 4: Workforce / HR Attrition Classification Pipeline
- [x] Extracted and verified raw IBM HR dataset (1,470 employee records, 35 attributes, 0 missing values).
- [x] Enforced strict feature exclusion: dropped 3 invariant constants (`EmployeeCount`, `StandardHours`, `Over18`) and 1 surrogate key (`EmployeeNumber`), leaving exactly 30 modeling predictors.
- [x] Implemented modular loader: `src/data/ibm_hr_loader.py` with rigorous shape and distribution assertions.
- [x] Implemented feature engineering and stratified splitting: `src/data/ibm_hr_features.py` (Train: 1,029 [166 pos / 16.13%], Val: 220 [35 pos / 15.91%], Test: 221 [36 pos / 16.29%]).
- [x] Enforced zero preprocessing leakage (ColumnTransformer fitted strictly on Train).
- [x] Computed empirical `scale_pos_weight = 863 / 166 = 5.1988` from training partition.
- [x] Trained baseline hierarchy evaluated on untouched test holdout:
  - **Level 0 (Prevalence Baseline):** PR-AUC = 0.1629, ROC-AUC = 0.5000, Brier = 0.1364, F1 = 0.0000
  - **Level 1 (Balanced Logistic Regression):** PR-AUC = **0.6190**, ROC-AUC = **0.8330**, Brier = 0.1578, F1 = 0.4587 (Recall = 0.6944)
  - **Level 2 (XGBoost Raw @ 0.50):** PR-AUC = 0.5030, ROC-AUC = 0.8045, Brier = 0.1415, ECE = 0.1723, F1 = 0.4878 (Recall = 0.5556)
  - **Level 2 (XGBoost Calibrated @ 0.50):** PR-AUC = 0.5030, ROC-AUC = 0.8045, Brier = **0.1086**, ECE = **0.0537**, F1 = 0.3404 (Precision = 0.7273)
  - **Level 2 (XGBoost Calibrated @ Optimal Validation $\tau^*=0.21$):** F1 = **0.4706**, Precision = 0.4082, Recall = **0.5556**, Specificity = 0.8432, Accuracy = 0.7964
- [x] Implemented scikit-learn 1.9 `FrozenEstimator` Sigmoid calibration on validation set, substantially improving calibration quality (Brier 0.1415 -> 0.1086; ECE 0.1723 -> 0.0537).
- [x] Extracted empirical TreeSHAP feature attributions on test holdout (`src/models/workforce/explain.py`): top features are `OverTime` (0.4450), `StockOptionLevel` (0.3434), `MonthlyIncome` (0.2698), `Age` (0.2413), and `JobRole` (0.2398).
- [x] Serialized comprehensive research bundle to `models/workforce/`:
  - `workforce_model.joblib` (0.13 MB)
  - `metrics.json`
  - `confusion_matrix.json`
  - `calibration.json`
  - `feature_importance.json`
  - `experiment_metadata.json`
- [x] Implemented production inference & scenario simulation service (`src/models/workforce/inference.py`) supporting `overtime_override` and `salary_hike_override` with baseline invariance, numerical tolerance validation, and strict epistemic tier labeling (`PREDICTED`).
- [x] Authored comprehensive unit & integration tests (`tests/test_workforce_pipeline.py`, `tests/test_workforce_inference.py`): 14 tests passing; entire test suite (33 tests) passing.

### Phase 5: Governance Status Clarification
- Phase 5 is not currently represented as an independent implementation phase in the frozen project architecture. No Phase 5 predictive artifact, model, or mandatory implementation dependency is assumed by Phase 6. Phase 6 therefore proceeds as the next approved implementation stage following the completion and freezing of the applicable predictive modules.
- Domain-specific explainable AI (TreeSHAP feature attributions and stability analyses) was integrated and serialized directly within the respective predictive phases:
  - Demand Forecasting TreeSHAP: top features `Sales_lag_14`, `Promo`, `Sales_lag_28` (`models/demand/feature_importance.json`).
  - Supply Chain Delivery Risk TreeSHAP: top features `days_for_shipment_scheduled`, `shipping_mode`, `type` (`models/supply_chain/feature_importance.json`).
  - Workforce Attrition TreeSHAP: top features `OverTime`, `StockOptionLevel`, `MonthlyIncome`, `Age`, `JobRole` (`models/workforce/feature_importance.json`).

### Phase 6: Scenario Engine & Cross-Domain Parameter Propagation
- [x] Defined and enforced strictly typed Pydantic v2 schemas: `ScenarioLevers`, `ScenarioAssumptions`, `DomainProvenance`, `DomainPredictionResult`, `WorkforceCohortSummary`, `ScenarioRunResult` (`src/scenario/schema.py`).
- [x] Implemented code-level `AssumptionRegistry` for `ASM-001` through `ASM-008` with strict phase boundary isolation (`src/scenario/assumptions.py`).
- [x] Implemented production `ScenarioEngine` orchestrator (`src/scenario/engine.py`) with SHA-256 model artifact integrity verification, baseline DataFrame immutability assertions, and exact IEEE 754 unrounded delta precision.
- [x] Implemented deterministic overtime assignment mapping targeting exact headcount proportions without disturbing baseline 'Yes' records.
- [x] Implemented `ASM-006` WorkLifeBalance decrement clamped in $[1, 4]$, `ASM-007` volume scaling, and `ASM-008` 30-day planning cycle synchronization.
- [x] Implemented discrete parameter sweep engine (`ScenarioSweepEngine` in `src/scenario/sweep.py`) for Experiment B and Experiment D.
- [x] Authored 20-point automated test suite (`tests/test_scenario_engine.py`): 20 passed; full repository regression passes cleanly: **53 passed, 0 failed in 30.76s**.
- [x] Zero financial calculations in Phase 6; Phase 6 artifact frozen.

---

## 3. Phase 6 → Phase 7 Architectural Handoff & Governance Boundary

The interface between Phase 6 (Scenario Engine) and Phase 7 (Business Impact Analysis) enforces strict epistemic and functional separation:

1. **Artifact Handoff:**
   - Phase 6 produces the immutable, strongly typed `ScenarioRunResult` containing domain predictions, unrounded deltas ($\Delta \hat{y}$, $\Delta \bar{P}_{\text{late}}$, $\Delta \bar{P}_{\text{att}}$), and cryptographic model fingerprints.
   - Phase 7 consumes `ScenarioRunResult` directly. Phase 7 does **not** reload raw data, does **not** invoke machine learning models, and does **not** alter frozen model weights.
2. **Assumptions Ownership Segregation:**
   - **Phase 6 Operational Assumptions:** `ASM-006` ($\Delta \text{WLB} = -1$), `ASM-007` ($\gamma_{\text{volume}} = 1.0$), `ASM-008` ($\tau_{\text{cycle}} = 30\text{ days}$).
   - **Phase 7 Financial Assumptions:** `ASM-001` (Late penalty: $\$25.00$), `ASM-002` (Expedite fee: $\$15.00$), `ASM-003` (Cancellation churn: $0.15$), `ASM-004` (Turnover replacement: $\$30,000$), `ASM-005` (Overtime hourly labor rate: $\$45.00/\text{hr}$).
3. **Epistemic Demarcation:**
   - Phase 6 quantities are epistemically `PREDICTED`, `ASSUMED`, and `PROPAGATED`.
   - Phase 7 financial figures ($\Delta \text{Revenue}$, $\Delta \text{Cost}$, $\Delta \text{Profit}$) are strictly `CALCULATED` scenario estimates, not realized accounting forecasts or causal claims.

### Phase 7: Business Impact Analysis Engine
- [x] Defined and enforced strictly typed Pydantic v2 schemas: `BusinessAssumptions`, `FinancialLineItemProvenance`, `FinancialLineItem`, `BreakEvenAnalysis`, `BusinessImpactResult` (`src/business/schema.py`).
- [x] Enforced strict assumption boundaries: `ASM-001` ($25.00), `ASM-002` ($15.00), `ASM-003` ($0.15$), `ASM-004` ($30,000), `ASM-005` ($45.00/hr), `cogs_ratio` ($0.60$), `unit_price` ($1.00$), `overtime_hours_per_worker` ($20.0$), `baseline_expedited_fraction` ($0.05$).
- [x] Prevented double-counting: delay penalty fees ($C_{\text{delay\_penalty}}$) apply strictly to delivered-delayed orders ($N_{\text{delayed}} \times (1 - \kappa_{\text{stockout}})$); cancelled/churned orders affect realized gross revenue and are never charged carrier penalties; COGS is applied strictly to realized sales revenue (Option B).
- [x] Implemented deterministic expedited freight surcharge mapping: `shipping_mode_override` $\in \{\text{"First Class"}, \text{"Same Day"}\} \implies 100\%$, $\in \{\text{"Standard Class"}, \text{"Second Class"}\} \implies 0\%$, and `None` $\implies$ baseline fraction.
- [x] Implemented production `BusinessImpactEngine` (`src/business/engine.py`) with continuous IEEE 754 precision, per-field `CALCULATED` epistemic provenance, and analytical break-even threshold calculations.
- [x] Implemented `BusinessSensitivityEngine` (`src/business/sensitivity.py`) for 1D parameter sweeps, break-even boundary searches, and grid sweeps over `ASM-001` through `ASM-005` (Experiment D).
- [x] Authored comprehensive 20-point automated test suite (`tests/test_business_impact.py`): 20 passed; full repository regression suite reports: **73 passed, 0 failed in 27.77s**.
- [x] Verified zero mutation of `ScenarioRunResult` and verified that frozen model artifacts remain invariant.

### Phase 8: Recommendation Engine & Strategic Trade-Off Analysis
- [x] Defined and enforced strictly typed Pydantic v2 schemas: `CRSWeights`, `CompositeRiskBreakdown`, `StrategicAction`, `TradeOffEvaluation`, `RecommendationResult` (`src/recommendation/schema.py`).
- [x] Implemented Composite Risk Score engine (`src/recommendation/crs.py`) with baseline domain weights (`ASM-009`: $w_{\text{supply}}=0.40, w_{\text{workforce}}=0.40, w_{\text{demand}}=0.20$), simplex validation, continuous IEEE-754 calculation, zero financial terms, and categorical risk level classification.
- [x] Implemented deterministic trigger rules engine (`src/recommendation/rules.py`) with all 7 approved rules (`RULE-01` to `RULE-07`), non-causal trade-off statements, and severity/exposure priority sorting.
- [x] Implemented central `RecommendationEngine` orchestrator (`src/recommendation/engine.py`) with lexicographic decision framework (`ASM-010`: $\tau_{\text{risk}}=50.0$), non-causal executive briefings, and Experiment D sensitivity tools (`sweep_crs_weights`, `find_recommendation_flip_threshold`).
- [x] Authored comprehensive 20-point automated test suite (`tests/test_recommendation_engine.py`): 20 passed; full repository regression reports: **93 passed, 0 failed in 23.64s**.
- [x] Verified zero mutation of `ScenarioRunResult` and `BusinessImpactResult`, and verified that all 3 serialized model fingerprints remain 100% invariant.

### Milestone 10: DecisionSphere Frontend & Decision Intelligence UI
- [x] Conducted comprehensive UI/UX research on decision-intelligence interfaces, progressive disclosure, epistemic honesty, and accessibility (`docs/frontend-research.md`).
- [x] Established 21-endpoint backend-to-frontend contract matrix with zero client-side mathematical reproduction.
- [x] Formulated product requirements, UX principles, screen specifications, and responsive design taxonomy (`docs/frontend-requirements.md`).
- [x] Architected design system with HSL design tokens, typography scale, 6-tier epistemic color scheme, and typed API architecture (`docs/frontend-architecture.md`).
- [x] Scaffolded Next.js 15.1.7 App Router + React 19 + TypeScript + Tailwind CSS 3.4.17 + TanStack Query v5 + Recharts application.
- [x] Implemented UI primitives: Button, Card, Badge, Slider, Input, Select, Table, Tabs, Dialog.
- [x] Implemented common specialized state components: `EpistemicBadge`, `ErrorBanner`, `LoadingSkeleton`, `EmptyState`, `MetricDisplay`.
- [x] Built application shell: Collapsible Sidebar, Header with real-time backend health probe and Gate I model integrity status badge, Breadcrumbs, PageHeader, AppShell layout.
- [x] Implemented typed API client with correlation ID propagation (`X-Request-ID`), error normalization (`DecisionSphereAPIError`), and endpoint modules for scenarios, simulations, policies, sensitivity, and system.
- [x] Implemented all 11 application feature routes (+ 1 built-in `not-found` route = 12 Next.js static routes):
  - `/` (Decision Cockpit / Dashboard)
  - `/scenarios` (Scenario Workspace List)
  - `/scenarios/[id]` (Two-Column Scenario Editor & Lever Configurator)
  - `/simulate` (Pre-Flight Review & 9-Stage Execution Runner)
  - `/simulations` (Simulation History)
  - `/simulations/[id]` (Executive Decision Results, Domain Cards, Waterfall & Cryptographic Provenance)
  - `/sensitivity` (Sensitivity Lab: Experiment B, Experiment D, CRS Simplex, Tipping Point Search)
  - `/policies` (Assumption Policy Management & Simplex Validation)
  - `/audit` (Provenance & Cryptographic Verification Tuple $\Sigma_{\text{run}}$)
  - `/system/health` (Infrastructure & DB Health Diagnostics)
  - `/system/models` (SHA-256 Model Fingerprint Verification & Integrity Table)
- [x] Built test suite: 35 frontend Vitest tests covering utils, constants, API client error normalization, and components.
- [x] Verified zero regression across backend and core models: 101 backend tests + 93 core tests = 194 passed.
- [x] Grand total: **229 automated tests passing, 0 failed**.
- [x] Verified `git diff --stat src models` is 100% empty (Invariants #1 & #2 preserved).

---

## 3. Phase 8 → Phase 9 Architectural Handoff & Governance Boundary

The interface between Phase 8 (Recommendation Engine) and Phase 9 (FastAPI REST Backend) establishes clean separation between analytical synthesis and web service routing:

1. **Artifact Handoff:**
   - Phase 8 produces `RecommendationResult` encapsulating the entire analytical execution (decision category, CRS breakdown, trade-off rationale, prioritized strategic actions, and non-causal executive briefing).
   - Phase 9 exposes RESTful API endpoints (`/api/v1/scenarios/run`, `/api/v1/recommendations`, `/api/v1/sensitivity`) that serve these Pydantic schemas directly as JSON responses to client applications.
2. **Epistemic Demarcation:**
   - Client applications receive fully tagged response payloads distinguishing `PREDICTED` model inferences, `PROPAGATED` operational bridges, `CALCULATED` financial items, and `RECOMMENDED` strategic actions.

---

## 4. Phase 9 Implementation Tracking

**Current Milestone:** Milestone 9.7 Completed & Verified; Phase 9 Architecture & Delivery COMPLETE.  
**Task Title:** *Phase 9: FastAPI REST Backend Service (`backend/`)*  
**Status:** COMPLETED & VERIFIED (194 Total Automated Tests Passing: 93 Analytical Core + 101 Backend)  
**Implementation Milestones:**
1. **[x] Milestone 9.0:** Foundation & Environment Hardening (Configuration, Dependencies, Structured Logging, Correlation IDs, Error Contracts, Health Probes) — **COMPLETED & VERIFIED (19 tests passing)**
2. **[x] Milestone 9.1:** Database Engine & SQLAlchemy 2.0 Models (Session Factory, 10 Relational Models, Constraints, Cascades, Persistence Boundary) — **COMPLETED & VERIFIED (24 backend tests passing; 5 model tests)**
3. **[x] Milestone 9.2:** Alembic Migrations Setup (Revision 18e29557529f, Gate C Idempotency Verified, Dual CLI Support) — **COMPLETED & VERIFIED (27 backend tests passing; 3 migration tests)**
4. **[x] Milestone 9.3:** Application Services Layer (ScenarioService, PolicyService, SimulationOrchestrator, SensitivityService; Gate F Atomicity, Gate G Version Immutability, Gate H Provenance Tuple, Gate I Model Integrity, ADR-006 AnyIO Threadpool Offload) — **COMPLETED & VERIFIED (45 backend tests passing; 18 service tests)**
5. **[x] Milestone 9.4:** Pydantic v2 Schemas & API DTOs (Request/Response separation, extra="forbid", Gate E schema validation, simplex validation, ORM-to-DTO serialization) — **COMPLETED & VERIFIED (55 backend tests passing; 10 schema tests)**
6. **[x] Milestone 9.5:** FastAPI Route Controllers & API Router (Thin service-driven controllers, centralized error handling, ADR-006 concurrency, route ordering, and comprehensive contract tests) — **COMPLETED & VERIFIED (83 backend tests passing; 28 route/contract tests)**
7. **[x] Milestone 9.6:** Backend Automated Async Test Suite (`httpx.AsyncClient` + `ASGITransport`; Gate J E2E Simulation Lifecycle, Gate F HTTP Rollback & Atomicity, Gate I HTTP Model Integrity Refusal, Gate D Database Constraints/Cascades, Asynchronous Concurrency) — **COMPLETED & VERIFIED (96 backend tests passing; 13 new async/integration tests)**
8. **[x] Milestone 9.7:** Docker & Docker Compose Setup (Multi-stage build, non-root appuser UID 10001, entrypoint PostgreSQL readiness & Alembic migrations, live container health + E2E simulation verified, test_docker_config.py, 5 new tests) — **COMPLETED & VERIFIED (101 backend tests passing; 194 total repository tests passing)**



