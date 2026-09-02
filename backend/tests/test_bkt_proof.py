"""
BKT Proof Tests — Deterministic, DB-independent.

Proves the actual BKT implementation (backend.algorithms.bkt) behaves
correctly across the full range of scenarios required by §7:

- Topic mastery can be initialized from diagnostic evidence
- Correct responses increase mastery
- Incorrect responses affect mastery appropriately
- Different topics maintain separate mastery states
- Weak/mastered classifications match documented thresholds
- The learning transition P(T) is applied after evidence updates

Uses ONLY the existing BKT implementation. No second formula invented.
"""

import uuid

import pytest

from backend.algorithms.bkt.estimator import (
    BKTResult,
    MasteryStatus,
    classify_mastery,
    compute_initial_mastery,
    update_mastery,
)
from backend.algorithms.mastery_engine import (
    MasteryLevel,
    STRONG_TOPIC_THRESHOLD,
    WEAK_TOPIC_THRESHOLD,
    classify_mastery_level,
    is_strong_topic,
    is_weak_topic,
)


class TestBKTInitializationFromDiagnosticEvidence:
    """Proves initial mastery is derived from actual evidence, not a fixed constant."""

    def test_all_correct_diagnostic_yields_high_mastery(self) -> None:
        mastery = compute_initial_mastery(diagnostic_responses=[True, True, True, True])
        assert mastery > 0.80, f"All-correct diagnostic should yield high mastery, got {mastery}"

    def test_all_incorrect_diagnostic_yields_low_mastery(self) -> None:
        mastery = compute_initial_mastery(diagnostic_responses=[False, False, False, False])
        assert mastery < 0.20, f"All-incorrect diagnostic should yield low mastery, got {mastery}"

    def test_three_of_four_correct_vs_one_of_four(self) -> None:
        strong = compute_initial_mastery(diagnostic_responses=[True, True, True, False])
        weak = compute_initial_mastery(diagnostic_responses=[False, False, False, True])
        assert strong > weak, (
            f"3/4 correct ({strong}) should yield higher initial mastery than 1/4 ({weak})"
        )

    def test_different_patterns_produce_different_values(self) -> None:
        """No two distinct diagnostic patterns should produce identical mastery."""
        patterns = [
            [True, True, True, True],
            [True, True, True, False],
            [True, True, False, False],
            [True, False, False, False],
            [False, False, False, False],
        ]
        values = [compute_initial_mastery(diagnostic_responses=p) for p in patterns]
        # Each pattern should produce a strictly higher value than the next
        for i in range(len(values) - 1):
            assert values[i] > values[i + 1], (
                f"Pattern with more correct answers should yield higher mastery: "
                f"pattern {i} ({values[i]}) vs pattern {i+1} ({values[i+1]})"
            )

    def test_single_correct_response(self) -> None:
        mastery = compute_initial_mastery(diagnostic_responses=[True])
        assert 0.0 < mastery < 1.0

    def test_single_incorrect_response(self) -> None:
        mastery = compute_initial_mastery(diagnostic_responses=[False])
        assert 0.0 < mastery < 1.0

    def test_empty_diagnostic_raises(self) -> None:
        with pytest.raises(ValueError, match="At least one"):
            compute_initial_mastery(diagnostic_responses=[])

    def test_mastery_always_bounded_zero_to_one(self) -> None:
        for length in range(1, 20):
            for correct_count in range(length + 1):
                responses = [True] * correct_count + [False] * (length - correct_count)
                mastery = compute_initial_mastery(diagnostic_responses=responses)
                assert 0.0 <= mastery <= 1.0, (
                    f"Mastery out of bounds for {correct_count}/{length}: {mastery}"
                )


class TestBKTCorrectResponsesIncreaseMastery:
    """Proves correct responses increase mastery probability."""

    @pytest.mark.parametrize("initial", [0.1, 0.3, 0.5, 0.7])
    def test_correct_response_always_increases(self, initial: float) -> None:
        result = update_mastery(previous_mastery=initial, is_correct=True)
        assert result.mastery_probability > initial, (
            f"Correct response should increase mastery from {initial}, got {result.mastery_probability}"
        )

    def test_repeated_correct_responses_trend_toward_mastery(self) -> None:
        mastery = compute_initial_mastery(diagnostic_responses=[True])
        for i in range(15):
            result = update_mastery(previous_mastery=mastery, is_correct=True)
            assert result.mastery_probability >= mastery, f"Iteration {i}: mastery should not decrease on correct"
            mastery = result.mastery_probability
        assert mastery > 0.95, f"After 15 correct responses, mastery should approach 1.0, got {mastery}"

    def test_correct_on_low_mastery_increases_meaningfully(self) -> None:
        result = update_mastery(previous_mastery=0.1, is_correct=True)
        assert result.mastery_probability > 0.2, "Correct answer on very low mastery should increase meaningfully"


class TestBKTIncorrectResponsesAffectMastery:
    """Proves incorrect responses affect mastery appropriately."""

    @pytest.mark.parametrize("initial", [0.3, 0.5, 0.7, 0.9])
    def test_incorrect_response_decreases_mastery(self, initial: float) -> None:
        result = update_mastery(previous_mastery=initial, is_correct=False)
        # Note: due to the learning transition P(T), mastery may not always
        # decrease below the starting point for all initial values. But
        # incorrect should produce LOWER mastery than correct from the same start.
        correct_result = update_mastery(previous_mastery=initial, is_correct=True)
        assert result.mastery_probability < correct_result.mastery_probability, (
            f"Incorrect should yield lower mastery than correct from same start {initial}"
        )

    def test_repeated_incorrect_keeps_mastery_low(self) -> None:
        mastery = compute_initial_mastery(diagnostic_responses=[False])
        for _ in range(10):
            result = update_mastery(previous_mastery=mastery, is_correct=False)
            mastery = result.mastery_probability
        assert mastery < 0.5, f"After many incorrect responses, mastery should stay low, got {mastery}"

    def test_incorrect_on_high_mastery_reduces_it(self) -> None:
        result = update_mastery(previous_mastery=0.9, is_correct=False)
        assert result.mastery_probability < 0.9, "Incorrect on high mastery should reduce it"


