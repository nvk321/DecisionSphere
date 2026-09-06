# DecisionSphere — Final Engineering Governance Contract

**Document Status:** FROZEN ENGINEERING CONTRACT (PHASE 9+)  
**Date:** September 5, 2026  
**Governing Authority:** DecisionSphere Engineering Protocol (`AGENTS.md`)  
**Target Milestone:** BCSE497J Review 2 / TRL 4 Functional Prototype  

---

## 1. Core Architecture Principles

1. **Analytical Core Isolation:**
   The analytical packages (`src/data/`, `src/models/`, `src/scenario/`, `src/business/`, `src/recommendation/`) are pure, framework-agnostic Python modules.
   - They MUST NOT import FastAPI, Starlette, SQLAlchemy, Alembic, or database drivers.
   - They MUST remain testable directly with `pytest` without a running database or server.
2. **Decoupled Modular Monolith:**
   All services run in a single process space. Inter-module communication occurs via in-memory function calls and strongly typed Pydantic models.
3. **Synchronous CPU-Bound ML Execution:**
   All CPU-intensive analytical executions are delegated to Starlette worker threadpools via `run_in_threadpool`. The FastAPI event loop must never be blocked by analytical computation.
4. **Offline ML Inference Only:**
   Models are trained offline, serialized as `.joblib` files, and loaded read-only into memory at application boot. Zero model training inside request handlers.

---

## 2. Dependency Rules

1. **Python Dependencies (`requirements.txt`):**
   - Core Web: `fastapi>=0.115.0`, `uvicorn[standard]>=0.30.0`
   - Database: `sqlalchemy>=2.0.30`, `alembic>=1.13.0`, `psycopg2-binary>=2.9.9`
   - Data & Settings: `pydantic>=2.7.0`, `pydantic-settings>=2.4.0`
   - Testing: `pytest>=8.0.0`, `httpx>=0.28.1`
   - Data & ML: `numpy`, `pandas`, `scipy`, `scikit-learn`, `xgboost`, `shap`, `joblib`
2. **Prohibited Dependencies:**
   No Celery, Redis, Kafka, RabbitMQ, PySpark, Ray, or distributed task queues.

---

## 3. Persistence Rules (PostgreSQL 16)

1. **System of Record Scope:**
   PostgreSQL stores relational business records: `scenarios`, `scenario_versions`, `assumption_policies`, `simulation_runs`, `domain_predictions`, `financial_results`, `financial_line_items`, `recommendation_results`, `strategic_actions`, and `audit_records`.
2. **Forbidden Database Bloat:**
   - Serialized ML models (`.joblib`) MUST NOT be stored in PostgreSQL.
   - Full 180k-row benchmark DataFrames MUST NOT be stored in PostgreSQL.
3. **Immutability & Version Binding:**
   - `scenario_versions` and `assumption_policies` are strictly immutable.
   - `simulation_runs` bind to specific foreign keys of `scenario_versions` and `assumption_policies`. Modifying scenario levers or policy parameters generates a new version row.
4. **Transaction Atomicity:**
   A simulation run execution and all its related child records (`domain_predictions`, `financial_results`, `recommendations`, `audit_records`) are committed inside a single database transaction. If any step fails, the entire transaction is rolled back.

---

## 4. API Design Rules

1. **Schema Enforcement:**
   - All Request and Response DTOs MUST be Pydantic v2 schemas.
   - Request schemas MUST enforce `model_config = ConfigDict(extra="forbid")`.
2. **DTO / Domain / ORM Separation:**
   - API schemas in `backend/app/schemas/` are distinct from ORM entities in `backend/app/models/` and domain models in `src/*/schema.py`.
   - SQLAlchemy ORM models MUST NEVER be returned directly from route handlers.
3. **Epistemic Tagging:**
   Every metric in an API response MUST include its `epistemic_tier` (`OBSERVED`, `PREDICTED`, `ASSUMED`, `PROPAGATED`, `CALCULATED`, `RECOMMENDED`).
