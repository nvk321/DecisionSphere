# DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform

[![Academic Project](https://img.shields.io/badge/Course-BCSE497J%20Project--I-blue.svg)](https://vit.ac.in/)
[![SDG Alignment](https://img.shields.io/badge/SDG-9%20Industry%2C%20Innovation%20%26%20Infrastructure-orange.svg)](#)
[![TRL 4](https://img.shields.io/badge/TRL-Level%204%20(Laboratory%20Validated)-brightgreen.svg)](#)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](#)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](#)
[![Next.js 15](https://img.shields.io/badge/Frontend-Next.js%2015%20%2B%20React%2019-black.svg)](#)
[![Tests Passing](https://img.shields.io/badge/Tests-236%20Passing-success.svg)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**DecisionSphere** is an AI-powered decision intelligence platform that allows enterprise leaders to simulate and evaluate hypothetical business decisions across interconnected operational domains **before** real-world capital deployment.

---

## 1. Executive Summary

| Dimension | Specification |
|---|---|
| **Core Problem** | Operational analytics systems operate in isolated silos (sales, logistics, HR), failing to anticipate the cross-domain cascading risks of commercial decisions. |
| **Three ML Domains** | **1. Retail Demand Forecasting** (Rossmann) $\cdot$ **2. Logistics Delivery Risk** (DataCo) $\cdot$ **3. Workforce Attrition** (IBM HR). |
| **Main Innovation** | A 13-stage linear execution pipeline linking calibrated ML models to deterministic managerial accounting ($\Delta \Pi$) and a rule-grounded recommendation engine (RULE-01 to RULE-07). |
| **Anti-Hallucination** | **Zero LLM arithmetic.** All financial metrics and risk scores are calculated deterministically; ML models are calibrated using Sigmoid Platt scaling. |
| **Verified Canonical Result** | $+15.0\%$ Demand Shock with active promo and $40.0\%$ overtime yields $+\$26,710.78$ revenue but triggers $+\$469,188.49$ logistics disruption and $+\$184,212.00$ labor strain $\to$ **Net Profit Delta $-\$642,716.18$** $\to$ **`REJECT_RESTRUCTURE`** (CRS: $37.48$). |

```
Commercial Demand Surge ──> Logistics Delivery Strain ──> Workforce Overtime & Attrition ──> Bottom-Line Profit Collapse
```

---

## 2. System Architecture

```
User Scenario Builder (Hypothetical Levers: ΔD, Promo, SLA, Overtime)
                         │
                         ▼
        FastAPI REST API & Scenario Engine
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   Retail Demand    Supply Chain      Workforce
    Forecasting      Risk Model       Risk Model
  (XGBoost / WAPE) (Calibrated AUC) (Calibrated AUC)
        │                │                │
        └────────────────┼────────────────┘
                         ▼
             Managerial Accounting Engine
    (Realized Revenue, COGS, Logistics Penalty, Overtime Wages)
                         │
                         ▼
        Composite Risk Score & Recommendation Engine
            (Lexicographic Rules RULE-01 to RULE-07)
                         │
                         ▼
      Next.js Interactive Decision Intelligence UI
```

---

## 3. Quick Start

### Prerequisites
- Python 3.13+ with virtual environment tools
- Node.js 20+ and npm
- Git

### Option A: Local Development Environment
```bash
# 1. Clone repository
git clone https://github.com/DecisionSphere/DecisionSphere.git
cd DecisionSphere

# 2. Set up Python backend & analytical core
python -m venv .venv
source .venv/bin/activate       # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Launch FastAPI backend (Port 8000)
uvicorn backend.app.main:app --port 8000 --reload

# 4. In a separate terminal, launch Next.js frontend (Port 3000)
cd frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser to access the dashboard.

### Option B: Docker Container Stack
```bash
docker-compose up --build
```

---

## 4. Repository Directory Structure

```
DecisionSphere/
├── README.md                          # Master navigation & quick start (this file)
├── LICENSE / CITATION.cff             # Academic attribution & open-source licensing
├── requirements.txt                   # Frozen Python dependencies
├── alembic.ini / Dockerfile           # Production containerization assets
│
├── src/                               # [FROZEN] Analytical core (models, scenario, business)
├── models/                            # [FROZEN] Pre-trained serialized estimators & TreeSHAP
│
├── backend/                           # Production FastAPI REST backend (101 unit tests)
│   ├── app/                           # API routes, Pydantic v2 schemas, services, ORM
│   └── tests/                         # Backend integration & route test suite
│
├── frontend/                          # Next.js 15 + React 19 single-page app (35 tests)
│   ├── src/app/                       # 12 static/dynamic routes (Dashboard, Simulate, etc.)
│   └── src/components/                # DecisionHero, FinancialWaterfall, RiskGauge, etc.
│
├── docs/                              # Authoritative system documentation (9 master docs)
│   ├── project-guide.md               # Beginner-friendly comprehensive walkthrough
│   ├── architecture.md                # System component boundaries & execution flow
│   ├── methodology.md                 # Scientific methodology, models, and calibration
│   ├── assumptions-limitations.md     # All modeling assumptions (ASM-001 to 008)
│   ├── reproducibility.md             # End-to-end reproduction instructions
│   ├── glossary.md                    # Epistemic hierarchy & domain terminology
│   ├── frontend-research-mapping.md   # Mathematical trace from UI to backend formulas
│   ├── number-lineage.md              # Reconciled canonical worked numbers
│   └── architecture-decisions/        # Architectural Decision Records (ADR-002 to 006)
│
├── paper/                             # IEEE publication manuscript suite
│   ├── DecisionSphere_Research_Paper.tex # IEEEtran conference manuscript (15 sections)
│   ├── references.bib                 # Verified BibTeX bibliography (12 primary citations)
│   ├── figures/                       # High-resolution 300 DPI publication plots
│   └── README.md                      # Overleaf & local compilation instructions
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
├── artifacts/figures/                 # 15 canonical generated 300 DPI figures
├── data/                              # Dataset manifests & provenance metadata
├── tests/                             # Analytical core & research tests (100 tests)
├── scripts/                           # Execution, auditing, and reproduction utilities
└── archive/                           # Preserved historical development records
```

---

## 5. Automated Testing & Quality Gates

DecisionSphere maintains a **100% passing test record (236/236 tests)**:
```bash
# 1. Analytical core & research suite (100 tests)
pytest tests/

# 2. FastAPI backend & API contracts (101 tests)
pytest backend/tests/

# 3. Frontend unit & component tests (35 tests)
cd frontend && npm test -- --run

# 4. Frontend production static build (12 routes)
cd frontend && npm run build
```

---

## 6. Academic Reproducibility & Research Artifacts

- **Jupyter Research Suite:** All 16 notebooks in `notebooks/` run sequentially without manual intervention.
- **Model Cryptographic Hashes (Gate H):**
  - `demand_model.joblib`: `fb438c03a742202657bb4ef9196ff17e004bc090e99218f02985dc7720f41941`
  - `supply_chain_model.joblib`: `0052e641cf355257abb332703c3e6a46c65e9ab10a975227d83cf77d7e689b59`
  - `workforce_model.joblib`: `4b195c7bee3ab8f4afe75ccd0c75fff0c8e18b9fca88a00305e165a010109918`
- **Canonical Scenario Extraction:**
  ```bash
  python scripts/get_canonical_run_metrics.py
  ```

---

## 7. Limitations & Epistemic Demarcation

1. **Non-Causal Associations:** Machine learning models estimate conditional statistical associations ($P(Y \mid X)$), not causal mechanisms. Cross-domain interactions represent parameterized operational hypotheses.
2. **Benchmark Testbeds:** Models are calibrated on public benchmarks (Rossmann, DataCo, IBM HR) as proof-of-concept testbeds rather than a single enterprise ERP database.
3. **Inelastic Immediate Buffers:** Models assume operational capacity cannot expand instantaneously without incurring contractual delay penalties and overtime wage multipliers.

---

## 8. Academic Governance & Citation

- **Course:** BCSE497J – Project I, School of Computer Science and Engineering (SCOPE), VIT
- **Faculty Guide:** Dr. Suresh A
- **Investigators:** P Naga Venkata Kushal (23BDS0133), P Manjunatha Kumar Tejas (23BCE0584), Jeswanth Reddy Sagabala (23BCE0203)
- **Title Lock Status:** Final and locked since Review 1 (29-07-2026).

If you reference or utilize this work, please cite:
```bibtex
@misc{decisionsphere2026,
  author = {P, Naga Venkata Kushal and P, Manjunatha Kumar Tejas and Jeswanth Reddy, Sagabala and A, Suresh},
  title  = {DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform},
  year   = {2026},
  url    = {https://github.com/DecisionSphere/DecisionSphere}
}
```

---

## 9. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.