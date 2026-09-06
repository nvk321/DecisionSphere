"""
FinancialResult and FinancialLineItem Relational Entities.
Stores deterministic managerial accounting statements and line-item disclosures.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List
import uuid

from sqlalchemy import Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.simulation_run import SimulationRun


class FinancialResult(Base):
    """
    Managerial income statement aggregate representing net profit and cost shifts.
    """
    __tablename__ = "financial_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_run_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("simulation_runs.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # High-level financial aggregates
    gross_revenue_delta: Mapped[float] = mapped_column(Float, nullable=False)
    realized_revenue_delta: Mapped[float] = mapped_column(Float, nullable=False)
    cogs_delta: Mapped[float] = mapped_column(Float, nullable=False)
    gross_margin_delta: Mapped[float] = mapped_column(Float, nullable=False)
    supply_chain_cost_delta: Mapped[float] = mapped_column(Float, nullable=False)
    workforce_cost_delta: Mapped[float] = mapped_column(Float, nullable=False)
    total_cost_delta: Mapped[float] = mapped_column(Float, nullable=False)
    net_profit_delta: Mapped[float] = mapped_column(Float, nullable=False)

    epistemic_tier: Mapped[str] = mapped_column(String(20), default="CALCULATED", nullable=False)

    # Relationships
    simulation_run: Mapped[SimulationRun] = relationship(
        "SimulationRun", back_populates="financial_result"
    )
    line_items: Mapped[List[FinancialLineItem]] = relationship(
        "FinancialLineItem", back_populates="financial_result", cascade="all, delete-orphan"
    )


class FinancialLineItem(Base):
    """
    Individual transparent accounting line item supporting waterfall decomposition.
    """
    __tablename__ = "financial_line_items"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    financial_result_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("financial_results.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    category: Mapped[str] = mapped_column(String(50), nullable=False)
    line_item_name: Mapped[str] = mapped_column(String(100), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    epistemic_tier: Mapped[str] = mapped_column(String(20), default="CALCULATED", nullable=False)

    # Relationships
    financial_result: Mapped[FinancialResult] = relationship(
        "FinancialResult", back_populates="line_items"
    )
