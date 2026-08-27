"""
Provider Manager (documented as "Model Factory").

Reads `settings.AI_PROVIDER` and returns the matching `AIProvider`
instance. Educational Intelligence and the rest of the AI Service
Layer never instantiate a provider adapter directly — only this
factory does, so adding a new provider (Section 7: OpenAI, Claude,
Llama, Mistral, DeepSeek, local LLMs are documented future work)
requires only a new provider class and one new entry here.

Reference: 02_System_Architecture/04_AI_Architecture.md (Section 12 - Model Factory)
Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 9 - Provider Manager)
"""

from __future__ import annotations

from backend.config import settings
from backend.core.exceptions import ExternalServiceError
from backend.providers.base import AIProvider
from backend.providers.gemini_provider import GeminiProvider

_PROVIDERS: dict[str, type[AIProvider]] = {
    "gemini": GeminiProvider,
}


def get_provider() -> AIProvider:
    """Instantiates the AI provider configured by `settings.AI_PROVIDER`."""
    provider_cls = _PROVIDERS.get(settings.AI_PROVIDER.lower())
    if provider_cls is None:
        raise ExternalServiceError(
            "No AI provider is configured for this deployment.",
            details={"reason": "unsupported_provider"},
        )
    return provider_cls()