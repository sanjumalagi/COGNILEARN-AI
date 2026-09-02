import uuid

from backend.algorithms.adaptive_engine.adaptive_decision_engine import (
    AdaptiveDecision,
    Difficulty,
    NextAction,
)
from backend.algorithms.irt.estimator import AbilityCategory
from backend.algorithms.mastery_engine import MasteryLevel
from backend.algorithms.teaching_engine.teaching_engine import (
    generate_teaching_context,
)
from backend.algorithms.teaching_engine.teaching_strategy_engine import (
    TeachingStrategy,
)


def make_decision(
    action: NextAction,
    *,
    topic_id: uuid.UUID | None = None,
    difficulty: Difficulty = Difficulty.MEDIUM,
    learning_objective: str | None = "Understand the concept",
    assessment_required: bool = False,
) -> AdaptiveDecision:
    return AdaptiveDecision(
        next_action=action,
        topic_id=topic_id,
        difficulty=difficulty,
        reason="Test decision",
        ai_support=action == NextAction.AI_EXPLANATION,
        assessment_required=assessment_required,
        learning_objective=learning_objective,
    )


def test_teaching_context_for_new_topic():
    topic_id = uuid.uuid4()

    context = generate_teaching_context(
        decision=make_decision(
            NextAction.LEARN_NEW_TOPIC,
            topic_id=topic_id,
            difficulty=Difficulty.EASY,
        ),
        mastery_level=MasteryLevel.NOT_STARTED,
        ability_category=AbilityCategory.BEGINNER,
    )

    assert context.topic_id == topic_id
    assert context.teaching_strategy == TeachingStrategy.CONCEPT_INTRODUCTION
    assert context.difficulty == Difficulty.EASY
    assert context.mastery_level == MasteryLevel.NOT_STARTED
    assert context.ability_category == AbilityCategory.BEGINNER
    assert context.recommended_activity == "learn_new_topic"
    assert context.assessment_required is False


def test_teaching_context_for_review():
    topic_id = uuid.uuid4()

    context = generate_teaching_context(
        decision=make_decision(
            NextAction.REVIEW_TOPIC,
            topic_id=topic_id,
        ),
        mastery_level=MasteryLevel.DEVELOPING,
        ability_category=AbilityCategory.INTERMEDIATE,
        weak_concepts=["Binary Search"],
    )

    assert context.topic_id == topic_id
    assert context.teaching_strategy == TeachingStrategy.GUIDED_REVISION
    assert context.mastery_level == MasteryLevel.DEVELOPING
    assert context.weak_concepts == ("Binary Search",)
    assert context.recommended_activity == "review_topic"


def test_teaching_context_for_practice_requires_assessment():
    topic_id = uuid.uuid4()

    context = generate_teaching_context(
        decision=make_decision(
            NextAction.PRACTICE,
            topic_id=topic_id,
            assessment_required=True,
        ),
        mastery_level=MasteryLevel.PROFICIENT,
        ability_category=AbilityCategory.INTERMEDIATE,
    )

    assert context.teaching_strategy == TeachingStrategy.GUIDED_PRACTICE
    assert context.assessment_required is True


def test_teaching_context_for_assessment_is_hard():
    topic_id = uuid.uuid4()

    context = generate_teaching_context(
        decision=make_decision(
            NextAction.ASSESSMENT,
            topic_id=topic_id,
            difficulty=Difficulty.HARD,
            assessment_required=True,
        ),
        mastery_level=MasteryLevel.MASTERED,
        ability_category=AbilityCategory.ADVANCED,
    )

    assert context.teaching_strategy == TeachingStrategy.ASSESSMENT
    assert context.difficulty == Difficulty.HARD
    assert context.assessment_required is True


def test_teaching_context_for_ai_explanation():
    topic_id = uuid.uuid4()

    context = generate_teaching_context(
        decision=make_decision(
            NextAction.AI_EXPLANATION,
            topic_id=topic_id,
        ),
        mastery_level=MasteryLevel.BEGINNER,
        ability_category=AbilityCategory.BEGINNER,
    )

    assert context.teaching_strategy == TeachingStrategy.PERSONALIZED_EXPLANATION
    assert context.recommended_activity == "ai_explanation"


def test_teaching_context_preserves_learning_objective():
    topic_id = uuid.uuid4()

    context = generate_teaching_context(
        decision=make_decision(
            NextAction.REVIEW_TOPIC,
            topic_id=topic_id,
            learning_objective="Explain how binary search reduces search space.",
        ),
        mastery_level=MasteryLevel.DEVELOPING,
        ability_category=AbilityCategory.INTERMEDIATE,
    )

    assert (
        context.learning_objective
        == "Explain how binary search reduces search space."
    )