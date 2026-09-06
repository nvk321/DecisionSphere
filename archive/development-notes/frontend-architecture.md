# DecisionSphere — Frontend Architectural Specification & Design System

**Document Version:** 1.0.0  
**Phase:** Milestone 10 (Frontend & Decision Intelligence UI)  
**Author:** DecisionSphere Frontend & Architecture Team  
**Status:** COMPLETE & AUTHORITATIVE  

---

## 1. System Overview & Technology Stack

DecisionSphere Frontend is structured as an enterprise-grade Single Page Application (SPA) powered by **Next.js (App Router)** and **React 19**, written in strict **TypeScript**.

### Technology Matrix

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Runtime / Framework** | Next.js (App Router) | 15.x / React 19 | Server Component boundaries, route code-splitting, static/client hybrid architecture. |
| **Type System** | TypeScript | 5.x | Strict null safety, interface synchronization with Pydantic v2 schemas. |
| **Design System / CSS** | Tailwind CSS + CSS Variables | Modern v4 | Semantic design tokens, dark/light theme switching, low bundle footprint. |
| **UI Primitives** | Radix UI / Accessible Primitives | Current | WCAG 2.2 AA accessible base (Dialog, Tabs, Slider, Tooltip, Switch, Select). |
| **Server State Management** | TanStack Query | v5 | Cache invalidation, query deduplication, optimistic updates, mutation orchestration. |
| **Form Handling & Validation** | React Hook Form + Zod | Current | Uncontrolled form inputs for lag-free slider dragging with Gate E boundary validation. |
| **Data Visualization** | Recharts | Current | SVG-based responsive charting for waterfalls, demand curves, and simplex matrices. |
| **Iconography** | Lucide React | Current | Consistent, clean 24px stroke-based icons. |
| **Unit / Component Testing** | Vitest + React Testing Library | Current | Rapid unit and interaction testing. |
| **End-to-End Automation** | Playwright | Current | Headless browser integration testing against live containerized FastAPI backend. |

---

## 2. Directory Structure & Architecture

The frontend application resides cleanly in `frontend/`:

```text
frontend/
├── public/                     # Static assets, branding marks
├── src/
│   ├── app/                    # Next.js App Router route hierarchy
│   │   ├── layout.tsx          # Root layout mounting QueryClientProvider, ThemeProvider, AppShell
│   │   ├── globals.css         # CSS design tokens, base resets, modern scrollbar styles
│   │   ├── page.tsx            # / (Decision Cockpit / Executive Dashboard)
│   │   ├── scenarios/
│   │   │   ├── page.tsx        # /scenarios (Scenario Workspace & Listing)
│   │   │   └── [id]/page.tsx   # /scenarios/[id] (Interactive Scenario Builder & History)
│   │   ├── simulate/
│   │   │   └── page.tsx        # /simulate (Simulation Runner & Execution Progress)
│   │   ├── simulations/
│   │   │   ├── page.tsx        # /simulations (Historical Simulation Runs Table)
│   │   │   └── [id]/page.tsx   # /simulations/[id] (Decision Analysis & Results View)
│   │   ├── sensitivity/
│   │   │   └── page.tsx        # /sensitivity (Sensitivity Lab: Experiments B & D)
│   │   ├── policies/
│   │   │   └── page.tsx        # /policies (Assumption Policy Governance)
│   │   ├── audit/
│   │   │   └── page.tsx        # /audit (Audit & Cryptographic Provenance Explorer)
│   │   └── system/
│   │       ├── health/page.tsx # /system/health (System Diagnostics & Connectivity)
│   │       └── models/page.tsx # /system/models (ML Model Integrity & Fingerprints)
│   ├── components/
│   │   ├── layout/             # Shell components: Sidebar, Header, Breadcrumbs, PageHeader
│   │   ├── ui/                 # Reusable design primitives (Card, Badge, Button, Slider, etc.)
│   │   ├── common/             # EpistemicBadge, ErrorBanner, MetricDisplay, LoadingSkeleton
│   │   ├── dashboard/          # DecisionHero, DomainMiniMatrix, CompactWaterfall
│   │   ├── scenarios/          # LeverControls, VersionTimeline, VersionDiff, ScenarioModal
│   │   ├── simulations/        # SimulationProgress, DomainComparison, FinancialWaterfall, RecommendationCard, ProvenanceCard
│   │   ├── sensitivity/        # DemandSweepChart, FinancialSweepChart, CRSSweepChart, TippingPointPanel
│   │   └── policies/           # PolicyForm, SimplexValidator, PolicyVersionList
│   ├── lib/
│   │   ├── api/                # Strongly-typed API client and TanStack Query hooks
│   │   │   ├── client.ts       # Central HTTP client, correlation IDs, error normalization
│   │   │   ├── types.ts        # TypeScript interfaces mirrored from backend Pydantic models
│   │   │   ├── scenarios.ts    # Scenario queries and mutations
│   │   │   ├── simulations.ts  # Simulation execution and history queries
│   │   │   ├── policies.ts     # Assumption policy queries and mutations
│   │   │   ├── sensitivity.ts  # Sensitivity sweep mutations
│   │   │   └── system.ts       # Health and model integrity probes
│   │   ├── utils/              # Formatters (currency, percent, date), classnames merge (cn)
│   │   └── constants/          # Epistemic tier colors, default policy rates, allowable bounds
├── tests/
│   ├── unit/                   # Vitest unit tests (formatters, validators, epistemic logic)
│   ├── components/             # React Testing Library component tests
│   └── e2e/                    # Playwright end-to-end browser automation suites
├── package.json
├── tsconfig.json
├── next.config.ts
└── tailwind.config.ts
```