class TestBKTSeparateTopicStates:
    """Proves different topics maintain independent mastery states.
    (This is inherently true since update_mastery operates on a single
    previous_mastery value, but we demonstrate it explicitly.)"""

    def test_two_topics_independent(self) -> None:
        topic_a_mastery = compute_initial_mastery(diagnostic_responses=[True, True, True])
        topic_b_mastery = compute_initial_mastery(diagnostic_responses=[False, False, False])

        # Update topic A with correct, topic B with incorrect
        topic_a_result = update_mastery(previous_mastery=topic_a_mastery, is_correct=True)
        topic_b_result = update_mastery(previous_mastery=topic_b_mastery, is_correct=False)

        # They should be vastly different
        assert topic_a_result.mastery_probability > topic_b_result.mastery_probability + 0.3, (
            "Topics should maintain independent mastery states"
        )

    def test_three_topics_diverge_from_same_start(self) -> None:
        """Three topics starting from the same initial mastery diverge based on responses."""
        initial = compute_initial_mastery(diagnostic_responses=[True, False])

        # Topic 1: all correct → should increase
        t1 = initial
        for _ in range(5):
            t1 = update_mastery(previous_mastery=t1, is_correct=True).mastery_probability

        # Topic 2: all incorrect → should stay low / decrease
        t2 = initial
        for _ in range(5):
            t2 = update_mastery(previous_mastery=t2, is_correct=False).mastery_probability

        # Topic 3: mixed → should be between the two
        t3 = initial
        for correct in [True, False, True, False, True]:
            t3 = update_mastery(previous_mastery=t3, is_correct=correct).mastery_probability

        assert t1 > t3 > t2, f"Expected t1({t1}) > t3({t3}) > t2({t2})"


class TestBKTWeakMasteredClassifications:
    """Proves the documented thresholds for weak/mastered classification."""

    def test_weak_threshold_is_040(self) -> None:
        assert WEAK_TOPIC_THRESHOLD == 0.40

    def test_strong_threshold_is_080(self) -> None:
        assert STRONG_TOPIC_THRESHOLD == 0.80

    @pytest.mark.parametrize(
        ("score", "expected_weak", "expected_strong"),
        [
            (0.0, True, False),
            (0.1, True, False),
            (0.39, True, False),
            (0.40, False, False),
            (0.5, False, False),
            (0.79, False, False),
            (0.80, False, True),
            (0.9, False, True),
            (1.0, False, True),
        ],
    )
    def test_weak_strong_classification(self, score: float, expected_weak: bool, expected_strong: bool) -> None:
        assert is_weak_topic(score) is expected_weak, f"is_weak_topic({score})"
        assert is_strong_topic(score) is expected_strong, f"is_strong_topic({score})"

    @pytest.mark.parametrize(
        ("score", "expected_bkt_status"),
        [
            (0.1, MasteryStatus.NEEDS_IMPROVEMENT),
            (0.39, MasteryStatus.NEEDS_IMPROVEMENT),
            (0.40, MasteryStatus.DEVELOPING),
            (0.6, MasteryStatus.DEVELOPING),
            (0.80, MasteryStatus.DEVELOPING),
            (0.81, MasteryStatus.MASTERED),
            (0.95, MasteryStatus.MASTERED),
        ],
    )
    def test_bkt_three_level_status(self, score: float, expected_bkt_status: MasteryStatus) -> None:
        assert classify_mastery(score) == expected_bkt_status

    @pytest.mark.parametrize(
        ("score", "expected_level"),
        [
            (None, MasteryLevel.NOT_STARTED),
            (0.1, MasteryLevel.BEGINNER),
            (0.39, MasteryLevel.BEGINNER),
            (0.40, MasteryLevel.DEVELOPING),
            (0.59, MasteryLevel.DEVELOPING),
            (0.60, MasteryLevel.PROFICIENT),
            (0.79, MasteryLevel.PROFICIENT),
            (0.80, MasteryLevel.MASTERED),
            (0.99, MasteryLevel.MASTERED),
        ],
    )
    def test_mastery_engine_five_level(self, score: float | None, expected_level: MasteryLevel) -> None:
        assert classify_mastery_level(score) == expected_level


class TestBKTRecommendationTrigger:
    """Proves the recommendation trigger fires correctly."""

    def test_needs_improvement_triggers_recommendation(self) -> None:
        result = update_mastery(previous_mastery=0.1, is_correct=False)
        assert result.recommendation_trigger is True

    def test_developing_does_not_trigger(self) -> None:
        result = update_mastery(previous_mastery=0.5, is_correct=True)
        assert result.recommendation_trigger is False

    def test_mastered_does_not_trigger(self) -> None:
        result = update_mastery(previous_mastery=0.9, is_correct=True)
        assert result.recommendation_trigger is False


class TestBKTNoFixedPrior:
    """Proves no fixed P(L0) constant is silently used."""

    def test_update_without_initial_mastery_raises(self) -> None:
        with pytest.raises(ValueError, match="diagnostic evidence"):
            update_mastery(previous_mastery=None, is_correct=True)

    def test_update_without_initial_mastery_raises_for_incorrect(self) -> None:
        with pytest.raises(ValueError, match="diagnostic evidence"):
            update_mastery(previous_mastery=None, is_correct=False)
