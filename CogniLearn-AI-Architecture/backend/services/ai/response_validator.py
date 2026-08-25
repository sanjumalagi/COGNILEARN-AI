"""
Response Validator.

Section 12's documented validation checks, run on the parsed response
before it is returned to a student or persisted. Content-safety
filtering itself (Section 12: "Safe content") is delegated to the
provider's own safety settings (the Gemini SDK's `safety_settings`,
left at their default — the strictest built-in policy — since no
project-specific moderation policy is documented) rather than
reimplemented here; this validator checks response *shape*, not
content moderation.

Reference: 02_System_Architecture/04_AI_Architecture.md (Section 13 - Response Parser workflow)
Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 12 - Response Validation)
"""

from __future__ import annotations

from backend.core.exceptions import ValidationFailedError

#: "Non-empty response" (Section 12) alone would accept a one-character
#: reply; this is the minimum length for a response to be a plausible
#: educational answer rather than a truncated/degenerate one.
_MIN_RESPONSE_CHARS = 10
#: Matches AI_MAX_OUTPUT_TOKENS's intent at the character level (roughly
#: 4 chars/token, the same heuristic token_manager.py uses), as a final
#: guard even if a provider ignores the requested output-token cap.
_MAX_RESPONSE_CHARS = 8000


def validate_response(text: str) -> None:
    """Raises `ValidationFailedError` if `text` fails Section 12's documented checks."""
    if not text or not text.strip():
        raise ValidationFailedError("AI provider returned an empty response.")
    if len(text) < _MIN_RESPONSE_CHARS:
        raise ValidationFailedError("AI provider response was too short to be useful.")
    if len(text) > _MAX_RESPONSE_CHARS:
        raise ValidationFailedError("AI provider response exceeded the maximum allowed length.")