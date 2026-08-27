"""
Learning Path Service.

Orchestrates the Learning Path Engine: gathers a student's encountered
topic mastery evidence, finds the next not-yet-encountered topic in
curriculum order (Course -> Module.sequence_number -> Topic, composed
entirely from existing Module 2 repository methods), applies the
documented ordering rules
(algorithms/adaptive_engine/learning_path_engine.py), and persists the
result — replacing any previous path, since the path reflects current
evidence rather than a historical log.

Reference: 04_ALGORITHM_DESIGN/05_LEARNING_PATH_ENGINE_DESIGN.md
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.algorithms.adaptive_engine.learning_path_engine import (
    TopicMasteryEvidence,
    build_learning_path,
)
from backend.core.exceptions import AuthorizationError, NotFoundError, ValidationFailedError
from backend.core.logging import get_logger
from backend.models import LearningPath, StudentProfile, User, UserRole
from backend.repositories import (
    LearnerProfileRepository,
    LearningPathRepository,
    ModuleRepository,
    TopicMasteryRepository,
    TopicRepository,
)

logger = get_logger(__name__)


class LearningPathService:
    """Business logic for generating and retrieving a student's learning path."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.learning_paths = LearningPathRepository(db)
        self.learner_profiles = LearnerProfileRepository(db)
        self.topic_masteries = TopicMasteryRepository(db)
        self.modules = ModuleRepository(db)
        self.topics = TopicRepository(db)

    def refresh_and_get_path(
        self, *, actor: User, course_id: uuid.UUID | None = None
    ) -> list[LearningPath]:
        """Regenerates and persists the student's learning path from
        current evidence, replacing any previous path, and returns it."""
        student = self._require_student(actor)
        learner_profile_id = self._learner_profile_id(student)

        masteries_page = self.topic_masteries.find_all(learner_profile_id=learner_profile_id, limit=10_000)
        encountered_ids = {m.topic_id for m in masteries_page.items}
        evidence = [
            TopicMasteryEvidence(topic_id=m.topic_id, mastery_score=m.mastery_score)
            for m in masteries_page.items
        ]

        next_topic_id = (
            self._find_next_unencountered_topic(course_id=course_id, encountered_ids=encountered_ids)
            if course_id is not None
            else None
        )

        steps = build_learning_path(encountered_topics=evidence, next_unencountered_topic_id=next_topic_id)

        existing = self.learning_paths.find_all(student_id=student.student_id, limit=10_000)
        for old in existing.items:
            self.learning_paths.delete(old.path_id)

        created = [
            self.learning_paths.create(
                student_id=student.student_id,
                topic_id=step.topic_id,
                sequence_order=step.sequence_order,
                status=step.status.value,
            )
            for step in steps
        ]
        logger.info("Learning path refreshed | student_id=%s | steps=%d", student.student_id, len(created))
        return created

    def find_next_unencountered_topic_id(
        self, *, actor: User, course_id: uuid.UUID | None
    ) -> uuid.UUID | None:
        """Exposed for AdaptiveDecisionService, so it does not duplicate
        curriculum-order traversal logic."""
        if course_id is None:
            return None
        student = self._require_student(actor)
        learner_profile_id = self._learner_profile_id(student)
        masteries_page = self.topic_masteries.find_all(learner_profile_id=learner_profile_id, limit=10_000)
        encountered_ids = {m.topic_id for m in masteries_page.items}
        return self._find_next_unencountered_topic(course_id=course_id, encountered_ids=encountered_ids)

    def _find_next_unencountered_topic(
        self, *, course_id: uuid.UUID, encountered_ids: set[uuid.UUID]
    ) -> uuid.UUID | None:
        modules_page = self.modules.find_all(
            course_id=course_id, offset=0, limit=1000, order_by=self.modules.model.sequence_number
        )
        for module in modules_page.items:
            topics_page = self.topics.find_by_module(module.module_id, offset=0, limit=1000)
            for topic in topics_page.items:
                if topic.topic_id not in encountered_ids:
                    return topic.topic_id
        return None

    def _learner_profile_id(self, student: StudentProfile) -> uuid.UUID:
        page = self.learner_profiles.find_all(student_id=student.student_id, limit=1)
        if page.total == 0:
            raise NotFoundError("No learner data yet — attempt an assessment first.")
        return page.items[0].learner_profile_id

    def _require_student(self, actor: User) -> StudentProfile:
        if actor.role != UserRole.STUDENT:
            raise AuthorizationError("Only students have a learning path.")
        if actor.student_profile is None:
            raise ValidationFailedError(
                "A student profile must be created (PATCH /users/{id}) before viewing a learning path."
            )
        return actor.student_profile