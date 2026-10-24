# DecisionSphere — Patent Drawings & Figure Specifications

**Authoritative Patent Drawings & Algorithmic Flowchart Specifications**  
**Document ID:** `DSP-PAT-FIGS-001`  
**Date:** 2026-10-24  
**Drafting Standard:** Conformance with Indian Patent Rules (Rule 15), USPTO 37 C.F.R. § 1.84, and PCT Rule 11.

---

## Overview of Figures
Every drawing specified herein corresponds to an actual, verified software module, data contract, or empirical experiment in the DecisionSphere repository.

---

### FIGURE 1: Overall System Architecture and Cryptographic Boundary Controller
- **Drawing Type:** System Block Diagram / Architectural Schematic.
- **Reference Numerals & Components:**
  - `100`: User Interface / API Client Input Bus.
  - `102`: Pydantic Compile-Time Input Validator.
  - `104`: Cryptographic Artifact Verification Controller (SHA-256 Engine).
  - `106`: Non-Transitory Model Storage (`.joblib` Binaries on Disk).
  - `108`: Immutable Historical Evaluation Cohorts (DataCo, IBM HR, Rossmann).
  - `110`: State-Space Dependency Graph Orchestrator ($\mathcal{G} = (\mathcal{V}, \mathcal{E})$).
  - `112`: Demand Forecasting Subsystem (Autoregressive XGBoost Regressor).
  - `114`: Temporal Cycle & Volume Normalization Bridge (`ASM-007`, `ASM-008`).
  - `116`: Calibrated Supply Chain Risk Subsystem (XGBoost + Platt Sigmoid).
  - `118`: Calibrated Workforce Attrition Subsystem (XGBoost + Platt Sigmoid).
  - `120`: Deterministic Managerial Accounting Engine (IEEE-754 64-bit Floating Point).
  - `122`: Multi-Criteria Composite Risk Engine ($S_{\text{supply}}, S_{\text{workforce}}, S_{\text{demand}}$).
  - `124`: Lexicographic Decision Gating Controller.
  - `126`: Output State Vector & Recommendation Dispatch Bus.

---

### FIGURE 2: Detailed State-Space Dependency Graph Architecture
- **Drawing Type:** Directed Acyclic Graph (DAG) Network Schematic.
- **Key Topological Elements:**
  - Node `N1`: Scenario Interventions Vector $U_t$ (Root Node, In-degree = 0).
  - Node `N2`: Retail Demand Forecast $Y_{\text{sales}}$.
  - Node `N3`: Enterprise Volume Coupling $N_{\text{orders}}$ (`ASM-007`, `ASM-008`).
  - Node `N4`: Calibrated Logistics Late Delivery Risk $\bar{p}_{\text{late}}$.
  - Node `N5`: Calibrated Workforce Attrition Risk $\bar{p}_{\text{att}}$ (`ASM-006`).
  - Node `N6`: Revenue & Fulfillment Accounting ($\text{GrossRev}, \text{RealizedRev}, L_{\text{fulfillment}}$).
  - Node `N7`: Logistics Disruption Expense Accounting ($C_{\text{delay}}, C_{\text{expedite}}$ via `ASM-001`, `ASM-002`).
  - Node `N8`: Workforce Operational Expense Accounting ($C_{\text{turnover}}, C_{\text{overtime}}$ via `ASM-004`, `ASM-005`).
  - Node `N9`: Net Incremental Operating Profit Delta $\Delta \Pi$.
  - Node `N10`: Composite Risk Score $\text{CRS}$ (Weighted multi-criteria sum).
  - Node `N11`: Lexicographic Feasibility Gate $\mathcal{D}(\Delta \Pi, \text{CRS})$ (Sink Node, Out-degree = 0).
  - **Directed Edges:** 18 verified dependency edges showing topological execution order derived via Kahn's algorithm.

---

