# ADR-005: Persistence Boundary and System of Record

## Status
**ACCEPTED** (2026-09-05)

## Context
Enterprise applications often suffer from architectural bloat by treating the relational database as a dumping ground for binary model artifacts, raw tabular datasets, or transient cache entries. In DecisionSphere, we must delineate what belongs in PostgreSQL versus what belongs in the filesystem or in-memory runtime.

## Decision
We define a strict **Persistence Boundary**:
1. **PostgreSQL as the System of Record:**
   - Stores scenario definitions, immutable scenario versions, assumption policies, simulation run records, aggregate domain prediction summaries, financial accounting line items, triggered rules, and recommended strategic actions.
2. **Filesystem as the Machine Learning Lake:**
   - Serialized machine learning models (`models/demand/demand_model.joblib`, `models/supply_chain/supply_chain_model.joblib`, `models/workforce/workforce_model.joblib`) remain stored strictly on the local filesystem, tracked via git LFS / persistent volume, and verified by SHA-256 byte hashes at application boot.
   - Large benchmark datasets (`data/raw/`, `data/processed/`) remain stored on disk.
3. **In-Memory Cache for Benchmark Baseline Data:**
   - Standard reference cohorts (e.g. 1,000 orders, 1,470 employees) used for baseline evaluations are loaded once into application memory at startup as read-only pandas DataFrames, avoiding redundant disk I/O on every simulation run.

## Consequences

### Positive
- **Database Leanliness & High Performance:** Eliminates database bloat from multi-megabyte binary blobs. Database backups and migrations remain fast and lightweight.
- **Clear Separation of Concerns:** Relational transactions govern business metadata; specialized file loaders govern ML inference assets.

### Negative / Trade-offs
- Model artifacts must be mounted or packaged into the backend Docker container filesystem. (Handled via container volumes and Docker build steps).
