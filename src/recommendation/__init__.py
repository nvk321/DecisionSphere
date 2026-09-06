"""
DecisionSphere — Phase 8 Recommendation Engine Package
Exports validated schemas, Composite Risk Score calculator, trigger rules, and trade-off orchestrator.
"""

from src.recommendation.schema import (
    RecommendationSeverity,
    StrategicDecisionCategory,
    CRSWeights,
    CompositeRiskBreakdown,
    StrategicAction,
    TradeOffEvaluation,
    RecommendationResult,
)
from src.recommendation.crs import CompositeRiskEngine
from src.recommendation.rules import RuleEvaluator
from src.recommendation.engine import RecommendationEngine

__all__ = [
    "RecommendationSeverity",
    "StrategicDecisionCategory",
    "CRSWeights",
    "CompositeRiskBreakdown",
    "StrategicAction",
    "TradeOffEvaluation",
    "RecommendationResult",
    "CompositeRiskEngine",
    "RuleEvaluator",
    "RecommendationEngine",
]
