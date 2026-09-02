from backend.algorithms.adaptive_engine.adaptive_decision_engine import NextAction
from backend.algorithms.teaching_engine.teaching_strategy_engine import (
    TeachingStrategy,
    select_teaching_strategy,
)


def test_new_topic_uses_concept_introduction():
    assert (
        select_teaching_strategy(NextAction.LEARN_NEW_TOPIC)
        == TeachingStrategy.CONCEPT_INTRODUCTION
    )


def test_review_uses_guided_revision():
    assert (
        select_teaching_strategy(NextAction.REVIEW_TOPIC)
        == TeachingStrategy.GUIDED_REVISION
    )


def test_practice_uses_guided_practice():
    assert (
        select_teaching_strategy(NextAction.PRACTICE)
        == TeachingStrategy.GUIDED_PRACTICE
    )


def test_assessment_uses_assessment_strategy():
    assert (
        select_teaching_strategy(NextAction.ASSESSMENT)
        == TeachingStrategy.ASSESSMENT
    )


def test_ai_explanation_uses_personalized_explanation():
    assert (
        select_teaching_strategy(NextAction.AI_EXPLANATION)
        == TeachingStrategy.PERSONALIZED_EXPLANATION
    )


def test_advance_uses_progression():
    assert (
        select_teaching_strategy(NextAction.ADVANCE)
        == TeachingStrategy.PROGRESSION
    )