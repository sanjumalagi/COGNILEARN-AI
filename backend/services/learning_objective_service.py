"""
Learning Objective ("Learning Outcome") Service.

Implements exactly the documented Learning Outcome API operations:
Create, Update, View, List — at `/api/v1/learning-outcomes`. Note
there is no documented Delete operation for this resource (unlike
Course/Module/Topic), so no delete method is implemented here.

Access rules mirror Course/Module/Topic: view is open to any
authenticated role, create/edit is Teacher/Admin.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.6 - Learning Outcome API)
Reference: 02_System_Architecture/06_Security_Architecture.md (Section 10 - Permission Matrix)
"""

import uuid

from sqlalchemy.orm import Session

from backend.core.exceptions import AuthorizationError, NotFoundError, ValidationFailedError
from backend.core.logging import get_logger
from backend.models import LearningObjective, User, UserRole
from backend.repositories import LearningObjectiveRepository, Page, TopicRepository
from backend.schemas.learning_objective import LearningObjectiveCreate, LearningObjectiveUpdate

logger = get_logger(__name__)

_EDITOR_ROLES = (UserRole.TEACHER, UserRole.ADMIN)


class LearningObjectiveService:
    """Business logic for viewing, listing, creating, and updating learning objectives."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.learning_objectives = LearningObjectiveRepository(db)
        self.topics = TopicRepository(db)

    def list_learning_objectives(
        self, *, offset: int = 0, limit: int = 50, topic_id: uuid.UUID | None = None
    ) -> Page[LearningObjective]:
        filters = {"topic_id": topic_id} if topic_id is not None else {}
        return self.learning_objectives.find_all(offset=offset, limit=limit, **filters)

    def get_learning_objective(self, *, objective_id: uuid.UUID) -> LearningObjective:
        objective = self.learning_objectives.find_by_id(objective_id)
        if objective is None:
            raise NotFoundError(f"Learning objective with id={objective_id!r} was not found.")
        return objective

    def create_learning_objective(
        self, *, actor: User, payload: LearningObjectiveCreate
    ) -> LearningObjective:
        self._require_editor(actor)
        if self.topics.find_by_id(payload.topic_id) is None:
            raise ValidationFailedError(f"Topic with id={payload.topic_id!r} was not found.")
        objective = self.learning_objectives.create(
            topic_id=payload.topic_id, description=payload.description
        )
        logger.info(
            "Learning objective created | objective_id=%s | actor_id=%s",
            objective.objective_id,
            actor.user_id,
        )
        return objective

    def update_learning_objective(
        self, *, actor: User, objective_id: uuid.UUID, payload: LearningObjectiveUpdate
    ) -> LearningObjective:
        self._require_editor(actor)
        self.get_learning_objective(objective_id=objective_id)
        objective = self.learning_objectives.update(objective_id, description=payload.description)
        logger.info(
            "Learning objective updated | objective_id=%s | actor_id=%s", objective_id, actor.user_id
        )
        return objective

    def _require_editor(self, actor: User) -> None:
        if actor.role not in _EDITOR_ROLES:
            raise AuthorizationError(
                "Only teachers and administrators may create or edit learning objectives."
            )