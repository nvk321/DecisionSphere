# DecisionSphere — Implementation Decision Log

This log records chronological engineering events, dependency updates, and implementation details for each milestone, complementing the formal Architecture Decision Records (ADRs).

---

## Milestone 9.0: Foundation & Environment Hardening

**Date:** September 5, 2026  
**Status:** **COMPLETED & VERIFIED**  
**Git Baseline Commit:** `13f6c0f017fab043f61397e9570bee7de6e97017`  
**Quality Gates Status:** **ALL GATES PASS (9.0-A through 9.0-I)**  

### 1. Objectives Achieved
1. Established the backend foundation package structure under `backend/`:
   ```
   backend/
   ├── __init__.py
   ├── app/
   │   ├── __init__.py
   │   ├── main.py
   │   └── core/
   │       ├── __init__.py
   │       ├── config.py
   │       ├── logging.py
   │       ├── errors.py
   │       └── security.py
   └── tests/
       ├── __init__.py
       ├── test_config.py
       ├── test_logging.py
       └── test_app_foundation.py
   ```
2. Implemented centralized, typed configuration (`backend/app/core/config.py`) using `pydantic-settings`:
   - All filesystem paths (`models_dir`, `data_dir`, etc.) resolve relative to authoritative `PROJECT_ROOT`, guaranteeing immunity to working directory drifts.
   - Authoritative registry of the three frozen machine learning models with exact SHA-256 byte hashes.
   - Self-verification probe `settings.verify_model_artifacts()` testing file existence and cryptographic hashes.
3. Implemented structured, production-ready logging (`backend/app/core/logging.py`):
   - `StructuredJsonFormatter` formatting log events as JSON with UTC ISO 8601 timestamps, log level, logger name, correlation ID, and exception traces.
   - Automatic regex-based redaction of sensitive credentials (`password`, `token`, `secret`, `api_key`).
   - Context variable `request_id_ctx` propagating correlation IDs across async task contexts.
4. Implemented `CorrelationIdMiddleware` and application factory (`backend/app/main.py`):
   - Extracts incoming `X-Request-ID` or generates a unique `req-{uuid}`.
   - Binds correlation ID to logging context and appends `X-Request-ID` and `X-Response-Time-MS` to all HTTP responses.
   - Configures CORS middleware for client origins (`localhost:3000`, `localhost:5173`).
   - Serves foundation liveness probe (`GET /api/v1/health`) and model verification probe (`GET /api/v1/models/status`).
   - Application instantiates cleanly without requiring a live PostgreSQL connection.
5. Implemented centralized exception handling (`backend/app/core/errors.py`):
   - Uniform error contract: `{"error": {"code": "...", "message": "...", "request_id": "...", "details": {...}}}`.
   - Standard domain exceptions: `AppException`, `ModelIntegrityError`, `ModelNotFoundError`, `EntityNotFoundError`, `ValidationAppError`, `ConfigurationError`.
   - Production error shielding: unhandled exceptions log full traces internally with `request_id` while returning a generic message to clients.
6. Implemented extensible security boundary (`backend/app/core/security.py`):
   - `verify_api_key` dependency verifying `X-API-Key` when configured; permits free pass-through in development mode without premature OAuth/JWT bloat.

### 2. Dependencies Added
- `fastapi` (0.141.1): Core REST framework.
- `uvicorn[standard]` (0.52.4): High-performance ASGI server.
- `pydantic-settings` (2.15.0): Environment variable configuration.
- Synchronized into `requirements.txt`.

### 3. Verification & Quality Gates Summary

| Gate | Requirement | Verification Target | Result |
|---|---|---|---|
| **Gate 9.0-A** | Core Analytical Regression | `pytest tests -q` | **PASS** (93 passed, 0 failed in 24.86s) |
| **Gate 9.0-B** | Backend Import | `from backend.app.main import app, create_app` | **PASS** (`test_gate_9_0_b_backend_import`) |
| **Gate 9.0-C** | Application Startup | App instantiates without PostgreSQL | **PASS** (`test_gate_9_0_c_application_startup_without_postgres`) |
| **Gate 9.0-D** | Centralized Configuration | Loads defaults & respects environment overrides | **PASS** (`test_settings_default_values`, `test_settings_env_override`) |
| **Gate 9.0-E** | Path Resolution | Paths resolve to `PROJECT_ROOT` regardless of cwd | **PASS** (`test_path_resolution_independent_of_cwd`) |
| **Gate 9.0-F** | Artifact Integrity | All 3 model SHA-256 signatures match | **PASS** (`test_model_artifact_verification_success`) |
| **Gate 9.0-G** | Correlation ID Tracking | `X-Request-ID` generated or echoed | **PASS** (`test_gate_9_0_g_correlation_id_*`) |
| **Gate 9.0-H** | Error Contract Shape | Uniform error JSON structure on 404 & exceptions | **PASS** (`test_gate_9_0_h_error_contract_*`) |
| **Gate 9.0-I** | Analytical Invariance | No files under `src/` or `models/` modified | **PASS** (Git status confirmed zero modifications) |

### 4. Overall Test Execution
- **Core Analytical Regression Suite:** 93 passed, 0 failed in 24.86s.
- **Backend Foundation Suite:** 19 passed, 0 failed in 0.65s.
- **Total Combined Tests:** **112 passed, 0 failed.**

---

## Milestone 9.1: Database Engine & SQLAlchemy 2.0 Models

**Date:** September 5, 2026  
**Status:** **COMPLETED & VERIFIED**  
**Quality Gates Status:** **ALL GATES PASS (Gate D, Analytical & Hash Invariance)**  

### 1. Objectives Achieved
1. Established database session and engine infrastructure under `backend/app/db/`:
   - `backend/app/db/base.py`: SQLAlchemy 2.0 `DeclarativeBase`.
   - `backend/app/db/session.py`: Engine with `pool_pre_ping=True`, thread-safe `sessionmaker`, and FastAPI `get_db_session` dependency.
