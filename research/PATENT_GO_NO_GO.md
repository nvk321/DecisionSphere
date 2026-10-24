# DecisionSphere — Patent Go/No-Go Technical & Legal Decision

**Authoritative Decision Document for Academic Leadership, Inventors, and Patent Counsel**  
**Document ID:** `DSP-PAT-GONO-001`  
**Date of Decision:** 2026-10-24  
**Statutory Review:** Section 3(k) Indian Patents Act (2017 CRI Guidelines); 35 U.S.C. § 101 (*Alice*); EPC Art. 52/56 (*Comvik*).

---

## 1. Current Patent Potential
**MODERATE (Viable as a Narrow, Specific Computer-Implemented System/Method; Currently Unsuitable if Claimed Broadly as an Enterprise Decision Tool)**

- **Justification:**  
  DecisionSphere is **NOT** patentable as a broad "business decision platform" or "promotional profit simulator" because such characterizations constitute non-statutory business methods and algorithms excluded under Section 3(k) of the Indian Patents Act, 35 U.S.C. § 101, and EPC Article 52(2)(c).  
  However, DecisionSphere contains a **defensible, patent-eligible technical core** if claimed strictly as a computer-implemented architecture that couples heterogeneous machine learning estimators via an acyclic state-space dependency graph and a Platt-calibrated probability-to-penalty pipeline that demonstrably bounds propagation error in downstream non-linear loss functions.

---

## 2. Proposed Invention (One Precise Paragraph)
A computer-implemented decision intelligence architecture and method that couples heterogeneous, independently trained statistical machine learning estimators into an acyclic state-space dependency graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ with an explicit 24-dimensional continuous state vector $S_t \in \mathbb{R}^{24}$, wherein uncalibrated classification decision margins from tabular tree models are transformed via parametric logistic sigmoid calibration to bound expected calibration error (reducing ECE by $72.7\%$) prior to ingestion into downstream non-linear step-loss penalty functions, and wherein state transitions are executed deterministically along topological sort orders with cryptographic SHA-256 model digest verification, discovering operational margin collapse tipping points ($\tau^* = +18.4\%$) and enforcing lexicographic solvency feasibility gating without generative hallucination.

---

## 3. What Is Actually New? (Evidence-Supported Points Only)
1. **Calibrated Probability-to-Step-Loss Coupling Pipeline:**  
   Proving mathematically and empirically (EXP-P05) that applying post-hoc Platt sigmoid calibration prior to multiplying classifier probabilities by contractual SLA penalties ($C_{\text{delay}} = N_{\text{orders}} \cdot \hat{p}_{\text{late}} \cdot \$25$) directly eliminates **$\$27,052.48$** in downstream penalty calculation distortion.
2. **Topologically Ordered State-Space Dependency Graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$:**  
   A verified 11-node, 18-edge Directed Acyclic Graph (`src/scenario/graph.py`) that strictly orders execution across disparate ML estimators and deterministic accounting line items via Kahn's algorithm, guaranteeing zero deadlocks and zero circular state regressions.
3. **Continuous 24-Dimensional Scenario State Vector $S_t \in \mathbb{R}^{24}$:**  
   A strongly typed mathematical state tensor (`src/scenario/state.py`) capturing physical sales run rates, logistics risk, workforce burnout, accounting balances, and operational risk indices with contiguous float64 serialization and exact Euclidean state distance calculation.
4. **Automated Operating Margin Tipping-Point Discovery Operator:**  
   An algorithmic bisection search mechanism (`src/scenario/propagation.py`) identifying the invariant commercial shock threshold ($\tau^* = +18.4\%$) where operational carrier fines and employee replacement costs exceed top-line expansion.
5. **Six-Tier Epistemic Boundary Control with Cryptographic Model Digests:**  
   Compile-time schema demarcation (`OBSERVED`, `PREDICTED`, `ASSUMED`, `PROPAGATED`, `CALCULATED`, `RECOMMENDED`) paired with runtime SHA-256 digest re-hashing on disk binaries (`.joblib`), guaranteeing bit-for-bit reproducibility and halting execution upon unauthorized model tampering.

---

