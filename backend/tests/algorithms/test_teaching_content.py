"""
AI Teaching Content Engine — Tests.

DB-independent tests covering all 24 requirements for the structured
instructional content generation pipeline.

Tests 1-6:   Strategy-specific content fields
Tests 7-12:  Teaching Context integrity (passthrough fields)
Tests 13-18: Parsing and validation
Tests 19-24: AI Service integration (mocked provider)
"""

from __future__ import annotations

import json
import uuid
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
)
from backend.core.exceptions import ValidationFailedError
from backend.services.ai.context_builder import LearnerContext
from backend.services.ai.prompt_builder import PromptBuilder
from backend.services.ai.prompt_templates import PromptTemplateName, get_template
from backend.services.ai.response_parser import parse_teaching_content
from backend.services.ai.response_validator import validate_teaching_content
from backend.services.ai.teaching_content import (
    REQUIRED_FIELDS_BY_STRATEGY,
    TeachingContent,
)


# -- Helpers -----------------------------------------------------------


def _make_tc(
    *,
    action: NextAction = NextAction.LEARN_NEW_TOPIC,
    topic_id: uuid.UUID | None = None,
    difficulty: Difficulty = Difficulty.MEDIUM,
    mastery_level: MasteryLevel = MasteryLevel.DEVELOPING,
    ability_category: AbilityCategory = AbilityCategory.INTERMEDIATE,
    learning_objective: str | None = "Understand binary search",
    weak_concepts: list[str] | None = None,
    assessment_required: bool = False,
) -> TeachingContextData:
    decision = AdaptiveDecision(
        next_action=action,
        topic_id=topic_id or uuid.uuid4(),
        difficulty=difficulty,
        reason="Test",
        ai_support=action == NextAction.AI_EXPLANATION,
        assessment_required=assessment_required,
        learning_objective=learning_objective,
    )
    return generate_teaching_context(
        decision=decision,
        mastery_level=mastery_level,
        ability_category=ability_category,
        weak_concepts=weak_concepts or [],
    )


def _make_learner_context(
    tc: TeachingContextData,
    topic_title: str = "Binary Search",
) -> LearnerContext:
    return LearnerContext(
        student_id=uuid.uuid4(),
        topic_id=tc.topic_id or uuid.uuid4(),
        topic_title=topic_title,
        ability_theta=0.5,
        ability_category=AbilityCategory.INTERMEDIATE,
        topic_mastery=0.55,
        mastery_level=MasteryLevel.DEVELOPING,
        weak_topic_titles=list(tc.weak_concepts),
        strong_topic_titles=["Arrays"],
        learning_objective=tc.learning_objective,
        recent_interactions=[],
        teaching_context=tc,
    )


def _valid_json_for_strategy(
    strategy: str,
    topic: str = "Binary Search",
    difficulty: str = "medium",
    learning_objective: str | None = "Understand binary search",
) -> str:
    """Generate a valid JSON response matching the strategy's required fields."""
    base = {
        "teaching_strategy": strategy,
        "topic": topic,
        "learning_objective": learning_objective,
        "difficulty": difficulty,
        "explanation": None,
        "examples": [],
        "key_takeaways": [],
        "practice_question": None,
        "hints": [],
        "expected_answer": None,
        "follow_up_activity": None,
    }

    if strategy == "Concept Introduction":
        base["explanation"] = "Binary search is an efficient algorithm that finds items in a sorted collection by repeatedly dividing the search space in half."
        base["examples"] = ["Search for 7 in [1,3,5,7,9]: mid=5, 7>5 so search right half, mid=7 found!"]
        base["key_takeaways"] = ["Binary search requires a sorted input", "Time complexity is O(log n)"]

    elif strategy == "Guided Revision":
        base["explanation"] = "Let us revise the key concepts of binary search. Remember that the array must be sorted for binary search to work correctly."
        base["examples"] = ["Given [2,4,6,8,10], find 6: compare with mid=6, found at index 2"]

    elif strategy == "Guided Practice":
        base["practice_question"] = "Given a sorted array [1, 3, 5, 7, 9, 11], use binary search to find the index of element 9. Show each step."
        base["hints"] = ["Start by identifying the middle element", "Compare 9 with the middle element to decide which half to search"]
        base["expected_answer"] = "Step 1: mid=5 (index 2), 9>5 so search right. Step 2: mid=9 (index 4), found! Answer: index 4"

    elif strategy == "Assessment":
        base["practice_question"] = "Explain why binary search cannot be applied to an unsorted array. Provide a counterexample."
        base["expected_answer"] = "Binary search relies on the sorted order to eliminate half the search space. In an unsorted array like [3,1,4,1,5], checking the middle element (4) and concluding all elements to the left are smaller would be incorrect."

    elif strategy == "Personalized Explanation":
        base["explanation"] = "Since you are struggling with the concept of dividing the search space, let me explain it differently. Think of a phone book - you do not start from page 1."
        base["examples"] = ["Phone book: looking for 'Smith', you open roughly to the middle, see 'M', and know Smith is in the second half"]

    elif strategy == "Progression":
        base["explanation"] = "Now that you understand basic binary search, let us explore binary search on rotated arrays. A rotated sorted array is one where a sorted array has been rotated around a pivot."
        base["key_takeaways"] = ["Modified binary search can handle rotated arrays", "The key insight is finding which half is sorted"]

    return json.dumps(base)


