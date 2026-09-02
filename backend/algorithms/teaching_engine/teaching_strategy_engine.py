"""
Teaching Strategy Engine.

Converts an Adaptive Decision into a pedagogically appropriate
teaching strategy.

Educational Intelligence decides WHAT the learner should do.
Teaching Intelligence decides HOW that need should be taught.
"""

from __future__ import annotations

from enum import Enum

from backend.algorithms.adaptive_engine.adaptive_decision_engine import (
    NextAction,
)


class TeachingStrategy(str, Enum):
    """Teaching strategies selected by Teaching Intelligence."""

    CONCEPT_INTRODUCTION = "Concept Introduction"
    GUIDED_REVISION = "Guided Revision"
    GUIDED_PRACTICE = "Guided Practice"
    ASSESSMENT = "Assessment"
    PERSONALIZED_EXPLANATION = "Personalized Explanation"
    PROGRESSION = "Progression"


_STRATEGY_BY_ACTION: dict[NextAction, TeachingStrategy] = {
    NextAction.LEARN_NEW_TOPIC: TeachingStrategy.CONCEPT_INTRODUCTION,
    NextAction.REVIEW_TOPIC: TeachingStrategy.GUIDED_REVISION,
    NextAction.PRACTICE: TeachingStrategy.GUIDED_PRACTICE,
    NextAction.ASSESSMENT: TeachingStrategy.ASSESSMENT,
    NextAction.AI_EXPLANATION: TeachingStrategy.PERSONALIZED_EXPLANATION,
    NextAction.ADVANCE: TeachingStrategy.PROGRESSION,
}


def select_teaching_strategy(action: NextAction) -> TeachingStrategy:
    """
    Select the teaching strategy for an adaptive decision.

    This function contains pedagogical reasoning and therefore belongs
    to Teaching Intelligence rather than the AI generation layer.
    """
    return _STRATEGY_BY_ACTION[action]