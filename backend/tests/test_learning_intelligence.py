"""
Module 7 — Learning Intelligence Tests.

Covers the IRT engine, BKT engine, Mastery Engine classification, the
end-to-end pipeline (triggered via submit_assessment), and the 5
documented GET /learner/* endpoints.
"""

import math
import uuid

import pytest
from fastapi.testclient import TestClient

from backend.algorithms.bkt.estimator import MasteryStatus, classify_mastery, update_mastery
from backend.algorithms.irt.estimator import (
    AbilityCategory,
    classify_ability,
    estimate_ability,
    probability_correct,
)
from backend.algorithms.mastery_engine import (
    MasteryLevel,
    calculate_overall_mastery,
    classify_mastery_level,
    is_strong_topic,
    is_weak_topic,
)
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


def _build_assessment_with_items(teacher_headers: dict, count: int = 4) -> tuple[dict, list[dict]]:
    course = client.post(
        "/api/v1/courses/", json={"title": "C", "description": "d"}, headers=teacher_headers
    ).json()
    module = client.post(
        "/api/v1/modules/",
        json={"course_id": course["course_id"], "title": "M", "sequence_number": 1},
        headers=teacher_headers,
    ).json()
    topic = client.post(
        "/api/v1/topics/",
        json={"module_id": module["module_id"], "title": "T", "description": "d", "difficulty_level": 1},
        headers=teacher_headers,
    ).json()
    assessment = client.post(
        "/api/v1/assessments/",
        json={"topic_id": topic["topic_id"], "title": "Quiz", "assessment_type": "quiz"},
        headers=teacher_headers,
    ).json()
    items = []
    for i in range(count):
        item = client.post(
            "/api/v1/assessment-items/",
            json={
                "assessment_id": assessment["assessment_id"],
                "question_text": f"Q{i}",
                "difficulty": round(0.2 + i * 0.15, 2),
                "bloom_level": "Remember",
                "correct_answer": "yes",
                "explanation": "x",
            },
            headers=teacher_headers,
        ).json()
        items.append(item)
    return assessment, items


class TestIRTFormula:
    def test_probability_correct_matches_documented_1pl_formula(self) -> None:
        theta, b = 1.0, 0.5
        expected = 1.0 / (1.0 + math.exp(-(theta - b)))
        assert probability_correct(theta, b) == pytest.approx(expected)

    def test_probability_is_half_when_ability_equals_difficulty(self) -> None:
        assert probability_correct(0.7, 0.7) == pytest.approx(0.5)

    def test_higher_ability_increases_probability(self) -> None:
        low = probability_correct(-1.0, 0.0)
        high = probability_correct(1.0, 0.0)
        assert high > low

    @pytest.mark.parametrize(
        ("theta", "expected"),
        [
            (-2.0, AbilityCategory.BEGINNER),
            (0.0, AbilityCategory.INTERMEDIATE),
            (2.0, AbilityCategory.ADVANCED),
        ],
    )
    def test_ability_classification_matches_documented_thresholds(self, theta, expected) -> None:
        assert classify_ability(theta) == expected

    def test_ability_classification_boundary_is_intermediate(self) -> None:
        assert classify_ability(-1.0) == AbilityCategory.INTERMEDIATE
        assert classify_ability(1.0) == AbilityCategory.INTERMEDIATE