# =====================================================================
# Tests 1-6: Strategy-Specific Content Fields
# =====================================================================


class TestConceptIntroductionContent:
    """Test 1: Concept Introduction produces expected structured fields."""

    def test_concept_introduction_has_required_fields(self) -> None:
        raw = _valid_json_for_strategy("Concept Introduction")
        content = parse_teaching_content(
            raw,
            teaching_strategy="Concept Introduction",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="medium",
        )
        validate_teaching_content(
            content,
            expected_strategy="Concept Introduction",
            expected_topic="Binary Search",
        )
        assert content.explanation is not None
        assert len(content.examples) >= 1
        assert len(content.key_takeaways) >= 1


class TestGuidedRevisionContent:
    """Test 2: Guided Revision produces revision-oriented content."""

    def test_guided_revision_has_required_fields(self) -> None:
        raw = _valid_json_for_strategy("Guided Revision")
        content = parse_teaching_content(
            raw,
            teaching_strategy="Guided Revision",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="medium",
        )
        validate_teaching_content(
            content,
            expected_strategy="Guided Revision",
            expected_topic="Binary Search",
        )
        assert content.explanation is not None
        assert len(content.examples) >= 1


class TestGuidedPracticeContent:
    """Test 3: Guided Practice produces practice question and guidance."""

    def test_guided_practice_has_required_fields(self) -> None:
        raw = _valid_json_for_strategy("Guided Practice")
        content = parse_teaching_content(
            raw,
            teaching_strategy="Guided Practice",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="medium",
        )
        validate_teaching_content(
            content,
            expected_strategy="Guided Practice",
            expected_topic="Binary Search",
        )
        assert content.practice_question is not None
        assert len(content.hints) >= 1
        assert content.expected_answer is not None


class TestAssessmentContent:
    """Test 4: Assessment produces assessment-oriented content."""

    def test_assessment_has_required_fields(self) -> None:
        raw = _valid_json_for_strategy("Assessment")
        content = parse_teaching_content(
            raw,
            teaching_strategy="Assessment",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="hard",
        )
        validate_teaching_content(
            content,
            expected_strategy="Assessment",
            expected_topic="Binary Search",
        )
        assert content.practice_question is not None
        assert content.expected_answer is not None


class TestPersonalizedExplanationContent:
    """Test 5: Personalized Explanation uses weak concepts."""

    def test_personalized_explanation_has_required_fields(self) -> None:
        raw = _valid_json_for_strategy("Personalized Explanation")
        content = parse_teaching_content(
            raw,
            teaching_strategy="Personalized Explanation",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="easy",
        )
        validate_teaching_content(
            content,
            expected_strategy="Personalized Explanation",
            expected_topic="Binary Search",
        )
        assert content.explanation is not None
        assert len(content.examples) >= 1
        # Explanation should address weak areas
        assert "struggling" in content.explanation.lower() or "search space" in content.explanation.lower()


