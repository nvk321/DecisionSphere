"""
Sensitivity Analysis Application Service (Milestone 9.3).
Orchestrates discrete sweeps for Experiment B (Response Curves) and Experiment D (Parametric Sensitivity),
wrapping Phase 6, 7, and 8 sensitivity utilities with AnyIO threadpool offloading.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
import uuid

from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.models.scenario import ScenarioVersion
from backend.app.services.simulation_orchestrator import simulation_orchestrator

from src.business.engine import BusinessImpactEngine
from src.business.schema import BusinessAssumptions, BusinessImpactResult
from src.business.sensitivity import BusinessSensitivityEngine, PARAM_BOUNDS
from src.recommendation.crs import CompositeRiskEngine
from src.recommendation.engine import RecommendationEngine
from src.recommendation.schema import CRSWeights, RecommendationResult
from src.scenario.engine import ScenarioEngine
from src.scenario.schema import ScenarioAssumptions, ScenarioLevers, ScenarioRunResult
from src.scenario.sweep import ScenarioSweepEngine

logger = logging.getLogger("decisionsphere.services.sensitivity")


class SensitivityService:
    """
    Application service managing parametric sensitivity sweeps across operational,
    financial, and multi-criteria risk weight dimensions.
    """

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    def run_demand_shock_sweep(
        self,
        base_levers: Optional[ScenarioLevers] = None,
        shock_percentages: Optional[List[float]] = None,
        assumptions: Optional[ScenarioAssumptions] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executes a 1D discrete sweep across retail demand shock percentages (Experiment B).
        """
        simulation_orchestrator.verify_models()

        if shock_percentages is None:
            shock_percentages = [-30.0, -20.0, -10.0, 0.0, 10.0, 20.0, 30.0]

        demand_path = str(self.settings.model_descriptors["demand"].resolve_path(self.settings.project_root))
        supply_path = str(self.settings.model_descriptors["supply_chain"].resolve_path(self.settings.project_root))
        workforce_path = str(self.settings.model_descriptors["workforce"].resolve_path(self.settings.project_root))

        scenario_engine = ScenarioEngine(
            demand_artifact_path=demand_path,
            supply_artifact_path=supply_path,
            workforce_artifact_path=workforce_path,
        )
        sweep_engine = ScenarioSweepEngine(scenario_engine)

        runs: List[ScenarioRunResult] = sweep_engine.sweep_demand_shocks(
            shock_percentages=shock_percentages,
            base_levers=base_levers,
            assumptions=assumptions,
        )

        output = []
        for r in runs:
            output.append({
                "demand_shock_pct": r.levers.demand_growth_pct,
                "projected_sales_units": r.demand_result.scenario_value,
                "delta_sales_units": r.demand_result.delta_value,
                "late_delivery_risk": r.supply_chain_result.scenario_value,
                "delta_late_risk": r.supply_chain_result.delta_value,
                "attrition_risk": r.workforce_result.scenario_value,
                "delta_attrition_risk": r.workforce_result.delta_value,
                "epistemic_tier": "PREDICTED",
            })
        return output

    async def run_demand_shock_sweep_async(
        self,
        base_levers: Optional[ScenarioLevers] = None,
        shock_percentages: Optional[List[float]] = None,
        assumptions: Optional[ScenarioAssumptions] = None,
    ) -> List[Dict[str, Any]]:
        """Async AnyIO threadpool offload for demand shock sweep."""
        return await run_in_threadpool(
            self.run_demand_shock_sweep,
            base_levers,
            shock_percentages,
            assumptions,
        )

    def run_financial_parameter_sweep(
        self,
        scenario_run: ScenarioRunResult,
        parameter_name: str,
        candidate_values: List[float],
        base_assumptions: Optional[BusinessAssumptions] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executes a 1D sweep across a financial coupling parameter (ASM-001 through ASM-005).
        """
        sensitivity_engine = BusinessSensitivityEngine()
        return sensitivity_engine.sweep_parameter(
            scenario_run=scenario_run,
            parameter_name=parameter_name,
            candidate_values=candidate_values,
            base_assumptions=base_assumptions,
        )

    async def run_financial_parameter_sweep_async(
        self,
        scenario_run: ScenarioRunResult,
        parameter_name: str,
        candidate_values: List[float],
        base_assumptions: Optional[BusinessAssumptions] = None,
    ) -> List[Dict[str, Any]]:
        """Async AnyIO threadpool offload for financial sweep."""
        return await run_in_threadpool(
            self.run_financial_parameter_sweep,
            scenario_run,
            parameter_name,
            candidate_values,
            base_assumptions,
        )

    def run_crs_weight_sweep(
        self,
        scenario_run: ScenarioRunResult,
        business_impact: BusinessImpactResult,
        candidate_weights: List[CRSWeights],
    ) -> List[Dict[str, Any]]:
        """
        Sweeps CRS domain weight simplex vectors, tracking decision and risk score shifts.
        Delegates directly to RecommendationEngine.sweep_crs_weights.
        """
        rec_engine = RecommendationEngine()
        return rec_engine.sweep_crs_weights(
            scenario_run=scenario_run,
            business_impact=business_impact,
            weight_configurations=candidate_weights,
        )

    async def run_crs_weight_sweep_async(
        self,
        scenario_run: ScenarioRunResult,
        business_impact: BusinessImpactResult,
        candidate_weights: List[CRSWeights],
    ) -> List[Dict[str, Any]]:
        """Async AnyIO threadpool offload for CRS weight sweep."""
        return await run_in_threadpool(
            self.run_crs_weight_sweep,
            scenario_run,
            business_impact,
            candidate_weights,
        )

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
        rec_engine = RecommendationEngine()
        return rec_engine.find_recommendation_flip_threshold(
            scenario_run=scenario_run,
            base_assumptions=base_assumptions,
            parameter_name=parameter_name,
            candidate_values=candidate_values,
            impact_engine=impact_engine,
        )

    async def find_recommendation_flip_threshold_async(
        self,
        scenario_run: ScenarioRunResult,
        base_assumptions: BusinessAssumptions,
        parameter_name: str,
        candidate_values: List[float],
        impact_engine: Optional[BusinessImpactEngine] = None,
    ) -> Optional[Dict[str, Any]]:
        """Async AnyIO threadpool offload for flip threshold search."""
        return await run_in_threadpool(
            self.find_recommendation_flip_threshold,
            scenario_run,
            base_assumptions,
            parameter_name,
            candidate_values,
            impact_engine,
        )

    async def run_financial_sweep_for_scenario_async(
        self,
        db: Session,
        parameter_name: str,
        candidate_values: List[float],
        scenario_version_id: Optional[uuid.UUID] = None,
        policy_id: Optional[uuid.UUID] = None,
    ) -> List[Dict[str, Any]]:
        """
        Executes a 1D financial parameter sweep for a given scenario version or neutral baseline.
        """
        from backend.app.services.policy_service import policy_service
        from backend.app.services.scenario_service import scenario_service

        policy = (
            policy_service.get_policy_or_404(db, policy_id)
            if policy_id
            else policy_service.get_or_create_default_policy(db)
        )
        version = (
            scenario_service.get_scenario_version_or_404(db, scenario_version_id)
            if scenario_version_id
            else None
        )
        if version is None:
            version = ScenarioVersion(
                version_number=0,
                demand_growth_pct=0.0,
                promo_active=False,
                scheduled_days_offset=0,
                shipping_mode_override=None,
                overtime_workforce_pct=0.0,
                salary_hike_override=0.0,
                unit_price=1.0,
            )

        sc_res, fin_res, _, _ = await run_in_threadpool(
            simulation_orchestrator.run_analytical_pipeline, version, policy
        )
        base_assump = policy_service.to_business_assumptions(policy)
        raw_items = await self.run_financial_parameter_sweep_async(
            scenario_run=sc_res,
            parameter_name=parameter_name,
            candidate_values=candidate_values,
            base_assumptions=base_assump,
        )
        return raw_items

    async def run_crs_weight_sweep_for_scenario_async(
        self,
        db: Session,
        candidate_weights: List[CRSWeights],
        scenario_version_id: Optional[uuid.UUID] = None,
        policy_id: Optional[uuid.UUID] = None,
        tau_risk: float = 50.0,
    ) -> List[Dict[str, Any]]:
        """
        Executes a CRS domain weight simplex sweep for a given scenario version.
        """
        from backend.app.services.policy_service import policy_service
        from backend.app.services.scenario_service import scenario_service

        policy = (
            policy_service.get_policy_or_404(db, policy_id)
            if policy_id
            else policy_service.get_or_create_default_policy(db)
        )
        version = (
            scenario_service.get_scenario_version_or_404(db, scenario_version_id)
            if scenario_version_id
            else None
        )
        if version is None:
            version = ScenarioVersion(
                version_number=0,
                demand_growth_pct=0.0,
                promo_active=False,
                scheduled_days_offset=0,
                shipping_mode_override=None,
                overtime_workforce_pct=0.0,
                salary_hike_override=0.0,
                unit_price=1.0,
            )

        sc_res, fin_res, _, _ = await run_in_threadpool(
            simulation_orchestrator.run_analytical_pipeline, version, policy
        )
        return await self.run_crs_weight_sweep_async(
            scenario_run=sc_res,
            business_impact=fin_res,
            candidate_weights=candidate_weights,
        )

    async def find_flip_threshold_for_scenario_async(
        self,
        db: Session,
        parameter_name: str,
        candidate_values: List[float],
        scenario_version_id: Optional[uuid.UUID] = None,
        policy_id: Optional[uuid.UUID] = None,
        tau_risk: float = 50.0,
    ) -> Optional[Dict[str, Any]]:
        """
        Finds parameter tipping points for a given scenario version.
        """
        from backend.app.services.policy_service import policy_service
        from backend.app.services.scenario_service import scenario_service

        policy = (
            policy_service.get_policy_or_404(db, policy_id)
            if policy_id
            else policy_service.get_or_create_default_policy(db)
        )
        version = (
            scenario_service.get_scenario_version_or_404(db, scenario_version_id)
            if scenario_version_id
            else None
        )
        if version is None:
            version = ScenarioVersion(
                version_number=0,
                demand_growth_pct=0.0,
                promo_active=False,
                scheduled_days_offset=0,
                shipping_mode_override=None,
                overtime_workforce_pct=0.0,
                salary_hike_override=0.0,
                unit_price=1.0,
            )

        sc_res, fin_res, _, _ = await run_in_threadpool(
            simulation_orchestrator.run_analytical_pipeline, version, policy
        )
        base_assump = policy_service.to_business_assumptions(policy)
        return await self.find_recommendation_flip_threshold_async(
            scenario_run=sc_res,
            base_assumptions=base_assump,
            parameter_name=parameter_name,
            candidate_values=candidate_values,
        )


sensitivity_service = SensitivityService()
