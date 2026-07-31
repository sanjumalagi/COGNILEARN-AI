"""
Module 5 — Course Management Tests.

Run through FastAPI's TestClient against real PostgreSQL, covering
Course/Module/Topic/LearningObjective CRUD, role permissions,
validation, and repository integration.
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


def _student_headers() -> dict:
    return _register_and_login(role="Student")[1]


def _create_course(headers: dict, title: str = "CS101") -> dict:
    response = client.post("/api/v1/courses/", json={"title": title, "description": "d"}, headers=headers)
    assert response.status_code == 201
    return response.json()


def _create_module(headers: dict, course_id: str, sequence_number: int = 1) -> dict:
    response = client.post(
        "/api/v1/modules/",
        json={"course_id": course_id, "title": "M", "sequence_number": sequence_number},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def _create_topic(headers: dict, module_id: str) -> dict:
    response = client.post(
        "/api/v1/topics/",
        json={"module_id": module_id, "title": "T", "description": "d", "difficulty_level": 1},
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


class TestCourseCrud:
    def test_teacher_can_create_course(self) -> None:
        course = _create_course(_teacher_headers())
        assert course["title"] == "CS101"
        assert course["modules"] == 0

    def test_admin_can_create_course(self) -> None:
        course = _create_course(_admin_headers())
        assert course["title"] == "CS101"

    def test_student_cannot_create_course(self) -> None:
        response = client.post(
            "/api/v1/courses/", json={"title": "X", "description": "d"}, headers=_student_headers()
        )
        assert response.status_code == 403

    def test_create_course_without_auth_returns_401(self) -> None:
        response = client.post("/api/v1/courses/", json={"title": "X", "description": "d"})
        assert response.status_code == 401

    def test_any_authenticated_role_can_view_a_course(self) -> None:
        course = _create_course(_teacher_headers())
        for headers in (_teacher_headers(), _student_headers(), _admin_headers()):
            response = client.get(f"/api/v1/courses/{course['course_id']}", headers=headers)
            assert response.status_code == 200

    def test_get_nonexistent_course_returns_404(self) -> None:
        response = client.get(f"/api/v1/courses/{uuid.uuid4()}", headers=_student_headers())
        assert response.status_code == 404

    def test_list_courses(self) -> None:
        _create_course(_teacher_headers())
        response = client.get("/api/v1/courses/", headers=_student_headers())
        assert response.status_code == 200
        body = response.json()
        assert body["total"] >= 1
        assert "items" in body

    def test_list_courses_pagination(self) -> None:
        teacher = _teacher_headers()
        for _ in range(3):
            _create_course(teacher)
        response = client.get("/api/v1/courses/?offset=0&limit=2", headers=_student_headers())
        assert response.status_code == 200
        assert len(response.json()["items"]) == 2

    def test_teacher_can_update_course(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        response = client.put(
            f"/api/v1/courses/{course['course_id']}",
            json={"title": "Updated", "description": "d2"},
            headers=teacher,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated"

    def test_student_cannot_update_course(self) -> None:
        course = _create_course(_teacher_headers())
        response = client.put(
            f"/api/v1/courses/{course['course_id']}",
            json={"title": "Updated", "description": "d2"},
            headers=_student_headers(),
        )
        assert response.status_code == 403

    def test_admin_can_delete_course(self) -> None:
        course = _create_course(_teacher_headers())
        response = client.delete(f"/api/v1/courses/{course['course_id']}", headers=_admin_headers())
        assert response.status_code == 204

        follow_up = client.get(f"/api/v1/courses/{course['course_id']}", headers=_student_headers())
        assert follow_up.status_code == 404

    def test_teacher_cannot_delete_course(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        response = client.delete(f"/api/v1/courses/{course['course_id']}", headers=teacher)
        assert response.status_code == 403

    def test_create_course_rejects_empty_title(self) -> None:
        response = client.post(
            "/api/v1/courses/", json={"title": "", "description": "d"}, headers=_teacher_headers()
        )
        assert response.status_code == 422


class TestModuleCrud:
    def test_teacher_can_create_module(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        assert module["course_id"] == course["course_id"]
        assert module["sequence_number"] == 1

    def test_create_module_for_nonexistent_course_returns_422(self) -> None:
        response = client.post(
            "/api/v1/modules/",
            json={"course_id": str(uuid.uuid4()), "title": "M", "sequence_number": 1},
            headers=_teacher_headers(),
        )
        assert response.status_code == 422

    def test_student_cannot_create_module(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        response = client.post(
            "/api/v1/modules/",
            json={"course_id": course["course_id"], "title": "M", "sequence_number": 1},
            headers=_student_headers(),
        )
        assert response.status_code == 403

    def test_get_module_by_id(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        response = client.get(f"/api/v1/modules/{module['module_id']}", headers=_student_headers())
        assert response.status_code == 200
        assert response.json()["module_id"] == module["module_id"]

    def test_list_modules_filtered_by_course(self) -> None:
        teacher = _teacher_headers()
        course_a = _create_course(teacher, title="A")
        course_b = _create_course(teacher, title="B")
        _create_module(teacher, course_a["course_id"])
        _create_module(teacher, course_b["course_id"])

        response = client.get(
            f"/api/v1/modules/?course_id={course_a['course_id']}", headers=_student_headers()
        )
        assert response.status_code == 200
        items = response.json()["items"]
        assert all(m["course_id"] == course_a["course_id"] for m in items)
        assert len(items) == 1

    def test_teacher_can_update_module(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])

        response = client.put(
            f"/api/v1/modules/{module['module_id']}",
            json={"title": "Renamed", "sequence_number": 2},
            headers=teacher,
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Renamed"
        assert response.json()["sequence_number"] == 2

    def test_admin_can_delete_module(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])

        response = client.delete(f"/api/v1/modules/{module['module_id']}", headers=_admin_headers())
        assert response.status_code == 204

    def test_student_cannot_delete_module(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])

        response = client.delete(f"/api/v1/modules/{module['module_id']}", headers=_student_headers())
        assert response.status_code == 403


class TestTopicCrud:
    def test_teacher_can_create_topic(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])
        assert topic["module_id"] == module["module_id"]
        assert topic["difficulty_level"] == 1

    def test_create_topic_for_nonexistent_module_returns_422(self) -> None:
        response = client.post(
            "/api/v1/topics/",
            json={
                "module_id": str(uuid.uuid4()),
                "title": "T",
                "description": "d",
                "difficulty_level": 1,
            },
            headers=_teacher_headers(),
        )
        assert response.status_code == 422

    def test_no_single_item_get_endpoint_for_topics(self) -> None:
        # Documented Topic API operations are Create/Update/Delete/List
        # only — no standalone "Get Topic" (unlike Module).
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])

        response = client.get(f"/api/v1/topics/{topic['topic_id']}", headers=_student_headers())
        # The path is matched (PUT/DELETE are registered for it), but no
        # GET handler exists, so FastAPI correctly returns 405, not 404.
        assert response.status_code == 405

    def test_list_topics_filtered_by_module(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module_a = _create_module(teacher, course["course_id"], sequence_number=1)
        module_b = _create_module(teacher, course["course_id"], sequence_number=2)
        _create_topic(teacher, module_a["module_id"])
        _create_topic(teacher, module_b["module_id"])

        response = client.get(
            f"/api/v1/topics/?module_id={module_a['module_id']}", headers=_student_headers()
        )
        assert response.status_code == 200
        items = response.json()["items"]
        assert len(items) == 1
        assert items[0]["module_id"] == module_a["module_id"]

    def test_teacher_can_update_topic(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])

        response = client.put(
            f"/api/v1/topics/{topic['topic_id']}",
            json={"title": "Renamed", "description": "d2", "difficulty_level": 3},
            headers=teacher,
        )
        assert response.status_code == 200
        assert response.json()["difficulty_level"] == 3

    def test_admin_can_delete_topic(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])

        response = client.delete(f"/api/v1/topics/{topic['topic_id']}", headers=_admin_headers())
        assert response.status_code == 204

    def test_teacher_cannot_delete_topic(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])

        response = client.delete(f"/api/v1/topics/{topic['topic_id']}", headers=teacher)
        assert response.status_code == 403


class TestLearningObjectiveCrud:
    def test_teacher_can_create_learning_objective(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])

        response = client.post(
            "/api/v1/learning-outcomes/",
            json={"topic_id": topic["topic_id"], "description": "Understand X"},
            headers=teacher,
        )
        assert response.status_code == 201
        assert response.json()["description"] == "Understand X"

    def test_create_learning_objective_for_nonexistent_topic_returns_422(self) -> None:
        response = client.post(
            "/api/v1/learning-outcomes/",
            json={"topic_id": str(uuid.uuid4()), "description": "X"},
            headers=_teacher_headers(),
        )
        assert response.status_code == 422

    def test_student_cannot_create_learning_objective(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])

        response = client.post(
            "/api/v1/learning-outcomes/",
            json={"topic_id": topic["topic_id"], "description": "X"},
            headers=_student_headers(),
        )
        assert response.status_code == 403

    def test_view_learning_objective_by_id(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])
        created = client.post(
            "/api/v1/learning-outcomes/",
            json={"topic_id": topic["topic_id"], "description": "X"},
            headers=teacher,
        ).json()

        response = client.get(
            f"/api/v1/learning-outcomes/{created['objective_id']}", headers=_student_headers()
        )
        assert response.status_code == 200
        assert response.json()["objective_id"] == created["objective_id"]

    def test_list_learning_objectives_filtered_by_topic(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])
        client.post(
            "/api/v1/learning-outcomes/",
            json={"topic_id": topic["topic_id"], "description": "X"},
            headers=teacher,
        )

        response = client.get(
            f"/api/v1/learning-outcomes/?topic_id={topic['topic_id']}", headers=_student_headers()
        )
        assert response.status_code == 200
        assert response.json()["total"] == 1

    def test_teacher_can_update_learning_objective(self) -> None:
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])
        created = client.post(
            "/api/v1/learning-outcomes/",
            json={"topic_id": topic["topic_id"], "description": "X"},
            headers=teacher,
        ).json()

        response = client.put(
            f"/api/v1/learning-outcomes/{created['objective_id']}",
            json={"description": "Updated"},
            headers=teacher,
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Updated"

    def test_no_delete_endpoint_for_learning_objectives(self) -> None:
        # Documented Learning Outcome API operations are
        # Create/Update/View/List only — no Delete.
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        topic = _create_topic(teacher, module["module_id"])
        created = client.post(
            "/api/v1/learning-outcomes/",
            json={"topic_id": topic["topic_id"], "description": "X"},
            headers=teacher,
        ).json()

        response = client.delete(
            f"/api/v1/learning-outcomes/{created['objective_id']}", headers=_admin_headers()
        )
        assert response.status_code in (404, 405)  # no route registered for DELETE


class TestCascadeAndRestrictBehavior:
    def test_deleting_course_cascades_to_modules_and_topics(self) -> None:
        admin_headers = _admin_headers()
        teacher = _teacher_headers()
        course = _create_course(teacher)
        module = _create_module(teacher, course["course_id"])
        _create_topic(teacher, module["module_id"])

        response = client.delete(f"/api/v1/courses/{course['course_id']}", headers=admin_headers)
        assert response.status_code == 204

        # The module and topic should be gone too (DB cascade, verified
        # at the DB layer in Module 1; here confirmed through the API).
        module_check = client.get(f"/api/v1/modules/{module['module_id']}", headers=admin_headers)
        assert module_check.status_code == 404