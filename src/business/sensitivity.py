"""
DecisionSphere — Phase 7 Business Sensitivity Analysis Engine
Performs deterministic, reproducible 1D parametric sensitivity sweeps and break-even searches
over financial coupling parameters ASM-001 through ASM-005 (Experiment D).

Epistemic Tier: CALCULATED (Tier 5)
Governing Mandate:
"Sensitivity sweeps stress-test declared assumptions to reveal financial stability boundaries;
they do not represent empirical observations or causal dynamics."
"""

from typing import List, Dict, Any, Optional
import numpy as np

from src.scenario.schema import ScenarioRunResult
from src.business.schema import BusinessAssumptions, BusinessImpactResult
from src.business.engine import BusinessImpactEngine


# Official sensitivity bounds from Table 1 of docs/assumptions-and-open-questions.md
PARAM_BOUNDS: Dict[str, tuple[float, float]] = {
    "asm_001_delay_penalty": (10.00, 60.00),
    "asm_002_expedite_fee": (5.00, 35.00),
    "asm_003_cancellation_factor": (0.05, 0.40),
    "asm_004_replacement_cost": (15000.00, 60000.00),
    "asm_005_overtime_rate": (30.00, 75.00),
    "cogs_ratio": (0.30, 0.90),
    "unit_price": (0.50, 50.00),
    "overtime_hours_per_worker": (5.0, 60.0),
    "baseline_expedited_fraction": (0.0, 1.0),
}


