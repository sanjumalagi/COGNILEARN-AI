"""
Learner Service.

Implements the five documented GET /learner/* endpoints — read-only
views over the LearnerProfile, TopicMastery, and ProgressHistory data
that the Learning Intelligence pipeline (learning_intelligence_service.py)
maintains.

Every student may only view their own learner model (there is no
documented cross-student access for this module).

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.9 - Learner Module)
Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 7 - Learner Profile APIs)
"""

import uuid

from sqlalchemy.orm import Session

from backend.algorithms.mastery_engine import (
    MasteryLevel,
    classify_mastery_level,
    is_strong_topic,
    is_weak_topic,
)
from backend.core.exceptions import AuthorizationError, NotFoundError, ValidationFailedError
from backend.models import LearnerProfile, ProgressHistory, User, UserRole
from backend.repositories import (
    LearnerProfileRepository,
    Page,
    ProgressHistoryRepository,
    TopicMasteryRepository,
    TopicRepository,
)
from backend.schemas.learner import (
    AbilityDetail,
    LearnerProfileDetail,
    ProgressEntry,
    TopicMasteryDetail,
)
from backend.services.learning_intelligence_service import LearningIntelligenceService


class LearnerService:
    """Business logic for a student viewing their own learner model."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.learner_profiles = LearnerProfileRepository(db)
        self.topic_masteries = TopicMasteryRepository(db)
        self.progress_history = ProgressHistoryRepository(db)
        self.topics = TopicRepository(db)

    def get_profile(self, *, actor: User) -> LearnerProfileDetail:
        profile = self._require_profile(actor)
        masteries = self.topic_masteries.find_all(
            learner_profile_id=profile.learner_profile_id, limit=10_000
        )
        completed_topics = sum(
            1
            for m in masteries.items
            if classify_mastery_level(m.mastery_score) == MasteryLevel.MASTERED
        )

        latest_progress = self.progress_history.find_all(
            student_id=actor.student_profile.student_id,
            offset=0,
            limit=1,
            order_by=ProgressHistory.recorded_at,
            descending=True,
        )
        current_topic = None
        if latest_progress.total > 0:
            topic = self.topics.find_by_id(latest_progress.items[0].topic_id)
            current_topic = topic.title if topic is not None else None

        return LearnerProfileDetail(
            student_id=actor.student_profile.student_id,
            ability_theta=profile.ability_theta,
            overall_mastery=profile.overall_mastery,
            completed_topics=completed_topics,
            current_topic=current_topic,
        )

    def get_ability(self, *, actor: User) -> AbilityDetail:
        self._require_profile(actor)
        irt_result = LearningIntelligenceService(self.db).get_ability_estimate(
            student_id=actor.student_profile.student_id
        )
        return AbilityDetail(
            ability_theta=irt_result.ability,
            ability_category=irt_result.category,
            confidence_score=irt_result.confidence_score,
            difficulty_recommendation=irt_result.difficulty_recommendation,
        )

    def get_mastery(self, *, actor: User, offset: int = 0, limit: int = 50) -> Page[TopicMasteryDetail]:
        profile = self._require_profile(actor)
        page = self.topic_masteries.find_all(
            learner_profile_id=profile.learner_profile_id, offset=offset, limit=limit
        )
        details = []
        for mastery in page.items:
            topic = self.topics.find_by_id(mastery.topic_id)
            details.append(
                TopicMasteryDetail(
                    topic_id=mastery.topic_id,
                    topic=topic.title if topic is not None else "Unknown Topic",
                    mastery=mastery.mastery_score,
                    status=classify_mastery_level(mastery.mastery_score),
                    is_weak=is_weak_topic(mastery.mastery_score),
                    is_strong=is_strong_topic(mastery.mastery_score),
                )
            )
        return Page(items=details, total=page.total, offset=page.offset, limit=page.limit)

    def get_progress(
        self, *, actor: User, offset: int = 0, limit: int = 50, topic_id: uuid.UUID | None = None
    ) -> Page[ProgressEntry]:
        self._require_profile(actor)
        filters = {"topic_id": topic_id} if topic_id is not None else {}
        page = self.progress_history.find_all(
            student_id=actor.student_profile.student_id,
            offset=offset,
            limit=limit,
            order_by=ProgressHistory.recorded_at,
            descending=True,
            **filters,
        )
        return Page(
            items=[ProgressEntry.model_validate(p) for p in page.items],
            total=page.total,
            offset=page.offset,
            limit=page.limit,
        )

    def get_history(self, *, actor: User, offset: int = 0, limit: int = 50) -> Page[ProgressEntry]:
        """The complete, unfiltered chronological progress log (see
        schemas/learner.py docstring for how this differs from
        get_progress, which supports narrowing by topic)."""
        return self.get_progress(actor=actor, offset=offset, limit=limit, topic_id=None)

    def _require_profile(self, actor: User) -> LearnerProfile:
        if actor.role != UserRole.STUDENT:
            raise AuthorizationError("Only students have a learner model.")
        if actor.student_profile is None:
            raise ValidationFailedError(
                "A student profile must be created (PATCH /users/{id}) before viewing learner data."
            )
        page = self.learner_profiles.find_all(student_id=actor.student_profile.student_id, limit=1)
        if page.total == 0:
            raise NotFoundError("No learner data yet — attempt an assessment first.")
        return page.items[0]