2. Implemented all 10 normalized relational models under `backend/app/models/` using typed SQLAlchemy 2.0 (`Mapped`, `mapped_column`, `relationship`):
   - `scenarios` (`Scenario`): Mutable scenario topic with `versions` cascade.
   - `scenario_versions` (`ScenarioVersion`): Immutable versioned lever parameters with `UniqueConstraint("scenario_id", "version_number")`.
   - `assumption_policies` (`AssumptionPolicy`): Immutable corporate policies capturing `ASM-001` to `ASM-010` with unique version numbers.
   - `simulation_runs` (`SimulationRun`): Execution record binding `ScenarioVersion` and `AssumptionPolicy`.
   - `domain_predictions` (`DomainPrediction`): Per-domain inference summaries (`DEMAND`, `SUPPLY_CHAIN`, `WORKFORCE`).
   - `financial_results` (`FinancialResult`): Income statement line-item aggregates (`gross_revenue`, `cogs`, `net_profit_delta`).
   - `financial_line_items` (`FinancialLineItem`): Transparent waterfall disclosures.
   - `recommendation_results` (`RecommendationResult`): Strategic decisions, Composite Risk Score, and executive briefing.
   - `strategic_actions` (`StrategicAction`): Prioritized mitigation directives.
   - `audit_records` (`AuditRecord`): Immutable append-only cryptographic provenance record storing $\Sigma_{\text{run}}$ JSON.
3. Enforced strict persistence boundary (ADR-005):
   - PostgreSQL stores metadata, versioned runs, and accounting disclosures.
   - Serialized `.joblib` model binaries and 180k-row DataFrames remain strictly on the filesystem / in RAM.
4. Authored comprehensive test suite `backend/tests/test_db_models.py` (5 tests):
   - Verifies schema creation, UUID primary keys, default timestamps.
   - Verifies unique constraint on `(scenario_id, version_number)`.
   - Verifies cascade deletions across scenario $\rightarrow$ versions and run $\rightarrow$ predictions/financials/actions/audit.
   - Verifies full relational navigation tree.

### 2. Dependencies Added
- `sqlalchemy` (2.0.52): Modern Python SQL toolkit and ORM.
- `psycopg2-binary` (2.9.12): PostgreSQL database driver.
- Synchronized into `requirements.txt`.

### 3. Verification & Quality Gates Summary
- **Backend Tests:** 24 passed, 0 failed in 1.65s (`backend/tests/`).
- **Core Analytical Regression:** 93 passed, 0 failed in 40.97s (`tests/`).
- **Total Combined Tests:** **117 passed, 0 failed.**
- **Model Hashes:** All 3 models verified 100% invariant against frozen SHA-256 signatures.
- **Analytical Core Invariance:** Zero lines of code under `src/` or `models/` modified.

---

## Milestone 9.2: Alembic Migrations Setup

**Date:** September 5, 2026  
**Status:** **COMPLETED & VERIFIED**  
**Quality Gates Status:** **ALL GATES PASS (Gate C, Gate A, Gate B)**  
**Migration Revision ID:** `18e29557529f`  

### 1. Objectives Achieved
1. Initialized and configured Alembic migration infrastructure under `backend/alembic/`:
   - `alembic.ini` (repo root): Configured with `script_location = %(here)s/backend/alembic` and `prepend_sys_path = .`.
   - `backend/alembic.ini`: Configured with `script_location = %(here)s/alembic` and `prepend_sys_path = ..` for native execution from within `backend/`.
   - `backend/alembic/env.py`: Fully integrated with Pydantic centralized configuration (`backend.app.core.config.get_settings()`). Zero hardcoded credentials in `.ini` files. Supports dynamic `-x url=...` CLI overrides and test fixture connection injection.
2. Registered all 10 normalized relational entities into Alembic `target_metadata = Base.metadata`:
   - `scenarios`
   - `scenario_versions`
   - `assumption_policies`
   - `simulation_runs`
   - `audit_records`
   - `domain_predictions`
   - `financial_results`
   - `financial_line_items`
   - `recommendation_results`
   - `strategic_actions`
3. Generated deterministic, reviewable initial migration script:
   - Revision ID: `18e29557529f` (`backend/alembic/versions/18e29557529f_001_initial_schema.py`).
   - `upgrade()`: Creates all 10 tables in topological DAG order with UUID primary keys, typed columns, foreign keys with `CASCADE` rules, indexes, and unique constraints.
   - `downgrade()`: Drops tables and indexes in strict reverse dependency order (`strategic_actions` down to `assumption_policies`).
4. Authored comprehensive migration test suite `backend/tests/test_migrations.py` (3 tests):
   - `test_alembic_single_head_revision`: Asserts exactly 1 single head revision (`18e29557529f`).
   - `test_gate_c_migration_idempotency`: Formally executes Gate C verification sequence (`upgrade head` $\rightarrow$ `downgrade base` $\rightarrow$ `upgrade head`), validating zero DDL errors, complete teardown, and idempotent recreation.
   - `test_metadata_tables_match_migration_schema`: Asserts 100% equivalence between `Base.metadata.tables` and migrated database schema.
5. Verified direct CLI execution across both repository root and `backend/` directory with zero errors.

### 2. Dependencies Added
- `alembic` (1.19.2): Database migration tool for SQLAlchemy.
- `Mako` (1.4.1): Templating library used by Alembic for migration code generation.
- Synchronized into `requirements.txt`.

### 3. Verification & Quality Gates Summary
- **Gate C (Database Migration Idempotency):** **PASS** (`upgrade head` $\rightarrow$ `downgrade base` $\rightarrow$ `upgrade head` passed without DDL or constraint errors).
- **Backend Tests:** 27 passed, 0 failed in 1.69s (`backend/tests/`).
- **Core Analytical Regression (Gate A):** 93 passed, 0 failed in 29.01s (`tests/`).
- **Total Combined Tests:** **120 passed, 0 failed in 25.51s.**
- **Model Hashes (Gate B):** All 3 models verified 100% invariant against frozen SHA-256 signatures.
- **Analytical Core Invariance:** Zero lines of code under `src/` or `models/` modified.

