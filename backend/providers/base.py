"""
Provider Adapter — base interface.

Every supported LLM provider (Gemini now; OpenAI/Claude/Llama/Mistral/
DeepSeek/local models are documented as future providers) implements
this common interface so the rest of the application never talks to a
provider SDK directly.

Reference: 02_System_Architecture/04_AI_Architecture.md (Section 11 - Provider Adapter)
Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 6 - AI Provider Abstraction)
"""

from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class ProviderResponse:
    """
    Standardized response returned by every provider adapter (Section 11:
    "Returning standardized responses to the AI Service Layer").
    """

    text: str
    provider_name: str
    model: str
    latency_ms: int
    prompt_tokens: int | None
    completion_tokens: int | None


class AIProvider(abc.ABC):
    """Common interface every provider adapter implements."""

    #: Short, stable identifier used in logs and AIInteraction.ai_provider.
    provider_name: str

    @abc.abstractmethod
    def generate(
        self, *, system_instruction: str, user_prompt: str, timeout_seconds: float
    ) -> ProviderResponse:
        """
        Sends a prompt to the provider and returns a standardized response.

        Implementations must raise `backend.core.exceptions.ExternalServiceError`
        (never a provider-SDK-specific exception) for authentication
        failures, timeouts, rate limits, provider outages, and invalid
        responses, so callers never need to know which provider is active.
        """
        raise NotImplementedError