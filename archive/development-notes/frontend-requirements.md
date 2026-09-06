# DecisionSphere — Frontend Product Requirements & Specifications

**Document Version:** 1.0.0  
**Phase:** Milestone 10 (Frontend & Decision Intelligence UI)  
**Author:** DecisionSphere Product & Engineering Team  
**Status:** COMPLETE & AUTHORITATIVE  

---

## 1. Product Mission & UX Principles

DecisionSphere enables executive decision-makers to simulate and evaluate hypothetical business decisions across commercial demand, supply chain logistics, and workforce attrition **before** committing capital and organizational resources.

The interface must adhere to six mandatory UX principles across all screens:

### Principle 1 — Decision First
The primary viewport must present the synthesized executive decision, Composite Risk Score (CRS), and net financial impact **before** exposing domain modeling mechanics, feature importance, or accounting tables.

### Principle 2 — Progressive Disclosure
Cognitive complexity is revealed deliberately along an established comprehension gradient:
$$\text{Decision} \longrightarrow \text{Risk Decomposition} \longrightarrow \text{Financial Waterfall} \longrightarrow \text{Domain Drivers} \longrightarrow \text{Calculations} \longrightarrow \text{Assumptions} \longrightarrow \text{Provenance}$$

### Principle 3 — Epistemic Honesty
The UI strictly forbids blending statistical machine learning inferences with observed historical ground truth. Every numerical datum, metric card, and table column must display its corresponding 6-tier epistemic tag (`OBSERVED`, `ASSUMED`, `PREDICTED`, `PROPAGATED`, `CALCULATED`, `RECOMMENDED`).

### Principle 4 — Backend Authority
The frontend performs zero mathematical calculations, financial formulas, or probability estimations. The frontend is exclusively responsible for presentation, sorting, filtering, formatting, and charting authoritative backend responses.

### Principle 5 — Explain Every Important Number
Key indicators must never stand alone as bare figures. Each metric must answer:
1. What is it? (Definition & units)
2. Where did it come from? (Epistemic tier & pipeline source)
3. What does it mean? (Contextual threshold / benchmark)
4. What should be done? (Associated strategic directive)

### Principle 6 — Visual Hierarchy Over Visual Decoration
Every pixel must serve comprehension. Distracting effects (excessive gradients, glassmorphism, gratuitous particle animations, oversized cards) are strictly prohibited. Visual weight is reserved for high-severity risk signals, decision categories, and primary bottlenecks.

---

## 2. Information Architecture & Navigation

The application uses a persistent, collapsible sidebar layout with responsive mobile drawers:

```text
DECISIONSPHERE

OVERVIEW
  Dashboard                   /

DECISIONS
  Scenarios                   /scenarios
  Simulate                    /simulate

ANALYSIS
  Simulation Runs             /simulations
  Sensitivity Lab             /sensitivity

GOVERNANCE
  Policies                    /policies
  Audit & Provenance          /audit

SYSTEM
  Model Integrity             /system/models
  System Health               /system/health
```

---

## 3. Screen-by-Screen Functional Requirements

### 3.1 Dashboard / Decision Cockpit (`/`)
- **Purpose**: High-level executive situational awareness and rapid access to recent decisions.
- **Top Viewport (Decision Hero)**:
  - Scenario Selector / Quick Switcher.
  - Decision Category Badge: `PROCEED` (Emerald), `PROCEED_WITH_MITIGATIONS` (Amber), `REJECT_RESTRUCTURE` (Rose).
  - Composite Risk Score meter (0–100) with categorical rating (`LOW`, `MODERATE`, `HIGH`, `SEVERE`).
  - Projected Net Profit Delta formatted as localized currency ($\pm \$X.XK$).
  - Primary Operational Vulnerability callout (e.g., "Workforce Burnout & Overtime Strain").
- **Middle Viewport (Domain Mini-Matrix & Financial Waterfall Preview)**:
  - 3-card domain breakdown comparing Baseline $\rightarrow$ Scenario $\rightarrow$ Delta for Demand (Units), Supply Chain (Late Risk %), and Workforce (Attrition Risk %).
  - Compact summary waterfall chart linking to the full simulation analysis.
- **Bottom Viewport (Recent Simulation Runs Table)**:
  - Tabular view of recent simulation runs showing Run ID, Scenario Name, Version, Policy, Decision, CRS, Net Profit, and Execution Timestamp.

### 3.2 Scenario Workspace (`/scenarios`, `/scenarios/[id]`)
- **Scenario Listing (`/scenarios`)**:
  - Filterable, searchable list of scenarios with name, description, version count, latest decision status, and archive status.
  - "Create Scenario" action opening a modal with title, description, and optional initial lever defaults.
