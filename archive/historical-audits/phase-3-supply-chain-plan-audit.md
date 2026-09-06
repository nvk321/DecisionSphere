# DecisionSphere — Phase 3 Plan Audit & Scientific Methodology Review

## 1. Executive Summary & Audit Mandate

In accordance with the DecisionSphere research-integrity protocol, this document performs a comprehensive pre-implementation audit of the **Phase 3: Supply Chain Delivery Risk Classification Pipeline** against:
- `docs/research-direction.md` (Scientific foundation, RQs, and Hypotheses $H_1$–$H_4$)
- `docs/literature-gap-matrix.md` (Adjacent literature and exact differentiation)
- `docs/experimental-design.md` (Protocols for Experiments A, B, C, and D)
- `docs/assumptions-and-open-questions.md` (The Parametric Assumptions Registry)
- `docs/data-audit-report.md` (Empirical dataset audit and leakage matrix)
- `AGENTS.md` (Section 13: Academic Research & Publication Protocol)

**Core Conclusion:** The proposed Phase 3 implementation is scientifically sound, but requires explicit methodological corrections regarding probability calibration, temporal split boundaries, target semantics, identifier leakage exclusion, and non-causal scenario terminology before code execution begins.

---

## 2. Empirical Verification of DataCo Dataset Statistics

The DataCo dataset was extracted and verified directly from the authoritative source archive `reference/archive (2).zip` (`DataCoSupplyChainDataset.csv`). All metrics are computed from the raw data:

| Metric | Proposed Plan Value | Verified Empirical Reality | Verification Status |
|---|---|---|---|
| **Total Rows** | 180,519 | **180,519** | Verified Exact |
| **Total Columns** | 53 | **53** | Verified Exact |
| **Unique Orders (`Order Id`)** | ~180k (implied) | **65,752** (Multiple item rows per order) | **Corrected:** Orders are multi-item |
| **Unique Customers (`Customer Id`)** | ~20k | **20,652** | Verified Exact |
| **Unique Products (`Product Card Id`)** | ~118 | **118** | Verified Exact |
| **Duplicate Rows** | 0 | **0** (100% distinct line item records) | Verified Exact |
| **Target Variable** | `Late_delivery_risk` | `Late_delivery_risk` (`int64`: $\{0, 1\}$) | Verified Exact |
| **Positive Class (Late = 1)** | ~54.8% | **98,977 rows (54.8291%)** | Verified Exact |
| **Negative Class (On-Time = 0)** | ~45.2% | **81,542 rows (45.1709%)** | Verified Exact |
| **Earliest Order Date** | 2015-01-01 | **2015-01-01 00:00:00** | Verified Exact |
| **Latest Order Date** | 2018-01-31 | **2018-01-31 23:38:00** | Verified Exact |
| **Temporal Span** | 1,126 days | **1,126 days (3.08 years)** | Verified Exact |

---

## 3. Target Definition & Causal Demarcation

### Target Semantics & Empirical Derivation
- Target column name: `Late_delivery_risk` (binary integer: $0$ or $1$).
- Empirical cross-tabulation with realized delivery states demonstrates:
  - `Late delivery`: $98,977$ records $\rightarrow$ **100.0%** have `Late_delivery_risk = 1`.
  - `Advance shipping`: $41,592$ records $\rightarrow$ **100.0%** have `Late_delivery_risk = 0`.
  - `Shipping on time`: $32,196$ records $\rightarrow$ **100.0%** have `Late_delivery_risk = 0`.
  - `Shipping canceled`: $7,754$ records $\rightarrow$ **100.0%** have `Late_delivery_risk = 0`.
- Furthermore, checking $(Days\ for\ shipping\ (real) > Days\ for\ shipment\ (scheduled))$ matches `Late_delivery_risk` in **97.55%** of records.
- **Scientific Formulation:** The target is an observed historical outcome indicating whether an order item was delayed past its contractual SLA dispatch schedule.
- **Prediction Formulation:**
  $$P(\text{Late Delivery Risk} = 1 \mid \mathbf{X}_{\text{order\_time}})$$
  Where $\mathbf{X}_{\text{order\_time}}$ contains strictly information observed at or before checkout.
- **Language Protocol:** We do NOT claim to "predict actual future delivery outcomes causally." We describe the model output strictly as **"conditional late-delivery risk prediction given order-time operational configurations."**

---

## 4. Full 53-Column Feature-Timing & Identifier Audit

Every column in `DataCoSupplyChainDataset.csv` is audited and categorized into one of six operational tiers:

| Index | Column Name | Data Type | Missing Count | Operational Timing | Classification | Final Action & Academic Rationale |
|---|---|---|---|---|---|---|
| 00 | `Type` | `str` | 0 | Checkout | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Payment type (DEBIT, TRANSFER, PAYMENT, CASH). Known at checkout. |
| 01 | `Days for shipping (real)` | `int64` | 0 | Post-Delivery | **C. REALIZED OUTCOME / LOOKAHEAD** | **STRICTLY EXCLUDED.** Real delivery duration. Direct target leakage. |
| 02 | `Days for shipment (scheduled)` | `int64` | 0 | Dispatch Planning | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Planned SLA lead time (0, 1, 2, 4 days). Core scenario lever. |
| 03 | `Benefit per order` | `float64` | 0 | Post-Fulfillment | **D. POST-TRANSACTION ACCOUNTING** | **STRICTLY EXCLUDED.** Realized accounting profit post-delivery. |
| 04 | `Sales per customer` | `float64` | 0 | Post-Fulfillment | **D. POST-TRANSACTION ACCOUNTING** | **STRICTLY EXCLUDED.** Realized post-sale net revenue. |
| 05 | `Delivery Status` | `str` | 0 | Post-Delivery | **C. REALIZED OUTCOME / LOOKAHEAD** | **STRICTLY EXCLUDED.** 100% deterministic target leak. |
| 06 | `Late_delivery_risk` | `int64` | 0 | Outcome Label | **TARGET VARIABLE** | **TARGET.** Ground-truth historical label. |
| 07 | `Category Id` | `int64` | 0 | Catalog Metadata | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Discrete product category ID (51 categories). |
| 08 | `Category Name` | `str` | 0 | Catalog Metadata | **F. AMBIGUOUS / REDUNDANT** | **EXCLUDED.** Redundant with `Category Id`. |
| 09 | `Customer City` | `str` | 0 | Checkout Address | **E. HIGH-CARDINALITY SURROGATE** | **EXCLUDED.** 563 cities; high sparsity and memorization risk. |
| 10 | `Customer Country` | `str` | 0 | Checkout Address | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Buyer country (Puerto Rico, EE. UU.). 2 values. |
| 11 | `Customer Email` | `str` | 0 | Registration | **E. PII / SURROGATE** | **STRICTLY EXCLUDED.** Masked PII string. |
| 12 | `Customer Fname` | `str` | 0 | Registration | **E. PII / SURROGATE** | **STRICTLY EXCLUDED.** Personal name text. |
| 13 | `Customer Id` | `int64` | 0 | Account Key | **E. PII / IDENTIFIER** | **STRICTLY EXCLUDED.** 20,652 unique IDs; memorization risk. |
| 14 | `Customer Lname` | `str` | 8 | Registration | **E. PII / SURROGATE** | **STRICTLY EXCLUDED.** Personal surname text. |
| 15 | `Customer Password` | `str` | 0 | Security | **E. PII / SURROGATE** | **STRICTLY EXCLUDED.** Masked password text. |
| 16 | `Customer Segment` | `str` | 0 | Account Metadata | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Consumer, Corporate, Home Office (3 categories). |
| 17 | `Customer State` | `str` | 0 | Checkout Address | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Buyer US state code (46 states). Categorical encoding. |
| 18 | `Customer Street` | `str` | 0 | Checkout Address | **E. PII / SURROGATE** | **STRICTLY EXCLUDED.** Street address text (7,458 unique). |
| 19 | `Customer Zipcode` | `int64` | 3 | Checkout Address | **E. HIGH-CARDINALITY SURROGATE** | **EXCLUDED.** High sparsity zip code; missing values present. |
| 20 | `Department Id` | `int64` | 0 | Catalog Metadata | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Internal department ID (11 departments). |
| 21 | `Department Name` | `str` | 0 | Catalog Metadata | **F. AMBIGUOUS / REDUNDANT** | **EXCLUDED.** Redundant with `Department Id`. |
| 22 | `Latitude` | `float64` | 0 | Store Location | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Origin store geographic coordinate. |
| 23 | `Longitude` | `float64` | 0 | Store Location | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Origin store geographic coordinate. |
| 24 | `Market` | `str` | 0 | Logistics Hub | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Destination global market (5 regions). Core routing feature. |
| 25 | `Order City` | `str` | 0 | Destination Address | **E. HIGH-CARDINALITY SURROGATE** | **EXCLUDED.** 3,597 destination cities; memorization risk. |
| 26 | `Order Country` | `str` | 0 | Destination Address | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Destination country code (164 countries). Grouped/encoded. |
| 27 | `Order Customer Id` | `int64` | 0 | Transaction Record | **E. PII / IDENTIFIER** | **STRICTLY EXCLUDED.** Duplicate of `Customer Id`. |
| 28 | `order date (DateOrders)` | `str` | 0 | Order Timestamp | **B. VALID DERIVED ORDER-TIME FEATURE** | **TEMPORAL ANCHOR.** Decomposed into year, month, day, day_of_week, hour. |
| 29 | `Order Id` | `int64` | 0 | Transaction Key | **E. SURROGATE KEY** | **STRICTLY EXCLUDED.** 65,752 unique IDs. Pure memorization risk. |
| 30 | `Order Item Cardprod Id` | `int64` | 0 | Line Item Key | **E. SURROGATE KEY** | **STRICTLY EXCLUDED.** Duplicate of `Product Card Id`. |
| 31 | `Order Item Discount` | `float64` | 0 | Checkout | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Discount dollar amount applied at purchase. |
| 32 | `Order Item Discount Rate` | `float64` | 0 | Checkout | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Percentage discount applied ($0.00$ to $0.25$). |
| 33 | `Order Item Id` | `int64` | 0 | Line Item Key | **E. SURROGATE KEY** | **STRICTLY EXCLUDED.** Primary key (180,519 unique). Zero predictive generalization. |
| 34 | `Order Item Product Price` | `float64` | 0 | Checkout | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Unit price of purchased catalog item. |
| 35 | `Order Item Profit Ratio` | `float64` | 0 | Post-Fulfillment | **D. POST-TRANSACTION ACCOUNTING** | **STRICTLY EXCLUDED.** Margin ratio realized post-delivery. |
| 36 | `Order Item Quantity` | `int64` | 0 | Checkout | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Ordered line quantity ($1$ to $5$). Core volume lever. |
| 37 | `Sales` | `float64` | 0 | Checkout | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Gross line total before discount (`Price` $\times$ `Qty`). |
| 38 | `Order Item Total` | `float64` | 0 | Checkout | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Net checkout amount paid by customer. |
| 39 | `Order Profit Per Order` | `float64` | 0 | Post-Fulfillment | **D. POST-TRANSACTION ACCOUNTING** | **STRICTLY EXCLUDED.** Realized accounting profit per order. |
| 40 | `Order Region` | `str` | 0 | Logistics Hub | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Destination geographic delivery region (23 regions). |
| 41 | `Order State` | `str` | 0 | Destination Address | **E. HIGH-CARDINALITY SURROGATE** | **EXCLUDED.** 1,089 destination states/provinces; high sparsity. |
| 42 | `Order Status` | `str` | 0 | Post-Fulfillment State | **C. REALIZED OUTCOME / LOOKAHEAD** | **STRICTLY EXCLUDED.** Fulfillment state (COMPLETE, CLOSED, etc.). |
| 43 | `Order Zipcode` | `float64` | 155,679 | Destination Address | **E. UNINFORMATIVE / MISSING** | **STRICTLY EXCLUDED.** 86.24% missing values. |
| 44 | `Product Card Id` | `int64` | 0 | Catalog Metadata | **E. HIGH-CARDINALITY SURROGATE** | **EXCLUDED.** 118 catalog IDs; 87.7% unseen in test. High memorization risk. |
| 45 | `Product Category Id` | `int64` | 0 | Catalog Metadata | **E. REDUNDANT KEY** | **EXCLUDED.** Exact duplicate of `Category Id`. |
| 46 | `Product Description` | `float64` | 180,519 | Catalog Metadata | **E. UNINFORMATIVE / MISSING** | **STRICTLY EXCLUDED.** 100.0% missing values (all rows NaN). |
| 47 | `Product Image` | `str` | 0 | Catalog Metadata | **E. UNINFORMATIVE URL** | **STRICTLY EXCLUDED.** External URL string. |
| 48 | `Product Name` | `str` | 0 | Catalog Metadata | **E. HIGH-CARDINALITY TEXT** | **EXCLUDED.** Product title string; cleanly represented by `Category Id`. |
| 49 | `Product Price` | `float64` | 0 | Catalog Metadata | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Catalog retail list price. |
| 50 | `Product Status` | `int64` | 0 | Catalog Metadata | **E. ZERO-VARIANCE CONSTANT** | **STRICTLY EXCLUDED.** Invariant column: all rows equal $0$. |
| 51 | `shipping date (DateOrders)` | `str` | 0 | Post-Order Dispatch | **C. REALIZED OUTCOME / LOOKAHEAD** | **STRICTLY EXCLUDED.** Physical dispatch timestamp. Unknown at order time. |
| 52 | `Shipping Mode` | `str` | 0 | Dispatch Planning | **A. VALID ORDER-TIME PREDICTOR** | **RETAIN.** Planned freight class (Standard, First, Second, Same Day). Core scenario lever. |

