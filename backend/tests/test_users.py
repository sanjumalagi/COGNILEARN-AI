"""
Module 4 — User Management Tests.

Run through FastAPI's TestClient against real PostgreSQL, exercising
the full request/response cycle for the documented User Module
endpoints (GET /, GET /{id}, PATCH /{id}, DELETE /{id}).
"""

import uuid

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)

VALID_PASSWORD = "Str0ng!Pass"


def _unique_email() -> str:
    return f"user{uuid.uuid4().hex}@example.com"


def _register_and_login(role: str = "Student") -> tuple[str, dict]:
    """Registers a user with the given role and returns (user_id, auth_headers)."""
    email = _unique_email()
    register = client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": email, "password": VALID_PASSWORD, "role": role},
    )
    user_id = register.json()["user_id"]
    login = client.post("/api/v1/auth/login", json={"email": email, "password": VALID_PASSWORD})
    access_token = login.json()["access_token"]
    return user_id, {"Authorization": f"Bearer {access_token}"}


class TestGetUser:
    def test_user_can_view_own_profile(self) -> None:
        user_id, headers = _register_and_login()
        response = client.get(f"/api/v1/users/{user_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["user_id"] == user_id

    def test_user_cannot_view_another_users_profile(self) -> None:
        _, headers_a = _register_and_login()
        user_id_b, _ = _register_and_login()

        response = client.get(f"/api/v1/users/{user_id_b}", headers=headers_a)
        assert response.status_code == 403

    def test_admin_can_view_any_users_profile(self) -> None:
        user_id, _ = _register_and_login()
        _, admin_headers = _register_and_login(role="Admin")

        response = client.get(f"/api/v1/users/{user_id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["user_id"] == user_id

    def test_get_user_without_auth_returns_401(self) -> None:
        user_id, _ = _register_and_login()
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 401

    def test_get_nonexistent_user_as_admin_returns_404(self) -> None:
        _, admin_headers = _register_and_login(role="Admin")
        response = client.get(f"/api/v1/users/{uuid.uuid4()}", headers=admin_headers)
        assert response.status_code == 404


class TestListUsers:
    def test_admin_can_list_users(self) -> None:
        _register_and_login()
        _, admin_headers = _register_and_login(role="Admin")

        response = client.get("/api/v1/users/", headers=admin_headers)
        assert response.status_code == 200
        body = response.json()
        assert body["total"] >= 2
        assert "items" in body

    def test_non_admin_cannot_list_users(self) -> None:
        _, student_headers = _register_and_login()
        response = client.get("/api/v1/users/", headers=student_headers)
        assert response.status_code == 403

    def test_list_users_supports_pagination(self) -> None:
        _, admin_headers = _register_and_login(role="Admin")
        for _ in range(3):
            _register_and_login()

        page = client.get("/api/v1/users/?offset=0&limit=2", headers=admin_headers)
        assert page.status_code == 200
        assert len(page.json()["items"]) == 2
        assert page.json()["limit"] == 2

    def test_list_users_supports_role_filter(self) -> None:
        _, admin_headers = _register_and_login(role="Admin")
        _register_and_login(role="Teacher")

        response = client.get("/api/v1/users/?role=Teacher", headers=admin_headers)
        assert response.status_code == 200
        assert all(item["role"] == "Teacher" for item in response.json()["items"])


class TestUpdateUser:
    def test_user_can_update_own_name(self) -> None:
        user_id, headers = _register_and_login()
        response = client.patch(f"/api/v1/users/{user_id}", json={"name": "New Name"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["name"] == "New Name"

    def test_user_cannot_update_another_users_profile(self) -> None:
        _, headers_a = _register_and_login()
        user_id_b, _ = _register_and_login()

        response = client.patch(f"/api/v1/users/{user_id_b}", json={"name": "Hacked"}, headers=headers_a)
        assert response.status_code == 403

    def test_admin_can_update_another_users_profile(self) -> None:
        user_id, _ = _register_and_login()
        _, admin_headers = _register_and_login(role="Admin")

        response = client.patch(
            f"/api/v1/users/{user_id}", json={"name": "Admin Edited"}, headers=admin_headers
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Admin Edited"

    def test_user_cannot_change_own_role(self) -> None:
        user_id, headers = _register_and_login()
        response = client.patch(f"/api/v1/users/{user_id}", json={"role": "Admin"}, headers=headers)
        assert response.status_code == 403

    def test_admin_can_change_a_users_role(self) -> None:
        user_id, _ = _register_and_login(role="Teacher")
        _, admin_headers = _register_and_login(role="Admin")

        response = client.patch(f"/api/v1/users/{user_id}", json={"role": "Admin"}, headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["role"] == "Admin"

    def test_update_email_to_existing_email_returns_409(self) -> None:
        taken_email = _unique_email()
        client.post(
            "/api/v1/auth/register",
            json={"name": "A", "email": taken_email, "password": VALID_PASSWORD, "role": "Student"},
        )
        user_id, headers = _register_and_login()

        response = client.patch(f"/api/v1/users/{user_id}", json={"email": taken_email}, headers=headers)
        assert response.status_code == 409

    def test_create_student_profile_via_patch(self) -> None:
        user_id, headers = _register_and_login(role="Student")
        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"student_profile": {"enrollment_number": "E-1", "program": "CS", "semester": 1}},
            headers=headers,
        )
        assert response.status_code == 200
        profile = response.json()["student_profile"]
        assert profile["enrollment_number"] == "E-1"
        assert profile["program"] == "CS"
        assert profile["semester"] == 1

    def test_create_student_profile_requires_all_fields(self) -> None:
        user_id, headers = _register_and_login(role="Student")
        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"student_profile": {"enrollment_number": "E-1"}},
            headers=headers,
        )
        assert response.status_code == 422

    def test_partial_update_of_existing_student_profile(self) -> None:
        user_id, headers = _register_and_login(role="Student")
        client.patch(
            f"/api/v1/users/{user_id}",
            json={"student_profile": {"enrollment_number": "E-1", "program": "CS", "semester": 1}},
            headers=headers,
        )

        response = client.patch(
            f"/api/v1/users/{user_id}", json={"student_profile": {"semester": 2}}, headers=headers
        )
        assert response.status_code == 200
        profile = response.json()["student_profile"]
        assert profile["semester"] == 2
        assert profile["enrollment_number"] == "E-1"  # untouched fields preserved

    def test_create_teacher_profile_via_patch(self) -> None:
        user_id, headers = _register_and_login(role="Teacher")
        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"teacher_profile": {"department": "CS", "designation": "Professor"}},
            headers=headers,
        )
        assert response.status_code == 200
        profile = response.json()["teacher_profile"]
        assert profile["department"] == "CS"
        assert profile["designation"] == "Professor"

    def test_student_profile_rejected_for_teacher_user(self) -> None:
        user_id, headers = _register_and_login(role="Teacher")
        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"student_profile": {"enrollment_number": "E-1", "program": "CS", "semester": 1}},
            headers=headers,
        )
        assert response.status_code == 422

    def test_update_without_auth_returns_401(self) -> None:
        user_id, _ = _register_and_login()
        response = client.patch(f"/api/v1/users/{user_id}", json={"name": "X"})
        assert response.status_code == 401


