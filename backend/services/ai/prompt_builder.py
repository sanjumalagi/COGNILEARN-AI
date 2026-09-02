"""
Prompt Builder.

Converts a `LearnerContext` (context_builder.py) plus a template
(prompt_templates.py) and the learner's current request into the
documented, structured prompt (Section 12 of the AI Prompt Model:
System Prompt -> Teaching Context -> Learner Context -> Learning
Objective -> Current User Request -> Response Instructions).

No prompt is ever constructed outside this module (Section 15:
"No prompts are created directly inside API endpoints or business
logic"), and prompt construction never makes an educational decision —
it only formats decisions already made by Educational Intelligence
(Modules 6–8) and Teaching Intelligence (Module 10).

All pedagogical decisions (teaching strategy, difficulty, recommended
activity, learning objective) are sourced from the TeachingContextData
produced by the Teaching Engine. This module only formats them into the
prompt structure the AI provider consumes.

Reference: 05_DATA_AND_MODEL_DESIGN/05_AI_PROMPT_MODEL.md
Reference: 02_System_Architecture/04_AI_Architecture.md
(Section 9 - Prompt Builder, Section 15 - Prompt Engineering Strategy)
"""

from __future__ import annotations

from dataclasses import dataclass

from backend.algorithms.adaptive_engine.adaptive_decision_engine import Difficulty
from backend.core.exceptions import ValidationFailedError
from backend.services.ai.context_builder import LearnerContext
from backend.services.ai.prompt_templates import PromptTemplate

#: Section 13's "Prompt length is acceptable" with no documented number;
#: this bounds the raw learner-supplied request, not the assembled prompt.
_MAX_USER_MESSAGE_CHARS = 2000


@dataclass(frozen=True)
class Prompt:
    """The two inputs `AIProvider.generate` needs, plus the metadata
    the caller needs to log and label the resulting interaction."""

    system_instruction: str
    user_prompt: str
    teaching_strategy_label: str
    difficulty: Difficulty


class PromptBuilder:
    """Assembles a structured `Prompt` from context + template + request."""

    def build(
        self, *, template: PromptTemplate, context: LearnerContext, user_message: str
    ) -> Prompt:
        self._validate(context=context, user_message=user_message)

        tc = context.teaching_context
        mastery_display = (
            f"{context.topic_mastery:.2f} ({context.mastery_level.value})"
            if context.topic_mastery is not None
            else context.mastery_level.value
        )

        sections = [
            "## Teaching Context",
            f"- Topic: {context.topic_title}",
            f"- Teaching Strategy: {tc.teaching_strategy.value}",
            f"- Difficulty: {tc.difficulty.value}",
            f"- Learning Objective: {tc.learning_objective or 'Not yet defined for this topic.'}",
            f"- Weak Concepts: {', '.join(tc.weak_concepts) or 'None identified.'}",
            f"- Current Mastery: {mastery_display}",
            "",
            "## Learner Context",
            f"- Ability Estimate (theta): {context.ability_theta:.2f} ({context.ability_category.value})",
            f"- Strong Topics: {', '.join(context.strong_topic_titles) or 'None identified.'}",
            f"- Recommended Next Action: {tc.recommended_activity}",
        ]
        if context.recent_interactions:
            sections.append("- Previous AI Interactions (most recent first):")
            sections.extend(f"  - {summary}" for summary in context.recent_interactions)

        sections += [
            "",
            "## Current User Request",
            user_message.strip(),
            "",
            "## Response Instructions",
            template.response_instructions,
        ]

        return Prompt(
            system_instruction=template.role_description,
            user_prompt="\n".join(sections),
            teaching_strategy_label=tc.teaching_strategy.value,
            difficulty=tc.difficulty,
        )

    def _validate(self, *, context: LearnerContext, user_message: str) -> None:
        """Section 13's Prompt Validation, run before any provider call."""
        if not user_message or not user_message.strip():
            raise ValidationFailedError("A user request is required.")
        if len(user_message) > _MAX_USER_MESSAGE_CHARS:
            raise ValidationFailedError(
                f"Request is too long (max {_MAX_USER_MESSAGE_CHARS} characters)."
            )
        if not context.topic_title:
            raise ValidationFailedError("Teaching context is incomplete: topic is required.")