---

## Milestone 9.3: Application Services Layer

**Date:** September 5, 2026  
**Status:** **COMPLETED & VERIFIED**  
**Quality Gates Status:** **ALL GATES PASS (Gate F, Gate G, Gate H, Gate I, ADR-006)**  

### 1. Objectives Achieved
1. Implemented the application/services layer under `backend/app/services/` connecting the SQLAlchemy 2.0 relational models to the frozen analytical core without modifying `src/` or `models/`:
   - `backend/app/services/scenario_service.py` (`ScenarioService`): Scenario CRUD, soft archiving, parameter retrieval, and version creation. Enforces **Gate G (Version Immutability)**: parameter updates always generate an incremented immutable `ScenarioVersion` entity, leaving prior versions untouched.
   - `backend/app/services/policy_service.py` (`PolicyService`): Assumption policy management covering `ASM-001` to `ASM-010`. Implements default baseline seeding, policy version incrementation, simplex constraint validation ($w_{\text{supply}} + w_{\text{workforce}} + w_{\text{demand}} = 1.0$), and contract conversion into `BusinessAssumptions` and `CRSWeights`.
   - `backend/app/services/simulation_orchestrator.py` (`SimulationOrchestrator`): Pipeline coordinator uniting Phase 6 (`ScenarioEngine`), Phase 7 (`BusinessImpactEngine`), and Phase 8 (`RecommendationEngine`).
     - **ADR-006 (AnyIO Threadpool Offloading):** CPU-bound analytical execution is executed asynchronously in background worker threads using `run_in_threadpool`, ensuring the async event loop is never blocked.
     - **Gate F (Transaction Atomicity):** Full simulation execution and multi-table persistence occurs inside an atomic database transaction. Any failure mid-simulation immediately rolls back the database session, leaving zero orphaned or partial run records.
     - **Gate H (Provenance Signature Tuple):** Persists all 8 mandatory elements of $\Sigma_{\text{run}}$ inside `AuditRecord` (`run_id`, `scenario_id`, `version_number`, `policy_id`, `model_hashes`, `input_levers_hash`, `timestamp_utc`, `git_commit_hash`).
     - **Gate I (Model Integrity Gate):** Proactively verifies existence and cryptographic SHA-256 signatures of all three serialized models (`demand`, `supply_chain`, `workforce`) before simulation start, raising structured `ModelNotFoundError` or `ModelIntegrityError` if compromised.
   - `backend/app/services/sensitivity_service.py` (`SensitivityService`): High-level sensitivity analysis service managing discrete sweeps for Experiment B (Demand Shock Curves) and Experiment D (Financial Coupling Parameters, CRS Simplex Weights, and Tipping Point Flip Threshold Search) with asynchronous threadpool offloading.
   - `backend/app/services/__init__.py`: Clean exports of all application service classes and singletons.
2. Authored comprehensive, isolated unit/integration test suites under `backend/tests/`:
   - `test_scenario_service.py` (5 tests): Creation, retrieval, Gate G version immutability, archiving, and validation error paths.
   - `test_policy_service.py` (5 tests): Default policy retrieval/creation, policy versioning, simplex validation failure paths, analytical conversion, and 404 errors.
   - `test_simulation_orchestrator.py` (5 tests): Full Phase 6/7/8 pipeline execution, Gate F atomicity rollback verification, Gate H full relational tree & 8-element provenance tuple persistence, Gate I model integrity failure handling (missing file & hash mismatch), and ADR-006 async threadpool offloading.
   - `test_sensitivity_service.py` (3 tests): Experiment B demand shock sweep, Experiment D financial parameter sweep, and CRS weight sweep with boundary flip threshold search.
3. Total backend test count increased from 27 to 45 passing tests.

### 2. Verification & Quality Gates Summary
- **Gate F (Transaction Atomicity):** **PASS** (Simulated analytical failure mid-simulation rolls back DB session; zero orphan records created).
- **Gate G (Version Immutability):** **PASS** (Updating levers creates a new `ScenarioVersion` row with incremented version number; prior versions remain immutable).
- **Gate H (Provenance Signature Tuple):** **PASS** (All 8 tuple components $\Sigma_{\text{run}}$ persisted and verified in `AuditRecord`).
- **Gate I (Model Integrity Gate):** **PASS** (Missing model file triggers `MODEL_NOT_FOUND`; SHA-256 mismatch triggers `MODEL_INTEGRITY_FAILURE`).
- **Backend Tests:** 45 passed, 0 failed in 56.18s (`backend/tests/`).
- **Core Analytical Regression:** 93 passed, 0 failed in 23.95s (`tests/`).
- **Total Combined Tests:** **138 passed, 0 failed.**
- **Model Hashes:** All 3 models verified 100% invariant against frozen SHA-256 signatures:
  - Demand: `FB438C03A742202657BB4EF9196FF17E004BC090E99218F02985DC7720F41941`
  - Supply Chain: `0052E641CF355257ABB332703C3E6A46C65E9AB10A975227D83CF77D7E689B59`
  - Workforce: `4B195C7BEE3AB8F4AFE75CCD0C75FFF0C8E18B9FCA88A00305E165A010109918`
- **Analytical Core Invariance:** Zero lines of code under `src/` or `models/` modified (`git diff --stat src models` is empty).

---

## Milestone 9.4: Pydantic v2 Schemas & API DTOs

**Date:** September 5, 2026  
**Status:** **COMPLETED & VERIFIED**  
**Quality Gates Status:** **ALL GATES PASS (Gate E: API Schema Validation)**  

