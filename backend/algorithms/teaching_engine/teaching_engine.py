"""
Teaching Engine.

Transforms Educational Intelligence outputs into a structured
Teaching Context consumed by the AI Service Layer.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from backend.algorithms.adaptive_engine.adaptive_decision_engine import (
    AdaptiveDecision,
    Difficulty,
)
from backend.algorithms.irt.estimator import AbilityCategory
from backend.algorithms.mastery_engine import MasteryLevel
from backend.algorithms.teaching_engine.teaching_strategy_engine import (
    TeachingStrategy,
    select_teaching_strategy,
)


@dataclass(frozen=True)
class TeachingContextData:
    """
    Structured Teaching Context produced by Teaching Intelligence.

    This is the pedagogical decision layer. It does not generate
    natural-language instructional content.
    """

    topic_id: uuid.UUID | None
    learning_objective: str | None
    teaching_strategy: TeachingStrategy
    difficulty: Difficulty
    mastery_level: MasteryLevel
    ability_category: AbilityCategory
    weak_concepts: tuple[str, ...]
    recommended_activity: str
    assessment_required: bool


def generate_teaching_context(
    *,
    decision: AdaptiveDecision,
    mastery_level: MasteryLevel,
    ability_category: AbilityCategory,
    weak_concepts: list[str] | tuple[str, ...] | None = None,
) -> TeachingContextData:
    """
    Generate Teaching Context from an Adaptive Decision and learner state.

    The Adaptive Decision answers WHAT comes next.
    This function answers HOW that next learning activity should be taught.
    """

    strategy = select_teaching_strategy(decision.next_action)

    return TeachingContextData(
        topic_id=decision.topic_id,
        learning_objective=decision.learning_objective,
        teaching_strategy=strategy,
        difficulty=decision.difficulty,
        mastery_level=mastery_level,
        ability_category=ability_category,
        weak_concepts=tuple(weak_concepts or ()),
        recommended_activity=decision.next_action.value,
        assessment_required=decision.assessment_required,
    )