"""
DecisionSphere — Phase 6 Scenario Sweep Engine
Provides discrete parameter sensitivity sweep utilities for Experiment B (Scenario Response Curves)
and Experiment D (Parametric Sensitivity Analysis) across frozen model artifacts.
"""

from typing import List, Dict, Any, Optional, Union
import pandas as pd

from src.scenario.schema import ScenarioLevers, ScenarioAssumptions, ScenarioRunResult
from src.scenario.engine import ScenarioEngine
from src.scenario.assumptions import ASM_REGISTRY, PHASE_6_OPERATIONAL_ASSUMPTIONS


class ScenarioSweepEngine:
    """
    Executes systematic parameter sweeps across user strategic levers and operational assumptions.
    
    Guarantees:
    - Purely deterministic grid evaluation.
    - Zero retraining, refitting, or recalibrating of underlying predictive models.
    - No unsupported statistical prior distributions (uniform or Gaussian) assigned to sensitivity ranges.
    """

    def __init__(self, engine: ScenarioEngine):
        self.engine = engine

    def sweep_demand_shocks(
        self,
        shock_percentages: List[float],
        base_levers: Optional[ScenarioLevers] = None,
        assumptions: Optional[ScenarioAssumptions] = None,
        demand_context: Optional[Dict[str, Any]] = None,
        orders_df: Optional[pd.DataFrame] = None,
        workforce_df: Optional[pd.DataFrame] = None,
    ) -> List[ScenarioRunResult]:
        """
        Evaluates system response across varying demand shock magnitudes (Experiment B).
        """
        if base_levers is None:
            base_levers = ScenarioLevers()
        if assumptions is None:
            assumptions = ScenarioAssumptions()

        results = []
        for shock in shock_percentages:
            levers = ScenarioLevers(
                scenario_name=f"Demand Shock {shock:+.1f}%",
                demand_growth_pct=shock,
                promo_active=base_levers.promo_active,
                scheduled_days_offset=base_levers.scheduled_days_offset,
                shipping_mode_override=base_levers.shipping_mode_override,
                overtime_workforce_pct=base_levers.overtime_workforce_pct,
                salary_hike_override=base_levers.salary_hike_override,
            )
            res = self.engine.run_scenario(
                levers=levers,
                assumptions=assumptions,
                demand_context=demand_context,
                orders_df=orders_df,
                workforce_df=workforce_df,
            )
            results.append(res)
        return results

    def sweep_overtime_mandates(
        self,
        overtime_percentages: List[float],
        base_levers: Optional[ScenarioLevers] = None,
        assumptions: Optional[ScenarioAssumptions] = None,
        demand_context: Optional[Dict[str, Any]] = None,
        orders_df: Optional[pd.DataFrame] = None,
        workforce_df: Optional[pd.DataFrame] = None,
    ) -> List[ScenarioRunResult]:
        """
        Evaluates workforce attrition risk response across varying mandated overtime levels.
        """
        if base_levers is None:
            base_levers = ScenarioLevers()
        if assumptions is None:
            assumptions = ScenarioAssumptions()

        results = []
        for ot_pct in overtime_percentages:
            levers = ScenarioLevers(
                scenario_name=f"Overtime Mandate {ot_pct:.0f}%",
                demand_growth_pct=base_levers.demand_growth_pct,
                promo_active=base_levers.promo_active,
                scheduled_days_offset=base_levers.scheduled_days_offset,
                shipping_mode_override=base_levers.shipping_mode_override,
                overtime_workforce_pct=ot_pct,
                salary_hike_override=base_levers.salary_hike_override,
            )
            res = self.engine.run_scenario(
                levers=levers,
                assumptions=assumptions,
                demand_context=demand_context,
                orders_df=orders_df,
                workforce_df=workforce_df,
            )
            results.append(res)
        return results

    def sweep_operational_assumption(
        self,
        asm_id: str,
        values: List[Union[int, float]],
        base_levers: Optional[ScenarioLevers] = None,
        base_assumptions: Optional[ScenarioAssumptions] = None,
        demand_context: Optional[Dict[str, Any]] = None,
        orders_df: Optional[pd.DataFrame] = None,
        workforce_df: Optional[pd.DataFrame] = None,
    ) -> List[ScenarioRunResult]:
        """
        Evaluates model sensitivity across an audited sensitivity range for ASM-006, ASM-007, or ASM-008 (Experiment D).
        """
        asm_clean = asm_id.strip().upper()
        if asm_clean not in PHASE_6_OPERATIONAL_ASSUMPTIONS:
            raise ValueError(
                f"Assumption '{asm_id}' is not an operational Phase 6 assumption. "
                f"Allowed Phase 6 assumptions are: {sorted(PHASE_6_OPERATIONAL_ASSUMPTIONS)}"
            )

        if base_levers is None:
            base_levers = ScenarioLevers()
        if base_assumptions is None:
            base_assumptions = ScenarioAssumptions()

        results = []
        for val in values:
            if not ASM_REGISTRY.validate_value(asm_clean, val):
                meta = ASM_REGISTRY.get(asm_clean)
                raise ValueError(
                    f"Value {val} is outside audited sensitivity range {meta.sensitivity_range} for {asm_clean}."
                )

            current_dict = base_assumptions.model_dump()
            if asm_clean == "ASM-006":
                current_dict["asm_006_wlb_decrement"] = int(val)
            elif asm_clean == "ASM-007":
                current_dict["asm_007_volume_scaling"] = float(val)
            elif asm_clean == "ASM-008":
                current_dict["asm_008_cycle_days"] = int(val)

            custom_assumptions = ScenarioAssumptions(**current_dict)
            res = self.engine.run_scenario(
                levers=base_levers,
                assumptions=custom_assumptions,
                demand_context=demand_context,
                orders_df=orders_df,
                workforce_df=workforce_df,
            )
            results.append(res)
        return results

    def to_dataframe(self, results: List[ScenarioRunResult]) -> pd.DataFrame:
        """
        Flattens a list of ScenarioRunResult objects into an analytical DataFrame for visualization.
        """
        records = []
        for r in results:
            rec = {
                "scenario_id": r.scenario_id,
                "scenario_name": r.scenario_name,
                "demand_growth_pct": r.levers.demand_growth_pct,
                "promo_active": r.levers.promo_active,
                "scheduled_days_offset": r.levers.scheduled_days_offset,
                "shipping_mode_override": r.levers.shipping_mode_override,
                "overtime_workforce_pct": r.levers.overtime_workforce_pct,
                "asm_006_wlb": r.assumptions.asm_006_wlb_decrement,
                "asm_007_volume_scaling": r.assumptions.asm_007_volume_scaling,
                "asm_008_cycle_days": r.assumptions.asm_008_cycle_days,
                "demand_baseline_sales": r.demand_result.baseline_value,
                "demand_scenario_sales": r.demand_result.scenario_value,
                "demand_delta_sales": r.demand_result.delta_value,
                "normalized_order_volume": r.normalized_order_volume,
                "supply_baseline_late_risk": r.supply_chain_result.baseline_value,
                "supply_scenario_late_risk": r.supply_chain_result.scenario_value,
                "supply_delta_late_risk": r.supply_chain_result.delta_value,
                "workforce_baseline_attrition_risk": r.workforce_result.baseline_value,
                "workforce_scenario_attrition_risk": r.workforce_result.scenario_value,
                "workforce_delta_attrition_risk": r.workforce_result.delta_value,
                "workforce_target_ot_pct": r.workforce_cohort_summary.target_overtime_percentage,
                "workforce_actual_ot_pct": r.workforce_cohort_summary.actual_scenario_overtime_percentage,
                "workforce_switched_count": r.workforce_cohort_summary.overtime_switched_count,
            }
            records.append(rec)
        return pd.DataFrame(records)
