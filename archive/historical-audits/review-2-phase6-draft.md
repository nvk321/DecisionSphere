# Review 2 — DecisionSphere Requirements, Plan & Deliverables

**Target Review Dates:** September 2 & September 9, 2026 (11:30 AM, Offline Mode)  
**Course:** BCSE497J – Project I  
**School:** School of Computer Science and Engineering (SCOPE), VIT  
**Faculty Guide:** Dr. Suresh A  
**Team Members:**
- P Naga Venkata Kushal (23BDS0133)
- P Manjunatha Kumar Tejas (23BCE0584)
- Jeswanth Reddy Sagabala (23BCE0203)

---

## 1. Official Guidelines & Assessment Rubrics

Per the official university document `1 Guidelines Student Project-1 review-2.docx`, the assessment is structured across four primary components:

| Component | Weight / Focus | Key Requirements |
|---|---|---|
| **1. Literature Survey & Gap Identification** | Academic Foundation & Background | Deepened literature survey, clear formulation of the research gap, and grounding in domain literature. |
| **2. Objectives, Methodology & Architecture** | System Engineering & Rigor | Finalized SMART objectives, detailed system architecture block diagrams, DFD, use case diagrams, and clear algorithmic methodologies. |
| **3. Implementation (60% to 75%) & Demonstration** | Core Working Software Prototype | Live demonstration of a working prototype featuring data ingestion, trained ML models, scenario builder, business impact calculations, and interactive UI. |
| **4. Presentation, Draft Report & Outcome** | Academic Documentation & Artifacts | Professional presentation deck conforming to `4 Review 2 PPT Template.pptx`, draft report conforming to `3 BCSE497J Project I Report - Template.docx`, and documented project outcomes. |

*Note: Every component evaluation includes oral Question & Answer (Q&A) with the faculty panel.*

---

## 2. Review 2 Mandatory Compliance Rules

1. **Title Lock:** Title modification is **NOT PERMITTED** after Review 1. Title must remain:  
   `DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform`
2. **Guide Email Approval:**
   - Formal approval must be obtained from Dr. Suresh A via email covering all four components:
     1. Attendance Sheet
     2. PowerPoint Presentation & Live Demonstration
     3. Initial Draft Project Report
     4. Outcome Report
   - A verified screenshot of the guide's approval email must be placed on **Slide 2** of the Review 2 PPT.
3. **Moodle Submission:** The Review 2 Draft Report document must be uploaded on Moodle prior to the evaluation deadline.
4. **Implementation Target:** Genuine, auditable 60% to 75% implementation. No hollow placeholders or mock dashboards.

---

## 3. Implementation Checklist for 60%–75% Milestone

- [x] **Data Pipeline (Phase 1):** Ingestion, cleaning, profiling, and audit completed across Retail Demand, DataCo Supply Chain, and IBM HR datasets (`docs/data-audit-report.md`, `data/dataset_manifest.json`).
- [x] **Demand Forecasting Model (Phase 2):** Complete retail demand forecasting pipeline implemented on Rossmann Store Sales (`src/data/`, `src/models/demand/`). Evaluated on chronological test set:
  - Level 0 (Naive Seasonal): MAE = 2,398.31 Sales units, RMSE = 3,275.60, WAPE = 33.32%
  - Level 1 (Ridge Regression): MAE = 862.57 Sales units, RMSE = 1,205.38, WAPE = 11.98%
  - Level 2 (XGBoost Regressor): MAE = 584.49 Sales units, RMSE = 838.83, WAPE = 8.12%
