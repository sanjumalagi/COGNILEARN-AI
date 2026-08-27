"""
Module 8 — Adaptive Intelligence Tests.

Covers the Recommendation Engine, Learning Path Engine, and Adaptive
Decision Engine rule logic, plus the 4 documented GET /adaptive/*
endpoints end-to-end.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from backend.algorithms.adaptive_engine.adaptive_decision_engine import Difficulty, NextAction, decide
from backend.algorithms.adaptive_engine.learning_path_engine import TopicMasteryEvidence, build_learning_path
from backend.algorithms.adaptive_engine.recommendation_engine import (
    RecommendationCandidate,
    RecommendationType,
    TopicEvidence,
    generate_recommendations,
)
from backend.algorithms.irt.estimator import AbilityCategory
from backend.main import app

client = TestClient(app)

VALID_PASSWORD = "Str0ng!Pass"


def _unique_email() -> str:
    return f"user{uuid.uuid4().hex}@example.com"


def _register_and_login(role: str = "Student") -> tuple[str, dict]:
    email = _unique_email()
    register = client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": email, "password": VALID_PASSWORD, "role": role},
    )
    user_id = register.json()["user_id"]
    login = client.post("/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD})
    return user_id, {"Authorization": f"Bearer {login.json()['access_token']}"}


def _teacher_headers() -> dict:
    return _register_and_login(role="Teacher")[1]


def _student() -> dict:
    user_id, headers = _register_and_login(role="Student")
    client.patch(
        f"/api/v1/users/{user_id}",
        json={"student_profile": {"enrollment_number": "E-1", "program": "CS", "semester": 1}},
        headers=headers,
    )
    return headers


def _build_course_with_topics(teacher_headers: dict, topic_count: int = 2) -> tuple[dict, list[dict]]:
    course = client.post(
        "/api/v1/courses/", json={"title": "C", "description": "d"}, headers=teacher_headers
    ).json()
    module = client.post(
        "/api/v1/modules/",
        json={"course_id": course["course_id"], "title": "M", "sequence_number": 1},
        headers=teacher_headers,
    ).json()
    topics = [
        client.post(
            "/api/v1/topics/",
            json={
                "module_id": module["module_id"],
                "title": f"Topic {i}",
                "description": "d",
                "difficulty_level": 1,
            },
            headers=teacher_headers,
        ).json()
        for i in range(topic_count)
    ]
    return course, topics


def _create_item_for_topic(teacher_headers: dict, topic_id: str) -> tuple[dict, dict]:
    assessment = client.post(
        "/api/v1/assessments/",
        json={"topic_id": topic_id, "title": "Quiz", "assessment_type": "quiz"},
        headers=teacher_headers,
    ).json()
    item = client.post(
        "/api/v1/assessment-items/",
        json={
            "assessment_id": assessment["assessment_id"],
            "question_text": "Q",
            "difficulty": 0.3,
            "bloom_level": "Remember",
            "correct_answer": "yes",
            "explanation": "x",
        },
        headers=teacher_headers,
    ).json()
    return assessment, item


class TestRecommendationEngineRules:
    def test_weak_topic_generates_revision(self) -> None:
        topic_id = uuid.uuid4()
        result = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.2, incorrect_response_count=0)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        assert len(result) == 1
        assert result[0].recommendation_type == RecommendationType.REVISION
        assert result[0].priority == 1

    def test_weak_topic_with_persistent_errors_also_generates_ai_support(self) -> None:
        topic_id = uuid.uuid4()
        result = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.2, incorrect_response_count=2)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        types = {r.recommendation_type for r in result}
        assert types == {RecommendationType.REVISION, RecommendationType.AI_SUPPORT}

    def test_weak_topic_with_single_error_does_not_trigger_ai_support(self) -> None:
        topic_id = uuid.uuid4()
        result = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.2, incorrect_response_count=1)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        assert len(result) == 1

    def test_moderate_topic_generates_practice(self) -> None:
        topic_id = uuid.uuid4()
        result = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.6, incorrect_response_count=0)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        assert result[0].recommendation_type == RecommendationType.PRACTICE

    def test_mastered_topic_with_advanced_ability_generates_challenge(self) -> None:
        topic_id = uuid.uuid4()
        result = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.9, incorrect_response_count=0)],
            ability_category=AbilityCategory.ADVANCED,
        )
        assert result[0].recommendation_type == RecommendationType.CHALLENGE

    def test_mastered_topic_with_non_advanced_ability_generates_progression(self) -> None:
        topic_id = uuid.uuid4()
        result = generate_recommendations(
            topics=[TopicEvidence(topic_id=topic_id, mastery_score=0.9, incorrect_response_count=0)],
            ability_category=AbilityCategory.INTERMEDIATE,
        )
        assert result[0].recommendation_type == RecommendationType.PROGRESSION

    def test_results_sorted_by_priority(self) -> None:
        weak = TopicEvidence(topic_id=uuid.uuid4(), mastery_score=0.1, incorrect_response_count=0)
        mastered = TopicEvidence(topic_id=uuid.uuid4(), mastery_score=0.9, incorrect_response_count=0)
        result = generate_recommendations(
            topics=[mastered, weak], ability_category=AbilityCategory.INTERMEDIATE
        )
        priorities = [r.priority for r in result]
        assert priorities == sorted(priorities)


class TestLearningPathEngineRules:
    def test_weak_topics_come_before_developing_topics(self) -> None:
        weak = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.2)
        developing = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.6)
        steps = build_learning_path(
            encountered_topics=[developing, weak], next_unencountered_topic_id=None
        )
        assert steps[0].topic_id == weak.topic_id
        assert steps[1].topic_id == developing.topic_id

    def test_mastered_topics_are_excluded(self) -> None:
        mastered = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.95)
        steps = build_learning_path(encountered_topics=[mastered], next_unencountered_topic_id=None)
        assert steps == []

    def test_next_unencountered_topic_appended_last(self) -> None:
        weak = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.2)
        next_topic_id = uuid.uuid4()
        steps = build_learning_path(encountered_topics=[weak], next_unencountered_topic_id=next_topic_id)
        assert steps[-1].topic_id == next_topic_id

    def test_sequence_order_is_contiguous_from_one(self) -> None:
        topics = [TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.2) for _ in range(3)]
        steps = build_learning_path(encountered_topics=topics, next_unencountered_topic_id=None)
        assert [s.sequence_order for s in steps] == [1, 2, 3]

    def test_worst_mastery_scores_first_within_weak_group(self) -> None:
        worse = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.1)
        less_bad = TopicMasteryEvidence(topic_id=uuid.uuid4(), mastery_score=0.3)
        steps = build_learning_path(encountered_topics=[less_bad, worse], next_unencountered_topic_id=None)
        assert steps[0].topic_id == worse.topic_id


class TestAdaptiveDecisionEngineRules:
    def test_revision_recommendation_maps_to_review_topic(self) -> None:
        rec = RecommendationCandidate(
            topic_id=uuid.uuid4(), recommendation_type=RecommendationType.REVISION, priority=1, reason="r"
        )
        decision = decide(
            top_recommendation=rec,
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.INTERMEDIATE,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.REVIEW_TOPIC
        assert decision.ai_support is False

    def test_ai_support_recommendation_maps_to_ai_explanation(self) -> None:
        rec = RecommendationCandidate(
            topic_id=uuid.uuid4(), recommendation_type=RecommendationType.AI_SUPPORT, priority=2, reason="r"
        )
        decision = decide(
            top_recommendation=rec,
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.INTERMEDIATE,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.AI_EXPLANATION
        assert decision.ai_support is True

    def test_challenge_recommendation_forces_hard_difficulty(self) -> None:
        rec = RecommendationCandidate(
            topic_id=uuid.uuid4(), recommendation_type=RecommendationType.CHALLENGE, priority=5, reason="r"
        )
        decision = decide(
            top_recommendation=rec,
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.INTERMEDIATE,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.ASSESSMENT
        assert decision.difficulty == Difficulty.HARD
        assert decision.assessment_required is True

    def test_no_recommendation_but_new_topic_available(self) -> None:
        next_topic_id = uuid.uuid4()
        decision = decide(
            top_recommendation=None,
            next_unencountered_topic_id=next_topic_id,
            ability_category=AbilityCategory.BEGINNER,
            learning_objective="Understand X",
        )
        assert decision.next_action == NextAction.LEARN_NEW_TOPIC
        assert decision.topic_id == next_topic_id
        assert decision.difficulty == Difficulty.EASY

    def test_nothing_pending_falls_back_to_advance(self) -> None:
        decision = decide(
            top_recommendation=None,
            next_unencountered_topic_id=None,
            ability_category=AbilityCategory.INTERMEDIATE,
            learning_objective=None,
        )
        assert decision.next_action == NextAction.ADVANCE
        assert decision.topic_id is None

    @pytest.mark.parametrize(
        ("ability", "expected_difficulty"),
        [
            (AbilityCategory.BEGINNER, Difficulty.EASY),
            (AbilityCategory.INTERMEDIATE, Difficulty.MEDIUM),
            (AbilityCategory.ADVANCED, Difficulty.HARD),
        ],
    )
    def test_difficulty_matches_ability_category(self, ability, expected_difficulty) -> None:
        decision = decide(
            top_recommendation=None,
            next_unencountered_topic_id=None,
            ability_category=ability,
            learning_objective=None,
        )
        assert decision.difficulty == expected_difficulty


class TestRecommendationsEndpoint:
    def test_weak_topic_produces_revision_and_ai_support(self) -> None:
        teacher = _teacher_headers()
        course, topics = _build_course_with_topics(teacher, topic_count=1)
        _, item = _create_item_for_topic(teacher, topics[0]["topic_id"])
        student = _student()

        for _ in range(2):
            client.post(
                "/api/v1/assessments/submit",
                json={"question_id": item["item_id"], "selected_answer": "no", "response_time": 3},
                headers=student,
            )

        response = client.get("/api/v1/adaptive/recommendations", headers=student)
        assert response.status_code == 200
        body = response.json()
        types = {r["recommendation_type"] for r in body["items"]}
        assert types == {"Revision", "AI Support"}

    def test_recommendations_regenerate_on_each_call(self) -> None:
        teacher = _teacher_headers()
        course, topics = _build_course_with_topics(teacher, topic_count=1)
        _, item = _create_item_for_topic(teacher, topics[0]["topic_id"])
        student = _student()

        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "no", "response_time": 3},
            headers=student,
        )
        first = client.get("/api/v1/adaptive/recommendations", headers=student).json()

        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "yes", "response_time": 3},
            headers=student,
        )
        second = client.get("/api/v1/adaptive/recommendations", headers=student).json()

        first_ids = {r["recommendation_id"] for r in first["items"]}
        second_ids = {r["recommendation_id"] for r in second["items"]}
        assert first_ids != second_ids  # stale recommendations replaced, not accumulated

    def test_teacher_cannot_access_recommendations(self) -> None:
        teacher = _teacher_headers()
        response = client.get("/api/v1/adaptive/recommendations", headers=teacher)
        assert response.status_code == 403

    def test_requires_auth(self) -> None:
        response = client.get("/api/v1/adaptive/recommendations")
        assert response.status_code == 401


class TestRevisionPlanEndpoint:
    def test_only_returns_weak_topic_types(self) -> None:
        teacher = _teacher_headers()
        course, topics = _build_course_with_topics(teacher, topic_count=2)
        _, weak_item = _create_item_for_topic(teacher, topics[0]["topic_id"])
        _, ok_item = _create_item_for_topic(teacher, topics[1]["topic_id"])
        student = _student()

        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": weak_item["item_id"], "selected_answer": "no", "response_time": 3},
            headers=student,
        )
        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": ok_item["item_id"], "selected_answer": "yes", "response_time": 3},
            headers=student,
        )

        response = client.get("/api/v1/adaptive/revision-plan", headers=student)
        assert response.status_code == 200
        types = {r["recommendation_type"] for r in response.json()["items"]}
        assert types.issubset({"Revision", "AI Support"})
        assert "Progression" not in types


class TestLearningPathEndpoint:
    def test_path_includes_next_unencountered_topic_when_course_given(self) -> None:
        teacher = _teacher_headers()
        course, topics = _build_course_with_topics(teacher, topic_count=2)
        _, item = _create_item_for_topic(teacher, topics[0]["topic_id"])
        student = _student()

        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "no", "response_time": 3},
            headers=student,
        )

        response = client.get(
            f"/api/v1/adaptive/learning-path?course_id={course['course_id']}", headers=student
        )
        assert response.status_code == 200
        topic_ids = {step["topic_id"] for step in response.json()["items"]}
        assert topics[0]["topic_id"] in topic_ids
        assert topics[1]["topic_id"] in topic_ids  # unencountered topic included

    def test_path_without_course_id_omits_new_topics(self) -> None:
        teacher = _teacher_headers()
        course, topics = _build_course_with_topics(teacher, topic_count=2)
        _, item = _create_item_for_topic(teacher, topics[0]["topic_id"])
        student = _student()

        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "no", "response_time": 3},
            headers=student,
        )

        response = client.get("/api/v1/adaptive/learning-path", headers=student)
        assert response.status_code == 200
        topic_ids = {step["topic_id"] for step in response.json()["items"]}
        assert topics[1]["topic_id"] not in topic_ids


class TestNextLearningOutcomeEndpoint:
    def test_returns_documented_shape(self) -> None:
        teacher = _teacher_headers()
        course, topics = _build_course_with_topics(teacher, topic_count=1)
        _, item = _create_item_for_topic(teacher, topics[0]["topic_id"])
        student = _student()

        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "no", "response_time": 3},
            headers=student,
        )

        response = client.get("/api/v1/adaptive/next-learning-outcome", headers=student)
        assert response.status_code == 200
        body = response.json()
        for field in (
            "next_action",
            "topic_id",
            "difficulty",
            "reason",
            "ai_support",
            "assessment_required",
            "learning_objective",
        ):
            assert field in body

    def test_weak_topic_produces_review_topic_action(self) -> None:
        teacher = _teacher_headers()
        course, topics = _build_course_with_topics(teacher, topic_count=1)
        _, item = _create_item_for_topic(teacher, topics[0]["topic_id"])
        student = _student()

        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "no", "response_time": 3},
            headers=student,
        )

        response = client.get("/api/v1/adaptive/next-learning-outcome", headers=student)
        assert response.json()["next_action"] == "review_topic"

    def test_no_evidence_with_course_suggests_learn_new_topic(self) -> None:
        teacher = _teacher_headers()
        course, topics = _build_course_with_topics(teacher, topic_count=1)
        student = _student()

        response = client.get(
            f"/api/v1/adaptive/next-learning-outcome?course_id={course['course_id']}", headers=student
        )
        assert response.status_code == 404  # no learner data yet (never submitted an answer)

    def test_requires_auth(self) -> None:
        response = client.get("/api/v1/adaptive/next-learning-outcome")
        assert response.status_code == 401