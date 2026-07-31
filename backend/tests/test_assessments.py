"""
Module 6 — Assessment Intelligence Tests.

Run through FastAPI's TestClient against real PostgreSQL, covering
Assessment/AssessmentItem CRUD, the student attempt flow (generate,
submit, results, history), auto-evaluation, score calculation,
validation, and authorization.
"""

import uuid

from fastapi.testclient import TestClient

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


def _admin_headers() -> dict:
    return _register_and_login(role="Admin")[1]


def _student() -> tuple[dict, str]:
    """Registers a Student, creates their profile, and returns (headers, student_profile_id)."""
    user_id, headers = _register_and_login(role="Student")
    response = client.patch(
        f"/api/v1/users/{user_id}",
        json={"student_profile": {"enrollment_number": "E-1", "program": "CS", "semester": 1}},
        headers=headers,
    )
    return headers, response.json()["student_profile"]["student_id"]


def _build_topic(teacher_headers: dict) -> dict:
    course = client.post(
        "/api/v1/courses/", json={"title": "C", "description": "d"}, headers=teacher_headers
    ).json()
    module = client.post(
        "/api/v1/modules/",
        json={"course_id": course["course_id"], "title": "M", "sequence_number": 1},
        headers=teacher_headers,
    ).json()
    return client.post(
        "/api/v1/topics/",
        json={"module_id": module["module_id"], "title": "T", "description": "d", "difficulty_level": 1},
        headers=teacher_headers,
    ).json()


def _create_assessment(teacher_headers: dict, topic_id: str) -> dict:
    response = client.post(
        "/api/v1/assessments/",
        json={"topic_id": topic_id, "title": "Quiz", "assessment_type": "quiz"},
        headers=teacher_headers,
    )
    assert response.status_code == 201
    return response.json()


def _create_item(
    teacher_headers: dict, assessment_id: str, question: str = "2+2?", answer: str = "4"
) -> dict:
    response = client.post(
        "/api/v1/assessment-items/",
        json={
            "assessment_id": assessment_id,
            "question_text": question,
            "difficulty": 0.3,
            "bloom_level": "Remember",
            "correct_answer": answer,
            "explanation": "Basic arithmetic.",
        },
        headers=teacher_headers,
    )
    assert response.status_code == 201
    return response.json()


