"""
Providers Package.

Concrete LLM provider adapters, each implementing `AIProvider`
(base.py). Only `GeminiProvider` is implemented — the current
documented provider; OpenAI/Claude/Llama/Mistral/DeepSeek/local models
are documented as future providers and can be added here without
changing any caller.

Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 5 - Folder Structure)
"""

from backend.providers.base import AIProvider, ProviderResponse
from backend.providers.gemini_provider import GeminiProvider

__all__ = ["AIProvider", "ProviderResponse", "GeminiProvider"]
