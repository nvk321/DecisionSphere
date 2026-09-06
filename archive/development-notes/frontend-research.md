# DecisionSphere — Frontend UX/UI Research & Contract Audit

**Document Version:** 1.0.0  
**Phase:** Milestone 10 (Frontend & Decision Intelligence UI)  
**Author:** DecisionSphere Frontend & Architecture Team  
**Status:** COMPLETE & AUTHORITATIVE  

---

## 1. Executive Summary & Objective

DecisionSphere is not a CRUD dashboard, a static metrics report, or an exploratory notebook viewer. It is an **enterprise decision-intelligence and scenario-analysis platform**. Its core user experience must answer seven sequential executive questions:

1. **What is happening?** (Current baseline vs. hypothetical shock)
2. **Why is it happening?** (Dominant operational bottlenecks and ML driver attributions)
3. **What happens if I change an assumption?** (Interactive scenario levers with immediate parameter bounds)
4. **What is the financial impact?** (Deterministic managerial income statement waterfall)
5. **What action is recommended?** (Prioritized strategic directives and non-causal trade-offs)
6. **What evidence supports that recommendation?** (Cross-domain predictions, calibrated probabilities, empirical feature rankings)
7. **Can the decision be reproduced and audited?** (Cryptographic provenance tuple $\Sigma_{\text{run}}$ verifying model SHA-256 hashes, Git commit, migration revision, and exact runtime parameters)

This research document bridges academic decision-support theory, cognitive engineering, modern web standards (incorporating `modern-web-guidance`), and the frozen Phase 9 FastAPI backend contracts.

---

## 2. Backend & Frontend Contract Matrix

Every UI capability is bound to the authoritative Phase 9 backend. No data fields may be invented on the client side.

