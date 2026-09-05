# AGENTS.md — DecisionSphere Engineering & Agent Protocol

This document establishes the mandatory operational rules, architectural contracts, academic constraints, and engineering protocols for all AI agents and human contributors working on **DecisionSphere**.

---

## 1. Project Identity & Governance (LOCKED)

- **Project Title:** `DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform`
- **Course:** `BCSE497J – Project I` (B.Tech Computer Science and Engineering)
- **Institution:** School of Computer Science and Engineering (SCOPE), VIT
- **Faculty Guide:** Dr. Suresh A
- **Team Members:**
  1. P Naga Venkata Kushal (Reg No: 23BDS0133)
  2. P Manjunatha Kumar Tejas (Reg No: 23BCE0584)
  3. Jeswanth Reddy Sagabala (Reg No: 23BCE0203)
- **Title Lock Status:** **FINAL AND LOCKED**. The project title was officially approved and presented during Review 1 (29-07-2026). Per university regulations, **modification of the project title is strictly prohibited**. Under no circumstances may any agent rename or rephrase the title.
- **SDG Alignment:** SDG 9 – Industry, Innovation and Infrastructure
- **Technology Readiness Level (TRL):**
  - Review 1: TRL 2 (Technology Concept Formulated)
  - Review 2 Target: TRL 4 (Component / System Validation in Laboratory Environment — Functional End-to-End Prototype, 60–75% Implementation)

---

## 2. Core Project Concept

DecisionSphere is an AI-powered strategic decision support platform that enables organizational decision-makers to simulate and evaluate hypothetical business decisions across multiple interconnected organizational domains **before** real-world implementation.

### The Problem Addressed
In modern enterprises, operational analytics systems exist in isolated organizational silos (e.g., demand forecasting isolated in sales, supply chain risk isolated in logistics, employee turnover isolated in HR). However, strategic business decisions inherently produce cascading cross-domain effects:
- A promotional campaign increases demand $\rightarrow$ elevates inventory requirements $\rightarrow$ exacerbates logistics and supplier delay risk $\rightarrow$ increases operational workload $\rightarrow$ increases employee overtime and turnover risk $\rightarrow$ alters operational costs and bottom-line profitability.

### The Systemic Workflow
```
User Scenario Creation (What-if parameters)
                  ↓
          Scenario Builder
                  ↓
           Scenario Engine
                  ↓
   ┌──────────────┼──────────────┐
   ▼              ▼              ▼
Demand       Supply Chain   HR Workforce
Forecasting  Risk Analysis  Risk Analysis
   │              │              │
   └──────────────┼──────────────┘
                  ↓
       Business Impact Analysis
   (Revenue, Cost, Risk Propagation)
                  ↓
        Recommendation Engine
   (Decision Trade-offs & Actions)
                  ↓
         Decision Dashboard
```

---

## 3. Scope & Anti-Goals

### In-Scope
1. **Data Ingestion & Modular Processing:** Loading, validating, cleaning, and preprocessing multi-source datasets (Retail Demand, DataCo Supply Chain, IBM HR Attrition).
2. **Predictive Analytics Modules:**
   - Retail Demand Forecasting (time-series predictive modeling).
   - Supply Chain Delivery Risk Classification (predicting shipment delays / late delivery risks).
   - HR Workforce Attrition Classification (predicting employee turnover risk).
3. **Explainable AI (XAI):** Grounded feature importance and SHAP explanations for predictive models.
4. **Scenario Engine:** Structured translation and propagation of user-defined hypothetical shocks (e.g., $+30\%$ demand, $+5$ days delay, $+10\%$ attrition).
5. **Business Impact Engine:** Transparent, traceable mathematical formulas linking operational risks to financial metrics (revenue, cost, inventory risk, workforce risk score).
6. **Recommendation Engine:** Evidence-grounded synthesis of strategic actions based on computed risks and trade-offs.
7. **Full-Stack Application:** FastAPI backend, React + TypeScript frontend, PostgreSQL database for scenario and run persistence.

