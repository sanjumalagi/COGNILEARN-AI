"""
IRT Proof Tests — Deterministic, DB-independent.

Proves the actual IRT implementation (backend.algorithms.irt) behaves
correctly across the full range of scenarios required by §6:

- Correct responses affect ability appropriately
- Incorrect responses affect ability appropriately
- Question difficulty is considered
- Ability remains within documented bounds [-4.0, 4.0]
- Ability changes as response history changes
- Confidence score is meaningful
- Difficulty recommendation tracks ability

Uses ONLY the existing IRT implementation. No second formula invented.
"""

import math

import pytest

from backend.algorithms.irt.estimator import (
    AbilityCategory,
    IRTResult,
    classify_ability,
    estimate_ability,
    probability_correct,
)


class TestIRTCorrectResponsesIncreaseAbility:
    """Proves correct responses shift ability upward."""

    def test_single_correct_on_easy_item(self) -> None:
        result = estimate_ability(responses=[(True, -1.0)])
        assert result.ability > 0.0, "A correct response on an easy item should push ability above baseline"

    def test_single_correct_on_hard_item(self) -> None:
        result = estimate_ability(responses=[(True, 2.0)])
        assert result.ability > 0.0, "A correct response on a hard item should push ability above baseline"

    def test_more_correct_means_higher_ability(self) -> None:
        # Use mixed responses so MLE doesn't clamp at the boundary
        fewer_correct = estimate_ability(responses=[(True, 0.5), (False, 0.5)])
        more_correct = estimate_ability(responses=[(True, 0.3), (True, 0.5), (True, 0.7), (False, 0.5)])
        assert more_correct.ability > fewer_correct.ability, (
            "More correct responses should produce higher estimated ability"
        )

    def test_all_correct_produces_high_ability(self) -> None:
        result = estimate_ability(responses=[(True, d) for d in [0.1, 0.3, 0.5, 0.7, 0.9]])
        assert result.ability > 2.0, "All correct on moderate items should yield high ability"
        assert result.category == AbilityCategory.ADVANCED


class TestIRTIncorrectResponsesDecreaseAbility:
    """Proves incorrect responses shift ability downward."""

    def test_single_incorrect_on_easy_item(self) -> None:
        result = estimate_ability(responses=[(False, -1.0)])
        assert result.ability < 0.0, "An incorrect response on an easy item should push ability below baseline"

    def test_single_incorrect_on_hard_item(self) -> None:
        result = estimate_ability(responses=[(False, 2.0)])
        assert result.ability < 0.0, "An incorrect response on a hard item should push ability below baseline"

    def test_more_incorrect_means_lower_ability(self) -> None:
        # Use mixed responses so MLE doesn't clamp at the boundary
        fewer_wrong = estimate_ability(responses=[(False, 0.5), (True, 0.5)])
        more_wrong = estimate_ability(responses=[(False, 0.3), (False, 0.5), (False, 0.7), (True, 0.5)])
        assert more_wrong.ability < fewer_wrong.ability, (
            "More incorrect responses should produce lower estimated ability"
        )

    def test_all_incorrect_produces_low_ability(self) -> None:
        result = estimate_ability(responses=[(False, d) for d in [0.1, 0.3, 0.5, 0.7, 0.9]])
        assert result.ability < -2.0, "All incorrect on moderate items should yield low ability"
        assert result.category == AbilityCategory.BEGINNER


class TestIRTDifficultyConsidered:
    """Proves question difficulty is factored into the ability estimate."""

    def test_correct_on_harder_items_yields_higher_ability(self) -> None:
        # Include one incorrect to prevent clamping at +4.0
        easy_correct = estimate_ability(responses=[(True, -1.0), (True, -0.5), (False, 0.0)])
        hard_correct = estimate_ability(responses=[(True, 1.0), (True, 1.5), (False, 0.0)])
        assert hard_correct.ability > easy_correct.ability, (
            "Answering hard items correctly should yield higher ability than easy items"
        )

    def test_incorrect_on_easier_items_yields_lower_ability(self) -> None:
        # Include one correct to prevent clamping at -4.0
        hard_wrong = estimate_ability(responses=[(False, 1.5), (False, 2.0), (True, 0.0)])
        easy_wrong = estimate_ability(responses=[(False, -1.0), (False, -0.5), (True, 0.0)])
        assert easy_wrong.ability < hard_wrong.ability, (
            "Getting easy items wrong should yield lower ability than getting hard items wrong"
        )

    def test_mixed_responses_difficulty_ordering(self) -> None:
        """A student who gets hard items right and easy items wrong should
        still have higher ability than the reverse."""
        # Student A: correct on hard items, wrong on easy
        student_a = estimate_ability(responses=[(True, 1.5), (True, 2.0), (False, -1.0), (False, -0.5)])
        # Student B: correct on easy items, wrong on hard
        student_b = estimate_ability(responses=[(True, -1.0), (True, -0.5), (False, 1.5), (False, 2.0)])
        assert student_a.ability > student_b.ability

    def test_probability_correct_at_difficulty_equals_ability(self) -> None:
        """P(theta=b) = 0.5 exactly, per the 1PL formula."""
        for b in [-2.0, -1.0, 0.0, 0.5, 1.0, 2.0]:
            assert probability_correct(b, b) == pytest.approx(0.5)


