"""
Sensitivity Analysis Route Controllers.
Provides RESTful endpoints for Experiment B (Response Curves) and Experiment D (Parametric Sensitivity).
"""
from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db_session
from backend.app.schemas.sensitivity import (
    CRSWeightSweepItem,
    CRSWeightSweepRequest,
    DemandShockSweepItem,
    DemandShockSweepRequest,
    FinancialSweepItem,
    FinancialSweepRequest,
    FlipThresholdResponse,
    FlipThresholdSearchRequest,
)
from backend.app.services.sensitivity_service import sensitivity_service
from src.recommendation.schema import CRSWeights
from src.scenario.schema import ScenarioLevers

logger = logging.getLogger("decisionsphere.api.sensitivity")
router = APIRouter()


@router.post(
    "/demand-sweep",
    response_model=List[DemandShockSweepItem],
    summary="Experiment B: Demand Shock Sensitivity Curve",
)
async def sweep_demand_shocks(
    payload: DemandShockSweepRequest,
) -> List[DemandShockSweepItem]:
    """
    Executes a discrete 1D parameter sweep across retail demand shock percentages.
    Tracks cascading non-linear effects on delivery delay risk and workforce attrition.
    Offloaded to worker threadpool via AnyIO (ADR-006).
    """
    base_levers = (
        payload.base_levers.to_scenario_levers()
        if payload.base_levers
        else None
    )
    raw_results = await sensitivity_service.run_demand_shock_sweep_async(
        base_levers=base_levers,
        shock_percentages=payload.shock_percentages,
    )

    return [
        DemandShockSweepItem(
            shock_pct=r["demand_shock_pct"],
            demand_forecast=r["projected_sales_units"],
            late_delivery_risk=r["late_delivery_risk"],
            workforce_attrition_risk=r["attrition_risk"],
            epistemic_tier="PREDICTED",
        )
        for r in raw_results
    ]


@router.post(
    "/financial-sweep",
    response_model=List[FinancialSweepItem],
    summary="Experiment D: Financial Parameter Sensitivity Sweep",
)
async def sweep_financial_parameter(
    payload: FinancialSweepRequest,
    db: Session = Depends(get_db_session),
) -> List[FinancialSweepItem]:
    """
    Executes a discrete 1D sensitivity sweep across an operational or labor coupling parameter
    (ASM-001 through ASM-005) to compute net profit trajectories.
    """
    raw_results = await sensitivity_service.run_financial_sweep_for_scenario_async(
        db=db,
        parameter_name=payload.parameter_name,
        candidate_values=payload.candidate_values,
        scenario_version_id=payload.scenario_version_id,
        policy_id=payload.policy_id,
    )

    return [
        FinancialSweepItem(
            parameter_name=r.get("parameter_name", payload.parameter_name),
            value=r.get("parameter_value", r.get("value", 0.0)),
            net_profit_delta=r["net_profit_delta"],
            is_profitable=r.get("is_profitable", r["net_profit_delta"] > 0.0),
            epistemic_tier="CALCULATED",
        )
        for r in raw_results
    ]


@router.post(
    "/crs-weight-sweep",
    response_model=List[CRSWeightSweepItem],
    summary="Multi-Criteria Risk Domain Weight Simplex Sweep",
)
async def sweep_crs_weights(
    payload: CRSWeightSweepRequest,
    db: Session = Depends(get_db_session),
) -> List[CRSWeightSweepItem]:
    """
    Sweeps alternative CRS domain weighting configurations (w_supply, w_workforce, w_demand),
    evaluating stability of the Composite Risk Score and executive decision categories.
    """
    candidate_weights = [
        CRSWeights(
            w_supply=w.w_supply,
            w_workforce=w.w_workforce,
            w_demand=w.w_demand,
        )
        for w in payload.candidate_weights
    ]

    raw_results = await sensitivity_service.run_crs_weight_sweep_for_scenario_async(
        db=db,
        candidate_weights=candidate_weights,
        scenario_version_id=payload.scenario_version_id,
        policy_id=payload.policy_id,
        tau_risk=payload.tau_risk,
    )

    return [
        CRSWeightSweepItem(
            w_supply=r["w_supply"],
            w_workforce=r["w_workforce"],
            w_demand=r["w_demand"],
            composite_risk_score=r["composite_risk_score"],
            risk_level=r["risk_level"],
            decision_category=r["decision_category"],
            epistemic_tier="CALCULATED",
        )
        for r in raw_results
    ]


@router.post(
    "/tipping-point",
    response_model=FlipThresholdResponse,
    summary="Decision Boundary Flip Threshold Search",
)
async def find_flip_threshold(
    payload: FlipThresholdSearchRequest,
    db: Session = Depends(get_db_session),
) -> FlipThresholdResponse:
    """
    Identifies parameter tipping points where the strategic decision category flips
    (e.g., from PROCEED to REJECT_RESTRUCTURE) without mutating baseline inputs.
    """
    result = await sensitivity_service.find_flip_threshold_for_scenario_async(
        db=db,
        parameter_name=payload.parameter_name,
        candidate_values=payload.candidate_values,
        scenario_version_id=payload.scenario_version_id,
        policy_id=payload.policy_id,
    )

    if result is None:
        return FlipThresholdResponse(
            parameter_name=payload.parameter_name,
            flip_detected=False,
            epistemic_tier="RECOMMENDED",
        )

    return FlipThresholdResponse(
        parameter_name=payload.parameter_name,
        flip_detected=result.get("flip_detected", True),
        flip_value=result.get("flip_value"),
        previous_category=result.get("previous_category"),
        new_category=result.get("new_category"),
        net_profit_delta=result.get("net_profit_delta"),
        composite_risk_score=result.get("composite_risk_score"),
        epistemic_tier="RECOMMENDED",
    )
