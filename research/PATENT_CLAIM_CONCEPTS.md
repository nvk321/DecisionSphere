# DecisionSphere — Patent Claim Concepts

**Authoritative Claim Concepts & Scope Definition**  
**Document ID:** `DSP-CLAIM-CONCEPTS-001`  
**Date:** 2026-10-24  
**Drafting Standard:** Subject matter eligibility under Section 3(k) Indian Patents Act (2017 CRI Guidelines), USPTO 35 U.S.C. § 101 / 112 (*Alice* two-step test), and EPO Art. 52/56 (*Comvik* doctrine).

---

## Notice Regarding Legal Character
The claim concepts set forth below represent **technical invention concepts and structural claim language**, not final legal claim forms. Final claim drafting and submission must be conducted by a registered Patent Agent or Patent Attorney admitted to practice before the respective patent office (Indian Patent Office / USPTO / EPO).

To overcome Section 3(k) (India) and Section 101 (US) business-method exclusions, all independent claims are **strictly grounded in computer-implemented data structures, cryptographic verification, state-space dependency graphs, and calibrated probability transformations**.

---

## 1. Independent Method Claim Concept (Claim 1)

**A computer-implemented method for calibrated multi-domain state propagation and non-linear operational risk evaluation across heterogeneous machine learning estimators, the method comprising:**

1. **verifying, by one or more processors prior to scenario execution,** cryptographic hash digests of a plurality of serialized machine learning model artifacts stored in a non-transitory memory against pre-registered cryptographic baseline digests, wherein execution is halted upon detecting a digest mismatch;
2. **receiving, via a strongly typed input interface,** a scenario intervention vector comprising user-specified operational shock parameters bounded by compile-time numerical constraints;
3. **instantiating, in the memory,** an immutable baseline state vector representing historical enterprise operational observations across a plurality of disparate operational domains;
4. **generating, via a first machine learning estimator** comprising an autoregressive gradient boosted decision tree, a forward demand forecast conditioned on the scenario intervention vector;
5. **transforming, by an enterprise normalization operator,** the forward demand forecast into a normalized operational order throughput volume using a temporal planning cycle factor and a volume scaling factor;
6. **generating, via a second machine learning estimator** comprising a supply chain tree classifier, an uncalibrated late-delivery decision margin for an order cohort, and transforming said decision margin into a calibrated late-delivery probability via a parametric logistic sigmoid transformation;
7. **mapping, by a deterministic workforce allocation engine,** an overtime target from the scenario intervention vector across an employee cohort to assign overtime status, adjusting an ordinal burnout feature, generating an uncalibrated attrition decision margin via a third machine learning estimator comprising a workforce tree classifier, and transforming said attrition margin into a calibrated attrition probability via a second parametric logistic sigmoid transformation;
8. **propagating, via a topologically ordered Directed Acyclic Graph (DAG) state-space operator,** the forward demand forecast, the calibrated late-delivery probability, the normalized order throughput volume, and the calibrated attrition probability through a plurality of directed dependency edges into a continuous 24-dimensional scenario state vector;
9. **computing, by a deterministic managerial accounting engine** operating with 64-bit floating-point precision on the scenario state vector, an incremental net operating profit delta ($\Delta \Pi$) and a normalized multi-criteria Composite Risk Score ($\text{CRS}$);
10. **evaluating, by a lexicographic decision gating controller,** a hierarchical feasibility rule to classify the scenario state vector into one of a plurality of mutually exclusive strategic decision categories, wherein the scenario is automatically assigned to a rejection state upon determining that $\Delta \Pi \le 0$; and
11. **transmitting, to a display interface or programmatic output bus,** the classified strategic decision, the 24-dimensional scenario state vector, and prioritized condition-action operational interventions.

---

## 2. Independent System Claim Concept (Claim 2)

**A decision intelligence computing system for calibrated multi-domain state propagation and non-linear operational risk evaluation, the system comprising:**
- one or more physical processors; and
- a non-transitory computer-readable memory storing executable instructions and a plurality of serialized machine learning model artifacts comprising at least a time-series demand regressor, a supply chain risk classifier, and a workforce attrition classifier, wherein the instructions, when executed by the one or more physical processors, cause the system to:
  - compute cryptographic runtime hash digests of the plurality of serialized model artifacts and verify identity with pre-registered baseline digests;
  - ingest strongly typed scenario intervention parameters bounded by pre-defined validation ranges;
  - execute the time-series demand regressor to generate a projected demand forecast;
  - normalize the projected demand forecast into an operational order volume via temporal cycle synchronization;
  - compute calibrated late-delivery probabilities for a plurality of order records via a Platt sigmoid transformation applied to raw tree ensemble margins;
  - assign overtime status deterministically across employee records, adjust ordinal work-life balance scores, and compute calibrated employee attrition probabilities via a Platt sigmoid transformation applied to raw workforce tree ensemble margins;
  - evolve an enterprise state along a Directed Acyclic Graph (DAG) state-space topology into a unified 24-dimensional continuous state vector;
  - compute an incremental net operating profit delta and an operational Composite Risk Score from the 24-dimensional state vector; and
  - classify the scenario state into a strategic decision category via a lexicographic feasibility gate that halts promotion approval when the incremental net operating profit delta is less than or equal to zero.

