# ADR-001: Initial System Architecture and Technology Stack

## Status
**ACCEPTED** (2026-09-05)

## Context
DecisionSphere is a B.Tech capstone project designed to simulate cross-domain enterprise scenarios across demand forecasting, supply chain risk, and workforce attrition. The project requires an architecture that is:
1. Feasible for a 3-student team to implement and demonstrate within academic review deadlines.
2. Technically robust, modular, and reproducible.
3. Capable of low-latency interactive simulation runs for live review panel demonstrations.
4. Academically defensible, avoiding unnecessary operational complexity while maintaining clear component boundaries.

## Decision

We adopt a **modular monolithic full-stack architecture** with a decoupled Python ML pipeline:

1. **Frontend:** React with TypeScript, built using Vite.
   - *Rationale:* Strong type safety, rapid development, rich visualization ecosystem for time-series charts and risk heatmaps, lightweight deployment without server-side rendering complexity.
2. **Backend:** FastAPI (Python 3.13+).
   - *Rationale:* High performance asynchronous REST API, native Pydantic v2 data contract validation, seamless integration with Python ML libraries (`scikit-learn`, `xgboost`, `shap`), automatic OpenAPI/Swagger documentation.
3. **Database:** PostgreSQL with SQLAlchemy ORM.
   - *Rationale:* Standard relational database for structured scenario configurations, simulation run parameters, user metadata, and historical reports.
4. **Machine Learning Pipeline:** Offline Python training with serialized inference artifacts (`.joblib`).
   - *Rationale:* Training complex ML models inside HTTP request handlers causes unacceptably high latency and memory spikes. Decoupling offline training from online inference ensures sub-second simulation response times.
5. **Business Impact & Recommendations:** Deterministic mathematical equations combined with rule-based trigger heuristics and optional LLM narrative synthesis.
   - *Rationale:* Prevents numerical hallucination while preserving transparent, auditable calculations and sophisticated strategic articulation.

## Consequences

### Positive
- **Simplicity & Reliability:** Zero external cluster dependencies (no Kubernetes, no distributed streaming platforms). High reliability during live review presentations.
- **Auditable Traceability:** Clear separation of concerns between data processing, ML inference, scenario orchestration, business impact calculations, and UI presentation.
- **Fast Iteration:** Pydantic schemas enforce strict contracts between frontend and backend while allowing rapid feature additions.

### Negative / Trade-offs
- The entire backend runs in a single process space; vertical scaling is limited to server resources (fully acceptable for laboratory demonstrations and local evaluation).
- Large datasets (DataCo) must be preprocessed and sampled for runtime benchmarks rather than queried live across millions of records.
