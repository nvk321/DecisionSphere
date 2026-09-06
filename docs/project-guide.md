# DecisionSphere: The Complete Master Project Guide
**From Zero Knowledge to Research-Grade Strategic Decision Intelligence**
*Authoritative Documentation & Pedagogical Reference Layer*

---

## Executive Table of Contents

1. [What DecisionSphere Is](#1-what-decisionsphere-is)
2. [The Business Problem: The Hidden Cost of Siloed Decisions](#2-the-business-problem-the-hidden-cost-of-siloed-decisions)
3. [Why Ordinary Dashboards Are Insufficient](#3-why-ordinary-dashboards-are-insufficient)
4. [What Decision Intelligence Means](#4-what-decision-intelligence-means)
5. [Core Concepts: Scenarios, Levers, Shocks, and Baselines](#5-core-concepts-scenarios-levers-shocks-and-baselines)
6. [The Data Foundation: Origins, Scope, and Data Dictionaries](#6-the-data-foundation-origins-scope-and-data-dictionaries)
7. [Why Three Domains Exist: The Operational Triad](#7-why-three-domains-exist-the-operational-triad)
8. [The Predictive Machine Learning Layer](#8-the-predictive-machine-learning-layer)
9. [How XGBoost Works in DecisionSphere](#9-how-xgboost-works-in-decisionsphere)
10. [Probability Calibration: Why Raw Model Probabilities Lie](#10-probability-calibration-why-raw-model-probabilities-lie)
11. [Explainable AI: TreeSHAP and Feature Contributions](#11-explainable-ai-treeshap-and-feature-contributions)
12. [Cross-Domain Parameter Propagation](#12-cross-domain-parameter-propagation)
13. [Managerial Financial Accounting: Why Sales Increases Destroy Margin](#13-managerial-financial-accounting-why-sales-increases-destroy-margin)
14. [Operational Strain: The Composite Risk Score (CRS)](#14-operational-strain-the-composite-risk-score-crs)
15. [Deterministic Recommendation & Policy Rules](#15-deterministic-recommendation--policy-rules)
16. [Auditing and Provenance: The Sigma Run Tuple](#16-auditing-and-provenance-the-sigma-run-tuple)
17. [Quality and Architecture Gates: Gates G, H, and I](#17-quality-and-architecture-gates-gates-g-h-and-i)
18. [Backend Service Layer: FastAPI Architecture](#18-backend-service-layer-fastapi-architecture)
19. [Presentation Layer: Next.js Decision Interface](#19-presentation-layer-nextjs-decision-interface)
20. [The Scientific Research & Jupyter Laboratory Layer](#20-the-scientific-research--jupyter-laboratory-layer)
21. [The Canonical Worked Example: Tracing a +15% Demand Shock](#21-the-canonical-worked-example-tracing-a-15-demand-shock)
22. [Epistemic Boundaries: Prediction vs Causation](#22-epistemic-boundaries-prediction-vs-causation)
23. [Assumptions, Limitations, and Threats to Validity](#23-assumptions-limitations-and-threats-to-validity)
24. [Step-by-Step Reproducibility Guide](#24-step-by-step-reproducibility-guide)

---

## 1. What DecisionSphere Is

### What It Means
DecisionSphere is a **decision intelligence platform** that evaluates the systemic consequences of hypothetical business decisions across sales, logistics, and human resources *before* those decisions are deployed in the real world.

### Why We Need It
In large enterprises, executives frequently launch promotional campaigns to grow top-line revenue without realizing that warehouse capacity cannot fulfill the resulting surge, leading to shipping delay penalties and excessive employee overtime burnout that destroys overall company profit.

### What DecisionSphere Does With It
DecisionSphere ingests user-defined scenario interventions (such as running a promotional campaign or expediting shipments), propagates those changes through machine learning models across three operational domains, evaluates the financial impact down to net dollar profit, measures organizational strain, and recommends specific strategic mitigations.

### Simple Example
Imagine a bakery manager deciding to offer a "Buy One, Get One Free" sale. Sales of bread double, but the ovens cannot bake fast enough, delivery vans arrive late, customers demand refunds, and bakers quit due to 16-hour work shifts. The bakery lost money despite record sales. DecisionSphere simulates this exact breakdown before the sale is announced.

### Technical Implementation
The analytical core consists of three offline-trained machine learning models:
1. An autoregressive XGBoost Regressor for retail demand forecasting.
2. A Sigmoid-calibrated XGBoost Classifier for supply chain late delivery risk.
3. A Sigmoid-calibrated XGBoost Classifier for workforce attrition risk.
These models are orchestrated by a multi-domain scenario propagation engine (`src/scenario/engine.py`), evaluated by a managerial financial accounting engine (`src/business/engine.py`), scored by a Composite Risk Score engine (`src/recommendation/crs.py`), and audited by a FastAPI service (`backend/app/services/simulation_orchestrator.py`).

### Where It Exists in the Repository
- High-level architecture: [`src/scenario/engine.py`](file:///d:/Projects/DecisionSphere/src/scenario/engine.py#L47-L86)
- System map: [`docs/research-system-map.md`](file:///d:/Projects/DecisionSphere/docs/research-system-map.md#L1-L100)

---

## 2. The Business Problem: The Hidden Cost of Siloed Decisions

### What It Means
Organizational silos occur when separate business departments (Sales, Supply Chain, HR) optimize their own goals independently without coordinating with one another.

### Why We Need It
When departments operate in isolation:
- **Marketing/Sales** is incentivized solely on gross revenue growth.
- **Logistics/Supply Chain** is evaluated on freight costs and on-time delivery rates.
- **Human Resources** is evaluated on headcount turnover and overtime labor budgets.
No single department is accountable for cross-domain friction.

### What DecisionSphere Does With It
DecisionSphere bridges these silos by modeling the operational ripple effects:
$$\text{Commercial Demand Surge} \longrightarrow \text{Logistics Bottleneck} \longrightarrow \text{Workforce Burnout} \longrightarrow \text{Margin Destruction}$$

### Simple Example
A marketing director launches a $20\%$ discount campaign. Sales jump by $15,000$ units, bringing in $\$6,000$ in gross margin. However, the unexpected volume causes 800 packages to miss customer delivery guarantees, incurring $\$20,000$ in carrier delay SLA fines, and forces 30 warehouse staff into mandatory overtime, triggering 2 employee resignations costing $\$60,000$ to re-hire and train. The company loses $\$74,000$ net profit.

### Technical Implementation
The coupling logic connects the retail sales forecast ($\hat{Y}_{\text{sales}}$) to warehouse dispatch orders via normalization parameters `ASM-007` and `ASM-008`, and connects dispatch volume to workforce overtime percentage via deterministic cohort assignment.

### Where It Exists in the Repository
- Coupling constants: [`src/scenario/assumptions.py`](file:///d:/Projects/DecisionSphere/src/scenario/assumptions.py#L28-L122)
- Multi-domain propagation: [`src/scenario/engine.py`](file:///d:/Projects/DecisionSphere/src/scenario/engine.py#L248-L387)

---

## 3. Why Ordinary Dashboards Are Insufficient

### What It Means
An operational dashboard (e.g., PowerBI, Tableau, Grafana) displays historical observations and current key performance indicators (KPIs).

### Why We Need It
Dashboards answer: *"What happened yesterday?"* or *"What is our inventory level today?"* They cannot answer: *"What will happen to employee attrition if we run a 14-day promotion next month under Standard Class freight?"*

### What DecisionSphere Does With It
DecisionSphere moves beyond descriptive dashboards into **prospective simulation**. Instead of static aggregations, it exposes interactive levers allowing decision-makers to test counterfactual scenarios and inspect the resulting distributions.

### Simple Example
Looking at your car's speedometer tells you that you are driving at 60 mph (dashboard). A navigation simulation tells you that if you take the upcoming highway exit, you will encounter a traffic jam and run out of gas in 12 miles (DecisionSphere).

### Technical Implementation
The system stores immutable scenario versions (`ScenarioVersion`) and executes forward simulation runs through AnyIO worker threads, returning a complete tree of predictive, financial, and strategic results without altering baseline historical records.

### Where It Exists in the Repository
- Asynchronous execution: [`backend/app/services/simulation_orchestrator.py`](file:///d:/Projects/DecisionSphere/backend/app/services/simulation_orchestrator.py#L144-L160)
- REST Endpoints: [`backend/app/api/v1/endpoints/simulations.py`](file:///d:/Projects/DecisionSphere/backend/app/api/v1/endpoints/simulations.py#L25-L65)

---

## 4. What Decision Intelligence Means

### What It Means
Decision Intelligence (DI) is the discipline of combining data science, machine learning, managerial accounting, and decision theory to model how decisions lead to tangible actions and business outcomes.

### Why We Need It
Machine learning models by themselves only output numbers (e.g., $0.62$ probability or $4,200$ units). Executives do not make decisions in probabilities; they make decisions in dollars, operational feasibility, and risk trade-offs.

### What DecisionSphere Does With It
DecisionSphere translates raw statistical predictions ($P(Y \mid X)$) into managerial financial line items (Gross Revenue, Realized Revenue, COGS, Penalties, Overtime Wages, Net Profit Delta), combines them into an operational Composite Risk Score, and executes deterministic policy rules to recommend concrete actions.

### Simple Example
A weather model outputs a $70\%$ probability of rain (raw prediction). Decision Intelligence tells the airport manager: "Close runway 2, fuel planes for a 20-minute holding pattern, and issue delay advisories to terminal passengers" (actionable recommendation).

### Technical Implementation
The Decision Intelligence pipeline follows the strict contract:
$$\text{Feature Vector} \xrightarrow{\text{ML}} \text{Prediction} \xrightarrow{\text{Propagation}} \text{Coupled Impact} \xrightarrow{\text{Accounting}} \text{Dollars} \xrightarrow{\text{Rules}} \text{Actions}$$

### Where It Exists in the Repository
- End-to-end pipeline: [`backend/app/services/simulation_orchestrator.py`](file:///d:/Projects/DecisionSphere/backend/app/services/simulation_orchestrator.py#L98-L132)
- Rule synthesis: [`src/recommendation/engine.py`](file:///d:/Projects/DecisionSphere/src/recommendation/engine.py#L44-L180)

---

## 5. Core Concepts: Scenarios, Levers, Shocks, and Baselines

### 5.1 Baseline
- **What It Means:** The observed historical state of the business without any new interventions.
- **DecisionSphere Usage:** Represents baseline demand ($\text{Promo}=0$), baseline logistics delivery risk (historical shipping mode distribution), and baseline workforce attrition ($29.4\%$ overtime).
- **Epistemic Tier:** `OBSERVED`.

### 5.2 Scenario
- **What It Means:** A cohesive bundle of hypothetical assumptions and operational levers representing a proposed business initiative.
- **DecisionSphere Usage:** Identified by an immutable `scenario_id` and versioned under `ScenarioVersion`.

### 5.3 Lever
- **What It Means:** An operational parameter directly controllable by the decision-maker.
- **DecisionSphere Levers:**
  1. `demand_growth_pct`: Sales volume adjustment factor ($[-50\%, +100\%]$).
  2. `promo_active`: Commercial promotional flag (`True` / `False`).
  3. `scheduled_days_offset`: Dispatch SLA compression or relaxation ($[-2, +5]$ days).
  4. `shipping_mode_override`: Logistical freight selection (`Standard Class`, `First Class`, etc.).
  5. `overtime_workforce_pct`: Target proportion of workforce assigned to mandatory overtime ($[0\%, 100\%]$).
  6. `salary_hike_override`: Retention compensation adjustment ($[0\%, 35\%]$).

### 5.4 Shock
- **What It Means:** The magnitude of deviation between the user lever and the baseline state ($\Delta \text{Demand} = +15\%$, $\text{LeadTimeOffset} = -1\,\text{day}$).

### Where It Exists in the Repository
- Schema: [`src/scenario/schema.py`](file:///d:/Projects/DecisionSphere/src/scenario/schema.py#L10-L40)

---

## 6. The Data Foundation: Origins, Scope, and Data Dictionaries

DecisionSphere utilizes three benchmark enterprise datasets, each selected for operational granularity and real-world realism.

### 6.1 Retail Demand Dataset (Rossmann Store Sales)
- **Source:** European retail pharmacy chain records (1,115 stores).
- **File Location:** `data/raw/rossmann/train.csv` and `store.csv`.
- **Dimensions:** 1,017,209 daily transaction rows, 9 initial columns.
- **Target Variable:** `Sales` (Continuous, Euros/Units).
- **Key Predictors:**
  - `DayOfWeek`, `Month`, `Day`, `WeekOfYear`, `IsWeekend` (Temporal factors).
  - `Promo` (Binary commercial promotion indicator; historical lift $+82.5\%$).
  - `LogCompetitionDistance`, `CompetitionOpen` (Market structure).
  - `Sales_lag_1`, `Sales_lag_7`, `Sales_lag_14`, `Sales_lag_28` (Autoregressive demand).
  - `Sales_rolling_mean_7`, `Sales_rolling_mean_14`, `Sales_rolling_std_7` (Rolling momentum).
- **Anti-Leakage Restriction:** `Customers` is strictly excluded because customer foot-traffic count is unavailable prior to store opening.

### 6.2 Supply Chain Delivery Risk Dataset (DataCo Smart Supply Chain)
- **Source:** Global e-commerce logistics fulfillment database.
- **File Location:** `data/raw/dataco/DataCoSupplyChainDataset.csv`.
- **Dimensions:** 180,519 order-item records, 53 initial columns.
- **Target Variable:** `Late_delivery_risk` (Binary: 1 = Shipment delayed, 0 = On time; $54.8\%$ late baseline).
- **Key Predictors:**
  - `days_for_shipment_scheduled` (Planned delivery SLA window: 0, 1, 2, 4 days).
  - `shipping_mode` (`Standard Class`, `Second Class`, `First Class`, `Same Day`).
  - `order_item_quantity`, `order_item_total`, `product_price` (Fulfillment load).
  - `latitude`, `longitude`, `market`, `order_region` (Geographic logistics routing).
- **Anti-Leakage Restrictions:**
  - `Days for shipping (real)` is omitted (encodes realized outcome).
  - `Delivery Status` is omitted (deterministic target duplicate).
  - `shipping date` is omitted (occurs after order placement).
  - `Order Profit Per Order` is omitted (realized post-delivery accounting).

### 6.3 Workforce Analytics Dataset (IBM HR Employee Attrition)
- **Source:** Enterprise employee demographic, compensation, and retention benchmark.
- **File Location:** `data/raw/workforce/WA_Fn-UseC_-HR-Employee-Attrition.csv`.
- **Dimensions:** 1,470 employee records, 35 initial columns.
- **Target Variable:** `Attrition` (Binary: 'Yes' [$16.1\%$], 'No' [$83.9\%$]).
- **Key Predictors:**
  - `OverTime` (Primary workload lever: 'Yes' vs 'No').
  - `WorkLifeBalance` (Survey rating: 1 = Bad, 2 = Good, 3 = Better, 4 = Best).
  - `MonthlyIncome`, `PercentSalaryHike`, `StockOptionLevel` (Compensation).
  - `TotalWorkingYears`, `YearsAtCompany`, `YearsInCurrentRole` (Tenure).
  - `JobRole`, `Department`, `BusinessTravel` (Organizational structure).
- **Anti-Leakage Restrictions:**
  - Invariants dropped: `EmployeeCount` ($=1$), `StandardHours` ($=80$), `Over18` ($='Y'$).
  - Surrogate keys dropped: `EmployeeNumber` (memorization risk).

### Where It Exists in the Repository
- Dataset manifest: [`data/dataset_manifest.json`](file:///d:/Projects/DecisionSphere/data/dataset_manifest.json#L1-L135)
- Loaders: [`src/data/rossmann_loader.py`](file:///d:/Projects/DecisionSphere/src/data/rossmann_loader.py), [`src/data/dataco_loader.py`](file:///d:/Projects/DecisionSphere/src/data/dataco_loader.py), [`src/data/ibm_hr_loader.py`](file:///d:/Projects/DecisionSphere/src/data/ibm_hr_loader.py)

---

## 7. Why Three Domains Exist: The Operational Triad

### What It Means
An enterprise can be modeled as three interdependent operational pillars:
1. **Commercial Demand:** Generating customer orders.
2. **Logistics Fulfillment:** Delivering orders physically through carrier networks.
3. **Human Capital:** Employing the staff who pick, pack, manage, and execute operations.

### Why We Need It
Optimizing any one domain creates compensating stresses in the other two. If an enterprise increases sales without logistics capacity, delivery fails. If it expands delivery capacity through forced overtime, workers resign. Evaluating all three simultaneously is the core value proposition of DecisionSphere.

### Simple Example
A three-legged stool stands stable. If you lengthen one leg (Demand) while shortening another (Workforce burnout), the stool collapses.

### Technical Implementation
The `ScenarioEngine` orchestrates three decoupled inference services (`DemandForecaster`, `SupplyChainInferenceService`, `WorkforceInferenceService`) and joins their predictions into a unified `ScenarioRunResult`.

---

## 8. The Predictive Machine Learning Layer

### What It Means
Machine learning models learn statistical relationships between input features and target outcomes from historical data.

### Why We Need It
Simple linear rules or static percentages cannot capture non-linear relationships (e.g., how the interaction between scheduled delivery days and shipping mode impacts delay risk).

### What DecisionSphere Does With It
Each domain employs a dedicated XGBoost model trained offline and stored as a serialized `.joblib` bundle containing feature column registries and preprocessing pipelines.

### Technical Implementation
- Demand: `XGBRegressor` minimizing squared error loss on chronological sales history.
- Supply Chain: `XGBClassifier` wrapped in `CalibratedClassifierCV(method='sigmoid')`.
- Workforce: `XGBClassifier` wrapped in `CalibratedClassifierCV(method='sigmoid')`.

### Where It Exists in the Repository
- Inference engines: [`src/models/demand/inference.py`](file:///d:/Projects/DecisionSphere/src/models/demand/inference.py), [`src/models/supply_chain/inference.py`](file:///d:/Projects/DecisionSphere/src/models/supply_chain/inference.py), [`src/models/workforce/inference.py`](file:///d:/Projects/DecisionSphere/src/models/workforce/inference.py)

---

## 9. How XGBoost Works in DecisionSphere

### What It Means
eXtreme Gradient Boosting (XGBoost) is an ensemble learning method that builds a sequence of shallow decision trees. Each new tree fits to the residuals (errors) made by the previous trees using gradient descent.

### Why We Need It
For tabular business datasets with mixed continuous and categorical variables, tree-based gradient boosting consistently outperforms deep neural networks in predictive accuracy, resistance to outliers, and inference speed.

### What DecisionSphere Does With It
- In Demand Forecasting: XGBoost predicts daily store sales based on day-of-week, historical lags, and promotions.
- In Supply Chain: XGBoost predicts the log-odds of a shipment being delayed.
- In Workforce: XGBoost identifies high-risk employees based on overtime, commute, compensation, and tenure.

### Where It Exists in the Repository
- Training scripts: `src/models/demand/train.py`, `src/models/supply_chain/train.py`, `src/models/workforce/train.py`

---

## 10. Probability Calibration: Why Raw Model Probabilities Lie

### What It Means
Probability calibration is the process of adjusting a classifier's raw output score so that it represents a true empirical probability.

### Why We Need It
By default, XGBoost optimizes ranking (ROC-AUC) or log-loss. A model might output $0.80$, but among all samples given a score of $0.80$, only $55\%$ actually experience delays. If an enterprise multiplies an uncalibrated probability by a $\$25$ delay penalty, the financial calculations will be wrong.

### What DecisionSphere Does With It
Both the Supply Chain and Workforce classifiers use **Sigmoid Platt Scaling** via scikit-learn's `CalibratedClassifierCV(method='sigmoid', cv='prefit')`. A logistic sigmoid mapping is fitted on the validation partition to map raw tree margins into true empirical probabilities.

### Simple Example
If a calibrated weather model says there is an $80\%$ chance of rain across 100 days, it actually rains on exactly 80 of those days.

### Technical Implementation
$$\hat{P}(\text{Late} \mid X) = \frac{1}{1 + \exp(A \cdot f(X) + B)}$$
where $f(X)$ is the raw XGBoost margin score, and $A, B$ are parameters fitted on the validation holdout.

### Where It Exists in the Repository
- Supply chain inference: [`src/models/supply_chain/inference.py`](file:///d:/Projects/DecisionSphere/src/models/supply_chain/inference.py#L62-L70)
- Workforce inference: [`src/models/workforce/inference.py`](file:///d:/Projects/DecisionSphere/src/models/workforce/inference.py#L76-L82)

---

## 11. Explainable AI: TreeSHAP and Feature Contributions

### What It Means
SHAP (SHapley Additive exPlanations) is a game-theoretic approach that explains individual model predictions by calculating the marginal contribution of each feature to the final prediction.

### Why We Need It
Saying "Late delivery risk is $62\%$" is not helpful unless the manager knows *why*. Is it because of the shipping mode? The destination region? Or the scheduled delivery window?

### What DecisionSphere Does With It
TreeSHAP decomposes predictions into additive feature contributions:
$$f(X) = \phi_0 + \sum_{i=1}^M \phi_i$$
where $\phi_0$ is the base expected value and $\phi_i$ is the contribution of feature $i$.
- In Supply Chain: Identifies `days_for_shipment_scheduled` and `shipping_mode` as primary drivers.
- In Workforce: Confirms `OverTime='Yes'` as the single largest contributor ($+0.4450$ log-odds) to employee attrition.

### Critical Research Principle: SHAP Is NOT Causation
SHAP measures **statistical feature attribution** within the model's learned representation. A positive SHAP value for overtime means: "In the training data, records with overtime had higher attrition." It does NOT constitute experimental causal proof that overtime *caused* the resignation.

### Where It Exists in the Repository
- SHAP evaluation: `src/models/demand/explain.py`, `src/models/supply_chain/explain.py`, `src/models/workforce/explain.py`

---

## 12. Cross-Domain Parameter Propagation

### What It Means
Cross-domain propagation is the algorithmic translation of an intervention in one domain into operational inputs for downstream domains.

### Why We Need It
A sales forecast produces "units of product." A logistics warehouse operates on "orders dispatched." An HR department schedules "headcount hours." These units must be mathematically translated to evaluate end-to-end consequences.

### Technical Implementation in DecisionSphere
1. **Demand to Orders (ASM-008 & ASM-007):**
   - The 14-day recursive sales forecast is averaged to a daily rate and aligned to a 30-day operational cycle (`ASM-008`):
     $$\text{NormalizedCycleVolume} = \left(\frac{Y_{\text{sales}}}{14}\right) \times 30$$
   - Normalized cycle volume is scaled by order factor $\gamma_{\text{volume}} = 0.10$ (`ASM-007`):
     $$N_{\text{orders}} = \text{NormalizedCycleVolume} \times 0.10$$
2. **Orders to Logistics Risk:**
   - Order records are modulated by `scheduled_days_offset` and `shipping_mode_override`.
   - The calibrated classifier evaluates mean late-delivery probability $P_{\text{late}}$.
3. **Logistics Load to Workforce Overtime:**
   - Target overtime headcount: $k_{\text{target}} = \lceil N_{\text{headcount}} \times (\text{overtime\_pct} / 100) \rceil$.
   - Deterministic assignment switches candidate employees from `OverTime='No'` to `'Yes'`.
   - `ASM-006` applies a heuristic decrement ($\Delta_{\text{WLB}} = -1$) to `WorkLifeBalance` for overtime workers.
   - The calibrated classifier evaluates mean attrition probability $P_{\text{att}}$.

### Where It Exists in the Repository
- Propagation engine: [`src/scenario/engine.py`](file:///d:/Projects/DecisionSphere/src/scenario/engine.py#L248-L451)

---

## 13. Managerial Financial Accounting: Why Sales Increases Destroy Margin

### What It Means
Managerial financial accounting computes the net dollar impact of an operational scenario using non-overlapping cost accounting formulas.

### The Central Question: How Can Sales Increase While Profit Decreases?
When gross sales volume increases:
1. **Gross Margin grows linearly:** Each additional unit generates $(1 - \text{cogs\_ratio}) \times \text{unit\_price}$ in gross margin (e.g., $\$0.40$ on a $\$1.00$ item).
2. **Logistics Penalties grow with volume and delay rate:** If late delivery risk is high ($55\%$), every additional 1,000 orders creates 550 late deliveries $\times \$25.00$ delay penalty (`ASM-001`) = $\$13,750$ in penalties.
3. **Fulfillment Cancellations destroy revenue (ASM-003):** Delays cause customer cancellations ($L_{\text{fulfillment}} = P_{\text{late}} \times 0.15$), wiping out expected sales.
4. **Workforce Turnover costs escalate quadratically:** Tripling overtime from $10\%$ to $30\%$ causes attrition risk to jump from $10.4\%$ to $25.0\%$. In a 221-employee cohort, an extra 32 departures $\times \$30,000$ replacement cost (`ASM-004`) equals **$\$960,000$** in turnover drag.

$$\Delta \text{NetProfit} = \Delta \text{GrossMargin} - \Delta \text{LogisticsCost} - \Delta \text{WorkforceCost}$$
When the surge in logistics penalties and employee turnover costs exceeds the small gross margin gain, net profit becomes deeply negative.

### Detailed Financial Line Items
| Line Item | Formula | Epistemic Tier | Baseline Assumption |
|---|---|---|---|
| **Gross Revenue** | $Y_{\text{sales}} \times \text{unit\_price}$ | `CALCULATED` | $\text{unit\_price} = \$1.00$ |
| **Realized Revenue** | $\text{GrossRevenue} \times (1 - \min(1, P_{\text{late}} \times \kappa_{\text{stockout}}))$ | `CALCULATED` | $\kappa_{\text{stockout}} = 0.15$ (`ASM-003`) |
| **COGS (Option B)** | $\text{RealizedRevenue} \times \text{cogs\_ratio}$ | `CALCULATED` | $\text{cogs\_ratio} = 0.60$ |
| **Gross Margin** | $\text{RealizedRevenue} - \text{COGS}$ | `CALCULATED` | Contribution margin |
| **Carrier Delay Penalty** | $N_{\text{orders}} \times P_{\text{late}} \times (1 - \kappa_{\text{stockout}}) \times C_{\text{penalty}}$ | `CALCULATED` | $C_{\text{penalty}} = \$25.00$ (`ASM-001`) |
| **Expedited Freight Fee** | $N_{\text{expedited}} \times C_{\text{expedite}}$ | `CALCULATED` | $C_{\text{expedite}} = \$15.00$ (`ASM-002`) |
| **Turnover Replacement** | $N_{\text{headcount}} \times P_{\text{att}} \times C_{\text{replacement}}$ | `CALCULATED` | $C_{\text{replacement}} = \$30,000.00$ (`ASM-004`) |
| **Overtime Wages** | $K_{\text{ot}} \times h_{\text{ot}} \times R_{\text{overtime}}$ | `CALCULATED` | $R_{\text{overtime}} = \$45.00/\text{hr}$, $h_{\text{ot}} = 20\,\text{hrs}$ (`ASM-005`) |
| **Net Profit Delta** | $\Delta \text{GrossMargin} - \Delta \text{SupplyCost} - \Delta \text{WorkforceCost}$ | `CALCULATED` | Bottom-line dollar feasibility |

### Where It Exists in the Repository
- Financial engine: [`src/business/engine.py`](file:///d:/Projects/DecisionSphere/src/business/engine.py#L66-L383)

---

## 14. Operational Strain: The Composite Risk Score (CRS)

### What It Means
The Composite Risk Score (CRS) is an index ($[0, 100]$) measuring aggregate operational friction across logistics fulfillment, workforce burnout, and demand shock magnitude.

### Why We Need It
Financial accounting only measures dollar costs. Some operational strains (such as running warehouse machinery at $98\%$ capacity or workers nearing exhaustion) do not immediately show up on an invoice but represent severe operational vulnerability.

### Technical Implementation
$$\text{CRS} = w_{\text{supply}} S_{\text{supply}} + w_{\text{workforce}} S_{\text{workforce}} + w_{\text{demand}} S_{\text{demand}}$$
- Default Simplex Weights (`ASM-009`): $w_{\text{supply}} = 0.40$, $w_{\text{workforce}} = 0.40$, $w_{\text{demand}} = 0.20$.
- Risk Categories:
  - $\text{CRS} < 30.0 \implies \mathbf{LOW}$
  - $30.0 \le \text{CRS} < 50.0 \implies \mathbf{MODERATE}$
  - $50.0 \le \text{CRS} < 75.0 \implies \mathbf{HIGH}$
  - $\text{CRS} \ge 75.0 \implies \mathbf{SEVERE}$

### Where It Exists in the Repository
- CRS Engine: [`src/recommendation/crs.py`](file:///d:/Projects/DecisionSphere/src/recommendation/crs.py#L23-L137)

---

## 15. Deterministic Recommendation & Policy Rules

### What It Means
The recommendation engine synthesizes computed operational risks and financial metrics into concrete, prioritized business actions.

### Lexicographic Decision Gating (ADR-003)
DecisionSphere enforces a strict lexicographic hierarchy to prevent commercial execution of value-destroying initiatives:
1. **Gate 1: Financial Feasibility.**
   If $\Delta \text{Profit} \le 0.0 \implies \mathbf{REJECT\_RESTRUCTURE}$
   *(Execution would destroy operating margin; redesign commercial discount or secure delivery capacity).*
2. **Gate 2: Operational Safety Buffer.**
   Else if $\text{CRS} \le \tau_{\text{risk}}$ ($50.0$) $\implies \mathbf{PROCEED}$
   *(Accretive profit achieved within safe operational risk limits).*
3. **Gate 3: Conditional Execution.**
   Else $\implies \mathbf{PROCEED\_WITH\_MITIGATIONS}$
   *(Profitable, but operational strain exceeds tolerance; deploy mandatory mitigations before launch).*

### The 7 Frozen Strategic Trigger Rules
1. `RULE-01` (`ACT-SC-001`, HIGH): Switch to Expedited Freight if $P_{\text{late}} \ge 0.65$ or ($\Delta P_{\text{late}} \ge 0.15$ and not First Class).
2. `RULE-02` (`ACT-SC-002`, MEDIUM): Increase Safety Stock Reorder Buffer by $15\%$ if $L_{\text{fulfillment}} \ge 0.10$.
3. `RULE-03` (`ACT-WF-001`, HIGH): Cap Mandatory Overtime at $20\%$ & Authorize Temporary Staffing if $P_{\text{att}} \ge 0.21$ and Overtime $\ge 30\%$.
4. `RULE-04` (`ACT-FIN-001`, CRITICAL): Margin Erosion Alert: Rescale Promotional Intensity if $\Delta \text{RealizedRevenue} > 0$ and $\Delta \text{Profit} < 0$.
5. `RULE-05` (`ACT-WF-002`, MEDIUM): Implement Targeted Retention Salary Adjustment if $P_{\text{att}} \ge 0.25$ and no salary hike specified.
6. `RULE-06` (`ACT-GOV-001`, HIGH): Operational Strain Warning: Mandate Logistics Buffers if $\Delta \text{Profit} > 0$ and $\text{CRS} \ge 60.0$.
7. `RULE-07` (`ACT-SC-003`, MEDIUM): Relax Compressed Dispatch SLA by $+1$ to $+2$ days if $\text{ScheduledOffset} \le -2$ and $P_{\text{late}} \ge 0.55$.

### Where It Exists in the Repository
- Rules registry: [`src/recommendation/rules.py`](file:///d:/Projects/DecisionSphere/src/recommendation/rules.py#L29-L305)
- Gating orchestrator: [`src/recommendation/engine.py`](file:///d:/Projects/DecisionSphere/src/recommendation/engine.py#L100-L152)

---

## 16. Auditing and Provenance: The Sigma Run Tuple

### What It Means
Provenance is the complete, verifiable historical record of every input, model artifact, code commit, and assumption policy that produced a specific decision.

### Why We Need It
In enterprise governance and scientific research, decisions must be 100% reproducible. If an executive asks two months later why a scenario was rejected, the system must reproduce the exact state of the world when that run occurred.

### Technical Implementation: The 8-Element Provenance Tuple $\Sigma_{\text{run}}$
Every simulation run persists an immutable `AuditRecord` containing:
$$\Sigma_{\text{run}} = \langle V_{\text{scen\_id}}, H_{\text{artifacts}}, P_{\text{id}}, P_{\text{ver}}, C_{\text{git}}, V_{\text{app}}, V_{\text{python}}, R_{\text{alembic}}, T_{\text{utc}} \rangle$$
1. `scenario_version_id`: UUID of immutable scenario parameters.
2. `artifact_hashes`: SHA-256 hashes of the three frozen `.joblib` model files.
3. `policy_id`: UUID of the corporate assumption policy (`ASM-001` to `ASM-010`).
4. `policy_version`: Sequential version number of the policy.
5. `git_commit`: Exact Git commit SHA of the running codebase.
6. `app_version`: Semantic software release version.
7. `python_version`: CPython runtime environment version.
8. `timestamp`: ISO-8601 UTC timestamp of execution.

### Where It Exists in the Repository
- Persistence logic: [`backend/app/services/simulation_orchestrator.py`](file:///d:/Projects/DecisionSphere/backend/app/services/simulation_orchestrator.py#L285-L302)

---

## 17. Quality and Architecture Gates: Gates G, H, and I

DecisionSphere implements three strict architectural quality gates:

### Gate G: Scenario and Policy Version Immutability
- **Contract:** Once a scenario or policy version is created and used in a simulation, it can never be modified or deleted. Any modification creates a new immutable version with an incremented version number.

### Gate H: Cryptographic Auditability & Transaction Atomicity
- **Contract:** Every simulation execution must commit its entire relational tree (run metadata, domain predictions, financial line items, recommendations, and the $\Sigma_{\text{run}}$ audit tuple) inside a single atomic database transaction. If any calculation fails, the transaction rolls back completely, preventing orphaned records.

### Gate I: Model Integrity Interlock
- **Contract:** At server startup and prior to every simulation execution, the system computes the SHA-256 hashes of `demand_model.joblib`, `supply_chain_model.joblib`, and `workforce_model.joblib`. If any hash does not match the frozen contract in `Settings.model_descriptors`, the server refuses to run and raises `ModelIntegrityError`.

### Where It Exists in the Repository
- Gate I check: [`backend/app/core/config.py`](file:///d:/Projects/DecisionSphere/backend/app/core/config.py#L141-L174)
- Gate H atomic commit: [`backend/app/services/simulation_orchestrator.py`](file:///d:/Projects/DecisionSphere/backend/app/services/simulation_orchestrator.py#L171-L312)

---

## 18. Backend Service Layer: FastAPI Architecture

### What It Means
FastAPI is a modern, high-performance Python web framework used to expose DecisionSphere's analytical capabilities via a validated REST API.

### Key Architectural Decisions
- **Asynchronous Execution Offloading (ADR-006):** Machine learning inference and Monte Carlo loops are CPU-bound. FastAPI offloads these tasks to worker threads via Starlette's `run_in_threadpool`, ensuring the async event loop is never blocked.
- **Strict Pydantic Validation:** All input levers and policy updates are validated against strict type bounds (e.g., simplex weights must sum to $1.0 \pm 10^{-4}$).

### REST API Route Overview
- `/api/v1/health` & `/api/v1/models`: System diagnostics and Gate I model verification.
- `/api/v1/scenarios`: Scenario CRUD and version management (Gate G).
- `/api/v1/policies`: Corporate assumption parameter management (`ASM-001` to `ASM-010`).
- `/api/v1/simulations`: Synchronous and asynchronous simulation execution, audit retrieval, and run comparison.
- `/api/v1/sensitivity`: Multi-dimensional parameter sweeps and tipping point search.

---

## 19. Presentation Layer: Next.js Decision Interface

### What It Means
The frontend is a modern React/Next.js single-page application built with TypeScript, delivering an executive decision interface.

### Key UI Features
1. **Decision Hero:** Prominently communicates the bottom-line recommendation (`PROCEED`, `PROCEED_WITH_MITIGATIONS`, `REJECT_RESTRUCTURE`), Net Profit Delta, and Composite Risk Score.
2. **Domain Cards:** Provide domain-specific views into sales volume, late delivery probability (with decision threshold $\tau^*$), and employee turnover risk.
3. **Financial Waterfall Table:** Itemizes each step of revenue realization, COGS deduction, logistics fines, and workforce expenses.
4. **Epistemic Badges:** Every metric in the interface displays a color-coded epistemic badge indicating whether it is `OBSERVED`, `PREDICTED`, `ASSUMED`, `PROPAGATED`, `CALCULATED`, or `RECOMMENDED`.

---

## 20. The Scientific Research & Jupyter Laboratory Layer

### What It Means
The `notebooks/` directory constitutes the **reproducible scientific laboratory** of DecisionSphere.

### Governing Rules
1. **The Backend Is the Analytical Authority:** Notebooks explain and inspect calculations; they do not invent competing formulas.
2. **The Frozen Core Remains Untouched:** `src/` and `models/` remain strictly invariant (`git diff --stat src models` must remain empty).
3. **The 16-Section Template:** Every notebook documents business questions, data sources, executable code, 300 DPI visualizations, plain-English interpretations, limitations, and viva takeaways.

---

## 21. The Canonical Worked Example: Tracing a +15% Demand Shock

To see how all pieces fit together, let us trace what happens when an executive tests a promotional initiative:
- **Input Levers:** `demand_growth_pct = +15.0%`, `promo_active = True`, `scheduled_days_offset = 0`, `shipping_mode = 'Standard Class'`, `overtime_pct = 40.0%` (mandating overtime to fulfill demand).

### Step 1: Demand Prediction
- Baseline 14-day sales (Store 1): $70,000$ units.
- Scenario sales with promotion and $+15\%$ growth: $80,500$ units ($\Delta = +10,500$ units).
- Normalized 30-day order volume (`ASM-007` & `ASM-008`): $17,250$ dispatch orders.

### Step 2: Logistics Prediction
- Under `Standard Class` with no lead time offset, the calibrated classifier predicts late delivery risk:
  $$P_{\text{late}} = 0.548 \quad (54.8\% \text{ delayed})$$
- Fulfillment loss rate (`ASM-003`):
  $$L_{\text{fulfillment}} = 0.548 \times 0.15 = 0.0822 \quad (8.22\% \text{ stockout cancellations})$$

### Step 3: Workforce Prediction
- Overtime increased from baseline $29.4\%$ to $40.0\%$.
- 23 employees switched to `OverTime='Yes'`; `WorkLifeBalance` decremented by 1 (`ASM-006`).
- The calibrated classifier predicts attrition risk jumps from $10.4\%$ to $25.2\%$.

### Step 4: Financial Calculation
1. **Gross Revenue Delta:** $+10,500 \times \$1.00 = +\$10,500.00$.
2. **Realized Revenue Delta:** After $8.22\%$ cancellations, realized revenue delta is $+\$9,636.90$.
3. **Gross Margin Delta (40% margin):** $+\$3,854.76$.
4. **Supply Chain Delay Penalties (ASM-001):**
   - Extra delayed orders incur fines: $\Delta \text{SupplyCost} \approx +\$20,625.00$.
5. **Workforce Turnover & Overtime Drag (ASM-004 & ASM-005):**
   - Expected departures increase by $\approx 33$ employees $\times \$30,000 = +\$990,000.00$.
   - Overtime wages for 88 workers $\times 20\,\text{hrs} \times \$45/\text{hr} = +\$79,200.00$.
   - $\Delta \text{WorkforceCost} \approx +\$1,069,200.00$.
6. **Net Incremental Profit Delta:**
   $$\Delta \text{Profit} = +\$3,854.76 - \$20,625.00 - \$1,069,200.00 = \mathbf{-\$1,085,970.24}$$

### Step 5: Risk Scoring & Recommendation
- $\text{CRS} = 0.40(65.2) + 0.40(72.1) + 0.20(35.5) = \mathbf{62.0}$ ($\text{HIGH RISK}$).
- Gate 1 evaluates $\Delta \text{Profit} \le 0 \implies \mathbf{REJECT\_RESTRUCTURE}$.
- Rule Engine triggers:
  - `RULE-04` (CRITICAL): Margin Erosion Alert.
  - `RULE-03` (HIGH): Cap Overtime at $20\%$ & Authorize Contract Staffing.
  - `RULE-02` (MEDIUM): Increase Safety Stock Buffers.

The executive is saved from launching an initiative that would have produced a million-dollar operational loss.

---

## 22. Epistemic Boundaries: Prediction vs Causation

A foundational rule of DecisionSphere is scientific precision:
- **Prediction $\neq$ Causation:** The machine learning models estimate conditional associations $P(Y \mid X)$ based on historical data. They do NOT prove that changing a feature will causally force the outcome in the real world.
- **TreeSHAP Contribution $\neq$ Causal Treatment Effect:** SHAP explains which features the model relied on to make its statistical inference; it does not represent an econometric causal coefficient.
- **The Six Epistemic Tiers:** Every data point in DecisionSphere is tagged with its origin:
  1. `OBSERVED`: Raw empirical records from benchmark datasets.
  2. `PREDICTED`: Statistical machine learning inferences ($P(Y \mid X)$).
  3. `ASSUMED`: User-specified scenario shock parameters and baseline coupling constants (`ASM-001` to `ASM-010`).
  4. `PROPAGATED`: Algorithmic downstream translations across operational domains.
  5. `CALCULATED`: Deterministic mathematical accounting equations for financial and risk metrics.
  6. `RECOMMENDED`: Explicit rule-grounded strategic actions synthesized from risk triggers.

---

## 23. Assumptions, Limitations, and Threats to Validity

Honest science requires documenting limitations:
1. **Benchmark Datasets:** Rossmann is European retail pharmacy data; DataCo is global e-commerce logistics; IBM HR is a synthetic corporate benchmark. They do not originate from a single physical company.
2. **Coupling Parameters (ASM-001 through ASM-008):** The scaling parameters linking sales units to orders and overtime hours are heuristic domain constants based on industry benchmarks; they are not empirically fitted regression coefficients.
3. **Static Cost Assumptions:** The financial engine assumes linear cost scaling. In real enterprise logistics, volume discounts or severe step-function penalties may occur.
4. **Generalizability:** The models reflect the specific macroeconomic environments and product categories present in the training datasets.

---

## 24. Step-by-Step Reproducibility Guide

To reproduce the DecisionSphere analytical suite on a clean machine:

### 1. Environment Setup (PowerShell)
```powershell
# Clone and enter directory
cd D:\Projects\DecisionSphere

# Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Verify Frozen Model Hashes (Gate I)
```powershell
.venv\Scripts\python.exe -c "
from backend.app.core.config import get_settings
settings = get_settings()
print(settings.verify_model_artifacts())
assert settings.all_models_verified(), 'Model integrity verification failed!'
print('All model artifacts verified successfully.')
"
```

### 3. Run the Complete Automated Test Suite
```powershell
# Run Analytical Core Tests (93 tests)
.venv\Scripts\pytest.exe tests

# Run Backend Service Tests (101 tests)
.venv\Scripts\pytest.exe backend\tests

# Run Frontend Vitest Suite (35 tests)
cd frontend
npm test
cd ..
```

### 4. Launch Development Servers
```powershell
# Terminal 1: Launch Backend Service
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Launch Frontend Application
cd frontend
npm run dev
```
Navigate to `http://localhost:3000` to interact with the DecisionSphere Decision Interface.
