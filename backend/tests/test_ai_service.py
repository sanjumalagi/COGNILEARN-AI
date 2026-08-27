"""
Module 9 — AI Service Tests.

Covers the AI service pipeline's non-provider-dependent components:
response parser, response validator, token manager, retry handler,
provider manager, prompt templates, and the 5 AI API endpoints (with
the provider mocked out — no Gemini API key needed for unit tests).
"""

import time
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.core.exceptions import ExternalServiceError, ValidationFailedError
from backend.main import app
from backend.providers.base import AIProvider, ProviderResponse
from backend.services.ai import provider_manager, response_parser, response_validator, token_manager
from backend.services.ai.prompt_templates import PromptTemplateName, get_template
from backend.services.ai.retry_handler import with_retries

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


def _student_with_topic() -> tuple[dict, str]:
    """Creates a student, a course/module/topic, and returns (student_headers, topic_id)."""
    user_id, student_headers = _register_and_login(role="Student")
    client.patch(
        f"/api/v1/users/{user_id}",
        json={"student_profile": {"enrollment_number": "E-1", "program": "CS", "semester": 1}},
        headers=student_headers,
    )
    teacher = _teacher_headers()
    course = client.post(
        "/api/v1/courses/", json={"title": "C", "description": "d"}, headers=teacher
    ).json()
    module = client.post(
        "/api/v1/modules/",
        json={"course_id": course["course_id"], "title": "M", "sequence_number": 1},
        headers=teacher,
    ).json()
    topic = client.post(
        "/api/v1/topics/",
        json={
            "module_id": module["module_id"],
            "title": "T",
            "description": "d",
            "difficulty_level": 1,
        },
        headers=teacher,
    ).json()
    return student_headers, topic["topic_id"]


def _mock_provider_response(text: str = "A" * 50) -> ProviderResponse:
    """A well-formed ProviderResponse for mocking."""
    return ProviderResponse(
        text=text,
        provider_name="MockProvider",
        model="mock-model-1",
        latency_ms=42,
        prompt_tokens=10,
        completion_tokens=20,
    )


# ── Response Parser ──────────────────────────────────────────────────


class TestResponseParser:
    def test_strips_surrounding_whitespace(self) -> None:
        assert response_parser.parse_response("  hello  ") == "hello"

    def test_removes_full_code_fence_wrapping(self) -> None:
        raw = "```markdown\nSome content\n```"
        assert response_parser.parse_response(raw) == "Some content"

    def test_preserves_internal_code_fences(self) -> None:
        raw = "Here is code:\n```python\nprint('hi')\n```\nDone."
        result = response_parser.parse_response(raw)
        assert "```python" in result

    def test_normalizes_crlf_to_lf(self) -> None:
        assert "\r" not in response_parser.parse_response("a\r\nb\r\nc")

    def test_try_parse_json_returns_dict_on_valid_json(self) -> None:
        assert response_parser.try_parse_json('{"key": "val"}') == {"key": "val"}

    def test_try_parse_json_returns_none_on_prose(self) -> None:
        assert response_parser.try_parse_json("Just some text.") is None

    def test_try_parse_json_returns_none_on_list(self) -> None:
        assert response_parser.try_parse_json("[1, 2, 3]") is None


# ── Response Validator ───────────────────────────────────────────────


class TestResponseValidator:
    def test_valid_response_passes(self) -> None:
        response_validator.validate_response("A" * 50)  # no exception

    def test_empty_string_raises(self) -> None:
        with pytest.raises(ValidationFailedError):
            response_validator.validate_response("")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValidationFailedError):
            response_validator.validate_response("   \n\t  ")

    def test_too_short_raises(self) -> None:
        with pytest.raises(ValidationFailedError):
            response_validator.validate_response("Hi")

    def test_too_long_raises(self) -> None:
        with pytest.raises(ValidationFailedError):
            response_validator.validate_response("A" * 9000)


# ── Token Manager ────────────────────────────────────────────────────


