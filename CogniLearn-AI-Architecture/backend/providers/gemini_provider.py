"""
Gemini Provider Adapter.

Wraps `google-generativeai` behind the `AIProvider` interface. This is
the only module in the codebase that imports `google.generativeai` —
every other component talks to `AIProvider`, never to the SDK.

Reference: 02_System_Architecture/04_AI_Architecture.md
(Section 11 - Provider Adapter, "Current: Google Gemini")
Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 7 - Supported AI Providers)
"""

from __future__ import annotations

import time

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from backend.config import settings
from backend.core.exceptions import ExternalServiceError
from backend.core.logging import get_logger
from backend.providers.base import AIProvider, ProviderResponse

logger = get_logger(__name__)

# Maps Gemini SDK errors to a short, provider-independent reason code
# recorded in ExternalServiceError.details — never the raw exception
# text, which for auth failures can echo back request metadata.
_ERROR_REASON_BY_EXCEPTION: dict[type[Exception], str] = {
    google_exceptions.DeadlineExceeded: "timeout",
    google_exceptions.GatewayTimeout: "timeout",
    google_exceptions.ResourceExhausted: "rate_limited",
    google_exceptions.ServiceUnavailable: "provider_unavailable",
    google_exceptions.InvalidArgument: "invalid_request",
    google_exceptions.PermissionDenied: "authentication_failed",
    google_exceptions.Unauthenticated: "authentication_failed",
}

#: Reason codes that `retry_handler.with_retries` should retry (Section 13:
#: "Timeout, Rate limiting, Temporary provider errors, Network interruptions").
RETRYABLE_REASONS = frozenset({"timeout", "provider_unavailable", "network_error"})


class GeminiProvider(AIProvider):
    """Google Gemini implementation of the Provider Adapter."""

    provider_name = "Gemini"

    def __init__(self) -> None:
        if not settings.GEMINI_API_KEY:
            # Caught before ever touching the SDK, so the resulting error
            # message is clear and never depends on how the SDK phrases a
            # missing-credential failure.
            raise ExternalServiceError(
                "AI provider is not configured.", details={"reason": "missing_api_key"}
            )
        # google-generativeai keeps API-key state in module-level global
        # config rather than a client instance; scoping the configure()
        # call to immediately before use (instead of at import time) keeps
        # this adapter safe to construct repeatedly and easy to unit test
        # with a monkeypatched `genai` module.
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self._model_name = settings.GEMINI_MODEL

    def generate(
        self, *, system_instruction: str, user_prompt: str, timeout_seconds: float
    ) -> ProviderResponse:
        model = genai.GenerativeModel(
            model_name=self._model_name,
            system_instruction=system_instruction,
            generation_config=genai.GenerationConfig(
                max_output_tokens=settings.AI_MAX_OUTPUT_TOKENS
            ),
        )

        started_at = time.monotonic()
        try:
            response = model.generate_content(
                user_prompt, request_options={"timeout": timeout_seconds}
            )
        except tuple(_ERROR_REASON_BY_EXCEPTION) as exc:
            reason = _ERROR_REASON_BY_EXCEPTION[type(exc)]
            logger.warning("Gemini request failed | reason=%s", reason)
            raise ExternalServiceError(
                "The AI provider could not complete this request.", details={"reason": reason}
            ) from exc
        except Exception as exc:  # noqa: BLE001 - any other SDK/network failure is still ours to translate
            logger.warning("Gemini request failed | reason=unexpected_error")
            raise ExternalServiceError(
                "The AI provider could not complete this request.",
                details={"reason": "unexpected_error"},
            ) from exc
        latency_ms = int((time.monotonic() - started_at) * 1000)

        try:
            text = response.text
        except ValueError as exc:
            # The SDK raises ValueError from `.text` when every candidate
            # was blocked (safety filters) or generation otherwise
            # produced no usable content — a valid response shape, but
            # not a usable one for the caller.
            raise ExternalServiceError(
                "The AI provider returned no usable content.",
                details={"reason": "empty_response"},
            ) from exc

        usage = getattr(response, "usage_metadata", None)
        prompt_tokens = getattr(usage, "prompt_token_count", None) if usage else None
        completion_tokens = getattr(usage, "candidates_token_count", None) if usage else None

        return ProviderResponse(
            text=text,
            provider_name=self.provider_name,
            model=self._model_name,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )