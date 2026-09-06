# DecisionSphere: Research Paper — Chapter 5: Data Benchmarks & Empirical Inventory

**Section:** 4. Data Benchmarks & Empirical Audit  
**Context:** Empirical Properties, Target Distributions, and Candidate Dataset Evaluation

---

### 4.1 Benchmark Selection Rationale
To construct a realistic, normalized enterprise decision environment, DecisionSphere integrates three public, peer-reviewed, open-access enterprise benchmarks:

| Dataset Identifier | Domain | Source / Publication | Dimensions | Target Variable | Nature of Target |
|:---|:---|:---|:---|:---|:---|
| **Rossmann Store Sales** | Commercial Demand | Kaggle / Rossmann GmbH (2015) | 1,017,209 rows, 10 cols | `Sales` (Daily Store Sales) | Continuous, Non-negative |
| **DataCo Smart Supply Chain** | Logistics Fulfillment | Constante et al. (2019) | 180,519 rows, 53 cols | `Late_delivery_risk` | Binary Balanced ($54.8\%$ late) |
| **IBM HR Analytics** | Workforce Retention | IBM Watson Analytics (2017) | 1,470 rows, 35 cols | `Attrition` | Binary Imbalanced ($16.1\%$ yes) |

---

### 4.2 Candidate Datasets Audited and Excluded
During the architectural design phase, several alternative datasets were audited and formally rejected:
1. **Walmart Recruiting Store Sales:** Excluded due to coarse weekly aggregation (lacking daily granularity necessary for 14-day operational horizons) and absence of store-level promotional metadata.
2. **Corporación Favorita Grocery Sales:** Excluded due to massive dataset size ($>125\text{M}$ rows) exceeding single-node laboratory prototyping constraints without offering superior cross-domain features.
3. **SCMS Delivery Health Commodity:** Excluded due to high temporal sparsity and specialized international NGO cold-chain features unsuited for general commercial enterprise modeling.

---

### 4.3 Empirical Characteristics & Target Distributions

#### 4.3.1 Commercial Demand (Rossmann)
The Rossmann benchmark captures daily sales across 1,115 pharmacy stores. Daily sales among open stores exhibit a right-skewed distribution with an empirical mean of $6,955.51$ units and a median of $6,369.00$ units. 
- Promotional status (`Promo=1`) is active on $38.2\%$ of open store days and exhibits a strong historical association with sales volume: mean sales increase from $5,929.50$ units (no promo) to $10,816.08$ units (promo active), representing an empirical promotional lift of $+82.5\%$.
- Weekly seasonality shows peak sales on Mondays ($8,216.42$ mean units) with store closures on Sundays ($1.8\%$ open rate, confined to transit hub stores).

#### 4.3.2 Logistics Delivery (DataCo)
DataCo records 180,519 order shipments spanning four distinct freight modes:
- Standard Class: $59.6\%$ volume, $60.1\%$ late delivery rate (scheduled lead time 4 days).
- Second Class: $19.7\%$ volume, $77.3\%$ late delivery rate (scheduled lead time 2 days).
- First Class: $15.4\%$ volume, $95.3\%$ late delivery rate (scheduled lead time 1 day).
- Same Day: $5.3\%$ volume, $52.3\%$ late delivery rate (scheduled lead time 0 days).
Overall empirical late delivery rate is $54.8\%$, presenting a balanced classification problem.

#### 4.3.3 Workforce Retention (IBM HR)
IBM HR encompasses 1,470 employee records. The dataset is characterized by significant class imbalance, with only $237$ employee departures ($16.1\%$ positive attrition class).
- Mandatory overtime (`OverTime='Yes'`) is assigned to $28.3\%$ of the workforce.
- Employees subject to overtime exhibit an empirical attrition rate of $30.5\%$, compared to $10.4\%$ for regular-hours workers, representing a $2.93\times$ relative risk ratio.
- Work-Life Balance ratings (4-point scale) show an inverse relationship with turnover: Level 1 (Bad) workers exhibit $27.8\%$ attrition, compared to $14.2\%$ for Level 3 (Better).