---

## 5. Correct Temporal Splitting Protocol

### Correction from Proposed Plan
The initial plan proposed `Train <= 2017-04-30` and `Val <= 2017-09-30`. Empirical audit of the monthly distribution showed that order volumes drop from ~5,200/month to ~2,100/month after September 2017. Splitting at April 2017 created an overly small test set (only 4.74% of records).

### Verified Clean Calendar Splitting
We adopt a clean calendar-boundary split that eliminates seasonal bias across full calendar years and guarantees $\max(\text{train}) < \min(\text{val}) < \min(\text{test})$:

| Partition | Start Timestamp | End Timestamp | Calendar Duration | Row Count | % of Dataset | Late Count (1) | On-Time Count (0) | Late Prevalence |
|---|---|---|---|---|---|---|---|---|
| **TRAIN** | `2015-01-01 00:00:00` | `2016-12-31 23:51:00` | **24 Months (2 Full Years)** | **125,200** | **69.36%** | 68,818 | 56,382 | **54.97%** |
| **VALIDATION** | `2017-01-01 00:33:00` | `2017-06-30 23:25:00` | **6 Months (H1 2017)** | **30,950** | **17.15%** | 16,729 | 14,221 | **54.05%** |
| **TEST** | `2017-07-01 00:07:00` | `2018-01-31 23:38:00` | **7 Months (H2 2017 + Jan 2018)** | **24,369** | **13.50%** | 13,430 | 10,939 | **55.11%** |
| **TOTAL** | `2015-01-01 00:00:00` | `2018-01-31 23:38:00` | **37 Months (1,126 Days)** | **180,519** | **100.00%** | 98,977 | 81,542 | **54.83%** |