## 4. What Is NOT New? (Explicit List of Standard Techniques)
The following elements are well-established prior art and **must never be claimed as proprietary inventions**:
1. **XGBoost Algorithm:** Standard gradient boosted decision trees (Chen & Guestrin, 2016).
2. **Platt Sigmoid Calibration:** Standard post-hoc logistic calibration (Platt, 1999; Niculescu-Mizil & Caruana, 2005).
3. **TreeSHAP:** Standard polynomial-time Shapley feature attribution algorithm (Lundberg & Lee, 2017).
4. **Standard Classifiers / Regressors:** Ridge Regression, Logistic Regression, Moving Averages.
5. **Monte Carlo Random Sampling:** Standard stochastic noise injection (Metropolis & Ulam, 1949).
6. **Standard Managerial Accounting Equations:** Gross Revenue ($Y \times P$), COGS ($Y \times C$), Overtime wage premiums ($1.5 \times \text{wage}$).
7. **FastAPI / React Web Architecture:** Standard REST API plumbing and UI components.

---

## 5. Closest Prior Art (Top 5 References)

| Rank | Reference | Assignee / Authors | Technology Summary | Why It Threatens DecisionSphere |
|---|---|---|---|---|
| **1** | **US 12,051,026 B2** | o9 Solutions, Inc. (2024) | Computational Unified Graph Hierarchy Model | Discloses graph networks managing relational dependencies and measure propagation across enterprise planning domains. |
| **2** | **US 10,956,858 B2** | Kinaxis Inc. (2021) | Cognitive Network Graph for Concurrent Supply Chain Planning | Discloses in-memory concurrent graph propagation of demand shocks directly into supply network bottlenecks. |
| **3** | **US 10,643,152 B2** | Quantellia LLC (2020) | Automated Decision Intelligence and Strategy Optimization | Discloses mapping decision levers through predictive models to business outcomes using Causal Decision Diagrams. |
| **4** | **US 9,892,372 B2** | Palantir Technologies (2018) | Creating Data in a Data Store Using a Dynamic Ontology | Discloses sandboxed scenario simulation forks and object-link-action propagation across enterprise data. |
| **5** | **US 10,204,319 B2** | SAP SE (2019) | Integrated Business Planning and Scenario Comparison | Discloses real-time scenario simulation and financial comparison in an enterprise ERP in-memory database. |

---

## 6. Distinguishing Features (Feature-by-Feature Comparison)

| Technical Dimension | Closest Prior Art (o9, Kinaxis, Palantir, Quantellia) | DecisionSphere Invention |
|---|---|---|
| **Underlying Model Coupling** | Unified relational database schema or static in-memory BOM graph | Decoupled, heterogeneous machine learning estimators coupled via a continuous 24-dimensional State Vector $S_t \in \mathbb{R}^{24}$ |
| **Uncertainty Calibration** | Uses uncalibrated raw scores, heuristic rules, or deterministic values | Strictly enforces Platt Sigmoid calibration, proving a $-72.7\%$ ECE drop that eliminates $\$27\text{k}+$ in penalty distortion |
| **Cross-Domain Scope** | Supply Chain / Inventory / Financials only | Integrated Commercial Shock $\rightarrow$ Carrier Logistics Delay $\rightarrow$ Human Labor Overtime & Turnover Attrition |
| **Epistemic Governance** | Asserts unverified causal graphs or subjective heuristics | Enforces a formal 6-Tier Epistemic Hierarchy preventing causal overreach and generative hallucination |
| **Runtime Security** | Database access controls | Cryptographic runtime SHA-256 model digests halting execution on byte-level model weight tampering |

---

## 7. Technical Effect (Measurable Technical Effects Only)
1. **Bounded Downstream Error Propagation:**  
   Platt calibration reduces Expected Calibration Error from $0.0521$ to $0.0142$ ($-72.7\%$), directly eliminating **$\$27,052.48$** in contractual penalty calculation error across $28,551$ orders.
2. **Deterministic Acyclic Convergence:**  
   The DAG propagation operator guarantees an acyclic topological execution path with **zero circular deadlocks** and bit-for-bit reproducibility ($\lVert S_1 - S_2 \rVert_2 = 0.000$).
3. **Linear Computational Complexity:**  
   The entire 13-stage pipeline scales strictly as **$\mathcal{O}(N)$**, executing in **$\approx 945 \text{ ms}$** per scenario evaluation on standard CPU hardware with negligible memory footprint ($\approx 185 \text{ KB}$).

---

