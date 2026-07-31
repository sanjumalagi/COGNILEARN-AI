"""
Topic Service.

Implements exactly the documented Topic API operations: Create, Update,
Delete, List — at `/api/v1/topics`. Note there is no documented
standalone "Get Topic" operation (unlike Module, which explicitly lists
both "Get Module" and "List Modules"), so no single-item GET is
implemented here.

Access rules mirror Course/Module: create/edit is Teacher/Admin, delete
is Admin only.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.5 - Topic API)
Reference: 02_System_Architecture/06_Security_Architecture.md (Section 10 - Permission Matrix)
"""

import uuid

from sqlalchemy.orm import Session

from backend.core.exceptions import AuthorizationError, NotFoundError, ValidationFailedError
from backend.core.logging import get_logger
from backend.models import Topic, User, UserRole
from backend.repositories import ModuleRepository, Page, TopicRepository
from backend.schemas.topic import TopicCreate, TopicUpdate

logger = get_logger(__name__)

_EDITOR_ROLES = (UserRole.TEACHER, UserRole.ADMIN)


class TopicService:
    """Business logic for listing, creating, updating, and deleting topics."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.topics = TopicRepository(db)
        self.modules = ModuleRepository(db)

    def list_topics(
        self, *, offset: int = 0, limit: int = 50, module_id: uuid.UUID | None = None
    ) -> Page[Topic]:
        if module_id is not None:
            return self.topics.find_by_module(module_id, offset=offset, limit=limit)
        return self.topics.find_all(offset=offset, limit=limit, order_by=Topic.title)

    def create_topic(self, *, actor: User, payload: TopicCreate) -> Topic:
        self._require_editor(actor)
        if self.modules.find_by_id(payload.module_id) is None:
            raise ValidationFailedError(f"Module with id={payload.module_id!r} was not found.")
        topic = self.topics.create(
            module_id=payload.module_id,
            title=payload.title,
            description=payload.description,
            difficulty_level=payload.difficulty_level,
        )
        logger.info("Topic created | topic_id=%s | actor_id=%s", topic.topic_id, actor.user_id)
        return topic

    def update_topic(self, *, actor: User, topic_id: uuid.UUID, payload: TopicUpdate) -> Topic:
        self._require_editor(actor)
        if self.topics.find_by_id(topic_id) is None:
            raise NotFoundError(f"Topic with id={topic_id!r} was not found.")
        topic = self.topics.update(
            topic_id,
            title=payload.title,
            description=payload.description,
            difficulty_level=payload.difficulty_level,
        )
        logger.info("Topic updated | topic_id=%s | actor_id=%s", topic_id, actor.user_id)
        return topic

    def delete_topic(self, *, actor: User, topic_id: uuid.UUID) -> None:
        if actor.role != UserRole.ADMIN:
            raise AuthorizationError("Only administrators may delete topics.")
        self.topics.delete(topic_id)
        logger.info("Topic deleted | topic_id=%s | actor_id=%s", topic_id, actor.user_id)

    def _require_editor(self, actor: User) -> None:
        if actor.role not in _EDITOR_ROLES:
            raise AuthorizationError("Only teachers and administrators may create or edit topics.")