---

## 3. Design System & Design Tokens

### 3.1 Color Semantics (Dark Mode Default + Light Mode Support)

All colors are expressed as HSL / OKLCH CSS custom properties:

```css
:root {
  /* Surface & Base */
  --background: 222.2 84% 4.9%;        /* #020817 Deep Slate / Obsidian */
  --foreground: 210 40% 98%;          /* #f8fafc Crisp Light */
  --surface-1: 222.2 84% 7.5%;        /* Base container card */
  --surface-2: 217.2 32.6% 12%;       /* Nested card / secondary surface */
  --surface-3: 217.2 32.6% 17.5%;     /* Hover / elevated surface */
  --border: 217.2 32.6% 17.5%;        /* Subtle clean borders */

  /* Decision Categories */
  --decision-proceed: 142.1 76.2% 36.3%;        /* #16a34a Emerald */
  --decision-mitigate: 38 92% 50%;             /* #f59e0b Amber */
  --decision-reject: 346.8 77.2% 49.8%;        /* #e11d48 Rose */

  /* Risk Tiers */
  --risk-low: 142.1 76.2% 36.3%;               /* Low operational risk */
  --risk-moderate: 38 92% 50%;                 /* Moderate operational strain */
  --risk-high: 24.6 95% 53.1%;                 /* High operational strain */
  --risk-severe: 346.8 77.2% 49.8%;            /* Severe / bottleneck breached */

  /* Epistemic Tiers */
  --epistemic-observed: 215 16% 47%;           /* Slate: Historical ground truth */
  --epistemic-predicted: 258 90% 66%;          /* Violet: ML statistical inference */
  --epistemic-assumed: 199 89% 48%;            /* Cyan: User scenario lever */
  --epistemic-propagated: 32 95% 44%;          /* Amber: Operational cross-domain bridge */
  --epistemic-calculated: 160 84% 39%;         /* Mint: Deterministic accounting formula */
  --epistemic-recommended: 280 82% 55%;        /* Purple: Synthesized strategic directive */

  /* System Status */
  --status-healthy: 142.1 76.2% 36.3%;
  --status-degraded: 38 92% 50%;
  --status-error: 346.8 77.2% 49.8%;
}
```

### 3.2 Typography Hierarchy

- **Font Family**: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif.
- **Monospace / Numerical Data**: "JetBrains Mono", "Fira Code", ui-monospace, SFMono-Regular, monospace.
- **Typographic Scale**:
  - `Display / KPI`: `text-3xl font-extrabold tracking-tight` (30px / 36px) — Reserved for Decision Category and Net Profit Impact.
  - `Page Title`: `text-2xl font-bold tracking-tight` (24px / 32px).
  - `Section Title`: `text-lg font-semibold tracking-tight` (18px / 28px).
  - `Body / Description`: `text-sm font-normal text-muted-foreground` (14px / 20px).
  - `Metric Label / Table Header`: `text-xs font-medium uppercase tracking-wider text-muted-foreground` (12px / 16px).
  - `Data / Figures`: Monospaced font with tabular numbers (`tabular-nums`) to prevent jitter during updates.

