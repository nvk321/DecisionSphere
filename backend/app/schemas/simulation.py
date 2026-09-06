"""
Simulation Run Pydantic v2 Schemas & Relational DTOs.
Handles multi-domain run requests, domain predictions, financial statements,
recommendations with strategic actions, and audit provenance records.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
import uuid

from pydantic import Field, computed_field, model_validator

from backend.app.schemas.common import BaseRequest, BaseSchema
from backend.app.schemas.scenario import ScenarioLeversSchema


class SimulationRequest(BaseRequest):
    """
    Request payload to trigger an atomic multi-domain simulation run.
    Optionally specifies version and policy IDs, or inline lever overrides.
    """
    scenario_version_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Target scenario version ID to simulate. Defaults to latest version if omitted."
    )
    policy_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Assumption policy ID to apply. Defaults to active corporate baseline if omitted."
    )
    override_levers: Optional[ScenarioLeversSchema] = Field(
        default=None,
        description="Optional temporary what-if lever overrides to evaluate without mutating the saved version."
    )


class DomainPredictionResponse(BaseSchema):
    """Inference output from an empirical machine learning pipeline."""
    id: uuid.UUID
    domain: str = Field(..., description="Domain code: DEMAND, SUPPLY_CHAIN, WORKFORCE")
    metric_name: str = Field(..., description="Target metric identifier")
    baseline_value: float = Field(..., description="Empirical historical baseline observation")
    scenario_value: float = Field(..., description="Predicted scenario outcome under applied levers")
    delta_value: float = Field(..., description="Unrounded delta shift (scenario - baseline)")
    epistemic_tier: str = Field("PREDICTED", description="Epistemic classification (PREDICTED)")


class FinancialLineItemDTO(BaseSchema):
    """Detailed managerial income statement disclosure."""
    id: Optional[uuid.UUID] = None
    category: str = Field(..., description="Line item accounting classification: REVENUE, EXPENSE, MARGIN")
    line_item_name: str = Field(..., description="Human-readable financial disclosure title")
    amount: float = Field(..., description="Monetary delta amount in USD")
    epistemic_tier: str = Field("CALCULATED", description="Epistemic classification (CALCULATED)")


class FinancialResultResponse(BaseSchema):
    """Managerial income statement aggregate and waterfall items."""
    id: uuid.UUID
    gross_revenue_delta: float
    realized_revenue_delta: float
    cogs_delta: float
    gross_margin_delta: float
    supply_chain_cost_delta: float
    workforce_cost_delta: float
    total_cost_delta: float
    net_profit_delta: float
    epistemic_tier: str = "CALCULATED"
    line_items: List[FinancialLineItemDTO] = Field(default_factory=list)


class StrategicActionDTO(BaseSchema):
    """Individual rule-grounded strategic intervention."""
    id: Optional[uuid.UUID] = None
    action_id: str = Field(..., description="Action identifier code (e.g. ACT-SC-001)")
    domain: str = Field(..., description="Affected operational domain")
    severity: str = Field(..., description="Execution priority: CRITICAL, HIGH, MEDIUM, LOW")
    title: str = Field(..., description="Action title")
    description: str = Field(..., description="Operational mitigation directive")
    trigger_rule_id: str = Field(..., description="Triggering rule identifier (e.g. RULE-01)")
    expected_trade_off: str = Field(..., description="Non-causal trade-off disclosure")
    epistemic_tier: str = Field("RECOMMENDED", description="Epistemic classification (RECOMMENDED)")


class RecommendationResponse(BaseSchema):
    """Synthesized recommendation result with Composite Risk Score decomposition."""
    id: uuid.UUID
    decision_category: str = Field(..., description="PROCEED, PROCEED_WITH_MITIGATIONS, REJECT_RESTRUCTURE")
    composite_risk_score: float = Field(..., description="Aggregate Composite Risk Score [0, 100]")
    risk_level: str = Field(..., description="Categorical risk level: LOW, MODERATE, HIGH, SEVERE")
    supply_chain_strain: float = Field(..., description="Logistics delay risk sub-index [0, 100]")
    workforce_strain: float = Field(..., description="Workforce attrition & overtime sub-index [0, 100]")
    demand_strain: float = Field(..., description="Demand volatility & stockout churn sub-index [0, 100]")
    primary_vulnerability: Optional[str] = Field(None, description="Dominant operational risk bottleneck")
    executive_briefing: str = Field(..., description="Non-causal executive synthesis statement")
    epistemic_tier: str = Field("RECOMMENDED", description="Epistemic classification (RECOMMENDED)")
    strategic_actions: List[StrategicActionDTO] = Field(default_factory=list)


class AuditProvenanceDTO(BaseSchema):
    """
    Cryptographic Provenance Signature Tuple (Sigma_run) matching Gate H.
    Guarantees reproducibility and scientific auditability of simulation outputs.
    """
    scenario_version_id: uuid.UUID
    artifact_hashes: Dict[str, str]
    policy_id: uuid.UUID
    policy_version: int
    git_commit: str
    app_version: str
    python_version: str
    migration_revision: str
    timestamp: str


class AuditRecordResponse(BaseSchema):
    """Read DTO for the audit record entity."""
    id: uuid.UUID
    simulation_run_id: Optional[uuid.UUID] = None
    provenance_tuple: Dict[str, Any]
    created_at: datetime

    @computed_field
    @property
    def git_commit_hash(self) -> str:
        return str(self.provenance_tuple.get("git_commit") or self.provenance_tuple.get("git_commit_hash", ""))

    @computed_field
    @property
    def model_hashes(self) -> Dict[str, str]:
        return self.provenance_tuple.get("artifact_hashes") or self.provenance_tuple.get("model_hashes", {})

    @computed_field
    @property
    def timestamp_utc(self) -> str:
        return str(self.provenance_tuple.get("timestamp") or self.provenance_tuple.get("timestamp_utc", ""))


class SimulationRunSummaryResponse(BaseSchema):
    """Lightweight summary of a simulation run for dashboard lists."""
    id: uuid.UUID
    scenario_version_id: uuid.UUID
    policy_id: uuid.UUID
    execution_status: str
    execution_duration_ms: Optional[float] = None
    executed_at: datetime
    decision_category: Optional[str] = None
    composite_risk_score: Optional[float] = None
    net_profit_delta: Optional[float] = None

    @model_validator(mode="before")
    @classmethod
    def extract_nested_aggregates(cls, data: Any) -> Any:
        if hasattr(data, "recommendation_result") or hasattr(data, "financial_result"):
            rec = getattr(data, "recommendation_result", None)
            fin = getattr(data, "financial_result", None)
            return {
                "id": data.id,
                "scenario_version_id": data.scenario_version_id,
                "policy_id": data.policy_id,
                "execution_status": data.execution_status,
                "execution_duration_ms": data.execution_duration_ms,
                "executed_at": data.executed_at,
                "decision_category": rec.decision_category if rec else None,
                "composite_risk_score": rec.composite_risk_score if rec else None,
                "net_profit_delta": fin.net_profit_delta if fin else None,
            }
        return data

    @computed_field
    @property
    def status(self) -> str:
        return self.execution_status

    @computed_field
    @property
    def duration_ms(self) -> Optional[float]:
        return self.execution_duration_ms

    @computed_field
    @property
    def created_at(self) -> datetime:
        return self.executed_at


class SimulationDetailResponse(BaseSchema):
    """Comprehensive end-to-end simulation output tree."""
    id: uuid.UUID
    scenario_version_id: uuid.UUID
    policy_id: uuid.UUID
    execution_status: str
    execution_duration_ms: Optional[float] = None
    executed_at: datetime
    domain_predictions: List[DomainPredictionResponse] = Field(default_factory=list)
    financial_result: Optional[FinancialResultResponse] = None
    recommendation_result: Optional[RecommendationResponse] = None
    audit_record: Optional[AuditRecordResponse] = None

    @computed_field
    @property
    def status(self) -> str:
        return self.execution_status

    @computed_field
    @property
    def duration_ms(self) -> Optional[float]:
        return self.execution_duration_ms

    @computed_field
    @property
    def created_at(self) -> datetime:
        return self.executed_at

    @computed_field
    @property
    def predictions(self) -> List[DomainPredictionResponse]:
        return self.domain_predictions
