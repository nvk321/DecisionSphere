# DecisionSphere — Final Release & Repository Audit Report

**Date of Release:** September 6, 2026  
**Project Title (Locked):** `DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform`  
**Course:** BCSE497J – Project I, School of Computer Science and Engineering (SCOPE), VIT  
**Faculty Guide:** Dr. Suresh A  
**Investigators:** P Naga Venkata Kushal (23BDS0133), P Manjunatha Kumar Tejas (23BCE0584), Jeswanth Reddy Sagabala (23BCE0203)  
**Technology Readiness Level:** TRL 4 (Component / System Laboratory Validation)  

---

## 1. Project Purpose & Scope

DecisionSphere is an AI-powered strategic decision intelligence platform that allows organizational leadership to simulate and evaluate hypothetical business decisions across three interconnected operational domains—**Demand Forecasting**, **Supply Chain Logistics**, and **Workforce Human Capital**—before committing capital in the real world. 

By replacing departmental analytical silos with a coupled 13-stage linear execution pipeline, DecisionSphere translates commercial shocks into downstream operational strains, computing transparent managerial accounting metrics ($\Delta \Pi$) and synthesizing rule-grounded strategic recommendations without non-deterministic language model arithmetic.

---

## 2. Final System Architecture

```
                       [User Scenario Parameters]
               (ΔDemand %, Promo, Lead Time SLA, Overtime %)
                                    │
                                    ▼
       [FastAPI REST API Layer (Pydantic v2 Contracts & Validation)]
                                    │
       [13-Stage Linear Execution Pipeline & Scenario Engine]
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
[Retail Demand Model]     [Supply Chain Risk Model]      [Workforce Risk Model]
 (Rossmann Store Sales)    (DataCo Smart Supply Chain)    (IBM HR Analytics)
  • XGBoost Regressor       • Calibrated XGB Classifier    • Calibrated XGB Classifier
  • WAPE = 8.12%            • ROC-AUC = 0.7795             • ROC-AUC = 0.8045
  • Chronological Split     • Platt Calibrated ECE=0.014   • Platt Calibrated ECE=0.053
    │                               │                               │
    └───────────────────────────────┼───────────────────────────────┘
                                    ▼
                   [Deterministic Managerial Accounting]
              (Realized Revenue, COGS, Logistics, Labor Costs)
                                    │
                                    ▼
                [Composite Risk Score (CRS) Simplex Scoring]
             (CRS = 0.40 Supply + 0.35 Workforce + 0.25 Demand)
                                    │
                                    ▼
               [Rule-Grounded Decision Engine (RULE-01 to 07)]
             (Decision Categories: APPROVE, REJECT_RESTRUCTURE, etc.)
                                    │
                                    ▼
   [Next.js 15 / React 19 Single-Page Application (11 Feature Routes / 12 Compiled Build Targets)]
```

---

## 3. Final Repository Structure