### 3.3 Spacing, Borders & Radius
- **Radius**: Restrained rounding (`rounded-lg` = $8\text{px}$, `rounded-md` = $6\text{px}$). No oversized pill containers.
- **Borders**: Clean `1px solid hsl(var(--border))` with elevated contrast rather than heavy drop shadows.
- **Motion**: Subtle $150\text{ms} - 200\text{ms}$ ease-out transitions for interactive elements; completely bypassed when `prefers-reduced-motion` is active.

---

## 4. Typed API Client Architecture (`frontend/src/lib/api/`)

### 4.1 Request & Response Pipeline

```text
React Component / Page
        │
        ▼
TanStack Query Hook (e.g. useScenario, useSimulate)
        │
        ▼
Typed API Module (e.g. scenarios.ts, simulations.ts)
        │
        ▼
Central API Client (client.ts)
  - Injects correlation ID (X-Request-ID)
  - Configures Base URL (/api/v1 via Next.js rewrite or direct)
  - Normalizes Error Envelopes (AppError)
        │
        ▼
FastAPI REST Backend (Uvicorn / Docker)
```

### 4.2 Error Normalization & Types

```typescript
export interface BackendErrorDetail {
  loc: string[];
  msg: string;
  type: string;
}

export interface BackendErrorEnvelope {
  error: {
    code: string;
    message: string;
    request_id?: string;
    details?: {
      errors?: BackendErrorDetail[];
      [key: string]: unknown;
    };
  };
}

export class DecisionSphereAPIError extends Error {
  public readonly code: string;
  public readonly requestId?: string;
  public readonly statusCode: number;
  public readonly details?: unknown;

  constructor(message: string, code: string, statusCode: number, requestId?: string, details?: unknown) {
    super(message);
    this.name = "DecisionSphereAPIError";
    this.code = code;
    this.statusCode = statusCode;
    this.requestId = requestId;
    this.details = details;
  }
}
```

---

## 5. Security & Safety Architecture

### 5.1 Model Integrity Simulation Interlock
1. On application mount, `useModelStatus()` queries `GET /api/v1/models/status`.
2. If `all_verified` is `false` or any model has status `HASH_MISMATCH` or `FILE_NOT_FOUND`:
   - An alert banner is pinned globally to the application header.
   - All "Run Simulation" buttons across the application are disabled with a tooltip: *"Simulation disabled: ML model integrity failure detected."*
   - Direct navigation to `/system/models` is provided with comparison of expected vs. observed SHA-256 hashes.

### 5.2 Gate G: Version Immutability Guarantee
1. When a user updates scenario levers, the UI clearly displays: *"Saving modifications creates a new immutable scenario version ($v_{n+1}$). Historical runs remain bound to version $v_n$."*
2. The payload is submitted via `PATCH /api/v1/scenarios/{id}` with `new_levers`.
3. The server persists the new `ScenarioVersion` row with an incremented version number. Historical records are never modified.

---

## 6. Testing Strategy

### 6.1 Unit Tests (Vitest)
- Formatter functions: Currency (`$120,400.00`, `-$504.5K`), percentages (`+15.0%`), numbers with sign.
- Epistemic badge metadata mapping (color, glyph, accessible description).
- Simplex weight equality validation ($\sum w_i = 1.0 \pm 10^{-5}$).
- Lever range boundary enforcement matching Gate E.

### 6.2 Component Tests (React Testing Library)
- `DecisionHero`: Correct categorization badge, CRS score, and primary vulnerability display.
- `LeverControls`: Slider and numeric input synchronization, range limits, reset behavior.
- `FinancialWaterfall`: Correct aggregation, negative expense representation, tabular accessibility.
- `ErrorBanner`: Request ID rendering and retry button dispatch.

### 6.3 End-to-End Tests (Playwright)
- **Happy Path Workflow**:
  1. Open dashboard, verify system health indicator is green.
  2. Navigate to `/scenarios`, click "Create Scenario", enter name.
  3. Adjust levers in `/scenarios/[id]` (Demand $+20\%$, Overtime $30\%$).
  4. Click "Run Simulation", review parameters in `/simulate`, confirm execution.
  5. Verify redirect to `/simulations/[id]`.
  6. Inspect Decision Category, Domain Predictions, Financial Waterfall, and Cryptographic Provenance.
- **Safety Interlock Test**:
  1. Trigger model integrity probe degradation.
  2. Verify simulation execution controls are disabled.
  3. Verify warning alert displays expected vs observed hash details.