class TestAssessmentCrud:
    def test_teacher_can_create_assessment(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        assert assessment["title"] == "Quiz"
        assert assessment["item_count"] == 0

    def test_student_cannot_create_assessment(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        student_headers, _ = _student()

        response = client.post(
            "/api/v1/assessments/",
            json={"topic_id": topic["topic_id"], "title": "Quiz", "assessment_type": "quiz"},
            headers=student_headers,
        )
        assert response.status_code == 403

    def test_create_assessment_for_nonexistent_topic_returns_422(self) -> None:
        response = client.post(
            "/api/v1/assessments/",
            json={"topic_id": str(uuid.uuid4()), "title": "Quiz", "assessment_type": "quiz"},
            headers=_teacher_headers(),
        )
        assert response.status_code == 422

    def test_get_assessment_by_id(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        student_headers, _ = _student()

        response = client.get(f"/api/v1/assessments/{assessment['assessment_id']}", headers=student_headers)
        assert response.status_code == 200
        assert response.json()["item_count"] == 0

    def test_list_assessments_filtered_by_topic(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        _create_assessment(teacher, topic["topic_id"])

        response = client.get(f"/api/v1/assessments/?topic_id={topic['topic_id']}", headers=teacher)
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_teacher_can_update_assessment(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])

        response = client.put(
            f"/api/v1/assessments/{assessment['assessment_id']}",
            json={"title": "Renamed", "assessment_type": "exam"},
            headers=teacher,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Renamed"

    def test_admin_can_delete_assessment(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])

        response = client.delete(
            f"/api/v1/assessments/{assessment['assessment_id']}", headers=_admin_headers()
        )
        assert response.status_code == 204

    def test_teacher_cannot_delete_assessment(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])

        response = client.delete(f"/api/v1/assessments/{assessment['assessment_id']}", headers=teacher)
        assert response.status_code == 403


class TestAssessmentItemCrud:
    def test_teacher_can_create_item(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item = _create_item(teacher, assessment["assessment_id"])
        assert item["correct_answer"] == "4"
        assert item["bloom_level"] == "Remember"

    def test_student_cannot_access_item_crud(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        student_headers, _ = _student()

        response = client.post(
            "/api/v1/assessment-items/",
            json={
                "assessment_id": assessment["assessment_id"],
                "question_text": "X?",
                "difficulty": 0.5,
                "bloom_level": "Remember",
                "correct_answer": "Y",
                "explanation": "Z",
            },
            headers=student_headers,
        )
        assert response.status_code == 403

    def test_create_item_rejects_invalid_bloom_level(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])

        response = client.post(
            "/api/v1/assessment-items/",
            json={
                "assessment_id": assessment["assessment_id"],
                "question_text": "X?",
                "difficulty": 0.5,
                "bloom_level": "NotARealLevel",
                "correct_answer": "Y",
                "explanation": "Z",
            },
            headers=teacher,
        )
        assert response.status_code == 422

    def test_create_item_rejects_out_of_range_difficulty(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])

        response = client.post(
            "/api/v1/assessment-items/",
            json={
                "assessment_id": assessment["assessment_id"],
                "question_text": "X?",
                "difficulty": 5.0,
                "bloom_level": "Remember",
                "correct_answer": "Y",
                "explanation": "Z",
            },
            headers=teacher,
        )
        assert response.status_code == 422

    def test_create_item_for_nonexistent_assessment_returns_422(self) -> None:
        response = client.post(
            "/api/v1/assessment-items/",
            json={
                "assessment_id": str(uuid.uuid4()),
                "question_text": "X?",
                "difficulty": 0.5,
                "bloom_level": "Remember",
                "correct_answer": "Y",
                "explanation": "Z",
            },
            headers=_teacher_headers(),
        )
        assert response.status_code == 422

    def test_teacher_can_update_item(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item = _create_item(teacher, assessment["assessment_id"])

        response = client.put(
            f"/api/v1/assessment-items/{item['item_id']}",
            json={
                "question_text": "Updated?",
                "difficulty": 0.7,
                "bloom_level": "Apply",
                "correct_answer": "42",
                "explanation": "Because.",
            },
            headers=teacher,
        )
        assert response.status_code == 200
        assert response.json()["bloom_level"] == "Apply"

    def test_admin_can_delete_item(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item = _create_item(teacher, assessment["assessment_id"])

        response = client.delete(f"/api/v1/assessment-items/{item['item_id']}", headers=_admin_headers())
        assert response.status_code == 204

    def test_deleting_item_with_response_history_is_restricted(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item = _create_item(teacher, assessment["assessment_id"])
        student_headers, student_id = _student()

        client.post(
            "/api/v1/assessments/generate",
            json={"student_id": student_id, "topic_id": topic["topic_id"]},
            headers=student_headers,
        )
        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "4", "response_time": 5},
            headers=student_headers,
        )

        response = client.delete(f"/api/v1/assessment-items/{item['item_id']}", headers=_admin_headers())
        assert response.status_code == 409


class TestAssessmentAttemptFlow:
    def test_generate_returns_sanitized_items_without_answer_key(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        _create_item(teacher, assessment["assessment_id"])
        student_headers, student_id = _student()

        response = client.post(
            "/api/v1/assessments/generate",
            json={"student_id": student_id, "topic_id": topic["topic_id"]},
            headers=student_headers,
        )
        assert response.status_code == 200
        item = response.json()["items"][0]
        assert "correct_answer" not in item
        assert "explanation" not in item

    def test_teacher_cannot_generate_assessment(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        _create_item(teacher, assessment["assessment_id"])

        response = client.post(
            "/api/v1/assessments/generate",
            json={"student_id": str(uuid.uuid4()), "topic_id": topic["topic_id"]},
            headers=teacher,
        )
        assert response.status_code == 403

    def test_generate_for_topic_without_assessment_returns_404(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        student_headers, student_id = _student()

        response = client.post(
            "/api/v1/assessments/generate",
            json={"student_id": student_id, "topic_id": topic["topic_id"]},
            headers=student_headers,
        )
        assert response.status_code == 404

    def test_generate_rejects_mismatched_student_id(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        _create_item(teacher, assessment["assessment_id"])
        student_headers, _ = _student()

        response = client.post(
            "/api/v1/assessments/generate",
            json={"student_id": str(uuid.uuid4()), "topic_id": topic["topic_id"]},
            headers=student_headers,
        )
        assert response.status_code == 403

    def test_student_without_profile_cannot_generate(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        _create_item(teacher, assessment["assessment_id"])
        _, student_headers = _register_and_login(role="Student")  # no profile created

        response = client.post(
            "/api/v1/assessments/generate",
            json={"student_id": str(uuid.uuid4()), "topic_id": topic["topic_id"]},
            headers=student_headers,
        )
        assert response.status_code == 422

    def test_submit_correct_answer_is_evaluated_correctly(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item = _create_item(teacher, assessment["assessment_id"])
        student_headers, student_id = _student()
        client.post(
            "/api/v1/assessments/generate",
            json={"student_id": student_id, "topic_id": topic["topic_id"]},
            headers=student_headers,
        )

        response = client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "4", "response_time": 3},
            headers=student_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["is_correct"] is True
        assert body["correct_answer"] == "4"

    def test_submit_incorrect_answer_is_evaluated_correctly(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item = _create_item(teacher, assessment["assessment_id"])
        student_headers, _ = _student()

        response = client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "5", "response_time": 3},
            headers=student_headers,
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is False

    def test_submit_answer_is_case_and_whitespace_insensitive(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item = _create_item(
            teacher, assessment["assessment_id"], question="Capital of France?", answer="Paris"
        )
        student_headers, _ = _student()

        response = client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "  paris  ", "response_time": 3},
            headers=student_headers,
        )
        assert response.status_code == 200
        assert response.json()["is_correct"] is True

    def test_teacher_cannot_submit_answers(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item = _create_item(teacher, assessment["assessment_id"])

        response = client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "4", "response_time": 3},
            headers=teacher,
        )
        assert response.status_code == 403

    def test_submit_for_nonexistent_item_returns_404(self) -> None:
        student_headers, _ = _student()
        response = client.post(
            "/api/v1/assessments/submit",
            json={"question_id": str(uuid.uuid4()), "selected_answer": "4", "response_time": 3},
            headers=student_headers,
        )
        assert response.status_code == 404


class TestScoreCalculation:
    def test_results_computes_score_total_and_percentage(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item_1 = _create_item(teacher, assessment["assessment_id"], question="2+2?", answer="4")
        item_2 = _create_item(teacher, assessment["assessment_id"], question="3+3?", answer="6")
        student_headers, _ = _student()

        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item_1["item_id"], "selected_answer": "4", "response_time": 3},
            headers=student_headers,
        )
        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item_2["item_id"], "selected_answer": "wrong", "response_time": 3},
            headers=student_headers,
        )

        response = client.get(
            f"/api/v1/assessments/results?assessment_id={assessment['assessment_id']}",
            headers=student_headers,
        )
        assert response.status_code == 200
        body = response.json()
        assert body["score"] == 1
        assert body["total"] == 2
        assert body["percentage"] == 50.0
        assert body["ability_theta"] is None
        assert body["mastery"] is None

    def test_results_uses_latest_response_when_item_answered_twice(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item = _create_item(teacher, assessment["assessment_id"], question="2+2?", answer="4")
        student_headers, _ = _student()

        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "wrong", "response_time": 3},
            headers=student_headers,
        )
        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "4", "response_time": 3},
            headers=student_headers,
        )

        response = client.get(
            f"/api/v1/assessments/results?assessment_id={assessment['assessment_id']}",
            headers=student_headers,
        )
        assert response.json()["score"] == 1

    def test_results_for_nonexistent_assessment_returns_404(self) -> None:
        student_headers, _ = _student()
        response = client.get(
            f"/api/v1/assessments/results?assessment_id={uuid.uuid4()}", headers=student_headers
        )
        assert response.status_code == 404


class TestHistory:
    def test_history_returns_only_own_responses(self) -> None:
        teacher = _teacher_headers()
        topic = _build_topic(teacher)
        assessment = _create_assessment(teacher, topic["topic_id"])
        item = _create_item(teacher, assessment["assessment_id"])

        student_a_headers, _ = _student()
        student_b_headers, _ = _student()

        client.post(
            "/api/v1/assessments/submit",
            json={"question_id": item["item_id"], "selected_answer": "4", "response_time": 3},
            headers=student_a_headers,
        )

        history_a = client.get("/api/v1/assessments/history", headers=student_a_headers)
        history_b = client.get("/api/v1/assessments/history", headers=student_b_headers)

        assert history_a.json()["total"] == 1
        assert history_b.json()["total"] == 0

    def test_history_without_auth_returns_401(self) -> None:
        response = client.get("/api/v1/assessments/history")
        assert response.status_code == 401