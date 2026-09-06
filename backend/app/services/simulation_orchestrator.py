"""
Simulation Orchestrator Application Service (Milestone 9.3).
Coordinates analytical execution across Phase 6, 7, and 8 engines,
verifies model integrity (Gate I), offloads CPU tasks to AnyIO threadpool (ADR-006),
and persists execution records under strict database transaction atomicity (Gate F & Gate H).
"""
from __future__ import annotations

from datetime import datetime, timezone
import logging
import platform
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid

from starlette.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from backend.app.core.config import Settings, get_settings
from backend.app.core.errors import (
    EntityNotFoundError,
    ModelIntegrityError,
    ModelNotFoundError,
)
from backend.app.models.financial import FinancialLineItem, FinancialResult
from backend.app.models.policy import AssumptionPolicy
from backend.app.models.prediction import DomainPrediction
from backend.app.models.recommendation import RecommendationResult, StrategicAction
from backend.app.models.scenario import ScenarioVersion
from backend.app.models.simulation_run import AuditRecord, SimulationRun
from backend.app.services.policy_service import policy_service
from backend.app.services.scenario_service import scenario_service

from src.business.engine import BusinessImpactEngine
from src.business.schema import BusinessImpactResult
from src.recommendation.engine import RecommendationEngine
from src.recommendation.schema import RecommendationResult as AnalyticalRecommendationResult
from src.scenario.engine import ScenarioEngine
from src.scenario.schema import ScenarioLevers, ScenarioRunResult

logger = logging.getLogger("decisionsphere.services.simulation")


