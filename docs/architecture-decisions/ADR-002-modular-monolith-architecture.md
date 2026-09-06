# ADR-002: Modular Monolith Architecture over Microservices

## Status
**ACCEPTED** (2026-09-05)

## Context
DecisionSphere integrates three predictive machine learning domains (Demand, Supply Chain, Workforce) with an operational scenario engine, a managerial accounting engine, and a recommendation engine. In modern enterprise software engineering, there is a frequent temptation to decompose such multi-domain systems into distributed microservices (e.g., separate services for Demand, Logistics, HR, Accounting, Recommendations, coupled via message brokers like Kafka/RabbitMQ and orchestrators like Celery/Kubernetes).

However, our project constraints include:
1. A 3-student team operating within fixed academic review deadlines (BCSE497J Review 2 / TRL 4).
2. The need for strict cross-domain deterministic reproducibility and transaction atomicity.
3. Zero tolerance for distributed system failure modes (network partitions, eventual consistency race conditions, out-of-order message delivery).
4. Sub-second interactive response times for live faculty demonstrations and simulation sweeps.

## Decision
We formally reject distributed microservices and adopt a **Clean Modular Monolith Architecture**:
- All analytical modules (`src/data/`, `src/models/`, `src/scenario/`, `src/business/`, `src/recommendation/`) reside in a single, version-controlled Python codebase as isolated, pure domain packages.
- The web service (`backend/app/`) runs as a single FastAPI process hosting synchronous inference execution offloaded to an asynchronous threadpool.
- Inter-module communication occurs via in-memory Python function calls and strongly typed Pydantic data structures, completely eliminating network latency and distributed serialization overhead.
- Persistence is handled by a single PostgreSQL 16 database.

## Consequences

### Positive
- **Deterministic Atomicity:** Complete scenario simulation (Phases 6–8) executes within a single synchronous transaction boundary. If any domain fails, the transaction is cleanly rolled back without leaving orphaned distributed state.
- **High Performance:** In-memory parameter propagation avoids HTTP/gRPC/AMQP network serialization, yielding execution latencies under 500ms for full multi-domain runs.
- **Radically Lower Operational Overhead:** No Kafka brokers, Redis clusters, or Celery workers required. Can be spun up locally or in Docker with a single command (`docker compose up`).
- **Testability:** Unit, integration, and regression tests run directly with `pytest` without needing mock brokers or distributed test harnesses.

### Negative / Trade-offs
- **Vertical Scaling Only:** CPU-intensive simulation scaling is bounded by the host machine's multi-core capacity rather than dynamic auto-scaling clusters. This is completely sufficient for laboratory research benchmarks and academic evaluation.