class TestDeleteUser:
    def test_admin_can_delete_a_user(self) -> None:
        user_id, _ = _register_and_login()
        _, admin_headers = _register_and_login(role="Admin")

        response = client.delete(f"/api/v1/users/{user_id}", headers=admin_headers)
        assert response.status_code == 204

        follow_up = client.get(f"/api/v1/users/{user_id}", headers=admin_headers)
        assert follow_up.status_code == 404

    def test_non_admin_cannot_delete_a_user(self) -> None:
        user_id, headers = _register_and_login()
        response = client.delete(f"/api/v1/users/{user_id}", headers=headers)
        assert response.status_code == 403

    def test_user_cannot_delete_themselves(self) -> None:
        user_id, headers = _register_and_login()
        response = client.delete(f"/api/v1/users/{user_id}", headers=headers)
        assert response.status_code == 403

    def test_delete_nonexistent_user_returns_404(self) -> None:
        _, admin_headers = _register_and_login(role="Admin")
        response = client.delete(f"/api/v1/users/{uuid.uuid4()}", headers=admin_headers)
        assert response.status_code == 404

    def test_delete_without_auth_returns_401(self) -> None:
        user_id, _ = _register_and_login()
        response = client.delete(f"/api/v1/users/{user_id}")
        assert response.status_code == 401