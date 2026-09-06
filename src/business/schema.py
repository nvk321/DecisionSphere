"""
DecisionSphere — Phase 7 Business Impact Analysis Pydantic v2 Data Contracts
Defines strictly typed, validated schemas for financial assumptions (ASM-001 through ASM-005),
financial line item provenance, financial line items, break-even summaries, and comprehensive
business impact simulation results.

Epistemic Tier: CALCULATED (Tier 5)
Governing Mandate:
"Business Impact Analysis converts scenario-derived model outputs into transparent financial
calculations under explicitly declared assumptions; it does not convert statistical predictions
into claims about guaranteed real-world outcomes."
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


EXPEDITED_SHIPPING_MODES = {"First Class", "Same Day"}
REGULAR_SHIPPING_MODES = {"Standard Class", "Second Class"}


class BusinessAssumptions(BaseModel):
    """
    Phase 7 financial and operational cost coupling parameters.
    Governed strictly by ASM-001 through ASM-005 and audited financial constants.
    Rejects Phase 6 operational parameters (ASM-006, ASM-007, ASM-008) and extra fields via extra='forbid'.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    # ASM-001: Contractual late-delivery penalty per delayed delivered shipment
    asm_001_delay_penalty: float = Field(
        25.00,
        ge=10.00,
        le=60.00,
        description="ASM-001: Contractual late delivery penalty ($/delayed delivered order) [10.00, 60.00]"
    )
    # ASM-002: Expedited freight shipping surcharge per order
    asm_002_expedite_fee: float = Field(
        15.00,
        ge=5.00,
        le=35.00,
        description="ASM-002: Expedited freight air shipping surcharge ($/expedited order) [5.00, 35.00]"
    )
    # ASM-003: Late-order cancellation / churn elasticity factor
    asm_003_cancellation_factor: float = Field(
        0.15,
        ge=0.05,
        le=0.40,
        description="ASM-003: Dimensionless customer churn cancellation factor for late orders [0.05, 0.40]"
    )
    # ASM-004: Employee turnover replacement / re-hiring cost
    asm_004_replacement_cost: float = Field(
        30000.00,
        ge=15000.00,
        le=60000.00,
        description="ASM-004: Employee turnover replacement & onboarding cost ($/departed employee) [15k, 60k]"
    )
    # ASM-005: Overtime hourly labor rate
    asm_005_overtime_rate: float = Field(
        45.00,
        ge=30.00,
        le=75.00,
        description="ASM-005: Overtime hourly labor rate ($/overtime hour) [30.00, 75.00]"
    )
    # Cost of Goods Sold (COGS) ratio on realized sales revenue
    cogs_ratio: float = Field(
        0.60,
        ge=0.30,
        le=0.90,
        description="Cost of Goods Sold (COGS) as a percentage of realized revenue [0.30, 0.90]"
    )
    # Selling price per sales unit
    unit_price: float = Field(
        1.00,
        ge=0.50,
        le=50.00,
        description="Average monetary selling price per sales unit ($/unit) [0.50, 50.00]"
    )
    # Overtime hours worked per active worker per planning cycle
    overtime_hours_per_worker: float = Field(
        20.0,
        ge=5.0,
        le=60.0,
        description="Standard overtime hours worked per worker per planning cycle [5.0, 60.0]"
    )
    # Historical baseline fraction of expedited freight orders
    baseline_expedited_fraction: float = Field(
        0.05,
        ge=0.0,
        le=1.0,
        description="Baseline historical fraction of orders shipped via expedited freight [0.0, 1.0]"
    )


class FinancialLineItemProvenance(BaseModel):
    """
    Field-level audit trail for a deterministic financial line item.
    Enforces epistemic tier CALCULATED, explicit formula traceability, and applied assumptions.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    epistemic_tier: Literal["CALCULATED"] = "CALCULATED"
    formula: str = Field(..., description="Explicit algebraic formula used for calculation")
    assumptions_applied: List[str] = Field(
        default_factory=list,
        description="IDs of applied assumptions (e.g. ['ASM-001', 'ASM-003'])"
    )
    unit: str = Field("USD", description="Dimensional monetary or percentage unit")
    calculation_statement: str = Field(..., description="Plain-language description of calculation mechanics")


class FinancialLineItem(BaseModel):
    """
    Container for baseline, scenario, and delta accounting of a single financial line item.
    Preserves continuous full-precision IEEE 754 floating-point numbers.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str = Field(..., description="Accounting line item name")
    baseline_value: float = Field(..., description="Unrounded baseline financial value")
    scenario_value: float = Field(..., description="Unrounded scenario financial value")
    delta_value: float = Field(..., description="Unrounded delta value (scenario_value - baseline_value)")
    unit: str = Field("USD", description="Monetary unit (default 'USD')")
    provenance: FinancialLineItemProvenance


class BreakEvenAnalysis(BaseModel):
    """
    Summary of break-even parameter thresholds identifying where net incremental profit reaches zero.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    break_even_delay_penalty: Optional[float] = Field(
        None, description="Contractual delay penalty ($/order) where DeltaProfit = 0"
    )
    break_even_replacement_cost: Optional[float] = Field(
        None, description="Employee turnover replacement cost ($/employee) where DeltaProfit = 0"
    )
    break_even_overtime_rate: Optional[float] = Field(
        None, description="Overtime hourly labor rate ($/hour) where DeltaProfit = 0"
    )
    break_even_cogs_ratio: Optional[float] = Field(
        None, description="COGS ratio on realized revenue where DeltaProfit = 0"
    )
    sensitivity_summary: Dict[str, Any] = Field(
        default_factory=dict, description="Summary of parameter sensitivities and margins"
    )


class BusinessImpactResult(BaseModel):
    """
    Complete, validated financial impact result evaluated from a ScenarioRunResult.
    Guarantees:
    - Pure financial accounting line items (revenue, COGS, supply chain, workforce, net profit delta).
    - Zero composite risk score (deferred to Phase 8).
    - Unrounded 64-bit float precision.
    - Explicit epistemic tier CALCULATED.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(..., description="Unique scenario identifier propagated from Phase 6")
    scenario_name: str = Field(..., description="Human-readable scenario title")
    gross_revenue: FinancialLineItem = Field(..., description="Gross revenue before fulfillment loss")
    realized_revenue: FinancialLineItem = Field(..., description="Realized revenue after delay fulfillment churn")
    cogs: FinancialLineItem = Field(..., description="Cost of Goods Sold on realized revenue (Option B)")
    gross_margin: FinancialLineItem = Field(..., description="Gross contribution margin (Realized Revenue - COGS)")
    supply_chain_cost: FinancialLineItem = Field(..., description="Supply chain disruption cost (delay + expedite)")
    workforce_cost: FinancialLineItem = Field(..., description="Workforce operational cost (turnover + overtime)")
    total_operational_cost: FinancialLineItem = Field(
        ..., description="Total operational cost (COGS + Supply Chain + Workforce)"
    )
    net_profit_delta: float = Field(
        ..., description="Net incremental scenario profit delta (Delta Realized Revenue - Delta Total Cost)"
    )
    is_profitable_scenario: bool = Field(
        ..., description="True if net_profit_delta > 0, False otherwise"
    )
    epistemic_tier: Literal["CALCULATED"] = "CALCULATED"
    break_even_analysis: BreakEvenAnalysis
    statement: str = Field(..., description="Epistemic and non-causal executive summary statement")
    timestamp: str = Field(..., description="ISO 8601 evaluation timestamp")