- **Scenario Detail & Interactive Builder (`/scenarios/[id]`)**:
  - Two-column analytical layout:
    - **Left Column (Lever Controls)**:
      - Demand Growth Shock: Slider coupled with numeric input ($-50\%$ to $+100\%$, default $0.0\%$, step $1\%$).
      - Promotional Campaign: Accessible switch toggle (`false` / `true`).
      - Scheduled Days Offset: Slider coupled with numeric input ($-3$ to $+3$ days, default $0$).
      - Shipping Mode Override: Dropdown selector (`Standard Class`, `Second Class`, `First Class`, `Same Day`, or `None / Baseline`).
      - Overtime Workforce Percentage: Slider coupled with numeric input ($0\%$ to $100\%$, default $0.0\%$).
      - Salary Hike Override: Slider coupled with numeric input ($0\%$ to $50\%$, default $None$).
    - **Right Column (Impact Preview & History)**:
      - Version History Timeline: Clear list of immutable versions ($v_1, v_2, \dots$).
      - Visual explanation: "Saving lever modifications creates a new immutable version ($v_{n+1}$). Historical versions and past simulation runs remain untouched."
      - Version Diff inspector comparing lever deltas between two chosen versions.
      - "Run Simulation" primary CTA with pre-execution review.

### 3.3 Simulation Runner & Progress (`/simulate`)
- **Review Step**:
  - Displays Scenario Name, Version, Modified Levers, and Bound Policy (defaulting to Corporate Baseline FY2026).
  - Explicit confirmation requirement before execution.
- **Execution Progress**:
  - Meaningful, non-fabricated progress state reflecting actual pipeline stages:
    1. Validating scenario levers & bounds
    2. Loading corporate assumption policy
    3. Executing Demand model (XGBoost Regressor)
    4. Executing Supply Chain model (Calibrated XGBoost Classifier)
    5. Executing Workforce model (Calibrated XGBoost Classifier)
    6. Computing cross-domain propagation
    7. Evaluating managerial financial waterfall
    8. Synthesizing recommendations & trade-offs
    9. Assembling cryptographic provenance tuple ($\Sigma_{\text{run}}$)
- **Automatic Routing**: Direct seamless transition to `/simulations/[id]` upon completion.

### 3.4 Simulation Results & Decision Analysis (`/simulations/[id]`)
- **A. Executive Decision Section**:
  - Decision Category, Composite Risk Score gauge with domain strain decomposition (Logistics $40\%$, Workforce $40\%$, Commercial $20\%$).
  - Executive Briefing statement from the backend.
- **B. Domain Predictions Comparison**:
  - Demand Forecasting: Historical Baseline vs. Scenario Projection vs. Delta Sales Units.
  - Logistics Delivery Risk: Historical Prevalence vs. Calibrated Scenario Probability vs. Delta.
  - Workforce Attrition Risk: Baseline Rate vs. Calibrated Scenario Attrition vs. Delta.
- **C. Managerial Financial Waterfall**:
  - SVG waterfall chart: Gross Revenue Delta $\rightarrow$ Churn/Cancellation Loss $\rightarrow$ Realized Revenue $\rightarrow$ COGS $\rightarrow$ Carrier Delay Penalties $\rightarrow$ Expedited Freight Surcharge $\rightarrow$ Overtime Labor Wages $\rightarrow$ Voluntary Turnover Replacement $\rightarrow$ Net Profit Delta.
  - Tabular breakdown with exact unrounded accounting numbers and epistemic classifications (`CALCULATED`).
