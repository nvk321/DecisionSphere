# DecisionSphere — Explainable AI (XAI) Strategy

## 1. The Role of XAI in Strategic Decision Support
In enterprise decision-making, predictive accuracy is insufficient without transparency. Executives will not reallocate inventory, adjust delivery schedules, or alter workforce staffing policies based on an uninterpretable "black-box" probability score.

DecisionSphere implements Explainable AI (XAI) to answer two fundamental stakeholder questions:
1. **Global Transparency:** *"What operational factors generally drive risks across our business processes?"*
2. **Local Explainability:** *"Why did the system predict an elevated risk score for this specific simulated scenario?"*

---

## 2. Technical Methodology

### 2.1 SHAP (SHapley Additive exPlanations)
- **Mathematical Foundation:** Grounded in cooperative game theory, Shapley values compute the marginal contribution of each operational feature toward shifting the prediction away from the dataset's base expected value:
  $$f(x) = \phi_0 + \sum_{i=1}^{M} \phi_i(x)$$
  where $\phi_0$ is the base expected model output and $\phi_i(x)$ is the feature attribution for feature $i$.
- **Implementation via TreeSHAP:** For tree-based models (XGBoost, Random Forest), TreeSHAP provides exact, polynomial-time Shapley value computation, enabling low-latency real-time inference explanations.

### 2.2 Global vs. Local Explanations
| Scope | Artifact | User Insight |
|---|---|---|
| **Global** | Mean $|SHAP|$ Summary Bar & Beeswarm Plots | Identifies systemic enterprise vulnerabilities (e.g., standard class shipping is the primary contributor to late delivery across all orders). |
| **Local** | Waterfall & Force Plots for Simulated Scenarios | Explains the specific levers driving risk in the user's active "what-if" scenario (e.g., $+15\%$ overtime was the dominant driver shifting attrition probability from $16\%$ to $28\%$). |

---

## 3. Grounding Rules & Anti-Hallucination
- **Direct Mathematical Derivation:** Explanation values must be extracted directly from model objects via `shap.TreeExplainer`.
- **No Fabricated Narratives:** Explanations must strictly cite features with non-zero Shapley values. If a factor was not in the model feature vector, it cannot be listed as an explanation.
- **Bridging XAI to Strategic Actions:** The Recommendation Engine ingests the top $K$ positive contributors to risk (e.g., high scheduled shipping days, frequent travel, excessive overtime) and maps them directly to corresponding mitigation actions.
