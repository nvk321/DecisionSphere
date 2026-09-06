"""
DecisionSphere — Phase 8 Recommendation & Strategic Trade-Off Analysis Engine
Orchestrates Composite Risk Evaluation, deterministic rule triggering, and lexicographic trade-off synthesis.

Epistemic Tier: RECOMMENDED (Tier 6)
Governing Mandate:
"The Recommendation Engine synthesizes multi-domain analytical outputs into actionable,
non-causal strategic decisions; it enforces strict epistemic separation and preserves
underlying result immutability."
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from src.scenario.schema import ScenarioRunResult
from src.business.schema import BusinessImpactResult, BusinessAssumptions
from src.business.engine import BusinessImpactEngine
from src.recommendation.schema import (
    CRSWeights,
    StrategicDecisionCategory,
    RecommendationSeverity,
    StrategicAction,
    TradeOffEvaluation,
    RecommendationResult,
)
from src.recommendation.crs import CompositeRiskEngine
from src.recommendation.rules import RuleEvaluator


class RecommendationEngine:
    """
    Central strategic orchestrator synthesizing operational simulations (Phase 6) and
    deterministic financial calculations (Phase 7) into prioritized, actionable interventions.
    """

    def __init__(
        self,
        crs_engine: Optional[CompositeRiskEngine] = None,
        operational_strain_threshold: float = 50.0,
    ):
        self.crs_engine = crs_engine or CompositeRiskEngine()
        self.operational_strain_threshold = operational_strain_threshold

    def evaluate(
        self,
        scenario_run: ScenarioRunResult,
        business_impact: BusinessImpactResult,
        weights: Optional[CRSWeights] = None,
        operational_strain_threshold: Optional[float] = None,
    ) -> RecommendationResult:
        """
        Synthesizes recommendations, evaluates CRS, and categorizes scenario trade-offs.

        Parameters
        ----------
        scenario_run : ScenarioRunResult
            Immutable operational multi-domain simulation output.
        business_impact : BusinessImpactResult
            Immutable financial accounting output.
        weights : Optional[CRSWeights]
            Custom or default CRS domain weights (ASM-009).
        operational_strain_threshold : Optional[float]
            Operational risk tolerance limit tau_risk (ASM-010). Defaults to 50.0.

        Returns
        -------
        RecommendationResult
            Complete strategic decision classification, CRS breakdown, and prioritized actions.
        """
        if not isinstance(scenario_run, ScenarioRunResult):
            raise TypeError(f"Expected ScenarioRunResult, got {type(scenario_run).__name__}")
        if not isinstance(business_impact, BusinessImpactResult):
            raise TypeError(f"Expected BusinessImpactResult, got {type(business_impact).__name__}")

        tau_risk = (
            operational_strain_threshold
            if operational_strain_threshold is not None
            else self.operational_strain_threshold
        )

        # ---------------------------------------------------------------------
        # 1. EVALUATE COMPOSITE RISK SCORE (CRS)
        # ---------------------------------------------------------------------
        crs_breakdown = self.crs_engine.evaluate(
            scenario_run=scenario_run,
            business_impact=business_impact,
            weights=weights,
        )

        # ---------------------------------------------------------------------
        # 2. TRIGGER AND PRIORITIZE STRATEGIC ACTIONS
        # ---------------------------------------------------------------------
        actions = RuleEvaluator.evaluate_all(
            scenario_run=scenario_run,
            business_impact=business_impact,
            crs=crs_breakdown,
        )

        # ---------------------------------------------------------------------
        # 3. LEXICOGRAPHIC STRATEGIC DECISION CATEGORIZATION
        # ---------------------------------------------------------------------
        # Step 1: Bottom-Line Financial Feasibility Gate
        delta_profit = float(business_impact.net_profit_delta)
        crs_value = float(crs_breakdown.composite_risk_score)

        if delta_profit <= 0.0:
            category = StrategicDecisionCategory.REJECT_RESTRUCTURE
            rationale = (
                f"Projected scenario results in negative net incremental operating profit "
                f"(${delta_profit:+,.2f} USD). Commercial execution under current cost structures "
                f"will result in margin erosion and value destruction."
            )
        elif crs_value <= tau_risk:
            category = StrategicDecisionCategory.PROCEED
            rationale = (
                f"Scenario achieves accretive net operating margin (${delta_profit:+,.2f} USD) "
                f"while maintaining operational strain within safe organizational buffers "
                f"(CRS {crs_value:.1f} <= {tau_risk:.1f})."
            )
        else:
            category = StrategicDecisionCategory.PROCEED_WITH_MITIGATIONS
            rationale = (
                f"Scenario generates positive incremental profit (${delta_profit:+,.2f} USD), "
                f"but operational strain exceeds risk tolerance limits (CRS {crs_value:.1f} > {tau_risk:.1f}). "
                f"Commercial rollout must be conditioned on deploying prioritized operational mitigations."
            )

        # ---------------------------------------------------------------------
        # 4. PRIMARY VULNERABILITY & COMPETING PRIORITIES IDENTIFICATION
        # ---------------------------------------------------------------------
        sub_scores = {
            "Supply Chain Logistics Delay": crs_breakdown.supply_chain_risk_score,
            "Workforce Burnout & Overtime": crs_breakdown.workforce_risk_score,
            "Demand Surge & Fulfillment Stockout": crs_breakdown.demand_execution_risk_score,
        }
        primary_vulnerability = max(sub_scores, key=sub_scores.get)

        competing_priorities = [
            "Top-line sales expansion vs Logistical delivery penalty exposure",
            "SLA lead-time compression vs Workforce overtime and burnout fatigue",
            "Short-term promotional capture vs Long-term employee turnover drag",
        ]

        trade_off = TradeOffEvaluation(
            decision_category=category,
            net_profit_delta_usd=delta_profit,
            composite_risk_score=crs_value,
            decision_rationale=rationale,
            primary_vulnerability=primary_vulnerability,
            competing_priorities=competing_priorities,
        )

        # ---------------------------------------------------------------------
        # 5. EPISTEMIC NON-CAUSAL EXECUTIVE BRIEFING
        # ---------------------------------------------------------------------
        timestamp_str = datetime.now(timezone.utc).isoformat()
        action_count = len(actions)
        critical_count = sum(1 for a in actions if a.severity == RecommendationSeverity.CRITICAL)

        briefing = (
            f"Under the declared scenario levers and empirical predictive baselines, the scenario indicates a "
            f"net profit shift of ${delta_profit:+,.2f} USD paired with an operational Composite Risk Score of "
            f"{crs_value:.1f}/100 ({crs_breakdown.risk_level} RISK). Strategic Decision: [{category.value}]. "
            f"The primary operational vulnerability is {primary_vulnerability}. "
            f"Based on deterministic policy rules, the system recommends {action_count} strategic intervention(s) "
            f"({critical_count} critical). This synthesis is rule-grounded and non-causal; it does not constitute "
            f"a guarantee of future operating performance."
        )

        return RecommendationResult(
            scenario_id=scenario_run.scenario_id,
            scenario_name=scenario_run.scenario_name,
            decision_category=category,
            composite_risk=crs_breakdown,
            trade_off_evaluation=trade_off,
            recommended_actions=actions,
            executive_briefing=briefing,
            timestamp=timestamp_str,
            epistemic_tier="RECOMMENDED",
        )

    # =========================================================================
    # EXPERIMENT D: SENSITIVITY & ROBUSTNESS ANALYSIS TOOLS
    # =========================================================================

    def sweep_crs_weights(
        self,
        scenario_run: ScenarioRunResult,
        business_impact: BusinessImpactResult,
        weight_configurations: List[CRSWeights],
    ) -> List[Dict[str, Any]]:
        """
        Sweeps CRS domain weights across the simplex to test recommendation category stability (Experiment D).

        Parameters
        ----------
        scenario_run : ScenarioRunResult
            Immutable scenario run result.
        business_impact : BusinessImpactResult
            Immutable financial result.
        weight_configurations : List[CRSWeights]
            List of valid simplex weight configurations to evaluate.

        Returns
        -------
        List[Dict[str, Any]]
            Sequential evaluation records containing CRS and decision categories.
        """
        results: List[Dict[str, Any]] = []
        for w in weight_configurations:
            res = self.evaluate(scenario_run, business_impact, weights=w)
            results.append({
                "w_supply": w.w_supply,
                "w_workforce": w.w_workforce,
                "w_demand": w.w_demand,
                "composite_risk_score": res.composite_risk.composite_risk_score,
                "risk_level": res.composite_risk.risk_level,
                "decision_category": res.decision_category.value,
            })
        return results

    def find_recommendation_flip_threshold(
        self,
        scenario_run: ScenarioRunResult,
        base_assumptions: BusinessAssumptions,
        parameter_name: str,
        candidate_values: List[float],
        impact_engine: Optional[BusinessImpactEngine] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Identifies parameter tipping points where the strategic decision category flips
        (e.g., from PROCEED to REJECT_RESTRUCTURE) without mutating inputs (Experiment D).
        """
        engine = impact_engine or BusinessImpactEngine()
        base_dict = base_assumptions.model_dump()

        previous_category = None
        for val in sorted(candidate_values):
            modified_dict = dict(base_dict)
            modified_dict[parameter_name] = float(val)
            assumptions = BusinessAssumptions(**modified_dict)

            impact_res = engine.evaluate(scenario_run, assumptions=assumptions)
            rec_res = self.evaluate(scenario_run, impact_res)

            curr_category = rec_res.decision_category.value
            if previous_category is not None and curr_category != previous_category:
                return {
                    "parameter_name": parameter_name,
                    "flip_value": float(val),
                    "previous_category": previous_category,
                    "new_category": curr_category,
                    "net_profit_delta": impact_res.net_profit_delta,
                    "composite_risk_score": rec_res.composite_risk.composite_risk_score,
                }
            previous_category = curr_category

        return None
