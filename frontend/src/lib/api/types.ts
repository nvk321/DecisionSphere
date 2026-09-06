/**
 * Strongly Typed DTOs matching FastAPI Phase 9 Pydantic v2 Schemas.
 */

import { EpistemicTier } from "../constants";

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page?: number;
  page_size?: number;
  total_pages?: number;
  skip?: number;
  limit?: number;
}

export interface ScenarioLevers {
  demand_growth_pct: number;
  promo_active: boolean;
  scheduled_days_offset: number;
  shipping_mode_override: string | null;
  overtime_workforce_pct: number;
  salary_hike_override: number | null;
  epistemic_tier?: "ASSUMED";
}

export interface ScenarioCreate {
  name: string;
  description?: string | null;
  initial_levers?: ScenarioLevers | null;
}

export interface ScenarioUpdate {
  name?: string | null;
  description?: string | null;
  new_levers?: ScenarioLevers | null;
  levers?: ScenarioLevers | null;
}

export interface ScenarioVersion {
  id: string;
  scenario_id: string;
  version_number: number;
  demand_growth_pct: number;
  promo_active: boolean;
  scheduled_days_offset: number;
  shipping_mode_override: string | null;
  overtime_workforce_pct: number;
  salary_hike_override: number | null;
  unit_price: number;
  created_at: string;
  is_active: boolean;
  levers?: ScenarioLevers;
}

export interface Scenario {
  id: string;
  name: string;
  description?: string | null;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  versions: ScenarioVersion[];
  latest_version?: ScenarioVersion | null;
}

export interface DomainPrediction {
  id: string;
  domain: "DEMAND" | "SUPPLY_CHAIN" | "WORKFORCE" | string;
  metric_name: string;
  baseline_value: number;
  scenario_value: number;
  delta_value: number;
  epistemic_tier: EpistemicTier | string;
}

export interface FinancialLineItem {
  id?: string;
  category: "REVENUE" | "EXPENSE" | "MARGIN" | string;
  line_item_name: string;
  amount: number;
  epistemic_tier: EpistemicTier | string;
}

export interface FinancialResult {
  id: string;
  gross_revenue_delta: number;
  realized_revenue_delta: number;
  cogs_delta: number;
  gross_margin_delta: number;
  supply_chain_cost_delta: number;
  workforce_cost_delta: number;
  total_cost_delta: number;
  net_profit_delta: number;
  epistemic_tier: EpistemicTier | string;
  line_items: FinancialLineItem[];
}

export interface StrategicAction {
  id?: string;
  action_id: string;
  domain: string;
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | string;
  title: string;
  description: string;
  trigger_rule_id: string;
  expected_trade_off: string;
  epistemic_tier: EpistemicTier | string;
}

export interface Recommendation {
  id: string;
  decision_category: "PROCEED" | "PROCEED_WITH_MITIGATIONS" | "REJECT_RESTRUCTURE" | string;
  composite_risk_score: number;
  risk_level: "LOW" | "MODERATE" | "HIGH" | "SEVERE" | string;
  supply_chain_strain: number;
  workforce_strain: number;
  demand_strain: number;
  primary_vulnerability?: string | null;
  executive_briefing: string;
  epistemic_tier: EpistemicTier | string;
  strategic_actions: StrategicAction[];
}

export interface AuditRecord {
  id: string;
  simulation_run_id?: string;
  provenance_tuple: {
    scenario_version_id: string;
    artifact_hashes: Record<string, string>;
    policy_id: string;
    policy_version: number;
    git_commit: string;
    app_version: string;
    python_version: string;
    migration_revision: string;
    timestamp: string;
    [key: string]: unknown;
  };
  created_at: string;
  git_commit_hash?: string;
  model_hashes?: Record<string, string>;
  timestamp_utc?: string;
}

export interface SimulationRunSummary {
  id: string;
  scenario_version_id: string;
  policy_id: string;
  execution_status: string;
  execution_duration_ms?: number | null;
  executed_at: string;
  decision_category?: string | null;
  composite_risk_score?: number | null;
  net_profit_delta?: number | null;
  status?: string;
  duration_ms?: number | null;
  created_at?: string;
}