| # | Capability | HTTP Method & Endpoint | Request Payload / Params | Response Payload Contract | UI Consumer Component / View |
|---|---|---|---|---|---|
| **1** | System Liveness & Readiness | `GET /api/v1/health` | None | `HealthResponse` (`status`, `app_name`, `version`, `database`, `models_verified`, `models`) | Header System Status Pill, `/system/health` |
| **2** | ML Model Integrity Verification | `GET /api/v1/models/status` | None | `ModelStatusResponse` (`status`, `all_verified`, `models` dictionary with SHA-256, path, existence, verification status) | `/system/models`, Simulation Safety Interlock |
| **3** | List Strategic Scenarios | `GET /api/v1/scenarios/` | Query: `skip`, `limit`, `include_archived` | `PaginatedResponse[ScenarioResponse]` (`items`, `total`, `page`, `page_size`, `total_pages`) | `/scenarios`, Scenario Quick Switcher in Dashboard |
| **4** | Create Strategic Scenario | `POST /api/v1/scenarios/` | `ScenarioCreate` (`name`, `description`, optional `initial_levers`) | `ScenarioResponse` (`id`, `name`, `description`, `is_archived`, `created_at`, `updated_at`, `versions`) | `/scenarios` (Create Modal) |
| **5** | Get Scenario Detail & Latest Version | `GET /api/v1/scenarios/{id}` | Path: `id` (UUID) | `ScenarioResponse` with all nested `ScenarioVersionResponse` items | `/scenarios/[id]` (Workspace) |
| **6** | Update Metadata or Submit New Levers | `PATCH /api/v1/scenarios/{id}` | `ScenarioUpdate` (`name`, `description`, `new_levers` / `levers`) | `ScenarioResponse` (Creates new immutable `ScenarioVersion` if levers provided) | `/scenarios/[id]` (Settings & Lever Form) |
| **7** | Soft-Archive Scenario | `DELETE /api/v1/scenarios/{id}` | Path: `id` (UUID) | `ScenarioResponse` (`is_archived=True`) | `/scenarios` (Archive Confirmation Dialog) |
| **8** | List Scenario Immutable Versions | `GET /api/v1/scenarios/{id}/versions` | Path: `id` (UUID) | `List[ScenarioVersionResponse]` (`id`, `version_number`, levers, `created_at`) | `/scenarios/[id]` (Version History Drawer & Diff) |
| **9** | Get Specific Scenario Version | `GET /api/v1/scenarios/{id}/versions/{v_id}` | Path: `id`, `v_id` | `ScenarioVersionResponse` | `/scenarios/[id]` (Historical Version Inspection) |
| **10** | Run Simulation for Scenario Shortcut | `POST /api/v1/scenarios/{id}/run` | `SimulationRequest` (`override_levers`, `policy_id`) | `SimulationDetailResponse` | `/scenarios/[id]` (Quick Run Action) |
| **11** | Execute Atomic Multi-Domain Simulation | `POST /api/v1/simulations/run` | `SimulationRequest` (`scenario_version_id`, `policy_id`, `override_levers`) | `SimulationDetailResponse` (`id`, `status`, `duration_ms`, `domain_predictions`, `financial_result`, `recommendation_result`, `audit_record`) | `/simulate` (Interactive Runner), Results Transition |
| **12** | Get Simulation Run Relational Tree | `GET /api/v1/simulations/{run_id}` | Path: `run_id` (UUID) | `SimulationDetailResponse` (Full relational tree) | `/simulations/[id]` (Decision Analysis Screen), Dashboard Hero |
| **13** | List Historical Simulation Runs | `GET /api/v1/simulations/` | Query: `scenario_id`, `skip`, `limit` | `PaginatedResponse[SimulationRunSummaryResponse]` (`id`, `decision_category`, `composite_risk_score`, `net_profit_delta`, `executed_at`) | `/simulations` (Run History Table), Dashboard Recent Runs |
| **14** | List Assumption Policies | `GET /api/v1/policies/` | Query: `skip`, `limit` | `List[PolicyResponse]` (`id`, `version_number`, `name`, `tau_risk`, simplex weights, financial rates) | `/policies` (Policy Governance List) |
| **15** | Get Active Corporate Baseline Policy | `GET /api/v1/policies/default` | None | `PolicyResponse` (v1 Corporate Baseline FY2026) | `/simulate` (Default Policy Binding), `/policies` |
| **16** | Get Specific Assumption Policy | `GET /api/v1/policies/{policy_id}` | Path: `policy_id` (UUID) | `PolicyResponse` | `/policies/[id]` |
| **17** | Create New Assumption Policy Version | `POST /api/v1/policies/` | `PolicyCreate` (`name`, `description`, financial rates, simplex weights: $w_s+w_w+w_d=1.0$, $\tau_{\text{risk}}$) | `PolicyResponse` (New immutable policy version) | `/policies` (New Policy Form with Simplex Validator) |
| **18** | Demand Shock Sweep (Experiment B) | `POST /api/v1/sensitivity/demand-sweep` | `DemandShockSweepRequest` (`base_levers`, `shock_percentages`) | `List[DemandShockSweepItem]` (`shock_pct`, `demand_forecast`, `late_delivery_risk`, `workforce_attrition_risk`) | `/sensitivity` (Demand Response Curve) |
| **19** | Financial Parameter Sweep (Experiment D) | `POST /api/v1/sensitivity/financial-sweep` | `FinancialSweepRequest` (`scenario_version_id`, `policy_id`, `parameter_name`, `candidate_values`) | `List[FinancialSweepItem]` (`parameter_name`, `value`, `net_profit_delta`, `is_profitable`) | `/sensitivity` (Financial Sensitivity & Break-Even) |
| **20** | CRS Simplex Weight Sweep | `POST /api/v1/sensitivity/crs-weight-sweep` | `CRSWeightSweepRequest` (`scenario_version_id`, `policy_id`, `candidate_weights`, `tau_risk`) | `List[CRSWeightSweepItem]` (`w_supply`, `w_workforce`, `w_demand`, `composite_risk_score`, `risk_level`, `decision_category`) | `/sensitivity` (Priority Simplex Stability Matrix) |
| **21** | Decision Tipping Point Search | `POST /api/v1/sensitivity/tipping-point` | `FlipThresholdSearchRequest` (`scenario_version_id`, `policy_id`, `parameter_name`, `candidate_values`) | `FlipThresholdResponse` (`parameter_name`, `flip_detected`, `flip_value`, `previous_category`, `new_category`, `net_profit_delta`) | `/sensitivity` (Tipping Point Analyzer) |

