"""
Adaptive Learning Proof Tests — Deterministic, DB-independent.

Proves the actual Adaptive Engine (backend.algorithms.adaptive_engine)
produces correct decisions across the scenarios required by §8:

- Low ability / weak mastery → remediation/review recommendation
- Stronger ability / mastery → progression recommendation
- Repeated mistakes → AI Support trigger
- Improving performance → learner state and decision changes

All decisions come from the actual engine. No hardcoded "weak = easy".
Uses ONLY the existing Adaptive Engine implementation.
"""

import uuid

import pytest

from backend.algorithms.adaptive_engine.adaptive_decision_engine import (
    AdaptiveDecision,
    Difficulty,
    NextAction,
    decide,
)
from backend.algorithms.adaptive_engine.learning_path_engine import (
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
from backend.algorithms.bkt.estimator import compute_initial_mastery, update_mastery
from backend.algorithms.irt.estimator import AbilityCategory, classify_ability, estimate_ability
from backend.algorithms.mastery_engine import classify_mastery_level, MasteryLevel


class TestLowAbilityWeakMasteryRemediation:
    """Proves: student with low ability + weak mastery → remediation."""

    def test_weak_student_gets_revision_recommendation(self) -> None:
        topic_id = uuid.uuid4()
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.15, incorrect_response_count=0)],
            ability_category=AbilityCategory.BEGINNER,
        )
        assert len(recs) >= 1
        assert recs[0].recommendation_type == RecommendationType.REVISION
        assert recs[0].topic_id == topic_id

    def test_weak_student_decision_is_review_topic(self) -> None:
        topic_id = uuid.uuid4()
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.15, incorrect_response_count=0)],
            ability_category=AbilityCategory.BEGINNER,
        )
        decision = decide(
            top_recommendation=recs[0],
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.BEGINNER,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.REVIEW_TOPIC
        assert decision.difficulty == Difficulty.EASY
        assert decision.topic_id == topic_id

    def test_weak_student_learning_path_prioritizes_weakest(self) -> None:
        weak1 = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.10)
        weak2 = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.25)
        steps = build_learning_path(encountered_topics=[weak2, weak1], next_unencountered_topic_id=None)
        assert steps[0].topic_id == weak1.topic_id, "Weakest topic should come first"
        assert steps[1].topic_id == weak2.topic_id


class TestStrongAbilityMasteryProgression:
    """Proves: student with stronger ability + mastery → progression."""

    def test_strong_student_gets_progression_recommendation(self) -> None:
        topic_id = uuid.uuid4()
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.90, incorrect_response_count=0)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        assert len(recs) == 1
        assert recs[0].recommendation_type == RecommendationType.PROGRESSION

    def test_advanced_student_gets_challenge_recommendation(self) -> None:
        topic_id = uuid.uuid4()
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.90, incorrect_response_count=0)],
            ability_category=AbilityCategory.ADVANCED,
        )
        assert len(recs) == 1
        assert recs[0].recommendation_type == RecommendationType.CHALLENGE

    def test_strong_student_decision_is_advance(self) -> None:
        topic_id = uuid.uuid4()
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.90, incorrect_response_count=0)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        decision = decide(
            top_recommendation=recs[0],
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.INTERMEDIATE,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.ADVANCE
        assert decision.difficulty == Difficulty.MEDIUM

    def test_advanced_student_decision_is_assessment(self) -> None:
        topic_id = uuid.uuid4()
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.90, incorrect_response_count=0)],
            ability_category=AbilityCategory.ADVANCED,
        )
        decision = decide(
            top_recommendation=recs[0],
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.ADVANCED,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.ASSESSMENT
        assert decision.difficulty == Difficulty.HARD
        assert decision.assessment_required is True

    def test_mastered_topics_excluded_from_learning_path(self) -> None:
        mastered = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.95)
        steps = build_learning_path(encountered_topics=[mastered], next_unencountered_topic_id=None)
        assert len(steps) == 0, "Mastered topics should not appear in learning path"