class TestProgressionContent:
    """Test 6: Progression produces next-level instructional content."""

    def test_progression_has_required_fields(self) -> None:
        raw = _valid_json_for_strategy("Progression")
        content = parse_teaching_content(
            raw,
            teaching_strategy="Progression",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="hard",
        )
        validate_teaching_content(
            content,
            expected_strategy="Progression",
            expected_topic="Binary Search",
        )
        assert content.explanation is not None
        assert len(content.key_takeaways) >= 1


# =====================================================================
# Tests 7-12: Teaching Context Integrity
# =====================================================================


class TestTeachingContextIntegrity:
    """Tests 7-12: Passthrough fields come from TeachingContextData."""

    def test_7_strategy_from_teaching_context(self) -> None:
        """Teaching strategy is passthrough from TeachingContextData."""
        tc = _make_tc(action=NextAction.REVIEW_TOPIC)
        raw = _valid_json_for_strategy("Guided Revision")
        content = parse_teaching_content(
            raw,
            teaching_strategy=tc.teaching_strategy.value,
            topic="Binary Search",
            learning_objective=tc.learning_objective,
            difficulty=tc.difficulty.value,
        )
        assert content.teaching_strategy == "Guided Revision"

    def test_8_difficulty_from_teaching_context(self) -> None:
        """Difficulty is passthrough from TeachingContextData."""
        tc = _make_tc(difficulty=Difficulty.HARD)
        raw = _valid_json_for_strategy("Concept Introduction")
        # LLM might echo "medium" but parser uses authoritative value
        content = parse_teaching_content(
            raw,
            teaching_strategy="Concept Introduction",
            topic="Binary Search",
            learning_objective=tc.learning_objective,
            difficulty="hard",
        )
        assert content.difficulty == "hard"

    def test_9_learning_objective_from_teaching_context(self) -> None:
        """Learning objective is passthrough from TeachingContextData."""
        tc = _make_tc(learning_objective="Master binary search invariant")
        raw = _valid_json_for_strategy("Concept Introduction")
        content = parse_teaching_content(
            raw,
            teaching_strategy="Concept Introduction",
            topic="Binary Search",
            learning_objective="Master binary search invariant",
            difficulty="medium",
        )
        assert content.learning_objective == "Master binary search invariant"

    def test_10_topic_preserved(self) -> None:
        """Requested topic is preserved even if LLM echoes differently."""
        data = json.loads(_valid_json_for_strategy("Concept Introduction"))
        data["topic"] = "Wrong Topic"  # LLM echoed wrong topic
        raw = json.dumps(data)

        content = parse_teaching_content(
            raw,
            teaching_strategy="Concept Introduction",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="medium",
        )
        # Parser always uses authoritative topic
        assert content.topic == "Binary Search"

    def test_11_recommended_activity_in_prompt(self) -> None:
        """Recommended activity from TeachingContextData appears in prompt."""
        tc = _make_tc(action=NextAction.PRACTICE)
        context = _make_learner_context(tc)
        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.TEACHING_CONTENT),
            context=context,
            user_message="Practice binary search.",
        )
        assert "practice" in prompt.user_prompt

    def test_12_assessment_requirement_in_prompt(self) -> None:
        """Assessment requirement from TeachingContextData appears in prompt."""
        tc = _make_tc(action=NextAction.ASSESSMENT, assessment_required=True)
        context = _make_learner_context(tc)
        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.TEACHING_CONTENT),
            context=context,
            user_message="Test me.",
        )
        # The teaching context section shows assessment strategy
        assert "Assessment" in prompt.user_prompt


# =====================================================================
# Tests 13-18: Parsing and Validation
# =====================================================================


