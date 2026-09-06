# DecisionSphere — Implementation Quality Gates & Tooling Strategy

**Document Status:** FROZEN QUALITY GATES (PHASE 9+)  
**Date:** September 5, 2026  
**Governing Authority:** DecisionSphere Engineering Protocol (`AGENTS.md`)  
**Target Milestone:** BCSE497J Review 2 / TRL 4 Functional Prototype  

---

## 1. Development Tooling Stack

| Tool | Category | Status | Role in DecisionSphere |
|---|---|---|---|
| **`pytest`** | Testing | **MUST HAVE** | Test runner for 93 analytical tests + backend endpoint integration tests. |
| **`pydantic v2`** | Validation | **MUST HAVE** | Enforces strongly typed schemas with `extra="forbid"` on all API contracts. |
| **`httpx`** | API Client | **MUST HAVE** | Async HTTP client for integration testing FastAPI endpoints. |
| **`ruff`** | Linting & Formatting | **MUST HAVE** | Fast Python linter and formatter enforcing PEP 8 and clean imports. |
| **`mypy` / `pyright`** | Static Typing | **SHOULD HAVE** | Static type checking to catch type inconsistencies between DTOs and models. |
| **`coverage`** | Test Coverage | **SHOULD HAVE** | Generates coverage reports ensuring $>85\%$ backend service coverage. |
| **`pre-commit`** | Git Hooks | **SHOULD HAVE** | Pre-commit hook preventing unformatted code or secrets from being committed. |
| **`Celery` / `Redis`** | Task Queue | **FORBIDDEN** | Unnecessary distributed complexity; rejected in favor of threadpools. |
| **`Kafka` / `RabbitMQ`** | Message Broker | **FORBIDDEN** | Microservice sprawl; rejected in favor of modular monolith. |
| **`Kubernetes`** | Orchestration | **FORBIDDEN** | Infrastructure overkill; rejected in favor of Docker Compose. |

---

## 2. Phase 9 Implementation Quality Gates (Gates A to K)

To ensure zero architectural regression and maintain publication-grade rigor, every milestone must pass its designated quality gates:

### Gate A: Analytical Invariance Gate
- **Requirement:** All 93 existing automated tests in `tests/` must pass with 100% success.
- **Verification Command:**
  ```powershell
  & .venv\Scripts\python.exe -m pytest tests -q
  ```
- **Threshold:** `93 passed, 0 failed`.

### Gate B: Model Hash Invariance Gate
- **Requirement:** The SHA-256 byte hashes of all three serialized model files must match their exact frozen fingerprints.
- **Verification Command:**
  ```powershell
  Get-FileHash models\demand\demand_model.joblib, models\supply_chain\supply_chain_model.joblib, models\workforce\workforce_model.joblib -Algorithm SHA256
  ```
- **Frozen Fingerprints:**
  - Demand: `FB438C03A742202657BB4EF9196FF17E004BC090E99218F02985DC7720F41941`
  - Supply Chain: `0052E641CF355257ABB332703C3E6A46C65E9AB10A975227D83CF77D7E689B59`
  - Workforce: `4B195C7BEE3AB8F4AFE75CCD0C75FFF0C8E18B9FCA88A00305E165A010109918`

### Gate C: Database Migration Idempotency Gate
- **Requirement:** Alembic migrations must execute cleanly in both directions without table or constraint corruption.
- **Verification Command:**
  ```bash
  alembic upgrade head && alembic downgrade base && alembic upgrade head
  ```
- **Threshold:** Zero SQL/DDL errors; idempotent schema reconstruction.

### Gate D: Database Relational Constraints Gate
- **Requirement:** Foreign keys, unique constraints, and cascade deletes must be strictly enforced by PostgreSQL.
- **Test Target:** `backend/tests/test_db_constraints.py` verifying that deleting a scenario cascades to its versions and that duplicate version numbers raise integrity errors.

### Gate E: API Schema Validation Gate
- **Requirement:** Inbound payloads with missing fields, out-of-bounds parameters, or extraneous keys (`extra="forbid"`) must be rejected with HTTP 422.
- **Test Target:** `backend/tests/test_api_validation.py`.

### Gate F: Transaction Atomicity Gate
- **Requirement:** A simulated analytical exception mid-simulation must roll back the database transaction, leaving zero partial or orphaned run records.
- **Test Target:** `backend/tests/test_simulation_atomicity.py`.

### Gate G: Version Immutability Gate
- **Requirement:** Modifying scenario levers must create an immutable `ScenarioVersion` row with an incremented version number, leaving prior versions unchanged.
- **Test Target:** `backend/tests/test_scenario_versioning.py`.

### Gate H: Provenance Signature Tuple Gate
- **Requirement:** Every completed simulation run must persist all 8 elements of $\Sigma_{\text{run}}$:
  $$\Sigma_{\text{run}} = \left\langle \text{ScenarioVerID}, \text{ArtifactHashes}, \text{PolicyVerID}, \text{GitCommitHash}, \text{AppVersion}, \text{PythonVersion}, \text{MigrationRevision}, \text{Timestamp} \right\rangle$$
- **Test Target:** `backend/tests/test_provenance.py`.

### Gate I: Model Integrity Failure Gate
- **Requirement:** If an ML model file is missing or its SHA-256 hash fails, the backend must refuse simulation execution and return HTTP 503 Service Unavailable with a structured error payload.
- **Test Target:** `backend/tests/test_model_integrity_failure.py`.

### Gate J: End-to-End Simulation Execution Gate
- **Requirement:** Full simulation lifecycle via HTTP: Create Scenario $\rightarrow$ Run Simulation $\rightarrow$ Fetch Results $\rightarrow$ Verify Financials & Recommendations.
- **Test Target:** `backend/tests/test_simulation_e2e.py`.

### Gate K: Frontend Interaction & Debounce Gate
- **Requirement:** Scenario builder input sliders must debounce API calls by 300ms, and all displayed metrics must render their epistemic tier badges.
- **Test Target:** Vitest component tests in `frontend/src/__tests__/`.

---

## 3. Milestone Gate Matrix

| Phase 9 Milestone | Name | Prerequisite Gates | Milestone Acceptance Gates |
|---|---|---|---|
| **9.0** | Foundation & Environment Hardening | None | Gate A, Gate B |
| **9.1** | Database Engine & Models | Milestone 9.0 | Gate D |
| **9.2** | Alembic Migrations Setup | Milestone 9.1 | Gate C |
| **9.3** | Application Services Layer | Milestone 9.2 | Gate F, Gate G |
| **9.4** | Pydantic v2 Schemas & API DTOs | Milestone 9.3 | Gate E |
| **9.5** | FastAPI Route Controllers | Milestone 9.4 | Gate H, Gate I |
| **9.6** | Backend Automated Test Suite | Milestone 9.5 | Gate J, Gate A (Full Regression) |
| **9.7** | Docker & Docker Compose Setup | Milestone 9.6 | Container healthcheck & e2e curl |