### 1. Objectives Achieved
1. Implemented the complete Pydantic v2 request/response schemas layer under `backend/app/schemas/`:
   - `common.py`: 6-tier `EpistemicTier` enum (`OBSERVED`, `PREDICTED`, `ASSUMED`, `PROPAGATED`, `CALCULATED`, `RECOMMENDED`), `BaseSchema` (`from_attributes=True`), `BaseRequest` (`extra="forbid"`), `ErrorResponse` / `APIErrorDetail`, and `PaginatedResponse[T]`.
   - `scenario.py`: `ScenarioLeversSchema` (with $[-50\%, +100\%]$ demand growth, $[-3, +3]$ schedule offset, shipping mode whitelist, $[0, 100\%]$ overtime workforce), `ScenarioCreate`, `ScenarioUpdate`, `ScenarioVersionResponse`, and `ScenarioResponse`.
   - `policy.py`: `PolicyCreate` (with simplex constraint validator $w_{\text{supply}} + w_{\text{workforce}} + w_{\text{demand}} = 1.0$, financial parameter bounds, and ASM alias remapping) and `PolicyResponse`.
   - `simulation.py`: `SimulationRequest`, `DomainPredictionResponse`, `FinancialLineItemDTO`, `FinancialResultResponse`, `StrategicActionDTO`, `RecommendationResponse`, `AuditProvenanceDTO`, `AuditRecordResponse`, `SimulationRunSummaryResponse`, and `SimulationDetailResponse`.
   - `sensitivity.py`: `DemandShockSweepRequest` (Experiment B), `FinancialSweepRequest` (Experiment D with whitelist check), `CRSWeightsDTO` / `CRSWeightSweepRequest`, `FlipThresholdSearchRequest`, and corresponding DTO items.
   - `health.py`: `ModelArtifactStatus`, `ModelStatusResponse`, and `HealthResponse`.
   - `__init__.py`: Clean centralized exports of all schemas and DTOs.
2. Formally enforced and verified **Gate E (API Schema Validation Gate)**:
   - `extra="forbid"` rejection verified across all request DTOs (`ScenarioCreate`, `ScenarioUpdate`, `ScenarioLeversSchema`, `PolicyCreate`, `SimulationRequest`, `FinancialSweepRequest`).
   - Numerical boundary enforcement verified ($[-50.0, 100.0]$ demand, $[-3, 3]$ days, $[0, 100]$ overtime, non-negative financial penalties).
   - Simplex equality constraint validation verified on domain weights ($w_s + w_w + w_d = 1.0$).
   - Bidirectional ORM-to-DTO transformation verified across scenarios, policies, simulation relational trees, and Gate H audit provenance JSON records.
3. Created `backend/tests/test_schemas.py` (10 tests) and `backend/tests/conftest.py`.
4. Backend test count increased from 45 to 55 passing tests. Total repository test suite: **148 passed, 0 failed**.

### 2. Verification & Quality Gates Summary
- **Gate E (API Schema Validation):** **PASS** (Extra attributes rejected, empirical bounds enforced, simplex validated, ORM models mapped cleanly).
- **Backend Tests:** 55 passed, 0 failed in 57.52s (`backend/tests/`).
- **Core Analytical Regression:** 93 passed, 0 failed in 23.70s (`tests/`).
- **Total Combined Tests:** **148 passed, 0 failed.**
- **Model Hashes:** All 3 models verified 100% invariant against frozen SHA-256 signatures:
  - Demand: `FB438C03A742202657BB4EF9196FF17E004BC090E99218F02985DC7720F41941`
  - Supply Chain: `0052E641CF355257ABB332703C3E6A46C65E9AB10A975227D83CF77D7E689B59`
  - Workforce: `4B195C7BEE3AB8F4AFE75CCD0C75FFF0C8E18B9FCA88A00305E165A010109918`
- **Analytical Core Invariance:** Zero lines of code under `src/` or `models/` modified (`git diff --stat src models` is empty).

---

## Milestone 9.5: FastAPI Route Controllers & API Router

**Date:** September 5, 2026  
**Status:** **COMPLETED & VERIFIED**  
**Quality Gates Status:** **ALL GATES PASS (Gate E, Gate F, Gate G, Gate H, Gate I)**  

### 1. Objectives Achieved
1. Implemented thin, service-driven RESTful route controllers under `backend/app/api/v1/`:
   - `endpoints/health.py`: `GET /health` (liveness/readiness probe with ML model verification and graceful DB connectivity) and `GET /models/status` (cryptographic SHA-256 inspection of frozen `.joblib` files).
   - `endpoints/scenarios.py`: Full RESTful CRUD, soft-archiving (`DELETE /{id}`), immutable version history (`GET /{id}/versions`, `GET /{id}/versions/{version_id}`), Gate G immutability enforcement on `PATCH`, and execution shortcut (`POST /{id}/run`).
   - `endpoints/policies.py`: Corporate baseline retrieval (`GET /default`), policy listing (`GET /`), lookup by UUID (`GET /{policy_id}`), and version creation (`POST /`) strictly enforcing simplex equality constraints ($w_{\text{supply}} + w_{\text{workforce}} + w_{\text{demand}} = 1.0$). Route ordering strictly preserved with `/default` registered prior to `/{policy_id}`.
   - `endpoints/simulations.py`: Atomic multi-domain simulation execution (`POST /run`), complete relational tree retrieval (`GET /{run_id}`), and paginated historical listing with decision summaries (`GET /`).
   - `endpoints/sensitivity.py`: Asynchronous offloaded parameter sweeps for Experiment B (`POST /demand-sweep`), Experiment D (`POST /financial-sweep`), CRS weight simplex sweeps (`POST /crs-weight-sweep`), and binary search tipping point analysis (`POST /tipping-point`).
   - `api_router.py`: Unified APIRouter mounting all modules under `/api/v1/`.
   - `backend/app/main.py`: Unified router mounted into FastAPI application.
