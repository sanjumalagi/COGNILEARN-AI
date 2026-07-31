"""
Course Service.

Implements the Course Management Component's course-level
responsibilities via the documented endpoints (GET /, POST /, GET /{id},
PUT /{id}, DELETE /{id}).

Access rules follow the documented Permission Matrix exactly:
View Courses (all roles), Create/Edit Course (Teacher, Admin), Delete
Course (Admin only). Enforced here, in the service layer, per Security
Architecture Section 10.

Reference: 02_System_Architecture/02_Component_Architecture.md (Section 7 - Course Management Component)
Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.3 - Course Module)
Reference: 02_System_Architecture/06_Security_Architecture.md (Section 10 - Permission Matrix)
"""

import uuid

from sqlalchemy.orm import Session

from backend.core.exceptions import AuthorizationError, NotFoundError
from backend.core.logging import get_logger
from backend.models import Course, User, UserRole
from backend.repositories import CourseRepository, Page
from backend.schemas.course import CourseCreate, CourseUpdate

logger = get_logger(__name__)

_EDITOR_ROLES = (UserRole.TEACHER, UserRole.ADMIN)


class CourseService:
    """Business logic for viewing, listing, creating, updating, and deleting courses."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.courses = CourseRepository(db)

    def list_courses(self, *, offset: int = 0, limit: int = 50) -> Page[Course]:
        return self.courses.find_all(offset=offset, limit=limit, order_by=Course.title)

    def get_course(self, *, course_id: uuid.UUID) -> Course:
        course = self.courses.find_by_id(course_id)
        if course is None:
            raise NotFoundError(f"Course with id={course_id!r} was not found.")
        return course

    def create_course(self, *, actor: User, payload: CourseCreate) -> Course:
        self._require_editor(actor)
        course = self.courses.create(title=payload.title, description=payload.description)
        logger.info("Course created | course_id=%s | actor_id=%s", course.course_id, actor.user_id)
        return course

    def update_course(self, *, actor: User, course_id: uuid.UUID, payload: CourseUpdate) -> Course:
        self._require_editor(actor)
        self.get_course(course_id=course_id)
        course = self.courses.update(course_id, title=payload.title, description=payload.description)
        logger.info("Course updated | course_id=%s | actor_id=%s", course_id, actor.user_id)
        return course

    def delete_course(self, *, actor: User, course_id: uuid.UUID) -> None:
        if actor.role != UserRole.ADMIN:
            raise AuthorizationError("Only administrators may delete courses.")
        self.courses.delete(course_id)
        logger.info("Course deleted | course_id=%s | actor_id=%s", course_id, actor.user_id)

    def _require_editor(self, actor: User) -> None:
        if actor.role not in _EDITOR_ROLES:
            raise AuthorizationError("Only teachers and administrators may create or edit courses.")