---

## 3. Dependent Claim Concepts

### Dependent Claim 3: Calibrated Probability-to-Step-Loss Coupling
*The method of Claim 1, wherein the calibrated late-delivery probability and the normalized order throughput volume are mapped directly into a non-linear contractual delay penalty loss function:*
$$C_{\text{delay}} = N_{\text{orders}} \times \left( \frac{1}{|\mathcal{O}|} \sum_{i \in \mathcal{O}} \hat{p}_{\text{late}, i} \right) \times C_{\text{penalty}}$$
*wherein said parametric logistic sigmoid transformation reduces Expected Calibration Error (ECE) from greater than 0.050 to less than 0.015, bounding downstream penalty calculation distortion within a pre-determined empirical confidence envelope.*

### Dependent Claim 4: State-Space Dependency Graph & Topological Execution
*The method of Claim 1, wherein the DAG state-space operator comprises an 11-node dependency graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ formally verified for acyclicity, and wherein node state transitions are computed strictly in accordance with a topological sort ordering derived via Kahn's algorithm, guaranteeing zero circular recursions and deterministic state convergence.*

### Dependent Claim 5: Six-Tier Epistemic Boundary Control
*The method of Claim 1, further comprising tagging every numerical element in the 24-dimensional state vector with one of six immutable epistemic tier labels selected from:*
- `OBSERVED`: historical ground truth from audited benchmark datasets;
- `PREDICTED`: statistical machine learning model inferences conditioned on input feature vectors;
- `ASSUMED`: user-specified scenario shock parameters and baseline operational constants;
- `PROPAGATED`: algorithmic downstream translations across operational domains;
- `CALCULATED`: deterministic mathematical accounting equations; and
- `RECOMMENDED`: rule-grounded strategic actions synthesized from risk triggers;
*wherein compile-time type validation prevents statistical predictions from being presented as deterministic financial statements or causal claims.*

### Dependent Claim 6: Deterministic Operating Margin Tipping-Point Discovery
*The method of Claim 1, further comprising executing a numerical bisection root-finding search over a continuous demand shock parameter space to identify an invariant operating margin tipping point $\tau^*$ where $\Delta \Pi(\tau^*) = 0$, wherein demand growth exceeding $\tau^*$ triggers a catastrophic net margin collapse due to non-linear expansion of carrier delay fines and workforce turnover replacement costs.*

### Dependent Claim 7: Numerical State Sensitivity Jacobian Matrix
*The method of Claim 1, further comprising computing a continuous numerical Jacobian sensitivity matrix $J \in \mathbb{R}^{24 \times 3}$ using central finite differences:*
$$J_{i, j} = \frac{\partial S_i}{\partial U_j} \approx \frac{S_i(U + \epsilon e_j) - S_i(U - \epsilon e_j)}{2\epsilon}$$
*to track the rate of change of every state dimension with respect to demand growth, shipping schedule compression, and workforce overtime percentage.*

### Dependent Claim 8: Polynomial-Time Shapley Attribution Traceability
*The method of Claim 1, further comprising computing exact local Shapley feature attributions for the supply chain tree classifier and workforce tree classifier using a polynomial-time TreeSHAP algorithm, and linking each strategic operational recommendation to the highest-ranking interventional feature attribution in the scenario state vector.*

### Dependent Claim 9: Deterministic Overtime Assignment Mapping
*The method of Claim 1, wherein mapping the overtime target comprises sorting non-overtime employee records by a deterministic primary index, identifying a required headcount delta $k_{\text{needed}} = \lceil N_{\text{headcount}} \cdot u_{\text{ot}} \rceil - k_{\text{base}}$, deterministically switching the first $k_{\text{needed}}$ records to active overtime status, and clamping an ordinal work-life balance feature within the closed integer interval $[1, 4]$.*

---

## 4. Statutory Ineligibility Shield Analysis

| Statutory Exclusion Hazard | Claim Protection Mechanism |
|---|---|
| **Section 3(k) IPA — "Business Method"** | The independent claims do not claim business methods or commercial rules in the abstract; they claim a specific **computer-implemented data transformation pipeline** that verifies cryptographic digests, maps continuous vectors through an acyclic DAG, and eliminates calibration error in non-linear loss functions. |
| **Section 3(k) IPA — "Computer Programme Per Se"** | Claims recite physical memory registers, cryptographic processors, continuous 24-dimensional vector structures, and tangible technical effects (reducing ECE by 72.7%, bounding numerical error propagation). |
| **35 U.S.C. § 101 — *Alice* Abstract Idea** | Claims recite "significantly more" than generic computer implementation (Step 2B) through the combination of SHA-256 verification, formal DAG topological ordering, Platt calibration transformation, and 6-tier epistemic demarcation. |
| **EPO Art. 52/56 — *Comvik* Technical Character** | The mathematical transformation of uncalibrated margins into calibrated probabilities and the state-space DAG propagation contribute directly to the technical character of the data processing system, independent of the business application. |