- **Strict Temporal Integrity:** Zero temporal overlap ($\max(\text{train}) < \min(\text{val}) < \min(\text{test})$).
- **Target Stability:** Remarkably consistent base rate ($54.97\%$ vs. $54.05\%$ vs. $55.11\%$).
- **Distribution Shift Note:** Test set captures the late-2017 volume moderation, providing a natural robustness evaluation.

---

## 6. Model Hierarchy & Probability Calibration Protocol

### 6.1 Multi-Level Baseline Hierarchy
1. **Level 0a (Naive Majority Class):** Constant prediction $\hat{y} = 1$.
2. **Level 0b (Prevalence Probability Baseline):** Constant probability $\hat{P} = \bar{y}_{\text{train}} = 0.549665$. Serves as the proper probability baseline for Brier Score and PR-AUC.
3. **Level 1 (Linear Baseline):** `LogisticRegression` with `StandardScaler` on numerical features and `OneHotEncoder(handle_unknown='ignore')` on categorical features.
4. **Level 2 (Tree Classifier):** `XGBClassifier` (`tree_method='hist'`).

### 6.2 Strict Probability Calibration Protocol
- An XGBoost classifier's `predict_proba` is an uncalibrated score $\hat{P}_{\text{raw}} \in [0, 1]$.
- **Calibration Procedure:**
  - Fit Level 2 model on $(X_{\text{train}}, y_{\text{train}})$.
  - Evaluate raw validation probabilities $\hat{P}_{\text{raw}}(y=1 \mid X_{\text{val}})$.
  - Fit `CalibratedClassifierCV(model, method='sigmoid', cv='prefit')` strictly on $(X_{\text{val}}, y_{\text{val}})$.
  - Compare validation Brier score and reliability curves between $\hat{P}_{\text{raw}}$ and $\hat{P}_{\text{cal}}$.
  - Retain calibrated model only if validation Brier score improves.
  - **The final test set remains completely untouched until final evaluation.**

