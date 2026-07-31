"""
Assessment Item Service (Question Bank Management).

Implements Assessment Item CRUD. Full item detail (including the
answer key) is Teacher/Admin only — students never see `correct_answer`
or `explanation` through this service; the sanitized view used during
an attempt is served separately by `assessment_attempt_service.py`.

Access rules mirror Assessment: view/edit is Teacher/Admin, delete is
Admin only (deleting an item with recorded responses is blocked by the
existing RESTRICT foreign key from Module 1, surfaced automatically as
a ConflictError by the repository layer).

Reference: 02_System_Architecture/02_Component_Architecture.md (Section 9 - Assessment Intelligence Component)
Reference: 02_System_Architecture/06_Security_Architecture.md (Section 10 - Permission Matrix)
"""

import uuid

from sqlalchemy.orm import Session

from backend.core.exceptions import AuthorizationError, NotFoundError, ValidationFailedError
from backend.core.logging import get_logger
from backend.models import AssessmentItem, User, UserRole
from backend.repositories import AssessmentItemRepository, AssessmentRepository, Page
from backend.schemas.assessment_item import AssessmentItemCreate, AssessmentItemUpdate

logger = get_logger(__name__)

_EDITOR_ROLES = (UserRole.TEACHER, UserRole.ADMIN)


class AssessmentItemService:
    """Business logic for viewing, listing, creating, updating, and deleting assessment items."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.items = AssessmentItemRepository(db)
        self.assessments = AssessmentRepository(db)

    def list_items(
        self, *, actor: User, offset: int = 0, limit: int = 50, assessment_id: uuid.UUID | None = None
    ) -> Page[AssessmentItem]:
        self._require_editor(actor)
        filters = {"assessment_id": assessment_id} if assessment_id is not None else {}
        return self.items.find_all(offset=offset, limit=limit, **filters)

    def get_item(self, *, actor: User, item_id: uuid.UUID) -> AssessmentItem:
        self._require_editor(actor)
        item = self.items.find_by_id(item_id)
        if item is None:
            raise NotFoundError(f"Assessment item with id={item_id!r} was not found.")
        return item

    def create_item(self, *, actor: User, payload: AssessmentItemCreate) -> AssessmentItem:
        self._require_editor(actor)
        if self.assessments.find_by_id(payload.assessment_id) is None:
            raise ValidationFailedError(f"Assessment with id={payload.assessment_id!r} was not found.")
        item = self.items.create(
            assessment_id=payload.assessment_id,
            question_text=payload.question_text,
            difficulty=payload.difficulty,
            bloom_level=payload.bloom_level,
            correct_answer=payload.correct_answer,
            explanation=payload.explanation,
        )
        logger.info("Assessment item created | item_id=%s | actor_id=%s", item.item_id, actor.user_id)
        return item

    def update_item(
        self, *, actor: User, item_id: uuid.UUID, payload: AssessmentItemUpdate
    ) -> AssessmentItem:
        self._require_editor(actor)
        if self.items.find_by_id(item_id) is None:
            raise NotFoundError(f"Assessment item with id={item_id!r} was not found.")
        item = self.items.update(
            item_id,
            question_text=payload.question_text,
            difficulty=payload.difficulty,
            bloom_level=payload.bloom_level,
            correct_answer=payload.correct_answer,
            explanation=payload.explanation,
        )
        logger.info("Assessment item updated | item_id=%s | actor_id=%s", item_id, actor.user_id)
        return item

    def delete_item(self, *, actor: User, item_id: uuid.UUID) -> None:
        if actor.role != UserRole.ADMIN:
            raise AuthorizationError("Only administrators may delete assessment items.")
        self.items.delete(item_id)
        logger.info("Assessment item deleted | item_id=%s | actor_id=%s", item_id, actor.user_id)

    def _require_editor(self, actor: User) -> None:
        if actor.role not in _EDITOR_ROLES:
            raise AuthorizationError(
                "Only teachers and administrators may access assessment item content."
            )