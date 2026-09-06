"""
Sensitivity Analysis Pydantic v2 Schemas.
Handles discrete parameter sweep requests and response containers
for Experiment B (Response Curves) and Experiment D (Parametric Sensitivity).
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
import uuid

from pydantic import Field, field_validator, model_validator

from backend.app.schemas.common import BaseRequest, BaseSchema
from backend.app.schemas.scenario import ScenarioLeversSchema


VALID_FINANCIAL_PARAMS = {
    "asm_001_delay_penalty",
    "asm_002_expedite_fee",
    "asm_003_cancellation_factor",
    "asm_004_replacement_cost",
    "asm_005_overtime_rate",
    "cogs_ratio",
}


class DemandShockSweepRequest(BaseRequest):
    """Payload for Experiment B: Retail demand shock sweep."""
    base_levers: Optional[ScenarioLeversSchema] = Field(
        default=None,
        description="Base levers to anchor the sweep. Defaults to neutral baseline if omitted."
    )
    shock_percentages: Optional[List[float]] = Field(
        default=None,
        description="Discrete shock percentage multipliers to evaluate (e.g. [-20, -10, 0, 10, 20, 30])"
    )

    @field_validator("shock_percentages")
    @classmethod
    def validate_shocks(cls, v: Optional[List[float]]) -> Optional[List[float]]:
        if v is not None:
            for s in v:
                if s < -50.0 or s > 100.0:
                    raise ValueError(f"Shock percentage {s}% exceeds allowable range [-50%, +100%]")
        return v


class DemandShockSweepItem(BaseSchema):
    """Single discrete point on the demand response curve."""
    shock_pct: float
    demand_forecast: float
    late_delivery_risk: float
    workforce_attrition_risk: float
    epistemic_tier: str = "PREDICTED"


class FinancialSweepRequest(BaseRequest):
    """Payload for Experiment D: Financial coupling parameter 1D sweep."""
    scenario_version_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional scenario version ID. If omitted, uses neutral baseline levers."
    )
    policy_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional assumption policy ID. If omitted, uses default policy."
    )
    parameter_name: str = Field(
        ...,
        description="Coupling parameter to sweep (e.g. 'asm_001_delay_penalty', 'asm_004_replacement_cost')"
    )
    candidate_values: List[float] = Field(
        ...,
        min_length=1,
        description="Discrete parameter values to evaluate"
    )

    @field_validator("parameter_name")
    @classmethod
    def validate_param(cls, v: str) -> str:
        if v not in VALID_FINANCIAL_PARAMS:
            raise ValueError(
                f"Unknown financial parameter '{v}'. Allowed parameters: {sorted(VALID_FINANCIAL_PARAMS)}"
            )
        return v

    @model_validator(mode="after")
    def validate_candidate_bounds(self) -> FinancialSweepRequest:
        from src.business.sensitivity import PARAM_BOUNDS
        if self.parameter_name in PARAM_BOUNDS:
            low, high = PARAM_BOUNDS[self.parameter_name]
            for val in self.candidate_values:
                if val < low or val > high:
                    raise ValueError(
                        f"Candidate value {val} for '{self.parameter_name}' exceeds allowable bounds [{low}, {high}]"
                    )
        return self


class FinancialSweepItem(BaseSchema):
    """Single discrete point in a financial sensitivity sweep."""
    parameter_name: str
    value: float
    net_profit_delta: float
    is_profitable: bool
    epistemic_tier: str = "CALCULATED"


class CRSWeightsDTO(BaseRequest):
    """CRS simplex domain weight candidate."""
    w_supply: float = Field(..., ge=0.0, le=1.0)
    w_workforce: float = Field(..., ge=0.0, le=1.0)
    w_demand: float = Field(..., ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_simplex(self) -> CRSWeightsDTO:
        total = round(self.w_supply + self.w_workforce + self.w_demand, 6)
        if abs(total - 1.0) > 1e-5:
            raise ValueError(f"CRS weights must sum to 1.0; got {total}")
        return self


class CRSWeightSweepRequest(BaseRequest):
    """Payload for sweeping multiple CRS domain weighting combinations."""
    scenario_version_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional scenario version ID. If omitted, uses neutral baseline levers."
    )
    policy_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional assumption policy ID. If omitted, uses default policy."
    )
    candidate_weights: List[CRSWeightsDTO] = Field(
        ...,
        min_length=1,
        description="List of candidate simplex weight vectors"
    )
    tau_risk: float = Field(
        default=50.0,
        ge=0.0,
        le=100.0,
        description="Operational strain tolerance threshold"
    )


class CRSWeightSweepItem(BaseSchema):
    """Output for a single weight configuration in a CRS sweep."""
    w_supply: float
    w_workforce: float
    w_demand: float
    composite_risk_score: float
    risk_level: str
    decision_category: str
    epistemic_tier: str = "CALCULATED"


class FlipThresholdSearchRequest(BaseRequest):
    """Payload for finding parameter tipping points where decision flips."""
    scenario_version_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional scenario version ID. If omitted, uses neutral baseline levers."
    )
    policy_id: Optional[uuid.UUID] = Field(
        default=None,
        description="Optional assumption policy ID. If omitted, uses default policy."
    )
    parameter_name: str = Field(..., description="Target parameter to inspect")
    candidate_values: List[float] = Field(
        ...,
        min_length=2,
        description="Candidate values to search across (must be sorted ascending)"
    )

    @field_validator("parameter_name")
    @classmethod
    def validate_param(cls, v: str) -> str:
        if v not in VALID_FINANCIAL_PARAMS:
            raise ValueError(
                f"Unknown parameter '{v}'. Allowed parameters: {sorted(VALID_FINANCIAL_PARAMS)}"
            )
        return v

    @model_validator(mode="after")
    def validate_candidate_bounds(self) -> FlipThresholdSearchRequest:
        from src.business.sensitivity import PARAM_BOUNDS
        if self.parameter_name in PARAM_BOUNDS:
            low, high = PARAM_BOUNDS[self.parameter_name]
            for val in self.candidate_values:
                if val < low or val > high:
                    raise ValueError(
                        f"Candidate value {val} for '{self.parameter_name}' exceeds allowable bounds [{low}, {high}]"
                    )
        return self


class FlipThresholdResponse(BaseSchema):
    """Result of recommendation boundary flip analysis."""
    parameter_name: str
    flip_detected: bool
    flip_value: Optional[float] = None
    previous_category: Optional[str] = None
    new_category: Optional[str] = None
    net_profit_delta: Optional[float] = None
    composite_risk_score: Optional[float] = None
    epistemic_tier: str = "RECOMMENDED"
