"""
DomainPrediction Relational Entity.
Stores statistical machine learning predictions across Demand, Supply Chain, and Workforce domains.
"""
from __future__ import annotations

from typing import TYPE_CHECKING
import uuid

from sqlalchemy import Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.simulation_run import SimulationRun


class DomainPrediction(Base):
    """
    Predictive inference summary for a single domain within a simulation run.
    """
    __tablename__ = "domain_predictions"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    domain: Mapped[str] = mapped_column(String(30), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False)
    baseline_value: Mapped[float] = mapped_column(Float, nullable=False)
    scenario_value: Mapped[float] = mapped_column(Float, nullable=False)
    delta_value: Mapped[float] = mapped_column(Float, nullable=False)
    epistemic_tier: Mapped[str] = mapped_column(String(20), default="PREDICTED", nullable=False)

    # Relationships
    simulation_run: Mapped[SimulationRun] = relationship(
        "SimulationRun", back_populates="domain_predictions"
    )