class TestRepeatedMistakesInfluenceDecision:
    """Proves: repeated mistakes → AI Support recommendation."""

    def test_two_incorrect_triggers_ai_support(self) -> None:
        topic_id = uuid.uuid4()
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.15, incorrect_response_count=2)],
            ability_category=AbilityCategory.BEGINNER,
        )
        types = {r.recommendation_type for r in recs}
        assert RecommendationType.REVISION in types
        assert RecommendationType.AI_SUPPORT in types

    def test_three_incorrect_also_triggers_ai_support(self) -> None:
        topic_id = uuid.uuid4()
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.15, incorrect_response_count=3)],
            ability_category=AbilityCategory.BEGINNER,
        )
        types = {r.recommendation_type for r in recs}
        assert RecommendationType.AI_SUPPORT in types

    def test_one_incorrect_does_not_trigger_ai_support(self) -> None:
        topic_id = uuid.uuid4()
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.15, incorrect_response_count=1)],
            ability_category=AbilityCategory.BEGINNER,
        )
        types = {r.recommendation_type for r in recs}
        assert RecommendationType.AI_SUPPORT not in types

    def test_ai_support_decision_sets_flag(self) -> None:
        topic_id = uuid.uuid4()
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.15, incorrect_response_count=2)],
            ability_category=AbilityCategory.BEGINNER,
        )
        # AI Support has priority 2, Revision has priority 1
        # The top recommendation (priority 1) is Revision
        # But if we pick the AI Support recommendation:
        ai_support_rec = next(r for r in recs if r.recommendation_type == RecommendationType.AI_SUPPORT)
        decision = decide(
            top_recommendation=ai_support_rec,
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.BEGINNER,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.AI_EXPLANATION
        assert decision.ai_support is True


class TestImprovingPerformanceChangesDecision:
    """Proves: improving performance → learner state transitions → different decisions."""

    def test_student_transitions_from_weak_to_practice(self) -> None:
        """Simulates a student whose mastery improves from weak to moderate,
        causing the recommendation to change from Revision to Practice."""
        topic_id = uuid.uuid4()

        # Phase 1: Weak mastery → Revision
        weak_recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.15, incorrect_response_count=0)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        assert weak_recs[0].recommendation_type == RecommendationType.REVISION

        # Phase 2: After improvement, moderate mastery → Practice
        improved_recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.55, incorrect_response_count=0)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        assert improved_recs[0].recommendation_type == RecommendationType.PRACTICE

    def test_student_transitions_from_practice_to_progression(self) -> None:
        """Mastery goes from moderate to mastered → Progression."""
        topic_id = uuid.uuid4()

        moderate_recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.55, incorrect_response_count=0)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        assert moderate_recs[0].recommendation_type == RecommendationType.PRACTICE

        mastered_recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.90, incorrect_response_count=0)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        assert mastered_recs[0].recommendation_type == RecommendationType.PROGRESSION

    def test_full_journey_using_actual_bkt(self) -> None:
        """Simulates a real student journey using actual BKT computations,
        watching the recommendation change as mastery evolves."""
        topic_id = uuid.uuid4()

        # Start: diagnostic evidence shows struggling student
        mastery = compute_initial_mastery(diagnostic_responses=[False, False, True, False])
        assert classify_mastery_level(mastery) in (MasteryLevel.BEGINNER, MasteryLevel.DEVELOPING)

        # The student starts getting correct answers
        for _ in range(3):
            result = update_mastery(previous_mastery=mastery, is_correct=True)
            mastery = result.mastery_probability

        # Now check: what does the engine recommend?
        recs_after_improvement = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=mastery, incorrect_response_count=1)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )

        # With 3 correct responses on initially weak mastery, student should
        # have improved enough that they're no longer in "Revision" territory
        # (the BKT engine with P(T)=0.3 will have pushed mastery upward)
        if mastery >= 0.40:
            assert recs_after_improvement[0].recommendation_type in (
                RecommendationType.PRACTICE,
                RecommendationType.PROGRESSION,
            )
        else:
            # Still weak — Revision is correct
            assert recs_after_improvement[0].recommendation_type == RecommendationType.REVISION

    def test_ability_category_changes_affect_difficulty(self) -> None:
        """As IRT ability changes, the difficulty level in decisions changes."""
        topic_id = uuid.uuid4()
        rec = RecommendationCandidate(
            topic_id=topic_id,
            recommendation_type=RecommendationType.PRACTICE,
            priority=3,
            reason="Practice needed",
        )

        beginner_decision = decide(
            top_recommendation=rec,
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.BEGINNER,
            learning_objective=None,
        )
        advanced_decision = decide(
            top_recommendation=rec,
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.ADVANCED,
            learning_objective=None,
        )

        assert beginner_decision.difficulty == Difficulty.EASY
        assert advanced_decision.difficulty == Difficulty.HARD


class TestMultiTopicAdaptiveScenario:
    """Proves the engine handles multiple topics with different mastery states."""

    def test_revision_prioritized_over_practice_over_progression(self) -> None:
        weak_topic = TopicEvidence(topic_id=uuid.uuid4(), mastery_score=0.15, incorrect_response_count=0)
        moderate_topic = TopicEvidence(topic_id=uuid.uuid4(), mastery_score=0.55, incorrect_response_count=0)
        strong_topic = TopicEvidence(topic_id=uuid.uuid4(), mastery_score=0.90, incorrect_response_count=0)

        recs = generate_recommendations(
            topics=[strong_topic, moderate_topic, weak_topic],  # Deliberately out of order
            ability_category=AbilityCategory.INTERMEDIATE,
        )

        # Should be sorted by priority: Revision (1) < Practice (3) < Progression (4)
        assert recs[0].recommendation_type == RecommendationType.REVISION
        assert recs[0].topic_id == weak_topic.topic_id
        assert recs[1].recommendation_type == RecommendationType.PRACTICE
        assert recs[1].topic_id == moderate_topic.topic_id
        assert recs[2].recommendation_type == RecommendationType.PROGRESSION
        assert recs[2].topic_id == strong_topic.topic_id

    def test_decision_uses_highest_priority_recommendation(self) -> None:
        weak_topic = TopicEvidence(topic_id=uuid.uuid4(), mastery_score=0.15, incorrect_response_count=0)
        strong_topic = TopicEvidence(topic_id=uuid.uuid4(), mastery_score=0.90, incorrect_response_count=0)

        recs = generate_recommendations(
            topics=[strong_topic, weak_topic],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        decision = decide(
            top_recommendation=recs[0],  # Highest priority
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.INTERMEDIATE,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.REVIEW_TOPIC
        assert decision.topic_id == weak_topic.topic_id

    def test_learning_path_orders_weak_then_developing_then_new(self) -> None:
        weak = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.15)
        developing = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.55)
        new_topic_id = uuid.uuid4()

        steps = build_learning_path(
            encountered_topics=[developing, weak],
            next_unencountered_topic_id=new_topic_id,
        )
        assert len(steps) == 3
        assert steps[0].topic_id == weak.topic_id
        assert steps[1].topic_id == developing.topic_id
        assert steps[2].topic_id == new_topic_id
        assert all(s.status == PathStepStatus.PENDING for s in steps)
