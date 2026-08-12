"""
Adaptive Decision Engine.

Synthesizes the top-priority Recommendation (from recommendation_engine.py)
and the next unencountered curriculum topic (from learning_path_engine.py)
into the single documented decision shape (Section 16's design
suggestion example): next_action, topic_id, difficulty, reason,
ai_support, assessment_required, learning_objective.

Rule mapping from Section 11/12's documented decision logic to the
seven documented Decision Categories (Section 8):

    Revision recommendation    -> "review_topic"
    AI Support recommendation  -> "ai_explanation" (ai_support=True)
    Practice recommendation    -> "practice"       (assessment_required=True)
    Progression recommendation -> "advance"
    Challenge recommendation   -> "assessment"      (difficulty="hard", assessment_required=True)
    No evidence yet, but a next curriculum topic exists -> "learn_new_topic"
    No evidence and no next topic                       -> "advance" (nothing left to recommend)

`difficulty` is a categorical label ("easy"/"medium"/"hard"), matching
the documented example's string value, derived from the learner's IRT
ability category (backend.algorithms.irt.estimator.AbilityCategory) —
Beginner->easy, Intermediate->medium, Advanced->hard — since no other
documented difficulty-labeling scheme exists.

Generating and persisting a Teaching Context in response to this
decision is explicitly Teaching Intelligence's responsibility
(Module 9), which this module excludes; this engine only computes and
returns the decision.

Reference: 04_ALGORITHM_DESIGN/06_Adaptive_Decision_Engine.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from backend.algorithms.adaptive_engine.recommendation_engine import (
    RecommendationCandidate,
    RecommendationType,
)
from backend.algorithms.irt.estimator import AbilityCategory


class NextAction(str, Enum):
    """The documented Decision Categories (Section 8) this engine can select."""

    LEARN_NEW_TOPIC = "learn_new_topic"
    REVIEW_TOPIC = "review_topic"
    PRACTICE = "practice"
    ASSESSMENT = "assessment"
    AI_EXPLANATION = "ai_explanation"
    ADVANCE = "advance"


class Difficulty(str, Enum):
    """Categorical difficulty label, matching the documented example's string value."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True)
class AdaptiveDecision:
    """The documented decision output shape (Section 16)."""

    next_action: NextAction
    topic_id: uuid.UUID | None
    difficulty: Difficulty
    reason: str
    ai_support: bool
    assessment_required: bool
    learning_objective: str | None


_ACTION_BY_RECOMMENDATION_TYPE = {
    RecommendationType.REVISION: NextAction.REVIEW_TOPIC,
    RecommendationType.AI_SUPPORT: NextAction.AI_EXPLANATION,
    RecommendationType.PRACTICE: NextAction.PRACTICE,
    RecommendationType.PROGRESSION: NextAction.ADVANCE,
    RecommendationType.CHALLENGE: NextAction.ASSESSMENT,
}

_DIFFICULTY_BY_ABILITY = {
    AbilityCategory.BEGINNER: Difficulty.EASY,
    AbilityCategory.INTERMEDIATE: Difficulty.MEDIUM,
    AbilityCategory.ADVANCED: Difficulty.HARD,
}


def decide(
    *,
    top_recommendation: RecommendationCandidate | None,
    next_unencountered_topic_id: uuid.UUID | None,
    ability_category: AbilityCategory,
    learning_objective: str | None,
) -> AdaptiveDecision:
    """
    Selects the single highest-priority next action.

    `top_recommendation` is the first (most urgent) item from
    `recommendation_engine.generate_recommendations()` — this engine
    does not recompute mastery evidence itself, consistent with the
    documented pipeline order (Recommendation Engine -> Adaptive
    Decision Engine).
    """
    difficulty = _DIFFICULTY_BY_ABILITY[ability_category]

    if top_recommendation is not None:
        action = _ACTION_BY_RECOMMENDATION_TYPE[top_recommendation.recommendation_type]
        if top_recommendation.recommendation_type == RecommendationType.CHALLENGE:
            difficulty = Difficulty.HARD
        return AdaptiveDecision(
            next_action=action,
            topic_id=top_recommendation.topic_id,
            difficulty=difficulty,
            reason=top_recommendation.reason,
            ai_support=action == NextAction.AI_EXPLANATION,
            assessment_required=action in (NextAction.PRACTICE, NextAction.ASSESSMENT),
            learning_objective=learning_objective,
        )

    if next_unencountered_topic_id is not None:
        return AdaptiveDecision(
            next_action=NextAction.LEARN_NEW_TOPIC,
            topic_id=next_unencountered_topic_id,
            difficulty=difficulty,
            reason="No prior evidence for this topic — beginning new topic.",
            ai_support=False,
            assessment_required=False,
            learning_objective=learning_objective,
        )

    return AdaptiveDecision(
        next_action=NextAction.ADVANCE,
        topic_id=None,
        difficulty=difficulty,
        reason="No pending recommendations or new topics available.",
        ai_support=False,
        assessment_required=False,
        learning_objective=None,
    )