# DecisionSphere: Architectural & Scientific Design Rationale

**Epistemological Foundations, Engineering Trade-Offs, and Methodological Justifications**  
*Academic Standard: TRL 4 / IEEE & Scopus Research Protocol*  
*Analytical Core Status: FROZEN & INVARIANT*

---

## 1. Introduction

DecisionSphere is engineered to bridge the fundamental gap between modern predictive machine learning and strategic executive decision-making. In enterprise environments, decisions are rarely isolated to a single department; commercial growth initiatives produce immediate operational strain in logistics and severe retention pressures in human resources.

This document systematically articulates the **Design Rationale** behind every structural, algorithmic, and governance choice within DecisionSphere, clearly demarcating **Repository Facts** (verified code/data properties) from **Methodological Rationales** (epistemic and decision-theoretic principles).

---

## 2. Core Architectural Design Decisions

### 2.1 Why Three Datasets?
- **Repository Fact:** DecisionSphere integrates three established, public, peer-reviewed benchmarks:
  1. *Rossmann Store Sales* (1,017,209 daily retail records across 1,115 stores; temporal range 2013–2015).
  2. *DataCo Smart Supply Chain* (180,519 order transactions; multi-class delivery status and shipping modes).
  3. *IBM HR Analytics Employee Attrition* (1,470 employee records; 35 organizational and demographic attributes).
- **Methodological Rationale:** No single public dataset captures the entire cross-domain enterprise lifecycle (sales demand $\to$ freight fulfillment $\to$ labor capacity). Using three domain-specialized, highly cited benchmarks provides authentic empirical distributions for each domain while enabling DecisionSphere to demonstrate cross-domain coupling in a normalized, reproducible laboratory environment (TRL 4). Synthetic monolithic datasets lack the authentic variance, noise, and class imbalance of real-world operational records.

---

### 2.2 Why Three Machine Learning Models?
- **Repository Fact:** DecisionSphere implements three distinct, specialized offline-trained models:
  1. Retail Demand: Autoregressive XGBoost Regressor predicting daily store sales.
  2. Supply Chain: Calibrated XGBoost Classifier predicting late delivery risk ($p_{\text{late}}$).
  3. Workforce Retention: Calibrated XGBoost Classifier predicting employee attrition risk ($p_{\text{att}}$).
- **Methodological Rationale:** Each business domain has fundamentally different mathematical targets, loss functions, and feature structures:
  - Demand is continuous, temporal, and autoregressive (minimizing squared/absolute error).
  - Logistics delivery risk is binary, order-time conditional, and roughly balanced ($54.8\%$ positive class).
  - Workforce attrition is binary, tabular, and heavily imbalanced ($16.1\%$ positive class).
  Attempting to train a single monolithic "foundation model" across disjoint enterprise tabular tables introduces massive cross-domain interference, destroys inductive biases, and prevents domain-specific explainability.

---

### 2.3 Why XGBoost as the Standard Architecture?
- **Repository Fact:** All three predictive engines in `src/models/` utilize Extreme Gradient Boosting (`XGBRegressor`, `XGBClassifier`).
- **Methodological Rationale:** Comprehensive empirical benchmarks (Grinsztajn et al. 2022, Shwartz-Ziv & Armon 2022, McElfresh et al. 2023) have consistently demonstrated that tree-based gradient boosting models outperform deep neural networks (e.g., TabNet, FT-Transformer) on tabular data in terms of:
  1. Generalization accuracy on heterogeneous tabular features (mixed numerical and categorical).
  2. Invariance to monotonic feature scaling.
  3. Resistance to uninformative features and outliers.
  4. Computational efficiency during inference (sub-millisecond latency per feature vector).
  5. Native compatibility with exact polynomial-time TreeSHAP explainability algorithms ($O(TLD^2)$).

---

### 2.4 Why Probability Calibration (Sigmoid / Platt Scaling)?
- **Repository Fact:** Both classification models (`models/supply_chain/` and `models/workforce/`) wrap raw XGBoost estimators within `CalibratedClassifierCV(method='sigmoid')`.
- **Methodological Rationale:** Tree ensembles optimize ranking and margin separation (log-loss or cross-entropy) but frequently produce uncalibrated posterior score distributions (Niculescu-Mizil & Caruana 2005). Raw probabilities cluster away from 0 and 1 due to bagging and leaf variance.
  In DecisionSphere, model outputs do not merely classify classes; they are **multiplied by financial dollar amounts** (e.g., $W_{\text{headcount}} \times p_{\text{att}} \times \$30,000$). An uncalibrated probability of $0.35$ that should be $0.20$ would artificially distort cost calculations by $\$450,000$. Probability calibration enforces statistical fidelity: when the model outputs $p=0.30$, exactly 30% of such events realize historically.

---

### 2.5 Why WAPE, ROC-AUC, PR-AUC, and Brier Score?
- **Repository Fact:** DecisionSphere records four distinct primary evaluation metrics across its models:
  - Demand: Weighted Absolute Percentage Error (WAPE).
  - Supply Chain: ROC-AUC, Brier Score, Balanced Accuracy.
  - Workforce: PR-AUC, ROC-AUC, Brier Score.
- **Methodological Rationale:**
  - *Standard MAPE* explodes towards infinity when actual sales approach zero ($\lim_{y \to 0} \frac{|y - \hat{y}|}{y} = \infty$). WAPE aggregates absolute error over total volume, providing a robust, scale-independent metric.
  - *Accuracy alone is deceptive on imbalanced datasets.* In IBM HR ($16.1\%$ attrition), a naive classifier predicting "No Attrition" achieves $83.9\%$ accuracy while failing completely on positive detection. PR-AUC explicitly measures minority class precision across recall thresholds without inflation by abundant true negatives.
  - *Brier Score* evaluates probabilistic calibration and resolution directly, ensuring probability estimates are reliable for financial multiplication.