### FIGURE 3: Scenario Processing & Interventional Vector Mapping Flow
- **Drawing Type:** Flowchart.
- **Process Steps:**
  - Step `302`: Ingest Scenario Levers $U = [\delta_d, u_{\text{promo}}, \Delta_{\text{days}}, \text{mode}, u_{\text{ot}}, \Delta_{\text{salary}}]^T$.
  - Step `304`: Validate parameter ranges ($\delta_d \in [-50, +100]\%$, $u_{\text{ot}} \in [0, 100]\%$).
  - Step `306`: Fork baseline evaluation copy $X_{\text{base}}$ and interventional scenario copy $X_{\text{scen}}$.
  - Step `308`: Inject promotional binary flag $u_{\text{promo}}$ into recursive demand forecaster.
  - Step `310`: Shift scheduled delivery days offset by $\Delta_{\text{days}}$ in order records.
  - Step `312`: Execute deterministic index slicing to switch first $k_{\text{needed}}$ non-overtime employees to active overtime status.
  - Step `314`: Apply ordinal decrement $\Delta \text{WLB} = -1$ to overtime employees.
  - Step `316`: Compile intermediate feature tensors for independent batch inference.

---

### FIGURE 4: Prediction & Probability Calibration Pipeline
- **Drawing Type:** Functional Block Diagram & Mathematical Graph.
- **Key Pipeline Stages:**
  - Stage `402`: Tree ensemble inference generating raw log-odds margins $z = g(x)$.
  - Stage `404`: Parametric Platt Sigmoid transformation $\hat{p} = \frac{1}{1 + \exp(-(Az + B))}$.
  - Stage `406`: Reliability curve comparison illustrating raw uncalibrated ECE ($0.0521$) vs calibrated ECE ($0.0142$).
  - Stage `408`: Mapping calibrated $\hat{p}$ into contractual step penalty $C_{\text{delay}} = N_{\text{orders}} \cdot \hat{p} \cdot \$25.00$.
  - Stage `410`: Callout demonstrating $\$27,052.48$ in contractual penalty distortion eliminated by calibration.

---

### FIGURE 5: Deterministic Financial Accounting Waterfall Pipeline
- **Drawing Type:** Mathematical Waterfall Block Diagram.
- **Line Items & Formulas:**
  - Box `502`: Gross Revenue Lift $= \Delta Y_{\text{sales}} \times \$10.00$.
  - Box `504`: Fulfillment Stockout Loss $= -(\text{Gross Revenue} \times \bar{p}_{\text{late}} \times 0.15)$.
  - Box `506`: Realized Incremental Revenue $= \text{Box 502} - \text{Box 504}$.
  - Box `508`: Cost of Goods Sold (COGS) $= -(\Delta Y_{\text{sales}} \times \$4.00)$.
  - Box `510`: Carrier Delay SLA Penalties $= -(N_{\text{orders}} \times \bar{p}_{\text{late}} \times \$25.00)$.
  - Box `512`: Voluntary Turnover Replacement Cost $= -(N_{\text{staff}} \times \bar{p}_{\text{att}} \times \$30,000.00)$.
  - Box `514`: Overtime Premium Payroll $= -(k_{\text{ot}} \times 40 \text{ hrs} \times \$45.00/\text{hr})$.
  - Box `516`: Synthesis into Net Incremental Operating Profit Delta $\Delta \Pi = \text{Box 506} - \text{Box 508} - \text{Box 510} - \text{Box 512} - \text{Box 514}$.

---

### FIGURE 6: Topological State Propagation Algorithm Flowchart
- **Drawing Type:** Algorithmic Logic Flowchart.
- **Logic Blocks:**
  - `602`: Initialize empty 24-dimensional State Vector $S_t = \mathbf{0} \in \mathbb{R}^{24}$.
  - `604`: Query `ScenarioDependencyGraph.topological_sort()` $\rightarrow$ ordered node queue $[N_1, \dots, N_{11}]$.
  - `606`: While node queue not empty: dequeue current node $N_i$.
  - `608`: Retrieve upstream state dimensions for $N_i$ from $S_t$.
  - `610`: Execute node transfer operator $f_{N_i}(\text{upstream\_states}, U; \Theta)$.
  - `612`: Write output dimensions to $S_t$ at registered dimension indices.
  - `614`: Check state convergence and verify Lipschitz bound $\lVert S_{t+1} - S_t \rVert_2 \le K \lVert U \rVert_2$.
  - `616`: Output populated Scenario State Vector $S_{t+1}$.

---