- **D. Rule-Grounded Strategic Recommendations**:
  - Prioritized list sorted by severity (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`).
  - Action identifier (e.g., `ACT-SC-001`), affected domain, description, trigger rule, and explicit non-causal trade-off disclosure.
- **E. Cryptographic Provenance Section**:
  - Collapsible audit panel rendering the 8-element provenance tuple: Scenario Version UUID, Policy Version UUID, 3 Model SHA-256 Hashes, Git Commit SHA, Python Version, App Version, Migration Revision, UTC Execution Timestamp.

### 3.5 Sensitivity Lab (`/sensitivity`)
- Four dedicated analytical experiment tabs:
  1. **Demand Shock Sweep (Experiment B)**: Evaluates non-linear response curves across $[-50\%, +100\%]$ demand growth. Charts demand forecast, delivery risk, and workforce attrition risk simultaneously.
  2. **Financial Coupling Parameter Sweep (Experiment D)**: 1D sweep across `ASM-001` (delay penalty), `ASM-002` (expedite fee), `ASM-004` (replacement cost), or `ASM-005` (overtime wage rate). Plots Net Profit Delta trajectory with a prominent $0$ break-even threshold line.
  3. **CRS Weight Simplex Sweep**: Evaluates decision category and risk score stability when organizational priorities shift across logistics, workforce, and commercial domains.
  4. **Tipping Point Analyzer**: Pinpoints exact boundary thresholds where decision flips (e.g., $18\%$ overtime flips recommendation from `PROCEED_WITH_MITIGATIONS` to `REJECT_RESTRUCTURE`).
- Interpretation panel accompanying every experiment explaining what the curves communicate.

### 3.6 Assumption Policy Governance (`/policies`)
- Listing of corporate assumption policy versions with active/default indicator.
- Creation form for new immutable policy version:
  - Policy title and description.
  - Financial rates: `late_penalty_rate` ($/order), `expedite_fee` ($/order), `stockout_churn_factor` ($[0,1]$), `replacement_cost` ($/employee), `overtime_wage_rate` ($/hour), `cogs_ratio` ($[0,1]$).
  - CRS Simplex Weights: $w_{\text{supply}}$, $w_{\text{workforce}}$, $w_{\text{demand}}$ with real-time visual validation enforcing $\sum w_i = 1.0$.
  - Operational tolerance threshold: $\tau_{\text{risk}}$ ($[0,100]$).
  - Policy immutability notice: "New policy versions do not mutate historical records."

### 3.7 Audit & Provenance Explorer (`/audit`)
- Searchable, filterable audit log of all simulation executions.
- Relational drill-down into exact parameters, model fingerprints, and execution durations.
- Copy-to-clipboard functionality for UUIDs, SHA-256 signatures, and Git commits.

### 3.8 System Health & Model Integrity (`/system/health`, `/system/models`)
- **System Health (`/system/health`)**:
  - Real-time status cards: API Service Liveness, PostgreSQL Connectivity, Model Artifact Integrity, Runtime Environment, App Version.
- **Model Integrity (`/system/models`)**:
  - Authoritative verification table for Retail Demand, DataCo Supply Chain, and IBM HR Attrition models.
  - Displays File Exists, Expected SHA-256, Observed SHA-256, and Verification Status (`VERIFIED`, `HASH_MISMATCH`, `FILE_NOT_FOUND`).
  - **Safety Interlock**: If any model fails verification, the UI displays a global persistent alert banner and disables simulation execution.

---

## 4. Required UX States

Every view must explicitly support and test eight distinct states:

| UX State | Requirement & Visual Behavior |
|---|---|
| **1. Loading** | Skeleton place-holders matching component geometry; smooth shimmer animation; no layout jumps (`contain-intrinsic-size`). |
| **2. Empty** | Clear illustration, explanatory message, and actionable next step (e.g., "No scenarios created yet. Create your first scenario to begin simulating business impacts."). |
| **3. Validation Error** | Inline field-level messages with `aria-invalid="true"` and `:user-invalid` styling; form-level summary if multiple errors exist. |
| **4. API Error** | User-friendly error message, error code (e.g., `RESOURCE_NOT_FOUND`), correlation ID (`request_id`), and a "Retry" CTA button. |
| **5. Simulation Failure** | Explicit notice that simulation execution halted and no trustworthy result was produced; displays server diagnostics and logs correlation ID. |
| **6. Model Integrity Failure** | System-wide persistent warning banner; disables all simulation execution triggers; provides link to `/system/models`. |
| **7. Partial Failure / Degraded** | If non-critical secondary metrics fail to load, display available primary metrics with a graceful fallback badge on failed widgets. |
| **8. Disabled / Permission** | Visible disabled state with descriptive tooltip explaining why the action is locked (e.g., "Cannot run simulation: Model integrity failure detected."). |

---

## 5. Accessibility (WCAG 2.2 AA)

- **Contrast Ratios**: Minimum $4.5:1$ for normal text, $3:1$ for large text and UI components/borders against dark and light surfaces.
- **Non-Color Dependence**: Every metric, badge, and status indicator must convey meaning through text, shape, or iconography in addition to color.
- **Keyboard Navigation**: Full tab order traversal across sidebar, forms, sliders, tables, modals, and tabs. Visible outline focus ring (`ring-2 ring-primary ring-offset-2`).
- **Screen Reader Support**: Semantic HTML (`<main>`, `<nav>`, `<aside>`, `<header>`, `<article>`, `<table>`). Form inputs linked to error messages via `aria-errormessage` and `aria-describedby`.
- **Reduced Motion**: Respects `prefers-reduced-motion: reduce`. Animations and transitions are instantly resolved.

---

## 6. Responsive Design Matrix

| Breakpoint | Viewport Width | Navigation Behavior | Analytical Layout Behavior |
|---|---|---|---|
| **Desktop / Wide** | $\ge 1280\text{px}$ | Persistent expanded sidebar ($260\text{px}$) | Full multi-column analytical panels; side-by-side lever configuration and live preview. |
| **Laptop / Compact** | $1024\text{px} - 1279\text{px}$ | Collapsible icon sidebar with hover tooltips | Stacked or 2-column grids; sticky review and run trigger bars. |
| **Tablet** | $768\text{px} - 1023\text{px}$ | Slide-over drawer navigation triggered via hamburger menu | Single-column cards with expandable accordions for secondary evidence. |
| **Mobile** | $< 768\text{px}$ | Mobile drawer menu; compact header | Priority given to Decision Hero and primary recommendation; financial waterfall renders as stacked bars and scrollable table. |