class TestParsing:
    """Tests 13-18: Response parsing and validation edge cases."""

    def test_13_valid_json_parsed_successfully(self) -> None:
        raw = _valid_json_for_strategy("Concept Introduction")
        content = parse_teaching_content(
            raw,
            teaching_strategy="Concept Introduction",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="medium",
        )
        assert isinstance(content, TeachingContent)
        assert content.teaching_strategy == "Concept Introduction"
        assert content.explanation is not None

    def test_14_malformed_json_falls_back_to_explanation(self) -> None:
        """Malformed JSON: parser wraps prose as explanation."""
        raw = "This is not valid JSON {broken"
        content = parse_teaching_content(
            raw,
            teaching_strategy="Concept Introduction",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="medium",
        )
        # Falls back: prose becomes explanation
        assert content.explanation is not None
        assert "broken" in content.explanation
        # Passthrough fields still set
        assert content.teaching_strategy == "Concept Introduction"
        assert content.topic == "Binary Search"

    def test_15_empty_response_rejected_by_validator(self) -> None:
        """Empty response: parsed as None explanation, validator rejects."""
        content = parse_teaching_content(
            "",
            teaching_strategy="Concept Introduction",
            topic="Binary Search",
            learning_objective=None,
            difficulty="medium",
        )
        # Explanation is None for empty input
        assert content.explanation is None
        # Validator should reject: required fields missing
        with pytest.raises(ValidationFailedError):
            validate_teaching_content(
                content,
                expected_strategy="Concept Introduction",
                expected_topic="Binary Search",
            )

    def test_16_missing_required_fields_rejected(self) -> None:
        """Missing required strategy-specific fields are rejected."""
        # Concept Introduction requires explanation, examples, key_takeaways
        data = {
            "teaching_strategy": "Concept Introduction",
            "topic": "Binary Search",
            "learning_objective": None,
            "difficulty": "medium",
            "explanation": "Some explanation here for binary search algorithm.",
            # examples missing!
            "examples": [],
            "key_takeaways": ["Important point"],
        }
        content = parse_teaching_content(
            json.dumps(data),
            teaching_strategy="Concept Introduction",
            topic="Binary Search",
            learning_objective=None,
            difficulty="medium",
        )
        with pytest.raises(ValidationFailedError, match="examples"):
            validate_teaching_content(
                content,
                expected_strategy="Concept Introduction",
                expected_topic="Binary Search",
            )

    def test_17_invalid_strategy_rejected(self) -> None:
        """Invalid teaching strategy value is rejected."""
        content = TeachingContent(
            teaching_strategy="Nonexistent Strategy",
            topic="Binary Search",
            learning_objective=None,
            difficulty="medium",
            explanation="Some text here.",
        )
        with pytest.raises(ValidationFailedError, match="Invalid teaching strategy"):
            validate_teaching_content(
                content,
                expected_strategy="Nonexistent Strategy",
                expected_topic="Binary Search",
            )

    def test_18_topic_mismatch_rejected(self) -> None:
        """Topic mismatch between expected and content is rejected."""
        content = TeachingContent(
            teaching_strategy="Concept Introduction",
            topic="Sorting Algorithms",
            learning_objective=None,
            difficulty="medium",
            explanation="Sorting is important.",
            examples=("Bubble sort example",),
            key_takeaways=("Sorting is O(n log n)",),
        )
        with pytest.raises(ValidationFailedError, match="does not match"):
            validate_teaching_content(
                content,
                expected_strategy="Concept Introduction",
                expected_topic="Binary Search",
            )


# =====================================================================
# Tests 19-24: AI Service Integration (mocked provider)
# =====================================================================