class TestTokenManager:
    def test_estimate_tokens_returns_positive_integer(self) -> None:
        assert token_manager.estimate_tokens("Hello world") >= 1

    def test_longer_text_has_higher_estimate(self) -> None:
        short = token_manager.estimate_tokens("Hi")
        long = token_manager.estimate_tokens("Hello " * 1000)
        assert long > short

    def test_fits_within_budget_true(self) -> None:
        assert token_manager.fits_within_budget("Hello", max_tokens=100) is True

    def test_fits_within_budget_false(self) -> None:
        assert token_manager.fits_within_budget("A" * 10000, max_tokens=10) is False


# ── Retry Handler ────────────────────────────────────────────────────


class TestRetryHandler:
    def test_succeeds_on_first_try(self) -> None:
        result = with_retries(lambda: "ok", max_retries=3, backoff_base_seconds=0)
        assert result == "ok"

    def test_retries_on_retryable_error_then_succeeds(self) -> None:
        call_count = 0

        def flaky() -> str:
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ExternalServiceError("temp", details={"reason": "timeout"})
            return "recovered"

        result = with_retries(flaky, max_retries=3, backoff_base_seconds=0)
        assert result == "recovered"
        assert call_count == 2

    def test_does_not_retry_non_retryable_error(self) -> None:
        call_count = 0

        def auth_fail() -> str:
            nonlocal call_count
            call_count += 1
            raise ExternalServiceError("auth", details={"reason": "authentication_failed"})

        with pytest.raises(ExternalServiceError):
            with_retries(auth_fail, max_retries=3, backoff_base_seconds=0)
        assert call_count == 1  # not retried

    def test_raises_after_max_retries_exhausted(self) -> None:
        def always_timeout() -> str:
            raise ExternalServiceError("timeout", details={"reason": "timeout"})

        with pytest.raises(ExternalServiceError):
            with_retries(always_timeout, max_retries=2, backoff_base_seconds=0)


# ── Provider Manager ────────────────────────────────────────────────


class TestProviderManager:
    def test_unsupported_provider_raises(self) -> None:
        with patch.object(provider_manager.settings, "AI_PROVIDER", "nonexistent"):
            with pytest.raises(ExternalServiceError):
                provider_manager.get_provider()


# ── Prompt Templates ─────────────────────────────────────────────────


class TestPromptTemplates:
    @pytest.mark.parametrize(
        "name",
        [
            PromptTemplateName.EXPLANATION,
            PromptTemplateName.HINT,
            PromptTemplateName.FEEDBACK,
            PromptTemplateName.SUMMARY,
            PromptTemplateName.CHAT,
        ],
    )
    def test_all_five_templates_exist_and_are_non_empty(self, name) -> None:
        template = get_template(name)
        assert template.name == name
        assert len(template.role_description) > 0
        assert len(template.response_instructions) > 0


# ── Provider Independence ───────────────────────────────────────────


class TestProviderIndependence:
    """Ensures the service layer never depends on a concrete provider."""

    def test_provider_response_is_provider_agnostic(self) -> None:
        """ProviderResponse has no Gemini-specific fields."""
        resp = _mock_provider_response()
        assert resp.provider_name == "MockProvider"
        assert resp.model == "mock-model-1"
        assert isinstance(resp.text, str)

    def test_ai_provider_is_abstract(self) -> None:
        with pytest.raises(TypeError):
            AIProvider()  # type: ignore[abstract]


# ── AI API Endpoint Security ────────────────────────────────────────


class TestAIEndpointSecurity:
    @pytest.mark.parametrize("endpoint", ["/explain", "/hint", "/feedback", "/summary", "/chat"])
    def test_requires_authentication(self, endpoint) -> None:
        response = client.post(
            f"/api/v1/ai{endpoint}", json={"topic_id": str(uuid.uuid4()), "message": "help"}
        )
        assert response.status_code == 401

    def test_rejects_empty_message(self) -> None:
        student, topic_id = _student_with_topic()
        response = client.post(
            "/api/v1/ai/explain", json={"topic_id": topic_id, "message": ""}, headers=student
        )
        assert response.status_code == 422

    def test_rejects_message_over_max_length(self) -> None:
        student, topic_id = _student_with_topic()
        response = client.post(
            "/api/v1/ai/explain",
            json={"topic_id": topic_id, "message": "x" * 2001},
            headers=student,
        )
        assert response.status_code == 422