---

### 2.6 Why Scenario Simulation Instead of Pure Point Forecasting?
- **Repository Fact:** Users interact with DecisionSphere by adjusting parameterized levers (`demand_growth_pct`, `promo_active`, `scheduled_days_offset`, `overtime_workforce_pct`) within `ScenarioLevers`.
- **Methodological Rationale:** Point forecasts answer only *"What will happen under current momentum?"* Strategic decision-makers require answers to *"What if we intervene?"* Simulation allows decision-makers to stress-test hypothetical operational postures, discover non-linear tipping points, and evaluate risk trade-offs before committing capital.

---

### 2.7 Why Deterministic Managerial Accounting Instead of ML Cost Prediction?
- **Repository Fact:** Financial calculations in `src/business/engine.py` are executed via deterministic mathematical accounting equations (Gross Revenue, COGS, Logistics Penalty, Turnover Cost, Net Profit Delta).
- **Methodological Rationale:** Financial accounting is governed by legal, audit, and managerial standards (GAAP / IFRS). Predicting financial profit using black-box neural networks or LLMs violates auditability, introduces hallucinated figures, and produces untraceable balance sheets. Coupling predictive statistical distributions with deterministic financial accounting ensures that every dollar delta is 100% mathematically traceable.

---

### 2.8 Why Explicit Architectural Assumptions (`ASM-001` to `ASM-008`)?
- **Repository Fact:** Cross-domain coupling constants are centralized in `src/business/engine.py` and documented with unique identifiers.
- **Methodological Rationale:** Coupling three distinct benchmark datasets into an enterprise scenario testbed requires explicit bridge assumptions (e.g., selling price per unit, fulfillment penalty per late shipment, turnover cost per employee). Hardcoding these constants invisibly across code files conceals assumptions. Centralizing and numbering them as formal assumptions (`ASM-001` to `ASM-008`) makes the system scientifically transparent, defensible, and amenable to automated sensitivity sweeps.

---

### 2.9 Why the 6-Tier Epistemic Hierarchy?
- **Repository Fact:** Every variable and response schema in DecisionSphere is tagged with one of six tiers (`OBSERVED`, `PREDICTED`, `ASSUMED`, `PROPAGATED`, `CALCULATED`, `RECOMMENDED`).
- **Methodological Rationale:** In AI decision systems, users frequently conflate ground-truth historical facts with statistical model guesses and hypothetical inputs. The 6-tier hierarchy (grounded in Shmueli 2010) enforces epistemic clarity at the API and UI layers, preventing executives from treating an assumption as an empirical observation or a statistical forecast as a guaranteed truth.

---

### 2.10 Why TreeSHAP for Explainability?
- **Repository Fact:** SHAP explanations are computed using `shap.TreeExplainer` on serialized XGBoost models.
- **Methodological Rationale:** Unlike perturbation-based explainers (e.g., LIME) which produce heuristic, sampling-dependent approximations, TreeSHAP computes exact game-theoretic Shapley values with local accuracy, consistency, and missingness guarantees (Lundberg et al. 2020). It reveals feature interactions and attributions without altering model behavior.

---

### 2.11 Why Cryptographic Provenance and Model SHA-256 Hashes?
- **Repository Fact:** `ScenarioEngine.get_artifact_fingerprints()` computes SHA-256 digests of all `.joblib` files on disk, and FastAPI returns these hashes in every simulation payload.
- **Methodological Rationale:** In regulatory and executive decision contexts, auditability is paramount. Model drift, silent artifact replacement, or accidental file corruption can invisibly alter strategic recommendations. Enforcing Gate H ensures cryptographic verification that every decision was produced by an identical, audited model state.

---

### 2.12 Why Immutable Scenario Versions and Safety Interlocks (Gate I)?
- **Repository Fact:** Scenarios are versioned immutably in PostgreSQL, and `RecommendationEngine` evaluates Gate I policy interlocks.
- **Methodological Rationale:** Strategic decisions require reproducible audit trails. Overwriting past scenario runs destroys experimental lineage. Furthermore, automated decision systems must have hard safety bounds: Gate I guarantees that no scenario resulting in negative net profit or critical risk ($\text{CRS} \ge 80$) can ever be classified as `APPROVE`.

---

### 2.13 Why Backend Authority Over Frontend or Notebook Calculations?
- **Repository Fact:** Analytical logic is strictly isolated in `src/` and exposed via FastAPI; the React frontend and Jupyter notebooks consume or inspect this authoritative core.
- **Methodological Rationale:** Implementing business logic in frontend components or ad-hoc notebooks creates code duplication, formula drift, and testing fragmentation. A single source of truth guarantees that an executive viewing the web dashboard, an engineer running automated tests, and a researcher executing notebooks observe identical, mathematically consistent results.

---

### 2.14 Why NOT Use a Generative LLM for Financial Calculations or Decisions?
- **Repository Fact:** DecisionSphere strictly excludes Generative Large Language Models (LLMs) from numerical inference, financial calculation, and risk scoring.
- **Methodological Rationale:** Generative language models are stochastic text generators optimized for linguistic plausibility, not arithmetic precision or deterministic constraint satisfaction. They are susceptible to hallucinations, numerical rounding inconsistencies, prompt injection, and epistemic drift. In strategic business planning, allocating capital based on hallucinated financial estimates is catastrophic. Deterministic formulas and calibrated predictive models provide mathematical guarantees that LLMs cannot deliver.
