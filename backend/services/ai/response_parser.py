"""
Response Parser.

Converts a provider's raw text response into application-ready content:
strips incidental Markdown code-fence wrapping some models add around
an entire answer, and normalizes line endings/whitespace. All of our
prompt templates request Markdown output (prompt_templates.py), so
`parse` does not attempt to force structure onto free-form prose;
`try_parse_json` is provided separately for the documented "Parse JSON
responses" responsibility, for any future template that requests a
JSON-formatted answer (Section 10 of the AI Prompt Model: "Output
Format" may be "JSON").

`parse_teaching_content` converts structured JSON output from the
TEACHING_CONTENT template into a `TeachingContent` dataclass, with
graceful fallback when the LLM returns prose instead of JSON.

Reference: 02_System_Architecture/04_AI_Architecture.md (Section 13 - Response Parser)
Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 11 - Response Parser)
"""

from __future__ import annotations

import json
import re

from backend.services.ai.teaching_content import TeachingContent

# Matches a response entirely wrapped in a single fenced code block,
# e.g. "```markdown\n...\n```" or "```\n...\n```" - not fences that
# appear only partway through an otherwise-prose answer.
_FULL_WRAP_FENCE = re.compile(r"^```[a-zA-Z]*\n(.*)\n```$", re.DOTALL)


def parse_response(raw_text: str) -> str:
    """Normalizes a provider's raw text into clean, application-ready content."""
    text = raw_text.strip()
    match = _FULL_WRAP_FENCE.match(text)
    if match:
        text = match.group(1).strip()
    # Normalize CRLF/CR to LF so downstream length checks and storage
    # are consistent regardless of what the provider returned.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def try_parse_json(text: str) -> dict | None:
    """Best-effort JSON parse for templates that request structured output.
    Returns None (not an error) for the common case of prose/Markdown text."""
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def parse_teaching_content(
    raw_text: str,
    *,
    teaching_strategy: str,
    topic: str,
    learning_objective: str | None,
    difficulty: str,
) -> TeachingContent:
    """
    Parse raw LLM output into a structured TeachingContent.

    The passthrough fields (teaching_strategy, topic, learning_objective,
    difficulty) come from TeachingContextData and are always authoritative.
    If the LLM echoes them back differently, the TeachingContextData values
    override. If the LLM returns prose instead of JSON, the text is
    wrapped as an explanation field.

    Args:
        raw_text: Raw text from the AI provider.
        teaching_strategy: Authoritative strategy from TeachingContextData.
        topic: Authoritative topic name from LearnerContext.
        learning_objective: Authoritative objective from TeachingContextData.
        difficulty: Authoritative difficulty from TeachingContextData.

    Returns:
        A TeachingContent dataclass.
    """
    cleaned = parse_response(raw_text)
    data = try_parse_json(cleaned)

    if data is None:
        # LLM returned prose — wrap it as an explanation with
        # authoritative passthrough fields from TeachingContextData.
        return TeachingContent(
            teaching_strategy=teaching_strategy,
            topic=topic,
            learning_objective=learning_objective,
            difficulty=difficulty,
            explanation=cleaned if cleaned else None,
        )

    def _str_or_none(key: str) -> str | None:
        val = data.get(key)
        return str(val).strip() if val is not None and str(val).strip() else None

    def _str_list(key: str) -> tuple[str, ...]:
        val = data.get(key)
        if not isinstance(val, list):
            return ()
        return tuple(str(item).strip() for item in val if str(item).strip())

    return TeachingContent(
        # Passthrough fields — always from TeachingContextData, never LLM
        teaching_strategy=teaching_strategy,
        topic=topic,
        learning_objective=learning_objective,
        difficulty=difficulty,
        # Generated content fields — from LLM output
        explanation=_str_or_none("explanation"),
        examples=_str_list("examples"),
        key_takeaways=_str_list("key_takeaways"),
        practice_question=_str_or_none("practice_question"),
        hints=_str_list("hints"),
        expected_answer=_str_or_none("expected_answer"),
        follow_up_activity=_str_or_none("follow_up_activity"),
    )