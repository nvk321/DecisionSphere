"""
DecisionSphere — Phase 8 Recommendation Rules Engine
Defines the deterministic condition-action trigger matrix and priority sorting algorithms.

Epistemic Tier: RECOMMENDED (Tier 6)
Governing Mandate:
"Strategic recommendations are triggered by explicit deterministic threshold rules;
they do not represent ungrounded LLM hallucinations or guaranteed causal interventions."
"""

from typing import List, Optional, Dict, Any, Callable
from src.scenario.schema import ScenarioRunResult
from src.business.schema import BusinessImpactResult
from src.recommendation.schema import (
    StrategicAction,
    RecommendationSeverity,
    CompositeRiskBreakdown,
)


SEVERITY_ORDER: Dict[RecommendationSeverity, int] = {
    RecommendationSeverity.CRITICAL: 0,
    RecommendationSeverity.HIGH: 1,
    RecommendationSeverity.MEDIUM: 2,
    RecommendationSeverity.LOW: 3,
}


class RuleEvaluator:
    """
    Evaluates the 7 frozen deterministic trigger rules against ScenarioRunResult,
    BusinessImpactResult, and CompositeRiskBreakdown.
    """

    @staticmethod
    def evaluate_all(
        scenario_run: ScenarioRunResult,
        business_impact: BusinessImpactResult,
        crs: CompositeRiskBreakdown,
    ) -> List[StrategicAction]:
        """
        Evaluates all rules deterministically and returns sorted strategic actions.

        Parameters
        ----------
        scenario_run : ScenarioRunResult
            Immutable operational scenario run result.
        business_impact : BusinessImpactResult
            Immutable financial accounting result.
        crs : CompositeRiskBreakdown
            Computed operational risk breakdown.

        Returns
        -------
        List[StrategicAction]
            Prioritized strategic actions sorted by severity, then exposure magnitude.
        """
        actions: List[StrategicAction] = []

        # Operational metrics extraction
        p_late_scen = float(scenario_run.supply_chain_result.scenario_value)
        delta_p_late = float(scenario_run.supply_chain_result.delta_value)
        shipping_mode = scenario_run.levers.shipping_mode_override
        scheduled_offset = int(scenario_run.levers.scheduled_days_offset)

        p_att_scen = float(scenario_run.workforce_result.scenario_value)
        ot_pct_scen = float(scenario_run.workforce_cohort_summary.actual_scenario_overtime_percentage)
        salary_hike = scenario_run.levers.salary_hike_override

        # Financial metrics extraction
        gross_scen = float(business_impact.gross_revenue.scenario_value)
        realized_scen = float(business_impact.realized_revenue.scenario_value)
        l_fulfillment_scen = (
            max(0.0, 1.0 - (realized_scen / gross_scen)) if gross_scen > 0.0 else (p_late_scen * 0.15)
        )
        delta_realized_rev = float(business_impact.realized_revenue.delta_value)
        delta_profit = float(business_impact.net_profit_delta)
        delta_supply_cost = float(business_impact.supply_chain_cost.delta_value)
        delta_wf_cost = float(business_impact.workforce_cost.delta_value)

        # ---------------------------------------------------------------------
        # RULE-01: Expedited Freight Air Surcharge Trigger
        # ---------------------------------------------------------------------
        # Condition: late probability >= 0.65 OR (delta late probability >= 0.15 AND shipping mode != 'First Class')
        r1_cond_1 = p_late_scen >= 0.65
        r1_cond_2 = (delta_p_late >= 0.15) and (shipping_mode != "First Class")
        if r1_cond_1 or r1_cond_2:
            actions.append(StrategicAction(
                action_id="ACT-SC-001",
                domain="Supply Chain",
                severity=RecommendationSeverity.HIGH,
                title="Transition High-Priority Shipments to Expedited Freight",
                description=(
                    "Transition high-priority order volume from Standard Class to First Class air freight "
                    "to bypass ground logistical bottlenecks and compress in-transit delays."
                ),
                trigger_rule_id="RULE-01",
                triggering_condition=(
                    f"P(Late)={p_late_scen:.2f} >= 0.65 OR (Delta P(Late)={delta_p_late:+.2f} >= 0.15 "
                    f"AND ShippingMode='{shipping_mode}' != 'First Class')"
                ),
                grounding_evidence={
                    "p_late_scenario": p_late_scen,
                    "delta_p_late": delta_p_late,
                    "shipping_mode_override": shipping_mode,
                    "supply_chain_cost_delta_usd": delta_supply_cost,
                },
                expected_trade_off=(
                    "Suppresses late-delivery risk and customer stockout cancellations but incurs contractual "
                    "expedited freight surcharges ($15.00/order)."
                ),
                epistemic_tier="RECOMMENDED",
            ))

        # ---------------------------------------------------------------------
        # RULE-02: Safety Stock Reorder Buffer Trigger
        # ---------------------------------------------------------------------
        # Condition: fulfillment loss >= 0.10 (10% churn)
        if l_fulfillment_scen >= 0.10:
            actions.append(StrategicAction(
                action_id="ACT-SC-002",
                domain="Supply Chain",
                severity=RecommendationSeverity.MEDIUM,
                title="Increase Safety Stock Reorder Thresholds",
                description=(
                    "Increase regional safety stock reorder levels by 15% across primary distribution centers "
                    "at least 10 days prior to scenario launch to absorb fulfillment lag."
                ),
                trigger_rule_id="RULE-02",
                triggering_condition=f"L_fulfillment={l_fulfillment_scen:.3f} >= 0.10",
                grounding_evidence={
                    "fulfillment_loss_rate": l_fulfillment_scen,
                    "realized_revenue_delta_usd": delta_realized_rev,
                },
                expected_trade_off=(
                    "Buffers inventory availability and shields customer retention at the expense of temporary "
                    "warehouse working capital and holding costs."
                ),
                epistemic_tier="RECOMMENDED",
            ))

        # ---------------------------------------------------------------------
        # RULE-03: Mandatory Overtime Cap & Temporary Staffing Trigger
        # ---------------------------------------------------------------------
        # Condition: attrition probability >= 0.21 AND realized overtime >= 30%
        if (p_att_scen >= 0.21) and (ot_pct_scen >= 30.0):
            actions.append(StrategicAction(
                action_id="ACT-WF-001",
                domain="Workforce",
                severity=RecommendationSeverity.HIGH,
                title="Cap Mandatory Overtime & Authorize Contract Staffing",
                description=(
                    "Cap mandatory overtime at 20% headcount; authorize emergency temporary contract staffing "
                    "to prevent critical employee burnout and turnover in high-stress roles."
                ),
                trigger_rule_id="RULE-03",
                triggering_condition=(
                    f"P(Attrition)={p_att_scen:.2f} >= 0.21 (tau*) AND OvertimeCohortPct={ot_pct_scen:.1f}% >= 30.0%"
                ),
                grounding_evidence={
                    "p_attrition_scenario": p_att_scen,
                    "actual_overtime_percentage": ot_pct_scen,
                    "workforce_cost_delta_usd": delta_wf_cost,
                },
                expected_trade_off=(
                    "Reduces employee burnout and prevents costly replacement drag ($30,000/departure) "
                    "via short-term contract staffing expenses."
                ),
                epistemic_tier="RECOMMENDED",
            ))

        # ---------------------------------------------------------------------
        # RULE-04: Margin Erosion Warning (Top Priority Alert)
        # ---------------------------------------------------------------------
        # Condition: incremental realized revenue > 0 AND incremental profit < 0
        if (delta_realized_rev > 0.0) and (delta_profit < 0.0):
            actions.append(StrategicAction(
                action_id="ACT-FIN-001",
                domain="Financial / Strategic",
                severity=RecommendationSeverity.CRITICAL,
                title="Margin Erosion Warning: Rescale Promotional Intensity",
                description=(
                    "Margin Erosion Warning: Incremental sales revenue is fully consumed by logistical SLA penalties, "
                    "expedited freight, and overtime expenses. Rescale promotional discount or secure delivery capacity."
                ),
                trigger_rule_id="RULE-04",
                triggering_condition=(
                    f"DeltaRealizedRevenue={delta_realized_rev:+,.2f} > 0.0 AND DeltaProfit={delta_profit:+,.2f} < 0.0"
                ),
                grounding_evidence={
                    "delta_realized_revenue_usd": delta_realized_rev,
                    "delta_profit_usd": delta_profit,
                    "total_operational_cost_delta_usd": float(business_impact.total_operational_cost.delta_value),
                },
                expected_trade_off=(
                    "Sacrifices unconstrained top-line revenue expansion in order to protect bottom-line operating margin "
                    "and avoid value destruction."
                ),
                epistemic_tier="RECOMMENDED",
            ))

        # ---------------------------------------------------------------------
        # RULE-05: Targeted Retention Compensation Adjustment
        # ---------------------------------------------------------------------
        # Condition: attrition probability >= 0.25 AND salary_hike_override is None (or <= 0.0)
        if (p_att_scen >= 0.25) and (salary_hike is None or salary_hike <= 0.0):
            actions.append(StrategicAction(
                action_id="ACT-WF-002",
                domain="Workforce",
                severity=RecommendationSeverity.MEDIUM,
                title="Implement Targeted Retention Salary Adjustment",
                description=(
                    "Implement a targeted retention adjustment (5% to 10%) for high-burnout cohorts to offset "
                    "overtime-induced attrition pressure during peak planning cycles."
                ),
                trigger_rule_id="RULE-05",
                triggering_condition=(
                    f"P(Attrition)={p_att_scen:.2f} >= 0.25 AND SalaryHikeOverride={salary_hike}"
                ),
                grounding_evidence={
                    "p_attrition_scenario": p_att_scen,
                    "salary_hike_override": salary_hike,
                    "replacement_cost_asm_004": 30000.00,
                },
                expected_trade_off=(
                    "Increases baseline payroll expense to avoid institutional knowledge loss and high onboarding costs."
                ),
                epistemic_tier="RECOMMENDED",
            ))

        # ---------------------------------------------------------------------
        # RULE-06: Operational Strain Warning (High CRS Proceed)
        # ---------------------------------------------------------------------
        # Condition: incremental profit > 0 AND CRS >= 60.0
        if (delta_profit > 0.0) and (crs.composite_risk_score >= 60.0):
            actions.append(StrategicAction(
                action_id="ACT-GOV-001",
                domain="Executive Governance",
                severity=RecommendationSeverity.HIGH,
                title="Operational Strain Warning: Mandate Execution Buffers",
                description=(
                    "Operational Strain Warning: Scenario is financially profitable but operates near organizational "
                    "failure limits (CRS >= 60.0). Mandate logistics and staffing buffer verification prior to launch."
                ),
                trigger_rule_id="RULE-06",
                triggering_condition=(
                    f"DeltaProfit={delta_profit:+,.2f} > 0.0 AND CRS={crs.composite_risk_score:.1f} >= 60.0"
                ),
                grounding_evidence={
                    "composite_risk_score": crs.composite_risk_score,
                    "delta_profit_usd": delta_profit,
                    "risk_level": crs.risk_level,
                },
                expected_trade_off=(
                    "Conditions commercial execution on operational risk mitigation sign-off to prevent hidden delivery failure."
                ),
                epistemic_tier="RECOMMENDED",
            ))

        # ---------------------------------------------------------------------
        # RULE-07: Relax Compressed Dispatch SLA Offset
        # ---------------------------------------------------------------------
        # Condition: scheduled_days_offset <= -2 AND late probability >= 0.55
        if (scheduled_offset <= -2) and (p_late_scen >= 0.55):
            actions.append(StrategicAction(
                action_id="ACT-SC-003",
                domain="Supply Chain",
                severity=RecommendationSeverity.MEDIUM,
                title="Relax Compressed Dispatch Lead Times",
                description=(
                    "Relax dispatch SLA back by +1 to +2 days to restore fulfillment reliability without "
                    "sacrificing promotional customer capture."
                ),
                trigger_rule_id="RULE-07",
                triggering_condition=(
                    f"ScheduledDaysOffset={scheduled_offset} <= -2 AND P(Late)={p_late_scen:.2f} >= 0.55"
                ),
                grounding_evidence={
                    "scheduled_days_offset": scheduled_offset,
                    "p_late_scenario": p_late_scen,
                },
                expected_trade_off=(
                    "Extends published customer delivery window slightly to avoid severe carrier delay SLA penalties."
                ),
                epistemic_tier="RECOMMENDED",
            ))

        # ---------------------------------------------------------------------
        # DETERMINISTIC PRIORITY SORTING
        # ---------------------------------------------------------------------
        # Primary: Severity (CRITICAL=0, HIGH=1, MEDIUM=2, LOW=3)
        # Secondary: Exposure magnitude descending (max of cost deltas / profit delta)
        # Tertiary: Action ID ascending (for stable tie-breaking)
        exposure_mag = max(abs(delta_supply_cost), abs(delta_wf_cost), abs(delta_profit))

        def sort_key(action: StrategicAction):
            return (
                SEVERITY_ORDER.get(action.severity, 99),
                -exposure_mag,
                action.action_id,
            )

        actions.sort(key=sort_key)
        return actions
