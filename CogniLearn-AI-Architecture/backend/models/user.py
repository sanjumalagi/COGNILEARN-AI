"""
User Model.

Stores authentication and role information.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - User)
Reference: 05_DATA_AND_MODEL_DESIGN/02_ENTITY_RELATIONSHIP_MODEL.md (Sections 10-12)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin
from backend.models.enums import UserRole

if TYPE_CHECKING:
    from backend.models.student_profile import StudentProfile
    from backend.models.teacher_profile import TeacherProfile


class User(TimestampMixin, Base):
    """
    An authenticated platform user (Student, Teacher, or Admin).

    Cascade policy: deleting a User cascades to its Student/Teacher
    profile, since a profile has no meaning without its owning user.
    """

    __tablename__ = "users"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            name="user_role",
            native_enum=True,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    # created_at: Mapped[datetime] — provided by TimestampMixin

    student_profile: Mapped["StudentProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    teacher_profile: Mapped["TeacherProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"User(user_id={self.user_id!r}, email={self.email!r}, role={self.role!r})"