### FIGURE 7: Lexicographic Decision Gating & CRS Synthesis Flowchart
- **Drawing Type:** Decision Tree / Logic Flowchart.
- **Decision Nodes:**
  - `702`: Evaluate Net Incremental Profit Delta $\Delta \Pi$.
  - `704`: Is $\Delta \Pi \le \$0.00$?
    - **YES branch:** Proceed directly to `706`: Assign **`REJECT_RESTRUCTURE`** (Execution halted due to margin erosion).
    - **NO branch ($\Delta \Pi > \$0.00$):** Proceed to `708`.
  - `708`: Evaluate Composite Risk Score $\text{CRS} = 0.40 S_{\text{supply}} + 0.40 S_{\text{workforce}} + 0.20 S_{\text{demand}}$.
  - `710`: Is $\text{CRS} \le \tau_{\text{risk}}$ ($\tau_{\text{risk}} = 50.0$)?
    - **YES branch:** Proceed to `712`: Assign **`PROCEED`** (Accretive margin within safe organizational buffers).
    - **NO branch ($\text{CRS} > 50.0$):** Proceed to `714`: Assign **`PROCEED_WITH_MITIGATIONS`** (Profitable, but requires deploying operational mitigations).
  - `716`: Prioritize condition-action strategic recommendations by severity and financial exposure.

---

### FIGURE 8: Canonical Scenario Worked Execution State Trace
- **Drawing Type:** Visual State Trace & Number Lineage Diagram.
- **Trace Values (Review 2 Canonical Testbed):**
  - Levers: Demand Growth $= +15.0\%$, Promo Active $= 1$, Overtime Target $= 40.0\%$.
  - Baseline Demand $= 65,862.0 \text{ units}$; Scenario Demand $= 94,413.4 \text{ units}$ ($\Delta = +28,551.4 \text{ units}$).
  - Normalized Order Volume $= 28,551.43 \text{ orders}$.
  - Supply Chain Late Probability: Baseline $= 55.45\% \rightarrow$ Scenario $= 62.75\%$ ($\Delta = +7.30\%$).
  - Workforce Attrition Probability: Baseline $= 16.14\% \rightarrow$ Scenario $= 18.92\%$ ($\Delta = +2.78\%$).
  - Financial Balances:
    - Gross Revenue Delta $= +\$285,514.35$
    - Realized Revenue Delta $= +\$26,710.78$ (Fulfillment Loss $= -\$258,803.57$)
    - COGS Delta $= +\$114,205.74$
    - Logistics Penalty Delta $= +\$399,860.00$
    - Turnover Cost Delta $= +\$184,212.00$
    - Overtime Wage Delta $= +\$25,200.00$
    - **Net Profit Delta $\Delta \Pi = -\$642,716.18$**
  - Decision: **`REJECT_RESTRUCTURE`** (Halts $\$642\text{k}$ in capital misallocation).

---

### FIGURE 9: Empirical Patent Validation Charts (EXP-P01 to EXP-P07)
- **Drawing Type:** 4-Panel Scientific Graph.
- **Panel 9A:** *EXP-P03 Margin Tipping Point Curve* — Net Operating Profit Delta vs Demand Growth (%) crossing zero at $\tau^* = +18.4\%$ (from `research/patent_experiments/figures/fig_p03_tipping_point.png`).
- **Panel 9B:** *EXP-P04 Monte Carlo Robustness Distribution* — Histogram of 50 stochastic runs showing mean $-\$649,955.19$, 95% CI $[-\$650,980, -\$648,930]$, and $100.0\%$ decision stability (from `research/patent_experiments/figures/fig_p04_robustness_ci.png`).
- **Panel 9C:** *EXP-P05 Probability Calibration Reliability Curves* — Comparing raw uncalibrated margins vs Platt sigmoid calibration, illustrating $72.7\%$ ECE reduction and elimination of $\$27,052.48$ in penalty distortion.
- **Panel 9D:** *EXP-P07 Computational Complexity Scaling* — Total runtime vs scenario batch size $N \in [1, 30]$ demonstrating linear profile $\mathcal{O}(N)$ with sub-second per-run latency (from `research/patent_experiments/figures/fig_p07_performance_scaling.png`).
