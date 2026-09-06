# ADR-004: Versioned Scenario and Policy Provenance

## Status
**ACCEPTED** (2026-09-05)

## Context
In decision-support platforms, scenario parameters and operational assumptions (`ASM-001` through `ASM-010`) evolve over time as organizational cost structures shift. If simulation runs merely reference mutable "current" configuration tables, historical auditability is destroyed: re-evaluating a scenario executed three months prior would yield different financial calculations and recommendations because underlying penalty rates or overtime costs changed.

## Decision
We enforce an **Immutable Versioned Snapshot Architecture** for all scenario inputs, assumption policies, and simulation runs:
1. **Immutable Scenario Versions:** When a user modifies scenario levers, a new immutable `ScenarioVersion` row is created (incrementing `version_number`). Past versions are never mutated.
2. **Immutable Policy Versions:** Assumption parameters (`ASM-001` to `ASM-010`, `cogs_ratio`, `unit_price`) are stored as versioned, immutable `AssumptionPolicy` entities.
3. **Execution Provenance Signature:** Every `SimulationRun` binds directly to an immutable `ScenarioVersion` and an immutable `AssumptionPolicy`, storing a complete cryptographic provenance tuple:
   $$\Sigma_{\text{run}} = \left\langle \text{ScenarioVerID}, \text{ArtifactHashes}, \text{PolicyVerID}, \text{GitCommitHash}, \text{AppVersion}, \text{PythonVersion}, \text{MigrationRevision}, \text{Timestamp} \right\rangle$$

## Consequences

### Positive
- **Auditable Historical Lineage:** A simulation executed at any point in time can be inspected with the exact parameters, policy values, and model versions active during that execution.
- **Reproducible Execution:** Prevents silent drifts in historical reporting when corporate assumptions or weights are re-calibrated.

### Negative / Trade-offs
- Modifying a scenario requires creating a new version record rather than in-place mutation, increasing table row counts. (This storage impact is negligible for relational databases).
