"""
Token Manager.

Estimates and bounds prompt size (Section 22 of the AI Architecture
document: "Prompt Optimization" / "Token Management Strategy", and
Section 15 of the AI Service Implementation document: "Estimating
prompt size... Optimizing prompt length"). No tokenizer library is
declared in requirements.txt, and the documented model (Gemini) does
not ship one either, so this uses the standard ~4-characters-per-token
approximation for English text rather than adding a new dependency
for an estimate that is only used defensively (staying comfortably
under the provider's real limit, not billing).

Reference: 02_System_Architecture/04_AI_Architecture.md (Section 23 - Token Management Strategy)
Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 15 - Token Management)
"""

from __future__ import annotations

_CHARS_PER_TOKEN_ESTIMATE = 4


def estimate_tokens(text: str) -> int:
    """Approximate token count for `text` (~4 characters/token for English)."""
    return max(1, len(text) // _CHARS_PER_TOKEN_ESTIMATE)


def fits_within_budget(text: str, *, max_tokens: int) -> bool:
    """Whether `text` is estimated to fit within `max_tokens`."""
    return estimate_tokens(text) <= max_tokens