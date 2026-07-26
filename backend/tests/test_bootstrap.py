"""
Module 0 — Project Bootstrap Tests.

Verifies that the project skeleton is fully runnable: the FastAPI
application starts, configuration loads, the health endpoint responds,
security headers are applied, and unhandled/validation errors are
converted into the centralized error envelope.

These tests intentionally avoid any database or AI provider dependency
since neither has been implemented yet.
"""

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "CogniLearn AI"
    assert "version" in body
    assert "environment" in body


def test_security_headers_are_present() -> None:
    response = client.get("/api/v1/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


def test_unknown_route_returns_centralized_error_envelope() -> None:
    response = client.get("/api/v1/this-route-does-not-exist")
    assert response.status_code == 404

    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "HTTP_ERROR"


def test_openapi_schema_is_served() -> None:
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "CogniLearn AI"


def test_settings_load_from_environment(monkeypatch) -> None:
    from backend.config.settings import Settings

    monkeypatch.setenv("APP_NAME", "CogniLearn AI Test")
    monkeypatch.setenv("PORT", "9000")

    test_settings = Settings()

    assert test_settings.APP_NAME == "CogniLearn AI Test"
    assert test_settings.PORT == 9000
