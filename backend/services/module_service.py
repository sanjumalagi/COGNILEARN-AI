"""
Module Service.

Implements the documented Module API operations (Create, Update,
Delete, Get, List) at `/api/v1/modules`.

Access rules mirror Course (same "Course Management Component",
same hierarchical containment): view is open to any authenticated
role, create/edit is Teacher/Admin, delete is Admin only.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.4 - Module API)
Reference: 02_System_Architecture/06_Security_Architecture.md (Section 10 - Permission Matrix)
"""

import uuid

from sqlalchemy.orm import Session

from backend.core.exceptions import AuthorizationError, NotFoundError, ValidationFailedError
from backend.core.logging import get_logger
from backend.models import Module, User, UserRole
from backend.repositories import CourseRepository, ModuleRepository, Page
from backend.schemas.module import ModuleCreate, ModuleUpdate

logger = get_logger(__name__)

_EDITOR_ROLES = (UserRole.TEACHER, UserRole.ADMIN)


class ModuleService:
    """Business logic for viewing, listing, creating, updating, and deleting modules."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.modules = ModuleRepository(db)
        self.courses = CourseRepository(db)

    def list_modules(
        self, *, offset: int = 0, limit: int = 50, course_id: uuid.UUID | None = None
    ) -> Page[Module]:
        filters = {"course_id": course_id} if course_id is not None else {}
        return self.modules.find_all(offset=offset, limit=limit, order_by=Module.sequence_number, **filters)

    def get_module(self, *, module_id: uuid.UUID) -> Module:
        module = self.modules.find_by_id(module_id)
        if module is None:
            raise NotFoundError(f"Module with id={module_id!r} was not found.")
        return module

    def create_module(self, *, actor: User, payload: ModuleCreate) -> Module:
        self._require_editor(actor)
        if self.courses.find_by_id(payload.course_id) is None:
            raise ValidationFailedError(f"Course with id={payload.course_id!r} was not found.")
        module = self.modules.create(
            course_id=payload.course_id, title=payload.title, sequence_number=payload.sequence_number
        )
        logger.info("Module created | module_id=%s | actor_id=%s", module.module_id, actor.user_id)
        return module

    def update_module(self, *, actor: User, module_id: uuid.UUID, payload: ModuleUpdate) -> Module:
        self._require_editor(actor)
        self.get_module(module_id=module_id)
        module = self.modules.update(
            module_id, title=payload.title, sequence_number=payload.sequence_number
        )
        logger.info("Module updated | module_id=%s | actor_id=%s", module_id, actor.user_id)
        return module

    def delete_module(self, *, actor: User, module_id: uuid.UUID) -> None:
        if actor.role != UserRole.ADMIN:
            raise AuthorizationError("Only administrators may delete modules.")
        self.modules.delete(module_id)
        logger.info("Module deleted | module_id=%s | actor_id=%s", module_id, actor.user_id)

    def _require_editor(self, actor: User) -> None:
        if actor.role not in _EDITOR_ROLES:
            raise AuthorizationError("Only teachers and administrators may create or edit modules.")