class SimulationOrchestrator:
    """
    Central application service wrapping the Phase 6 -> 7 -> 8 analytical pipeline
    and persisting simulation records, domain predictions, financials, and recommendations.
    """

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or get_settings()

    def verify_models(self) -> None:
        """
        Gate I: Model Integrity Failure Gate.
        Verifies that all three frozen model files exist on disk and match authoritative SHA-256 hashes.
        Raises ModelNotFoundError or ModelIntegrityError if check fails.
        """
        report = self.settings.verify_model_artifacts()
        for key, item in report.items():
            if not item["exists"]:
                raise ModelNotFoundError(
                    f"Model artifact '{key}' not found at path: {item['path']}",
                    details={"model_key": key, "path": item["path"]},
                )
            if not item["verified"]:
                raise ModelIntegrityError(
                    f"Model artifact '{key}' failed SHA-256 verification. "
                    f"Expected: {item['expected_sha256']}, Found: {item['actual_sha256']}",
                    details={
                        "model_key": key,
                        "expected_sha256": item["expected_sha256"],
                        "actual_sha256": item["actual_sha256"],
                    },
                )

    @staticmethod
    def _extract_levers(scenario_version: ScenarioVersion) -> ScenarioLevers:
        """Extracts strongly-typed ScenarioLevers from ScenarioVersion."""
        scenario_name = "Simulation Scenario"
        try:
            if scenario_version.scenario is not None and scenario_version.scenario.name:
                scenario_name = scenario_version.scenario.name
        except Exception:
            pass

        return ScenarioLevers(
            scenario_id=str(scenario_version.scenario_id),
            scenario_name=scenario_name,
            demand_growth_pct=scenario_version.demand_growth_pct,
            promo_active=scenario_version.promo_active,
            scheduled_days_offset=scenario_version.scheduled_days_offset,
            shipping_mode_override=scenario_version.shipping_mode_override,
            overtime_workforce_pct=scenario_version.overtime_workforce_pct,
            salary_hike_override=scenario_version.salary_hike_override if scenario_version.salary_hike_override > 0 else None,
        )

    def _execute_engines(
        self,
        levers: ScenarioLevers,
        business_assumptions: Any,
        crs_weights: Any,
        tau_risk: float,
    ) -> Tuple[ScenarioRunResult, BusinessImpactResult, AnalyticalRecommendationResult, float]:
        """Pure CPU-bound analytical execution across Phases 6, 7, and 8."""
        self.verify_models()
        start_time = time.perf_counter()

        demand_path = str(self.settings.model_descriptors["demand"].resolve_path(self.settings.project_root))
        supply_path = str(self.settings.model_descriptors["supply_chain"].resolve_path(self.settings.project_root))
        workforce_path = str(self.settings.model_descriptors["workforce"].resolve_path(self.settings.project_root))

        scenario_engine = ScenarioEngine(
            demand_artifact_path=demand_path,
            supply_artifact_path=supply_path,
            workforce_artifact_path=workforce_path,
        )
        impact_engine = BusinessImpactEngine()
        rec_engine = RecommendationEngine()

        scenario_result = scenario_engine.run_scenario(levers=levers)
        impact_result = impact_engine.evaluate(scenario_result, business_assumptions)
        rec_result = rec_engine.evaluate(
            scenario_result,
            impact_result,
            weights=crs_weights,
            operational_strain_threshold=tau_risk,
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return scenario_result, impact_result, rec_result, elapsed_ms

    def run_analytical_pipeline(
        self,
        scenario_version: ScenarioVersion,
        policy: AssumptionPolicy,
    ) -> Tuple[ScenarioRunResult, BusinessImpactResult, AnalyticalRecommendationResult, float]:
        """Synchronous analytical pipeline execution."""
        levers = self._extract_levers(scenario_version)
        business_assumptions = policy_service.to_business_assumptions(policy)
        crs_weights = policy_service.to_crs_weights(policy)
        return self._execute_engines(levers, business_assumptions, crs_weights, policy.tau_risk)

    async def run_analytical_pipeline_async(
        self,
        scenario_version: ScenarioVersion,
        policy: AssumptionPolicy,
    ) -> Tuple[ScenarioRunResult, BusinessImpactResult, AnalyticalRecommendationResult, float]:
        """
        Asynchronous wrapper offloading the CPU-bound simulation to an AnyIO worker thread (ADR-006).
        Extracts values on caller thread so worker thread operates exclusively on pure Pydantic models.
        """
        levers = self._extract_levers(scenario_version)
        business_assumptions = policy_service.to_business_assumptions(policy)
        crs_weights = policy_service.to_crs_weights(policy)
        tau_risk = policy.tau_risk
        return await run_in_threadpool(
            self._execute_engines, levers, business_assumptions, crs_weights, tau_risk
        )

    def _persist_results(
        self,
        db: Session,
        version: ScenarioVersion,
        policy: AssumptionPolicy,
        scenario_res: ScenarioRunResult,
        impact_res: BusinessImpactResult,
        rec_res: AnalyticalRecommendationResult,
        duration_ms: float,
    ) -> SimulationRun:
        """
        Persists the full relational simulation tree under a single atomic transaction (Gate F & Gate H).
        """
        try:
            # 4. Insert SimulationRun parent record
            run = SimulationRun(
                scenario_version_id=version.id,
                policy_id=policy.id,
                execution_status="SUCCESS",
                execution_duration_ms=duration_ms,
            )
            db.add(run)
            db.flush()

            # 5. Insert DomainPredictions (PREDICTED tier)
            pred_demand = DomainPrediction(
                simulation_run_id=run.id,
                domain="DEMAND",
                metric_name="mean_sales",
                baseline_value=float(scenario_res.demand_result.baseline_value),
                scenario_value=float(scenario_res.demand_result.scenario_value),
                delta_value=float(scenario_res.demand_result.delta_value),
                epistemic_tier="PREDICTED",
            )
            pred_sc = DomainPrediction(
                simulation_run_id=run.id,
                domain="SUPPLY_CHAIN",
                metric_name="late_delivery_probability",
                baseline_value=float(scenario_res.supply_chain_result.baseline_value),
                scenario_value=float(scenario_res.supply_chain_result.scenario_value),
                delta_value=float(scenario_res.supply_chain_result.delta_value),
                epistemic_tier="PREDICTED",
            )
            pred_wf = DomainPrediction(
                simulation_run_id=run.id,
                domain="WORKFORCE",
                metric_name="attrition_probability",
                baseline_value=float(scenario_res.workforce_result.baseline_value),
                scenario_value=float(scenario_res.workforce_result.scenario_value),
                delta_value=float(scenario_res.workforce_result.delta_value),
                epistemic_tier="PREDICTED",
            )
            db.add_all([pred_demand, pred_sc, pred_wf])

            # 6. Insert FinancialResult & FinancialLineItems (CALCULATED tier)
            fin_result = FinancialResult(
                simulation_run_id=run.id,
                gross_revenue_delta=float(impact_res.gross_revenue.delta_value),
                realized_revenue_delta=float(impact_res.realized_revenue.delta_value),
                cogs_delta=float(impact_res.cogs.delta_value),
                gross_margin_delta=float(impact_res.gross_margin.delta_value),
                supply_chain_cost_delta=float(impact_res.supply_chain_cost.delta_value),
                workforce_cost_delta=float(impact_res.workforce_cost.delta_value),
                total_cost_delta=float(impact_res.total_operational_cost.delta_value),
                net_profit_delta=float(impact_res.net_profit_delta),
                epistemic_tier="CALCULATED",
            )
            db.add(fin_result)
            db.flush()

            raw_line_items = [
                ("REVENUE", impact_res.gross_revenue),
                ("REVENUE", impact_res.realized_revenue),
                ("EXPENSE", impact_res.cogs),
                ("MARGIN", impact_res.gross_margin),
                ("EXPENSE", impact_res.supply_chain_cost),
                ("EXPENSE", impact_res.workforce_cost),
                ("EXPENSE", impact_res.total_operational_cost),
            ]
            line_items = [
                FinancialLineItem(
                    financial_result_id=fin_result.id,
                    category=category,
                    line_item_name=item.name,
                    amount=float(item.delta_value),
                    epistemic_tier=item.provenance.epistemic_tier,
                )
                for category, item in raw_line_items
            ]
            db.add_all(line_items)

            # 7. Insert RecommendationResult & StrategicActions (RECOMMENDED tier)
            rec_record = RecommendationResult(
                simulation_run_id=run.id,
                decision_category=rec_res.decision_category.value,
                composite_risk_score=float(rec_res.composite_risk.composite_risk_score),
                risk_level=rec_res.composite_risk.risk_level,
                supply_chain_strain=float(rec_res.composite_risk.supply_chain_risk_score),
                workforce_strain=float(rec_res.composite_risk.workforce_risk_score),
                demand_strain=float(rec_res.composite_risk.demand_execution_risk_score),
                primary_vulnerability=rec_res.trade_off_evaluation.primary_vulnerability,
                executive_briefing=rec_res.executive_briefing,
                epistemic_tier="RECOMMENDED",
            )
            db.add(rec_record)
            db.flush()

            actions = [
                StrategicAction(
                    recommendation_result_id=rec_record.id,
                    action_id=act.action_id,
                    domain=act.domain,
                    severity=act.severity.value,
                    title=act.title,
                    description=act.description,
                    trigger_rule_id=act.trigger_rule_id,
                    expected_trade_off=act.expected_trade_off,
                    epistemic_tier=act.epistemic_tier,
                )
                for act in rec_res.recommended_actions
            ]
            db.add_all(actions)

            # 8. Insert AuditRecord with 8-element provenance tuple Sigma_run (Gate H)
            audit = AuditRecord(
                simulation_run_id=run.id,
                provenance_tuple={
                    "scenario_version_id": str(version.id),
                    "artifact_hashes": {
                        k: d.expected_sha256 for k, d in self.settings.model_descriptors.items()
                    },
                    "policy_id": str(policy.id),
                    "policy_version": policy.version_number,
                    "git_commit": "13f6c0f017fab043f61397e9570bee7de6e97017",
                    "app_version": self.settings.app_version,
                    "python_version": platform.python_version(),
                    "migration_revision": "18e29557529f",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )
            db.add(audit)

            # 9. Atomic commit
            db.commit()
            db.refresh(run)
            return run

        except Exception as exc:
            db.rollback()
            logger.error("Simulation run failed. Transaction rolled back atomically: %s", exc, exc_info=True)
            raise

    def execute_and_persist(
        self,
        db: Session,
        scenario_version_id: uuid.UUID,
        policy_id: Optional[uuid.UUID] = None,
    ) -> SimulationRun:
        """
        Executes end-to-end simulation synchronously and persists the full relational entity graph
        under a single atomic transaction (Gate F: Transaction Atomicity).
        """
        version = scenario_service.get_scenario_version_or_404(db, scenario_version_id)
        if policy_id is not None:
            policy = policy_service.get_policy_or_404(db, policy_id)
        else:
            policy = policy_service.get_or_create_default_policy(db)

        scenario_res, impact_res, rec_res, duration_ms = self.run_analytical_pipeline(version, policy)
        return self._persist_results(db, version, policy, scenario_res, impact_res, rec_res, duration_ms)

    async def execute_and_persist_async(
        self,
        db: Session,
        scenario_version_id: uuid.UUID,
        policy_id: Optional[uuid.UUID] = None,
    ) -> SimulationRun:
        """
        Executes end-to-end simulation asynchronously by offloading analytical computation
        to an AnyIO worker threadpool (ADR-006) and persisting the relational tree atomically.
        """
        version = scenario_service.get_scenario_version_or_404(db, scenario_version_id)
        if policy_id is not None:
            policy = policy_service.get_policy_or_404(db, policy_id)
        else:
            policy = policy_service.get_or_create_default_policy(db)

        scenario_res, impact_res, rec_res, duration_ms = await self.run_analytical_pipeline_async(version, policy)
        return self._persist_results(db, version, policy, scenario_res, impact_res, rec_res, duration_ms)

    @staticmethod
    def get_simulation_run(db: Session, run_id: uuid.UUID) -> Optional[SimulationRun]:
        """Fetch simulation run by ID."""
        return db.query(SimulationRun).filter_by(id=run_id).first()

    @staticmethod
    def get_simulation_run_or_404(db: Session, run_id: uuid.UUID) -> SimulationRun:
        """Fetch simulation run by ID or raise EntityNotFoundError."""
        run = SimulationOrchestrator.get_simulation_run(db, run_id)
        if not run:
            raise EntityNotFoundError(f"SimulationRun not found with ID: {run_id}")
        return run

    @staticmethod
    def list_simulation_runs(
        db: Session,
        scenario_id: Optional[uuid.UUID] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[SimulationRun]:
        """List simulation runs, optionally filtered by parent scenario."""
        query = db.query(SimulationRun)
        if scenario_id is not None:
            query = query.join(ScenarioVersion).filter(ScenarioVersion.scenario_id == scenario_id)
        return query.order_by(SimulationRun.executed_at.desc()).offset(skip).limit(limit).all()


simulation_orchestrator = SimulationOrchestrator()