### 2.1 Backend Contract Auditing & Edge Cases
- **Immutability Invariant (Gate G)**: Updating levers via `PATCH /api/v1/scenarios/{id}` or `POST /api/v1/scenarios/{id}/run` does NOT modify the historical `ScenarioVersion`. It creates an incremented version ($v_n \rightarrow v_{n+1}$). The UI must make this version transition transparent.
- **Model Integrity Interlock (Gate I)**: If `models_verified` is `false`, the backend rejects simulation runs with HTTP 503 (`MODEL_INTEGRITY_FAILURE`). The frontend must proactively inspect this on mount and disable simulation execution controls.
- **Error Envelopes**: Errors return `{"error": {"code": str, "message": str, "request_id": str, "details": dict}}`. The frontend client must catch this envelope and extract `code` and `request_id` for user-facing diagnosis.
- **Pagination**: Paginated endpoints return `items`, `total`, `page`, `page_size`, `total_pages`. The UI table components must support zero-based `skip` / `limit` parameters while displaying 1-indexed pages.

---

## 3. Product UX Research: Decision-Intelligence & Analytical Systems

### 3.1 Mental Models in Strategic Decision Making
Decision-makers operate under cognitive bandwidth limitations. Standard enterprise software fails when it forces users to hunt across five tabs to answer "Should we do this?".
In strategic planning (e.g., executing a promotion, extending delivery windows, mandating overtime), decision-makers need a clear cognitive pipeline:
$$\text{Executive Intent} \longrightarrow \text{Simulated Consequence} \longrightarrow \text{Trade-off Evaluation} \longrightarrow \text{Action Directives}$$

### 3.2 Epistemic Status & Uncertainty Communication
In academic research and enterprise risk management, the most dangerous failure mode is **epistemic confusion**—mistaking a statistical model inference for historical fact, or treating an accounting assumption as an empirical forecast. DecisionSphere enforces a 6-tier hierarchy:

| Epistemic Tier | Scientific Meaning | Visual Encoding in UI | Example Data Element |
|---|---|---|---|
| `OBSERVED` | Measured historical empirical baseline | Slate / Zinc Neutral Badge with solid border | Baseline Store Sales (5,840 units), Historical Delay Rate (54.8%) |
| `PREDICTED` | Statistical ML inference $P(Y \mid X)$ | Violet / Indigo Badge with sparkle glyph | Projected Sales (6,850 units), Calibrated Late Risk (62.3%) |
| `ASSUMED` | User-defined scenario lever or policy parameter | Sky / Cyan Badge with slider glyph | Demand Growth Shock (+15%), Expedite Fee ($15/order) |
| `PROPAGATED` | Deterministic cross-domain bridge | Amber / Orange Badge with link glyph | Imputed Overtime WorkLifeBalance Shift ($\Delta \text{WLB} = -1$) |
| `CALCULATED` | Exact deterministic managerial accounting formula | Emerald / Mint Badge with calculator glyph | Realized Gross Margin ($\Delta \$120,400$), Delay Penalties |
| `RECOMMENDED` | Rule-grounded multi-criteria strategic synthesis | Purple / Fuchsia Badge with compass glyph | Decision Category (`REJECT_RESTRUCTURE`), Strategic Actions |

### 3.3 Design Decisions & Anti-Patterns Matrix

For every core design decision in DecisionSphere, we establish strict rules:

| Design Decision | Principle | Why It Matters for DecisionSphere | DecisionSphere Implementation | Anti-Pattern to Avoid |
|---|---|---|---|---|
| **Decision-First Visual Hierarchy** | Decision outcome before technical mechanics | Executives have seconds to understand operational posture | Prominent Decision Hero Card showing Decision Category, CRS, and Net Profit Delta before charts | Burying the recommendation at the bottom of a 20-card dashboard |
| **Progressive Disclosure** | Gradual revelation of operational complexity | Prevents cognitive overload while allowing auditability | Decision $\rightarrow$ Drivers $\rightarrow$ Financial Waterfall $\rightarrow$ Predictions $\rightarrow$ Provenance | Dumping raw JSON or 30 unformatted metrics into the initial viewport |
| **Epistemic Demarcation** | Explicit categorization of every metric | Prevents epistemic confusion between model guesses and facts | Colored `EpistemicBadge` components on all data points and column headers | Uniform typography that implies all numbers have equal certainty |
| **Backend Authority** | Zero client-side mathematical reproduction | Guarantees scientific reproducibility across platforms | Frontend strictly visualizes backend responses; zero formulas in TypeScript | Re-computing financial line items or summing CRS weights in React |
| **Accessible Form Controls** | Predictable, restrained scenario lever adjustment | Ensures scenario parameters stay within valid analytical bounds | Sliders coupled with numeric inputs, explicit units, and min/max limits | Unbounded text inputs that trigger 422 errors on backend submission |
| **Cryptographic Provenance** | Non-intrusive yet complete audit trail | Validates academic rigor and compliance reproducibility | Collapsible provenance drawer/section displaying SHA-256 hashes and Git commit | Omitting model hashes or hiding execution metadata |
| **Safety Interlocks** | System state dictates operational capability | Prevents execution of unverified ML models | Global banner and disabled execution triggers if model integrity check fails | Silently running predictions against corrupted model binaries |

