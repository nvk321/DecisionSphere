# DecisionSphere — Scientific Methodology & Modeling Protocols

This document specifies the scientific methodology, machine learning architectures, statistical validation, calibration protocols, cross-domain propagation rules, and governance gates implemented in **DecisionSphere**.

---

## 1. Research Problem & Epistemic Boundaries

DecisionSphere provides scenario-based decision intelligence across three historically siloed enterprise operational domains:
1. **Demand Forecasting** (Rossmann Store Sales benchmark)
2. **Supply Chain Delivery Risk** (DataCo Supply Chain benchmark)
3. **Workforce Attrition Risk** (IBM HR Analytics benchmark)

### Epistemic Hierarchy
In accordance with scientific epistemology (Shmueli 2010), every quantity in DecisionSphere belongs strictly to one of six explicit epistemic tiers:

```
[1. OBSERVED]   Ground-truth empirical records from benchmark datasets
       ↓
[2. PREDICTED]  Statistical ML estimations P(Y|X) or E[Y|X] conditioned on feature vectors
       ↓
[3. ASSUMED]    User-defined scenario levers (ΔD, ΔL, ΔO) and baseline business constants
       ↓
[4. PROPAGATED] Algorithmic cross-domain translation rules across operational domains
       ↓
[5. CALCULATED] Deterministic managerial accounting and financial profit/loss formulas
       ↓
[6. RECOMMENDED] Rule-grounded strategic action syntheses triggered by risk thresholds
```

> [!IMPORTANT]
> **Non-Causal Epistemic Claim:** Predictions are strictly conditional statistical associations ($P(Y \mid X)$). Cross-domain interactions are deterministic propagation hypotheses layered on top of independently trained predictive models. DecisionSphere makes no unverified claims of physical or economic causality.

---

## 2. The 13-Stage End-to-End Analytical Pipeline

The system executes a deterministic 13-stage linear pipeline:

```
[Stage 1: Multi-Source Ingestion & Schema Validation]
                ↓
[Stage 2: Anti-Leakage Feature Engineering & Registry Verification]
                ↓
[Stage 3: Offline Model Artifact Integrity Verification (Gate H: SHA-256)]
                ↓
[Stage 4: Scenario Parameter Ingestion & Range Validation (Pydantic v2)]
                ↓
[Stage 5: Retail Demand Recursive Forecasting (XGBoost Regressor)]
                ↓
[Stage 6: Cross-Domain Logistics Propagation (Volume & Strain Scaling)]
                ↓
[Stage 7: Calibrated Late Delivery Classification (Gate G: Sigmoid Calibrated)]
                ↓
[Stage 8: Cross-Domain Workforce Propagation (Overtime Strain Scaling)]
                ↓
[Stage 9: Calibrated Workforce Attrition Classification (Gate G: Sigmoid Calibrated)]
                ↓
[Stage 10: Deterministic Managerial Accounting Engine (Revenue, COGS, Disruption, Labor)]
                ↓
[Stage 11: Composite Risk Normalization & Scoring (Simplex-Weighted CRS)]
                ↓
[Stage 12: Rule-Grounded Strategic Action Synthesis (Gate I: Decision Categorization)]
                ↓
[Stage 13: Cryptographic Provenance Packaging & REST API / UI Presentation]
```

---

## 3. Machine Learning Architectures & Training Protocols

### 3.1 Domain 1: Retail Demand Forecasting
- **Dataset:** Rossmann Store Sales (1,115 stores, 1,017,209 daily records).
- **Target Variable:** `Sales` (daily units sold).
- **Anti-Leakage Partitioning:** Strict chronological split.
  - Training: 2013-01-01 to 2014-12-31.
  - Evaluation / Test Holdout: 2015-01-01 to 2015-07-31.
  - No random shuffling. Rolling features and lag buffers ($t-1, t-7, t-14, t-28$) are calculated strictly using preceding observations.
- **Model Hierarchy & Empirical Benchmark:**
  - Level 0 (Naive 7-day Seasonal): $\text{MAE} = 2,398.31$, $\text{RMSE} = 3,275.60$, $\text{WAPE} = 33.32\%$.
  - Level 1 (Ridge Linear Regression): $\text{MAE} = 862.57$, $\text{RMSE} = 1,205.38$, $\text{WAPE} = 11.98\%$.
  - Level 2 (XGBoost Regressor): $\text{MAE} = 584.49$, $\text{RMSE} = 838.83$, $\text{WAPE} = 8.12\%$.
- **Explainability:** TreeSHAP feature importances confirm promotional status (`Promo`), day of week (`DayOfWeek`), store competition distance, and seasonal lags as primary predictive drivers.

