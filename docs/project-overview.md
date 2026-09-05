# DecisionSphere — Project Overview

## 1. Executive Summary
**DecisionSphere** is an AI-powered strategic planning and risk evaluation platform designed to support organizational leadership in testing "what-if" business decisions before committing capital and operational resources. Modern organizations operate in tightly coupled environments: market promotions stimulate sales demand, which tests supplier delivery times and inventory buffers, while simultaneously intensifying operational workload and employee burnout risk. By synthesizing predictive machine learning models across retail demand forecasting, supply chain logistics risk, and workforce attrition into a cohesive scenario simulation and business impact engine, DecisionSphere breaks down departmental analytical silos and provides actionable, explainable strategic recommendations.

## 2. Academic Context
- **Degree Program:** Bachelor of Technology (B.Tech) in Computer Science and Engineering
- **Course Title & Code:** Project-I (BCSE497J)
- **Institution:** School of Computer Science and Engineering (SCOPE), Vellore Institute of Technology (VIT)
- **Project Title (Final & Locked):** *DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform*
- **Faculty Guide:** Dr. Suresh A
- **Student Investigators:**
  - P Naga Venkata Kushal (23BDS0133)
  - P Manjunatha Kumar Tejas (23BCE0584)
  - Jeswanth Reddy Sagabala (23BCE0203)
- **Sustainable Development Goals (SDG):** SDG 9 – Industry, Innovation and Infrastructure
- **Technology Readiness Level (TRL):** 
  - Review 1: TRL 2 (Technology concept formulated)
  - Review 2: TRL 4 (Component and system validation in laboratory environment / functional prototype)

## 3. The Core Innovation: Cross-Domain Scenario Simulation
Rather than operating as a point-solution forecasting or risk tool, DecisionSphere's key intellectual and engineering contribution lies in **cross-domain scenario propagation**:
1. **User Scenario Definition:** Strategic decision-makers define parametric operational changes (e.g., promotional demand surge of $+30\%$, supplier delivery disruption of $+7$ days, or heightened workforce attrition of $+5\%$).
2. **Predictive Analytics Propagation:**
   - **Demand Forecasting:** Predicts volume shifts and demand volatility over a planning horizon.
   - **Supply Chain Risk Analysis:** Predicts probability of delivery delays, stockout bottlenecks, and logistics failure modes.
   - **HR Workforce Risk Analysis:** Evaluates employee attrition probability and workforce pressure resulting from operational strain.
3. **Deterministic Business Impact Analysis:** Evaluates bottom-line financial and operational exposure (revenue gain vs. delay penalties, expedited shipping costs, turnover replacement expenses).
4. **Explainable Recommendations:** Delivers explainable feature attributions (via SHAP and feature importance) paired with strategic trade-off summaries.

## 4. Key Target Deliverables for Review 2 (60–75% Milestone)
- Fully audited and validated datasets (Retail Demand, DataCo Supply Chain, IBM HR Analytics).
- Trained and evaluated baseline and optimized ML models for each domain.
- Explainable AI (SHAP) integration.
- Functional Scenario Builder and Scenario Engine.
- Deterministic Business Impact Analysis engine with mathematical traceability.
- FastAPI backend serving prediction and scenario simulation endpoints.
- PostgreSQL database storing scenario parameters, simulation runs, and business impact reports.
- React + TypeScript dashboard with interactive visualizations.
- Complete draft report following official BCSE497J formatting guidelines and Review 2 presentation deck.
