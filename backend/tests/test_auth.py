"""
Module 3 — Authentication & Authorization Tests.

Run against the same real, disposable PostgreSQL database used by
Modules 1-2 (see conftest.py), and through FastAPI's TestClient so the
full request/response cycle (routing, dependency injection, exception
handlers) is exercised, not just the service layer in isolation.
"""

import time
import uuid

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.config import settings
from backend.core.exceptions import AuthenticationError, ConflictError, ValidationFailedError
from backend.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    validate_password_policy,
    verify_password,
)
from backend.main import app
from backend.models import UserRole
from backend.services.auth_service import AuthService

client = TestClient(app)

VALID_PASSWORD = "Str0ng!Pass"


def _unique_email() -> str:
    return f"user{uuid.uuid4().hex}@example.com"


def _register(email: str, password: str = VALID_PASSWORD, role: str = "Student"):
    return client.post(
        "/api/v1/auth/register",
        json={"name": "Test User", "email": email, "password": password, "role": role},
    )


def _login(email: str, password: str = VALID_PASSWORD):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


class TestPasswordHashing:
    def test_hash_is_not_the_plaintext_password(self) -> None:
        hashed = hash_password(VALID_PASSWORD)
        assert hashed != VALID_PASSWORD
        assert hashed.startswith("$2b$")

    def test_verify_password_matches_correct_password(self) -> None:
        hashed = hash_password(VALID_PASSWORD)
        assert verify_password(VALID_PASSWORD, hashed) is True

    def test_verify_password_rejects_wrong_password(self) -> None:
        hashed = hash_password(VALID_PASSWORD)
        assert verify_password("WrongPassword1!", hashed) is False

    @pytest.mark.parametrize(
        "password",
        [
            "short1!",  # too short
            "nouppercase1!",  # missing uppercase
            "NOLOWERCASE1!",  # missing lowercase
            "NoNumberHere!",  # missing digit
            "NoSpecialChar1",  # missing special character
        ],
    )
    def test_password_policy_rejects_weak_passwords(self, password: str) -> None:
        with pytest.raises(ValidationFailedError):
            validate_password_policy(password)

    def test_password_policy_accepts_compliant_password(self) -> None:
        validate_password_policy(VALID_PASSWORD)  # does not raise

    def test_password_policy_rejects_overlong_password(self) -> None:
        with pytest.raises(ValidationFailedError):
            validate_password_policy("Aa1!" + "x" * 80)


