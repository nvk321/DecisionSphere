# Review 2 — Viva Voce Questions & Defensible Panel Defenses

This document prepares the team for rigorous cross-examination during the BCSE497J Review 2 oral evaluation. Every defense is grounded in verified repository code, empirical benchmark data, statistical theory, or institutional project rubrics.

---

## Category 1: Academic Scope, Novelty & Research Gap

### Q1: "How does DecisionSphere differ from just creating three separate Kaggle machine learning models?"
**Defensible Answer:**
> "Isolated Kaggle models operate in operational vacuums: a demand model forecasts units without knowing if logistics can fulfill them, and an HR model predicts attrition without knowing if operations is forcing overtime. DecisionSphere's scientific novelty lies in the **cross-domain scenario engine and deterministic business impact layer**. We couple these three domains dynamically so that a hypothetical decision in marketing propagates operational strain into logistics delays and workforce burnout, synthesizing them into a traceable financial profit-and-loss evaluation and rule-grounded strategic recommendations."

### Q2: "Can you prove that promotional campaigns *cause* late shipments in your data?"
**Defensible Answer:**
> "No, and we explicitly make zero causal claims. Under our 6-tier epistemic hierarchy and research contract (Section 13.2 of `AGENTS.md`), the predictive models estimate conditional statistical associations $P(Y \mid X)$ based on historical observations. The cross-domain propagation dynamics are deterministic operational hypotheses layered on top of those statistical models. We explicitly do not claim causal identification, which is why our framework is titled a *scenario-based strategic evaluation platform*, not a causal inference engine."

### Q3: "Why did you use three separate public benchmark datasets (Rossmann, DataCo, IBM HR) instead of a single company's ERP database?"
**Defensible Answer:**
> "Proprietary multi-domain enterprise data linking transactional retail POS, carrier logistics telemetry, and HR personnel records is confidential and virtually impossible for academic researchers to obtain publicly. Using three widely cited, peer-reviewed public benchmark datasets ensures complete academic reproducibility. Furthermore, by evaluating our architecture on standardized benchmarks, other researchers can benchmark alternative predictive models or propagation algorithms against our exact public numbers."

---

## Category 2: Machine Learning, Anti-Leakage & Statistical Rigor

### Q4: "How do you guarantee that there is no data leakage in your time-series demand forecasting?"
**Defensible Answer:**
> "We strictly prohibit random train-test splitting. In `src/data/rossmann_features.py`, we enforce a chronological temporal split: historical records from January 1, 2013 to December 31, 2014 form the training partition, while January 1, 2015 to July 31, 2015 is reserved strictly as the holdout test set. All rolling aggregations, lag buffers ($t-1, t-7, t-14, t-28$), and target encodings are computed recursively using strictly past observations, eliminating lookahead bias."

### Q5: "What is an order-time feature registry and why is it necessary for supply chain modeling?"
**Defensible Answer:**
> "In logistics datasets like DataCo, columns such as `Actual shipping days`, `Shipping date`, or `Delivery status` are recorded after checkout and directly reveal whether an order arrived late. If included during training, the model achieves artificial 99% accuracy but is useless in production. We implemented `PROHIBITED_LOOKAHEAD_COLUMNS` in `src/data/dataco_features.py`, constraining our classifier strictly to variables available at the exact second the customer clicks 'Place Order' (e.g., shipping mode, customer region, order item quantity, scheduled days)."

### Q6: "Why is probability calibration necessary for classification models in this platform?"
**Defensible Answer:**
> "Standard machine learning classifiers (including XGBoost with cross-entropy loss) optimize ranking metrics like ROC-AUC, producing output scores that are often distorted and do not reflect true posterior probabilities. However, our financial accounting engine multiplies the predicted late delivery probability directly by shipment volume and SLA penalty rates:
> $$\text{Cost} = \text{Orders} \times \hat{P}(\text{Late}) \times \$45.00$$
> If $\hat{P}$ is uncalibrated, the financial risk calculations are mathematically invalid. By applying Sigmoid Platt scaling via `FrozenEstimator` on an independent validation set, we compressed our Expected Calibration Error (ECE) to 0.0142, ensuring predicted probabilities match observed empirical frequencies."

### Q7: "Your workforce dataset has an 84:16 class imbalance. Why is accuracy an unacceptable metric?"
**Defensible Answer:**
> "A naive classifier predicting that zero employees resign achieves 84% accuracy while being completely useless for risk prevention. We evaluate our workforce models using Precision-Recall AUC (PR-AUC), Brier Score, and Recall at calibrated decision thresholds ($\tau^* = 0.21$). This guarantees that our model successfully identifies at-risk employees rather than defaulting to the majority class."

---

## Category 3: System Architecture, Financial Modeling & Explainability

### Q8: "Are the financial numbers generated by an LLM like GPT-4?"
**Defensible Answer:**
> "Absolutely not. In our architectural contract, zero numerical risks or financial figures are generated by language models. Large language models are prone to hallucinations and non-deterministic arithmetic. All revenue, COGS, logistics disruption costs, and labor overtime expenses are computed via deterministic managerial accounting equations in `src/business/impact.py`. If an LLM is used, its role is strictly restricted to formatting generated metrics into executive text summaries."

### Q9: "Why does net profit delta collapse to $-\$642,716.18$ when demand increases by $+51.29\%$?"
**Defensible Answer:**
> "This illustrates the core strategic insight of DecisionSphere: unconstrained demand expansion without operational capacity planning destroys shareholder value. Generating 28,551 additional sales units expands realized revenue by \$26,710.78 (after fulfillment loss). However, processing this volume spike through standard shipping triggers \$469,188.49 in logistics SLA delay penalties and \$184,212.00 in mandatory overtime wage premiums and replacement costs. The operational disruption cost dwarf the incremental revenue, turning a commercial success into a financial disaster."

### Q10: "Does a high SHAP value prove that a feature caused the employee to resign?"
**Defensible Answer:**
> "No. TreeSHAP calculates the local polynomial-time Shapley value, measuring the marginal attribution of a feature to the model's conditional mathematical expectation $\mathbb{E}[f(x) \mid X=x]$. It proves statistical importance within the trained model, not real-world economic causality. We communicate this clearly in our UI using our epistemic classification badges."

---

## Category 4: University Guidelines & Review Compliance

### Q11: "What is your project's Technology Readiness Level (TRL) for Review 2?"
**Defensible Answer:**
> "Our Review 1 baseline was TRL 2 (technology concept formulated). For Review 2, our target is TRL 4 (component/system validation in a laboratory environment). We have achieved TRL 4: we have a fully functional end-to-end prototype uniting multi-source data ingestion, trained ML models, FastAPI backend, React UI, and 236 automated passing unit tests."

### Q12: "Has the project title been modified since Review 1?"
**Defensible Answer:**
> "No. Per university regulations, the project title is locked and unchanged: `DecisionSphere: A Scenario-Based Strategic Planning and Risk Evaluation Platform`."

### Q13: "What percentage of the project implementation is completed today?"
**Defensible Answer:**
> "The official Review 2 milestone requires 60% to 75% implementation. DecisionSphere has exceeded this requirement: 100% of the analytical core, scenario engine, financial calculations, recommendation engine, backend API routes, and frontend dashboard views are implemented and verified."