export interface SimulationDetail {
  id: string;
  scenario_version_id: string;
  policy_id: string;
  execution_status: string;
  execution_duration_ms?: number | null;
  executed_at: string;
  domain_predictions: DomainPrediction[];
  financial_result?: FinancialResult | null;
  recommendation_result?: Recommendation | null;
  audit_record?: AuditRecord | null;
  status?: string;
  duration_ms?: number | null;
  created_at?: string;
  predictions?: DomainPrediction[];
}

export interface SimulationRequest {
  scenario_version_id?: string | null;
  policy_id?: string | null;
  override_levers?: ScenarioLevers | null;
}

export interface AssumptionPolicy {
  id: string;
  name: string;
  version_number: number;
  description?: string | null;
  late_penalty_rate: number;
  expedite_fee: number;
  stockout_churn_factor: number;
  replacement_cost: number;
  overtime_wage_rate: number;
  order_scaling_factor: number;
  planning_cycle_days: number;
  crs_w_supply: number;
  crs_w_workforce: number;
  crs_w_demand: number;
  tau_risk: number;
  cogs_ratio: number;
  created_at: string;
  is_active: boolean;
}

export interface PolicyCreate {
  name: string;
  description?: string | null;
  late_penalty_rate?: number;
  expedite_fee?: number;
  stockout_churn_factor?: number;
  replacement_cost?: number;
  overtime_wage_rate?: number;
  cogs_ratio?: number;
  order_scaling_factor?: number;
  planning_cycle_days?: number;
  crs_w_supply: number;
  crs_w_workforce: number;
  crs_w_demand: number;
  tau_risk?: number;
}

export interface DemandShockSweepItem {
  shock_pct: number;
  demand_forecast: number;
  late_delivery_risk: number;
  workforce_attrition_risk: number;
  epistemic_tier: string;
}

export interface DemandShockSweepRequest {
  base_levers?: ScenarioLevers | null;
  shock_percentages?: number[] | null;
}

export interface FinancialSweepItem {
  parameter_name: string;
  value: number;
  net_profit_delta: number;
  is_profitable: boolean;
  epistemic_tier: string;
}

export interface FinancialSweepRequest {
  scenario_version_id?: string | null;
  policy_id?: string | null;
  parameter_name: string;
  candidate_values: number[];
}

export interface CRSWeightsDTO {
  w_supply: number;
  w_workforce: number;
  w_demand: number;
}

export interface CRSWeightSweepItem {
  w_supply: number;
  w_workforce: number;
  w_demand: number;
  composite_risk_score: number;
  risk_level: string;
  decision_category: string;
  epistemic_tier: string;
}

export interface CRSWeightSweepRequest {
  scenario_version_id?: string | null;
  policy_id?: string | null;
  candidate_weights: CRSWeightsDTO[];
  tau_risk?: number;
}

export interface FlipThresholdSearchRequest {
  scenario_version_id?: string | null;
  policy_id?: string | null;
  parameter_name: string;
  candidate_values: number[];
}

export interface FlipThresholdResponse {
  parameter_name: string;
  flip_detected: boolean;
  flip_value?: number | null;
  previous_category?: string | null;
  new_category?: string | null;
  net_profit_delta?: number | null;
  composite_risk_score?: number | null;
  epistemic_tier: string;
}

export interface ModelArtifactStatus {
  name: string;
  path: string;
  exists: boolean;
  verified: boolean;
  expected_sha256: string;
  actual_sha256?: string | null;
  status: "VERIFIED" | "HASH_MISMATCH" | "FILE_NOT_FOUND" | string;
}

export interface ModelStatusResponse {
  status: string;
  models: Record<string, ModelArtifactStatus>;
  all_verified: boolean;
  models_verified?: boolean | null;
}

export interface HealthResponse {
  status: "healthy" | "degraded" | string;
  app_name: string;
  version: string;
  database: "connected" | "disconnected" | string;
  models_verified: boolean;
  models?: Record<string, unknown> | null;
  environment?: string;
}
