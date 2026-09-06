# DecisionSphere: Four-Track Learning Path & Viva Defense Guide

**Pedagogical Curricula for Beginners, Software Engineers, Academic Researchers, and Viva Candidates**  
*Academic Standard: TRL 4 / IEEE & Scopus Research Protocol*  
*Analytical Core Status: FROZEN & INVARIANT*

---

## 1. Overview of the Learning Framework

DecisionSphere is a multi-disciplinary platform spanning machine learning, systems engineering, managerial accounting, and decision intelligence. To enable stakeholders of varying backgrounds to master the platform rapidly, this guide defines four specialized learning curricula:

1. **Track 1: The Zero-to-One Beginner Track** (Conceptual understanding without code).
2. **Track 2: The Full-Stack Engineer Track** (Architectural mechanics, APIs, schemas, and deployment).
3. **Track 3: The Empirical Researcher Track** (EDA, statistical modeling, calibration, SHAP, and sensitivity).
4. **Track 4: The University Viva & Review Defense Track** (Examiner questions, rigorous answers, and counter-arguments).

---

## 2. Track 1: The Zero-to-One Beginner Track

**Goal:** Understand how a commercial decision produces cascading operational and financial consequences.

```
Commercial Decision (Promo +15%)
              ↓
    Demand Volume Surges
              ↓
  Warehouse & Carrier Strain
              ↓
   Severe Delivery Delays
              ↓
   Mandatory Worker Overtime
              ↓
   Employee Turnover Spikes
              ↓
Financial Loss (-$642.7K Net Profit Delta)
              ↓
  Strategic Action (REJECT & RESTRUCTURE)
```

### Study Sequence:
1. **The Core Business Dilemma:** Read `docs/DecisionSphere-Complete-Project-Guide.md` (Sections 1 to 4). Understand why sales teams and logistics teams frequently work at cross-purposes.
2. **The Three Domains:** Read Sections 5 & 6. Learn what retail demand (Rossmann), supply chain delivery (DataCo), and workforce retention (IBM HR) represent.
3. **The Ripple Effect:** Open `notebooks/00_project_orientation.ipynb`. Run the interactive orientation and observe how changing a single slider shifts all three domains.
4. **How Money is Calculated:** Read `docs/DecisionSphere-Complete-Project-Guide.md` (Section 16). Discover why a company can sell more goods yet lose money due to late delivery penalties and worker replacement costs (\$30,000 per departure).
5. **The Final Action:** Learn what the three decision categories (`PROCEED`, `PROCEED_WITH_MITIGATIONS`, `REJECT_RESTRUCTURE`) mean on the dashboard.

---

## 3. Track 2: The Full-Stack Engineer Track

**Goal:** Master the codebase, API contracts, Pydantic schemas, database models, Next.js components, and containerization.

### Study Sequence:
1. **Architectural System Map:** Read `docs/research-system-map.md`. Inspect the 13-stage execution pipeline connecting raw data to React UI.
2. **Data Schemas & Type Contracts:**
   - Review `src/scenario/schema.py` (`ScenarioLevers`, `ScenarioResult`, `DomainResult`).
   - Review `src/business/schema.py` (`FinancialImpactResult`, `CostItem`).
   - Review `src/recommendation/schema.py` (`RecommendationResult`, `CompositeRiskScore`, `DecisionCategory`).
3. **Backend Service Orchestration:**
   - Inspect `backend/app/api/v1/endpoints/simulations.py` (FastAPI execution routes).
   - Inspect `backend/app/models/scenario.py` (SQLAlchemy / PostgreSQL relational models).
   - Verify model artifact loading in `src/scenario/engine.py` (`get_artifact_fingerprints()`, Gate H).
4. **Frontend Architecture & Data Flow:**
   - Inspect `frontend/src/app/dashboard/page.tsx` and `components/dashboard/DecisionHero.tsx`.
   - Review API client implementation in `frontend/src/services/api.ts`.
   - Inspect `components/charts/FinancialWaterfallChart.tsx` for data transformation.
5. **Automated Testing Suite:**
   - Run `pytest tests/` (93 core tests).
   - Run `pytest backend/tests/` (101 FastAPI tests).
   - Run `npm test` inside `frontend/` (35 Jest component tests).
6. **Docker & Container Deployment:** Inspect `docker-compose.yml` and test container orchestration.

---

## 4. Track 3: The Empirical Researcher Track

**Goal:** Understand statistical modeling methodologies, anti-leakage controls, probability calibration, and experimental sensitivity.

### Study Sequence:
1. **Data Inventory & Anti-Leakage Controls:**
   - Study `notebooks/01_data_inventory_and_provenance.ipynb`.
   - Review `PROHIBITED_LOOKAHEAD_COLUMNS` in `src/data/dataco_features.py` to understand why post-fulfillment columns are quarantined.
2. **Exploratory Data Analysis (EDA):**
   - Study `notebooks/02_demand_eda.ipynb` (promotional lift, weekly seasonality).
   - Study `notebooks/03_supply_chain_eda.ipynb` (shipping modes, scheduled SLA vs late delivery rates).
   - Study `notebooks/04_workforce_eda.ipynb` (overtime relative risk, class imbalance).
3. **Machine Learning Model Engineering:**
   - Study `notebooks/05_demand_model.ipynb` (recursive autoregressive multi-step XGBoost).
   - Study `notebooks/06_supply_chain_model.ipynb` (calibrated XGBoost with Sigmoid Platt scaling, Brier score).
   - Study `notebooks/07_workforce_model.ipynb` (PR-AUC vs ROC-AUC on imbalanced data).
