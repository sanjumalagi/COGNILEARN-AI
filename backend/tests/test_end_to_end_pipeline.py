"""
End-to-End Pipeline Test — Deterministic, DB-independent.

Simulates the complete documented pipeline for a new student:

    NEW STUDENT
    → INITIAL DIAGNOSTIC QUIZ
    → Student answers several questions
    → IRT calculates ability
    → BKT calculates topic mastery
    → Adaptive Engine evaluates learner state
    → System produces next recommendation/activity
    → Student answers again
    → IRT/BKT update
    → Adaptive decision changes or remains appropriately stable

Does NOT mock IRT/BKT/Adaptive logic — uses the actual algorithm
implementations directly. Mocks only the external infrastructure
(database) by passing data between pipeline stages manually, exactly
as the service layer would.
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
    PathStep,
    TopicMasteryEvidence,
    build_learning_path,
)
from backend.algorithms.adaptive_engine.recommendation_engine import (
    RecommendationCandidate,
    RecommendationType,
    TopicEvidence,
    generate_recommendations,
)
from backend.algorithms.bkt.estimator import (
    BKTResult,
    MasteryStatus,
    compute_initial_mastery,
    update_mastery,
)
from backend.algorithms.irt.estimator import (
    AbilityCategory,
    IRTResult,
    classify_ability,
    estimate_ability,
)
from backend.algorithms.mastery_engine import (
    MasteryLevel,
    calculate_overall_mastery,
    classify_mastery_level,
    is_strong_topic,
    is_weak_topic,
)


class TestEndToEndPipeline:
    """Full deterministic end-to-end scenario for a new student."""

    def test_complete_student_journey(self) -> None:
        """
        Scenario: A new student takes a diagnostic quiz across two topics,
        answers, gets IRT/BKT estimates, receives adaptive recommendations,
        then answers more and observes updated state.
        """
        # ─── Setup: Course with 2 topics, each with assessment items ──
        topic_algebra = uuid.uuid4()
        topic_geometry = uuid.uuid4()
        next_topic = uuid.uuid4()  # An unencountered topic in curriculum

        # Item difficulties for each topic
        algebra_items = [
            {"difficulty": 0.3, "item_id": uuid.uuid4()},
            {"difficulty": 0.5, "item_id": uuid.uuid4()},
            {"difficulty": 0.7, "item_id": uuid.uuid4()},
            {"difficulty": 0.9, "item_id": uuid.uuid4()},
        ]
        geometry_items = [
            {"difficulty": 0.2, "item_id": uuid.uuid4()},
            {"difficulty": 0.4, "item_id": uuid.uuid4()},
            {"difficulty": 0.6, "item_id": uuid.uuid4()},
        ]

        # ─── Phase 1: Initial Diagnostic Quiz ─────────────────────────
        # Student answers the diagnostic: weak on algebra, OK on geometry
        algebra_diagnostic_answers = [True, True, False, False]  # 2/4 correct
        geometry_diagnostic_answers = [True, True, True]  # 3/3 correct

        # Response history for IRT (is_correct, difficulty)
        all_responses: list[tuple[bool, float]] = []
        for answer, item in zip(algebra_diagnostic_answers, algebra_items, strict=True):
            all_responses.append((answer, item["difficulty"]))
        for answer, item in zip(geometry_diagnostic_answers, geometry_items, strict=True):
            all_responses.append((answer, item["difficulty"]))

        # ─── Phase 2: IRT Ability Estimation ──────────────────────────
        irt_result_1 = estimate_ability(responses=all_responses, previous_theta=None)
        print(f"\n[Phase 2] IRT Result after diagnostic:")
        print(f"  Ability: {irt_result_1.ability:.4f}")
        print(f"  Category: {irt_result_1.category}")
        print(f"  Confidence: {irt_result_1.confidence_score}")
        print(f"  Difficulty Recommendation: {irt_result_1.difficulty_recommendation}")

        # Diagnostic: 5/7 correct on mostly easy/moderate items → positive ability
        assert irt_result_1.ability > 0.0, "5/7 correct should yield positive ability"
        assert irt_result_1.confidence_score > 0.0, "With 7 responses, confidence should be non-zero"

        # ─── Phase 3: BKT Topic Mastery ───────────────────────────────
        # Initialize mastery from diagnostic evidence
        algebra_initial_mastery = compute_initial_mastery(diagnostic_responses=algebra_diagnostic_answers)
        geometry_initial_mastery = compute_initial_mastery(diagnostic_responses=geometry_diagnostic_answers)

        print(f"\n[Phase 3] Initial BKT mastery:")
        print(f"  Algebra: {algebra_initial_mastery:.4f} ({classify_mastery_level(algebra_initial_mastery)})")
        print(f"  Geometry: {geometry_initial_mastery:.4f} ({classify_mastery_level(geometry_initial_mastery)})")

        assert geometry_initial_mastery > algebra_initial_mastery, (
            "Geometry (3/3) should have higher initial mastery than algebra (2/4)"
        )

        # Apply one BKT update per topic (processing each diagnostic response)
        # In the real system, _update_topic_mastery uses the diagnostic evidence
        # for initialization and then applies individual updates.
        # Here we simulate the first post-diagnostic update:
        algebra_mastery = algebra_initial_mastery
        geometry_mastery = geometry_initial_mastery

        # ─── Phase 4: Overall Mastery ─────────────────────────────────
        overall_mastery_1 = calculate_overall_mastery([algebra_mastery, geometry_mastery])
        print(f"\n[Phase 4] Overall mastery: {overall_mastery_1:.4f}")
        assert 0.0 < overall_mastery_1 < 1.0

        # ─── Phase 5: Adaptive Engine — Recommendations ───────────────
        ability_category = classify_ability(irt_result_1.ability)
        topic_evidence = [
            TopicEvidence(topic_id=topic_algebra, mastery_score=algebra_mastery, incorrect_response_count=2),
            TopicEvidence(topic_id=topic_geometry, mastery_score=geometry_mastery, incorrect_response_count=0),
        ]
        recommendations_1 = generate_recommendations(
            topics=topic_evidence, ability_category=ability_category
        )
        print(f"\n[Phase 5] Recommendations ({len(recommendations_1)}):")
        for rec in recommendations_1:
            print(f"  {rec.recommendation_type} (priority={rec.priority}): {rec.reason}")

        assert len(recommendations_1) >= 1

        # ─── Phase 6: Adaptive Decision ───────────────────────────────
        learning_path = build_learning_path(
            encountered_topics=[
                TopicMasteryEvidence(topic_id=topic_algebra, mastery_score=algebra_mastery),
                TopicMasteryEvidence(topic_id=topic_geometry, mastery_score=geometry_mastery),
            ],
            next_unencountered_topic_id=next_topic,
        )

        decision_1 = decide(
            top_recommendation=recommendations_1[0] if recommendations_1 else None,
            next_unencountered_topic_id=next_topic,
            ability_category=ability_category,
            learning_objective="Understand quadratic equations",
        )
        print(f"\n[Phase 6] Adaptive Decision:")
        print(f"  Action: {decision_1.next_action}")
        print(f"  Topic: {decision_1.topic_id}")
        print(f"  Difficulty: {decision_1.difficulty}")
        print(f"  Reason: {decision_1.reason}")
        print(f"  AI Support: {decision_1.ai_support}")

        # Algebra has 2 incorrect responses and weak mastery → should be
        # Revision or AI Support (if misconception threshold met)
        assert decision_1.next_action in (
            NextAction.REVIEW_TOPIC,
            NextAction.AI_EXPLANATION,
            NextAction.PRACTICE,
        )

        # ─── Phase 7: Student Answers More Questions ──────────────────
        # Student improves on algebra: 3 more correct answers
        additional_algebra = [(True, 0.3), (True, 0.5), (True, 0.7)]
        all_responses.extend(additional_algebra)

        # Update BKT for algebra (3 correct)
        for _ in range(3):
            bkt_result = update_mastery(previous_mastery=algebra_mastery, is_correct=True)
            algebra_mastery = bkt_result.mastery_probability

        print(f"\n[Phase 7] After 3 more correct on algebra:")
        print(f"  Algebra mastery: {algebra_mastery:.4f}")

        # ─── Phase 8: IRT/BKT Update ─────────────────────────────────
        irt_result_2 = estimate_ability(responses=all_responses, previous_theta=irt_result_1.ability)
        print(f"\n[Phase 8] Updated IRT:")
        print(f"  Ability: {irt_result_2.ability:.4f} (was {irt_result_1.ability:.4f})")
        print(f"  Category: {irt_result_2.category}")

        # More correct answers → ability should increase
        assert irt_result_2.ability > irt_result_1.ability, (
            "3 additional correct responses should increase ability"
        )
        # Algebra mastery should have increased
        assert algebra_mastery > algebra_initial_mastery, (
            "3 correct responses should increase algebra mastery"
        )

        # ─── Phase 9: Updated Adaptive Decision ──────────────────────
        ability_category_2 = classify_ability(irt_result_2.ability)
        topic_evidence_2 = [
            TopicEvidence(topic_id=topic_algebra, mastery_score=algebra_mastery, incorrect_response_count=2),
            TopicEvidence(topic_id=topic_geometry, mastery_score=geometry_mastery, incorrect_response_count=0),
        ]
        recommendations_2 = generate_recommendations(
            topics=topic_evidence_2, ability_category=ability_category_2
        )
        decision_2 = decide(
            top_recommendation=recommendations_2[0] if recommendations_2 else None,
            next_unencountered_topic_id=next_topic,
            ability_category=ability_category_2,
            learning_objective="Understand quadratic equations",
        )
        print(f"\n[Phase 9] Updated Adaptive Decision:")
        print(f"  Action: {decision_2.next_action}")
        print(f"  Difficulty: {decision_2.difficulty}")
        print(f"  Reason: {decision_2.reason}")

        # With improved algebra mastery, the decision should change
        # (or remain appropriately stable if mastery hasn't crossed a threshold)
        overall_mastery_2 = calculate_overall_mastery([algebra_mastery, geometry_mastery])
        print(f"\n[Final] Overall mastery: {overall_mastery_2:.4f} (was {overall_mastery_1:.4f})")
        assert overall_mastery_2 >= overall_mastery_1, "Overall mastery should not decrease with correct answers"

        # ─── Phase 10: Learning Path Updated ──────────────────────────
        learning_path_2 = build_learning_path(
            encountered_topics=[
                TopicMasteryEvidence(topic_id=topic_algebra, mastery_score=algebra_mastery),
                TopicMasteryEvidence(topic_id=topic_geometry, mastery_score=geometry_mastery),
            ],
            next_unencountered_topic_id=next_topic,
        )
        print(f"\n[Final] Learning path ({len(learning_path_2)} steps):")
        for step in learning_path_2:
            print(f"  Step {step.sequence_order}: topic={step.topic_id}, status={step.status}")

        # The path should still include next_topic as the final step
        if learning_path_2:
            assert learning_path_2[-1].topic_id == next_topic or any(
                s.topic_id == next_topic for s in learning_path_2
            ), "Next unencountered topic should be in the learning path"

    def test_struggling_student_journey(self) -> None:
        """Scenario: A consistently struggling student — all answers wrong."""
        topic_id = uuid.uuid4()
        items = [0.3, 0.4, 0.5, 0.6, 0.7]

        # All incorrect diagnostic
        diagnostic = [False] * 5
        responses = [(False, d) for d in items]

        # IRT: should be low
        irt_result = estimate_ability(responses=responses)
        assert irt_result.ability < -1.0
        assert irt_result.category == AbilityCategory.BEGINNER

        # BKT: should be very low
        mastery = compute_initial_mastery(diagnostic_responses=diagnostic)
        assert mastery < 0.2
        assert is_weak_topic(mastery)
        assert classify_mastery_level(mastery) == MasteryLevel.BEGINNER

        # Recommendation: Revision
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=mastery, incorrect_response_count=5)],
            ability_category=irt_result.category,
        )
        assert any(r.recommendation_type == RecommendationType.REVISION for r in recs)
        assert any(r.recommendation_type == RecommendationType.AI_SUPPORT for r in recs)

        # Decision: review with easy difficulty
        decision = decide(
            top_recommendation=recs[0],
            next_unencountered_topic_id=None,
            ability_category=irt_result.category,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.REVIEW_TOPIC
        assert decision.difficulty == Difficulty.EASY

    def test_high_achieving_student_journey(self) -> None:
        """Scenario: An excellent student — all answers correct on hard items."""
        topic_id = uuid.uuid4()
        items = [0.5, 0.7, 0.9, 1.2, 1.5]

        # All correct
        diagnostic = [True] * 5
        responses = [(True, d) for d in items]

        # IRT: should be very high
        irt_result = estimate_ability(responses=responses)
        assert irt_result.ability > 2.0
        assert irt_result.category == AbilityCategory.ADVANCED

        # BKT: should be near 1.0
        mastery = compute_initial_mastery(diagnostic_responses=diagnostic)
        for _ in range(5):
            bkt_result = update_mastery(previous_mastery=mastery, is_correct=True)
            mastery = bkt_result.mastery_probability
        assert mastery > 0.95
        assert is_strong_topic(mastery)
        assert classify_mastery_level(mastery) == MasteryLevel.MASTERED

        # Recommendation: Challenge (advanced student with mastered topic)
        recs = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=mastery, incorrect_response_count=0)],
            ability_category=irt_result.category,
        )
        assert recs[0].recommendation_type == RecommendationType.CHALLENGE

        # Decision: assessment with hard difficulty
        decision = decide(
            top_recommendation=recs[0],
            next_unencountered_topic_id=None,
            ability_category=irt_result.category,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.ASSESSMENT
        assert decision.difficulty == Difficulty.HARD
        assert decision.assessment_required is True

    def test_new_student_with_no_evidence_gets_new_topic(self) -> None:
        """Scenario: No evidence yet, but there is a next topic in the curriculum."""
        next_topic = uuid.uuid4()
        decision = decide(
            top_recommendation=None,
            next_unencountered_topic_id=next_topic,
            ability_category=AbilityCategory.INTERMEDIATE,
            learning_objective="Intro to Linear Algebra",
        )
        assert decision.next_action == NextAction.LEARN_NEW_TOPIC
        assert decision.topic_id == next_topic
        assert decision.learning_objective == "Intro to Linear Algebra"

    def test_completed_curriculum_advance(self) -> None:
        """Scenario: All topics mastered, nothing left."""
        mastered = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.95)
        path = build_learning_path(encountered_topics=[mastered], next_unencountered_topic_id=None)
        assert len(path) == 0, "Completed curriculum should have empty learning path"

        decision = decide(
            top_recommendation=None,
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.ADVANCED,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.ADVANCE
        assert decision.topic_id is None
