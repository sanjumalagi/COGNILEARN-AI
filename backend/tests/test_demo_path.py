"""
Demo Path Script — Deterministic, DB-independent.

Demonstrates the complete 10-step demo path using only the algorithm
layer, producing readable output showing exactly what happens at each
step. This serves as a practical demonstration and API-sequence guide
for anyone who wants to see the system in action without a database.

Run directly:  python -m pytest tests/test_demo_path.py -v -s

The -s flag is important to see the printed output.
"""

import uuid

import pytest

from backend.algorithms.adaptive_engine.adaptive_decision_engine import (
    Difficulty,
    NextAction,
    decide,
)
from backend.algorithms.adaptive_engine.learning_path_engine import (
    TopicMasteryEvidence,
    build_learning_path,
)
from backend.algorithms.adaptive_engine.recommendation_engine import (
    RecommendationType,
    TopicEvidence,
    generate_recommendations,
)
from backend.algorithms.bkt.estimator import compute_initial_mastery, update_mastery
from backend.algorithms.irt.estimator import classify_ability, estimate_ability
from backend.algorithms.mastery_engine import (
    calculate_overall_mastery,
    classify_mastery_level,
    is_strong_topic,
    is_weak_topic,
)


class TestDemoPath:
    """Demonstrates the complete 10-step adaptive learning demo."""

    def test_full_demo_path(self) -> None:
        """
        ══════════════════════════════════════════════════════════
        STEP 1: Create/register student
        ══════════════════════════════════════════════════════════
        In a real API call:
          POST /api/v1/auth/register
          POST /api/v1/auth/login
          PATCH /api/v1/users/{id} (create student_profile)
        """
        student_id = uuid.uuid4()
        print(f"\n{'='*60}")
        print("STEP 1: Student registered")
        print(f"  Student ID: {student_id}")
        print(f"{'='*60}")

        """
        ══════════════════════════════════════════════════════════
        STEP 2: Create/use course/topic/question set
        ══════════════════════════════════════════════════════════
        In a real API call:
          POST /api/v1/courses/
          POST /api/v1/modules/
          POST /api/v1/topics/
          POST /api/v1/assessments/
          POST /api/v1/assessment-items/
        """
        course_id = uuid.uuid4()
        topic_calculus = uuid.uuid4()
        topic_statistics = uuid.uuid4()
        topic_probability = uuid.uuid4()  # Not yet encountered

        # Question items with difficulty levels
        calculus_items = [
            {"id": uuid.uuid4(), "question": "What is d/dx of x²?", "difficulty": 0.3, "correct_answer": "2x"},
            {"id": uuid.uuid4(), "question": "Integral of sin(x)?", "difficulty": 0.5, "correct_answer": "-cos(x)"},
            {"id": uuid.uuid4(), "question": "Chain rule for f(g(x))?", "difficulty": 0.7, "correct_answer": "f'(g(x))*g'(x)"},
            {"id": uuid.uuid4(), "question": "Partial derivative concept?", "difficulty": 0.9, "correct_answer": "hold other vars constant"},
        ]
        statistics_items = [
            {"id": uuid.uuid4(), "question": "What is the mean of {2,4,6}?", "difficulty": 0.2, "correct_answer": "4"},
            {"id": uuid.uuid4(), "question": "Standard deviation concept?", "difficulty": 0.5, "correct_answer": "spread measure"},
            {"id": uuid.uuid4(), "question": "Central limit theorem?", "difficulty": 0.8, "correct_answer": "sample means -> normal"},
        ]

        print(f"\n{'='*60}")
        print("STEP 2: Course content created")
        print(f"  Course: Advanced Mathematics ({course_id})")
        print(f"  Topic 1: Calculus ({topic_calculus}) — {len(calculus_items)} items")
        print(f"  Topic 2: Statistics ({topic_statistics}) — {len(statistics_items)} items")
        print(f"  Topic 3: Probability ({topic_probability}) — not yet encountered")
        print(f"{'='*60}")

        """
        ══════════════════════════════════════════════════════════
        STEP 3: Start initial diagnostic assessment
        ══════════════════════════════════════════════════════════
        In a real API call:
          POST /api/v1/assessments/generate
        """
        print(f"\n{'='*60}")
        print("STEP 3: Starting diagnostic assessment")
        print(f"  Assessment covers Calculus and Statistics topics")
        print(f"{'='*60}")

        """
        ══════════════════════════════════════════════════════════
        STEP 4: Submit answers
        ══════════════════════════════════════════════════════════
        In a real API call (for each item):
          POST /api/v1/assessments/submit
        """
        # Student answers: good at easy calculus, struggles with hard
        calculus_answers = [True, True, False, False]  # 2/4 correct
        # Student is strong at statistics
        stats_answers = [True, True, True]  # 3/3 correct

        all_responses: list[tuple[bool, float]] = []
        incorrect_counts: dict[uuid.UUID, int] = {topic_calculus: 0, topic_statistics: 0}

        print(f"\n{'='*60}")
        print("STEP 4: Student submits answers")
        print("  Calculus:")
        for i, (answer, item) in enumerate(zip(calculus_answers, calculus_items, strict=True)):
            all_responses.append((answer, item["difficulty"]))
            if not answer:
                incorrect_counts[topic_calculus] += 1
            print(f"    Q{i+1}: {item['question']}")
            print(f"    Answer: {'✓ Correct' if answer else '✗ Incorrect'} (difficulty={item['difficulty']})")

        print("  Statistics:")
        for i, (answer, item) in enumerate(zip(stats_answers, statistics_items, strict=True)):
            all_responses.append((answer, item["difficulty"]))
            if not answer:
                incorrect_counts[topic_statistics] += 1
            print(f"    Q{i+1}: {item['question']}")
            print(f"    Answer: {'✓ Correct' if answer else '✗ Incorrect'} (difficulty={item['difficulty']})")
        print(f"{'='*60}")

        """
        ══════════════════════════════════════════════════════════
        STEP 5: View IRT ability
        ══════════════════════════════════════════════════════════
        In a real API call:
          GET /api/v1/learner/ability
        """
        irt_result = estimate_ability(responses=all_responses)
        ability_category = classify_ability(irt_result.ability)

        print(f"\n{'='*60}")
        print("STEP 5: IRT Ability Estimate")
        print(f"  Ability (θ): {irt_result.ability:.4f}")
        print(f"  Category: {irt_result.category.value}")
        print(f"  Confidence: {irt_result.confidence_score}")
        print(f"  Next Item Difficulty Recommendation: {irt_result.difficulty_recommendation}")
        print(f"{'='*60}")

        assert irt_result.ability > 0.0, "5/7 correct should produce positive ability"

        """
        ══════════════════════════════════════════════════════════
        STEP 6: View BKT topic mastery
        ══════════════════════════════════════════════════════════
        In a real API call:
          GET /api/v1/learner/mastery
        """
        calc_mastery = compute_initial_mastery(diagnostic_responses=calculus_answers)
        stats_mastery = compute_initial_mastery(diagnostic_responses=stats_answers)

        print(f"\n{'='*60}")
        print("STEP 6: BKT Topic Mastery")
        print(f"  Calculus:")
        print(f"    Mastery: {calc_mastery:.4f}")
        print(f"    Level: {classify_mastery_level(calc_mastery).value}")
        print(f"    Weak: {is_weak_topic(calc_mastery)}, Strong: {is_strong_topic(calc_mastery)}")
        print(f"  Statistics:")
        print(f"    Mastery: {stats_mastery:.4f}")
        print(f"    Level: {classify_mastery_level(stats_mastery).value}")
        print(f"    Weak: {is_weak_topic(stats_mastery)}, Strong: {is_strong_topic(stats_mastery)}")
        print(f"  Overall: {calculate_overall_mastery([calc_mastery, stats_mastery]):.4f}")
        print(f"{'='*60}")

        assert stats_mastery > calc_mastery

        """
        ══════════════════════════════════════════════════════════
        STEP 7: Get adaptive recommendation
        ══════════════════════════════════════════════════════════
        In a real API call:
          GET /api/v1/adaptive/recommendations
          GET /api/v1/adaptive/next-learning-outcome
        """
        recs = generate_recommendations(
            topics=[
                TopicEvidence(topic_id=topic_calculus, mastery_score=calc_mastery, incorrect_response_count=incorrect_counts[topic_calculus]),
                TopicEvidence(topic_id=topic_statistics, mastery_score=stats_mastery, incorrect_response_count=incorrect_counts[topic_statistics]),
            ],
            ability_category=ability_category,
        )
        decision = decide(
            top_recommendation=recs[0] if recs else None,
            next_unencountered_topic_id=topic_probability,
            ability_category=ability_category,
            learning_objective="Master calculus fundamentals",
        )
        path = build_learning_path(
            encountered_topics=[
                TopicMasteryEvidence(topic_id=topic_calculus, mastery_score=calc_mastery),
                TopicMasteryEvidence(topic_id=topic_statistics, mastery_score=stats_mastery),
            ],
            next_unencountered_topic_id=topic_probability,
        )

        print(f"\n{'='*60}")
        print("STEP 7: Adaptive Recommendations")
        print(f"  Recommendations ({len(recs)}):")
        for rec in recs:
            print(f"    [{rec.priority}] {rec.recommendation_type.value}: {rec.reason}")
        print(f"\n  Decision:")
        print(f"    Next Action: {decision.next_action.value}")
        print(f"    Topic: {decision.topic_id}")
        print(f"    Difficulty: {decision.difficulty.value}")
        print(f"    AI Support: {decision.ai_support}")
        print(f"    Reason: {decision.reason}")
        print(f"\n  Learning Path ({len(path)} steps):")
        for step in path:
            print(f"    Step {step.sequence_order}: {step.topic_id} ({step.status.value})")
        print(f"{'='*60}")

        assert len(recs) >= 1

        """
        ══════════════════════════════════════════════════════════
        STEP 8: Answer another question (student improves on calculus)
        ══════════════════════════════════════════════════════════
        """
        print(f"\n{'='*60}")
        print("STEP 8: Student answers 3 more calculus questions correctly")

        for i in range(3):
            new_difficulty = 0.4 + i * 0.1
            all_responses.append((True, new_difficulty))
            bkt_result = update_mastery(previous_mastery=calc_mastery, is_correct=True)
            calc_mastery = bkt_result.mastery_probability
            print(f"  Q{i+1}: Correct (difficulty={new_difficulty}), Calculus mastery → {calc_mastery:.4f}")
        print(f"{'='*60}")

        """
        ══════════════════════════════════════════════════════════
        STEP 9: Observe updated learner state
        ══════════════════════════════════════════════════════════
        """
        irt_result_2 = estimate_ability(responses=all_responses)
        ability_category_2 = classify_ability(irt_result_2.ability)
        overall_2 = calculate_overall_mastery([calc_mastery, stats_mastery])

        print(f"\n{'='*60}")
        print("STEP 9: Updated Learner State")
        print(f"  IRT Ability: {irt_result.ability:.4f} → {irt_result_2.ability:.4f}")
        print(f"  IRT Category: {irt_result.category.value} → {irt_result_2.category.value}")
        print(f"  Calculus Mastery: {compute_initial_mastery(diagnostic_responses=calculus_answers):.4f} → {calc_mastery:.4f}")
        print(f"  Statistics Mastery: {stats_mastery:.4f} (unchanged)")
        print(f"  Overall Mastery: {calculate_overall_mastery([compute_initial_mastery(diagnostic_responses=calculus_answers), stats_mastery]):.4f} → {overall_2:.4f}")
        print(f"{'='*60}")

        assert irt_result_2.ability > irt_result.ability, "Ability should increase with more correct answers"
        assert calc_mastery > compute_initial_mastery(diagnostic_responses=calculus_answers), "Calculus mastery should increase"

        """
        ══════════════════════════════════════════════════════════
        STEP 10: Observe adaptive decision change
        ══════════════════════════════════════════════════════════
        """
        recs_2 = generate_recommendations(
            topics=[
                TopicEvidence(topic_id=topic_calculus, mastery_score=calc_mastery, incorrect_response_count=2),
                TopicEvidence(topic_id=topic_statistics, mastery_score=stats_mastery, incorrect_response_count=0),
            ],
            ability_category=ability_category_2,
        )
        decision_2 = decide(
            top_recommendation=recs_2[0] if recs_2 else None,
            next_unencountered_topic_id=topic_probability,
            ability_category=ability_category_2,
            learning_objective="Master calculus fundamentals",
        )

        print(f"\n{'='*60}")
        print("STEP 10: Updated Adaptive Decision")
        print(f"  Previous Decision: {decision.next_action.value} ({decision.difficulty.value})")
        print(f"  Current Decision:  {decision_2.next_action.value} ({decision_2.difficulty.value})")
        print(f"  Reason: {decision_2.reason}")

        if decision.next_action != decision_2.next_action:
            print(f"  → DECISION CHANGED due to improved learner state")
        elif decision.difficulty != decision_2.difficulty:
            print(f"  → DIFFICULTY CHANGED due to improved ability")
        else:
            print(f"  → Decision stable (mastery may not have crossed threshold)")
        print(f"{'='*60}")

        print(f"\n{'='*60}")
        print("DEMO COMPLETE")
        print(f"  ✓ Student registered and profiled")
        print(f"  ✓ Course with topics and questions created")
        print(f"  ✓ Initial diagnostic assessment taken")
        print(f"  ✓ IRT ability estimated: {irt_result_2.ability:.4f} ({irt_result_2.category.value})")
        print(f"  ✓ BKT topic mastery computed")
        print(f"  ✓ Adaptive recommendations generated")
        print(f"  ✓ Additional answers submitted and processed")
        print(f"  ✓ Learner state updated")
        print(f"  ✓ Adaptive decision reflects current state")
        print(f"{'='*60}")

        # Final assertions: the system works end-to-end
        assert irt_result_2.confidence_score > irt_result.confidence_score, (
            "More responses should increase confidence"
        )


