"""
Assessment Model.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Assessment)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.models.assessment_item import AssessmentItem
    from backend.models.topic import Topic


class Assessment(TimestampMixin, Base):
    """
    Assessment metadata for a Topic.

    Cascade policy: deleting the owning Topic cascades here (enforced
    on the Topic side). Deleting an Assessment cascades to its
    AssessmentItems, since an item has no meaning without its
    assessment.
    """

    __tablename__ = "assessments"

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.topic_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    assessment_type: Mapped[str] = mapped_column(String, nullable=False)
    # created_at: Mapped[datetime] — provided by TimestampMixin

    topic: Mapped["Topic"] = relationship(back_populates="assessments")

    items: Mapped[list["AssessmentItem"]] = relationship(
        back_populates="assessment",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"Assessment(assessment_id={self.assessment_id!r}, title={self.title!r})"
