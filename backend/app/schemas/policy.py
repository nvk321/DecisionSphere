"""
Assumption Policy Pydantic v2 Schemas.
Manages enterprise parameter sets (ASM-001 through ASM-010),
simplex constraints validation on domain weights, and ORM serialization.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
import uuid

from pydantic import Field, model_validator

from backend.app.schemas.common import BaseRequest, BaseSchema


class PolicyCreate(BaseRequest):
    """
    Payload for creating or versioning an enterprise assumption policy.
    Enforces Gate E simplex constraints on CRS weights (w_s + w_w + w_d = 1.0)
    and empirical validation bounds on operational/financial parameters.
    Supports both ASM standard codes (asm_001_delay_penalty, w_supply)
    and canonical database column names (late_penalty_rate, crs_w_supply).
    """
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Policy title (e.g. 'Corporate Baseline FY2026')"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Policy context and rationale"
    )

    # ASM-001 through ASM-005 Financial Coupling Constants
    late_penalty_rate: float = Field(
        default=25.0,
        ge=0.0,
        description="ASM-001: Contractual late-delivery penalty per delayed order ($/order)"
    )
    expedite_fee: float = Field(
        default=15.0,
        ge=0.0,
        description="ASM-002: Expedited logistics freight surcharge per order ($/order)"
    )
    stockout_churn_factor: float = Field(
        default=0.15,
        ge=0.0,
        le=1.0,
        description="ASM-003: Customer churn cancellation factor on delayed orders [0.0, 1.0]"
    )
    replacement_cost: float = Field(
        default=30000.0,
        ge=0.0,
        le=60000.0,
        description="ASM-004: Voluntary employee turnover replacement cost ($/employee) [0, 60000]"
    )
    overtime_wage_rate: float = Field(
        default=45.0,
        ge=0.0,
        description="ASM-005: Overtime hourly labor cost rate ($/hour)"
    )
    cogs_ratio: float = Field(
        default=0.60,
        ge=0.0,
        le=1.0,
        description="Cost of Goods Sold ratio on realized sales revenue [0.0, 1.0]"
    )
    order_scaling_factor: float = Field(
        default=1.0,
        ge=0.0,
        description="ASM-007: Volume scaling factor"
    )
    planning_cycle_days: int = Field(
        default=30,
        ge=1,
        description="ASM-008: Temporal planning cycle horizon in days"
    )

    # ASM-009 Composite Risk Score Simplex Domain Weights
    crs_w_supply: float = Field(
        default=0.40,
        ge=0.0,
        le=1.0,
        description="Weight assigned to supply chain late-delivery strain sub-index"
    )
    crs_w_workforce: float = Field(
        default=0.40,
        ge=0.0,
        le=1.0,
        description="Weight assigned to workforce attrition & overtime strain sub-index"
    )
    crs_w_demand: float = Field(
        default=0.20,
        ge=0.0,
        le=1.0,
        description="Weight assigned to demand volatility & fulfillment churn sub-index"
    )

    # ASM-010 Operational Strain Risk Tolerance Threshold
    tau_risk: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Operational strain tolerance threshold gating PROCEED vs PROCEED_WITH_MITIGATIONS [0, 100]"
    )

    @model_validator(mode="before")
    @classmethod
    def remap_asm_aliases(cls, data: Any) -> Any:
        """Remaps ASM naming conventions to canonical policy attributes."""
        if isinstance(data, dict):
            mapping = {
                "asm_001_delay_penalty": "late_penalty_rate",
                "asm_002_expedite_fee": "expedite_fee",
                "asm_003_cancellation_factor": "stockout_churn_factor",
                "asm_004_replacement_cost": "replacement_cost",
                "asm_005_overtime_rate": "overtime_wage_rate",
                "w_supply": "crs_w_supply",
                "w_workforce": "crs_w_workforce",
                "w_demand": "crs_w_demand",
            }
            res = {}
            for k, v in data.items():
                target_key = mapping.get(k, k)
                res[target_key] = v
            return res
        return data

    @model_validator(mode="after")
    def validate_simplex_equality(self) -> PolicyCreate:
        """Enforces simplex constraint: crs_w_supply + crs_w_workforce + crs_w_demand = 1.0."""
        total = round(self.crs_w_supply + self.crs_w_workforce + self.crs_w_demand, 6)
        if abs(total - 1.0) > 1e-5:
            raise ValueError(
                f"CRS domain weights must satisfy simplex equality sum = 1.0; "
                f"got {self.crs_w_supply} + {self.crs_w_workforce} + {self.crs_w_demand} = {total}"
            )
        return self

    @property
    def asm_001_delay_penalty(self) -> float:
        return self.late_penalty_rate

    @property
    def asm_002_expedite_fee(self) -> float:
        return self.expedite_fee

    @property
    def asm_003_cancellation_factor(self) -> float:
        return self.stockout_churn_factor

    @property
    def asm_004_replacement_cost(self) -> float:
        return self.replacement_cost

    @property
    def asm_005_overtime_rate(self) -> float:
        return self.overtime_wage_rate

    @property
    def w_supply(self) -> float:
        return self.crs_w_supply

    @property
    def w_workforce(self) -> float:
        return self.crs_w_workforce

    @property
    def w_demand(self) -> float:
        return self.crs_w_demand


class PolicyResponse(BaseSchema):
    """Read DTO for an assumption policy."""
    id: uuid.UUID
    name: str
    version_number: int
    description: Optional[str] = None
    late_penalty_rate: float
    expedite_fee: float
    stockout_churn_factor: float
    replacement_cost: float
    overtime_wage_rate: float
    order_scaling_factor: float = 1.0
    planning_cycle_days: int = 30
    crs_w_supply: float
    crs_w_workforce: float
    crs_w_demand: float
    tau_risk: float
    cogs_ratio: float
    created_at: datetime
    is_active: bool = True

    # Aliases matching ASM convention
    @property
    def asm_001_delay_penalty(self) -> float:
        return self.late_penalty_rate

    @property
    def asm_002_expedite_fee(self) -> float:
        return self.expedite_fee

    @property
    def asm_003_cancellation_factor(self) -> float:
        return self.stockout_churn_factor

    @property
    def asm_004_replacement_cost(self) -> float:
        return self.replacement_cost

    @property
    def asm_005_overtime_rate(self) -> float:
        return self.overtime_wage_rate

    @property
    def w_supply(self) -> float:
        return self.crs_w_supply

    @property
    def w_workforce(self) -> float:
        return self.crs_w_workforce

    @property
    def w_demand(self) -> float:
        return self.crs_w_demand