```
DecisionSphere/
├── README.md                          # Master navigation, quickstart & research overview
├── LICENSE                            # MIT open-source academic license
├── CITATION.cff                       # Machine-readable academic citation metadata
├── requirements.txt                   # Frozen Python environment dependencies
├── alembic.ini / Dockerfile           # Production containerization assets
├── docker-compose.yml                 # Multi-container orchestration (Postgres, API, Web)
├── docker-entrypoint.sh               # Container initialization script
├── RELEASE_AUDIT.md                   # Complete release & repository audit (this document)
│
├── src/                               # [FROZEN] Core analytical package (Zero drift)
│   ├── data/                          # Feature engineering & anti-leakage registries
│   ├── models/                        # Estimator wrappers and inference pipelines
│   ├── scenario/                      # Parameter contracts and cross-domain propagation
│   ├── business/                      # Deterministic managerial accounting engine
│   └── recommendation/                # Composite risk scoring and rules RULE-01 to 07
│
├── models/                            # [FROZEN] Serialized pre-trained estimators & XAI
│   ├── demand/                        # demand_model.joblib & feature_importance.json
│   ├── supply_chain/                  # supply_chain_model.joblib & feature_importance.json
│   └── workforce/                     # workforce_model.joblib & feature_importance.json
│
├── backend/                           # Production FastAPI REST backend
│   ├── app/                           # Routers, schemas, services, database models
│   └── tests/                         # 101 automated integration and contract tests
│
├── frontend/                          # Next.js 15 + React 19 single-page application
│   ├── src/app/                       # 11 functional application routes (12 compiled build targets)
│   ├── src/components/                # UI widgets, Recharts waterfall, gauges, modals
│   └── tests/                         # 35 automated Vitest unit & component tests
│
├── docs/                              # Authoritative documentation suite (9 master docs)
│   ├── project-guide.md               # Beginner-friendly complete guide
│   ├── architecture.md                # Component boundaries and execution diagrams
│   ├── methodology.md                 # Scientific methodology, ML models, calibration
│   ├── assumptions-limitations.md     # All assumptions (ASM-001 to 008) and validity threats
│   ├── reproducibility.md             # Step-by-step reproduction instructions
│   ├── glossary.md                    # Unified domain terminology & 6 epistemic tiers
│   ├── frontend-research-mapping.md   # Mathematical trace from UI to backend formulas
│   ├── number-lineage.md              # Reconciled canonical worked numbers
│   ├── frontend-manual-verification.md# Pedagogical testing and verification guide
│   └── architecture-decisions/        # Architectural Decision Records (ADR-001 to ADR-006)
│
├── paper/                             # Formal academic research publication package
│   ├── DecisionSphere_Research_Paper.tex # IEEEtran conference LaTeX manuscript (15 sections)
│   ├── references.bib                 # Verified BibTeX bibliography (12 primary citations)
│   ├── figures/                       # High-resolution 300 DPI publication plots (15 plots)
│   ├── tables/                        # Modular LaTeX table sources
│   └── README.md                      # Overleaf and local compilation guide
│
├── university_reviews/
│   ├── REVIEW_1/                      # Review 1 slides and summary
│   └── REVIEW_2/                      # Review 2 deliverable package (BCSE497J)
│       ├── requirements.md            # Official evaluation rubrics mapping
│       ├── evidence-matrix.md         # Traceability matrix (all marked PASS)
│       ├── presentation-outline.md    # 24-slide PPT blueprint with speaking cues
│       ├── demo-checklist.md          # Step-by-step live viva demonstration runbook
│       ├── viva-questions.md          # Exhaustive examiner defense Q&A
│       └── final-status.md            # Readiness sign-off declaration
│
├── notebooks/                         # 16 executable research notebooks (00_ to 15_)
├── artifacts/figures/                 # 15 canonical generated 300 DPI plots
├── data/                              # Dataset manifests, schemas, and download notes
├── tests/                             # Analytical core & research test suite (100 tests)
├── scripts/                           # Execution, auditing, and reproduction utilities
└── archive/                           # Preserved historical development records
    ├── historical-audits/             # Point-in-time phase audit reports (Phases 3-9)
    ├── development-notes/             # Intermediate development scratchpads & designs
    └── README.md                      # Catalog and provenance of archived materials
```

---

## 4. Final Dataset Inventory & Provenance

| Dataset | Origin / Source | License | Records | Attributes | Partition Protocol | Leakage Safeguards |
|---|---|---|---|---|---|---|
| **Retail Demand** | Rossmann Store Sales (Kaggle) | Open / Competition | 1,017,209 | 18 | Strict Chronological (Train: 2013–14; Test: 2015) | No random shuffling; rolling lags computed strictly on past data. |
| **Supply Chain** | DataCo Smart Supply Chain (Mendeley Data) | CC BY 4.0 | 180,519 | 53 | Chronological Holdout | Immutable `PROHIBITED_LOOKAHEAD_COLUMNS` order-time registry. |
| **Workforce** | IBM HR Analytics Employee Attrition (Kaggle) | Open Data | 1,470 | 35 | Stratified Holdout (80/20) | Encoders, scalers, and imputers fitted strictly on training partition. |

---

## 5. Final Model Inventory & Verification