### 6.3 Threshold Selection Protocol
- The classification decision threshold $\tau^*$ is selected **strictly on the validation set** to maximize balanced validation F1-score:
  $$\tau^* = \arg\max_{\tau \in [0.1, 0.9]} F_1(\mathbf{y}_{\text{val}}, \hat{P}_{\text{val}} \ge \tau)$$
- **Zero test labels are ever inspected during threshold selection.** The threshold $\tau^*$ is serialized into model metadata and applied deterministically to test inferences.

---

## 7. Explainability & Scenario Simulation Semantics

### 7.1 TreeSHAP Non-Predetermined Protocol
- SHAP feature attributions will be computed empirically using TreeSHAP on a representative sample of test observations ($N=2,000$).
- Feature rankings are determined strictly by empirical mean absolute SHAP values:
  $$I_j = \frac{1}{N} \sum_{i=1}^{N} |\phi_j^{(i)}|$$
- Local explanations will report:
  *"The fitted model associated [Feature State] with an adjusted predicted risk of $\Delta P$ relative to the baseline expectation."*
  (Strictly avoiding causal claims such as "Feature caused the delay").

### 7.2 Scenario Simulation Interface & Epistemic Demarcation
- Function: `simulate_scenario(orders_df, shipping_mode_override=None, scheduled_days_offset=0)`
- `scheduled_days_offset`: Modifies the *planned SLA duration* (`days_for_shipment_scheduled`), representing a compressed delivery window. (Realized shipping delay is strictly prohibited).
- Return schema:
  ```json
  {
    "baseline_probability": 0.4215,
    "scenario_probability": 0.5680,
    "delta_probability": 0.1465,
    "scenario_definition": {"shipping_mode": "First Class", "scheduled_days_offset": -1},
    "epistemic_tier": "PREDICTED"
  }
  ```
- **Monotonicity Diagnostic:** Evaluated via a parameter sweep across scheduled days $[1, 2, 3, 4]$ and reported empirically as monotonic, approximately monotonic, or non-monotonic without forcing or falsifying the model's learned response.

---

## 8. Alignment with Paper Contributions (RQ1 & RQ3)

The Phase 3 Supply Chain model is designed specifically as an empirical component supporting:
1. **RQ1 (Cross-Domain Trade-Off Discovery):** Exposes downstream delivery risk increases when promotional demand surges saturate standard shipping channels, feeding the Business Impact Engine (Experiment A).
2. **RQ3 (Explainability & Decision Defensibility):** Local TreeSHAP attributions identify whether logistics lead times or geographic bottlenecks dominate risk, providing auditable grounding for recommendation rules (Experiment C).
