"""
Progress History Model.

Tracks learner progress over time.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Progress History)
Reference: 05_DATA_AND_MODEL_DESIGN/02_ENTITY_RELATIONSHIP_MODEL.md (Section 12 - Foreign Keys)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, utcnow

if TYPE_CHECKING:
    from backend.models.student_profile import StudentProfile
    from backend.models.topic import Topic


class ProgressHistory(Base):
    """
    A historical snapshot of a student's mastery on a topic over time.

    Cascade policy: this is a historical/audit record. Both its
    `student_id` and `topic_id` foreign keys use RESTRICT, so neither a
    StudentProfile nor a Topic can be deleted while progress history
    still references it.
    """

    __tablename__ = "progress_history"

    progress_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.student_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.topic_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    student: Mapped["StudentProfile"] = relationship(
        back_populates="progress_history", passive_deletes="all"
    )
    topic: Mapped["Topic"] = relationship(passive_deletes="all")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"ProgressHistory(progress_id={self.progress_id!r}, mastery_score={self.mastery_score!r})"