class TestIRTEstimation:
    def test_empty_history_returns_center_with_no_previous_theta(self) -> None:
        result = estimate_ability(responses=[], previous_theta=None)
        assert result.ability == 0.0

    def test_empty_history_falls_back_to_previous_theta(self) -> None:
        result = estimate_ability(responses=[], previous_theta=1.23)
        assert result.ability == 1.23

    def test_estimate_matches_hand_calculated_mle(self) -> None:
        # 3 correct + 1 incorrect at difficulties 0.3-0.6; hand-verified MLE ~1.5517.
        responses = [(True, 0.3), (True, 0.4), (True, 0.5), (False, 0.6)]
        result = estimate_ability(responses=responses)
        assert result.ability == pytest.approx(1.5517, abs=1e-3)

    def test_estimate_is_independent_of_starting_previous_theta(self) -> None:
        responses = [(True, 0.3), (True, 0.4), (True, 0.5), (False, 0.6)]
        r_none = estimate_ability(responses=responses, previous_theta=None)
        r_high = estimate_ability(responses=responses, previous_theta=4.0)
        r_low = estimate_ability(responses=responses, previous_theta=-4.0)
        assert r_none.ability == pytest.approx(r_high.ability, abs=1e-6)
        assert r_none.ability == pytest.approx(r_low.ability, abs=1e-6)

    def test_all_correct_clamps_at_max_ability(self) -> None:
        responses = [(True, 0.1), (True, 0.2), (True, 0.3)]
        result = estimate_ability(responses=responses)
        assert result.ability == 4.0  # IRT_ABILITY_MAX default

    def test_all_incorrect_clamps_at_min_ability(self) -> None:
        responses = [(False, 0.1), (False, 0.2), (False, 0.3)]
        result = estimate_ability(responses=responses)
        assert result.ability == -4.0  # IRT_ABILITY_MIN default

    def test_difficulty_recommendation_equals_ability_estimate(self) -> None:
        result = estimate_ability(responses=[(True, 0.5), (False, 0.5)])
        assert result.difficulty_recommendation == round(result.ability, 4)


class TestBKTFormula:
    # ── Evidence-based initial mastery ───────────────────────────────

    def test_no_fixed_prior_l0_used_for_new_learners(self) -> None:
        """update_mastery(previous_mastery=None) must raise ValueError,
        proving no fixed P(L0) is silently used for new learners."""
        with pytest.raises(ValueError, match="diagnostic evidence"):
            update_mastery(previous_mastery=None, is_correct=True)
        with pytest.raises(ValueError, match="diagnostic evidence"):
            update_mastery(previous_mastery=None, is_correct=False)

    def test_different_diagnostic_evidence_produces_different_initial_mastery(self) -> None:
        """Two learners with different diagnostic response patterns must
        receive different initial mastery estimates."""
        from backend.algorithms.bkt.estimator import compute_initial_mastery

        strong_learner = compute_initial_mastery(diagnostic_responses=[True, True, True, False])
        weak_learner = compute_initial_mastery(diagnostic_responses=[False, False, True, False])

        assert strong_learner != weak_learner
        assert strong_learner > weak_learner

    def test_compute_initial_mastery_all_correct(self) -> None:
        """All-correct diagnostic → high initial mastery."""
        from backend.algorithms.bkt.estimator import compute_initial_mastery

        mastery = compute_initial_mastery(diagnostic_responses=[True, True, True])
        assert mastery > 0.8

    def test_compute_initial_mastery_all_incorrect(self) -> None:
        """All-incorrect diagnostic → low initial mastery."""
        from backend.algorithms.bkt.estimator import compute_initial_mastery

        mastery = compute_initial_mastery(diagnostic_responses=[False, False, False])
        assert mastery < 0.2

    def test_compute_initial_mastery_mixed_responses(self) -> None:
        """Mixed diagnostic → intermediate mastery."""
        from backend.algorithms.bkt.estimator import compute_initial_mastery

        mastery = compute_initial_mastery(diagnostic_responses=[True, False, True, False])
        assert 0.2 < mastery < 0.8

    def test_compute_initial_mastery_empty_raises(self) -> None:
        """Empty response list must raise ValueError."""
        from backend.algorithms.bkt.estimator import compute_initial_mastery

        with pytest.raises(ValueError, match="At least one"):
            compute_initial_mastery(diagnostic_responses=[])

    def test_compute_initial_mastery_single_response(self) -> None:
        """Single response works (degenerate but valid case)."""
        from backend.algorithms.bkt.estimator import compute_initial_mastery

        correct = compute_initial_mastery(diagnostic_responses=[True])
        incorrect = compute_initial_mastery(diagnostic_responses=[False])

        assert correct > incorrect
        assert 0.0 <= correct <= 1.0
        assert 0.0 <= incorrect <= 1.0

    def test_compute_initial_mastery_uses_configurable_guess_slip(self) -> None:
        """Changing P(G) and P(S) settings affects the initial mastery
        computation, proving the configurable parameters are used."""
        from unittest.mock import patch

        from backend.algorithms.bkt.estimator import compute_initial_mastery
        from backend.config import settings

        responses = [True, False, True]
        default_mastery = compute_initial_mastery(diagnostic_responses=responses)

        # With higher guess probability, correct answers carry less weight
        with patch.object(settings, "BKT_PROB_GUESS", 0.4):
            high_guess_mastery = compute_initial_mastery(diagnostic_responses=responses)

        assert default_mastery != high_guess_mastery

    # ── Standard BKT update behavior ────────────────────────────────

    def test_correct_response_increases_mastery(self) -> None:
        result = update_mastery(previous_mastery=0.3, is_correct=True)
        assert result.mastery_probability > 0.3

    def test_incorrect_response_decreases_mastery(self) -> None:
        result = update_mastery(previous_mastery=0.7, is_correct=False)
        assert result.mastery_probability < 0.7

    def test_mastery_stays_within_bounds(self) -> None:
        result = update_mastery(previous_mastery=0.99, is_correct=True)
        assert 0.0 <= result.mastery_probability <= 1.0

    @pytest.mark.parametrize(
        ("score", "expected"),
        [
            (0.2, MasteryStatus.NEEDS_IMPROVEMENT),
            (0.6, MasteryStatus.DEVELOPING),
            (0.9, MasteryStatus.MASTERED),
        ],
    )
    def test_bkt_status_classification_matches_documented_thresholds(self, score, expected) -> None:
        assert classify_mastery(score) == expected

    def test_recommendation_trigger_set_only_for_needs_improvement(self) -> None:
        low = update_mastery(previous_mastery=0.1, is_correct=False)
        high = update_mastery(previous_mastery=0.9, is_correct=True)
        assert low.recommendation_trigger is True
        assert high.recommendation_trigger is False

    def test_repeated_correct_responses_trend_toward_mastery(self) -> None:
        from backend.algorithms.bkt.estimator import compute_initial_mastery

        mastery = compute_initial_mastery(diagnostic_responses=[True])
        for _ in range(8):
            result = update_mastery(previous_mastery=mastery, is_correct=True)
            mastery = result.mastery_probability
        assert mastery > 0.9


