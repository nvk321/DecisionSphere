"""
Scenario and ScenarioVersion Relational Entities.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import uuid

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.simulation_run import SimulationRun


class Scenario(Base):
    """
    Mutable corporate scenario container representing a strategic planning topic.
    """
    __tablename__ = "scenarios"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    versions: Mapped[List[ScenarioVersion]] = relationship(
        "ScenarioVersion",
        back_populates="scenario",
        cascade="all, delete-orphan",
        order_by="ScenarioVersion.version_number",
    )


class ScenarioVersion(Base):
    """
    Immutable versioned snapshot of specific scenario lever parameters.
    """
    __tablename__ = "scenario_versions"
    __table_args__ = (
        UniqueConstraint("scenario_id", "version_number", name="uq_scenario_version_number"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scenario_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # Scenario Lever Parameters
    demand_growth_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    promo_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    scheduled_days_offset: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shipping_mode_override: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    overtime_workforce_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    salary_hike_override: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    scenario: Mapped[Scenario] = relationship("Scenario", back_populates="versions")
    simulation_runs: Mapped[List[SimulationRun]] = relationship(
        "SimulationRun", back_populates="scenario_version"
    )
