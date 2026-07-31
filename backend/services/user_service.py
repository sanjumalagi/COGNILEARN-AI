"""
User Management Service.

Implements the User Management Component's responsibilities (Profile
Management) via the four documented endpoints (GET /, GET /{id},
PATCH /{id}, DELETE /{id}).

Access rules are enforced here, in the service layer, per Security
Architecture Section 10: "Permissions should be enforced in the service
layer rather than relying solely on frontend controls." The documented
Permission Matrix does not cover User Management resources explicitly,
so the rules below follow the same least-privilege / Admin-override
pattern the matrix uses everywhere else (e.g. "Delete Course: Admin
only"):

- List all users: Admin only.
- View a user: the user themselves, or an Admin.
- Update a user: the user themselves, or an Admin. Changing `role` is
  Admin-only (prevents self privilege-escalation).
- Delete a user: Admin only (matches the "Account Deactivation" /
  administrative-action responsibility documented for this component).

Reference: 02_System_Architecture/02_Component_Architecture.md (Section 6 - User Management Component)
Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.2 - User Module)
Reference: 02_System_Architecture/06_Security_Architecture.md (Section 10 - Permission Matrix)
"""

import uuid

from sqlalchemy.orm import Session

from backend.core.exceptions import AuthorizationError, ConflictError, NotFoundError, ValidationFailedError
from backend.core.logging import get_logger
from backend.models import User, UserRole
from backend.repositories import Page, StudentProfileRepository, TeacherProfileRepository, UserRepository
from backend.schemas.user import StudentProfileUpdate, TeacherProfileUpdate, UserUpdateRequest

logger = get_logger(__name__)


class UserService:
    """Business logic for viewing, listing, updating, and deleting users and their profiles."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.student_profiles = StudentProfileRepository(db)
        self.teacher_profiles = TeacherProfileRepository(db)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def list_users(
        self, *, actor: User, offset: int = 0, limit: int = 50, role: UserRole | None = None
    ) -> Page[User]:
        if actor.role != UserRole.ADMIN:
            raise AuthorizationError("Only administrators may list users.")
        filters = {"role": role} if role is not None else {}
        return self.users.find_all(offset=offset, limit=limit, order_by=User.created_at, **filters)

    def get_user(self, *, actor: User, target_id: uuid.UUID) -> User:
        self._require_self_or_admin(actor, target_id)
        user = self.users.find_by_id(target_id)
        if user is None:
            raise NotFoundError(f"User with id={target_id!r} was not found.")
        return user

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def update_user(self, *, actor: User, target_id: uuid.UUID, payload: UserUpdateRequest) -> User:
        self._require_self_or_admin(actor, target_id)
        target = self.get_user(actor=actor, target_id=target_id)

        if payload.role is not None:
            if actor.role != UserRole.ADMIN:
                raise AuthorizationError("Only administrators may change a user's role.")
            target = self.users.update(target_id, role=payload.role)

        if payload.email is not None and payload.email != target.email:
            existing = self.users.find_by_email(payload.email)
            if existing is not None and existing.user_id != target_id:
                raise ConflictError("This email address is already registered.")
            target = self.users.update(target_id, email=payload.email)

        if payload.name is not None:
            target = self.users.update(target_id, name=payload.name)

        if payload.student_profile is not None:
            self._upsert_student_profile(target, payload.student_profile)

        if payload.teacher_profile is not None:
            self._upsert_teacher_profile(target, payload.teacher_profile)

        # SQLAlchemy's identity map would otherwise return `target` with its
        # already-loaded (and now stale) student_profile/teacher_profile
        # relationship, even though a profile may have just been created.
        self.db.expire(target, ["student_profile", "teacher_profile"])

        logger.info("User updated | user_id=%s | actor_id=%s", target_id, actor.user_id)
        refreshed = self.users.find_by_id(target_id)
        assert refreshed is not None  # target_id was just validated to exist above
        return refreshed

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def delete_user(self, *, actor: User, target_id: uuid.UUID) -> None:
        if actor.role != UserRole.ADMIN:
            raise AuthorizationError("Only administrators may delete users.")
        self.users.delete(target_id)
        logger.info("User deleted | user_id=%s | actor_id=%s", target_id, actor.user_id)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _require_self_or_admin(self, actor: User, target_id: uuid.UUID) -> None:
        if actor.role != UserRole.ADMIN and actor.user_id != target_id:
            raise AuthorizationError("You may only access your own profile.")

    def _upsert_student_profile(self, user: User, payload: StudentProfileUpdate) -> None:
        if user.role != UserRole.STUDENT:
            raise ValidationFailedError("A student profile can only be set on a Student user.")

        if user.student_profile is None:
            if None in (payload.enrollment_number, payload.program, payload.semester):
                raise ValidationFailedError(
                    "enrollment_number, program, and semester are all required to create a student profile."
                )
            self.student_profiles.create(
                user_id=user.user_id,
                enrollment_number=payload.enrollment_number,
                program=payload.program,
                semester=payload.semester,
            )
        else:
            fields = payload.model_dump(exclude_none=True)
            if fields:
                self.student_profiles.update(user.student_profile.student_id, **fields)

    def _upsert_teacher_profile(self, user: User, payload: TeacherProfileUpdate) -> None:
        if user.role != UserRole.TEACHER:
            raise ValidationFailedError("A teacher profile can only be set on a Teacher user.")

        if user.teacher_profile is None:
            if None in (payload.department, payload.designation):
                raise ValidationFailedError(
                    "department and designation are both required to create a teacher profile."
                )
            self.teacher_profiles.create(
                user_id=user.user_id,
                department=payload.department,
                designation=payload.designation,
            )
        else:
            fields = payload.model_dump(exclude_none=True)
            if fields:
                self.teacher_profiles.update(user.teacher_profile.teacher_id, **fields)