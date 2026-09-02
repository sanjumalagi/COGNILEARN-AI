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

`validate_teaching_content` validates structured TeachingContent
responses produced by the AI Teaching Content Engine, enforcing
strategy-specific field requirements and topic consistency.

Reference: 02_System_Architecture/04_AI_Architecture.md (Section 13 - Response Parser workflow)
Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 12 - Response Validation)
"""

from __future__ import annotations

from backend.core.exceptions import ValidationFailedError
from backend.services.ai.teaching_content import (
    REQUIRED_FIELDS_BY_STRATEGY,
    TeachingContent,
)

#: "Non-empty response" (Section 12) alone would accept a one-character
#: reply; this is the minimum length for a response to be a plausible
#: educational answer rather than a truncated/degenerate one.
_MIN_RESPONSE_CHARS = 10
#: Matches AI_MAX_OUTPUT_TOKENS's intent at the character level (roughly
#: 4 chars/token, the same heuristic token_manager.py uses), as a final
#: guard even if a provider ignores the requested output-token cap.
_MAX_RESPONSE_CHARS = 8000

#: Minimum character length for content fields that carry substantive
#: instructional text (explanation, practice_question, expected_answer).
_MIN_CONTENT_FIELD_CHARS = 10


def validate_response(text: str) -> None:
    """Raises `ValidationFailedError` if `text` fails Section 12's documented checks."""
    if not text or not text.strip():
        raise ValidationFailedError("AI provider returned an empty response.")
    if len(text) < _MIN_RESPONSE_CHARS:
        raise ValidationFailedError("AI provider response was too short to be useful.")
    if len(text) > _MAX_RESPONSE_CHARS:
        raise ValidationFailedError("AI provider response exceeded the maximum allowed length.")


def validate_teaching_content(
    content: TeachingContent,
    *,
    expected_strategy: str,
    expected_topic: str,
) -> None:
    """
    Validate a structured TeachingContent response.

    Checks:
    1. Teaching strategy is a known value
    2. Teaching strategy matches the expected strategy
    3. Topic matches the expected topic (case-insensitive)
    4. Required fields for the strategy are non-empty
    5. Substantive text fields meet minimum length

    Raises:
        ValidationFailedError: If any check fails.
    """
    # 1. Strategy is known
    if content.teaching_strategy not in REQUIRED_FIELDS_BY_STRATEGY:
        raise ValidationFailedError(
            f"Invalid teaching strategy in AI response: '{content.teaching_strategy}'."
        )

    # 2. Strategy matches expected
    if content.teaching_strategy != expected_strategy:
        raise ValidationFailedError(
            f"AI response strategy '{content.teaching_strategy}' does not match "
            f"expected strategy '{expected_strategy}'."
        )

    # 3. Topic matches expected (case-insensitive)
    if content.topic.strip().lower() != expected_topic.strip().lower():
        raise ValidationFailedError(
            f"AI response topic '{content.topic}' does not match "
            f"expected topic '{expected_topic}'."
        )

    # 4. Required fields for this strategy must be non-empty
    required = REQUIRED_FIELDS_BY_STRATEGY[content.teaching_strategy]
    for field_name in required:
        value = getattr(content, field_name, None)
        if value is None:
            raise ValidationFailedError(
                f"Required field '{field_name}' is missing for strategy "
                f"'{content.teaching_strategy}'."
            )
        # For tuple fields (examples, key_takeaways, hints), check length > 0
        if isinstance(value, tuple) and len(value) == 0:
            raise ValidationFailedError(
                f"Required field '{field_name}' is empty for strategy "
                f"'{content.teaching_strategy}'."
            )
        # For string fields, check non-empty
        if isinstance(value, str) and not value.strip():
            raise ValidationFailedError(
                f"Required field '{field_name}' is empty for strategy "
                f"'{content.teaching_strategy}'."
            )

    # 5. Substantive text fields meet minimum length
    for field_name in ("explanation", "practice_question", "expected_answer"):
        value = getattr(content, field_name, None)
        if value is not None and len(value.strip()) > 0 and len(value.strip()) < _MIN_CONTENT_FIELD_CHARS:
            if field_name in required:
                raise ValidationFailedError(
                    f"Field '{field_name}' is too short (minimum {_MIN_CONTENT_FIELD_CHARS} "
                    f"characters) for strategy '{content.teaching_strategy}'."
                )