2. Preserved all architectural contracts and constraints:
   - **No Business Logic in Routes:** Controllers perform strictly HTTP parameter binding, Pydantic validation, service delegation, and DTO response mapping.
   - **ADR-006 Concurrency Preservation:** Routes directly `await` async service-layer methods without introducing nested or redundant worker threadpools.
   - **Gates F, G, H, I Preservation:** Verified transactional atomicity (Gate F), version immutability (Gate G), 8-element provenance tuples (Gate H), and cryptographic model verification (Gate I).
   - **Centralized Error Handling:** All domain exceptions and validation errors map to standard structured JSON responses via `format_error_response` with correlation ID propagation.
3. Created comprehensive HTTP test suites under `backend/tests/`:
   - `test_api_contract.py` (8 tests): Unified router mounting, OpenAPI schema verification, Swagger/ReDoc UI access, 404/405 error shapes.
   - `test_routes_scenarios.py` (6 tests): Scenario CRUD lifecycle, Gate G version immutability, simulation shortcut, soft-archiving, cross-scenario version rejection, Gate E extra field rejection.
   - `test_routes_policies.py` (6 tests): Default baseline, listing, lookup by ID, valid simplex creation, simplex sum violation rejection, negative weight rejection, Gate E rejection.
   - `test_routes_simulations.py` (3 tests): Execution and Gate H provenance record, listing and filtering, Gate E rejection.
   - `test_routes_sensitivity.py` (5 tests): Demand shock sweep, financial parameter sweep, CRS weight sweep, tipping point search, Gate E rejection.
4. Total backend test count increased from 55 to **83 passing tests** (0 failures). Total repository test suite: **176 passed, 0 failed**.

### 2. Verification & Quality Gates Summary
- **Gate E (API Schema Validation):** **PASS** (Extra inputs forbidden, numerical bounds validated, simplex constraints checked).
- **Gate F (Simulation Transaction Atomicity):** **PASS** (Entire simulation relational tree committed atomically or rolled back on failure).
- **Gate G (Scenario Version Immutability):** **PASS** (Updating levers creates a new immutable version record, leaving prior versions intact).
- **Gate H (Cryptographic Provenance Signature Tuple):** **PASS** (All 8 tuple components verified in `audit_record.provenance_tuple`).
- **Gate I (Model Artifact Integrity):** **PASS** (Frozen SHA-256 byte hashes verified on disk).
- **Backend Tests:** 83 passed, 0 failed in 127.60s (`backend/tests/`).
- **Core Analytical Regression:** 93 passed, 0 failed in 45.73s (`tests/`).
- **Total Combined Tests:** **176 passed, 0 failed.**
- **Model Hashes:** All 3 models verified 100% invariant against frozen SHA-256 signatures:
  - Demand: `FB438C03A742202657BB4EF9196FF17E004BC090E99218F02985DC7720F41941`
  - Supply Chain: `0052E641CF355257ABB332703C3E6A46C65E9AB10A975227D83CF77D7E689B59`
  - Workforce: `4B195C7BEE3AB8F4AFE75CCD0C75FFF0C8E18B9FCA88A00305E165A010109918`
- **Analytical Core Invariance:** Zero lines of code under `src/` or `models/` modified (`git diff --stat src models` is empty).

---

## Milestone 9.6: Backend Automated Async Test Suite (`httpx.AsyncClient`)

**Date:** September 6, 2026  
**Status:** **COMPLETED & VERIFIED**  
**Quality Gates Status:** **ALL GATES PASS (Gate D, Gate F, Gate I, Gate J, Concurrency)**  

### 1. Objectives Achieved
1. Built the asynchronous end-to-end HTTP integration test infrastructure:
   - Configured `httpx.AsyncClient` with `ASGITransport(app=app)` and `anyio_backend` fixture in `backend/tests/conftest.py` for high-fidelity HTTP-level testing without spawning external live server processes.
   - Bound database session overrides (`get_db_session`) across the lifespan of async requests to isolated in-memory SQLite instances.
2. Implemented Gate J (Full End-to-End Simulation Lifecycle & Sensitivity Sweeps) in `backend/tests/test_simulation_e2e.py` (4 tests):
   - `test_async_full_simulation_lifecycle`: Validates complete lifecycle from `POST /api/v1/scenarios/` $\rightarrow$ immutable v1 versioning $\rightarrow$ execution shortcut `POST /api/v1/scenarios/{id}/run` $\rightarrow$ domain predictions (demand, supply chain, workforce) $\rightarrow$ non-overlapping financial line items $\rightarrow$ recommendation engine trade-offs & strategic actions $\rightarrow$ Gate H 8-element provenance tuple.
   - `test_async_simulation_with_custom_policy_and_overrides`: Validates custom policy registration, temporary override levers triggering immutable v2 version creation, and direct primary-key retrieval.
   - `test_async_parameter_sweeps_e2e`: Validates Experiment B demand shock curve, Experiment D financial parameter sweep (`asm_001_delay_penalty`), CRS simplex domain weights sweep, and binary search tipping point analysis.
   - `test_async_concurrent_simulations_lifecycle`: Validates concurrent execution of two independent scenarios via `anyio` task groups, proving ADR-006 threadpool offload and atomic persistence handle overlapping async requests without cross-talk or race conditions.
3. Implemented Gate F (Transaction Atomicity & Rollback Verification) in `backend/tests/test_simulation_atomicity.py` (1 test):
   - `test_gate_f_simulation_atomicity_and_rollback_through_http`: Injects a simulated storage/subsystem crash during relational entity staging after domain predictions and financial results are instantiated but prior to commit.
   - Asserts that HTTP responds with status 500 (`INTERNAL_ERROR`), and verifies direct database state contains exactly 0 runs, 0 predictions, 0 financials, 0 line items, 0 recommendations, and 0 audit records (zero orphan records).
   - Validates that subsequent uncorrupted run succeeds and commits cleanly.
