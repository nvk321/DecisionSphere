# DecisionSphere — Assumptions, Open Questions & Risk Log

In accordance with anti-hallucination and academic integrity rules, this document captures every operational assumption, parameter heuristic, and unresolved question. Items are tracked until empirically verified.

---

## 1. Operational & Business Formula Assumptions

| ID | Domain | Assumption Description | Grounding / Source | Status |
|---|---|---|---|---|
| **ASM-001** | Supply Chain | Contractual late delivery penalty defaults to $\$25.00$ per delayed order. | Public DataCo dataset contains order prices but lacks contractual penalty clauses. Industry heuristic. | `[ASSUMPTION]` |
| **ASM-002** | Supply Chain | Expedited freight shipping surcharge defaults to $\$15.00$ per unit when toggling expedited shipping. | Logistics standard freight benchmark. User configurable in UI. | `[ASSUMPTION]` |
| **ASM-003** | Supply Chain | High late delivery probability causes a 15% cancellation / demand loss factor ($\kappa_{\text{stockout}} = 0.15$). | E-commerce industry cancellation benchmark for multi-day delayed orders. | `[ASSUMPTION]` |
| **ASM-004** | Workforce | Cost of replacing an employee who leaves (churn) is estimated at 50% of annual median salary ($\approx \$30,000$). | Society for Human Resource Management (SHRM) benchmark. | `[ASSUMPTION]` |
| **ASM-005** | Workforce | Overtime hourly labor premium is calculated at $1.5\times$ standard hourly rate ($\approx \$45/\text{hour}$). | Standard labor compensation law standard. | `[ASSUMPTION]` |
| **ASM-006** | Scenario Engine | Extreme volume surges decrements `WorkLifeBalance` by 1 level for impacted roles. | Heuristic parameter to model organizational strain propagation. | `[ASSUMPTION]` |

*Protocol: Whenever an assumption is used in the codebase, it must refer to its ID (e.g., `# ASM-001`) and remain configurable via application settings.*

---

## 2. Open Technical Questions & Decision Points

### Q1: Demand Forecasting Dataset Selection
- **Candidates:**
  - Option A: *Corporación Favorita Store Sales* (Ecuador grocery: rich daily granularity, 54 stores, promotions, oil prices, holidays; ~116 MB).
  - Option B: *Walmart Recruiting Store Sales* (US weekly sales, 45 stores, markdowns, macroeconomic features; ~12 MB).
  - Option C: *Rossmann Store Sales* (European pharmacy daily sales, 1,115 stores, promotions, competition; ~36 MB).
- **Evaluation Criteria:** Temporal granularity (daily preferred), clarity of promotional levers, memory footprint, and alignment with multi-department enterprise scenarios.
- **Resolution Plan:** Execute automated audit in Phase 1 and select the optimal dataset based on concrete empirical profiling.

### Q2: Supply Chain Target Formulation in DataCo
- **Candidates:**
  - Option A: Binary classification on `Late_delivery_risk` (0 vs 1).
  - Option B: Multi-class classification on `Delivery Status` (Late delivery, Advance shipping, Shipping on time, Shipping canceled).
- **Resolution Plan:** Binary classification (`Late_delivery_risk`) is the primary target for clear risk scoring; multi-class classification will be evaluated as a secondary exploratory target.

### Q3: LLM Integration Mode for Recommendation Generation
- **Candidates:**
  - Option A: Pure deterministic rule-based recommendation generator (100% offline, zero API latency/cost).
  - Option B: Hybrid architecture: Rule-based recommendation engine produces structured actions, passed to an LLM API (OpenAI / Gemini) for narrative synthesis if API key is provided, gracefully falling back to deterministic templates if offline.
- **Decision:** **Option B (Hybrid with deterministic fallback)** is chosen to ensure both advanced demonstrability and absolute offline reliability during laboratory presentations.

---

## 3. Risk Log & Mitigations

| Risk ID | Risk Description | Severity | Likelihood | Mitigation Strategy |
|---|---|---|---|---|
| **RSK-001** | DataCo dataset memory footprint (~96 MB CSV, 180k rows) causing latency in API inference. | Medium | High | Train model offline, save compact `.joblib` model artifact ($<5\text{MB}$), and use sampled evaluation subsets for runtime dashboard benchmarks. |
| **RSK-002** | Class imbalance in IBM HR Attrition (~16% positive) leading to uninformative models if measured solely by accuracy. | High | High | Enforce PR-AUC, ROC-AUC, and F1-score evaluation; apply class weighting (`scale_pos_weight`) in tree models. |
| **RSK-003** | Temporal leakage in time-series demand forecasting. | High | Medium | Enforce strict chronological splits in code; prohibit random shuffling. |
| **RSK-004** | Live review failure due to external network dependency (LLM API / Cloud DB). | Critical | Low | Self-contained local execution: local PostgreSQL / SQLite fallback, offline model inference, deterministic recommendation fallback. |
