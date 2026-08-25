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
it only formats decisions and evidence that Modules 6-8 already
computed. This is the module-level design decision on "Teaching
Context":

  The documented architecture (05_DATA_AND_MODEL_DESIGN/05_AI_PROMPT_MODEL.md
  Section 4/7) has a Teaching Engine generate a "Teaching Context"
  (current topic, teaching strategy, difficulty, learning objective,
  weak concepts, current mastery) that this module then formats into a
  prompt. The Teaching Engine belongs to Teaching Intelligence
  (Module 10), which has not been implemented yet. Every one of those
  Teaching Context fields is nonetheless already available from
  Modules 6-8 without any new pedagogical reasoning:
    - Current Topic / Learning Objective / Current Mastery / Weak
      Concepts: read directly from stored learner state
      (context_builder.py).
    - Teaching Strategy: the fixed label on the template selected by
      which documented AI Module endpoint was called
      (prompt_templates.py) — not a strategy *decision*, since the
      "decision" here is simply which of the 5 documented endpoints
      the learner invoked.
    - Difficulty: read from the learner's IRT ability category via a
      small, local mapping mirroring Module 8's Adaptive Decision
      Engine's own difficulty categorization, not a new rule.
  So this module supplies the "Teaching Context" prompt section
  entirely from existing Educational Intelligence outputs, with zero
  new instructional reasoning — consistent with "AI services may
  consume outputs from Educational Intelligence" and "Do NOT move
  pedagogical decision-making into the LLM." When Module 10 is
  implemented, its real Teaching Context should replace this section
  rather than duplicate it.

Reference: 05_DATA_AND_MODEL_DESIGN/05_AI_PROMPT_MODEL.md
Reference: 02_System_Architecture/04_AI_Architecture.md
(Section 9 - Prompt Builder, Section 15 - Prompt Engineering Strategy)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.algorithms.irt.estimator import AbilityCategory
from backend.core.exceptions import ValidationFailedError
from backend.services.ai.context_builder import LearnerContext
from backend.services.ai.prompt_templates import PromptTemplate

#: Section 13's "Prompt length is acceptable" with no documented number;
#: this bounds the raw learner-supplied request, not the assembled prompt.
_MAX_USER_MESSAGE_CHARS = 2000


class Difficulty(str, Enum):
    """Categorical difficulty label, mirroring Module 8's own difficulty categorization."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


# Mirrors the ability->difficulty mapping already established in Module
# 8's adaptive_decision_engine.py (Beginner->easy, Intermediate->medium,
# Advanced->hard) — duplicated at the enum-value level (not imported)
# since Module 8's mapping is module-private there; kept in sync by
# using the same public `AbilityCategory` values Module 8 itself reads.
_DIFFICULTY_BY_ABILITY = {
    AbilityCategory.BEGINNER: Difficulty.EASY,
    AbilityCategory.INTERMEDIATE: Difficulty.MEDIUM,
    AbilityCategory.ADVANCED: Difficulty.HARD,
}


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

        difficulty = _DIFFICULTY_BY_ABILITY[context.ability_category]
        mastery_display = (
            f"{context.topic_mastery:.2f} ({context.mastery_level.value})"
            if context.topic_mastery is not None
            else context.mastery_level.value
        )

        sections = [
            "## Teaching Context",
            f"- Topic: {context.topic_title}",
            f"- Teaching Strategy: {template.teaching_strategy_label}",
            f"- Difficulty: {difficulty.value}",
            f"- Learning Objective: {context.learning_objective or 'Not yet defined for this topic.'}",
            f"- Weak Concepts: {', '.join(context.weak_topic_titles) or 'None identified.'}",
            f"- Current Mastery: {mastery_display}",
            "",
            "## Learner Context",
            f"- Ability Estimate (theta): {context.ability_theta:.2f} ({context.ability_category.value})",
            f"- Strong Topics: {', '.join(context.strong_topic_titles) or 'None identified.'}",
            f"- Recommended Next Action: {context.recommended_next_action or 'Not available.'}",
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
            teaching_strategy_label=template.teaching_strategy_label,
            difficulty=difficulty,
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