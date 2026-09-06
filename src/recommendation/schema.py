"""
DecisionSphere — Phase 8 Recommendation Engine Pydantic v2 Data Contracts
Defines strictly typed, validated schemas for Composite Risk Score (CRS), strategic actions,
lexicographic trade-off evaluation, and comprehensive recommendation output results.

Epistemic Tier: RECOMMENDED (Tier 6)
Governing Mandate:
"Recommendations synthesize empirical predictions, operational propagations, and deterministic
accounting calculations into rule-grounded strategic actions; they do not claim mathematical
optimality or guarantee real-world outcomes."
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict


class RecommendationSeverity(str, Enum):
    """Execution priority and urgency for recommended actions."""
    CRITICAL = "CRITICAL"    # Immediate margin erosion or systemic operational failure
    HIGH = "HIGH"            # Severe delivery risk, acute attrition, or high operational strain
    MEDIUM = "MEDIUM"        # Buffer degradation, SLA compression, or retention advisory
    LOW = "LOW"              # Minor operational advisory or non-urgent optimization


class StrategicDecisionCategory(str, Enum):
    """Lexicographic multi-objective scenario classification."""
    PROCEED = "PROCEED"                                  # DeltaProfit > 0 AND CRS <= tau_risk (50.0)
    PROCEED_WITH_MITIGATIONS = "PROCEED_WITH_MITIGATIONS" # DeltaProfit > 0 AND CRS > tau_risk (50.0)
    REJECT_RESTRUCTURE = "REJECT_RESTRUCTURE"            # DeltaProfit <= 0 (value destruction)


class CRSWeights(BaseModel):
    """
    Phase 8 Composite Risk Score domain weighting configuration (ASM-009).
    Enforces the simplex constraint: w_supply + w_workforce + w_demand = 1.0, with w_i >= 0.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    w_supply: float = Field(
        0.40, ge=0.0, le=1.0, description="Weight on supply chain late-delivery risk sub-index"
    )
    w_workforce: float = Field(
        0.40, ge=0.0, le=1.0, description="Weight on workforce attrition & overtime sub-index"
    )
    w_demand: float = Field(
        0.20, ge=0.0, le=1.0, description="Weight on demand volatility & stockout sub-index"
    )

    @field_validator("w_demand")
    @classmethod
    def validate_simplex(cls, v: float, info) -> float:
        w_s = info.data.get("w_supply", 0.40)
        w_w = info.data.get("w_workforce", 0.40)
        total = round(w_s + w_w + v, 6)
        if abs(total - 1.0) > 1e-5:
            raise ValueError(f"CRS weights must sum to 1.0; got {w_s} + {w_w} + {v} = {total}")
        return v


class CompositeRiskBreakdown(BaseModel):
    """
    Field-level audit trail and decomposition of the Composite Risk Score (CRS).
    Purely operational multi-criteria index measuring aggregate execution strain.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    supply_chain_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Logistics delivery risk sub-index [0, 100]"
    )
    workforce_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Workforce attrition and overtime sub-index [0, 100]"
    )
    demand_execution_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Fulfillment and stockout churn sub-index [0, 100]"
    )
    composite_risk_score: float = Field(
        ..., ge=0.0, le=100.0, description="Weighted aggregate operational strain [0, 100]"
    )
    risk_level: Literal["LOW", "MODERATE", "HIGH", "SEVERE"] = Field(
        ..., description="Qualitative categorical classification of aggregate risk"
    )
    weights_applied: Dict[str, float] = Field(
        ..., description="Exact weights applied to sub-indices (ASM-009)"
    )
    epistemic_tier: Literal["CALCULATED"] = "CALCULATED"


class StrategicAction(BaseModel):
    """
    Individual prioritized, rule-grounded strategic intervention.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    action_id: str = Field(..., description="Deterministic action code, e.g. ACT-SC-001")
    domain: Literal["Supply Chain", "Workforce", "Demand", "Financial / Strategic", "Executive Governance"]
    severity: RecommendationSeverity
    title: str = Field(..., description="Short action summary")
    description: str = Field(..., description="Specific operational mitigation directive")
    trigger_rule_id: str = Field(..., description="ID of triggering rule, e.g. RULE-01")
    triggering_condition: str = Field(..., description="Formal mathematical condition satisfied")
    grounding_evidence: Dict[str, Any] = Field(..., description="Exact quantitative metrics and probabilities cited")
    expected_trade_off: str = Field(..., description="Epistemic and non-causal trade-off disclosure")
    epistemic_tier: Literal["RECOMMENDED"] = "RECOMMENDED"


class TradeOffEvaluation(BaseModel):
    """
    Structured summary of cross-domain trade-offs and decision rationale.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    decision_category: StrategicDecisionCategory
    net_profit_delta_usd: float = Field(..., description="Unrounded bottom-line profit delta")
    composite_risk_score: float = Field(..., description="Operational Composite Risk Score")
    decision_rationale: str = Field(..., description="Detailed explanation of the lexicographic evaluation")
    primary_vulnerability: str = Field(..., description="Dominant bottleneck or operational risk vector")
    competing_priorities: List[str] = Field(..., description="Summary of conflicting cross-domain tensions")


class RecommendationResult(BaseModel):
    """
    Complete, validated recommendation and trade-off analysis result for a scenario run.
    Guarantees:
    - Pure rule-grounded and lexicographic synthesis.
    - Zero causal claims.
    - Explicit 6-tier epistemic hierarchy demarcation.
    """
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_id: str = Field(..., description="Unique scenario identifier propagated from Phase 6/7")
    scenario_name: str = Field(..., description="Human-readable scenario title")
    decision_category: StrategicDecisionCategory
    composite_risk: CompositeRiskBreakdown
    trade_off_evaluation: TradeOffEvaluation
    recommended_actions: List[StrategicAction] = Field(
        ..., description="Deterministically prioritized strategic actions"
    )
    executive_briefing: str = Field(..., description="Epistemic, non-causal executive synthesis")
    timestamp: str = Field(..., description="ISO 8601 evaluation timestamp")
    epistemic_tier: Literal["RECOMMENDED"] = "RECOMMENDED"