### Anti-Goals (What DecisionSphere Is NOT)
- **NOT an isolated ML demo:** It is NOT merely a demand forecasting notebook, an HR attrition script, or a supply chain classifier.
- **NOT an LLM Chatbot:** It is NOT a conversational agent or generic chat interface. LLMs (if used) are restricted strictly to narrative synthesis of deterministic metrics.
- **NOT an ERP / Enterprise Microservices Sprawl:** No Kubernetes, no Kafka, no distributed clusters, no redundant microservices.
- **NO Fabricated Numbers:** No LLM is ever permitted to invent, extrapolate, or estimate numerical risks or financial forecasts without deterministic formulas or trained models.

---

## 4. Source of Truth Hierarchy

When resolving conflicts, all agents must adhere to this strict precedence order:

1. **LEVEL 1 — Official University Requirements & Deadlines** (VIT BCSE497J Guidelines, Rubrics, Official Templates).
2. **LEVEL 2 — Finalized Review 1 Decisions & Guide Approvals** (Locked Title, Approved Scope, Guide Directives).
3. **LEVEL 3 — Project Documentation** (`docs/`, `AGENTS.md`, `university_reviews/reviews-overview.md`).
4. **LEVEL 4 — Verified Code & Unit Tests** (`src/`, `backend/`, `frontend/`, `tests/`).
5. **LEVEL 5 — Agent Hypotheses & Assumptions** (Must always be validated and marked as `ASSUMPTION` until confirmed).

*Rule: If code or agent output contradicts documentation or university guidelines, the higher level prevails. Never silently rewrite higher-level documentation to fit ad-hoc code.*

---

## 5. Technology Stack & Architectural Constraints

- **Frontend:** React (Vite) + TypeScript + Vanilla CSS / modern CSS design tokens + Charting library (e.g., Recharts / Chart.js).
- **Backend:** FastAPI (Python 3.13+) with Pydantic v2 data contracts.
- **Database:** PostgreSQL for scenarios, simulation runs, parameter histories, and user reports.
- **Data & ML:** Python (`pandas`, `numpy`, `scikit-learn`, `scipy`, `xgboost`, `shap`, `matplotlib`, `seaborn`).
- **Environment & Dependency Management:** Virtual environment (`.venv`) using `pip` tracked in `requirements.txt`.
- **Architectural Separation:**
  - `data/`: Raw and processed datasets (never commit huge raw CSVs).
  - `notebooks/`: Exploratory Data Analysis (EDA) and experimental model benchmarking only.
  - `src/`: Reusable, modular Python packages (`src/data/`, `src/models/`, `src/scenario/`, `src/business/`, `src/recommendation/`).
  - `backend/`: FastAPI API routes, Pydantic schemas, database models, service orchestrators.
  - `frontend/`: React SPA components, state management, API clients, interactive charts.
  - `tests/`: Automated unit and integration tests.

---

## 6. Machine Learning & Modeling Protocol

1. **No Data Leakage:**
   - For time-series data: **Strict chronological split** (train on past, validate on future). Random shuffling is strictly prohibited.
   - For tabular classification: Split data into Train/Validation/Test **before** fitting transformers, encoders, or scalers.
2. **Evidence-Based Baselines:**
   - Always establish a naive baseline (e.g., moving average/historical mean for forecasting; majority class/logistic regression for classification) before evaluating complex models.
3. **Comprehensive Evaluation Metrics:**
   - Time Series: MAE, RMSE, MAPE / sMAPE.
   - Imbalanced Classification: ROC-AUC, PR-AUC, F1-score, Precision, Recall, Confusion Matrix. Accuracy alone is unacceptable for imbalanced datasets.
4. **Offline Training / Inference Only:**
   - Models are trained offline and serialized (`.joblib` or `.pkl`).
   - The FastAPI backend loads saved model artifacts into memory for inference; model training inside request handlers is forbidden.
5. **Explainability (XAI):**
   - Use SHAP or tree-based feature importances.
   - Model explanations must be mathematically grounded in the actual model outputs.

---

## 7. Dataset Management & Provenance

