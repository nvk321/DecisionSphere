# DecisionSphere — Assumptions, Open Questions & Risk Log

In accordance with anti-hallucination and academic integrity rules, this document captures every operational assumption, parameter heuristic, and unresolved question. Items are tracked until empirically verified.

---

## 1. Operational & Business Formula Assumptions (The Parametric Registry)

In accordance with anti-hallucination rules and academic integrity protocols, heterogeneous public benchmarks are coupled through transparent, parameterized constants. Every assumption is assigned a baseline value, an uncertainty range for sensitivity testing (Experiment D), a dimensional unit, and an empirical justification.

### Phase 6: Operational Scenario Assumptions (`src/scenario/`)
Consumed strictly by the Scenario Engine for cross-domain operational parameter propagation. These parameters carry **zero financial valuation**:

| ID | Domain | Parameter Description | Math Symbol | Baseline Value | Sensitivity Range (Exp D) | Dimensional Unit | Grounding / Source | Status |
|---|---|---|---|---|---|---|---|---|
| **ASM-006** | Scenario Engine | Overtime-induced satisfaction decrement | $\Delta \text{WLB}$ | **$-1\text{ level}$** | $\{0, -1, -2\}$ | `ordinal scale level` | Heuristic parameter modeling organizational burnout on $[1, 4]$ survey scale. | `[ASSUMPTION]` |
| **ASM-007** | Enterprise Normalization | Order-volume scaling factor | $\gamma_{\text{volume}}$ | **$1.0$ (Direct)** | $[0.5, 2.0]$ | `orders / sales unit` | Synthetic normalization bridge between retail sales volume and warehouse dispatch orders. | `[ASSUMPTION]` |
| **ASM-008** | Temporal Synchronization | Planning cycle alignment factor | $\tau_{\text{cycle}}$ | **$30\text{ days}$** | $[14, 90\text{ days}]$ | `days` | Aligns daily demand forecasting horizons with monthly operational planning cycles. | `[ASSUMPTION]` |

### Phase 7: Financial Business Impact Assumptions (`src/business/`)
Consumed strictly by the Business Impact Engine for deterministic financial accounting ($\Delta \text{Revenue}$, $\Delta \text{Cost}$, $\Delta \text{Profit}$). Prohibited from entering Phase 6:

| ID | Domain | Parameter Description | Math Symbol | Baseline Value | Sensitivity Range (Exp D) | Dimensional Unit | Grounding / Source | Status |
|---|---|---|---|---|---|---|---|---|
| **ASM-001** | Supply Chain | Contractual late delivery penalty per delayed order | $C_{\text{delay\_penalty}}$ | **$\$25.00$** | $[\$10.00, \$60.00]$ | `USD / delayed order` | Standard 3PL carrier SLA late-delivery contractual penalty benchmark. | `[ASSUMPTION]` |
| **ASM-002** | Supply Chain | Expedited freight shipping surcharge per unit | $C_{\text{expedite\_fee}}$ | **$\$15.00$** | $[\$5.00, \$35.00]$ | `USD / expedited order` | Commercial express air cargo surcharge over standard ground freight. | `[ASSUMPTION]` |
| **ASM-003** | Supply Chain | Late order cancellation / demand loss factor | $\kappa_{\text{stockout}}$ | **$0.15$ ($15\%$)** | $[0.05, 0.40]$ | `dimensionless churn ratio` | E-commerce industry cancellation benchmark for multi-day fulfillment delays. | `[ASSUMPTION]` |
| **ASM-004** | Workforce | Employee replacement / turnover cost | $C_{\text{replacement}}$ | **$\$30,000$** | $[\$15,000, \$60,000]$ | `USD / departed employee` | SHRM benchmark ($50\%$ to $75\%$ of annualized median salary). | `[ASSUMPTION]` |
| **ASM-005** | Workforce | Overtime hourly labor rate | $R_{\text{overtime}}$ | **$\$45.00/\text{hr}$** | $[\$30.00, \$75.00/\text{hr}]$ | `USD / overtime hour` | Standard US FLSA $1.5\times$ overtime rate on an annualized $\$60,000$ base wage $(\$30.00/\text{hr} \text{ base} \times 1.5)$. | `[ASSUMPTION]` |
| **`cogs_ratio`** | Financial | Cost of Goods Sold ratio on realized sales | $c_{\text{cogs}}$ | **$0.60$ ($60\%$)** | $[0.30, 0.90]$ | `ratio` | Retail industry benchmark gross margin ($40\%$). | `[ASSUMPTION]` |
| **`unit_price`** | Commercial | Monetary selling price per retail unit | $\bar{P}$ | **$\$1.00$** | $[\$0.50, \$50.00]$ | `USD / sales unit` | Baseline retail sales price. | `[ASSUMPTION]` |