| Model Domain | Algorithm | Serialization Path | Target | Primary Metric | Calibration Protocol | Verified SHA-256 Digest |
|---|---|---|---|---|---|---|
| **Demand** | XGBoost Regressor | `models/demand/demand_model.joblib` | Daily Sales | $\text{WAPE} = 8.12\%$ | N/A (Continuous) | `fb438c03a742202657bb4ef9196ff17e004bc090e99218f02985dc7720f41941` |
| **Supply Chain** | Calibrated XGBoost | `models/supply_chain/supply_chain_model.joblib` | Late Risk (0/1) | $\text{ROC-AUC} = 0.7795$ | Platt Sigmoid ($\text{ECE} = 0.0142$) | `0052e641cf355257abb332703c3e6a46c65e9ab10a975227d83cf77d7e689b59` |
| **Workforce** | Calibrated XGBoost | `models/workforce/workforce_model.joblib` | Attrition (0/1) | $\text{ROC-AUC} = 0.8045$ | Platt Sigmoid ($\text{ECE} = 0.0537$) | `4b195c7bee3ab8f4afe75ccd0c75fff0c8e18b9fca88a00305e165a010109918` |

---

## 6. Final Notebook Inventory (All 16 Passing)

1. `00_project_orientation.ipynb`: Architecture, environment setup, and verification orientation.
2. `01_data_inventory_and_provenance.ipynb`: Ingestion profiling, missingness, and SHA-256 verification.
3. `02_demand_eda.ipynb`: Retail demand seasonal cycles, store clusters, and calendar patterns.
4. `03_supply_chain_eda.ipynb`: Shipment delay distributions, carrier lead times, and shipping modes.
5. `04_workforce_eda.ipynb`: Attrition drivers, overtime strain, salary bands, and department tenure.
6. `05_demand_model.ipynb`: Multi-tier demand modeling (Naive, Ridge, XGBoost) and TreeSHAP attribution.
7. `06_supply_chain_model.ipynb`: Late delivery classification, order-time filtering, and Sigmoid calibration.
8. `07_workforce_model.ipynb`: Class-imbalanced attrition modeling, probability calibration, and TreeSHAP.
9. `08_model_evaluation_and_comparison.ipynb`: Multi-metric model comparison tables and reliability curves.
10. `09_cross_domain_decision_pipeline.ipynb`: Deterministic scenario parameter coupling and feature updating.
11. `10_financial_accounting.ipynb`: Realized revenue, COGS, logistics penalty, and overtime labor formulas.
12. `11_risk_and_recommendation_engine.ipynb`: Simplex-weighted Composite Risk Scoring and rules RULE-01 to 07.
13. `12_sensitivity_analysis.ipynb`: Unidimensional parameter sweeps, tipping points, and weight stability.
14. `13_end_to_end_decision_walkthrough.ipynb`: Full 13-stage linear pipeline execution trace.
15. `14_research_figures.ipynb`: Automated reproduction and generation of publication-quality plots.
16. `15_number_lineage_worked_example.ipynb`: Single-store pedagogical worked trace vs enterprise canonical run.

---

## 7. Final Publication Figure Inventory

1. `architecture_overview.png`: 13-stage execution pipeline and governance gates.
2. `dataset_distributions.png`: Multi-source dataset empirical distribution histograms.
3. `demand_feature_importance.png`: TreeSHAP attribution plot for retail demand forecasting.
4. `supply_chain_confusion_matrix.png`: Confusion matrix for calibrated logistics classifier at $\tau^* = 0.17$.
5. `supply_chain_roc_pr_calibration.png`: ROC, Precision-Recall, and Platt reliability diagrams for logistics.
6. `workforce_feature_importance.png`: TreeSHAP attribution plot for employee turnover risk.
7. `workforce_roc_pr_calibration.png`: ROC, Precision-Recall, and Platt reliability diagrams for workforce.
8. `cross_domain_propagation.png`: Parameterized feature coupling and shock propagation flowchart.
9. `financial_waterfall.png`: Managerial accounting waterfall breakdown for the canonical Review 2 scenario.
10. `risk_decomposition.png`: Multi-domain operational strain polar decomposition and CRS gauge.
11. `demand_sensitivity_curve.png`: Demand forecast elasticity across promotional intensity.
12. `financial_sensitivity_sweep.png`: Profitability surface across varying delay penalties and overtime multipliers.
13. `crs_weight_stability.png`: Simplex weight perturbation stability analysis.
14. `tipping_point_analysis.png`: Identification of the $+12.5\%$ unbuffered promotional tipping point.
15. `number_lineage_trace.png`: Complete parameter-to-recommendation arithmetic audit trace.

---

## 8. Final Documentation Inventory

