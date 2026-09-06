"""
Scenario & Version Pydantic v2 Schemas.
Enforces Gate E validation boundaries on what-if scenario levers,
version immutability representation, and ORM entity serialization.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
import uuid

from pydantic import Field, field_validator, computed_field, model_validator

from backend.app.schemas.common import BaseRequest, BaseSchema
from src.scenario.schema import ScenarioLevers


VALID_SHIPPING_MODES = {"Standard Class", "Second Class", "First Class", "Same Day"}


class ScenarioLeversSchema(BaseRequest):
    """
    Strongly-typed, boundary-checked what-if scenario levers.
    Enforces Gate E validation rules matching the analytical core constraints.
    """
    demand_growth_pct: float = Field(
        default=0.0,
        ge=-50.0,
        le=100.0,
        description="Hypothetical retail demand growth shock percentage [-50%, +100%]"
    )
    promo_active: bool = Field(
        default=False,
        description="Toggle for promotional campaign activation"
    )
    scheduled_days_offset: int = Field(
        default=0,
        ge=-3,
        le=3,
        description="Supply chain delivery lead time schedule offset in days [-3, +3]"
    )
    shipping_mode_override: Optional[str] = Field(
        default=None,
        description="Optional forced logistics shipping mode override"
    )
    overtime_workforce_pct: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Target percentage of workforce operating with mandatory overtime [0%, 100%]"
    )
    salary_hike_override: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=50.0,
        description="Optional percentage salary increase override [0%, 50%]"
    )
    epistemic_tier: Literal["ASSUMED"] = "ASSUMED"

    @field_validator("shipping_mode_override")
    @classmethod
    def validate_shipping_mode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in VALID_SHIPPING_MODES:
            raise ValueError(
                f"Invalid shipping_mode_override '{v}'. Allowed modes: {sorted(VALID_SHIPPING_MODES)}"
            )
        return v

    def to_scenario_levers(self) -> ScenarioLevers:
        """Converts DTO to domain ScenarioLevers model excluding epistemic classification."""
        return ScenarioLevers(**self.model_dump(exclude={"epistemic_tier"}))


class ScenarioCreate(BaseRequest):
    """Payload for creating a new business scenario."""
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Descriptive scenario title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional detailed context or justification for this scenario"
    )
    initial_levers: Optional[ScenarioLeversSchema] = Field(
        default=None,
        description="Optional initial lever parameters to seed version 1"
    )


class ScenarioUpdate(BaseRequest):
    """
    Payload for updating an existing scenario.
    Updating levers triggers Gate G: Version Immutability (increments version).
    """
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200,
        description="Updated scenario title"
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Updated scenario description"
    )
    levers: Optional[ScenarioLeversSchema] = Field(
        default=None,
        description="New lever parameter configuration; creates an incremented immutable version"
    )
    new_levers: Optional[ScenarioLeversSchema] = Field(
        default=None,
        description="Alias for levers"
    )

    @model_validator(mode="before")
    @classmethod
    def unify_levers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "new_levers" in data and "levers" not in data:
                data["levers"] = data["new_levers"]
        return data


class ScenarioVersionResponse(BaseSchema):
    """Read DTO for an immutable scenario version."""
    id: uuid.UUID
    scenario_id: uuid.UUID
    version_number: int
    demand_growth_pct: float
    promo_active: bool
    scheduled_days_offset: int
    shipping_mode_override: Optional[str] = None
    overtime_workforce_pct: float
    salary_hike_override: Optional[float] = None
    unit_price: float = 1.0
    created_at: datetime
    is_active: bool = True

    @property
    def levers(self) -> ScenarioLeversSchema:
        """Helper extracting structured levers."""
        return ScenarioLeversSchema(
            demand_growth_pct=self.demand_growth_pct,
            promo_active=self.promo_active,
            scheduled_days_offset=self.scheduled_days_offset,
            shipping_mode_override=self.shipping_mode_override,
            overtime_workforce_pct=self.overtime_workforce_pct,
            salary_hike_override=self.salary_hike_override,
        )


class ScenarioResponse(BaseSchema):
    """Read DTO for a scenario container."""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    is_archived: bool
    created_at: datetime
    updated_at: datetime
    versions: List[ScenarioVersionResponse] = Field(default_factory=list)

    @computed_field
    @property
    def latest_version(self) -> Optional[ScenarioVersionResponse]:
        """Returns the latest ScenarioVersion if versions exist."""
        return self.versions[-1] if self.versions else None