4. Implemented Gate I (Model Integrity Failure & Execution Refusal) in `backend/tests/test_model_integrity_failure.py` (3 tests):
   - `test_gate_i_model_hash_mismatch_refuses_simulation`: Monkeypatches expected SHA-256 hash in memory (never mutating `.joblib` files on disk), verifies `GET /api/v1/models/status` reports `degraded` and `HASH_MISMATCH`, asserts `POST /run` refuses simulation execution, and verifies clean recovery upon unpatching.
   - `test_gate_i_missing_model_file_refuses_simulation`: Monkeypatches file path in memory to a non-existent path, verifies `FILE_NOT_FOUND`, asserts simulation refusal, and verifies clean recovery.
   - `test_gate_i_all_three_models_active_and_healthy_in_http_status`: Validates baseline operational state where all 3 models report `status='VERIFIED'`, `exists=True`, and matching SHA-256 signatures.
5. Implemented Gate D (Database Constraints & Cascades) in `backend/tests/test_db_constraints.py` (5 tests):
   - `test_scenario_cascade_delete_versions`: Deleting a scenario cascades to all associated versions.
   - `test_scenario_version_unique_constraint`: Enforces `uq_scenario_version` constraint ($(\text{scenario\_id}, \text{version\_number})$ uniqueness).
   - `test_policy_version_unique_constraint`: Enforces $(\text{name}, \text{version})$ uniqueness on assumption policies.
   - `test_financial_result_cascade_line_items`: Deleting a `FinancialResult` cascades to all `FinancialLineItem` records.
   - `test_recommendation_result_cascade_strategic_actions`: Deleting a `RecommendationResult` cascades to all `StrategicAction` records.
6. Total backend test count increased from 83 to **96 passing tests** (0 failures). Total repository test suite: **189 passed, 0 failed**.

### 2. Verification & Quality Gates Summary
- **Gate D (Relational Constraints & Cascades):** **PASS** (5/5 tests passed).
- **Gate F (Transaction Atomicity & Rollback):** **PASS** (1/1 test passed via HTTP).
- **Gate I (Model Artifact Integrity Failure):** **PASS** (3/3 tests passed via HTTP, in-memory patch with 100% restoration).
- **Gate J (E2E Simulation Lifecycle):** **PASS** (4/4 tests passed via `httpx.AsyncClient`).
- **Backend Tests:** 96 passed, 0 failed (`backend/tests/`).
- **Core Analytical Regression:** 93 passed, 0 failed in 44.30s (`tests/`).
- **Total Combined Tests:** **189 passed, 0 failed.**
- **Model Hashes:** All 3 models verified 100% invariant against frozen SHA-256 signatures:
  - Demand: `FB438C03A742202657BB4EF9196FF17E004BC090E99218F02985DC7720F41941`
  - Supply Chain: `0052E641CF355257ABB332703C3E6A46C65E9AB10A975227D83CF77D7E689B59`
  - Workforce: `4B195C7BEE3AB8F4AFE75CCD0C75FFF0C8E18B9FCA88A00305E165A010109918`
- **Analytical Core Invariance:** Zero lines of code under `src/` or `models/` modified (`git diff --stat src models` is empty).

---

## Milestone 9.7: Docker & Docker Compose Setup

**Date:** September 6, 2026  
**Status:** **COMPLETED & VERIFIED**  
**Quality Gates Status:** **ALL GATES PASS (Security, Deterministic Migrations, Model Invariance, Live E2E Stack Verification)**  

### 1. Objectives Achieved
1. **Multi-Stage Container Architecture (`Dockerfile`):**
   - Implemented multi-stage `Dockerfile` with `builder` and `runtime` stages based on official `python:3.13-slim-bookworm`.
   - **Non-Root Execution:** Dedicated system user `appuser` (UID 10001) and group `appgroup` (GID 10001); Uvicorn process runs strictly as unprivileged `appuser`.
   - **Native Runtime Prerequisites:** Installed essential system packages (`libpq5` for PostgreSQL, `libgomp1` for XGBoost OpenMP parallelism on Linux, and `curl` for container healthchecks).
   - **Dependency Isolation:** Safe platform dependency filtering (`grep -v "pywinpty"` into `/tmp/requirements-linux.txt`) executed exclusively within Docker build; canonical `requirements.txt` preserved without mutation.
   - **Evaluation Datasets:** Benchmark data cohorts copied with `--chown=appuser:appgroup data/ data/` allowing non-root simulation execution without external dependencies, while legacy multi-gigabyte reference ZIPs remain excluded via `.dockerignore`.
   - **Deterministic Healthcheck:** Standard `curl -f http://localhost:8000/api/v1/health` probe declared with 10s interval, 5s timeout, and 3 retries.
2. **Deterministic Startup & Migration Entrypoint (`docker-entrypoint.sh`):**
   - Built with strict POSIX bash `set -eo pipefail` and normalized to Unix LF line endings.
   - Performs active TCP/connection polling against PostgreSQL database host and port before attempting migrations.
   - Executes deterministic database schema migrations (`alembic upgrade head`); halts container startup immediately if migrations fail.
   - Hands off execution via `exec "$@"` ensuring proper Unix signal handling (SIGTERM, SIGINT) for graceful shutdown.
3. **Multi-Container Orchestration (`docker-compose.yml`):**
   - Service `db`: PostgreSQL 16 Alpine (`postgres:16-alpine`), persistent named volume `postgres_data`, and healthcheck using `pg_isready`.
   - Service `backend`: DecisionSphere FastAPI backend container depending on `db` with `condition: service_healthy`.
   - Network: Isolated bridge network `decisionsphere-network`.
   - Explicitly documented default credentials (`postgres:postgres`) as local development credentials, requiring external environment injection for production deployments.
4. **Environment & Security Template (`.env.example`):**
   - Complete documentation of all configuration variables (`DATABASE_URL`, `POSTGRES_PASSWORD`, `CORS_ORIGINS`, `SECRET_KEY`, etc.).
   - Prominent security warnings regarding secret rotation and database passwords.
