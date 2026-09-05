# DecisionSphere — System Architecture & Component Design

## 1. High-Level Architectural Diagram

```mermaid
graph TD
    subgraph Client Layer ["Client Presentation Layer (React + TypeScript)"]
        UI_SB["Scenario Builder & Parameter Controls"]
        UI_DF["Demand Forecast Visualizer"]
        UI_SC["Supply Chain Risk Heatmap"]
        UI_HR["Workforce Attrition Risk Monitor"]
        UI_BI["Business Impact & Cost-Benefit Panel"]
        UI_REC["Explainable Recommendations & Trade-offs"]
    end

    subgraph API Layer ["API & Orchestration Layer (FastAPI Backend)"]
        API_ROUTER["FastAPI Router & Pydantic Validators"]
        SCEN_ENG["Scenario Engine (Parameter Propagation)"]
        BI_ENG["Business Impact Engine (Traceable Formulas)"]
        REC_ENG["Recommendation Synthesizer"]
    end

    subgraph Analytics Layer ["Analytics & Machine Learning Services"]
        ML_DEMAND["Demand Forecasting Model (Time-Series / XGBoost)"]
        ML_SUPPLY["Supply Chain Risk Classifier (Late Delivery)"]
        ML_HR["Workforce Risk Classifier (Attrition Probability)"]
        XAI_MOD["Explainable AI Module (SHAP / Feature Attribution)"]
    end

    subgraph Persistence Layer ["Data & Storage Layer"]
        DB[(PostgreSQL Database)]
        subgraph Tables
            T_USERS["Users & Sessions"]
            T_SCEN["Scenario Definitions"]
            T_RUNS["Simulation Runs"]
            T_IMPACT["Impact & Recommendations"]
        end
        DATA_FILES["Processed Datasets (Parquet / Cleaned CSV)"]
        MODEL_STORE["Serialized Model Store (.joblib Artifacts)"]
    end

    UI_SB -->|Scenario Parameters (JSON)| API_ROUTER
    API_ROUTER --> SCEN_ENG
    SCEN_ENG --> ML_DEMAND
    SCEN_ENG --> ML_SUPPLY
    SCEN_ENG --> ML_HR
    ML_DEMAND --> BI_ENG
    ML_SUPPLY --> BI_ENG
    ML_HR --> BI_ENG
    ML_DEMAND --> XAI_MOD
    ML_SUPPLY --> XAI_MOD
    ML_HR --> XAI_MOD
    BI_ENG --> REC_ENG
    XAI_MOD --> REC_ENG
    REC_ENG --> API_ROUTER
    API_ROUTER --> UI_DF
    API_ROUTER --> UI_SC
    API_ROUTER --> UI_HR
    API_ROUTER --> UI_BI
    API_ROUTER --> UI_REC

    API_ROUTER <--> DB
    ML_DEMAND <--> MODEL_STORE
    ML_SUPPLY <--> MODEL_STORE
    ML_HR <--> MODEL_STORE
```

---

## 2. Layered Responsibilities

### 2.1 Client Presentation Layer (React + TypeScript)
- **Scenario Builder:** Dynamic slider and toggle controls allowing users to define operational shifts ($\Delta$ Demand %, Delivery Delay days, Attrition Rate shocks, Promotional flags).
- **Domain Dashboards:** Visualizations displaying historical vs. simulated forecast curves, supply chain risk probability distributions, and workforce risk indicators.
- **Business Impact Summary:** Key Performance Indicator (KPI) cards showing Projected Revenue, Net Additional Operational Costs, Delay Penalties, and Net Bottom-Line Impact.
- **Explainability Views:** Interactive SHAP waterfall / force plots and bar charts illustrating the primary factors driving risk classifications.

### 2.2 API & Orchestration Layer (FastAPI)
- **REST Endpoints:**
  - `GET /api/scenarios` — Retrieve scenario library and presets.
  - `POST /api/scenarios/simulate` — Execute cross-domain simulation run.
  - `GET /api/scenarios/{id}/history` — Retrieve historical run logs.
  - `GET /api/explain/{model_type}` — Retrieve SHAP feature explanations.
- **Pydantic Validation:** Strict type enforcement ensuring parameter bounds (e.g., preventing negative delay days or impossible percentages).
- **Service Orchestrator:** Manages parallel or sequential execution across ML inference services and aggregates outputs into the business impact engine.

### 2.3 Analytics & ML Services Layer (`src/models/`, `src/scenario/`)
- Pure Python services decoupled from web frameworks.
- Loads serialized pre-trained artifacts (`.joblib`) during application startup.
- Executes low-latency inferences given modified scenario features.
- Computes SHAP value matrices for explainability.

### 2.4 Persistence Layer (PostgreSQL & Artifact Storage)
- **PostgreSQL:** Stores scenario configuration metadata, simulation run records, execution timestamps, and generated recommendation logs.
- **Model Artifact Storage:** Local directory storing versioned model binaries and preprocessing scalers/encoders.
- **Data Store:** Parquet and cleaned CSV files holding operational baselines.

---

## 3. Communication & Data Flow Sequence

1. **User Request:** User adjusts scenario sliders on the frontend and clicks **"Simulate Scenario"**.
2. **Validation:** Frontend submits `POST /api/scenarios/simulate` with payload conforming to `ScenarioInputSchema`.
3. **Parameter Translation:** Scenario Engine translates high-level scenario levers into feature-level deltas for each domain module.
4. **Predictive Inference:**
   - Demand model infers adjusted sales volume.
   - Supply chain model infers late delivery probability given altered logistical assumptions.
   - HR model infers employee attrition risk given elevated operational pressure.
5. **Explainability Extraction:** XAI module computes top contributing features for elevated risk scores.
6. **Business Impact Modeling:** The Business Impact Engine applies deterministic financial formulas to compute revenue, penalty costs, turnover costs, and net margin.
7. **Recommendation Generation:** The Recommendation Engine evaluates rule triggers and synthesizes trade-off summaries.
8. **Persistence:** Simulation parameters and computed metrics are saved in PostgreSQL.
9. **Response:** Comprehensive structured JSON is returned to the frontend for visualization.
