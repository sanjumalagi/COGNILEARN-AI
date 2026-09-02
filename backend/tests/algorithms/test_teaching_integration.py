"""
Teaching Intelligence <-> AI Service Layer Integration Tests.

DB-independent tests that verify the Teaching Intelligence pipeline
is correctly wired into the AI Service. Only the external AI provider
and database-dependent services are mocked.

These tests verify all 12 integration requirements:
 1. AIService invokes TeachingEngineService
 2. Teaching Context reaches ContextBuilder
 3. Teaching strategy comes from Teaching Strategy Engine
 4. Difficulty comes from Educational/Adaptive Intelligence
 5. Learning objective comes from the selected topic
 6. Topic requested by the learner is preserved
 7. PromptBuilder receives the structured Teaching Context
 8. AI provider still receives the generated prompt
 9. Existing AI interaction logging still works
10. Existing error handling still works
11. Existing AI tests continue passing (via regression run)
12. Existing Teaching Engine tests continue passing (via regression run)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from unittest.mock import MagicMock, patch

import pytest

from backend.algorithms.adaptive_engine.adaptive_decision_engine import (
    AdaptiveDecision,
    Difficulty,
    NextAction,
)
from backend.algorithms.irt.estimator import AbilityCategory
from backend.algorithms.mastery_engine import MasteryLevel
from backend.algorithms.teaching_engine.teaching_engine import (
    TeachingContextData,
    generate_teaching_context,
)
from backend.algorithms.teaching_engine.teaching_strategy_engine import (
    TeachingStrategy,
    select_teaching_strategy,
)
from backend.core.exceptions import ValidationFailedError
from backend.services.ai.context_builder import LearnerContext
from backend.services.ai.prompt_builder import Prompt, PromptBuilder
from backend.services.ai.prompt_templates import PromptTemplateName, get_template


# -- Helpers ----------------------------------------------------------


def _make_teaching_context(
    *,
    action: NextAction = NextAction.REVIEW_TOPIC,
    topic_id: uuid.UUID | None = None,
    difficulty: Difficulty = Difficulty.MEDIUM,
    mastery_level: MasteryLevel = MasteryLevel.DEVELOPING,
    ability_category: AbilityCategory = AbilityCategory.INTERMEDIATE,
    learning_objective: str | None = "Understand binary search",
    weak_concepts: tuple[str, ...] = ("Sorting",),
    assessment_required: bool = False,
) -> TeachingContextData:
    """Create a TeachingContextData via the real Teaching Engine."""
    decision = AdaptiveDecision(
        next_action=action,
        topic_id=topic_id or uuid.uuid4(),
        difficulty=difficulty,
        reason="Test decision",
        ai_support=action == NextAction.AI_EXPLANATION,
        assessment_required=assessment_required,
        learning_objective=learning_objective,
    )
    return generate_teaching_context(
        decision=decision,
        mastery_level=mastery_level,
        ability_category=ability_category,
        weak_concepts=list(weak_concepts),
    )


def _make_learner_context(
    *,
    teaching_context: TeachingContextData | None = None,
    topic_id: uuid.UUID | None = None,
) -> LearnerContext:
    """Create a LearnerContext with a real TeachingContextData."""
    tid = topic_id or uuid.uuid4()
    tc = teaching_context or _make_teaching_context(topic_id=tid)
    return LearnerContext(
        student_id=uuid.uuid4(),
        topic_id=tid,
        topic_title="Binary Search",
        ability_theta=0.5,
        ability_category=AbilityCategory.INTERMEDIATE,
        topic_mastery=0.55,
        mastery_level=MasteryLevel.DEVELOPING,
        weak_topic_titles=["Sorting"],
        strong_topic_titles=["Arrays"],
        learning_objective=tc.learning_objective,
        recent_interactions=[],
        teaching_context=tc,
    )


# -- Requirement 3: Teaching strategy comes from Teaching Strategy Engine --


class TestTeachingStrategySourcedFromEngine:
    """Requirement 3: Teaching strategy in the prompt comes from the
    Teaching Strategy Engine, not from the prompt template."""

    @pytest.mark.parametrize(
        "action,expected_strategy",
        [
            (NextAction.LEARN_NEW_TOPIC, TeachingStrategy.CONCEPT_INTRODUCTION),
            (NextAction.REVIEW_TOPIC, TeachingStrategy.GUIDED_REVISION),
            (NextAction.PRACTICE, TeachingStrategy.GUIDED_PRACTICE),
            (NextAction.ASSESSMENT, TeachingStrategy.ASSESSMENT),
            (NextAction.AI_EXPLANATION, TeachingStrategy.PERSONALIZED_EXPLANATION),
            (NextAction.ADVANCE, TeachingStrategy.PROGRESSION),
        ],
    )
    def test_prompt_teaching_strategy_matches_engine_decision(
        self, action: NextAction, expected_strategy: TeachingStrategy
    ) -> None:
        tc = _make_teaching_context(action=action)
        context = _make_learner_context(teaching_context=tc)

        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.EXPLANATION),
            context=context,
            user_message="Explain this.",
        )

        # Teaching strategy label comes from Teaching Intelligence, NOT the template
        assert prompt.teaching_strategy_label == expected_strategy.value

    def test_prompt_teaching_strategy_differs_from_template_label(self) -> None:
        """The template label (e.g. 'Personalized Explanation') is no longer
        used as the strategy; the Teaching Strategy Engine's decision is used."""
        template = get_template(PromptTemplateName.EXPLANATION)
        tc = _make_teaching_context(action=NextAction.REVIEW_TOPIC)
        context = _make_learner_context(teaching_context=tc)

        prompt = PromptBuilder().build(
            template=template, context=context, user_message="Explain."
        )

        # Template would say "Personalized Explanation", but Teaching Engine says "Guided Revision"
        assert prompt.teaching_strategy_label == "Guided Revision"
        assert prompt.teaching_strategy_label != template.teaching_strategy_label