class TestJWT:
    def test_access_token_contains_documented_claims(self) -> None:
        user_id = uuid.uuid4()
        token = create_access_token(user_id=user_id, email="a@b.com", role=UserRole.STUDENT)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])

        assert payload["sub"] == str(user_id)
        assert payload["email"] == "a@b.com"
        assert payload["role"] == "Student"
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_decode_token_round_trip(self) -> None:
        user_id = uuid.uuid4()
        token = create_access_token(user_id=user_id, email="a@b.com", role=UserRole.TEACHER)
        payload = decode_token(token, expected_type=TokenType.ACCESS)
        assert payload["sub"] == str(user_id)

    def test_decode_token_rejects_wrong_type(self) -> None:
        user_id = uuid.uuid4()
        refresh = create_refresh_token(user_id=user_id, email="a@b.com", role=UserRole.STUDENT)
        with pytest.raises(AuthenticationError):
            decode_token(refresh, expected_type=TokenType.ACCESS)

    def test_decode_token_rejects_malformed_token(self) -> None:
        with pytest.raises(AuthenticationError):
            decode_token("not-a-real-jwt", expected_type=TokenType.ACCESS)

    def test_decode_token_rejects_expired_token(self) -> None:
        user_id = uuid.uuid4()
        expired_payload = {
            "sub": str(user_id),
            "email": "a@b.com",
            "role": "Student",
            "type": "access",
            "exp": int(time.time()) - 10,  # already expired
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        with pytest.raises(AuthenticationError):
            decode_token(expired_token, expected_type=TokenType.ACCESS)

    def test_decode_token_rejects_wrong_signing_key(self) -> None:
        user_id = uuid.uuid4()
        payload = {
            "sub": str(user_id),
            "email": "a@b.com",
            "role": "Student",
            "type": "access",
            "exp": int(time.time()) + 3600,
        }
        forged = jwt.encode(payload, "a-completely-different-secret-key-value", algorithm="HS256")
        with pytest.raises(AuthenticationError):
            decode_token(forged, expected_type=TokenType.ACCESS)


class TestAuthServiceRegistration:
    def test_register_creates_user_with_hashed_password(self, db_session: Session) -> None:
        service = AuthService(db_session)
        user = service.register(
            name="Ada", email=_unique_email(), password=VALID_PASSWORD, role=UserRole.STUDENT
        )
        db_session.commit()

        assert user.password_hash != VALID_PASSWORD
        assert verify_password(VALID_PASSWORD, user.password_hash)

    def test_register_duplicate_email_raises_conflict(self, db_session: Session) -> None:
        service = AuthService(db_session)
        email = _unique_email()
        service.register(name="First", email=email, password=VALID_PASSWORD, role=UserRole.STUDENT)
        db_session.commit()

        with pytest.raises(ConflictError):
            service.register(name="Second", email=email, password=VALID_PASSWORD, role=UserRole.STUDENT)


class TestAuthServiceAuthentication:
    def test_authenticate_succeeds_with_correct_credentials(self, db_session: Session) -> None:
        service = AuthService(db_session)
        email = _unique_email()
        service.register(name="Grace", email=email, password=VALID_PASSWORD, role=UserRole.TEACHER)
        db_session.commit()

        user = service.authenticate(email=email, password=VALID_PASSWORD)
        assert user.email == email

    def test_authenticate_rejects_wrong_password(self, db_session: Session) -> None:
        service = AuthService(db_session)
        email = _unique_email()
        service.register(name="Grace", email=email, password=VALID_PASSWORD, role=UserRole.TEACHER)
        db_session.commit()

        with pytest.raises(AuthenticationError):
            service.authenticate(email=email, password="WrongPassword1!")

    def test_authenticate_rejects_unknown_email(self, db_session: Session) -> None:
        service = AuthService(db_session)
        with pytest.raises(AuthenticationError):
            service.authenticate(email=_unique_email(), password=VALID_PASSWORD)


class TestRegisterEndpoint:
    def test_register_returns_201_and_public_user(self) -> None:
        response = _register(_unique_email())
        assert response.status_code == 201
        body = response.json()
        assert "password" not in body
        assert "password_hash" not in body
        assert body["role"] == "Student"

    def test_register_duplicate_email_returns_409_with_documented_envelope(self) -> None:
        email = _unique_email()
        _register(email)
        response = _register(email)

        assert response.status_code == 409
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "CONFLICT"

    def test_register_rejects_weak_password(self) -> None:
        response = _register(_unique_email(), password="weak")
        assert response.status_code == 422

    def test_register_rejects_invalid_role(self) -> None:
        response = _register(_unique_email(), role="SuperAdmin")
        assert response.status_code == 422


class TestLoginEndpoint:
    def test_login_returns_documented_response_shape(self) -> None:
        email = _unique_email()
        _register(email)

        response = _login(email)
        assert response.status_code == 200
        body = response.json()
        assert body["token_type"] == "Bearer"
        assert body["role"] == "Student"
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["expires_in"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    def test_login_invalid_password_returns_401_with_documented_envelope(self) -> None:
        email = _unique_email()
        _register(email)

        response = _login(email, password="WrongPassword1!")
        assert response.status_code == 401
        body = response.json()
        assert body["success"] is False
        assert body["error"]["code"] == "AUTHENTICATION_FAILED"

    def test_login_unknown_user_returns_401(self) -> None:
        response = _login(_unique_email())
        assert response.status_code == 401

    def test_login_error_message_does_not_reveal_which_field_was_wrong(self) -> None:
        email = _unique_email()
        _register(email)

        unknown_user_response = _login(_unique_email())
        wrong_password_response = _login(email, password="WrongPassword1!")

        assert (
            unknown_user_response.json()["error"]["message"]
            == wrong_password_response.json()["error"]["message"]
        )


class TestProtectedRoutes:
    def test_me_without_token_returns_401(self) -> None:
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_me_with_invalid_token_returns_401(self) -> None:
        response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
        assert response.status_code == 401

    def test_me_with_valid_token_returns_current_user(self) -> None:
        email = _unique_email()
        _register(email)
        access_token = _login(email).json()["access_token"]

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        assert response.json()["email"] == email

    def test_me_with_refresh_token_instead_of_access_token_returns_401(self) -> None:
        email = _unique_email()
        _register(email)
        refresh_token = _login(email).json()["refresh_token"]

        response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh_token}"})
        assert response.status_code == 401

    def test_logout_requires_authentication(self) -> None:
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401

    def test_logout_with_valid_token_succeeds(self) -> None:
        email = _unique_email()
        _register(email)
        access_token = _login(email).json()["access_token"]

        response = client.post("/api/v1/auth/logout", headers={"Authorization": f"Bearer {access_token}"})
        assert response.status_code == 200
        assert "message" in response.json()


class TestRefreshEndpoint:
    def test_refresh_with_valid_refresh_token_returns_new_access_token(self) -> None:
        email = _unique_email()
        _register(email)
        login_body = _login(email).json()

        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": login_body["refresh_token"]}
        )
        assert response.status_code == 200
        body = response.json()
        assert "access_token" in body
        assert body["access_token"] != login_body["access_token"]

    def test_refresh_with_access_token_instead_of_refresh_token_returns_401(self) -> None:
        email = _unique_email()
        _register(email)
        login_body = _login(email).json()

        response = client.post(
            "/api/v1/auth/refresh", json={"refresh_token": login_body["access_token"]}
        )
        assert response.status_code == 401

    def test_refresh_with_garbage_token_returns_401(self) -> None:
        response = client.post("/api/v1/auth/refresh", json={"refresh_token": "garbage"})
        assert response.status_code == 401


class TestRoleAuthorization:
    """RBAC dependency (`require_role`), tested directly since no
    business endpoint yet applies it (Module 3 implements the mechanism;
    later modules apply it per the documented Permission Matrix)."""

    def test_require_role_allows_matching_role(self) -> None:
        from backend.core.dependencies import require_role
        from backend.models import User

        student = User(name="S", email=_unique_email(), password_hash="x", role=UserRole.STUDENT)
        dependency = require_role(UserRole.STUDENT, UserRole.TEACHER)

        result = dependency(current_user=student)
        assert result is student

    def test_require_role_rejects_non_matching_role(self) -> None:
        from backend.core.dependencies import require_role
        from backend.core.exceptions import AuthorizationError
        from backend.models import User

        teacher = User(name="T", email=_unique_email(), password_hash="x", role=UserRole.TEACHER)
        dependency = require_role(UserRole.ADMIN)

        with pytest.raises(AuthorizationError):
            dependency(current_user=teacher)

    def test_require_role_allows_one_of_several_roles(self) -> None:
        from backend.core.dependencies import require_role
        from backend.models import User

        admin = User(name="A", email=_unique_email(), password_hash="x", role=UserRole.ADMIN)
        dependency = require_role(UserRole.TEACHER, UserRole.ADMIN)

        result = dependency(current_user=admin)
        assert result is admin