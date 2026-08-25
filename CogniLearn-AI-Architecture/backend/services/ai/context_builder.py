"""
Context Builder (documented as "Context Manager").

Gathers exactly the context Section 10 of the AI Architecture document
lists — learner ability (IRT), mastery probability (BKT), weak/strong
learning outcomes, recommended activity, previous AI interactions —
from the already-implemented Educational Intelligence layer (Modules
6-8). No new educational reasoning happens here: every value is read
directly from stored learner state or delegated to an existing
service/algorithm.

"Learning resources" (also listed in Section 10) is omitted: no
Learning Resource entity exists in the implemented schema yet (the
documented Learning Resource API, Section 23.7, has not been built in
any prior module), so there is nothing to gather.

"Recommended activity" is read from AdaptiveDecisionService (Module 8)
rather than a Teaching Engine, since Teaching Intelligence (Module 10)
has not been implemented yet — see prompt_builder.py's module
docstring for the full reasoning. When Module 10 lands, its Teaching
Context should replace this module rather than duplicate it.

Reference: 02_System_Architecture/04_AI_Architecture.md (Section 10 - Context Manager)
Reference: 05_DATA_AND_MODEL_DESIGN/05_AI_PROMPT_MODEL.md (Section 8 - Learner Context)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from backend.algorithms.irt.estimator import AbilityCategory, classify_ability
from backend.algorithms.mastery_engine import (
    MasteryLevel,
    classify_mastery_level,
    is_strong_topic,
    is_weak_topic,
)
from backend.config import settings
from backend.core.exceptions import AuthorizationError, NotFoundError, ValidationFailedError
from backend.models import StudentProfile, TeachingContext, Topic, User, UserRole
from backend.repositories import (
    LearnerProfileRepository,
    LearningObjectiveRepository,
    TeachingContextRepository,
    TopicMasteryRepository,
    TopicRepository,
)
from backend.services.adaptive_decision_service import AdaptiveDecisionService

#: Caps weak/strong topic lists so prompts stay small (Section 22:
#: "only relevant educational context") — no documented numeric limit.
_MAX_CONTEXT_TOPICS = 5
#: Caps how much of a stored AI response is echoed back into a new
#: prompt as "previous interaction" context.
_INTERACTION_SUMMARY_CHARS = 160


@dataclass(frozen=True)
class LearnerContext:
    """Structured educational context for one AI request (Section 8 of the AI Prompt Model)."""

    student_id: uuid.UUID
    topic_id: uuid.UUID
    topic_title: str
    ability_theta: float
    ability_category: AbilityCategory
    topic_mastery: float | None
    mastery_level: MasteryLevel
    weak_topic_titles: list[str]
    strong_topic_titles: list[str]
    recommended_next_action: str | None
    learning_objective: str | None
    recent_interactions: list[str]


class ContextBuilder:
    """Assembles a `LearnerContext` for one student + topic, ready for the Prompt Builder."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.learner_profiles = LearnerProfileRepository(db)
        self.topic_masteries = TopicMasteryRepository(db)
        self.topics = TopicRepository(db)
        self.learning_objectives = LearningObjectiveRepository(db)
        self.teaching_contexts = TeachingContextRepository(db)

    def build(self, *, actor: User, topic_id: uuid.UUID) -> LearnerContext:
        student = self._require_student(actor)
        topic = self._require_topic(topic_id)

        profile_page = self.learner_profiles.find_all(student_id=student.student_id, limit=1)
        if profile_page.total == 0:
            raise NotFoundError("No learner data yet — attempt an assessment first.")
        profile = profile_page.items[0]
        ability_category = classify_ability(profile.ability_theta)

        masteries = self.topic_masteries.find_all(
            learner_profile_id=profile.learner_profile_id, limit=10_000
        )
        topic_mastery = next(
            (m.mastery_score for m in masteries.items if m.topic_id == topic_id), None
        )
        weak_titles, strong_titles = self._weak_and_strong_topic_titles(masteries.items)

        recommended_next_action = self._recommended_next_action(actor)
        learning_objective = self._learning_objective_description(topic_id)
        recent_interactions = self._recent_interactions(student_id=student.student_id, topic_id=topic_id)

        return LearnerContext(
            student_id=student.student_id,
            topic_id=topic_id,
            topic_title=topic.title,
            ability_theta=profile.ability_theta,
            ability_category=ability_category,
            topic_mastery=topic_mastery,
            mastery_level=classify_mastery_level(topic_mastery),
            weak_topic_titles=weak_titles,
            strong_topic_titles=strong_titles,
            recommended_next_action=recommended_next_action,
            learning_objective=learning_objective,
            recent_interactions=recent_interactions,
        )

    def _weak_and_strong_topic_titles(self, masteries: list) -> tuple[list[str], list[str]]:
        weak_titles: list[str] = []
        strong_titles: list[str] = []
        for mastery in masteries:
            if is_weak_topic(mastery.mastery_score) and len(weak_titles) < _MAX_CONTEXT_TOPICS:
                topic = self.topics.find_by_id(mastery.topic_id)
                if topic is not None:
                    weak_titles.append(topic.title)
            elif is_strong_topic(mastery.mastery_score) and len(strong_titles) < _MAX_CONTEXT_TOPICS:
                topic = self.topics.find_by_id(mastery.topic_id)
                if topic is not None:
                    strong_titles.append(topic.title)
        return weak_titles, strong_titles

    def _recommended_next_action(self, actor: User) -> str | None:
        try:
            decision = AdaptiveDecisionService(self.db).get_next_decision(actor=actor)
        except NotFoundError:
            return None
        return decision.next_action.value

    def _learning_objective_description(self, topic_id: uuid.UUID) -> str | None:
        page = self.learning_objectives.find_all(topic_id=topic_id, limit=1)
        return page.items[0].description if page.total > 0 else None

    def _recent_interactions(self, *, student_id: uuid.UUID, topic_id: uuid.UUID) -> list[str]:
        context_page = self.teaching_contexts.find_all(
            student_id=student_id,
            topic_id=topic_id,
            limit=settings.AI_RECENT_INTERACTIONS_LIMIT,
            order_by=TeachingContext.generated_at,
            descending=True,
        )
        summaries: list[str] = []
        for context in context_page.items:
            for interaction in context.ai_interactions:
                snippet = interaction.response[:_INTERACTION_SUMMARY_CHARS].strip()
                summaries.append(f"{context.teaching_strategy}: {snippet}")
        return summaries[: settings.AI_RECENT_INTERACTIONS_LIMIT]

    def _require_student(self, actor: User) -> StudentProfile:
        if actor.role != UserRole.STUDENT:
            raise AuthorizationError("Only students receive AI tutoring.")
        if actor.student_profile is None:
            raise ValidationFailedError(
                "A student profile must be created (PATCH /users/{id}) before requesting AI tutoring."
            )
        return actor.student_profile

    def _require_topic(self, topic_id: uuid.UUID) -> Topic:
        topic = self.topics.find_by_id(topic_id)
        if topic is None:
            raise NotFoundError("Topic not found.")
        return topic