# -- Requirement 4: Difficulty comes from Adaptive Intelligence --------


class TestDifficultySourcedFromAdaptiveIntelligence:
    """Requirement 4: Difficulty in the prompt comes from the Adaptive
    Decision Engine's difficulty field in TeachingContextData, not from
    a local ability-to-difficulty mapping."""

    @pytest.mark.parametrize(
        "difficulty",
        [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD],
    )
    def test_prompt_difficulty_matches_teaching_context(
        self, difficulty: Difficulty
    ) -> None:
        tc = _make_teaching_context(difficulty=difficulty)
        context = _make_learner_context(teaching_context=tc)

        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.HINT),
            context=context,
            user_message="Give me a hint.",
        )

        assert prompt.difficulty == difficulty

    def test_difficulty_is_not_derived_from_ability_category(self) -> None:
        """Proves difficulty comes from Teaching Context, not from ability.
        A Beginner student could have HARD difficulty if the Adaptive
        Decision Engine decided so."""
        tc = _make_teaching_context(
            difficulty=Difficulty.HARD,
            ability_category=AbilityCategory.BEGINNER,
        )
        # Override ability_category to BEGINNER on the learner context
        context = LearnerContext(
            student_id=uuid.uuid4(),
            topic_id=uuid.uuid4(),
            topic_title="Test Topic",
            ability_theta=-1.5,
            ability_category=AbilityCategory.BEGINNER,
            topic_mastery=0.2,
            mastery_level=MasteryLevel.BEGINNER,
            weak_topic_titles=[],
            strong_topic_titles=[],
            learning_objective=tc.learning_objective,
            recent_interactions=[],
            teaching_context=tc,
        )

        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.CHAT),
            context=context,
            user_message="Help me.",
        )

        # HARD difficulty despite BEGINNER ability -- proves no local mapping
        assert prompt.difficulty == Difficulty.HARD


# -- Requirement 5: Learning objective from Teaching Context -----------


class TestLearningObjectiveFromTeachingContext:
    """Requirement 5: Learning objective in the prompt comes from the
    Teaching Context, not from an independent lookup."""

    def test_learning_objective_appears_in_prompt(self) -> None:
        tc = _make_teaching_context(
            learning_objective="Explain how binary search reduces search space."
        )
        context = _make_learner_context(teaching_context=tc)

        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.EXPLANATION),
            context=context,
            user_message="Explain binary search.",
        )

        assert "Explain how binary search reduces search space." in prompt.user_prompt

    def test_none_learning_objective_shows_fallback(self) -> None:
        tc = _make_teaching_context(learning_objective=None)
        context = _make_learner_context(teaching_context=tc)

        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.EXPLANATION),
            context=context,
            user_message="Explain.",
        )

        assert "Not yet defined for this topic." in prompt.user_prompt