class TestMasteryEngine:
    def test_not_started_when_no_score(self) -> None:
        assert classify_mastery_level(None) == MasteryLevel.NOT_STARTED

    @pytest.mark.parametrize(
        ("score", "expected"),
        [
            (0.1, MasteryLevel.BEGINNER),
            (0.5, MasteryLevel.DEVELOPING),
            (0.7, MasteryLevel.PROFICIENT),
            (0.9, MasteryLevel.MASTERED),
        ],
    )
    def test_five_level_classification(self, score, expected) -> None:
        assert classify_mastery_level(score) == expected

    def test_weak_and_strong_topic_thresholds(self) -> None:
        assert is_weak_topic(0.3) is True
        assert is_weak_topic(0.5) is False
        assert is_strong_topic(0.85) is True
        assert is_strong_topic(0.5) is False

    def test_overall_mastery_is_mean_of_topic_scores(self) -> None:
        assert calculate_overall_mastery([0.2, 0.4, 0.6]) == pytest.approx(0.4)

    def test_overall_mastery_empty_list_is_zero(self) -> None:
        assert calculate_overall_mastery([]) == 0.0


class TestPipelineIntegration:
    def test_submitting_answers_creates_learner_profile_and_topic_mastery(self) -> None:
        teacher = _teacher_headers()
        assessment, items = _build_assessment_with_items(teacher, count=1)
        student = _student()

        response = client.post(
            "/api/v1/assessments/submit",
            json={"question_id": items[0]["item_id"], "selected_answer": "yes", "response_time": 3},
            headers=student,
        )
        assert response.status_code == 200

        profile = client.get("/api/v1/learner/profile", headers=student)
        assert profile.status_code == 200
        assert profile.json()["overall_mastery"] > 0.0

    def test_ability_updates_across_multiple_submissions(self) -> None:
        teacher = _teacher_headers()
        assessment, items = _build_assessment_with_items(teacher, count=4)
        student = _student()

        for i, item in enumerate(items):
            answer = "yes" if i != 3 else "no"
            client.post(
                "/api/v1/assessments/submit",
                json={"question_id": item["item_id"], "selected_answer": answer, "response_time": 3},
                headers=student,
            )

        ability = client.get("/api/v1/learner/ability", headers=student).json()
        # Exact MLE arithmetic is verified precisely in TestIRTEstimation
        # against a hand-calculated case; this integration test only
        # confirms the pipeline produces a sensible, non-default result.
        assert ability["ability_theta"] != 0.0
        assert ability["ability_category"] in ("Intermediate", "Advanced")

    def test_mastery_reflects_bkt_update_for_the_topic(self) -> None:
        teacher = _teacher_headers()
        assessment, items = _build_assessment_with_items(teacher, count=3)
        student = _student()

        for item in items:
            client.post(
                "/api/v1/assessments/submit",
                json={"question_id": item["item_id"], "selected_answer": "yes", "response_time": 3},
                headers=student,
            )

        mastery = client.get("/api/v1/learner/mastery", headers=student).json()
        assert mastery["total"] == 1
        assert mastery["items"][0]["mastery"] > 0.5
        assert mastery["items"][0]["is_strong"] is True

    def test_progress_history_recorded_per_submission(self) -> None:
        teacher = _teacher_headers()
        assessment, items = _build_assessment_with_items(teacher, count=3)
        student = _student()

        for item in items:
            client.post(
                "/api/v1/assessments/submit",
                json={"question_id": item["item_id"], "selected_answer": "yes", "response_time": 3},
                headers=student,
            )

        progress = client.get("/api/v1/learner/progress", headers=student).json()
        assert progress["total"] == 3

    def test_history_matches_progress_when_unfiltered(self) -> None:
        teacher = _teacher_headers()
        assessment, items = _build_assessment_with_items(teacher, count=2)
        student = _student()

        for item in items:
            client.post(
                "/api/v1/assessments/submit",
                json={"question_id": item["item_id"], "selected_answer": "yes", "response_time": 3},
                headers=student,
            )

        history = client.get("/api/v1/learner/history", headers=student).json()
        progress = client.get("/api/v1/learner/progress", headers=student).json()
        assert history["total"] == progress["total"] == 2

    def test_progress_filtered_by_topic(self) -> None:
        teacher = _teacher_headers()
        assessment, items = _build_assessment_with_items(teacher, count=2)
        student = _student()
        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": items[0]["item_id"], "selected_answer": "yes", "response_time": 3},
            headers=student,
        )

        progress = client.get(
            f"/api/v1/learner/progress?topic_id={assessment['topic_id']}", headers=student
        )
        assert progress.status_code == 200
        assert progress.json()["total"] == 1

    def test_initial_mastery_derived_from_assessment_evidence(self) -> None:
        """When two new students submit different correctness patterns,
        they must receive different initial mastery, proving the system
        uses actual assessment evidence rather than a fixed P(L0) constant."""
        teacher = _teacher_headers()
        assessment, items = _build_assessment_with_items(teacher, count=2)
        student_strong = _student()
        student_weak = _student()

        # Strong student answers all correct
        for item in items:
            client.post(
                "/api/v1/assessments/submit",
                json={"question_id": item["item_id"], "selected_answer": "yes", "response_time": 3},
                headers=student_strong,
            )

        # Weak student answers all incorrect
        for item in items:
            client.post(
                "/api/v1/assessments/submit",
                json={"question_id": item["item_id"], "selected_answer": "no", "response_time": 3},
                headers=student_weak,
            )

        mastery_strong = client.get("/api/v1/learner/mastery", headers=student_strong).json()
        mastery_weak = client.get("/api/v1/learner/mastery", headers=student_weak).json()

        strong_score = mastery_strong["items"][0]["mastery"]
        weak_score = mastery_weak["items"][0]["mastery"]

        assert strong_score > weak_score, (
            f"Strong learner ({strong_score}) must have higher mastery "
            f"than weak learner ({weak_score})"
        )

class TestLearnerEndpointsAuthorization:
    def test_profile_without_learner_data_returns_404(self) -> None:
        student = _student()
        response = client.get("/api/v1/learner/profile", headers=student)
        assert response.status_code == 404

    def test_teacher_cannot_access_learner_profile(self) -> None:
        teacher = _teacher_headers()
        response = client.get("/api/v1/learner/profile", headers=teacher)
        assert response.status_code == 403

    def test_student_without_profile_gets_validation_error(self) -> None:
        _, headers = _register_and_login(role="Student")  # no student_profile created
        response = client.get("/api/v1/learner/ability", headers=headers)
        assert response.status_code == 422

    def test_learner_endpoints_require_auth(self) -> None:
        for path in ("/profile", "/mastery", "/ability", "/progress", "/history"):
            response = client.get(f"/api/v1/learner{path}")
            assert response.status_code == 401