### 3.2 Domain 2: Supply Chain Late Delivery Classification
- **Dataset:** DataCo Smart Supply Chain for Big Data Analysis (180,519 order shipments).
- **Target Variable:** `Late_delivery_risk` (binary: 1 = late delivery, 0 = on-time delivery).
- **Anti-Leakage Invariant:** Order-time predictor registry. Strict exclusion of post-checkout variables (`Shipping date`, `Actual shipping days`, carrier tracking logs) via `PROHIBITED_LOOKAHEAD_COLUMNS`.
- **Model Hierarchy & Empirical Benchmark:**
  - Level 0 (Majority Class Baseline): $\text{ROC-AUC} = 0.5000$.
  - Level 1 (Logistic Regression): $\text{ROC-AUC} = 0.7520$, $\text{PR-AUC} = 0.8216$.
  - Level 2 (XGBoost Classifier): $\text{ROC-AUC} = 0.7795$, $\text{PR-AUC} = 0.8423$, $\text{Brier} = 0.1807$.
- **Probabilistic Calibration:** Calibrated post-training using Sigmoid (Platt Scaling) via `FrozenEstimator` on independent validation partition, driving Expected Calibration Error (ECE) to $0.0142$. Optimal threshold $\tau^* = 0.17$ yields $F_1 = 0.7224$, $\text{Recall} = 1.0000$.

### 3.3 Domain 3: Workforce Attrition Risk Classification
- **Dataset:** IBM HR Analytics Employee Attrition & Performance (1,470 employee records).
- **Target Variable:** `Attrition` (binary: 1 = voluntary turnover, 0 = retained).
- **Anti-Leakage Partitioning:** Stratified holdout partition (80% train, 20% test). All encoders, scalers, and imputers fitted strictly on training partition.
- **Model Hierarchy & Empirical Benchmark:**
  - Level 0 (Class Ratio Naive Baseline): $\text{PR-AUC} = 0.1629$.
  - Level 1 (Logistic Regression): $\text{PR-AUC} = 0.6190$, $\text{ROC-AUC} = 0.8330$.
  - Level 2 (XGBoost Classifier): $\text{PR-AUC} = 0.5030$, $\text{ROC-AUC} = 0.8045$, $\text{Brier} = 0.1086$, $\text{ECE} = 0.0537$.
- **Probabilistic Calibration:** Calibrated via Sigmoid `FrozenEstimator`. Optimal threshold $\tau^* = 0.21$ yields $F_1 = 0.4706$, $\text{Recall} = 0.5556$, $\text{Specificity} = 0.8432$.
- **Explainability:** Top predictive TreeSHAP contributors: `OverTime` (0.4450), `StockOptionLevel` (0.3434), `MonthlyIncome` (0.2698), `Age` (0.2413), and `JobRole` (0.2398).

---

## 4. Deterministic Cross-Domain Scenario Propagation

User scenario parameters propagate across domains through explicit mathematical coupling equations:

### 4.1 Demand to Supply Chain Coupling
When user applies a demand shock $\Delta D$, promotional campaign flag $P$, and lead time SLA offset $\Delta L$:
1. Operational order dispatch volume scales:
   $$\text{Order Volume}_{\text{scen}} = \text{Order Volume}_{\text{base}} \times (1 + \Delta D)$$
2. Dispatch strain alters fulfillment features entering the calibrated logistics model:
   - Shipping mode sensitivity (`Shipping Mode_Standard Class` vs `First Class`)
   - Order-to-ship lead time target adjusted by $\Delta L$.
3. Evaluated scenario late delivery probability:
   $$\hat{P}_{\text{late, scen}} = \text{Model}_{\text{supply}}(\mathbf{x}_{\text{scen}})$$

### 4.2 Demand and Operations to Workforce Coupling
When operational demand expands or management imposes mandatory overtime:
1. Overtime hours requirement expands proportionally:
   $$\text{OT\%}_{\text{scen}} = \min(1.0, \text{OT\%}_{\text{base}} + \Delta O)$$
2. Binary overtime indicator in workforce feature vector reflects mandatory schedule:
   $$\text{OverTime}_{\text{scen}} = 1 \quad \text{if } \text{OT\%}_{\text{scen}} > 0.25 \text{ else } 0$$
3. Evaluated scenario turnover probability:
   $$\hat{P}_{\text{attr, scen}} = \text{Model}_{\text{workforce}}(\mathbf{x}_{\text{scen}})$$

---

## 5. Deterministic Managerial Accounting Engine

Financial outcomes are calculated through transparent accounting formulas with zero LLM fabrication:

1. **Gross Revenue Delta:**
   $$\Delta \text{Gross Revenue} = \Delta \text{Units} \times \bar{P}$$
   *(where $\bar{P} = \$1.00$ normalized retail price unit)*
2. **Realized Revenue Delta (Fulfillment-Discounted):**
   $$\Delta \text{Realized Revenue} = \Delta \text{Gross Revenue} \times (1 - \hat{P}_{\text{late, scen}} \times c_{\text{fulfillment\_loss}})$$