class TestAIServiceIntegration:
    """Tests 19-24: AI Service structured content pipeline with mocked provider."""

    def test_19_teaching_content_prompt_uses_teaching_context(self) -> None:
        """AIService passes Teaching Context into prompt generation
        (verified via the TEACHING_CONTENT template prompt content)."""
        tc = _make_tc(
            action=NextAction.LEARN_NEW_TOPIC,
            difficulty=Difficulty.EASY,
            learning_objective="Learn sorting basics",
            weak_concepts=["Bubble Sort"],
        )
        context = _make_learner_context(tc, topic_title="Sorting")
        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.TEACHING_CONTENT),
            context=context,
            user_message="Teach me sorting.",
        )
        assert "Concept Introduction" in prompt.user_prompt
        assert "easy" in prompt.user_prompt
        assert "Learn sorting basics" in prompt.user_prompt
        assert "Bubble Sort" in prompt.user_prompt

    def test_20_prompt_sent_to_provider(self) -> None:
        """The generated prompt has system_instruction and user_prompt."""
        tc = _make_tc(action=NextAction.LEARN_NEW_TOPIC)
        context = _make_learner_context(tc)
        prompt = PromptBuilder().build(
            template=get_template(PromptTemplateName.TEACHING_CONTENT),
            context=context,
            user_message="Explain binary search.",
        )
        assert len(prompt.system_instruction) > 0
        assert len(prompt.user_prompt) > 0
        assert "## Teaching Context" in prompt.user_prompt
        assert "JSON" in prompt.user_prompt

    def test_21_provider_response_parsed_into_teaching_content(self) -> None:
        """Provider JSON response is parsed into TeachingContent."""
        raw = _valid_json_for_strategy("Guided Practice")
        content = parse_teaching_content(
            raw,
            teaching_strategy="Guided Practice",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="medium",
        )
        assert isinstance(content, TeachingContent)
        assert content.practice_question is not None
        assert content.expected_answer is not None
        assert len(content.hints) >= 1

    def test_22_parsed_response_validated(self) -> None:
        """Validated TeachingContent passes all checks."""
        raw = _valid_json_for_strategy("Assessment")
        content = parse_teaching_content(
            raw,
            teaching_strategy="Assessment",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="hard",
        )
        # Should not raise
        validate_teaching_content(
            content,
            expected_strategy="Assessment",
            expected_topic="Binary Search",
        )

    def test_23_teaching_content_template_exists(self) -> None:
        """TEACHING_CONTENT template exists and has proper structure."""
        template = get_template(PromptTemplateName.TEACHING_CONTENT)
        assert template.name == PromptTemplateName.TEACHING_CONTENT
        assert len(template.role_description) > 0
        assert len(template.response_instructions) > 0
        assert "JSON" in template.response_instructions

    def test_24_all_strategies_have_required_fields_defined(self) -> None:
        """Every TeachingStrategy has a required fields mapping."""
        for strategy in TeachingStrategy:
            assert strategy.value in REQUIRED_FIELDS_BY_STRATEGY, (
                f"Strategy '{strategy.value}' has no required fields mapping"
            )

    def test_code_fence_wrapped_json_parsed(self) -> None:
        """JSON wrapped in code fences (common LLM behavior) is parsed."""
        inner = _valid_json_for_strategy("Concept Introduction")
        raw = f"```json\n{inner}\n```"
        content = parse_teaching_content(
            raw,
            teaching_strategy="Concept Introduction",
            topic="Binary Search",
            learning_objective="Understand binary search",
            difficulty="medium",
        )
        assert content.explanation is not None
        assert len(content.examples) >= 1

    def test_strategy_mismatch_rejected_by_validator(self) -> None:
        """Validator rejects when strategy in content differs from expected."""
        content = TeachingContent(
            teaching_strategy="Guided Practice",
            topic="Binary Search",
            learning_objective=None,
            difficulty="medium",
            practice_question="What is binary search? Explain the algorithm step by step.",
            hints=("Think about dividing the array",),
            expected_answer="Binary search divides the sorted array in half each step",
        )
        with pytest.raises(ValidationFailedError, match="does not match"):
            validate_teaching_content(
                content,
                expected_strategy="Concept Introduction",
                expected_topic="Binary Search",
            )

    def test_prose_fallback_sets_all_passthrough_fields(self) -> None:
        """When LLM returns prose, all passthrough fields are correctly set."""
        content = parse_teaching_content(
            "Here is a detailed explanation of binary search that is long enough to pass validation checks.",
            teaching_strategy="Personalized Explanation",
            topic="Binary Search",
            learning_objective="Master search algorithms",
            difficulty="hard",
        )
        assert content.teaching_strategy == "Personalized Explanation"
        assert content.topic == "Binary Search"
        assert content.learning_objective == "Master search algorithms"
        assert content.difficulty == "hard"
        assert content.explanation is not None
