"""
Teacher Profile Model.

Stores teacher information, extending the base User record.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Teacher Profile)
Reference: 05_DATA_AND_MODEL_DESIGN/02_ENTITY_RELATIONSHIP_MODEL.md (Sections 10-12)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.user import User


class TeacherProfile(Base):
    """
    Teacher-specific profile data, one-to-one with `User`.

    Cascade policy: deleting the owning User cascades here (enforced on
    the User side).
    """

    __tablename__ = "teacher_profiles"

    teacher_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    department: Mapped[str] = mapped_column(String, nullable=False)
    designation: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped["User"] = relationship(back_populates="teacher_profile")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"TeacherProfile(teacher_id={self.teacher_id!r}, user_id={self.user_id!r})"
