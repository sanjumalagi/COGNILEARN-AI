"""
Assessment Response Model.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Assessment Response)
Reference: 05_DATA_AND_MODEL_DESIGN/02_ENTITY_RELATIONSHIP_MODEL.md (Section 12 - Foreign Keys)
"""

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, utcnow

if TYPE_CHECKING:
    from backend.models.assessment_item import AssessmentItem
    from backend.models.student_profile import StudentProfile


class AssessmentResponse(Base):
    """
    A student's answer to an AssessmentItem — the primary evidence
    consumed by the IRT and BKT engines.

    Cascade policy: this is an educational evidence record. Both its
    `student_id` and `item_id` foreign keys use RESTRICT, so neither a
    StudentProfile nor an AssessmentItem can be deleted while response
    history referencing it still exists.
    """

    __tablename__ = "assessment_responses"

    response_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.student_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessment_items.item_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    selected_answer: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    response_time: Mapped[int] = mapped_column(Integer, nullable=False)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )

    student: Mapped["StudentProfile"] = relationship(
        back_populates="assessment_responses", passive_deletes="all"
    )
    item: Mapped["AssessmentItem"] = relationship(back_populates="responses", passive_deletes="all")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"AssessmentResponse(response_id={self.response_id!r}, is_correct={self.is_correct!r})"