## 8. Experimental Evidence (Actual Numbers and Figures)
- **Capital Misallocation Avoidance (EXP-P01):** Prevents **$\$642,716.18$** in capital destruction by halting a commercial campaign that uncoupled planning falsely approves ($+\$171,306$).
- **Component Ablation Flip (EXP-P02):** Ablating cross-domain coupling causes a fatal decision category flip from `REJECT_RESTRUCTURE` to `PROCEED`.
- **Margin Tipping Point (EXP-P03):** Identifies the exact bifurcation boundary at **$\tau^* = +18.4\%$** demand growth (`fig_p03_tipping_point.png`).
- **Stochastic Decision Stability (EXP-P04):** Monte Carlo perturbation ($N=50$) proves **$100.0\%$ decision stability** with mean loss $-\$649,955.19$ and 95% CI $[-\$650,980, -\$648,930]$ (`fig_p04_robustness_ci.png`).
- **Calibration Error Reduction (EXP-P05):** ECE dropped by **$72.7\%$**, eliminating **$\$27,052.48$** in contractual penalty distortion.
- **Explainability Attribution (EXP-P06):** Top operational levers (`days_for_shipment_scheduled`: $0.748$, `OverTime`: $0.445$) dominate TreeSHAP attributions.
- **Complexity Profile (EXP-P07):** Strictly linear $\mathcal{O}(N)$ scaling verified across batch sizes $N \in [1, 30]$ (`fig_p07_performance_scaling.png`).

---

## 9. Remaining Weaknesses (Brutally Honest Assessment)
1. **Synthetic Enterprise Coupling:**  
   The platform couples three public benchmark datasets (Rossmann German retail, DataCo global logistics, IBM HR US tech). While normalized via temporal cycle constants (`ASM-007`, `ASM-008`), a patent examiner could argue that the coupling parameters are empirical heuristics rather than physically measured natural constants.
2. **Vulnerability to Section 3(k) / Section 101 Subject Matter Challenges:**  
   Patent examiners are heavily biased to categorize any platform outputting "profit" or "cost" as an unpatentable business method. If claims are drafted carelessly without emphasizing the technical data structures and calibration error bounding, the application will face severe Section 3(k) rejections.
3. **Linear Accounting Approximations:**  
   The accounting engine assumes linear piece-wise cost curves; real-world logistics frequently exhibits non-linear step-function thresholds (e.g., signing a new 3PL contract or leasing a warehouse).

---

## 10. Recommended Next Step & Action Plan

### Recommendation: **PROCEED WITH PROVISIONAL PATENT APPLICATION FIRST, FOLLOWED BY CONTROLLED ACADEMIC PUBLICATION**

1. **File an Indian Provisional Patent Specification First:**
   - **Filing Entity:** School of Computer Science and Engineering (SCOPE), VIT / Student Inventors.
   - **Title:** *A Computer-Implemented System and Method for Calibrated Multi-Domain State Propagation and Non-Linear Operational Risk Evaluation Across Heterogeneous Machine Learning Estimators.*
   - **Basis of Filing:** The complete 32-section Invention Disclosure (`research/PATENT_INVENTION_DISCLOSURE.md`), Claim Concepts (`research/PATENT_CLAIM_CONCEPTS.md`), Figure Specifications (`research/PATENT_FIGURE_SPECIFICATIONS.md`), and Empirical Results (`research/patent_experiments/`).
   - **Cost/Timeline Advantage:** An Indian provisional filing establishes an international priority date (Paris Convention / PCT) at minimal institutional filing cost, granting a 12-month window to complete enterprise pilot testing before filing the complete specification.

2. **Conduct a Formal Prior-Art Search with a Registered Patent Attorney:**
   - Submit `research/PATENT_PRIOR_ART_MATRIX.csv` and `research/PATENT_EVIDENCE_MATRIX.csv` to a certified Indian Patent Agent to refine claim boundaries against o9 Solutions and Kinaxis patents.

3. **Strict Pre-Filing Non-Disclosure Protocol:**
   - **DO NOT** publish or publicly release the source code files:
     - `src/scenario/graph.py` (State-Space Dependency Graph)
     - `src/scenario/state.py` (24-Dimensional State Vector)
     - `src/scenario/propagation.py` (Dynamic State Propagation Operator)
     - `research/PATENT_CLAIM_CONCEPTS.md`
   - **DO NOT** publish the academic research paper or upload pre-prints (e.g., to arXiv) until the official Provisional Patent Application Number and Filing Date have been issued by the Indian Patent Office (IPO). Public disclosure prior to filing constitutes prior art against your own invention, permanently destroying absolute novelty in India and Europe.

4. **Academic Publication Sequence:**
   - Immediately upon receiving the official IPO provisional filing receipt, proceed to submit the academic paper (`paper/DecisionSphere_Research_Paper.tex`) to target IEEE/ACM conferences. The paper will enjoy full academic dissemination while your intellectual property remains legally protected.
