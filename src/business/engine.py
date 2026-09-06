"""
DecisionSphere — Phase 7 Business Impact Analysis Engine
Calculates deterministic, traceable financial accounting metrics (Revenue, COGS, Disruption Costs, Net Profit Delta)
from Phase 6 ScenarioRunResult under explicit BusinessAssumptions (ASM-001 through ASM-005).

Epistemic Tier: CALCULATED (Tier 5)
Governing Mandate:
"Business Impact Analysis converts scenario-derived model outputs into transparent financial
calculations under explicitly declared assumptions; it does not convert statistical predictions
into claims about guaranteed real-world outcomes."
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from copy import deepcopy

from src.scenario.schema import ScenarioRunResult
from src.business.schema import (
    BusinessAssumptions,
    FinancialLineItemProvenance,
    FinancialLineItem,
    BreakEvenAnalysis,
    BusinessImpactResult,
    EXPEDITED_SHIPPING_MODES,
    REGULAR_SHIPPING_MODES,
)


class BusinessImpactEngine:
    """
    Evaluates financial implications of multi-domain scenario execution results.
    Adheres strictly to the 6-tier epistemic hierarchy, preventing double-counting
    and preserving 64-bit IEEE 754 floating-point precision without premature rounding.
    """

    def __init__(self, default_assumptions: Optional[BusinessAssumptions] = None):
        self.default_assumptions = default_assumptions or BusinessAssumptions()

    def evaluate(
        self,
        scenario_run: ScenarioRunResult,
        assumptions: Optional[BusinessAssumptions] = None,
    ) -> BusinessImpactResult:
        """
        Executes deterministic financial calculations on an immutable ScenarioRunResult.

        Parameters
        ----------
        scenario_run : ScenarioRunResult
            Immutable, validated multi-domain scenario run result from Phase 6.
        assumptions : Optional[BusinessAssumptions]
            Financial and cost coupling parameters (ASM-001 to ASM-005). If None, uses defaults.

        Returns
        -------
        BusinessImpactResult
            Complete, strictly validated financial accounting breakdown.
        """
        if not isinstance(scenario_run, ScenarioRunResult):
            raise TypeError(f"Expected ScenarioRunResult, got {type(scenario_run).__name__}")

        p = assumptions or self.default_assumptions
        if not isinstance(p, BusinessAssumptions):
            raise TypeError(f"Expected BusinessAssumptions, got {type(p).__name__}")

        # ---------------------------------------------------------------------
        # 1. RETAIL SALES & GROSS REVENUE ACCOUNTING
        # ---------------------------------------------------------------------
        y_sales_base = float(scenario_run.demand_result.baseline_value)
        y_sales_scen = float(scenario_run.demand_result.scenario_value)

        gross_rev_base = y_sales_base * p.unit_price
        gross_rev_scen = y_sales_scen * p.unit_price
        gross_rev_delta = gross_rev_scen - gross_rev_base

        gross_rev_provenance = FinancialLineItemProvenance(
            epistemic_tier="CALCULATED",
            formula="GrossRevenue = Y_sales * unit_price",
            assumptions_applied=["unit_price"],
            unit="USD",
            calculation_statement=(
                f"Gross revenue calculated from demand model forecast multiplied by unit selling price "
                f"(${p.unit_price:.2f}/unit)."
            ),
        )
        gross_revenue_item = FinancialLineItem(
            name="Gross Revenue",
            baseline_value=gross_rev_base,
            scenario_value=gross_rev_scen,
            delta_value=gross_rev_delta,
            unit="USD",
            provenance=gross_rev_provenance,
        )

        # ---------------------------------------------------------------------
        # 2. FULFILLMENT LOSS & REALIZED REVENUE ACCOUNTING
        # ---------------------------------------------------------------------
        p_late_base = float(scenario_run.supply_chain_result.baseline_value)
        p_late_scen = float(scenario_run.supply_chain_result.scenario_value)

        l_fulfill_base = min(1.0, p_late_base * p.asm_003_cancellation_factor)
        l_fulfill_scen = min(1.0, p_late_scen * p.asm_003_cancellation_factor)

        realized_rev_base = gross_rev_base * (1.0 - l_fulfill_base)
        realized_rev_scen = gross_rev_scen * (1.0 - l_fulfill_scen)
        realized_rev_delta = realized_rev_scen - realized_rev_base

        realized_rev_provenance = FinancialLineItemProvenance(
            epistemic_tier="CALCULATED",
            formula="RealizedRevenue = GrossRevenue * (1 - min(1.0, P_late * kappa_stockout))",
            assumptions_applied=["ASM-003", "unit_price"],
            unit="USD",
            calculation_statement=(
                f"Realized revenue accounts for delay-induced stockout cancellations via ASM-003 "
                f"(kappa_stockout={p.asm_003_cancellation_factor:.2f})."
            ),
        )
        realized_revenue_item = FinancialLineItem(
            name="Realized Revenue",
            baseline_value=realized_rev_base,
            scenario_value=realized_rev_scen,
            delta_value=realized_rev_delta,
            unit="USD",
            provenance=realized_rev_provenance,
        )

        # ---------------------------------------------------------------------
        # 3. COST OF GOODS SOLD (COGS) — OPTION B: REALIZED SALES
        # ---------------------------------------------------------------------
        cogs_base = realized_rev_base * p.cogs_ratio
        cogs_scen = realized_rev_scen * p.cogs_ratio
        cogs_delta = cogs_scen - cogs_base

        cogs_provenance = FinancialLineItemProvenance(
            epistemic_tier="CALCULATED",
            formula="COGS = RealizedRevenue * cogs_ratio",
            assumptions_applied=["cogs_ratio", "ASM-003", "unit_price"],
            unit="USD",
            calculation_statement=(
                f"COGS evaluated strictly on realized sales revenue at ratio cogs_ratio={p.cogs_ratio:.2f}. "
                f"Cancelled orders do not incur goods production costs."
            ),
        )
        cogs_item = FinancialLineItem(
            name="Cost of Goods Sold (COGS)",
            baseline_value=cogs_base,
            scenario_value=cogs_scen,
            delta_value=cogs_delta,
            unit="USD",
            provenance=cogs_provenance,
        )

        # Contribution Gross Margin
        gm_base = realized_rev_base - cogs_base
        gm_scen = realized_rev_scen - cogs_scen
        gm_delta = gm_scen - gm_base

        gm_provenance = FinancialLineItemProvenance(
            epistemic_tier="CALCULATED",
            formula="GrossMargin = RealizedRevenue - COGS",
            assumptions_applied=["cogs_ratio", "ASM-003", "unit_price"],
            unit="USD",
            calculation_statement="Contribution margin generated by realized product shipments.",
        )
        gross_margin_item = FinancialLineItem(
            name="Gross Margin",
            baseline_value=gm_base,
            scenario_value=gm_scen,
            delta_value=gm_delta,
            unit="USD",
            provenance=gm_provenance,
        )

        # ---------------------------------------------------------------------
        # 4. SUPPLY CHAIN DISRUPTION COST (DELIVERY PENALTY + EXPEDITED FREIGHT)
        # ---------------------------------------------------------------------
        n_orders_scen = float(scenario_run.normalized_order_volume)
        if y_sales_scen > 0.0:
            n_orders_base = n_orders_scen * (y_sales_base / y_sales_scen)
        else:
            n_orders_base = n_orders_scen

        # Delivered-delayed orders (excluding lost/cancelled orders)
        n_deliv_delayed_base = n_orders_base * p_late_base * (1.0 - p.asm_003_cancellation_factor)
        n_deliv_delayed_scen = n_orders_scen * p_late_scen * (1.0 - p.asm_003_cancellation_factor)

        delay_penalty_base = n_deliv_delayed_base * p.asm_001_delay_penalty
        delay_penalty_scen = n_deliv_delayed_scen * p.asm_001_delay_penalty

        # Expedited shipping mapping
        shipping_mode = scenario_run.levers.shipping_mode_override
        n_expedited_base = n_orders_base * p.baseline_expedited_fraction

        if shipping_mode in EXPEDITED_SHIPPING_MODES:
            n_expedited_scen = n_orders_scen * 1.0
        elif shipping_mode in REGULAR_SHIPPING_MODES:
            n_expedited_scen = 0.0
        else:
            # Default or None: fallback to baseline fraction
            n_expedited_scen = n_orders_scen * p.baseline_expedited_fraction

        expedite_cost_base = n_expedited_base * p.asm_002_expedite_fee
        expedite_cost_scen = n_expedited_scen * p.asm_002_expedite_fee

        supply_cost_base = delay_penalty_base + expedite_cost_base
        supply_cost_scen = delay_penalty_scen + expedite_cost_scen
        supply_cost_delta = supply_cost_scen - supply_cost_base

        supply_provenance = FinancialLineItemProvenance(
            epistemic_tier="CALCULATED",
            formula=(
                "SupplyCost = (N_orders * P_late * (1 - kappa_stockout) * C_delay_penalty) + "
                "(N_expedited * C_expedite_fee)"
            ),
            assumptions_applied=["ASM-001", "ASM-002", "ASM-003", "baseline_expedited_fraction"],
            unit="USD",
            calculation_statement=(
                f"Delay penalties (${p.asm_001_delay_penalty:.2f}/delayed order) charged only on delivered-delayed "
                f"shipments. Expedited air freight fees (${p.asm_002_expedite_fee:.2f}/order) charged on expedited volume."
            ),
        )
        supply_chain_item = FinancialLineItem(
            name="Supply Chain Cost",
            baseline_value=supply_cost_base,
            scenario_value=supply_cost_scen,
            delta_value=supply_cost_delta,
            unit="USD",
            provenance=supply_provenance,
        )

        # ---------------------------------------------------------------------
        # 5. WORKFORCE DISRUPTION & OVERTIME LABOR COST
        # ---------------------------------------------------------------------
        n_headcount = float(scenario_run.workforce_cohort_summary.total_headcount)
        p_att_base = float(scenario_run.workforce_result.baseline_value)
        p_att_scen = float(scenario_run.workforce_result.scenario_value)

        # Turnover replacement cost
        turnover_cost_base = (n_headcount * p_att_base) * p.asm_004_replacement_cost
        turnover_cost_scen = (n_headcount * p_att_scen) * p.asm_004_replacement_cost

        # Overtime labor cost
        k_ot_base = float(scenario_run.workforce_cohort_summary.baseline_overtime_count)
        k_ot_scen = float(scenario_run.workforce_cohort_summary.scenario_overtime_count)

        ot_hours_base = k_ot_base * p.overtime_hours_per_worker
        ot_hours_scen = k_ot_scen * p.overtime_hours_per_worker

        ot_cost_base = ot_hours_base * p.asm_005_overtime_rate
        ot_cost_scen = ot_hours_scen * p.asm_005_overtime_rate

        workforce_cost_base = turnover_cost_base + ot_cost_base
        workforce_cost_scen = turnover_cost_scen + ot_cost_scen
        workforce_cost_delta = workforce_cost_scen - workforce_cost_base

        workforce_provenance = FinancialLineItemProvenance(
            epistemic_tier="CALCULATED",
            formula=(
                "WorkforceCost = (N_workforce * P_attrition * C_replacement) + "
                "(K_ot * h_ot * R_overtime)"
            ),
            assumptions_applied=["ASM-004", "ASM-005", "overtime_hours_per_worker"],
            unit="USD",
            calculation_statement=(
                f"Turnover replacement cost (${p.asm_004_replacement_cost:.2f}/departure) evaluated on expected departures. "
                f"Overtime wages evaluated at ${p.asm_005_overtime_rate:.2f}/hour for {p.overtime_hours_per_worker:.1f} hours/cycle."
            ),
        )
        workforce_item = FinancialLineItem(
            name="Workforce Cost",
            baseline_value=workforce_cost_base,
            scenario_value=workforce_cost_scen,
            delta_value=workforce_cost_delta,
            unit="USD",
            provenance=workforce_provenance,
        )

        # ---------------------------------------------------------------------
        # 6. TOTAL OPERATIONAL COST & NET INCREMENTAL PROFIT
        # ---------------------------------------------------------------------
        total_cost_base = cogs_base + supply_cost_base + workforce_cost_base
        total_cost_scen = cogs_scen + supply_cost_scen + workforce_cost_scen
        total_cost_delta = total_cost_scen - total_cost_base

        total_cost_provenance = FinancialLineItemProvenance(
            epistemic_tier="CALCULATED",
            formula="TotalOperationalCost = COGS + SupplyCost + WorkforceCost",
            assumptions_applied=[
                "cogs_ratio", "ASM-001", "ASM-002", "ASM-003", "ASM-004", "ASM-005"
            ],
            unit="USD",
            calculation_statement="Sum of product manufacturing, logistical disruption, and workforce operational expenses.",
        )
        total_operational_cost_item = FinancialLineItem(
            name="Total Operational Cost",
            baseline_value=total_cost_base,
            scenario_value=total_cost_scen,
            delta_value=total_cost_delta,
            unit="USD",
            provenance=total_cost_provenance,
        )

        # Net Incremental Profit Delta: Delta Realized Revenue - Delta Total Cost
        net_profit_delta = realized_rev_delta - total_cost_delta
        is_profitable = bool(net_profit_delta > 0.0)

        # ---------------------------------------------------------------------
        # 7. BREAK-EVEN ANALYSIS (PARAMETER THRESHOLDS WHERE DELTA PROFIT = 0)
        # ---------------------------------------------------------------------
        # Break-even Delay Penalty: DeltaGrossMargin - DeltaExpedite - DeltaWorkforce - (DeltaN_deliv_delayed * C*) = 0
        delta_n_deliv_delayed = n_deliv_delayed_scen - n_deliv_delayed_base
        delta_expedite_cost = expedite_cost_scen - expedite_cost_base
        
        be_delay_penalty = None
        if abs(delta_n_deliv_delayed) > 1e-9:
            be_delay_penalty = (gm_delta - delta_expedite_cost - workforce_cost_delta) / delta_n_deliv_delayed

        # Break-even Replacement Cost: DeltaGrossMargin - DeltaSupply - DeltaOvertime - (DeltaN_departures * C*) = 0
        delta_departures = (n_headcount * p_att_scen) - (n_headcount * p_att_base)
        delta_ot_cost = ot_cost_scen - ot_cost_base

        be_replacement_cost = None
        if abs(delta_departures) > 1e-9:
            be_replacement_cost = (gm_delta - supply_cost_delta - delta_ot_cost) / delta_departures

        # Break-even Overtime Rate: DeltaGrossMargin - DeltaSupply - DeltaTurnover - (DeltaOTHours * R*) = 0
        delta_ot_hours = ot_hours_scen - ot_hours_base
        delta_turnover_cost = turnover_cost_scen - turnover_cost_base

        be_overtime_rate = None
        if abs(delta_ot_hours) > 1e-9:
            be_overtime_rate = (gm_delta - supply_cost_delta - delta_turnover_cost) / delta_ot_hours

        # Break-even COGS Ratio: DeltaRealizedRev * (1 - cogs*) - DeltaSupply - DeltaWorkforce = 0
        be_cogs_ratio = None
        if abs(realized_rev_delta) > 1e-9:
            be_cogs_ratio = 1.0 - (supply_cost_delta + workforce_cost_delta) / realized_rev_delta

        break_even = BreakEvenAnalysis(
            break_even_delay_penalty=be_delay_penalty,
            break_even_replacement_cost=be_replacement_cost,
            break_even_overtime_rate=be_overtime_rate,
            break_even_cogs_ratio=be_cogs_ratio,
            sensitivity_summary={
                "delta_n_delivered_delayed_orders": delta_n_deliv_delayed,
                "delta_expected_departures": delta_departures,
                "delta_overtime_hours": delta_ot_hours,
                "net_profit_delta_usd": net_profit_delta,
            },
        )

        # ---------------------------------------------------------------------
        # 8. EPISTEMIC NON-CAUSAL EXECUTIVE STATEMENT
        # ---------------------------------------------------------------------
        profit_verb = "increase" if net_profit_delta >= 0.0 else "reduction"
        statement = (
            f"Under the declared scenario assumptions, the model-implied net profit shift is calculated as "
            f"${net_profit_delta:+,.2f} USD (Realized Revenue Delta: ${realized_rev_delta:+,.2f} USD, "
            f"Total Cost Delta: ${total_cost_delta:+,.2f} USD), representing a net {profit_verb}. "
            f"This calculation is based on statistical conditional predictions and declared assumptions; "
            f"it does not constitute a causal guarantee."
        )

        timestamp_str = datetime.now(timezone.utc).isoformat()

        return BusinessImpactResult(
            scenario_id=scenario_run.scenario_id,
            scenario_name=scenario_run.scenario_name,
            gross_revenue=gross_revenue_item,
            realized_revenue=realized_revenue_item,
            cogs=cogs_item,
            gross_margin=gross_margin_item,
            supply_chain_cost=supply_chain_item,
            workforce_cost=workforce_item,
            total_operational_cost=total_operational_cost_item,
            net_profit_delta=net_profit_delta,
            is_profitable_scenario=is_profitable,
            epistemic_tier="CALCULATED",
            break_even_analysis=break_even,
            statement=statement,
            timestamp=timestamp_str,
        )
