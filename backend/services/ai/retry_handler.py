"""
Retry Handler.

Retries only the transient failure reasons Section 13 of the AI
Service Implementation document names ("Timeout, Rate limiting,
Temporary provider errors, Network interruptions") — never
authentication failures or invalid requests, which will not succeed
on retry and should surface immediately.

Reference: 02_System_Architecture/04_AI_Architecture.md
(Section 18 - Error Handling, "Automatic retry", "Exponential backoff")
Reference: 06_IMPLEMENTATION_GUIDE/03_AI_SERVICE_IMPLEMENTATION.md (Section 13 - Retry Mechanism)
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from backend.core.exceptions import ExternalServiceError
from backend.core.logging import get_logger
from backend.providers.gemini_provider import RETRYABLE_REASONS

logger = get_logger(__name__)

T = TypeVar("T")


def with_retries(
    func: Callable[[], T], *, max_retries: int, backoff_base_seconds: float
) -> T:
    """
    Calls `func`, retrying on `ExternalServiceError`s whose
    `details["reason"]` is retryable, up to `max_retries` attempts, with
    exponential backoff (`backoff_base_seconds * 2**attempt` between
    attempts). Non-retryable errors, and the final attempt's error, are
    re-raised.
    """
    attempt = 0
    while True:
        try:
            return func()
        except ExternalServiceError as exc:
            reason = exc.details.get("reason")
            attempt += 1
            if reason not in RETRYABLE_REASONS or attempt > max_retries:
                if attempt > max_retries:
                    logger.warning(
                        "AI request failed after %d attempt(s) | reason=%s", attempt, reason
                    )
                raise
            delay = backoff_base_seconds * (2 ** (attempt - 1))
            logger.info(
                "Retrying AI request | attempt=%d/%d | reason=%s | delay_seconds=%.1f",
                attempt,
                max_retries,
                reason,
                delay,
            )
            time.sleep(delay)