---

## 4. Modern Web Standards & `modern-web-guidance` Audit

Applying research from the Chrome and Edge web platform teams (`modern-web-guidance`):

1. **Accessible Error Synchronization (`accessible-error-announcement`)**:
   - In form inputs (e.g., scenario lever overrides, policy parameters), synchronize CSS `:user-invalid` with ARIA `aria-invalid="true"` and `aria-errormessage`.
   - Avoid premature error announcements on initial tab focus. Only announce errors after interaction and blur.
2. **Performance in Complex Layouts (`interactions-in-complex-layouts`)**:
   - For multi-column analytical views (e.g., Scenario Workspace lever panel + live impact preview), apply `content-visibility: auto` with `contain-intrinsic-size` to off-screen calculation tables and historical comparison lists to avoid global document reflow during slider movement.
3. **Restrained Theming & Dark Mode (`dark-mode`)**:
   - Implement seamless dark/light modes using CSS `color-scheme` and HSL/OKLCH design tokens.
   - Synchronize browser UI scrollbars via `scrollbar-color` and `scrollbar-width` without bloating the bundle with heavy JavaScript scrollbars.
4. **Accessible Charts**:
   - Every Recharts visualization must have an accessible data table alternative, screen-reader summaries (`aria-label`, `aria-describedby`), and dual encoding (never relying on color hue alone—using shapes, dashed lines, and numerical tooltips).
5. **Reduced Motion**:
   - Adhere strictly to `@media (prefers-reduced-motion: reduce)`. Disable slider transitions, progress bar animations, and tab slide effects when reduced motion is requested.

---

## 5. Technology Stack Selection & Version Rationale

| Dependency / Layer | Selection | Version Target | Engineering Rationale |
|---|---|---|---|
| **Framework** | Next.js (App Router) | 15.x / React 19 | Server Component boundaries, route-level code splitting, edge-ready proxying, zero layout flash. |
| **Language** | TypeScript | 5.x | Strict null checks, end-to-end type safety matching backend Pydantic schemas. |
| **Styling** | Tailwind CSS + CSS Variables | v4 / Modern CSS | Zero runtime overhead, design token variables, accessible contrast ratios. |
| **Component Primitives** | Radix UI / shadcn style primitives | Current | Headless, accessible primitives (Dialog, Tabs, Slider, Tooltip, Dropdown) with full WCAG 2.2 keyboard navigation. |
| **State & Server Cache** | TanStack Query | v5 | Automated caching, background refetching, mutation lifecycle, optimistic updates, request deduplication. |
| **Form Validation** | React Hook Form + Zod | Current | Performant, uncontrolled inputs with zero re-render lag during rapid slider dragging; schema validation matching Gate E. |
| **Data Visualization** | Recharts | Current | SVG-based, responsive, declarative React charting library capable of custom waterfall bars, domain curves, and tipping-point annotations. |
| **Icons** | Lucide React | Current | Lightweight, clean, consistent stroke-width iconography. |
| **Testing** | Vitest + Testing Library + Playwright | Current | Fast unit/component tests in Node v26 and cross-browser End-to-End browser automation against the FastAPI backend. |

---

## 6. Verification Against Strict Invariants

1. **Zero modifications to `src/`**: Validated. The frontend lives entirely in `frontend/` and `docs/`.
2. **Zero modifications to model binaries**: Validated. `models/` remains untouched.
3. **No client-side calculations**: Validated. All numbers, waterfalls, and recommendations are sourced from FastAPI endpoints.
4. **No invented fields**: Validated. The contract matrix maps 1-to-1 with Phase 9 schemas.
5. **No mocked production data**: Validated. The frontend communicates with the real backend.
6. **No bypass of backend validation**: Validated. Front-end Zod schemas mirror backend Pydantic bounds (`[-50, 100]` for demand shock, simplex $\sum w_i = 1.0$).
7. **Immutable versioning preserved**: Validated. Creating new levers triggers a version increment; historical versions are never overwritten.
8. **Provenance visible**: Validated. Provenance tuple is rendered in full detail on simulation results and audit views.