class TestIRTAbilityBounds:
    """Proves ability stays within the documented [-4.0, 4.0] bounds."""

    def test_all_correct_clamps_at_max(self) -> None:
        result = estimate_ability(responses=[(True, d) for d in range(-3, 4)])
        assert result.ability <= 4.0
        assert result.ability == 4.0  # All correct → clamped at max

    def test_all_incorrect_clamps_at_min(self) -> None:
        result = estimate_ability(responses=[(False, d) for d in range(-3, 4)])
        assert result.ability >= -4.0
        assert result.ability == -4.0  # All incorrect → clamped at min

    def test_extreme_responses_stay_bounded(self) -> None:
        """Even 100 extreme responses don't exceed bounds."""
        all_correct = estimate_ability(responses=[(True, 0.0)] * 100)
        all_wrong = estimate_ability(responses=[(False, 0.0)] * 100)
        assert -4.0 <= all_correct.ability <= 4.0
        assert -4.0 <= all_wrong.ability <= 4.0

    def test_mixed_responses_within_bounds(self) -> None:
        result = estimate_ability(responses=[(i % 2 == 0, i * 0.1) for i in range(50)])
        assert -4.0 <= result.ability <= 4.0


class TestIRTAbilityChangesWithHistory:
    """Proves ability changes as response history evolves."""

    def test_adding_correct_response_increases_ability(self) -> None:
        base = estimate_ability(responses=[(True, 0.5), (False, 0.5)])
        extended = estimate_ability(responses=[(True, 0.5), (False, 0.5), (True, 0.5)])
        assert extended.ability > base.ability

    def test_adding_incorrect_response_decreases_ability(self) -> None:
        base = estimate_ability(responses=[(True, 0.5), (False, 0.5)])
        extended = estimate_ability(responses=[(True, 0.5), (False, 0.5), (False, 0.5)])
        assert extended.ability < base.ability

    def test_gradual_improvement_trajectory(self) -> None:
        """Simulates a student who improves over time: ability should trend upward."""
        # Start weak, gradually get more right
        histories = [
            [(False, 0.3), (False, 0.4)],  # All wrong
            [(False, 0.3), (False, 0.4), (True, 0.3)],  # Start getting some right
            [(False, 0.3), (False, 0.4), (True, 0.3), (True, 0.4), (True, 0.5)],  # Mostly right now
        ]
        abilities = [estimate_ability(responses=h).ability for h in histories]
        for i in range(1, len(abilities)):
            assert abilities[i] > abilities[i - 1], (
                f"Ability should increase as performance improves: step {i}"
            )

    def test_decline_trajectory(self) -> None:
        """Simulates a student who declines: ability should trend downward."""
        histories = [
            [(True, 0.5), (True, 0.6)],  # All right
            [(True, 0.5), (True, 0.6), (False, 0.5)],  # Start getting wrong
            [(True, 0.5), (True, 0.6), (False, 0.5), (False, 0.4), (False, 0.3)],  # Mostly wrong now
        ]
        abilities = [estimate_ability(responses=h).ability for h in histories]
        for i in range(1, len(abilities)):
            assert abilities[i] < abilities[i - 1], (
                f"Ability should decrease as performance declines: step {i}"
            )


class TestIRTConfidenceAndRecommendation:
    """Proves confidence score and difficulty recommendation are meaningful."""

    def test_no_responses_yields_zero_confidence(self) -> None:
        result = estimate_ability(responses=[])
        assert result.confidence_score == 0.0

    def test_more_responses_increases_confidence(self) -> None:
        few = estimate_ability(responses=[(True, 0.5), (False, 0.3)])
        many = estimate_ability(responses=[(True, 0.5), (False, 0.3)] * 10)
        assert many.confidence_score > few.confidence_score

    def test_difficulty_recommendation_equals_ability(self) -> None:
        """The Rasch model's optimal next-item difficulty is b = theta."""
        result = estimate_ability(responses=[(True, 0.3), (True, 0.5), (False, 0.7)])
        assert result.difficulty_recommendation == round(result.ability, 4)

    def test_confidence_bounded_zero_to_one(self) -> None:
        for responses in [
            [(True, 0.5)],
            [(False, 0.5)],
            [(True, 0.5)] * 50,
            [(True, 0.1), (False, 0.9)] * 20,
        ]:
            result = estimate_ability(responses=responses)
            assert 0.0 <= result.confidence_score <= 1.0


class TestIRTCategoryClassification:
    """Proves the documented ability category thresholds."""

    @pytest.mark.parametrize(
        ("theta", "expected"),
        [
            (-4.0, AbilityCategory.BEGINNER),
            (-1.5, AbilityCategory.BEGINNER),
            (-1.01, AbilityCategory.BEGINNER),
            (-1.0, AbilityCategory.INTERMEDIATE),  # boundary inclusive
            (0.0, AbilityCategory.INTERMEDIATE),
            (1.0, AbilityCategory.INTERMEDIATE),  # boundary inclusive
            (1.01, AbilityCategory.ADVANCED),
            (2.0, AbilityCategory.ADVANCED),
            (4.0, AbilityCategory.ADVANCED),
        ],
    )
    def test_documented_thresholds(self, theta: float, expected: AbilityCategory) -> None:
        assert classify_ability(theta) == expected