3. **Cost of Goods Sold (COGS) Delta:**
   $$\Delta \text{COGS} = \Delta \text{Units} \times c_{\text{cogs\_unit}} \quad (c_{\text{cogs\_unit}} = \$0.56133)$$
4. **Logistics Disruption Cost Delta:**
   $$\Delta \text{Logistics Cost} = \text{Orders} \times (\hat{P}_{\text{late, scen}} - \hat{P}_{\text{late, base}}) \times c_{\text{delay\_penalty}} + \text{Volume Adjustment}$$
5. **Workforce & Overtime Cost Delta:**
   $$\Delta \text{Labor Cost} = W \times \bar{S}_{\text{hourly}} \times (\text{OT Hours}_{\text{scen}} \times 1.5 - \text{OT Hours}_{\text{base}}) + W \times \Delta \hat{P}_{\text{attr}} \times c_{\text{replacement}}$$
6. **Net Operating Profit Delta ($\Delta \Pi$):**
   $$\Delta \Pi = \Delta \text{Realized Revenue} - \Delta \text{COGS} - \Delta \text{Logistics Cost} - \Delta \text{Labor Cost}$$

---

## 6. Composite Risk Score & Recommendation Synthesis

### 6.1 Composite Risk Score (CRS)
The Composite Risk Score is a normalized $[0, 100]$ index defined across three normalized domain strains:
$$\text{CRS} = w_{\text{supply}} S_{\text{supply}} + w_{\text{workforce}} S_{\text{workforce}} + w_{\text{demand}} S_{\text{demand}}$$
- Default simplex weights: $w_{\text{supply}} = 0.40$, $w_{\text{workforce}} = 0.35$, $w_{\text{demand}} = 0.25$ ($\sum w_i = 1.0$).
- Risk classification bands:
  - **LOW:** $\text{CRS} < 30.0$
  - **MODERATE:** $30.0 \le \text{CRS} < 60.0$
  - **HIGH:** $60.0 \le \text{CRS} < 75.0$
  - **CRITICAL:** $\text{CRS} \ge 75.0$

### 6.2 Decision Categorization
The system assigns a strategic classification based on risk and profit boundaries:
- **`APPROVE`**: $\Delta \Pi \ge 0$ and $\text{CRS} < 30.0$.
- **`APPROVE_WITH_CONDITIONS`**: $\Delta \Pi \ge 0$ and $30.0 \le \text{CRS} < 60.0$.
- **`REJECT_RESTRUCTURE`**: $\Delta \Pi < 0$ or $60.0 \le \text{CRS} < 75.0$.
- **`CRITICAL_REJECT`**: $\Delta \Pi < -\$100,000$ and $\text{CRS} \ge 75.0$.

### 6.3 Rule-Grounded Recommendation Engine (RULE-01 to RULE-07)
| Rule ID | Trigger Condition | Recommended Strategic Action | Priority |
|---|---|---|---|
| **RULE-01** | Late delivery risk $\ge 60\%$ or delay $\ge 3$ days | `ACT-SC-001`: Activate Secondary Supplier Buffer & Dynamic Carrier Re-routing | HIGH |
| **RULE-02** | Late delivery risk $\ge 75\%$ and shipping is Express | `ACT-SC-002`: Enforce Carrier SLA Penalty & Switch Tier-1 Logistics Partner | CRITICAL |
| **RULE-03** | Attrition probability $\ge 25\%$ or overtime $\ge 30\%$ | `ACT-HR-001`: Enforce Overtime Caps & Implement Retention Retention Incentives | HIGH |
| **RULE-04** | $\Delta \Pi < 0$ and demand shock $> 0$ | `ACT-FIN-001`: Margin Erosion Warning: Rescale Promotional Intensity | CRITICAL |
| **RULE-05** | Inventory turnover $< 3.0$ or stockout risk $\ge 40\%$ | `ACT-OPS-001`: Rebalance Safety Stock Parameters & Expedite Replenishment | MEDIUM |
| **RULE-06** | $\text{CRS} \ge 75.0$ (Systemic Critical Risk) | `ACT-SYS-001`: Circuit Breaker: Halt Unconstrained Scenario Execution | CRITICAL |
| **RULE-07** | $\Delta \Pi \ge 0$ and $\text{CRS} < 30.0$ (Optimal Profile) | `ACT-STRAT-001`: Greenlight Expansion with Routine Quarterly Governance | LOW |

---

## 7. Governance Quality Gates

1. **Gate G (Probabilistic Calibration):** Verified Sigmoid/Isotonic calibration bounds ensuring classification scores represent empirical probabilities.
2. **Gate H (Cryptographic Model Integrity):** SHA-256 hash checks verifying that model binaries in `models/` match verified reference signatures before inference.
3. **Gate I (Policy Interlock):** Prevents automated scenario approval if $\text{CRS} \ge 60$ or $\Delta \Pi < 0$.