- [x] **Supply Chain Risk Model (Phase 3):** Trained classifier predicting late delivery risk on DataCo (`src/models/supply_chain/`). Chronological test holdout results: Level 0 (ROC-AUC 0.50) -> Level 1 (ROC-AUC 0.7520, PR-AUC 0.8216) -> Level 2 XGBoost (ROC-AUC 0.7795, PR-AUC 0.8423, Brier 0.1807). Calibrated via `FrozenEstimator` Sigmoid on validation; threshold $\tau^*=0.17$ yields F1 = 0.7224, Recall = 1.0000. (COMPLETED — FROZEN).
- [x] **Workforce Risk Model (Phase 4):** Trained classifier predicting employee attrition on IBM HR (`src/models/workforce/`). Stratified test holdout results: Level 0 (PR-AUC 0.1629) -> Level 1 (PR-AUC 0.6190, ROC-AUC 0.8330) -> Level 2 XGBoost (PR-AUC 0.5030, ROC-AUC 0.8045, Brier 0.1086, ECE 0.0537). Calibrated via `FrozenEstimator` Sigmoid on validation; threshold $\tau^*=0.21$ yields F1 = 0.4706, Recall = 0.5556, Specificity = 0.8432. (COMPLETED — FROZEN).
- [x] **Explainability & Governance (TreeSHAP XAI integrated directly in Phases 2–4; Phase 5 Governance Status):** TreeSHAP feature attribution matrices integrated across all three predictive domains: Demand (`models/demand/feature_importance.json`), Supply Chain (`models/supply_chain/feature_importance.json`), and Workforce (`models/workforce/feature_importance.json`). Top workforce features: `OverTime` (0.4450), `StockOptionLevel` (0.3434), `MonthlyIncome` (0.2698), `Age` (0.2413), `JobRole` (0.2398). Phase 5 is recognized as a governance status clarification, not an independent implementation deliverable.
- [x] **Scenario Engine (Phase 6):** Functional parameter mapping translating user shocks ($\Delta D, \Delta S, \Delta O$) across models (`src/scenario/`). Enforces strict 6-tier epistemic demarcation, cryptographic model artifact integrity verification, deterministic overtime assignment, discrete parameter sweeps (`ScenarioSweepEngine`), and exclusion of financial calculations. (COMPLETED — FROZEN).
- [ ] **Business Impact Analysis (Phase 7):** Pre-implementation architecture and audit completed (`docs/phase-7-business-impact-audit.md`); implementation awaiting approval (deterministic mathematical calculations for revenue, delay penalties, overtime costs, and net profit delta).
- [ ] **Recommendation Engine (Phase 8):** Rule-grounded synthesis linking risk triggers to prioritized actionable mitigations.
- [ ] **Backend API (Phase 9):** FastAPI application with Pydantic schemas serving `/api/scenarios/simulate`.
- [ ] **Database (Phase 11):** PostgreSQL schema storing scenario configurations and simulation run logs.
- [ ] **Frontend Dashboard (Phase 10):** Interactive React + TypeScript user interface with scenario sliders, forecast graphs, risk gauges, and recommendation cards.
- [x] **Testing Suite (Phases 2–6):** Deterministic unit tests covering data transforms, inference bounds, immutability, and scenario propagation (**53 tests passing cleanly across all modules**).

---

## 4. Required Academic Deliverables Status

| Deliverable | Source Template | Target Format | Progress |
|---|---|---|---|
| **Review 2 PPT** | `university_reviews/REVIEW 2/4 Review 2 PPT Template.pptx` | `.pptx` (adhering to 13-slide template) | Outline & content finalized; slide compilation pending Phase 11 completion. |
| **Draft Project Report** | `university_reviews/REVIEW 2/3 BCSE497J Project I Report - Template.docx` | `.docx` (Chapters 1–4, Times New Roman, exact line spacing) | Report sections drafted in markdown (`docs/`); document compilation scheduled upon model evaluation. |
| **Guide Approval** | University requirement | Email Screenshot on Slide 2 | Pending final prototype walkthrough with guide. |
| **Working Software Demonstration** | DecisionSphere Codebase | Live offline demonstration (React + FastAPI + PostgreSQL) | Planned for presentation day. |

---

## 5. Potential Panel Questions & Prepared Defenses

1. **Panel Question:** *"How does this differ from building three separate Kaggle projects?"*  
   **Defense:** "Individual Kaggle models operate in isolation without decision context. DecisionSphere's novelty is the **cross-domain scenario engine and business impact layer**, which simulates how a decision in one domain (e.g., a promotional sales surge) impacts operational logistics delays and workforce burnout, synthesizing them into a traceable financial profit-and-loss evaluation."
2. **Panel Question:** *"Are the business impact dollar figures produced by an LLM?"*  
   **Defense:** "No. To maintain academic and financial integrity, all revenue, penalty, and labor cost computations are calculated using deterministic mathematical equations grounded in validated industry formulas and published dataset baselines. LLMs are used only for summarizing trade-offs in plain language."
3. **Panel Question:** *"How do you prevent data leakage in your demand forecasting model?"*  
   **Defense:** "We enforce strict chronological time-based splitting. Models are trained only on past time windows and evaluated on subsequent holdout periods without random shuffling, and all lag/rolling features are lagged by at least one timestep."