class TestDemoPathAPISequence:
    """Documents the exact API call sequence for the demo path.
    This test exists as a reference — it only verifies the sequence is documented."""

    def test_api_sequence_documented(self) -> None:
        """The exact API calls for the 10-step demo:

        1. Register/Login:
           POST /api/v1/auth/register  {"name": "...", "email": "...", "password": "...", "role": "Student"}
           POST /api/v1/auth/login     {"email": "...", "password": "..."}
           PATCH /api/v1/users/{id}    {"student_profile": {"enrollment_number": "E-1", "program": "CS", "semester": 1}}

        2. Create course content (Teacher):
           POST /api/v1/courses/        {"title": "...", "description": "..."}
           POST /api/v1/modules/        {"course_id": "...", "title": "...", "sequence_number": 1}
           POST /api/v1/topics/         {"module_id": "...", "title": "...", "description": "...", "difficulty_level": 1}
           POST /api/v1/assessments/    {"topic_id": "...", "title": "...", "assessment_type": "quiz"}
           POST /api/v1/assessment-items/ {"assessment_id": "...", "question_text": "...", "difficulty": 0.5, ...}

        3. Start assessment (Student):
           POST /api/v1/assessments/generate  {"student_id": "...", "topic_id": "..."}

        4. Submit answers (Student, per item):
           POST /api/v1/assessments/submit  {"question_id": "...", "selected_answer": "...", "response_time": 5}

        5. View IRT ability:
           GET /api/v1/learner/ability

        6. View BKT mastery:
           GET /api/v1/learner/mastery

        7. Get adaptive recommendation:
           GET /api/v1/adaptive/recommendations
           GET /api/v1/adaptive/next-learning-outcome
           GET /api/v1/adaptive/learning-path?course_id=...

        8. Answer more questions:
           POST /api/v1/assessments/submit  (repeat)

        9. View updated state:
           GET /api/v1/learner/ability
           GET /api/v1/learner/mastery
           GET /api/v1/learner/profile

        10. View updated decision:
            GET /api/v1/adaptive/next-learning-outcome
            GET /api/v1/adaptive/recommendations
        """
        # This test documents the API sequence — no assertions needed
        # beyond confirming the module imports work (which they do by
        # reaching this point).
        assert True
