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

Reference: 02_System_Architecture/04_AI_Architecture.md (Section 13 - Response Parser)
Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 11 - Response Parser)
"""

from __future__ import annotations

import json
import re

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