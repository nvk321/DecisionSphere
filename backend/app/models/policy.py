"""
AssumptionPolicy Relational Entity.
Stores versioned, immutable corporate parameter policies (ASM-001 through ASM-010).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
import uuid

from sqlalchemy import DateTime, Float, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.simulation_run import SimulationRun


class AssumptionPolicy(Base):
    """
    Immutable versioned corporate policy containing assumptions ASM-001 to ASM-010.
    """
    __tablename__ = "assumption_policies"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="Corporate Baseline Policy")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ASM-001 through ASM-005 (Financial accounting parameters)
    late_penalty_rate: Mapped[float] = mapped_column(Float, default=25.0, nullable=False)
    expedite_fee: Mapped[float] = mapped_column(Float, default=15.0, nullable=False)
    stockout_churn_factor: Mapped[float] = mapped_column(Float, default=0.15, nullable=False)
    replacement_cost: Mapped[float] = mapped_column(Float, default=30000.0, nullable=False)
    overtime_wage_rate: Mapped[float] = mapped_column(Float, default=45.0, nullable=False)

    # ASM-007 and ASM-008 (Normalization & temporal synchronization)
    order_scaling_factor: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    planning_cycle_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    # ASM-009 (CRS Simplex domain weights)
    crs_w_supply: Mapped[float] = mapped_column(Float, default=0.40, nullable=False)
    crs_w_workforce: Mapped[float] = mapped_column(Float, default=0.40, nullable=False)
    crs_w_demand: Mapped[float] = mapped_column(Float, default=0.20, nullable=False)

    # ASM-010 (Operational risk tolerance threshold)
    tau_risk: Mapped[float] = mapped_column(Float, default=50.0, nullable=False)

    # Financial margin benchmark
    cogs_ratio: Mapped[float] = mapped_column(Float, default=0.60, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    simulation_runs: Mapped[List[SimulationRun]] = relationship(
        "SimulationRun", back_populates="policy"
    )