- `docs/project-guide.md`: Authoritative beginner-friendly guide explaining the system from zero.
- `docs/architecture.md`: System architectural blueprints, layer responsibilities, and execution flow.
- `docs/methodology.md`: Complete machine learning training protocols, benchmarks, and calibration.
- `docs/assumptions-limitations.md`: Complete assumptions catalog (`ASM-001` to `ASM-008`) and validity threats.
- `docs/reproducibility.md`: Step-by-step reproduction instructions for another researcher.
- `docs/glossary.md`: Technical dictionary and formal 6-tier epistemic definitions.
- `docs/frontend-research-mapping.md`: Exhaustive UI-to-API-to-backend-to-formula mathematical trace.
- `docs/number-lineage.md`: Explicit reconciliation of canonical enterprise figures vs pedagogical traces.
- `docs/frontend-manual-verification.md`: Interactive pedagogical testing and verification runbook.
- `docs/architecture-decisions/`: Immutable ADR records (ADR-001 through ADR-006).

---

## 9. Review 2 Status Sign-Off

```
============================================================
REVIEW 2 READINESS: FULLY PREPARED & EXCEEDS 60-75% THRESHOLD
============================================================
```
- **Component 1 (Literature Survey & Gap):** Complete (15+ papers, verified research gap).
- **Component 2 (Objectives, Methodology, Architecture):** Complete (SMART objectives, 13-stage DFD).
- **Component 3 (Implementation & Demonstration):** Complete (100% analytical core, backend, and UI implemented; 236 tests passing).
- **Component 4 (Presentation & Report):** Complete (24-slide PPT blueprint, Chapters 1–4 report ready).
- **Guide Approval:** Verified authorization from Dr. Suresh A for Slide 2.

---

## 10. Research Paper Manuscript Status

```
============================================================
PAPER STATUS: IEEE-FORMATTED RESEARCH MANUSCRIPT READY
============================================================
```
- Location: `paper/DecisionSphere_Research_Paper.tex`
- Bibliography: `paper/references.bib` (12 verified primary citations, zero fabricated DOIs).
- Structure: Standard 15-section IEEE conference format.
- Canonical Scenario Reconciliation: Aligned to live backend canonical figures ($-\$642,716.18$).

---

## 11. Test & Build Status

| Suite | Scope | Total Tests | Status | Execution Time |
|---|---|:---:|:---:|:---:|
| Analytical Core (`tests/`) | Models, data transforms, scenario engine, business impact | 93 | **PASS** | 51.4s |
| Research Quality Suite (`tests/`) | Notebook structure, figures, docs completeness, model hashes | 7 | **PASS** | 7.3s |
| FastAPI Backend (`backend/tests/`) | REST routes, Pydantic schemas, policy simplex, simulations | 101 | **PASS** | 173.4s |
| Frontend Client (`frontend/tests/`) | Unit utilities, API client, Recharts waterfall, RiskGauge | 35 | **PASS** | 9.4s |
| **Grand Total** | **Entire Automated Testing Infrastructure** | **236** | **100% PASS** | **~4.0 mins** |
| Next.js Production Build | Static & dynamic page generation | 11 feature routes (+ 1 /_not-found) | **COMPILED** | 3.9s |

---

## 12. Reproducibility & Model Integrity Status

- **Automated Verification:** `python scripts/reproduce_all.py` executes all 5 quality gates cleanly.
- **Model Hash Verification:**
  - `demand_model.joblib`: `fb438c03...` (VERIFIED MATCH)
  - `supply_chain_model.joblib`: `0052e641...` (VERIFIED MATCH)
  - `workforce_model.joblib`: `4b195c7b...` (VERIFIED MATCH)
- **Analytical Core Invariance:** `git diff --stat src models` returns **0 files modified**.

---

## 13. Authoritative Canonical Review 2 Scenario Reconciliation

