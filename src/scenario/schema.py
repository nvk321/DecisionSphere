"""
DecisionSphere — Phase 6 Scenario Engine Pydantic v2 Data Contracts
Defines strictly typed, validated schemas for scenario levers, operational assumptions,
domain predictions, cryptographic provenance, and multi-domain execution results.
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


VALID_SHIPPING_MODES = {"Standard Class", "Second Class", "First Class", "Same Day"}


class ScenarioLevers(BaseModel):
    """
    User-specified strategic and operational levers defining a hypothetical scenario.
    All fields have explicit units and strict bounds.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: Optional[str] = Field(
        None,
        description="Optional unique identifier; if omitted, deterministically derived from canonical parameters."
    )
    scenario_name: str = Field(
        "Custom Scenario",
        description="Human-readable scenario title"
    )
    demand_growth_pct: float = Field(
        0.0,
        ge=-50.0,
        le=100.0,
        description="Hypothetical retail demand volume shock percentage (%)"
    )
    promo_active: bool = Field(
        False,
        description="Whether a retail promotional campaign is active (Promo=1)"
    )
    scheduled_days_offset: int = Field(
        0,
        ge=-3,
        le=3,
        description="Dispatch lead-time SLA offset in days (negative = compressed SLA; positive = relaxed SLA)"
    )
    shipping_mode_override: Optional[str] = Field(
        None,
        description="Optional freight class override: 'Standard Class', 'Second Class', 'First Class', 'Same Day'"
    )
    overtime_workforce_pct: float = Field(
        0.0,
        ge=0.0,
        le=100.0,
        description="Target percentage of the workforce mandated to work overtime (%)"
    )
    salary_hike_override: Optional[float] = Field(
        None,
        ge=0.0,
        le=35.0,
        description="Optional compensation hike percentage (%) applied to PercentSalaryHike"
    )

    @field_validator("shipping_mode_override")
    @classmethod
    def validate_shipping_mode(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() not in VALID_SHIPPING_MODES:
            raise ValueError(
                f"Invalid shipping_mode_override '{v}'. Must be one of {sorted(VALID_SHIPPING_MODES)} or None."
            )
        return v.strip() if v is not None else None


class ScenarioAssumptions(BaseModel):
    """
    Phase 6 operational assumptions.
    Strictly segregated from Phase 7 financial assumptions (ASM-001 through ASM-005).
    Passing any extra or financial parameter raises ValidationError.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    # ASM-006: Overtime-induced satisfaction decrement
    asm_006_wlb_decrement: int = Field(
        -1,
        ge=-2,
        le=0,
        description="ASM-006: WorkLifeBalance ordinal survey decrement under overtime {-2, -1, 0}"
    )
    # ASM-007: Order-volume scaling factor
    asm_007_volume_scaling: float = Field(
        1.00,
        ge=0.50,
        le=2.00,
        description="ASM-007: Dimensionless order-to-sales scaling factor (orders / sales unit) [0.5, 2.0]"
    )
    # ASM-008: Temporal cycle alignment factor
    asm_008_cycle_days: int = Field(
        30,
        ge=14,
        le=90,
        description="ASM-008: Operational planning cycle length in days [14, 90]"
    )


class DomainProvenance(BaseModel):
    """
    Per-field cryptographic and methodological audit trail for a domain inference.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_model: str = Field(..., description="Predictive module name (Demand, Supply Chain, Workforce)")
    model_artifact: str = Field(..., description="Path to serialized joblib model file")
    artifact_sha256: str = Field(..., description="Cryptographic SHA-256 fingerprint of the model file")
    epistemic_tier: str = Field("PREDICTED", description="Epistemic hierarchy tier")
    input_modifications: Dict[str, Any] = Field(default_factory=dict, description="Feature overrides applied")
    assumptions_applied: List[str] = Field(default_factory=list, description="IDs of applied assumptions (e.g. ASM-006)")
    causal_claim: bool = Field(False, description="Strict invariant: False (non-causal statistical association)")
    calculation_description: str = Field(..., description="Mathematical and methodological basis")


class DomainPredictionResult(BaseModel):
    """
    Container for baseline, scenario, and delta values with provenance and threshold classifications.
    Preserves continuous full-precision IEEE 754 floating-point values.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    domain: str = Field(..., description="Domain name ('Demand', 'Supply Chain', 'Workforce')")
    unit: str = Field(..., description="Physical or statistical unit of measurement")
    baseline_value: float = Field(..., description="Unrounded IEEE 754 baseline prediction")
    scenario_value: float = Field(..., description="Unrounded IEEE 754 scenario prediction")
    delta_value: float = Field(..., description="Unrounded delta: scenario_value - baseline_value")
    decision_threshold: Optional[float] = Field(None, description="Classification threshold tau* (if applicable)")
    baseline_class: Optional[int] = Field(None, description="Binary classification at baseline (if applicable)")
    scenario_class: Optional[int] = Field(None, description="Binary classification under scenario (if applicable)")
    classification_change_statement: Optional[str] = Field(
        None, description="Non-causal interpretation of threshold crossing"
    )
    provenance: DomainProvenance


class WorkforceCohortSummary(BaseModel):
    """
    Structured summary of deterministic overtime assignment across the evaluated workforce population.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    total_headcount: int = Field(..., description="Number of evaluated employees in the cohort")
    baseline_overtime_count: int = Field(..., description="Number of employees with OverTime='Yes' at baseline")
    scenario_overtime_count: int = Field(..., description="Number of employees with OverTime='Yes' under scenario")
    overtime_switched_count: int = Field(..., description="Number of employees switched from 'No' to 'Yes'")
    target_overtime_percentage: float = Field(..., description="Target overtime percentage requested by user")
    actual_scenario_overtime_percentage: float = Field(..., description="Achieved overtime percentage in cohort")
    wlb_decrement_applied: int = Field(..., description="ASM-006 WorkLifeBalance decrement applied to overtime rows")
    epistemic_tier: str = Field("PROPAGATED", description="Epistemic tier for operational feature assignment")


class ScenarioRunResult(BaseModel):
    """
    Complete multi-domain scenario run result.
    Guarantees:
    - Zero financial fields (revenue, cost, profit prohibited in Phase 6).
    - Bitwise numerical reproducibility.
    - Explicit 6-tier epistemic demarcation.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(..., description="Unique deterministic scenario identifier")
    scenario_name: str = Field(..., description="Human-readable scenario title")
    levers: ScenarioLevers
    assumptions: ScenarioAssumptions
    demand_result: DomainPredictionResult
    supply_chain_result: DomainPredictionResult
    workforce_result: DomainPredictionResult
    workforce_cohort_summary: WorkforceCohortSummary
    normalized_order_volume: float = Field(
        ...,
        description="Normalized dispatch order volume calculated via ASM-007 and ASM-008"
    )
    execution_timestamp: str = Field(..., description="ISO 8601 execution timestamp (audit trail only)")
    epistemic_tier: Literal["PROPAGATED"] = "PROPAGATED"
    interpretation: str = Field(..., description="Epistemic and non-causal summary of the scenario run")