class BusinessSensitivityEngine:
    """
    Executes reproducible parametric sensitivity sweeps and break-even boundary detection
    without mutating the underlying ScenarioRunResult or baseline BusinessAssumptions.
    """

    def __init__(self, impact_engine: Optional[BusinessImpactEngine] = None):
        self.impact_engine = impact_engine or BusinessImpactEngine()

    def sweep_parameter(
        self,
        scenario_run: ScenarioRunResult,
        parameter_name: str,
        candidate_values: List[float],
        base_assumptions: Optional[BusinessAssumptions] = None,
    ) -> List[Dict[str, Any]]:
        """
        Sweeps a single assumption parameter across candidate values, recording financial deltas.

        Parameters
        ----------
        scenario_run : ScenarioRunResult
            Immutable scenario execution result.
        parameter_name : str
            Name of the BusinessAssumptions parameter to vary.
        candidate_values : List[float]
            List of values within valid parameter bounds to evaluate.
        base_assumptions : Optional[BusinessAssumptions]
            Starting assumptions baseline. If None, uses default BusinessAssumptions.

        Returns
        -------
        List[Dict[str, Any]]
            Sequential evaluation records including net profit delta and cost breakdown.
        """
        if parameter_name not in PARAM_BOUNDS:
            raise ValueError(
                f"Unknown or non-sweepable parameter '{parameter_name}'. Valid parameters: {sorted(PARAM_BOUNDS.keys())}"
            )

        base = base_assumptions or BusinessAssumptions()
        base_dict = base.model_dump()
        records: List[Dict[str, Any]] = []

        for val in candidate_values:
            # Instantiate validated BusinessAssumptions with the single overridden field
            modified_dict = dict(base_dict)
            modified_dict[parameter_name] = float(val)
            scenario_assumptions = BusinessAssumptions(**modified_dict)

            result = self.impact_engine.evaluate(scenario_run, assumptions=scenario_assumptions)

            records.append({
                "parameter_name": parameter_name,
                "parameter_value": float(val),
                "net_profit_delta": result.net_profit_delta,
                "realized_revenue_delta": result.realized_revenue.delta_value,
                "total_operational_cost_delta": result.total_operational_cost.delta_value,
                "supply_chain_cost_delta": result.supply_chain_cost.delta_value,
                "workforce_cost_delta": result.workforce_cost.delta_value,
                "cogs_delta": result.cogs.delta_value,
                "is_profitable_scenario": result.is_profitable_scenario,
            })

        return records

    def find_break_even_point(
        self,
        scenario_run: ScenarioRunResult,
        parameter_name: str,
        base_assumptions: Optional[BusinessAssumptions] = None,
    ) -> Optional[float]:
        """
        Identifies the exact parameter threshold where net incremental profit delta crosses zero (DeltaProfit = 0).

        Parameters
        ----------
        scenario_run : ScenarioRunResult
            Immutable scenario run result.
        parameter_name : str
            Parameter to solve for break-even.
        base_assumptions : Optional[BusinessAssumptions]
            Starting baseline assumptions.

        Returns
        -------
        Optional[float]
            The break-even parameter value if solvable and within or near valid bounds; None if gradient is zero.
        """
        base = base_assumptions or BusinessAssumptions()
        base_result = self.impact_engine.evaluate(scenario_run, assumptions=base)
        be = base_result.break_even_analysis

        if parameter_name == "asm_001_delay_penalty":
            return be.break_even_delay_penalty
        elif parameter_name == "asm_004_replacement_cost":
            return be.break_even_replacement_cost
        elif parameter_name == "asm_005_overtime_rate":
            return be.break_even_overtime_rate
        elif parameter_name == "cogs_ratio":
            return be.break_even_cogs_ratio
        elif parameter_name == "asm_002_expedite_fee":
            # Solve: DeltaGrossMargin - DeltaDelayCost - DeltaWorkforce - (DeltaN_expedited * C_expedite*) = 0
            # From engine:
            delta_gm = base_result.gross_margin.delta_value
            delta_wf = base_result.workforce_cost.delta_value
            # Delivery delay cost delta
            y_sales_scen = float(scenario_run.demand_result.scenario_value)
            y_sales_base = float(scenario_run.demand_result.baseline_value)
            n_orders_scen = float(scenario_run.normalized_order_volume)
            n_orders_base = n_orders_scen * (y_sales_base / y_sales_scen) if y_sales_scen > 0 else n_orders_scen
            
            p_late_base = float(scenario_run.supply_chain_result.baseline_value)
            p_late_scen = float(scenario_run.supply_chain_result.scenario_value)
            n_deliv_delayed_base = n_orders_base * p_late_base * (1.0 - base.asm_003_cancellation_factor)
            n_deliv_delayed_scen = n_orders_scen * p_late_scen * (1.0 - base.asm_003_cancellation_factor)
            delta_delay_cost = (n_deliv_delayed_scen - n_deliv_delayed_base) * base.asm_001_delay_penalty

            # Expedited counts
            mode = scenario_run.levers.shipping_mode_override
            n_exp_base = n_orders_base * base.baseline_expedited_fraction
            if mode in {"First Class", "Same Day"}:
                n_exp_scen = n_orders_scen * 1.0
            elif mode in {"Standard Class", "Second Class"}:
                n_exp_scen = 0.0
            else:
                n_exp_scen = n_orders_scen * base.baseline_expedited_fraction
            
            delta_n_exp = n_exp_scen - n_exp_base
            if abs(delta_n_exp) > 1e-9:
                return (delta_gm - delta_delay_cost - delta_wf) / delta_n_exp
            return None
        else:
            # For non-linear parameters (e.g. asm_003_cancellation_factor), use bisection within bounds
            low, high = PARAM_BOUNDS[parameter_name]
            f_low = self.sweep_parameter(scenario_run, parameter_name, [low], base)[0]["net_profit_delta"]
            f_high = self.sweep_parameter(scenario_run, parameter_name, [high], base)[0]["net_profit_delta"]

            if f_low * f_high > 0:
                # No sign change within bounds
                return None

            for _ in range(50):
                mid = (low + high) / 2.0
                f_mid = self.sweep_parameter(scenario_run, parameter_name, [mid], base)[0]["net_profit_delta"]
                if abs(f_mid) < 1e-5:
                    return mid
                if f_low * f_mid < 0:
                    high = mid
                    f_high = f_mid
                else:
                    low = mid
                    f_low = f_mid
            return (low + high) / 2.0

    def sweep_all_asm(
        self,
        scenario_run: ScenarioRunResult,
        steps: int = 5,
        base_assumptions: Optional[BusinessAssumptions] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Executes uniform grid sensitivity sweeps for ASM-001 through ASM-005 over their declared ranges.

        Parameters
        ----------
        scenario_run : ScenarioRunResult
            Immutable scenario execution result.
        steps : int
            Number of evaluation points per parameter (minimum 2).
        base_assumptions : Optional[BusinessAssumptions]
            Starting assumptions baseline.

        Returns
        -------
        Dict[str, List[Dict[str, Any]]]
            Mapping of parameter names (ASM-001 to ASM-005) to their evaluation records.
        """
        if steps < 2:
            raise ValueError(f"steps must be >= 2, got {steps}")

        asm_keys = [
            "asm_001_delay_penalty",
            "asm_002_expedite_fee",
            "asm_003_cancellation_factor",
            "asm_004_replacement_cost",
            "asm_005_overtime_rate",
        ]

        all_results: Dict[str, List[Dict[str, Any]]] = {}
        for key in asm_keys:
            low, high = PARAM_BOUNDS[key]
            values = [float(x) for x in np.linspace(low, high, steps)]
            all_results[key] = self.sweep_parameter(scenario_run, key, values, base_assumptions)

        return all_results