The repository enforces **strictly one canonical enterprise scenario**:
- Commercial Shock: Demand Shock $+15.0\%$, Promo Active.
- Logistics Setting: Standard Class Shipping, $0\text{d}$ Lead Time SLA Offset.
- Workforce Setting: $40.0\%$ Mandatory Overtime, Baseline Wage.
- **Demand Delta:** $+28,551.04$ units ($+51.29\%$)
- **Late Delivery Rate:** $49.24\% \to 47.11\%$ ($\Delta = -2.13\text{ pp}$)
- **Workforce Attrition Rate:** $16.51\% \to 18.85\%$ ($\Delta = +2.34\text{ pp}$)
- **Gross Revenue Delta:** $+\$28,551.04$
- **Realized Revenue Delta:** $+\$26,710.78$
- **COGS Delta:** $+\$16,026.47$
- **Logistics Disruption Cost Delta:** $+\$469,188.49$
- **Workforce Cost Delta:** $+\$184,212.00$
- **Net Operating Profit Delta:** $-\$642,716.18$
- **Composite Risk Score:** $37.48 / 100$ (`MODERATE RISK`)
- **Decision Category:** `REJECT_RESTRUCTURE`
- **Triggered Action:** `[RULE-04] ACT-FIN-001: Margin Erosion Warning: Rescale Promotional Intensity`

*Historical Disambiguation:*
- $-\$380.5\text{K}$: Explicitly preserved only in `docs/number-lineage.md` as a pedagogical single-facility worked trace (Store 1, $W=100$) for manual classroom verification.
- $-\$823.2\text{K}$: Explicitly archived as an exploratory milestone stress-test featuring extreme overtime ($60\%\text{--}80\%$).

---

## 14. Complete Change Log & File Migration Summary

### A. Files Deleted
**ZERO.** In accordance with Rule 2 ("DO NOT DELETE FIRST"), zero source code, documentation, or historical records were deleted.

### B. Files Moved to `archive/`
1. `docs/phase-3-supply-chain-plan-audit.md` $\to$ `archive/historical-audits/`
2. `docs/phase-4-workforce-audit.md` $\to$ `archive/historical-audits/`
3. `docs/phase-6-scenario-engine-audit.md` $\to$ `archive/historical-audits/`
4. `docs/phase-6-scenario-engine-post-audit.md` $\to$ `archive/historical-audits/`
5. `docs/phase-7-business-impact-audit.md` $\to$ `archive/historical-audits/`
6. `docs/phase-9-final-gate.md` $\to$ `archive/historical-audits/`
7. `docs/phase-9-foundation-and-architecture.md` $\to$ `archive/historical-audits/`
8. `docs/pre-phase-9-research-and-architecture-audit.md` $\to$ `archive/historical-audits/`
9. `docs/reference-project-audit.md` $\to$ `archive/historical-audits/`
10. `docs/data-audit-report.md` $\to$ `archive/historical-audits/`
11. `docs/implementation-quality-gates.md` $\to$ `archive/historical-audits/`
12. `docs/implementation-roadmap.md` $\to$ `archive/historical-audits/`
13. `docs/current-state.md` $\to$ `archive/historical-audits/`
14. `docs/decision-log.md` $\to$ `archive/historical-audits/`
15. `docs/assumptions-and-open-questions.md` $\to$ `archive/historical-audits/`
16. `docs/anti-goals.md` $\to$ `archive/development-notes/`
17. `docs/literature-gap-matrix.md` $\to$ `archive/development-notes/`
18. `docs/ml-evaluation-strategy.md` $\to$ `archive/development-notes/`
19. `docs/ml-problem-definition.md` $\to$ `archive/development-notes/`
20. `docs/research-contract.md` $\to$ `archive/development-notes/`
21. `docs/research-direction.md` $\to$ `archive/development-notes/`
22. `docs/research-system-map.md` $\to$ `archive/development-notes/`
23. `docs/scope.md` $\to$ `archive/development-notes/`
24. `docs/problem-statement.md` $\to$ `archive/development-notes/`
25. `docs/project-overview.md` $\to$ `archive/development-notes/`
26. `docs/xai-strategy.md` $\to$ `archive/development-notes/`
27. `docs/engineering-contract.md` $\to$ `archive/development-notes/`
28. `docs/experimental-design.md` $\to$ `archive/development-notes/`
29. `docs/data-contracts.md` $\to$ `archive/development-notes/`
30. `docs/data-pipeline.md` $\to$ `archive/development-notes/`
31. `docs/business-impact-analysis.md` $\to$ `archive/development-notes/`
32. `docs/scenario-engine.md` $\to$ `archive/development-notes/`
33. `docs/recommendation-engine.md` $\to$ `archive/development-notes/`
34. `docs/frontend-requirements.md` $\to$ `archive/development-notes/`
35. `docs/frontend-research.md` $\to$ `archive/development-notes/`
36. `docs/frontend-architecture.md` $\to$ `archive/development-notes/`
37. `docs/DecisionSphere-Learning-Path.md` $\to$ `archive/development-notes/`
38. `docs/DecisionSphere-Design-Rationale.md` $\to$ `archive/development-notes/`
39. `docs/research-paper-materials/` (14 markdown chapters) $\to$ `archive/development-notes/research-paper-markdown-drafts/`
40. `university_reviews/REVIEW_2/review-2.md` (outdated Phase-6 draft) $\to$ `archive/historical-audits/review-2-phase6-draft.md`

