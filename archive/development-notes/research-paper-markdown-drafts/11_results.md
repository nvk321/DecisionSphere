# DecisionSphere: Research Paper — Chapter 11: Empirical Results & Analysis

**Section:** 10. Empirical Results & Findings  
**Context:** Statistical Comparisons, Calibration Improvements, Financial Tipping Points, and Sensitivity Analysis

---

### 10.1 Model Performance Benchmarks

#### 10.1.1 Retail Demand Forecasting Performance
Table 1 summarizes holdout test set performance for 14-day multi-step recursive forecasting on Rossmann store sales:

| Model Architecture | MAE (Units) | RMSE (Units) | WAPE (%) | Inference Latency |
|:---|:---:|:---:|:---:|:---:|
| Naive Historical Mean | $1,842.15$ | $2,410.82$ | $26.48\%$ | $<0.1\text{ ms}$ |
| 7-Day Moving Average | $1,284.30$ | $1,752.40$ | $18.46\%$ | $<0.1\text{ ms}$ |
| Ridge Regression (Calendar Features) | $1,110.50$ | $1,520.15$ | $15.96\%$ | $0.2\text{ ms}$ |
| **DecisionSphere XGBoost Regressor** | **$782.40$** | **$1,105.65$** | **$11.23\%$** | **$1.4\text{ ms}$** |

The XGBoost regressor achieves a holdout WAPE of $11.23\%$, representing a $39.2\%$ error reduction over the 7-day moving average and successfully capturing non-linear promotional surges.

---

#### 10.1.2 Classification & Calibration Benchmark Results
Table 2 summarizes classification performance on the Supply Chain (DataCo) and Workforce (IBM HR) test partitions:

| Domain & Model Architecture | ROC-AUC | PR-AUC | Balanced Acc | Raw Brier Score | Calibrated Brier | Calibration Gain |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Supply Chain: Logistic Regression** | $0.6982$ | $0.6840$ | $0.6410$ | $0.1245$ | $0.1180$ | $+5.2\%$ |
| **Supply Chain: Uncalibrated RF** | $0.7420$ | $0.7285$ | $0.6825$ | $0.1102$ | — | — |
| **Supply Chain: DecisionSphere XGBoost**| **$0.7710$** | **$0.7620$** | **$0.7145$** | $0.1012$ | **$0.0886$** | **$+12.5\%$** |
| **Workforce: Weighted Logistic Reg** | $0.7240$ | $0.3415$ | $0.6820$ | $0.1450$ | $0.1320$ | $+8.9\%$ |
| **Workforce: Uncalibrated XGBoost** | $0.8120$ | $0.5190$ | $0.7410$ | $0.1203$ | — | — |
| **Workforce: DecisionSphere XGBoost** | **$0.8143$** | **$0.5284$** | **$0.7580$** | $0.1203$ | **$0.0988$** | **$+17.9\%$** |

**Key Findings:**
1. In logistics modeling, excluding lookahead variables yields a realistic, deployable $\text{ROC-AUC} = 0.7710$.
2. In workforce modeling, DecisionSphere achieves $\text{PR-AUC} = 0.5284$ on a heavily imbalanced dataset ($16.1\%$ positive class), representing a $3.28\times$ lift over the no-skill baseline ($0.1610$).
3. Post-hoc Sigmoid calibration significantly reduces Brier scores across both models ($12.5\%$ in logistics, $17.9\%$ in workforce), satisfying Gate G requirements.

---

### 10.2 Downstream Operational Shock Propagation (Answering RQ1)
Figure `artifacts/figures/cross_domain_propagation.png` illustrates the propagation of commercial demand shocks through downstream operations:
- A $+15\%$ demand growth shock increases cycle dispatch volume from $1,000$ to $1,023$ orders.
- Due to the reliance on Standard Class freight without lead-time extension, late delivery probability remains elevated at $54.8\%$.
- When $40\%$ of the workforce is assigned to mandatory overtime to clear volume, mean employee attrition risk escalates from $16.1\%$ to $27.2\%$ (a $+68.9\%$ relative increase).

---

### 10.3 Financial Valuation & The Margin Tipping Point (Answering RQ3)
Figure `artifacts/figures/financial_waterfall.png` and `artifacts/figures/tipping_point_analysis.png` confirm the value destruction hypothesis:
- At $+15\%$ demand expansion, incremental realized revenue is $+\$3,856.25$, yielding an incremental gross commercial margin ($\text{Revenue} - \text{COGS}$) of $+\$1,542.50$.
- However, carrier delay penalties add $+\$300.00$, overtime premiums add $+\$50,000.00$, and turnover replacement drag adds $+\$331,500.00$ ($100 \times 0.1105 \times \$30,000$).
- Total net operating margin delta is $-\$380,453.75$.

**The Demand Tipping Point:**
Parameter sweep analysis reveals that without workforce restructuring or freight SLA renegotiation, the maximum profitable demand shock is **$+4.2\%$**. Any commercial promotional surge exceeding $+4.2\%$ pushes turnover costs above gross margin gains, destroying enterprise value.

---

### 10.4 Decision Stability & Weight Robustness (Answering RQ4)
Figure `artifacts/figures/crs_weight_stability.png` demonstrates that the Composite Risk Score is highly robust to subjective governance weighting preferences:
- Perturbing individual domain weights by $\pm 20\%$ shifts the Composite Risk Score by at most $\pm 3.4$ points on a 100-point scale.
- For our canonical $+15\%$ scenario, the strategic recommendation remains invariant at `REJECT_RESTRUCTURE` across all tested weight permutations, proving that the decision is driven by fundamental operational constraints rather than arbitrary weighting artifacts.
