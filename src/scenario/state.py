"""
DecisionSphere — Formal State-Space Vector Architecture
Defines the mathematical Scenario State Vector S_t in R^k for cross-domain operational simulation.
Epistemic Tier: Formal State Representation spanning PREDICTED, PROPAGATED, and CALCULATED.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import numpy as np
from pydantic import BaseModel, Field


class ScenarioStateVector(BaseModel):
    """
    Formal mathematical representation of the enterprise scenario state S_t in R^24.
    
    Provides strict IEEE-754 continuous precision, vector serialization,
    Euclidean state distance calculation, and non-divergent state transitions.
    """
    # 1. Commercial / Demand State (Dimension 1-6)
    sales_baseline: float = Field(..., description="Baseline forecasted demand units Y_0")
    sales_scenario: float = Field(..., description="Scenario forecasted demand units Y_s")
    sales_delta: float = Field(..., description="Incremental demand units Delta Y")
    daily_sales_rate: float = Field(..., description="Daily sales run rate Y_s / H")
    cycle_volume: float = Field(..., description="Planning cycle volume V_cycle (ASM-008)")
    order_volume: float = Field(..., description="Operational order dispatch volume N_orders (ASM-007)")

    # 2. Logistics / Supply Chain State (Dimension 7-11)
    late_prob_baseline: float = Field(..., description="Baseline late delivery probability p_late,0")
    late_prob_scenario: float = Field(..., description="Scenario late delivery probability p_late,s")
    late_prob_delta: float = Field(..., description="Shift in late delivery risk Delta p_late")
    scheduled_days_offset: float = Field(..., description="Logistics schedule compression/expansion offset")
    expedited_shipping_flag: float = Field(..., description="Binary flag indicating air freight mode (1.0) or standard (0.0)")

    # 3. Workforce / Human Capital State (Dimension 12-16)
    attrition_prob_baseline: float = Field(..., description="Baseline mean attrition risk p_att,0")
    attrition_prob_scenario: float = Field(..., description="Scenario mean attrition risk p_att,s")
    attrition_prob_delta: float = Field(..., description="Shift in employee attrition risk Delta p_att")
    overtime_percentage: float = Field(..., description="Assigned overtime workforce percentage u_ot in [0, 100]")
    work_life_balance_decrement: float = Field(..., description="Applied burnout decrement Delta WLB (ASM-006)")

    # 4. Managerial Accounting State (Dimension 17-21)
    gross_revenue_delta: float = Field(..., description="Gross revenue incremental delta USD")
    realized_revenue_delta: float = Field(..., description="Realized revenue incremental delta USD")
    supply_chain_cost_delta: float = Field(..., description="Incremental logistics penalties and expedite fees USD")
    workforce_cost_delta: float = Field(..., description="Incremental turnover and overtime payroll costs USD")
    net_profit_delta: float = Field(..., description="Net incremental operating profit delta Delta Pi USD")

    # 5. Composite Operational Risk State (Dimension 22-24)
    supply_risk_index: float = Field(..., description="Supply chain delivery risk sub-index S_supply in [0, 100]")
    workforce_risk_index: float = Field(..., description="Workforce burnout risk sub-index S_workforce in [0, 100]")
    composite_risk_score: float = Field(..., description="Aggregate multi-criteria Composite Risk Score CRS in [0, 100]")

    # Provenance and Metadata
    scenario_id: str = Field(default="state_default", description="Scenario identifier")
    timestamp: Optional[str] = Field(default=None, description="ISO timestamp of state computation")

    def to_numpy(self) -> np.ndarray:
        """
        Converts the 24-dimensional state vector to a contiguous 1D NumPy array in R^24.
        """
        return np.array([
            self.sales_baseline,
            self.sales_scenario,
            self.sales_delta,
            self.daily_sales_rate,
            self.cycle_volume,
            self.order_volume,
            self.late_prob_baseline,
            self.late_prob_scenario,
            self.late_prob_delta,
            self.scheduled_days_offset,
            self.expedited_shipping_flag,
            self.attrition_prob_baseline,
            self.attrition_prob_scenario,
            self.attrition_prob_delta,
            self.overtime_percentage,
            self.work_life_balance_decrement,
            self.gross_revenue_delta,
            self.realized_revenue_delta,
            self.supply_chain_cost_delta,
            self.workforce_cost_delta,
            self.net_profit_delta,
            self.supply_risk_index,
            self.workforce_risk_index,
            self.composite_risk_score,
        ], dtype=np.float64)

    @classmethod
    def state_dimension(cls) -> int:
        """Returns the canonical state-space dimension k = 24."""
        return 24

    @classmethod
    def feature_names(cls) -> List[str]:
        """Returns the canonical ordered feature names of the 24 state dimensions."""
        return [
            "sales_baseline",
            "sales_scenario",
            "sales_delta",
            "daily_sales_rate",
            "cycle_volume",
            "order_volume",
            "late_prob_baseline",
            "late_prob_scenario",
            "late_prob_delta",
            "scheduled_days_offset",
            "expedited_shipping_flag",
            "attrition_prob_baseline",
            "attrition_prob_scenario",
            "attrition_prob_delta",
            "overtime_percentage",
            "work_life_balance_decrement",
            "gross_revenue_delta",
            "realized_revenue_delta",
            "supply_chain_cost_delta",
            "workforce_cost_delta",
            "net_profit_delta",
            "supply_risk_index",
            "workforce_risk_index",
            "composite_risk_score",
        ]

    def state_norm(self, ord: Optional[int] = 2) -> float:
        """Computes the vector p-norm (default L2 Euclidean norm) of the state vector."""
        return float(np.linalg.norm(self.to_numpy(), ord=ord))

    def distance_to(self, other: "ScenarioStateVector", ord: Optional[int] = 2) -> float:
        """
        Computes the distance ||S_1 - S_2|| between two enterprise scenario states in R^24.
        """
        return float(np.linalg.norm(self.to_numpy() - other.to_numpy(), ord=ord))

    @classmethod
    def from_pipeline_results(
        cls,
        scenario_run: Any,
        business_impact: Any,
        crs_breakdown: Any,
    ) -> "ScenarioStateVector":
        """
        Factory method constructing ScenarioStateVector from Phase 6, 7, and 8 results.
        """
        is_expedited = (
            1.0 if scenario_run.levers.shipping_mode_override in ["First Class", "Same Day"] else 0.0
        )
        return cls(
            sales_baseline=float(scenario_run.demand_result.baseline_value),
            sales_scenario=float(scenario_run.demand_result.scenario_value),
            sales_delta=float(scenario_run.demand_result.delta_value),
            daily_sales_rate=float(scenario_run.demand_result.scenario_value) / 14.0,
            cycle_volume=float(scenario_run.demand_result.scenario_value) / 14.0 * float(scenario_run.assumptions.asm_008_cycle_days),
            order_volume=float(scenario_run.normalized_order_volume),
            late_prob_baseline=float(scenario_run.supply_chain_result.baseline_value),
            late_prob_scenario=float(scenario_run.supply_chain_result.scenario_value),
            late_prob_delta=float(scenario_run.supply_chain_result.delta_value),
            scheduled_days_offset=float(scenario_run.levers.scheduled_days_offset),
            expedited_shipping_flag=is_expedited,
            attrition_prob_baseline=float(scenario_run.workforce_result.baseline_value),
            attrition_prob_scenario=float(scenario_run.workforce_result.scenario_value),
            attrition_prob_delta=float(scenario_run.workforce_result.delta_value),
            overtime_percentage=float(scenario_run.workforce_cohort_summary.actual_scenario_overtime_percentage),
            work_life_balance_decrement=float(scenario_run.assumptions.asm_006_wlb_decrement),
            gross_revenue_delta=float(business_impact.gross_revenue.delta_value),
            realized_revenue_delta=float(business_impact.realized_revenue.delta_value),
            supply_chain_cost_delta=float(business_impact.supply_chain_cost.delta_value),
            workforce_cost_delta=float(business_impact.workforce_cost.delta_value),
            net_profit_delta=float(business_impact.net_profit_delta),
            supply_risk_index=float(crs_breakdown.supply_chain_risk_score),
            workforce_risk_index=float(crs_breakdown.workforce_risk_score),
            composite_risk_score=float(crs_breakdown.composite_risk_score),
            scenario_id=scenario_run.scenario_id,
            timestamp=scenario_run.execution_timestamp,
        )
