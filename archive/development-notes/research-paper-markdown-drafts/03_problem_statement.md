# DecisionSphere: Research Paper — Chapter 3: Problem Statement & Research Questions

**Section:** 2. Problem Formulation & Research Questions  
**Context:** Mathematical and Conceptual Formalization of the Cross-Domain Decision Problem

---

### 2.1 Formal Problem Definition
Let an enterprise be represented by an operational state vector $\mathbf{S} = (\mathbf{D}, \mathbf{L}, \mathbf{W})$, comprising:
- Demand state $\mathbf{D} \in \mathbb{R}^{n_d}$ (sales volume, promotion status, historical lags).
- Logistics state $\mathbf{L} \in \mathbb{R}^{n_l}$ (dispatch volume, freight modes, scheduled delivery SLAs).
- Workforce state $\mathbf{W} \in \mathbb{R}^{n_w}$ (headcount, overtime allocation, compensation, job satisfaction).

A decision-maker introduces an executive intervention or scenario lever vector $\mathbf{\theta} \in \Theta$:
$$\mathbf{\theta} = (\Delta_{\text{demand\_pct}}, \text{Promo}, \Delta_{\text{sla\_days}}, \text{Mode}, \Delta_{\text{overtime\_pct}}, \Delta_{\text{salary\_pct}})$$

Under existing isolated enterprise paradigms, the commercial division estimates demand in isolation:
$$\hat{\mathbf{D}}_{\text{isolated}} = f_{\text{demand}}(\mathbf{D}, \mathbf{\theta})$$
and computes expected financial benefit purely as a function of projected revenue:
$$\mathbb{E}[\Delta \text{Revenue}] = \Delta V \times P_{\text{unit}}$$

However, in reality, the execution of $\mathbf{\theta}$ induces an unmodeled state transition in downstream domains through operational coupling functions $\mathcal{T}_{\text{logistics}}$ and $\mathcal{T}_{\text{workforce}}$:
$$\mathbf{L}' = \mathcal{T}_{\text{logistics}}(\mathbf{L}, \hat{\mathbf{D}}, \mathbf{\theta})$$
$$\mathbf{W}' = \mathcal{T}_{\text{workforce}}(\mathbf{W}, \mathbf{L}', \mathbf{\theta})$$

Consequently, the true enterprise objective is not revenue maximization, but the maximization of net operating profit delta subject to risk constraints:
$$\max_{\mathbf{\theta} \in \Theta} \Delta \Pi(\mathbf{\theta}) = \Delta R_{\text{realized}}(\hat{\mathbf{D}}, \hat{\mathbf{L}}) - \Delta \text{COGS}(\hat{\mathbf{D}}) - \Delta C_{\text{logistics}}(\hat{\mathbf{L}}) - \Delta C_{\text{workforce}}(\hat{\mathbf{W}})$$
$$\text{subject to } \quad \text{CRS}(\hat{\mathbf{D}}, \hat{\mathbf{L}}, \hat{\mathbf{W}}) \le \tau_{\text{risk}}$$

When downstream propagation $\mathcal{T}$ is ignored, the enterprise operates under an **unconscious margin deficit**, optimizing a localized objective while destroying global enterprise value.

---

### 2.2 Formal Research Questions (RQs)

To rigorously evaluate the capability of DecisionSphere to resolve this problem, we formulate four primary research questions:

- **RQ1 (Downstream Sensitivity):** *To what extent does a localized commercial demand shock ($\Delta_{\text{demand}} \in [+10\%, +30\%]$) amplify downstream delivery delay risk ($p_{\text{late}}$) and employee attrition probability ($p_{\text{att}}$) under fixed capacity constraints?*
- **RQ2 (Calibration Efficacy):** *Does post-hoc Sigmoid probability calibration on tree-ensemble classifiers significantly improve the probabilistic fidelity (Brier Score, reliability curves) required for deterministic financial risk multiplication compared to uncalibrated margin scores?*
- **RQ3 (Financial Tipping Points):** *At what precise parameter boundaries and contractual penalty thresholds does an apparently profitable sales surge invert into a net operating loss ($\Delta \Pi < 0$)?*
- **RQ4 (Decision Stability & Explainability):** *How robust is the synthesized strategic recommendation (`APPROVE` vs `REJECT_RESTRUCTURE`) to perturbations in domain risk weights, and do TreeSHAP feature attributions align with managerial operational drivers?*
