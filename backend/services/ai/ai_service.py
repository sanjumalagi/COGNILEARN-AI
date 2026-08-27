"""
AI Service.

The single entry point the API layer calls for all five documented AI
Module endpoints (explain/hint/feedback/summary/chat). Orchestrates
the full documented AI Request Lifecycle (Section 14): builds context,
builds the prompt, invokes the configured provider with retries,
parses and validates the response, persists the interaction, and
returns the result.

Reference: 02_System_Architecture/04_AI_Architecture.md
(Section 6 - AI Service Layer, Section 14 - AI Request Lifecycle)
Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md
(Section 10 - AI Tutor APIs)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from backend.config import settings
from backend.core.logging import get_logger
from backend.models import User
from backend.providers.base import ProviderResponse
from backend.repositories import AIInteractionRepository, TeachingContextRepository
from backend.services.ai import provider_manager, response_parser, response_validator, token_manager
from backend.services.ai.context_builder import ContextBuilder
from backend.services.ai.prompt_builder import Prompt, PromptBuilder
from backend.services.ai.prompt_templates import PromptTemplateName, get_template
from backend.services.ai.retry_handler import with_retries

logger = get_logger(__name__)


@dataclass(frozen=True)
class AITutorResult:
    """Matches the documented AI Tutor Response shape exactly."""

    response: str
    teaching_strategy: str
    generated_by: str


class AIService:
    """Business logic for the five documented AI Module endpoints."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.context_builder = ContextBuilder(db)
        self.prompt_builder = PromptBuilder()
        self.teaching_contexts = TeachingContextRepository(db)
        self.ai_interactions = AIInteractionRepository(db)

    def explain(self, *, actor: User, topic_id: uuid.UUID, user_message: str) -> AITutorResult:
        return self._generate(
            PromptTemplateName.EXPLANATION, actor=actor, topic_id=topic_id, user_message=user_message
        )

    def hint(self, *, actor: User, topic_id: uuid.UUID, user_message: str) -> AITutorResult:
        return self._generate(
            PromptTemplateName.HINT, actor=actor, topic_id=topic_id, user_message=user_message
        )

    def feedback(self, *, actor: User, topic_id: uuid.UUID, user_message: str) -> AITutorResult:
        return self._generate(
            PromptTemplateName.FEEDBACK, actor=actor, topic_id=topic_id, user_message=user_message
        )

    def summary(self, *, actor: User, topic_id: uuid.UUID, user_message: str) -> AITutorResult:
        return self._generate(
            PromptTemplateName.SUMMARY, actor=actor, topic_id=topic_id, user_message=user_message
        )

    def chat(self, *, actor: User, topic_id: uuid.UUID, user_message: str) -> AITutorResult:
        return self._generate(
            PromptTemplateName.CHAT, actor=actor, topic_id=topic_id, user_message=user_message
        )

    def _generate(
        self, template_name: PromptTemplateName, *, actor: User, topic_id: uuid.UUID, user_message: str
    ) -> AITutorResult:
        context = self.context_builder.build(actor=actor, topic_id=topic_id)
        prompt = self.prompt_builder.build(
            template=get_template(template_name), context=context, user_message=user_message
        )

        prompt_tokens_estimate = token_manager.estimate_tokens(prompt.user_prompt)
        provider_response = with_retries(
            lambda: self._invoke_provider(prompt),
            max_retries=settings.AI_MAX_RETRIES,
            backoff_base_seconds=settings.AI_RETRY_BACKOFF_BASE_SECONDS,
        )

        parsed_text = response_parser.parse_response(provider_response.text)
        response_validator.validate_response(parsed_text)

        self._log_interaction(
            student_id=context.student_id,
            topic_id=topic_id,
            prompt=prompt,
            parsed_text=parsed_text,
            provider_response=provider_response,
        )

        logger.info(
            "AI interaction complete | student_id=%s | template=%s | provider=%s | model=%s | "
            "latency_ms=%d | prompt_tokens_estimate=%d | prompt_tokens=%s | completion_tokens=%s",
            context.student_id,
            template_name.value,
            provider_response.provider_name,
            provider_response.model,
            provider_response.latency_ms,
            prompt_tokens_estimate,
            provider_response.prompt_tokens,
            provider_response.completion_tokens,
        )

        return AITutorResult(
            response=parsed_text,
            teaching_strategy=prompt.teaching_strategy_label,
            generated_by=provider_response.provider_name,
        )

    def _invoke_provider(self, prompt: Prompt) -> ProviderResponse:
        provider = provider_manager.get_provider()
        return provider.generate(
            system_instruction=prompt.system_instruction,
            user_prompt=prompt.user_prompt,
            timeout_seconds=settings.AI_REQUEST_TIMEOUT_SECONDS,
        )

    def _log_interaction(
        self,
        *,
        student_id: uuid.UUID,
        topic_id: uuid.UUID,
        prompt: Prompt,
        parsed_text: str,
        provider_response: ProviderResponse,
    ) -> None:
        """
        Persists the documented TeachingContext + AIInteraction pair
        (Section 5 of the Database Schema). See prompt_builder.py's
        module docstring for why creating a minimal TeachingContext
        row here — populated entirely from data Modules 6-8 already
        produced — does not constitute implementing Teaching
        Intelligence.
        """
        context_row = self.teaching_contexts.create(
            student_id=student_id,
            topic_id=topic_id,
            teaching_strategy=prompt.teaching_strategy_label,
            learning_objective=self._resolve_learning_objective(topic_id),
            difficulty=prompt.difficulty.value,
        )
        self.ai_interactions.create(
            context_id=context_row.context_id,
            ai_provider=provider_response.provider_name,
            prompt=prompt.user_prompt,
            response=parsed_text,
        )

    def _resolve_learning_objective(self, topic_id: uuid.UUID) -> str:
        # TeachingContext.learning_objective is NOT NULL; a fallback
        # covers topics with no learning objective authored yet.
        from backend.repositories import LearningObjectiveRepository

        page = LearningObjectiveRepository(self.db).find_all(topic_id=topic_id, limit=1)
        if page.total > 0:
            return page.items[0].description
        return "General understanding of this topic."