/**
 * Authoritative Constants for DecisionSphere Frontend.
 */

export type EpistemicTier =
  | "OBSERVED"
  | "PREDICTED"
  | "ASSUMED"
  | "PROPAGATED"
  | "CALCULATED"
  | "RECOMMENDED";

export interface EpistemicMeta {
  label: string;
  badgeClass: string;
  borderClass: string;
  bgClass: string;
  textClass: string;
  description: string;
}

export const EPISTEMIC_TIERS: Record<EpistemicTier, EpistemicMeta> = {
  OBSERVED: {
    label: "OBSERVED",
    badgeClass: "bg-slate-800/80 text-slate-300 border-slate-700",
    borderClass: "border-slate-700",
    bgClass: "bg-slate-900/40",
    textClass: "text-slate-300",
    description: "Historical ground truth from benchmark datasets",
  },
  PREDICTED: {
    label: "PREDICTED",
    badgeClass: "bg-violet-900/50 text-violet-300 border-violet-700/60",
    borderClass: "border-violet-700/60",
    bgClass: "bg-violet-950/30",
    textClass: "text-violet-300",
    description: "Machine learning conditional statistical inference P(Y|X)",
  },
  ASSUMED: {
    label: "ASSUMED",
    badgeClass: "bg-sky-900/50 text-sky-300 border-sky-700/60",
    borderClass: "border-sky-700/60",
    bgClass: "bg-sky-950/30",
    textClass: "text-sky-300",
    description: "User-defined scenario lever or corporate policy parameter",
  },
  PROPAGATED: {
    label: "PROPAGATED",
    badgeClass: "bg-amber-900/50 text-amber-300 border-amber-700/60",
    borderClass: "border-amber-700/60",
    bgClass: "bg-amber-950/30",
    textClass: "text-amber-300",
    description: "Algorithmic cross-domain operational bridge",
  },
  CALCULATED: {
    label: "CALCULATED",
    badgeClass: "bg-emerald-900/50 text-emerald-300 border-emerald-700/60",
    borderClass: "border-emerald-700/60",
    bgClass: "bg-emerald-950/30",
    textClass: "text-emerald-300",
    description: "Deterministic mathematical managerial accounting formula",
  },
  RECOMMENDED: {
    label: "RECOMMENDED",
    badgeClass: "bg-purple-900/50 text-purple-300 border-purple-700/60",
    borderClass: "border-purple-700/60",
    bgClass: "bg-purple-950/30",
    textClass: "text-purple-300",
    description: "Prioritized rule-grounded strategic intervention",
  },
};

export type DecisionCategory =
  | "PROCEED"
  | "PROCEED_WITH_MITIGATIONS"
  | "REJECT_RESTRUCTURE";

export interface DecisionMeta {
  label: string;
  badgeClass: string;
  borderClass: string;
  bgClass: string;
  textClass: string;
  summary: string;
}

export const DECISION_CATEGORIES: Record<DecisionCategory, DecisionMeta> = {
  PROCEED: {
    label: "PROCEED",
    badgeClass: "bg-emerald-950 text-emerald-300 border-emerald-600",
    borderClass: "border-emerald-600",
    bgClass: "bg-emerald-950/40",
    textClass: "text-emerald-400",
    summary: "Simulated scenario operates within operational tolerances and delivers positive economic value.",
  },
  PROCEED_WITH_MITIGATIONS: {
    label: "PROCEED WITH MITIGATIONS",
    badgeClass: "bg-amber-950 text-amber-300 border-amber-600",
    borderClass: "border-amber-600",
    bgClass: "bg-amber-950/40",
    textClass: "text-amber-400",
    summary: "Scenario creates manageable operational strain requiring prioritized mitigation actions.",
  },
  REJECT_RESTRUCTURE: {
    label: "REJECT / RESTRUCTURE",
    badgeClass: "bg-rose-950 text-rose-300 border-rose-600",
    borderClass: "border-rose-600",
    bgClass: "bg-rose-950/40",
    textClass: "text-rose-400",
    summary: "Critical operational strain or negative economic returns breached acceptable thresholds.",
  },
};

export type RiskLevel = "LOW" | "MODERATE" | "HIGH" | "SEVERE";

export const RISK_LEVELS: Record<RiskLevel, { label: string; color: string; badgeClass: string }> = {
  LOW: {
    label: "LOW RISK",
    color: "#16a34a",
    badgeClass: "bg-emerald-950 text-emerald-300 border-emerald-600",
  },
  MODERATE: {
    label: "MODERATE RISK",
    color: "#f59e0b",
    badgeClass: "bg-amber-950 text-amber-300 border-amber-600",
  },
  HIGH: {
    label: "HIGH RISK",
    color: "#ea580c",
    badgeClass: "bg-orange-950 text-orange-300 border-orange-600",
  },
  SEVERE: {
    label: "SEVERE STRAIN",
    color: "#e11d48",
    badgeClass: "bg-rose-950 text-rose-300 border-rose-600",
  },
};

export const VALID_SHIPPING_MODES = [
  "Standard Class",
  "Second Class",
  "First Class",
  "Same Day",
] as const;

export const DEFAULT_POLICY_CONSTANTS = {
  late_penalty_rate: 25.0,
  expedite_fee: 15.0,
  stockout_churn_factor: 0.15,
  replacement_cost: 30000.0,
  overtime_wage_rate: 45.0,
  cogs_ratio: 0.60,
  crs_w_supply: 0.40,
  crs_w_workforce: 0.40,
  crs_w_demand: 0.20,
  tau_risk: 50.0,
};

export const NAVIGATION_ITEMS = [
  {
    group: "OVERVIEW",
    items: [
      { name: "Dashboard", href: "/", icon: "LayoutDashboard" },
    ],
  },
  {
    group: "DECISIONS",
    items: [
      { name: "Scenarios", href: "/scenarios", icon: "Sliders" },
      { name: "Simulate", href: "/simulate", icon: "PlayCircle" },
    ],
  },
  {
    group: "ANALYSIS",
    items: [
      { name: "Simulation Runs", href: "/simulations", icon: "History" },
      { name: "Sensitivity Lab", href: "/sensitivity", icon: "FlaskConical" },
    ],
  },
  {
    group: "GOVERNANCE",
    items: [
      { name: "Policies", href: "/policies", icon: "ShieldCheck" },
      { name: "Audit & Provenance", href: "/audit", icon: "FileText" },
    ],
  },
  {
    group: "SYSTEM",
    items: [
      { name: "Model Integrity", href: "/system/models", icon: "Fingerprint" },
      { name: "System Health", href: "/system/health", icon: "Activity" },
    ],
  },
] as const;
