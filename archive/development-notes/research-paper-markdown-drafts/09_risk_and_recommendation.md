# DecisionSphere: Research Paper — Chapter 9: Risk Scoring & Policy Governance Engine

**Section:** 8. Composite Risk Scoring & Policy Rules  
**Context:** Multi-Criteria Risk Normalization, Weight Stability, and Recommendation Logic

---

### 8.1 Multi-Domain Risk Normalization
To synthesize heterogeneous operational metrics (sales units, shipping delay probabilities, and employee turnover percentages) into a coherent decision framework, DecisionSphere maps each domain output into a normalized risk score $R_d \in [0, 100]$:

1. **Demand Risk ($R_{\text{demand}}$):**
   Evaluates capacity divergence from optimal operating volume ($V^* = 10,000$ units):
   $$R_{\text{demand}} = \min\left(100, \frac{|\hat{V}_{\text{scen}} - V^*|}{V^*} \times 100\right)$$

2. **Supply Chain Risk ($R_{\text{supply}}$):**
   Evaluates calibrated late delivery probability relative to customer SLA tolerance ($\tau_{\text{late}} = 0.50$):
   $$R_{\text{supply}} = \min\left(100, \frac{\hat{P}(\text{Late}=1)}{\tau_{\text{late}}} \times 50\right)$$

3. **Workforce Risk ($R_{\text{workforce}}$):**
   Evaluates calibrated attrition probability relative to organizational turnover tolerance ($\tau_{\text{attrition}} = 0.20$):
   $$R_{\text{workforce}} = \min\left(100, \frac{\hat{P}(\text{Attrition}=1)}{\tau_{\text{attrition}}} \times 50\right)$$

---

### 8.2 Composite Risk Score (CRS) Formulation
The Composite Risk Score is computed as a weighted linear combination of normalized domain risks:
$$\text{CRS} = w_{\text{demand}} R_{\text{demand}} + w_{\text{supply}} R_{\text{supply}} + w_{\text{workforce}} R_{\text{workforce}}$$
where $\sum_{d} w_d = 1.0$ and default governance weights are balanced:
$$w = (0.333, 0.333, 0.334)$$

**Risk Level Categorization:**
- **Low Risk:** $0 \le \text{CRS} < 30$ (Green)
- **Medium Risk:** $30 \le \text{CRS} < 60$ (Amber)
- **High Risk:** $60 \le \text{CRS} < 80$ (Orange)
- **Critical Risk:** $80 \le \text{CRS} \le 100$ (Red)

---

### 8.3 Rule-Grounded Strategic Recommendation Engine (Gate I)
DecisionSphere strictly avoids opaque black-box optimization. Instead, it evaluates an explicit, prioritized decision rule tree:

| Rule ID | Trigger Condition | Decision Action | Strategic Meaning & Managerial Directive |
|:---:|:---|:---:|:---|
| **RULE-01** | $\text{CRS} \ge 80 \quad \text{OR} \quad R_{\text{supply}} \ge 90$ | `HALT_FURTHER_INVESTIGATION` | Critical operational danger. Severe risk of widespread delivery failure or mass resignations. Immediate executive intervention required. |
| **RULE-04** | $\Delta \Pi < 0 \quad \text{AND} \quad \Delta \text{Revenue} > 0$ | `REJECT_RESTRUCTURE` | Margin Erosion Paradox. Sales expansion destroys operating profit due to downstream delay penalties and workforce replacement costs. Restructure scenario levers. |
| **RULE-02** | $\text{CRS} \ge 60 \quad \text{OR} \quad \Delta \Pi < -\$50,000$ | `REJECT_RESTRUCTURE` | High operational risk or severe projected financial deficit. Scenario parameters exceed organizational risk appetite. |
| **RULE-03** | $30 \le \text{CRS} < 60 \quad \text{AND} \quad \Delta \Pi \ge 0$ | `APPROVE_WITH_CONDITIONS` | Operationally viable with positive margin, but carries elevated risk in one domain. Requires localized mitigations (e.g., temporary flex staffing). |
| **RULE-05** | $\text{CRS} < 30 \quad \text{AND} \quad \Delta \Pi > 0$ | `APPROVE` | Unconditional strategic approval. The scenario expands operating margins while remaining safely within operational capacity limits. |
