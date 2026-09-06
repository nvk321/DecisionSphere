"""
DecisionSphere — Phase 8 Composite Risk Score (CRS) Engine
Evaluates deterministic, multi-criteria operational strain indices across logistics, workforce,
and demand fulfillment execution dimensions (ASM-009).

Epistemic Tier: CALCULATED (Tier 5)
Governing Mandate:
"The Composite Risk Score is an operational multi-criteria index measuring aggregate execution strain;
it does not measure dollar loss or make causal claims."
"""

from typing import Optional, Dict, Any
from src.scenario.schema import ScenarioRunResult
from src.business.schema import BusinessImpactResult
from src.recommendation.schema import CRSWeights, CompositeRiskBreakdown


def _clamp(val: float, min_val: float, max_val: float) -> float:
    """Clamps a floating point value to the closed interval [min_val, max_val]."""
    return max(min_val, min(max_val, val))


class CompositeRiskEngine:
    """
    Computes normalized domain operational risk sub-indices and the aggregate Composite Risk Score (CRS).
    Guarantees pure operational focus (zero financial inclusion) and continuous IEEE-754 precision.
    """

    def __init__(self, default_weights: Optional[CRSWeights] = None):
        self.default_weights = default_weights or CRSWeights()

    def evaluate(
        self,
        scenario_run: ScenarioRunResult,
        business_impact: Optional[BusinessImpactResult] = None,
        weights: Optional[CRSWeights] = None,
    ) -> CompositeRiskBreakdown:
        """
        Calculates sub-indices and aggregate Composite Risk Score from ScenarioRunResult and BusinessImpactResult.

        Parameters
        ----------
        scenario_run : ScenarioRunResult
            Immutable multi-domain operational scenario run result from Phase 6.
        business_impact : Optional[BusinessImpactResult]
            Immutable financial business impact result from Phase 7.
        weights : Optional[CRSWeights]
            Custom or baseline domain weights (ASM-009). If None, uses default weights (0.40, 0.40, 0.20).

        Returns
        -------
        CompositeRiskBreakdown
            Complete sub-index breakdown, aggregate CRS, and categorical risk level.
        """
        if not isinstance(scenario_run, ScenarioRunResult):
            raise TypeError(f"Expected ScenarioRunResult, got {type(scenario_run).__name__}")

        w = weights or self.default_weights
        if not isinstance(w, CRSWeights):
            raise TypeError(f"Expected CRSWeights, got {type(w).__name__}")

        # ---------------------------------------------------------------------
        # 1. SUPPLY CHAIN DELIVERY RISK SUB-INDEX (S_supply in [0, 100])
        # ---------------------------------------------------------------------
        # Evaluates absolute late probability (weight 0.70) and positive shift (weight 0.30)
        p_late_scen = float(scenario_run.supply_chain_result.scenario_value)
        delta_p_late = float(scenario_run.supply_chain_result.delta_value)

        # Shift saturated at delta = +0.30
        norm_delta_late = _clamp(delta_p_late / 0.30, 0.0, 1.0)
        s_supply = 100.0 * (0.70 * _clamp(p_late_scen, 0.0, 1.0) + 0.30 * norm_delta_late)
        s_supply = _clamp(s_supply, 0.0, 100.0)

        # ---------------------------------------------------------------------
        # 2. WORKFORCE BURNOUT & ATTRITION SUB-INDEX (S_workforce in [0, 100])
        # ---------------------------------------------------------------------
        # Evaluates absolute attrition probability (weight 0.60) and overtime ratio (weight 0.40)
        p_att_scen = float(scenario_run.workforce_result.scenario_value)
        ot_pct_scen = float(scenario_run.workforce_cohort_summary.actual_scenario_overtime_percentage)

        # Attrition saturated at 40% (severe benchmark)
        norm_attrition = _clamp(p_att_scen / 0.40, 0.0, 1.0)
        norm_overtime = _clamp(ot_pct_scen / 100.0, 0.0, 1.0)
        s_workforce = 100.0 * (0.60 * norm_attrition + 0.40 * norm_overtime)
        s_workforce = _clamp(s_workforce, 0.0, 100.0)

        # ---------------------------------------------------------------------
        # 3. DEMAND & FULFILLMENT EXECUTION SUB-INDEX (S_demand in [0, 100])
        # ---------------------------------------------------------------------
        # Evaluates promotional shock magnitude (weight 0.50) and fulfillment loss rate (weight 0.50)
        demand_growth_pct = float(scenario_run.levers.demand_growth_pct)
        norm_demand_shock = _clamp(max(0.0, demand_growth_pct) / 50.0, 0.0, 1.0)

        # Fulfillment loss rate from BusinessImpactResult or direct formula
        if business_impact is not None and business_impact.gross_revenue.scenario_value > 0.0:
            gross_scen = float(business_impact.gross_revenue.scenario_value)
            realized_scen = float(business_impact.realized_revenue.scenario_value)
            l_fulfillment = max(0.0, 1.0 - (realized_scen / gross_scen))
        else:
            # Fallback based on late probability and baseline cancellation factor 0.15
            l_fulfillment = min(1.0, p_late_scen * 0.15)

        # Saturated at 20% cancellation churn
        norm_fulfillment_loss = _clamp(l_fulfillment / 0.20, 0.0, 1.0)
        s_demand = 100.0 * (0.50 * norm_demand_shock + 0.50 * norm_fulfillment_loss)
        s_demand = _clamp(s_demand, 0.0, 100.0)

        # ---------------------------------------------------------------------
        # 4. AGGREGATE COMPOSITE RISK SCORE (CRS in [0, 100])
        # ---------------------------------------------------------------------
        crs = (w.w_supply * s_supply) + (w.w_workforce * s_workforce) + (w.w_demand * s_demand)
        crs = _clamp(crs, 0.0, 100.0)

        # Categorical risk level classification
        if crs < 30.0:
            risk_level = "LOW"
        elif crs < 50.0:
            risk_level = "MODERATE"
        elif crs < 75.0:
            risk_level = "HIGH"
        else:
            risk_level = "SEVERE"

        return CompositeRiskBreakdown(
            supply_chain_risk_score=s_supply,
            workforce_risk_score=s_workforce,
            demand_execution_risk_score=s_demand,
            composite_risk_score=crs,
            risk_level=risk_level,
            weights_applied={
                "w_supply": w.w_supply,
                "w_workforce": w.w_workforce,
                "w_demand": w.w_demand,
            },
            epistemic_tier="CALCULATED",
        )