5. **Live Stack Verification Chain (`scripts/verify_container_stack.py`):**
   - Probed live `/api/v1/health`: HTTP 200, status `healthy`, database `connected`, models `verified`.
   - Probed live `/api/v1/models/status`: HTTP 200, all 3 model domains verified byte-identical to frozen SHA-256 fingerprints.
   - Live Containerized Simulation E2E Test:
     - `POST /api/v1/scenarios/` $\rightarrow$ Created scenario `8648552b-fea5-4653-bc7b-a361ad5f1482`.
     - `POST /api/v1/scenarios/{id}/run` $\rightarrow$ HTTP 201 Created (Duration: 5273 ms).
     - Validated 3 Domain Predictions (`DEMAND`, `SUPPLY_CHAIN`, `WORKFORCE`).
     - Validated Managerial Financial Accounting Result ($\Delta \text{Net Profit} = -\$504,503.29$, $\Delta \text{Realized Revenue} = +\$26,770.69$).
     - Validated Strategic Recommendation (`REJECT_RESTRUCTURE`, Composite Risk Score 34.17, `ACT-FIN-001`).
     - Validated Gate H Cryptographic Provenance Record ($\Sigma_{\text{run}}$ persisted with commit, migration revision, and exact model hashes).
   - Graceful Teardown: `docker compose down -v` cleanly stopped and removed containers, volumes, and networks.
6. **Automated Docker Configuration Tests (`backend/tests/test_docker_config.py`):**
   - 5 new automated tests verifying Dockerfile multi-stage structure, non-root user (UID 10001), Compose service dependencies, entrypoint LF line endings, and .dockerignore exclusions.
7. **Full Repository Regression Suite:**
   - Backend test suite: **101 passed, 0 failed** in 123.49s (`backend/tests/`).
   - Core analytical test suite: **93 passed, 0 failed** in 22.66s (`tests/`).
   - Total repository test suite: **194 passed, 0 failed.**

### 2. Verification & Quality Gates Summary
- **Non-Root Execution:** **PASS** (Container runs strictly as `appuser`, UID 10001).
- **Deterministic Migration:** **PASS** (`alembic upgrade head` executed successfully before Uvicorn start).
- **Live Container E2E Simulation:** **PASS** (All 3 domain predictions, financials, recommendations, Gate H audit record generated inside container).
- **Authoritative Model Hashes:** All 3 models verified 100% invariant against frozen SHA-256 signatures:
  - Demand: `FB438C03A742202657BB4EF9196FF17E004BC090E99218F02985DC7720F41941`
  - Supply Chain: `0052E641CF355257ABB332703C3E6A46C65E9AB10A975227D83CF77D7E689B59`
  - Workforce: `4B195C7BEE3AB8F4AFE75CCD0C75FFF0C8E18B9FCA88A00305E165A010109918`
- **Analytical Core Invariance:** Zero lines of code under `src/` or `models/` modified (`git diff --stat src models` is empty).

---

## Milestone 10: DecisionSphere Frontend & Decision Intelligence UI

**Date:** September 6, 2026  
**Status:** **COMPLETED & VERIFIED**  
**Quality Gates Status:** **ALL GATES PASS (Frontend Unit, Component, Build, and Full Analytical Regression)**  

### 1. Objectives Achieved
1. **Frontend Architecture & Scaffold (`frontend/`):**
   - Next.js 15.1.7 (App Router), React 19, TypeScript, Tailwind CSS 3.4.17, TanStack Query v5, Recharts, Lucide React.
   - Restrained HSL design token system with dark/light mode, custom scrollbars, and WCAG 2.2 AA accessible focus rings.
   - Built UI primitive component library: Button, Card, Badge, Slider, Input, Select, Table, Tabs, Dialog.
   - Built specialized common state components: `EpistemicBadge`, `ErrorBanner`, `LoadingSkeleton`, `EmptyState`, `MetricDisplay`.
2. **Authoritative Application Shell:**
   - Collapsible 5-group analytical sidebar (Overview, Decisions, Analysis, Governance, System).
   - Sticky Header with real-time `/api/v1/health` status badge and Gate I model integrity indicator pill (`/api/v1/models/status`).
   - Breadcrumbs navigation and accessible page headers.
3. **Typed API Layer & Correlation ID Propagation:**
   - Centralized HTTP client (`frontend/src/lib/api/client.ts`) injecting `X-Request-ID` correlation IDs on every request.
   - Normalized error parser mapping FastAPI error envelopes (`code`, `message`, `requestId`, `details`) into `DecisionSphereAPIError`.
   - 100% typed endpoint modules matching backend Pydantic contracts (`scenarios`, `simulations`, `policies`, `sensitivity`, `system`).
4. **All 12 Primary Routes Implemented:**
   - `/` (Decision Cockpit / Executive Dashboard)
   - `/scenarios` (Scenario Workspace List)
   - `/scenarios/[id]` (Two-Column Scenario Editor & Lever Configurator with Gate G versioning)
   - `/simulate` (Pre-Flight Review & 9-Stage Execution Runner with Gate I safety refusal)
   - `/simulations` (Simulation History)
   - `/simulations/[id]` (Decision Analysis: Hero, 3-Domain Predictive Cards, Financial Waterfall, Strategic Recommendations, and Cryptographic Provenance Accordion)
   - `/sensitivity` (Sensitivity Lab: Experiment B Demand Sweep, Experiment D Financial Sweep, CRS Simplex Weight Stability, Tipping Point Search)
   - `/policies` (Assumption Policy Management & Simplex Equality Validation $\sum w_i = 1.0$)
   - `/audit` (Provenance & Cryptographic Verification Tuple $\Sigma_{\text{run}}$ with Copy-to-Clipboard)
   - `/system/health` (Infrastructure & DB Health Diagnostics)
   - `/system/models` (SHA-256 Model Fingerprint Verification & Integrity Table)