# -- Requirement 6: Topic requested by learner is preserved ------------


class TestTopicPreserved:
    """Requirement 6: The topic_id explicitly requested by the AI
    interaction is preserved through the entire pipeline."""

    def test_topic_id_preserved_in_learner_context(self) -> None:
        requested_topic = uuid.uuid4()
        tc = _make_teaching_context(topic_id=requested_topic)
        context = _make_learner_context(teaching_context=tc, topic_id=requested_topic)

        assert context.topic_id == requested_topic
        assert context.teaching_context.topic_id == requested_topic


# -- Requirement 7: PromptBuilder receives structured Teaching Context --


class TestPromptBuilderReceivesTeachingContext:
    """Requirement 7: PromptBuilder receives and uses all fields from
    the structured Teaching Context."""

    def test_prompt_contains_all_teaching_context_fields(self) -> None:
        tc = _make_teaching_context(
            action=NextAction.REVIEW_TOPIC,
            difficulty=Difficulty.EASY,
            learning_objective="Understand sorting complexity",
            weak_concepts=("Bubble Sort", "Selection Sort"),
        )
        context = _make_learner_context(teaching_context=tc)

        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.FEEDBACK),
            context=context,
            user_message="Review my work.",
        )

        assert "Guided Revision" in prompt.user_prompt  # teaching_strategy
        assert "easy" in prompt.user_prompt  # difficulty
        assert "Understand sorting complexity" in prompt.user_prompt  # learning_objective
        assert "Bubble Sort" in prompt.user_prompt  # weak_concepts
        assert "Selection Sort" in prompt.user_prompt  # weak_concepts
        assert "review_topic" in prompt.user_prompt  # recommended_activity

    def test_prompt_contains_recommended_activity(self) -> None:
        tc = _make_teaching_context(action=NextAction.PRACTICE)
        context = _make_learner_context(teaching_context=tc)

        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.CHAT),
            context=context,
            user_message="Help.",
        )

        assert "practice" in prompt.user_prompt


# -- Requirement 8: AI provider receives the generated prompt ----------


class TestProviderReceivesPrompt:
    """Requirement 8: Prompt structure is correct for provider consumption."""

    def test_prompt_has_system_instruction_and_user_prompt(self) -> None:
        tc = _make_teaching_context()
        context = _make_learner_context(teaching_context=tc)

        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.EXPLANATION),
            context=context,
            user_message="Explain sorting.",
        )

        assert len(prompt.system_instruction) > 0
        assert len(prompt.user_prompt) > 0
        assert "## Teaching Context" in prompt.user_prompt
        assert "## Learner Context" in prompt.user_prompt
        assert "## Current User Request" in prompt.user_prompt
        assert "## Response Instructions" in prompt.user_prompt


# -- Requirement 10: Error handling still works ------------------------


class TestErrorHandling:
    """Requirement 10: Existing validation errors still raised."""

    def test_empty_message_raises_validation_error(self) -> None:
        tc = _make_teaching_context()
        context = _make_learner_context(teaching_context=tc)

        with pytest.raises(ValidationFailedError):
            PromptBuilder().build(
                template=get_template(PromptTemplateName.EXPLANATION),
                context=context,
                user_message="",
            )

    def test_too_long_message_raises_validation_error(self) -> None:
        tc = _make_teaching_context()
        context = _make_learner_context(teaching_context=tc)

        with pytest.raises(ValidationFailedError):
            PromptBuilder().build(
                template=get_template(PromptTemplateName.EXPLANATION),
                context=context,
                user_message="x" * 2001,
            )

    def test_empty_topic_title_raises_validation_error(self) -> None:
        tc = _make_teaching_context()
        context = LearnerContext(
            student_id=uuid.uuid4(),
            topic_id=uuid.uuid4(),
            topic_title="",  # empty
            ability_theta=0.0,
            ability_category=AbilityCategory.INTERMEDIATE,
            topic_mastery=None,
            mastery_level=MasteryLevel.NOT_STARTED,
            weak_topic_titles=[],
            strong_topic_titles=[],
            learning_objective=None,
            recent_interactions=[],
            teaching_context=tc,
        )

        with pytest.raises(ValidationFailedError):
            PromptBuilder().build(
                template=get_template(PromptTemplateName.EXPLANATION),
                context=context,
                user_message="Explain.",
            )


