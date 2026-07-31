"""
Assessment Service (Authoring/CRUD).

Implements `create_assessment()` (one of the documented Public
Services) plus the read/update/delete operations added per Module 6's
explicit "Assessment CRUD" scope. The student attempt-flow operations
(start/submit/evaluate/score/history) live in
`assessment_attempt_service.py`.

Access rules mirror Course/Module/Topic (same content-authoring
pattern): view is open to any authenticated role, create/edit is
Teacher/Admin, delete is Admin only.

Reference: 02_System_Architecture/02_Component_Architecture.md (Section 9 - Assessment Intelligence Component)
Reference: 02_System_Architecture/06_Security_Architecture.md (Section 10 - Permission Matrix)
"""

import uuid

from sqlalchemy.orm import Session

from backend.core.exceptions import AuthorizationError, NotFoundError, ValidationFailedError
from backend.core.logging import get_logger
from backend.models import Assessment, User, UserRole
from backend.repositories import AssessmentRepository, Page, TopicRepository
from backend.schemas.assessment import AssessmentCreate, AssessmentUpdate

logger = get_logger(__name__)

_EDITOR_ROLES = (UserRole.TEACHER, UserRole.ADMIN)


class AssessmentService:
    """Business logic for viewing, listing, creating, updating, and deleting assessments."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.assessments = AssessmentRepository(db)
        self.topics = TopicRepository(db)

    def list_assessments(
        self, *, offset: int = 0, limit: int = 50, topic_id: uuid.UUID | None = None
    ) -> Page[Assessment]:
        if topic_id is not None:
            return self.assessments.find_by_topic(topic_id, offset=offset, limit=limit)
        return self.assessments.find_all(offset=offset, limit=limit)

    def get_assessment(self, *, assessment_id: uuid.UUID) -> Assessment:
        assessment = self.assessments.find_by_id(assessment_id)
        if assessment is None:
            raise NotFoundError(f"Assessment with id={assessment_id!r} was not found.")
        return assessment

    def create_assessment(self, *, actor: User, payload: AssessmentCreate) -> Assessment:
        self._require_editor(actor)
        if self.topics.find_by_id(payload.topic_id) is None:
            raise ValidationFailedError(f"Topic with id={payload.topic_id!r} was not found.")
        assessment = self.assessments.create(
            topic_id=payload.topic_id, title=payload.title, assessment_type=payload.assessment_type
        )
        logger.info(
            "Assessment created | assessment_id=%s | actor_id=%s", assessment.assessment_id, actor.user_id
        )
        return assessment

    def update_assessment(
        self, *, actor: User, assessment_id: uuid.UUID, payload: AssessmentUpdate
    ) -> Assessment:
        self._require_editor(actor)
        self.get_assessment(assessment_id=assessment_id)
        assessment = self.assessments.update(
            assessment_id, title=payload.title, assessment_type=payload.assessment_type
        )
        logger.info("Assessment updated | assessment_id=%s | actor_id=%s", assessment_id, actor.user_id)
        return assessment

    def delete_assessment(self, *, actor: User, assessment_id: uuid.UUID) -> None:
        if actor.role != UserRole.ADMIN:
            raise AuthorizationError("Only administrators may delete assessments.")
        self.assessments.delete(assessment_id)
        logger.info("Assessment deleted | assessment_id=%s | actor_id=%s", assessment_id, actor.user_id)

    def _require_editor(self, actor: User) -> None:
        if actor.role not in _EDITOR_ROLES:
            raise AuthorizationError("Only teachers and administrators may create or edit assessments.")