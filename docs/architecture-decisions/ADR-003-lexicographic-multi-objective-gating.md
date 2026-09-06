# ADR-003: Lexicographic Multi-Objective Decision Gating

## Status
**ACCEPTED** (2026-09-05)

## Context
Strategic business decisions involve conflicting objectives: maximizing economic return (Net Incremental Profit $\Delta \text{Profit}$) while minimizing operational execution risk (Composite Risk Score $\text{CRS}$). A naive approach often seen in multi-criteria decision analysis is to collapse these two disparate dimensions into a single scalar objective via a weighted linear combination:
$$U = \alpha \cdot (\Delta \text{Profit}) - (1 - \alpha) \cdot \text{CRS}$$
However, this scalarization suffers from severe practical and theoretical flaws:
1. It permits unit incomparability (trading dollars against dimensionless risk index points).
2. It allows a scenario with massive, reckless operational strain (e.g. 80% delivery failure and catastrophic employee burnout) to be approved simply because projected nominal profit is extremely large.
3. Conversely, it allows an unprofitable commercial promotion ($\Delta \text{Profit} < 0$) to be approved simply because operational risk is low.

## Decision
We implement a **Strict Lexicographic Decision Gating Framework** with a prioritized two-tier decision rule:
1. **Tier 1 (Economic Viability Gate):**
   $$\Delta \text{Profit} \le 0.0 \implies \mathbf{REJECT\_RESTRUCTURE}$$
   *A scenario that destroys shareholder capital is unconditionally rejected or sent for commercial restructuring, regardless of how safe or benign operational strain is.*
2. **Tier 2 (Operational Strain Gate - Evaluated iff $\Delta \text{Profit} > 0.0$):**
   - If $\text{CRS} \le \tau_{\text{risk}}$ ($50.0 / 100$) $\implies \mathbf{PROCEED}$
   - If $\text{CRS} > \tau_{\text{risk}}$ ($50.0 / 100$) $\implies \mathbf{PROCEED\_WITH\_MITIGATIONS}$

## Consequences

### Positive
- **Guaranteed Profitability:** Eliminates the risk of greenlighting loss-making campaigns under the guise of "low risk".
- **Grounded Governance:** Scenarios that are financially accretive but operationally volatile are not naively rubber-stamped; they are gated behind explicit, actionable mitigation requirements (Rules `RULE-01` through `RULE-07`).
- **Mathematical Traceability:** Every decision classification is 100% auditable and reproducible without opaque utility weights or heuristic black-box scoring.

### Negative / Trade-offs
- Hard threshold boundaries ($\Delta \text{Profit} = 0$, $\text{CRS} = 50.0$) create discrete step transitions (flip points). These flip points must be explicitly communicated to decision-makers through sensitivity analysis curves.
