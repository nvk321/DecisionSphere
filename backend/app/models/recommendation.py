"""
RecommendationResult and StrategicAction Relational Entities.
Stores lexicographic strategic decisions, Composite Risk Scores, and prioritized mitigations.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
import uuid

from sqlalchemy import Float, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.simulation_run import SimulationRun


class RecommendationResult(Base):
    """
    Strategic recommendation output synthesizing Composite Risk Score and decision gating.
    """
    __tablename__ = "recommendation_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    decision_category: Mapped[str] = mapped_column(String(30), nullable=False)
    composite_risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)

    # Sub-indices
    supply_chain_strain: Mapped[float] = mapped_column(Float, nullable=False)
    workforce_strain: Mapped[float] = mapped_column(Float, nullable=False)
    demand_strain: Mapped[float] = mapped_column(Float, nullable=False)

    primary_vulnerability: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    executive_briefing: Mapped[str] = mapped_column(Text, nullable=False)
    epistemic_tier: Mapped[str] = mapped_column(String(20), default="RECOMMENDED", nullable=False)

    # Relationships
    simulation_run: Mapped[SimulationRun] = relationship(
        "SimulationRun", back_populates="recommendation_result"
    )
    strategic_actions: Mapped[List[StrategicAction]] = relationship(
        "StrategicAction", back_populates="recommendation_result", cascade="all, delete-orphan"
    )


class StrategicAction(Base):
    """
    Individual evidence-grounded mitigation action directive.
    """
    __tablename__ = "strategic_actions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_result_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("recommendation_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    action_id: Mapped[str] = mapped_column(String(50), nullable=False)
    domain: Mapped[str] = mapped_column(String(30), nullable=False)
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    trigger_rule_id: Mapped[str] = mapped_column(String(50), nullable=False)
    expected_trade_off: Mapped[str] = mapped_column(Text, nullable=False)
    epistemic_tier: Mapped[str] = mapped_column(String(20), default="RECOMMENDED", nullable=False)

    # Relationships
    recommendation_result: Mapped[RecommendationResult] = relationship(
        "RecommendationResult", back_populates="strategic_actions"
    )
