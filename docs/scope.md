# DecisionSphere — Project Scope & System Boundaries

## 1. Functional Scope

### A. Data Ingestion & Modular Preprocessing Layer
- Ingestion of verified open-source benchmark datasets:
  - **Demand Forecasting:** Store Sales Time Series Dataset (Corporación Favorita / Walmart / Rossmann — to be finalized upon empirical audit).
  - **Supply Chain Risk:** DataCo Smart Supply Chain for Big Data Analysis.
  - **Workforce Risk:** IBM HR Analytics Employee Attrition & Performance Dataset.
- Automated missing value handling, temporal alignment, categorical encoding, and feature scaling.
- Prevention of data leakage through strict split ordering (train/test before featurization; chronological split for time-series).

### B. Machine Learning & Predictive Modeling
- **Retail Demand Forecasting:** Multi-horizon sales volume forecasting considering promotional activity, seasonality, and calendar variables.
- **Supply Chain Risk Classifier:** Binary or multi-class risk classification predicting late delivery risk and shipping status anomalies.
- **Workforce Risk Classifier:** Binary classification predicting employee attrition probability and identifying operational turnover drivers.
- **Explainability (XAI):** Computation of global feature importances and local SHAP explanation values for model transparency.

### C. Scenario Engine
- Scenario parameter definition interface supporting adjustments to:
  - Demand growth percentage ($\Delta \text{Demand} \in [-50\%, +100\%]$).
  - Supply chain shipment delay offset ($\Delta \text{Delay Days} \in [0, 30]$).
  - Workforce attrition shock ($\Delta \text{Attrition} \in [0\%, +30\%]$).
  - Operational interventions (promotional flags, expedited shipping, temporary staffing adjustments).
- Mapping and feeding scenario shock parameters into corresponding model inference pipelines.

### D. Business Impact Analysis Engine
- Deterministic calculation of:
  - Projected Gross Revenue.
  - Estimated Delay and Fulfillment Penalty Costs.
  - Estimated Workforce Churn and Replacement Costs.
  - Net Operational Margin and Composite Risk Index.
- Direct side-by-side comparison of Baseline vs. Simulated Scenario.

### E. Recommendation Engine
- Rule-grounded synthesis linking risk severity and cost trade-offs to actionable mitigations.
- Optional structured LLM integration strictly for plain-language summarization and strategic trade-off articulation without hallucinating numbers.

### F. Application & Dashboard Layer
- **Backend:** High-performance RESTful API powered by FastAPI with Pydantic v2 data validation and SQLAlchemy ORM.
- **Database:** PostgreSQL storing scenario configurations, run histories, and generated impact reports.
- **Frontend:** Responsive React + TypeScript dashboard with interactive parameter sliders, multi-line time-series forecast charts, risk heatmaps, and scenario comparison views.

---

## 2. Non-Functional Scope
- **Performance:** Sub-second inference latency for cached baseline scenarios; $<3$ seconds for complete multi-model scenario simulation run.
- **Reproducibility:** Versioned Python environments, seed-locked ML training pipelines, deterministic calculation modules.
- **Academic Feasibility:** Architecture tailored for a 3-student B.Tech project timeline, avoiding unnecessary operational overhead.

---

## 3. Academic & Boundary Constraints
- **Simulation Environment:** The platform simulates hypothetical outcomes on established enterprise benchmark datasets rather than live corporate enterprise ERP feeds.
- **Model Training:** Training is executed offline; the runtime application consumes serialized model artifacts.
- **Scope Limitations:** Advanced autonomous agent swarms, automated ERP transaction execution, and live continuous retraining are explicitly out of scope for Project I.