4. **Explainable AI (TreeSHAP):**
   - Review TreeSHAP summary beeswarm and feature importance plots across the three models.
   - Enforce the non-causal rule: SHAP values represent statistical feature attribution, not physical causal mechanisms.
5. **Sensitivity Analysis & Tipping Points:**
   - Study `notebooks/12_sensitivity_analysis.ipynb`.
   - Analyze the 2D parameter sweep and examine the demand tipping point where profit inverts from positive to negative.

---

## 5. Track 4: University Viva & Defense Guide

This track prepares candidates for technical viva voce examinations and panel defenses.

---

### Question 1: Why did you use three separate datasets instead of a single enterprise dataset?
**Candidate Answer:**
> *"In real-world enterprise research, public datasets that encompass the entire commercial lifecycle—from retail point-of-sale to freight shipping and employee HR records—do not exist due to proprietary privacy constraints. Monolithic synthetic datasets lack authentic real-world variance, noise, and class imbalance.*
> 
> *Therefore, in accordance with TRL 4 laboratory validation, DecisionSphere utilizes three peer-reviewed, highly cited public benchmarks: Rossmann Store Sales (1M records), DataCo Smart Supply Chain (180K records), and IBM HR Analytics (1.4K records). We couple these authentic empirical distributions within a normalized enterprise scenario testbed governed by explicit, numbered coupling assumptions (`ASM-001` to `ASM-008`)."*

---

### Question 2: Why choose XGBoost over Deep Learning (e.g., TabNet, Transformers)?
**Candidate Answer:**
> *"Extensive empirical studies in tabular machine learning (Grinsztajn et al. 2022, McElfresh et al. 2023) demonstrate that tree-based gradient boosting consistently outperforms deep neural architectures on tabular data. XGBoost provides superior generalization on mixed data types, is invariant to monotonic scaling, operates with sub-millisecond inference latency, and natively supports exact polynomial-time TreeSHAP ($O(TLD^2)$) for rigorous explainability."*

---

### Question 3: Why is probability calibration necessary, and how did you implement it?
**Candidate Answer:**
> *"Tree ensemble margins are optimized for ranking (log-loss/cross-entropy), which pushes predicted probabilities away from 0 and 1, resulting in poor calibration. In DecisionSphere, predicted probabilities are not just binary labels; they are directly multiplied by financial currency amounts (e.g., multiplying late probability by $\$25$ delay penalties or attrition probability by $\$30,000$ replacement costs).*
> 
> *An uncalibrated probability would directly distort financial accounting. We implemented post-hoc Sigmoid (Platt) scaling via `CalibratedClassifierCV` fitted on an independent validation split, verified by Brier scores below $0.10$ and reliability curve alignment across deciles."*

---

### Question 4: How can a promotional campaign that increases sales by +15% result in a negative net profit?
**Candidate Answer:**
> *"This is the central demonstration of Decision Intelligence. Sales forecasting in commercial silos focuses strictly on top-line revenue ($+\$3,856$). However, in our canonical scenario, fulfilling this surge requires Standard Class logistics, which carries a $54.8\%$ baseline late delivery risk, incurring $\$300$ in delay penalties and freight fees.*
> 
> *More critically, absorbing this surge requires shifting $40\%$ of the workforce to mandatory overtime. Under our calibrated workforce model, overtime fatigue increases turnover probability from $16.1\%$ to $27.2\%$. Under SHRM accounting benchmarks (`ASM-004`), replacing departed workers costs $\$30,000$ each. The resulting turnover replacement drag ($+\$331,500$) completely overwhelms the gross margin gain, producing a net loss of $-\$380,453$ and triggering `REJECT_RESTRUCTURE` under `RULE-04`."*

---

### Question 5: Does your model prove that promotions cause employee attrition?
**Candidate Answer:**
> *"No, and we explicitly prohibit that claim in our documentation and UI under our Anti-Causality Protocol. Our models estimate conditional statistical distributions $P(Y \mid X)$ based on historical associations, not structural causal effects $P(Y \mid \text{do}(X))$.*
> 
> *The model demonstrates that under historical conditions, employees subjected to sustained overtime exhibit a $3.0\times$ higher relative risk of departure. DecisionSphere uses this association as an operational risk indicator, not a physical causal proof."*

---

### Question 6: What happens if an executive disagrees with your Composite Risk Score weights?
**Candidate Answer:**
> *"DecisionSphere separates objective predictions from subjective risk preferences. The default Composite Risk Score uses equal weighting ($w = 0.333, 0.333, 0.334$), but our Policy Governance Engine allows executives to adjust domain weights via `/api/v1/policy/update`.*
> 
> *Furthermore, in Notebook 12 (`12_sensitivity_analysis.ipynb`), we conducted empirical weight stability tests demonstrating that the Composite Risk Score and decision boundaries remain structurally stable under $\pm 20\%$ weight perturbations."*

---

### Question 7: How do you guarantee reproducibility and prevent model drift?
**Candidate Answer:**
> *"We enforce Gate H cryptographic integrity. Every offline-trained model artifact (`.joblib`) is hashed using SHA-256. At server startup and during every simulation run, `ScenarioEngine` calculates the SHA-256 digest of the files on disk and compares them against verified signatures.*
> 
> *These hashes are embedded into the API response envelope and displayed on the web frontend. If a model file is modified by even one byte, Gate H fails immediately, preventing unverified execution."*