4. **Correlation IDs:**
   Every incoming HTTP request MUST receive an `X-Request-ID` header, propagated through structured JSON logs and audit records.
5. **Error Contract:**
   All 4xx/5xx responses MUST adhere to the standardized error schema containing `error_code`, `message`, `details`, and `request_id`.

---

## 5. Security & Configuration Rules

1. **Configuration via Environment:**
   All configuration is managed via `pydantic-settings` (`backend/app/core/config.py`).
2. **Zero Secrets in Version Control:**
   Database passwords, API keys, and secret tokens MUST be read from `.env` (with `.env.example` committed).
3. **SQL Injection Prevention:**
   100% of database interactions MUST use SQLAlchemy 2.0 ORM expressions or parameterized queries. Raw unescaped SQL strings are strictly prohibited.
4. **CORS Whitelist:**
   CORS is restricted to explicitly configured frontend origins (`http://localhost:3000`, `http://127.0.0.1:3000`).

---

## 6. Testing Rules

1. **Base Regression Gate:**
   All 93 analytical tests in `tests/` MUST continue passing with 100% success on every commit.
2. **Model Hash Invariance Gate:**
   SHA-256 byte hashes of all three model files MUST be verified and match exact frozen fingerprints before tests run.
3. **Migration Idempotency Gate:**
   `alembic upgrade head` $\rightarrow$ `alembic downgrade base` $\rightarrow$ `alembic upgrade head` MUST execute cleanly without data corruption.
4. **API Integration Testing:**
   All backend endpoints MUST be tested using `httpx.AsyncClient`, verifying status codes, schema validation, transaction rollbacks, and error payloads.

---

## 7. Provenance Rules

Every completed simulation run MUST persist an immutable Provenance Signature Tuple:

$$\Sigma_{\text{run}} = \left\langle \text{ScenarioVerID}, \text{ArtifactHashes}, \text{PolicyVerID}, \text{GitCommitHash}, \text{AppVersion}, \text{PythonVersion}, \text{MigrationRevision}, \text{Timestamp} \right\rangle$$

This ensures that months later, an evaluator can reload the exact run parameters and reproduce identical financial line items and strategic recommendations.

---

## 8. Frontend UX & Visualization Rules

1. **Decision-Support First:**
   The frontend is NOT a CRUD table viewer. The UI is designed around the executive decision journey: Scenario Selection $\rightarrow$ Lever Tuning $\rightarrow$ Simulation $\rightarrow$ Decision Banner $\rightarrow$ Financial Waterfall $\rightarrow$ Risk Breakdown $\rightarrow$ Strategic Mitigations $\rightarrow$ Sensitivity Analysis $\rightarrow$ Audit Trace.
2. **Epistemic Visual Badging:**
   Every displayed metric MUST visually display its epistemic tier. An assumed or propagated value must NEVER be styled as an observed empirical fact.
3. **Restrained Design Language:**
   Dark executive theme (`#0B0F19`), clean typography (Inter / Outfit), tabular numeric alignment for financial columns, and meaningful status accents (`#EF4444`, `#F59E0B`, `#10B981`, `#6366F1`). Zero gratuitous clutter or decorative animations.

---

## 9. Docker Deployment Rules

1. **3-Container Architecture:**
   The system deploys strictly as:
   - `postgres`: PostgreSQL 16 Alpine with named volume `decision_pgdata`.
   - `backend`: FastAPI with non-root user (`appuser:10001`), healthcheck probe, and read-only model mounts.
   - `frontend`: React SPA built with Vite and served statically via Nginx with SPA routing fallback.
2. **Startup Ordering:**
   The backend container runs database migrations (`alembic upgrade head`) automatically on startup before launching Uvicorn.

---

## 10. Performance Constraints

1. **Simulation Latency:**
   Complete multi-domain simulation execution (Phases 6–8) MUST complete in $< 500\text{ms}$ on standard commodity hardware.
2. **Memory Footprint:**
   Benchmark reference DataFrames loaded into memory at startup MUST NOT exceed $150\text{MB}$ RAM total. Redundant deep copies during concurrent requests are strictly forbidden.