1. **Reference Folder Integrity:**
   - The `reference/` folder contains historical archives, ZIPs, notebooks, and reference materials.
   - **Do NOT modify, delete, or overwrite files in `reference/`**.
   - Treat `reference/` as read-only historical source material.
2. **Data Audit Requirement:**
   - Before modeling, an explicit audit must be performed on candidate datasets (Retail Demand, DataCo Supply Chain, IBM HR).
   - Document row counts, column types, missingness, target distributions, temporal ranges, potential leakage, and limitations.
3. **No Synthetic Hallucination:**
   - Never invent columns or features that do not exist in the source datasets.
   - If a business metric requires an operational assumption because a variable is missing, explicitly document it as a heuristic assumption in `docs/assumptions-and-open-questions.md`.

---

## 8. Scenario Engine & Business Impact Protocol

1. **Scenario Parameters:**
   - Must be strongly typed and validated (e.g., `demand_shock_pct: float`, `supplier_delay_days: int`, `attrition_rate_delta: float`).
2. **Traceable Impact Formulas:**
   - Every business impact calculation must be traceable to a deterministic formula:
     $$\Delta \text{Revenue} = \text{Base Revenue} \times (1 + \text{Demand Shock}) \times (1 - \text{Fulfillment Loss})$$
     $$\Delta \text{Cost} = \text{Supply Chain Disruption Cost} + \text{Overtime/Attrition Cost} + \text{Base Cost}$$
3. **Clear Demarcation:**
   - The UI and API must explicitly distinguish between:
     - Historical Baseline Observations
     - Machine Learning Forecasts / Inferences
     - User-Defined Scenario Levers
     - Computed Business Impacts

---

## 9. Conceptual Agent Roles & Responsibilities

All AI agents assisting in this repository must operate under one of the following defined personas:

| Agent Role | Scope & Responsibilities |
|---|---|
| **Project Architect** | System structure, design boundaries, source of truth maintenance, ADR authoring, preventing architectural drift. |
| **Data / ML Engineer** | Dataset audits, feature engineering, pipeline validation, baseline modeling, XAI generation, serialized model artifact management. |
| **Backend Engineer** | FastAPI endpoints, Pydantic schemas, database models (PostgreSQL/SQLAlchemy), model inference services, scenario orchestration. |
| **Frontend Engineer** | React + TypeScript UI, scenario builder components, risk matrices, interactive time-series charts, responsive UX. |
| **QA / Test Engineer** | Deterministic unit tests (data transforms, formulas, API validation), model sanity checks, edge-case validation. |
| **Academic / Documentation Agent** | Review reports, PPT alignment with official university templates, IEEE reference validation, academic defensibility. |

---

## 10. Anti-Hallucination & Verification Protocol

- **Never invent citations or papers.** Use verified papers documented in Review 1 and legitimate peer-reviewed literature.
- **Never claim an untested feature works.** Run the code or write an automated test.
- **Never claim a model achieves high accuracy without empirical logs.**
- **Never invent dataset columns or foreign keys.**
- **When uncertain:** STOP. Mark the ambiguity as `[TO BE VERIFIED]` or `[ASSUMPTION]`, inspect the evidence, and log it in `docs/assumptions-and-open-questions.md`.

---

## 11. Git Strategy & Workflow

- Every major stage must be accompanied by an atomic, conventional commit:
  - `chore: ...` (environment, setup, configs)
  - `docs: ...` (documentation, ADRs, review deliverables)
  - `feat: ...` (new feature, pipeline, model, API, component)
  - `test: ...` (unit tests, integration suites)
  - `refactor: ...` (code cleanup without behavior changes)
- Never make vague commit messages like "updates", "fixes", or "wip".

---

## 12. Definition of Done (DoD)

A task or feature is considered **Done** if and only if:
1. Requirements and technical rationale are documented in `docs/`.
2. Clean, modular code is written following project conventions.
3. Automated unit or integration tests pass.
4. Input validation and error handling are implemented.
5. No credentials, secrets, or massive raw datasets are tracked in Git.
6. The state changes are reflected in `docs/current-state.md`.
7. An atomic Git commit has been executed.
