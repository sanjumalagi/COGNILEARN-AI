"""
Student Profile Model.

Stores student-specific details, extending the base User record.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Student Profile)
Reference: 05_DATA_AND_MODEL_DESIGN/02_ENTITY_RELATIONSHIP_MODEL.md (Sections 10-12)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.assessment_response import AssessmentResponse
    from backend.models.learner_profile import LearnerProfile
    from backend.models.learning_path import LearningPath
    from backend.models.progress_history import ProgressHistory
    from backend.models.recommendation import Recommendation
    from backend.models.teaching_context import TeachingContext
    from backend.models.user import User


class StudentProfile(Base):
    """
    Student-specific profile data, one-to-one with `User`.

    Cascade policy: deleting the owning User cascades here (enforced on
    the User side). Deleting a StudentProfile cascades to its
    LearnerProfile, since the learner model has no meaning without a
    student. Historical/evidence records (AssessmentResponse,
    ProgressHistory) are NOT cascaded — they use RESTRICT so a student
    with recorded educational history cannot be silently deleted.
    """

    __tablename__ = "student_profiles"

    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    enrollment_number: Mapped[str] = mapped_column(String, nullable=False)
    program: Mapped[str] = mapped_column(String, nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)

    user: Mapped["User"] = relationship(back_populates="student_profile")

    learner_profile: Mapped["LearnerProfile | None"] = relationship(
        back_populates="student",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Educational evidence/history — RESTRICT, no ORM-level cascade.
    assessment_responses: Mapped[list["AssessmentResponse"]] = relationship(
        back_populates="student", passive_deletes="all"
    )
    progress_history: Mapped[list["ProgressHistory"]] = relationship(
        back_populates="student", passive_deletes="all"
    )

    # Generated/derivative adaptive data — cascades with the student.
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    learning_paths: Mapped[list["LearningPath"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    teaching_contexts: Mapped[list["TeachingContext"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"StudentProfile(student_id={self.student_id!r}, user_id={self.user_id!r})"
