# ADR-006: Synchronous CPU-Bound ML Execution Strategy

## Status
**ACCEPTED** (2026-09-05)

## Context
The core analytical simulation in DecisionSphere (`ScenarioEngine.execute()`, `BusinessImpactEngine.calculate()`, `RecommendationEngine.evaluate()`) is written in synchronous Python using numerical packages (`numpy`, `pandas`, `xgboost`, `scikit-learn`). These routines are CPU-bound rather than I/O-bound.

FastAPI is built on an asynchronous event loop (AnyIO / Starlette). If CPU-intensive synchronous operations are invoked directly inside an `async def` endpoint, they block the event loop, preventing concurrent requests (such as health probes, status checks, or reads) from being processed until the calculation finishes.

## Decision
We adopt **Starlette Threadpool Offloading** for CPU-bound simulation invocations:
1. Analytical calls are delegated to the worker threadpool using:
   ```python
   from starlette.concurrency import run_in_threadpool

   result = await run_in_threadpool(orchestrator.run_simulation, scenario_params, policy)
   ```
2. Database operations use standard SQLAlchemy session management scoped per request.
3. Thread safety: The pre-loaded scikit-learn and XGBoost model objects are treated as strictly **read-only** (only invoking `predict()` / `predict_proba()`), which is inherently thread-safe in Python.
4. Input DataFrames are passed as copies or immutably constructed cohorts so that worker threads do not mutate shared global state.

## Consequences

### Positive
- **Responsive Event Loop:** The FastAPI server remains completely responsive to concurrent HTTP requests (health checks, scenario listing) even while a 500ms simulation run is executing on a worker thread.
- **Simplicity:** Eliminates the need for external task queues (Celery, Redis) while providing proper asynchronous isolation for CPU tasks.

### Negative / Trade-offs
- Subject to Python's Global Interpreter Lock (GIL) for pure Python operations, although C-extensions (NumPy, XGBoost) release the GIL during matrix computations. This provides sufficient multi-core concurrency for Review 2 workloads.
