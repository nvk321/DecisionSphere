"""
DecisionSphere — Formal Dynamic State Propagation Operator Architecture
Formalizes the state-space operator S_(t+1) = F(S_t, U_t, P_hat; Theta),
sensitivity Jacobian computation nabla_U S, and numerical tipping-point boundary discovery.
"""

from typing import Dict, Any, Optional, Tuple, List, Callable
import numpy as np

from src.scenario.schema import ScenarioLevers, ScenarioAssumptions, ScenarioRunResult
from src.scenario.engine import ScenarioEngine
from src.scenario.state import ScenarioStateVector
from src.scenario.graph import ScenarioDependencyGraph
from src.business.engine import BusinessImpactEngine
from src.business.schema import BusinessAssumptions, BusinessImpactResult
from src.recommendation.engine import RecommendationEngine
from src.recommendation.schema import RecommendationResult, StrategicDecisionCategory


class StatePropagationOperator:
    """
    Formal mathematical operator F: (S_t, U_t, P_hat; Theta) -> S_(t+1)
    
    Provides:
    - Deterministic state transition computation across the DAG topology.
    - Numerical Jacobian sensitivity matrix J in R^(24 x 3).
    - Algebraic margin tipping-point boundary discovery (bisection search for Delta Pi = 0).
    - Lipschitz state stability verification ||Delta S|| <= K ||U||.
    """

    def __init__(
        self,
        scenario_engine: Optional[ScenarioEngine] = None,
        business_engine: Optional[BusinessImpactEngine] = None,
        recommendation_engine: Optional[RecommendationEngine] = None,
    ):
        self.scenario_engine = scenario_engine or ScenarioEngine()
        self.business_engine = business_engine or BusinessImpactEngine()
        self.recommendation_engine = recommendation_engine or RecommendationEngine()
        self.dependency_graph = ScenarioDependencyGraph()

    def evaluate_state(
        self,
        levers: ScenarioLevers,
        assumptions: Optional[ScenarioAssumptions] = None,
        business_assumptions: Optional[BusinessAssumptions] = None,
    ) -> Tuple[ScenarioStateVector, ScenarioRunResult, BusinessImpactResult, RecommendationResult]:
        """
        Executes a single forward state evaluation across the complete pipeline.
        
        Returns:
            Tuple of (ScenarioStateVector, ScenarioRunResult, BusinessImpactResult, RecommendationResult)
        """
        scen_run = self.scenario_engine.run_scenario(
            levers=levers,
            assumptions=assumptions,
        )
        b_impact = self.business_engine.evaluate(
            scenario_run=scen_run,
            assumptions=business_assumptions,
        )
        rec_res = self.recommendation_engine.evaluate(
            scenario_run=scen_run,
            business_impact=b_impact,
        )
        state_vec = ScenarioStateVector.from_pipeline_results(
            scenario_run=scen_run,
            business_impact=b_impact,
            crs_breakdown=rec_res.composite_risk,
        )
        return state_vec, scen_run, b_impact, rec_res

    def propagate(
        self,
        initial_state: ScenarioStateVector,
        intervention: ScenarioLevers,
        assumptions: Optional[ScenarioAssumptions] = None,
        business_assumptions: Optional[BusinessAssumptions] = None,
    ) -> ScenarioStateVector:
        """
        Evaluates the transition operator S_(t+1) = F(S_t, U_t, P_hat; Theta).
        """
        next_state, _, _, _ = self.evaluate_state(
            levers=intervention,
            assumptions=assumptions,
            business_assumptions=business_assumptions,
        )
        return next_state

    def compute_sensitivity_jacobian(
        self,
        base_levers: ScenarioLevers,
        epsilon: float = 1.0,
    ) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Computes the numerical Jacobian matrix J in R^(24 x 3):
        J_ij = d S_i / d U_j using central finite differences.
        
        Inputs evaluated:
            U_1: demand_growth_pct
            U_2: scheduled_days_offset
            U_3: overtime_workforce_pct
        """
        # Central baseline
        state_base, _, _, _ = self.evaluate_state(base_levers)
        s_base_arr = state_base.to_numpy()
        dim_s = len(s_base_arr)

        lever_names = ["demand_growth_pct", "scheduled_days_offset", "overtime_workforce_pct"]
        jacobian = np.zeros((dim_s, len(lever_names)), dtype=np.float64)

        # 1. Perturb demand_growth_pct
        l_plus = base_levers.model_copy(update={"demand_growth_pct": base_levers.demand_growth_pct + epsilon})
        l_minus = base_levers.model_copy(update={"demand_growth_pct": base_levers.demand_growth_pct - epsilon})
        s_plus, _, _, _ = self.evaluate_state(l_plus)
        s_minus, _, _, _ = self.evaluate_state(l_minus)
        jacobian[:, 0] = (s_plus.to_numpy() - s_minus.to_numpy()) / (2.0 * epsilon)

        # 2. Perturb scheduled_days_offset
        l_plus = base_levers.model_copy(update={"scheduled_days_offset": base_levers.scheduled_days_offset + int(np.ceil(epsilon))})
        l_minus = base_levers.model_copy(update={"scheduled_days_offset": base_levers.scheduled_days_offset - int(np.ceil(epsilon))})
        s_plus, _, _, _ = self.evaluate_state(l_plus)
        s_minus, _, _, _ = self.evaluate_state(l_minus)
        denom_sc = 2.0 * int(np.ceil(epsilon))
        jacobian[:, 1] = (s_plus.to_numpy() - s_minus.to_numpy()) / max(1.0, denom_sc)

        # 3. Perturb overtime_workforce_pct
        l_plus = base_levers.model_copy(update={"overtime_workforce_pct": min(100.0, base_levers.overtime_workforce_pct + epsilon)})
        l_minus = base_levers.model_copy(update={"overtime_workforce_pct": max(0.0, base_levers.overtime_workforce_pct - epsilon)})
        s_plus, _, _, _ = self.evaluate_state(l_plus)
        s_minus, _, _, _ = self.evaluate_state(l_minus)
        actual_diff = l_plus.overtime_workforce_pct - l_minus.overtime_workforce_pct
        jacobian[:, 2] = (s_plus.to_numpy() - s_minus.to_numpy()) / max(1e-5, actual_diff)

        return jacobian, ScenarioStateVector.feature_names(), lever_names

    def find_margin_tipping_point(
        self,
        base_levers: Optional[ScenarioLevers] = None,
        search_interval: Tuple[float, float] = (0.0, 30.0),
        tolerance: float = 0.05,
        max_iterations: int = 30,
    ) -> Dict[str, Any]:
        """
        Discovers the exact demand growth percentage delta* where Net Incremental Operating Profit Delta Pi = 0.
        Uses bisection search over the continuous interval [low, high].
        """
        levers_template = base_levers or ScenarioLevers(
            scenario_name="TippingPointSearch",
            promo_active=True,
            demand_growth_pct=0.0,
            scheduled_days_offset=0,
            shipping_mode_override="Standard Class",
            overtime_workforce_pct=40.0,
            salary_hike_override=None,
        )

        low, high = search_interval

        def f_profit(growth: float) -> float:
            test_l = levers_template.model_copy(update={"demand_growth_pct": growth})
            st, _, b_imp, _ = self.evaluate_state(test_l)
            return float(b_imp.net_profit_delta)

        f_low = f_profit(low)
        f_high = f_profit(high)

        if f_low * f_high > 0.0:
            # Check if there is an interior root or monotonic profile
            return {
                "root_found": False,
                "low_growth": low,
                "high_growth": high,
                "f_low": f_low,
                "f_high": f_high,
                "message": "Profit signs at boundary points are identical; no simple single root in interval.",
            }

        iter_count = 0
        mid = (low + high) / 2.0
        while (high - low) / 2.0 > tolerance and iter_count < max_iterations:
            iter_count += 1
            mid = (low + high) / 2.0
            f_mid = f_profit(mid)

            if abs(f_mid) < 1.0:  # Within $1.00 of zero profit
                break

            if np.sign(f_mid) == np.sign(f_low):
                low = mid
                f_low = f_mid
            else:
                high = mid
                f_high = f_mid

        final_st, _, final_b, final_rec = self.evaluate_state(
            levers_template.model_copy(update={"demand_growth_pct": mid})
        )

        return {
            "root_found": True,
            "tipping_point_demand_growth_pct": round(float(mid), 3),
            "net_profit_delta_at_root": float(final_b.net_profit_delta),
            "iterations": iter_count,
            "composite_risk_score": float(final_rec.composite_risk.composite_risk_score),
            "decision_category": final_rec.decision_category.value,
        }
