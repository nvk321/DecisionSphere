"""
SimulationRun and AuditRecord Relational Entities.
Tracks execution records, runtime performance, and immutable provenance signatures.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional
import uuid

from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.financial import FinancialResult
    from backend.app.models.policy import AssumptionPolicy
    from backend.app.models.prediction import DomainPrediction
    from backend.app.models.recommendation import RecommendationResult
    from backend.app.models.scenario import ScenarioVersion


class SimulationRun(Base):
    """
    Execution record linking an immutable scenario version, an immutable policy,
    analytical model predictions, financial outcomes, and recommendations.
    """
    __tablename__ = "simulation_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scenario_versions.id"), nullable=False, index=True
    )
    policy_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assumption_policies.id"), nullable=False, index=True
    )

    execution_status: Mapped[str] = mapped_column(String(20), default="SUCCESS", nullable=False)
    execution_duration_ms: Mapped[float] = mapped_column(Float, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

    # Relationships
    scenario_version: Mapped[ScenarioVersion] = relationship(
        "ScenarioVersion", back_populates="simulation_runs"
    )
    policy: Mapped[AssumptionPolicy] = relationship(
        "AssumptionPolicy", back_populates="simulation_runs"
    )
    domain_predictions: Mapped[List[DomainPrediction]] = relationship(
        "DomainPrediction", back_populates="simulation_run", cascade="all, delete-orphan"
    )
    financial_result: Mapped[Optional[FinancialResult]] = relationship(
        "FinancialResult", back_populates="simulation_run", uselist=False, cascade="all, delete-orphan"
    )
    recommendation_result: Mapped[Optional[RecommendationResult]] = relationship(
        "RecommendationResult", back_populates="simulation_run", uselist=False, cascade="all, delete-orphan"
    )
    audit_record: Mapped[Optional[AuditRecord]] = relationship(
        "AuditRecord", back_populates="simulation_run", uselist=False, cascade="all, delete-orphan"
    )


class AuditRecord(Base):
    """
    Immutable audit record storing the 8-element cryptographic provenance signature tuple.
    """
    __tablename__ = "audit_records"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    provenance_tuple: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    simulation_run: Mapped[SimulationRun] = relationship(
        "SimulationRun", back_populates="audit_record"
    )
