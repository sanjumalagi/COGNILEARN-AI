"""
Assessment Item Model.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Assessment Item)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.assessment import Assessment
    from backend.models.assessment_response import AssessmentResponse


class AssessmentItem(Base):
    """
    A question used in an Assessment.

    Cascade policy: deleting the owning Assessment cascades here
    (enforced on the Assessment side). Deleting an AssessmentItem that
    has recorded AssessmentResponses is RESTRICTED — response history
    is an educational record and must not be silently destroyed.
    """

    __tablename__ = "assessment_items"

    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.assessment_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[float] = mapped_column(Float, nullable=False)
    bloom_level: Mapped[str] = mapped_column(String, nullable=False)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    assessment: Mapped["Assessment"] = relationship(back_populates="items")

    responses: Mapped[list["AssessmentResponse"]] = relationship(
        back_populates="item",
        passive_deletes="all",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"AssessmentItem(item_id={self.item_id!r}, bloom_level={self.bloom_level!r})"
