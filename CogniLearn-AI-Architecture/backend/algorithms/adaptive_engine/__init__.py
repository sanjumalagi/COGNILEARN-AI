"""
Adaptive Engine Sub-Package.

Learning path generation, recommendation logic, and adaptive
next-action decisions — rule-based, per the documented design
(no numeric formulas specified for this layer).

Reference: 04_ALGORITHM_DESIGN/04_RECOMMENDATION_ENGINE_DESIGN.md
Reference: 04_ALGORITHM_DESIGN/05_LEARNING_PATH_ENGINE_DESIGN.md
Reference: 04_ALGORITHM_DESIGN/06_Adaptive_Decision_Engine.md
"""

from backend.algorithms.adaptive_engine.adaptive_decision_engine import (
    AdaptiveDecision,
    Difficulty,
    NextAction,
    decide,
)
from backend.algorithms.adaptive_engine.learning_path_engine import (
    PathStep,
    PathStepStatus,
    TopicMasteryEvidence,
    build_learning_path,
)
from backend.algorithms.adaptive_engine.recommendation_engine import (
    RecommendationCandidate,
    RecommendationType,
    TopicEvidence,
    generate_recommendations,
)

__all__ = [
    "AdaptiveDecision",
    "Difficulty",
    "NextAction",
    "decide",
    "PathStep",
    "PathStepStatus",
    "TopicMasteryEvidence",
    "build_learning_path",
    "RecommendationCandidate",
    "RecommendationType",
    "TopicEvidence",
    "generate_recommendations",
]