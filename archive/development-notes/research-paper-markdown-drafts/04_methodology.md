# DecisionSphere: Research Paper — Chapter 4: Methodology & System Architecture

**Section:** 3. Methodology & Architectural Framework  
**Context:** The 13-Stage End-to-End Analytical Pipeline and Invariance Protocols

---

### 3.1 Architectural Overview
DecisionSphere is engineered around a strict **13-Stage Linear Execution Pipeline** where each stage transforms inputs into strongly typed outputs validated against Pydantic v2 data contracts:

```
[Stage 1: Multi-Source Ingestion]
                ↓
[Stage 2: Feature Engineering & Anti-Leakage Registry]
                ↓
[Stage 3: Offline Model Artifact Integrity Verification (Gate H)]
                ↓
[Stage 4: Scenario Parameter Ingestion & Validation]
                ↓
[Stage 5: Retail Demand Recursive Forecasting]
                ↓
[Stage 6: Cross-Domain Logistics Propagation]
                ↓
[Stage 7: Calibrated Late Delivery Classification (Gate G)]
                ↓
[Stage 8: Cross-Domain Workforce Propagation]
                ↓
[Stage 9: Calibrated Employee Attrition Classification (Gate G)]
                ↓
[Stage 10: Deterministic Managerial Accounting Engine]
                ↓
[Stage 11: Composite Risk Normalization & Scoring]
                ↓
[Stage 12: Rule-Grounded Strategic Action Synthesis (Gate I)]
                ↓
[Stage 13: Cryptographic Provenance & API Presentation]
```

---

### 3.2 Anti-Leakage Engineering & Temporal Isolation
Data leakage is the single most pervasive flaw in applied enterprise machine learning. DecisionSphere enforces three strict anti-leakage engineering invariants:

1. **Chronological Splitting in Time-Series Forecasting:**
   For retail demand, random train-test splitting is strictly prohibited. The Rossmann dataset is partitioned chronologically:
   - Training: Historical observations from Jan 1, 2013 to Dec 31, 2014.
   - Validation & Test: Jan 1, 2015 to Jul 31, 2015.
   All rolling features, lag buffers, and target encodings are fitted strictly on past observations.

2. **Order-Time Predictor Registry in Logistics Modeling:**
   In logistics classification, any variable recorded post-checkout (such as actual shipping date, carrier scan timestamps, or shipping cost variance) leaks the target. DecisionSphere establishes an immutable `PROHIBITED_LOOKAHEAD_COLUMNS` registry in `src/data/dataco_features.py`. The model is constrained solely to information available at the instant of order placement.

3. **Pre-Split Feature Encoding in Tabular Workforce Modeling:**
   In workforce attrition modeling, categorical encoders, min-max scalers, and imputation statistics are fitted strictly on the training partition before being applied to the test split, preventing distribution leakage.

---

### 3.3 The Three Governance Gates (G, H, I)
To guarantee production safety and scientific reproducibility, DecisionSphere implements three mandatory gating mechanisms:

- **Gate G (Probabilistic Calibration Gate):** Verifies that predicted classification probabilities conform to isotonic or sigmoid calibration bounds with a maximum allowable Brier score threshold ($\text{BS} \le 0.15$). Uncalibrated raw decision scores cannot enter the financial calculation pipeline.
- **Gate H (Cryptographic Model Integrity Gate):** Computes SHA-256 digests of all serialized model files (`demand_model.joblib`, `supply_chain_model.joblib`, `workforce_model.joblib`) and compares them against verified reference signatures. Any modification of model weights triggers immediate execution termination.
- **Gate I (Policy Governance Interlock):** Guarantees that automated approval cannot be issued for any scenario where $\text{CRS} \ge 60$ or $\Delta \Pi < 0$, mandating executive review or rejection.

---

### 3.4 Invariance of the Analytical Core
In accordance with academic reproducibility standards, the analytical core (`src/` and `models/`) remains completely frozen. The Jupyter research suite and frontend interface interact with this core via standardized Python API imports and RESTful HTTP payloads, ensuring that experimental evaluations reflect the exact production code.
