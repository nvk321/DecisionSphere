# DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform

[![Academic Project](https://img.shields.io/badge/Course-BCSE497J%20Project--I-blue.svg)](https://vit.ac.in/)
[![SDG Alignment](https://img.shields.io/badge/SDG-9%20Industry%2C%20Innovation%20%26%20Infrastructure-orange.svg)](#)
[![TRL](https://img.shields.io/badge/TRL-Level%202%20%E2%86%92%20Target%204-green.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](#)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](#)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB.svg)](#)

DecisionSphere is an AI-powered strategic planning and risk evaluation platform designed to help enterprise decision-makers evaluate the cross-domain impacts of strategic business decisions **before** real-world implementation.

---

## 1. Project Metadata & Governance (LOCKED)

- **Project Title:** `DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform`
- **Course Code & Title:** BCSE497J – Project I
- **Department:** School of Computer Science and Engineering (SCOPE)
- **Institution:** Vellore Institute of Technology (VIT)
- **Faculty Guide:** Dr. Suresh A
- **Student Investigators:**
  - P Naga Venkata Kushal (Reg No: 23BDS0133)
  - P Manjunatha Kumar Tejas (Reg No: 23BCE0584)
  - Jeswanth Reddy Sagabala (Reg No: 23BCE0203)
- **Title Lock:** The project title was finalized and approved in **Review 1 (29-07-2026)** and is strictly locked.

---

## 2. Core Project Concept

Instead of evaluating business departments in isolated silos or relying solely on retrospective analytics, DecisionSphere allows leadership to construct hypothetical **"what-if" operational scenarios** and evaluate their cascading systemic consequences:

$$\text{Promotional Demand Surge} \longrightarrow \text{Supply Chain Shipping Delays} \longrightarrow \text{Workforce Overtime \& Attrition} \longrightarrow \text{Bottom-Line Profit Impact}$$

### Conceptual Workflow
```
User Scenario Builder (Hypothetical Levers)
                 │
                 ▼
          Scenario Engine
                 │
   ┌─────────────┼─────────────┐
   ▼             ▼             ▼
 Demand     Supply Chain   Workforce
Forecast    Risk Model     Risk Model
   │             │             │
   └─────────────┼─────────────┘
                 ▼
      Business Impact Analysis
   (Revenue, Penalties, Margins)
                 │
                 ▼
       Recommendation Engine
   (Explainable Mitigations)
                 │
                 ▼
        Decision Dashboard
```

---

## 3. System Architecture & Tech Stack

- **Frontend Client:** React + TypeScript (Vite), Vanilla CSS design system, Interactive charting (Recharts / Chart.js).
- **Backend Services:** FastAPI (Python 3.13+) with Pydantic v2 data contracts.
- **Relational Database:** PostgreSQL (SQLAlchemy ORM) for scenarios, simulation runs, and impact logs.
- **Data & Machine Learning:** Python (`pandas`, `numpy`, `scikit-learn`, `scipy`, `xgboost`, `shap`).
- **Explainability (XAI):** TreeSHAP for global and local risk feature attribution.

---

## 4. Repository Structure

```
DecisionSphere/
├── AGENTS.md                  # Mandatory AI agent operational protocol & rules
├── README.md                  # Master project documentation
├── requirements.txt           # Python dependencies (UTF-8 normalized)
├── .gitignore                 # Version control exclusion rules
│
├── docs/                      # Architectural source-of-truth documents
│   ├── project-overview.md
│   ├── problem-statement.md
│   ├── scope.md
│   ├── anti-goals.md
│   ├── architecture.md
│   ├── data-pipeline.md
│   ├── data-contracts.md
│   ├── ml-problem-definition.md
│   ├── ml-evaluation-strategy.md
│   ├── xai-strategy.md
│   ├── scenario-engine.md
│   ├── business-impact-analysis.md
│   ├── recommendation-engine.md
│   ├── implementation-roadmap.md
│   ├── current-state.md
│   ├── assumptions-and-open-questions.md
│   └── architecture-decisions/
│       └── ADR-001-initial-architecture.md
│
├── university_reviews/        # Official academic review management
│   ├── reviews-overview.md    # Master university schedule & rubrics
│   ├── REVIEW 1/              # Review 1 presentation, approved scope & notes
│   │   ├── Review 1 - DecisionSphere.pptx
│   │   └── review-1.md
│   └── REVIEW 2/              # Review 2 guidelines, report template & checklist
│       ├── 1 Guidelines Student Project-1 review-2.docx
│       ├── 3 BCSE497J Project I Report - Template.docx
│       ├── 4 Review 2 PPT Template.pptx
│       └── review-2.md
│
├── data/                      # Data layer (raw datasets gitignored)
│   ├── raw/
│   ├── processed/
│   └── README.md
│
└── reference/                 # Immutable historical reference archives & benchmarks
```

---

## 5. Development Status & Next Steps

- **Current Milestone:** Phase 0 (Project Initialization & Foundation) — **COMPLETED**
- **Target Review:** Review 2 (Scheduled September 2026, 60–75% functional prototype)
- **Immediate Next Task (Phase 1):** Execute automated dataset profiling and audit across candidate retail demand, DataCo supply chain, and IBM HR datasets to finalize features, prevent lookahead leakage, and select the primary demand forecasting dataset.

---

## 6. Engineering & Academic Standards

All contributors and AI agents must strictly follow the protocols established in [AGENTS.md](file:///d:/Projects/DecisionSphere/AGENTS.md):
1. **Source of Truth Hierarchy:** University Guidelines > Guide Approvals > Project Documentation > Verified Code > Hypotheses.
2. **Anti-Hallucination:** No fabricated citations, accuracy claims, or non-existent dataset attributes.
3. **Traceability:** All financial and operational impact figures are derived from deterministic equations.
4. **Git Discipline:** Conventional atomic commits (`feat:`, `docs:`, `chore:`, `test:`).