### Phase 8: Recommendation & Risk Governance Assumptions (`src/recommendation/`)
Consumed strictly by the Recommendation Engine for Composite Risk Scoring and Lexicographic Gating:

| ID | Domain | Parameter Description | Math Symbol | Baseline Value | Sensitivity Range (Exp D) | Dimensional Unit | Grounding / Source | Status |
|---|---|---|---|---|---|---|---|---|
| **ASM-009** | Risk Engine | Composite Risk Score Domain Simplex Weights | $(w_s, w_w, w_d)$ | **$(0.40, 0.40, 0.20)$** | $\sum w_i = 1.0, w_i \ge 0$ | `simplex weights` | Executive governance balancing logistics, workforce, and commercial strain. | `[ASSUMPTION]` |
| **ASM-010** | Risk Engine | Operational Risk Tolerance Ceiling | $\tau_{\text{risk}}$ | **$50.0 / 100$** | $[30.0, 70.0]$ | `index score` | Lexicographic threshold gating accretive scenarios behind mandatory mitigations. | `[ASSUMPTION]` |

*Protocol:*
1. Whenever an assumption is used in the codebase, it must explicitly reference its ID (e.g., `# ASM-001`) in code comments and docstrings.
2. Phase 6 schemas (`ScenarioAssumptions`) must reject `ASM-001` through `ASM-005`, `ASM-009`, and `ASM-010`.
3. Phase 7 schemas (`BusinessAssumptions`) must reject `ASM-006` through `ASM-008`, `ASM-009`, and `ASM-010`.
4. Phase 8 schemas (`CRSWeights`) must strictly enforce simplex normalization ($\sum w_i = 1.0$).
5. All parameters must remain user-configurable via versioned policies (`PolicyVersion`) within their declared sensitivity bounds.
6. The sensitivity of the platform's outputs to these parameters is systematically evaluated in **Experiment D** (`docs/experimental-design.md`).

---

## 2. Technical Questions & Resolved Decisions

### Q1: Demand Forecasting Dataset Selection
- **Status:** **RESOLVED (Phase 1 Audit)**
- **Decision:** **Rossmann Store Sales** (`reference/rossmann-store-sales.zip`) is selected as the primary demand forecasting dataset.
- **Empirical Rationale:**
  - Provides daily sales granularity across 1,115 stores over 941 days.
  - Contains an explicit, high-impact `Promo` operational lever (+82.5% sales lift).
  - 100% complete data in `train.csv` (0 missing values, no negative sales anomalies).
  - Feasible and fast in memory (158 MB RAM) compared to Corporación Favorita (3M rows, 50% zero-inflation) and Walmart (weekly buckets, >50% missing markdowns).

### Q2: Supply Chain Target Formulation & Leakage Prevention in DataCo
- **Status:** **RESOLVED (Phase 1 Audit)**
- **Decision:** Binary classification on `Late_delivery_risk` (0 = On-time, 1 = Late) is the primary target ($54.8\%$ positive balance).
- **Critical Leakage Discovery:** `Days for shipping (real)` must be **DROPPED** from all predictive feature vectors because it is an outcome variable known only after shipment delivery ($real > scheduled \implies late$). Secondary fulfillment variables (`Delivery Status`, `shipping date (DateOrders)`, `Order Status`) are also strictly dropped.

### Q3: LLM Integration Mode for Recommendation Generation
- **Status:** **ACCEPTED**
- **Decision:** **Hybrid architecture with deterministic fallback.** The core recommendation engine executes a deterministic condition-action matrix and XAI feature attributions. If an LLM API key is provided, an LLM synthesizes an executive summary; otherwise, the platform falls back smoothly to deterministic templates with zero downtime.