5. **Architectural Decisions Logged:**
   - **DEC-020 (Frontend Tech Stack):** Next.js 15 App Router + React 19 + Tailwind CSS + TanStack Query v5 chosen for server-side code splitting, fast route pre-fetching, and reactive state management.
   - **DEC-021 (Strict 6-Tier Epistemic Hierarchy):** Enforced `OBSERVED`, `PREDICTED`, `ASSUMED`, `PROPAGATED`, `CALCULATED`, and `RECOMMENDED` badges and semantic borders across every metric in the interface.
   - **DEC-022 (Backend-Authoritative Zero Client Math):** Frontend performs strictly zero recalculation of machine learning inferences, business impact equations, or composite risk scores. All displayed values originate directly from backend API responses.
   - **DEC-023 (Gate I Safety Interlock in UI):** Simulation runner actively polls `/api/v1/models/status` and unconditionally blocks execution if `models_verified = false`, displaying an explicit refusal banner.
   - **DEC-024 (Two-Column Analytical Workspace):** Left panel provides constrained lever sliders with explicit physical units; right panel provides immediate baseline vs. shock delta inspection.
   - **DEC-025 (Cryptographic Provenance $\Sigma_{\text{run}}$ Verification):** Full audit tuples (Git commit, migration revision, exact SHA-256 model hashes) are inspectable on every simulation detail page.
6. **Automated Verification Suite:**
   - 35 frontend Vitest tests passing (`npm test`).
   - 0 TypeScript errors (`npm run typecheck`).
   - 0 ESLint errors (`npm run lint`).
   - Production Next.js build verified (`npm run build`: 12/12 static pages generated).
   - 101 backend tests passing (`pytest backend/tests`).
   - 93 core analytical tests passing (`pytest tests`).
   - Grand total: **229 automated tests passing, 0 failed**.
   - Invariance verified: `git diff --stat src models` is 100% empty.

---

## Milestone 11: Research, Explainability, EDA, ML Documentation & Publication Suite

**Date:** September 6, 2026  
**Status:** **COMPLETED & VERIFIED**  
**Quality Gates Status:** **ALL GATES PASS (16/16 Notebooks Executed with 0 Errors, 15 Figures Generated, 7 Research Tests Passing, 236 Total Automated Tests)**  

### 1. Objectives Achieved
1. **Complete 16-Part Jupyter Research & Learning Suite (`notebooks/`):**
   - Conforms to the mandatory 16-section pedagogical template (Title, Purpose, Prerequisites, Business Question, Technical Question, Epistemic Demarcation, Dataset/Source, Data Prep, Executable Analysis, Visualizations, Results, What This Tells Us, What This Does NOT Tell Us, Platform Connection, Limitations, Viva Takeaways).
   - Fully executed and verified with `scripts/execute_notebook_suite.py` in 210.52s with **16/16 passing and 0 errors**.
   - Guaranteed execution independence via `ROOT_ANCHOR_CODE` and canonical project-relative paths.
2. **15 Publication Figures at 300 DPI (`artifacts/figures/`):**
   - Generated deterministically by `notebooks/14_research_figures.ipynb`:
     `architecture_overview.png`, `dataset_distributions.png`, `demand_feature_importance.png`, `supply_chain_confusion_matrix.png`, `supply_chain_roc_pr_calibration.png`, `workforce_feature_importance.png`, `workforce_roc_pr_calibration.png`, `cross_domain_propagation.png`, `financial_waterfall.png`, `risk_decomposition.png`, `demand_sensitivity_curve.png`, `financial_sensitivity_sweep.png`, `crs_weight_stability.png`, `tipping_point_analysis.png`, `number_lineage_trace.png`.
3. **Authoritative Research & Epistemic Documentation:**
   - `docs/research-system-map.md`: 13-stage end-to-end analytical architecture map linking code, line numbers, and mathematical equations.
   - `docs/DecisionSphere-Complete-Project-Guide.md`: 24-section comprehensive pedagogical master guide teaching the platform from zero.
   - `docs/DecisionSphere-Glossary.md`: Exhaustive alphabetical glossary defining all terms, metrics, and governing formulas across the 6 epistemic tiers.
   - `docs/DecisionSphere-Number-Lineage.md`: Master lineage trace table connecting every UI number to its API endpoint, backend service, function, and canonical run output.
   - `docs/DecisionSphere-Design-Rationale.md`: Systematic academic justification for 3 datasets, 3 models, XGBoost, calibration, and deterministic accounting.
   - `docs/DecisionSphere-Assumptions-and-Limitations.md`: Honest appraisal of benchmark bounds, non-causal limits, ASM coupling registry, and threats to validity.
   - `docs/Frontend-to-Research-Mapping.md`: Complete Rosetta Stone connecting Next.js UI components to research notebooks and documentation.
   - `docs/reproducibility.md`: Step-by-step PowerShell reproduction instructions for external researchers.
   - `docs/DecisionSphere-Learning-Path.md`: Four tailored learning tracks (Beginner, Full-Stack Engineer, Empirical Researcher, Viva Defense).
   - `docs/research-paper-materials/`: 14 formal research paper chapters (`01_abstract_draft.md` to `14_conclusion.md`).
4. **Frontend Scientific Comprehension Integration:**
   - Enhanced `frontend/src/components/dashboard/DecisionHero.tsx` with an interactive "Scientific Interpretation & Lineage Drawer" explaining recommendation rule origins (`RULE-04`), Composite Risk Score weighting, and the financial calculation formula without modifying analytical logic.
5. **Quality Gates & Automated Verification:**
   - `tests/test_research_suite.py`: 7 automated regression tests verifying notebook existence, 16-section structure, figures, model SHA-256 fingerprints, and core documentation completeness.
   - Core analytical tests: **100 passed, 0 failed** (`pytest tests/`).
   - Backend tests: **101 passed, 0 failed** (`pytest backend/tests/`).
   - Frontend tests: **35 passed, 0 failed** (`npm test`).
   - Frontend production build: **12/12 static routes generated cleanly** (`npm run build`).
   - Grand total: **236 automated tests passing, 0 failed**.
   - Frozen core invariance: `git diff --stat src models` is **0 files changed, 0 insertions, 0 deletions**.
