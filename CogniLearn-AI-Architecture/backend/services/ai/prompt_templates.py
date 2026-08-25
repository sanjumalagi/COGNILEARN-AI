"""
Prompt Templates.

Reusable instructional framing for each documented AI Module endpoint
(Section 23.11 of the API Architecture: /explain, /hint, /feedback,
/summary, /chat). Section 16 of the AI Architecture document names six
templates (Explanation, Hint, Feedback, Revision, Summary, Practice);
this module implements the five that a documented endpoint actually
invokes. "Chat" is not one of Section 16's six names, but is the
correct template for the documented `/chat` endpoint: Section 17's AI
Output Types list names "Conversational Tutoring" as a distinct output
type, and the endpoint table has no other candidate. Revision and
Practice are not implemented here — no endpoint in this module invokes
them (Revision-style content is retrieved as data, not AI-generated,
via GET /adaptive/revision-plan in Module 8); adding unused templates
would be dead code.

Each template supplies the "System Context" and "Instruction" /
"Output Format" sections of the documented prompt structure (Section
15); `prompt_builder.py` supplies the remaining sections (Learner
Context, Educational Context, User Request).

Reference: 02_System_Architecture/04_AI_Architecture.md
(Section 15 - Prompt Engineering Strategy, Section 16 - Prompt Templates)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PromptTemplateName(str, Enum):
    """One entry per documented AI Module endpoint that generates content."""

    EXPLANATION = "explanation"
    HINT = "hint"
    FEEDBACK = "feedback"
    SUMMARY = "summary"
    CHAT = "chat"


@dataclass(frozen=True)
class PromptTemplate:
    """
    A template's fixed instructional framing.

    `teaching_strategy_label` is recorded verbatim in the persisted
    TeachingContext.teaching_strategy column and returned as
    AITutorResponse.teaching_strategy, matching the documented example
    response ("teaching_strategy": "Worked Example") — here it names
    which of the five AI output types (Section 17) this response is.
    """

    name: PromptTemplateName
    teaching_strategy_label: str
    role_description: str
    response_instructions: str


_TEMPLATES: dict[PromptTemplateName, PromptTemplate] = {
    PromptTemplateName.EXPLANATION: PromptTemplate(
        name=PromptTemplateName.EXPLANATION,
        teaching_strategy_label="Personalized Explanation",
        role_description=(
            "Act as an educational tutor. Explain the concept clearly and accurately, "
            "at a level appropriate to the learner's current ability and mastery."
        ),
        response_instructions=(
            "Explain step-by-step, in Markdown, using simple language appropriate to the "
            "learner's ability level. Include one worked example."
        ),
    ),
    PromptTemplateName.HINT: PromptTemplate(
        name=PromptTemplateName.HINT,
        teaching_strategy_label="Contextual Hint",
        role_description=(
            "Act as an educational tutor providing a guided hint. Guide the learner's "
            "reasoning without revealing the final answer."
        ),
        response_instructions=(
            "Provide a short hint in Markdown that nudges the learner toward the answer. "
            "Do not reveal answers immediately or state the final result."
        ),
    ),
    PromptTemplateName.FEEDBACK: PromptTemplate(
        name=PromptTemplateName.FEEDBACK,
        teaching_strategy_label="Adaptive Feedback",
        role_description=(
            "Act as an educational tutor reviewing the learner's recent assessment "
            "performance. Explain mistakes and suggest concrete improvements."
        ),
        response_instructions=(
            "Return Markdown with a concise summary of what went well, what to improve, "
            "and one actionable next step."
        ),
    ),
    PromptTemplateName.SUMMARY: PromptTemplate(
        name=PromptTemplateName.SUMMARY,
        teaching_strategy_label="Learning Summary",
        role_description=(
            "Act as an educational tutor summarizing a learning resource or topic for "
            "quick review."
        ),
        response_instructions="Return a concise bullet-point summary in Markdown.",
    ),
    PromptTemplateName.CHAT: PromptTemplate(
        name=PromptTemplateName.CHAT,
        teaching_strategy_label="Conversational Tutoring",
        role_description=(
            "Act as an educational tutor in an ongoing conversation. Answer the learner's "
            "follow-up question, staying within the current topic and learning objective."
        ),
        response_instructions=(
            "Respond conversationally in Markdown. Do not introduce unrelated topics."
        ),
    ),
}


def get_template(name: PromptTemplateName) -> PromptTemplate:
    """Returns the fixed template for a given AI output type."""
    return _TEMPLATES[name]