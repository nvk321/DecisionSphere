# DecisionSphere — Anti-Goals & Architectural Boundaries

To maintain technical clarity, academic defensibility, and feasibility for a B.Tech project team, this document explicitly defines what **DecisionSphere is NOT designed to be**.

---

## 1. Not an Isolated Single-Domain ML Project
- **Anti-Goal:** Producing merely a standalone demand forecasting notebook, an HR attrition classifier, or a logistics delay predictor.
- **Rationale:** Individual machine learning models on these benchmark datasets are well-trodden academic exercises. The unique academic contribution and novelty of DecisionSphere is the **cross-domain scenario integration, business impact modeling, and explainable decision framework**.

## 2. Not an LLM Chatbot or Hallucinatory Conversational Agent
- **Anti-Goal:** Building a conversational chatbot that attempts to "guess" or "hallucinate" sales numbers, risk percentages, or financial projections.
- **Rationale:** Generative LLMs without deterministic grounding fabricate figures and lack mathematical reproducibility. All numerical forecasts, risk probabilities, and monetary estimates in DecisionSphere must derive exclusively from trained machine learning models or deterministic mathematical formulas.

## 3. Not an Over-Engineered Enterprise Distributed System
- **Anti-Goal:** Deploying Kubernetes clusters, Apache Kafka streaming buses, Spark distributed compute engines, or complex microservices architectures.
- **Rationale:** DecisionSphere is an academic undergraduate capstone project. Introducing enterprise infrastructure creates brittle configuration debt, distracts from core analytical logic, and risks failure during live laboratory review demonstrations. A clean, modular monolithic architecture (React + FastAPI + PostgreSQL) delivers superior reliability, auditability, and speed.

## 4. Not an Autonomous Automated ERP Execution Engine
- **Anti-Goal:** Automatically issuing purchase orders, hiring staff, or modifying live corporate supply chains without human oversight.
- **Rationale:** DecisionSphere is a **decision support system (DSS)**, designed to provide transparent, explainable recommendations to human decision-makers, preserving human-in-the-loop governance.

## 5. Not an Ad-Hoc Collection of Exploratory Notebooks
- **Anti-Goal:** Leaving the project as disconnected `.ipynb` files that cannot be executed as an automated software system.
- **Rationale:** Academic rigor requires reproducibility and engineering maturity. Exploratory notebooks will be systematically refactored into verified, modular Python packages (`src/`) accessible via standardized APIs.