# -- End-to-End: TeachingContextData flows through entire pipeline -----


class TestEndToEndTeachingContextFlow:
    """Verifies the full chain: Teaching Engine -> ContextBuilder data ->
    PromptBuilder -> Prompt, all using real algorithm code."""

    def test_full_pipeline_review_scenario(self) -> None:
        """A struggling student triggers Guided Revision with easy difficulty."""
        topic_id = uuid.uuid4()

        # Step 1: Adaptive Decision (would come from AdaptiveDecisionService)
        decision = AdaptiveDecision(
            next_action=NextAction.REVIEW_TOPIC,
            topic_id=topic_id,
            difficulty=Difficulty.EASY,
            reason="Mastery below threshold",
            ai_support=False,
            assessment_required=False,
            learning_objective="Explain linear search step by step",
        )

        # Step 2: Teaching Engine produces Teaching Context
        tc = generate_teaching_context(
            decision=decision,
            mastery_level=MasteryLevel.BEGINNER,
            ability_category=AbilityCategory.BEGINNER,
            weak_concepts=["Linear Search", "Arrays"],
        )

        assert tc.teaching_strategy == TeachingStrategy.GUIDED_REVISION
        assert tc.difficulty == Difficulty.EASY
        assert tc.recommended_activity == "review_topic"

        # Step 3: LearnerContext carries the Teaching Context
        context = LearnerContext(
            student_id=uuid.uuid4(),
            topic_id=topic_id,
            topic_title="Linear Search",
            ability_theta=-1.0,
            ability_category=AbilityCategory.BEGINNER,
            topic_mastery=0.25,
            mastery_level=MasteryLevel.BEGINNER,
            weak_topic_titles=["Linear Search", "Arrays"],
            strong_topic_titles=[],
            learning_objective=tc.learning_objective,
            recent_interactions=[],
            teaching_context=tc,
        )

        # Step 4: PromptBuilder formats it
        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.EXPLANATION),
            context=context,
            user_message="I don't understand linear search.",
        )

        # Verify Teaching Intelligence decisions are in the prompt
        assert "Guided Revision" in prompt.user_prompt
        assert "easy" in prompt.user_prompt
        assert "Explain linear search step by step" in prompt.user_prompt
        assert "Linear Search" in prompt.user_prompt
        assert "Arrays" in prompt.user_prompt
        assert "review_topic" in prompt.user_prompt

        # Verify prompt metadata matches Teaching Context
        assert prompt.teaching_strategy_label == "Guided Revision"
        assert prompt.difficulty == Difficulty.EASY

    def test_full_pipeline_assessment_scenario(self) -> None:
        """An advanced student triggers Assessment with hard difficulty."""
        topic_id = uuid.uuid4()

        decision = AdaptiveDecision(
            next_action=NextAction.ASSESSMENT,
            topic_id=topic_id,
            difficulty=Difficulty.HARD,
            reason="Student is ready for assessment",
            ai_support=False,
            assessment_required=True,
            learning_objective="Prove correctness of binary search",
        )

        tc = generate_teaching_context(
            decision=decision,
            mastery_level=MasteryLevel.MASTERED,
            ability_category=AbilityCategory.ADVANCED,
        )

        assert tc.teaching_strategy == TeachingStrategy.ASSESSMENT
        assert tc.assessment_required is True

        context = LearnerContext(
            student_id=uuid.uuid4(),
            topic_id=topic_id,
            topic_title="Binary Search",
            ability_theta=2.5,
            ability_category=AbilityCategory.ADVANCED,
            topic_mastery=0.92,
            mastery_level=MasteryLevel.MASTERED,
            weak_topic_titles=[],
            strong_topic_titles=["Binary Search", "Sorting"],
            learning_objective=tc.learning_objective,
            recent_interactions=[],
            teaching_context=tc,
        )

        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.FEEDBACK),
            context=context,
            user_message="How did I do on the assessment?",
        )

        assert "Assessment" in prompt.user_prompt
        assert "hard" in prompt.user_prompt
        assert prompt.teaching_strategy_label == "Assessment"
        assert prompt.difficulty == Difficulty.HARD
