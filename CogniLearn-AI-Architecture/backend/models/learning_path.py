"""
Learning Path Model.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Learning Path)
Reference: 05_DATA_AND_MODEL_DESIGN/02_ENTITY_RELATIONSHIP_MODEL.md (Section 12 - Foreign Keys)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.student_profile import StudentProfile
    from backend.models.topic import Topic


class LearningPath(Base):
    """
    One step in a student's adaptive learning sequence for a topic.

    Cascade policy: generated/derivative adaptive data — deleting the
    owning StudentProfile cascades here. The `topic_id` foreign key
    uses RESTRICT — a Topic cannot be deleted while learning path
    entries still reference it.
    """

    __tablename__ = "learning_paths"

    path_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.student_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.topic_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)

    student: Mapped["StudentProfile"] = relationship(back_populates="learning_paths")
    topic: Mapped["Topic"] = relationship(passive_deletes="all")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"LearningPath(path_id={self.path_id!r}, status={self.status!r})"