### C. Files Created
1. `paper/DecisionSphere_Research_Paper.tex`: Full IEEEtran LaTeX manuscript.
2. `paper/references.bib`: Verified BibTeX primary citations database.
3. `paper/README.md`: Compilation guide for Overleaf and local environments.
4. `paper/figures/`: High-resolution copies of all 15 publication figures.
5. `paper/tables/`: Modular LaTeX table sources (`datasets.tex`, `model_performance.tex`, `canonical_scenario.tex`).
6. `CITATION.cff`: Standard academic repository citation metadata.
7. `LICENSE`: Official MIT open-source license.
8. `university_reviews/REVIEW_2/requirements.md`: Formal evaluation rubrics mapping.
9. `university_reviews/REVIEW_2/evidence-matrix.md`: Empirical requirement-to-evidence matrix.
10. `university_reviews/REVIEW_2/presentation-outline.md`: Complete 24-slide PPT blueprint.
11. `university_reviews/REVIEW_2/demo-checklist.md`: Step-by-step viva demo runbook.
12. `university_reviews/REVIEW_2/viva-questions.md`: Panel cross-examination defense guide.
13. `university_reviews/REVIEW_2/final-status.md`: Institutional readiness sign-off.
14. `docs/methodology.md`: Unified scientific methodology and ML modeling specification.
15. `archive/README.md`: Index and provenance of all archived development materials.
16. `scripts/reproduce_all.py`: Unified reproducibility validation script.
17. `RELEASE_AUDIT.md`: This comprehensive final release report.

### D. Files Renamed / Consolidated
1. `docs/DecisionSphere-Complete-Project-Guide.md` $\to$ `docs/project-guide.md`
2. `docs/DecisionSphere-Glossary.md` $\to$ `docs/glossary.md`
3. `docs/DecisionSphere-Number-Lineage.md` $\to$ `docs/number-lineage.md`
4. `docs/Frontend-to-Research-Mapping.md` $\to$ `docs/frontend-research-mapping.md`
5. `docs/DecisionSphere-Assumptions-and-Limitations.md` $\to$ `docs/assumptions-limitations.md`
6. `university_reviews/REVIEW 1` $\to$ `university_reviews/REVIEW_1` (standardized without spaces)
7. `university_reviews/REVIEW 2` $\to$ `university_reviews/REVIEW_2` (standardized without spaces)

### E. Files Modified
1. `README.md`: Complete rewrite to provide clean navigation, architecture, quickstart, and reproduction.
2. `tests/test_research_suite.py`: Updated to verify canonical release documentation and IEEE manuscript layout.

### F. Files Preserved (Core & Benchmarks)
- All analytical core packages in `src/` (Invariant).
- All pre-trained model artifacts in `models/` (Invariant).
- All test suites in `tests/` and `backend/tests/`.
- All 16 research notebooks in `notebooks/`.
- All frontend source code in `frontend/`.
- All historical reference archives in `reference/`.
- All university templates (`1 Guidelines...docx`, `3 BCSE497J...docx`, `4 Review 2 PPT Template.pptx`).

### G. Rationale for Changes
- Separates the active runtime system and canonical documentation from point-in-time development notes.
- Eliminates overlapping, redundant documentation without destroying academic evidence.
- Provides publication-grade IEEE LaTeX manuscript assets for academic venues.
- Ensures zero path-escaping bugs by eliminating whitespace in review folder names.
- Guarantees 100% academic reproducibility for external researchers.

---

## 14. Final Sign-Off

The DecisionSphere repository is now transformed into a clean, professional, research-ready, and academically defensible codebase. It stands fully prepared for University Review 2 presentation, viva voce examination, and subsequent IEEE research paper submission.
