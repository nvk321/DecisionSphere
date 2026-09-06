# DecisionSphere: Research Paper — Chapter 12: Scientific Discussion & Limitations

**Section:** 11. Discussion & Threats to Validity  
**Context:** Contextualizing Empirical Findings, Causal Boundaries, and Assumptions

---

### 11.1 The Epistemic Boundary: Prediction vs Causality
A foundational principle of this research is adherence to scientific epistemology (Shmueli 2010). The machine learning models in DecisionSphere estimate conditional observational distributions:
$$\hat{f}(X) \approx \mathbb{E}[Y \mid X]$$
They do not estimate structural causal treatment effects $\mathbb{E}[Y \mid \text{do}(X)]$.

Specifically:
1. We do not claim that running a promotional campaign physically *causes* an exact $+82.5\%$ sales lift in unobserved retail environments; rather, we model the historical association between promotions and sales observed in the benchmark data.
2. We do not claim that TreeSHAP feature attributions represent physical causal mechanisms. TreeSHAP provides a game-theoretic decomposition of model predictions relative to expected baseline values, explaining *how the model computed its output*, not *how the physical world operates*.
3. We do not claim that assigning an employee to overtime *causes* them to quit; rather, the model conditions on empirical evidence that overtime environments correlate with a $3.0\times$ higher departure rate.

---

### 11.2 The "Synthetic Enterprise" Coupling Assumption
Because public datasets covering the end-to-end commercial lifecycle from retail sales to logistics parcels and HR payroll do not exist, DecisionSphere integrates three peer-reviewed public benchmarks into a **normalized enterprise scenario testbed**:
- Rossmann Store Sales provides empirical demand elasticity and promotional variance.
- DataCo Smart Supply Chain provides empirical shipping lead times and carrier delivery distributions.
- IBM HR Analytics provides empirical workplace attrition characteristics under overtime strain.

The bridge between these datasets is governed by explicitly numbered architectural assumptions (`ASM-001` through `ASM-008`). While these coupling parameters reflect realistic industry accounting constants (such as SHRM replacement cost benchmarks), they are operational assumptions rather than learned cross-dataset statistical covariances.

---

### 11.3 Linear Accounting Approximations
The managerial accounting model in DecisionSphere evaluates linear piece-wise operational costs over short-term planning cycles (14 to 30 days). In long-term strategic planning, enterprises experience non-linear step-function costs (e.g., leasing additional fulfillment centers or negotiating stepped freight volume discounts) which are outside the scope of the current TRL 4 prototype.

---

### 11.4 Generalization & Production Scope
The DecisionSphere prototype is laboratory-validated at TRL 4:
- Models are trained offline and serialized (`.joblib`).
- Inference runs in sub-50ms latency on standard single-node server hardware.
- Real-time continuous streaming gradient updates and distributed microservice clusters (Kubernetes/Kafka) were deliberately excluded to maintain architectural simplicity, zero-dependency deployment, and complete reproducibility.