---

## 3. Risk Log & Mitigations

| Risk ID | Risk Description | Severity | Likelihood | Mitigation Strategy | Status |
|---|---|---|---|---|---|
| **RSK-001** | DataCo dataset memory footprint (~96 MB CSV, 180k rows) causing latency in API inference. | Medium | High | Train model offline, save compact `.joblib` model artifact ($<5\text{MB}$), and use sampled evaluation subsets for runtime dashboard benchmarks. | **Active / Mitigated** |
| **RSK-002** | Class imbalance in IBM HR Attrition (~16% positive) leading to uninformative models if measured solely by accuracy. | High | High | Enforce PR-AUC, ROC-AUC, and F1-score evaluation; apply class weighting (`scale_pos_weight`) in tree models. | **Active / Mitigated** |
| **RSK-003** | Temporal leakage in time-series demand forecasting. | High | Medium | Enforce strict chronological splits in code; prohibit random shuffling. | **Active / Mitigated** |
| **RSK-004** | Lookahead leakage in DataCo via `Days for shipping (real)`. | Critical | High | Formally documented and enforced feature exclusion in `docs/data-audit-report.md`. | **RESOLVED** |
| **RSK-005** | Live review failure due to external network dependency (LLM API / Cloud DB). | Critical | Low | Self-contained local execution: local PostgreSQL / SQLite fallback, offline model inference, deterministic recommendation fallback. | **Active / Mitigated** |
| **RSK-006** | Large DataFrame memory footprint in concurrent API runs. | Medium | Medium | Pre-load immutable benchmark references in RAM; avoid redundant deep-copies. | **Active / Mitigated** |
| **RSK-007** | Database schema drift across development environments. | High | Medium | Strict enforcement of Alembic version-controlled migrations; zero manual DDL. | **Active / Mitigated** |
| **RSK-008** | Event loop blocking from CPU-intensive ML inferences. | Medium | Medium | Wrap analytical execution inside Starlette run_in_threadpool. | **Active / Mitigated** |

---

## 4. Research Integrity & Open Methodological Issues

In accordance with academic rigor, the following methodological issues are flagged as open research inquiries rather than assumed facts:

1. **H1 Falsification Metric (Decision Divergence Rate):**
   - Pearson correlation ($r > 0.98$ between $\Delta \text{Revenue}$ and $\Delta \text{Profit}$) is conceptually insufficient to falsify decision divergence because linear association does not capture discrete decision boundary shifts.
   - *Status:* Refined to Categorical Decision Divergence Rate ($\text{DDR} \ge 20\%$) across high-shock scenarios ($\Delta D \ge +30\%$).
2. **H2 Inverted-U Response Surface:**
   - Whether net marginal profit $\frac{\partial (\Delta \text{Profit})}{\partial (\Delta D)}$ exhibits an inverted-U dynamic depends on the ratio of unit gross margin ($\$0.40$) to delivery penalties ($\$25.00$) and saturation of late delivery risk.
   - *Status:* Treated as an empirical research question to map via Experiment B sweeps rather than an assumed certainty.
3. **H3 Parameter Invariance Windows:**
   - The heuristic $\pm 25\%$ parameter variation window is not empirically grounded in enterprise cost accounting variance.
   - *Status:* Refined in Experiment D to compute the exact numerical distance to the nearest discrete decision flip point ($\delta_{\text{boundary}} = \min |\theta_{\text{current}} - \theta_{\text{flip}}|$).
4. **H4 Statistical Significance vs Monotonicity for TreeSHAP:**
   - Running inferential $p$-value hypothesis tests on deterministic TreeSHAP attributions across synthetic cohorts ($N > 1000$) is methodologically flawed because large sample sizes yield trivially tiny $p$-values.
   - *Status:* Refined to Spearman's Rank Correlation ($\rho > 0.70$) and Directional Agreement Ratio ($\text{DAR} \ge 85\%$).
5. **Cross-Domain Coupling Generalizability:**
   - Rossmann, DataCo, and IBM HR are heterogeneous benchmark datasets from different organizations. They function as a *Normalized Synthetic Coupling Testbed*, not a single observed real-world enterprise.

