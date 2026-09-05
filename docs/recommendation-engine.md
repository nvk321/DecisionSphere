# DecisionSphere — Recommendation Engine Architecture

## 1. Objective & Design Philosophy
The **Recommendation Engine** converts quantitative analytical outputs, risk probabilities, and financial impact metrics into prioritized, explainable, and decision-oriented recommendations.

### Core Architectural Principle
**Grounded Deterministic Synthesis:**
- DecisionSphere does **not** rely on an ungrounded LLM to invent business recommendations or predict numerical figures.
- Strategic recommendations are anchored in deterministic business rules, threshold triggers, and validated feature attributions from the Explainable AI (SHAP) module.
- If an LLM is integrated, its scope is strictly restricted to linguistic synthesis, formatting, and executive summarization of the computed recommendations.

---

## 2. Rule-Based Trigger Matrix

The engine evaluates condition triggers against computed metrics:

| Domain | Condition / Trigger | Priority | Recommended Strategic Action |
|---|---|---|---|
| **Supply Chain** | $P(\text{Late Delivery}) > 0.65$ AND $\Delta \text{Delay Days} > 3$ | **HIGH** | Transition high-margin orders from Standard Class to First Class freight; notify regional fulfillment centers to initiate split-shipment buffering. |
| **Supply Chain** | Inventory Stockout Risk $> 0.20$ | **MEDIUM** | Increase safety stock reorder thresholds by $15\%$ across critical product categories at least 10 days prior to scenario launch. |
| **Workforce** | $P(\text{Attrition}) > 0.25$ AND Overtime $> 30\%$ | **HIGH** | Cap mandatory overtime; allocate emergency temporary contract staffing budget to prevent key employee turnover in high-stress roles. |
| **Demand / Revenue** | $\Delta \text{Profit} < 0$ despite $\Delta \text{Revenue} > 0$ | **CRITICAL** | **Margin Erosion Warning:** Projected demand surge is outweighed by late shipment SLA penalties and overtime expenses. Scale back promotional scope or secure supplier delivery commitments before campaign rollout. |
| **Procurement** | Delay $> 7$ days AND Demand Surge $> 20\%$ | **HIGH** | Activate pre-qualified secondary or local suppliers to bypass international shipping bottlenecks. |

---

## 3. Grounded LLM Integration (Optional Extension)
When an LLM (e.g., via OpenAI, Google Gemini, or Claude API) is connected:
1. **Prompt Template:**
   ```
   SYSTEM: You are an enterprise strategic advisor. You are given verified, deterministic
   simulation results and XAI feature attributions. Do NOT invent numbers. Summarize the trade-offs
   and explain the rationale behind the recommended actions.

   DATA INPUTS:
   - Scenario: {scenario_name}
   - Revenue Delta: {revenue_gain_vs_baseline}
   - Delay Risk: {simulated_late_delivery_risk}% (Top factor: {top_delay_factor})
   - Workforce Attrition Risk: {simulated_attrition_probability}% (Top factor: {top_hr_factor})
   - Net Profit Delta: {net_incremental_profit}
   - Rule-Triggered Actions: {rule_actions}
   ```
2. **Output:** A coherent executive briefing structured as:
   - Executive Summary
   - Operational Vulnerabilities Identified
   - Recommended Strategic Interventions
   - Trade-Off Considerations
