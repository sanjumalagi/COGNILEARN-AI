"""
Topic Model.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Topic)
Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 8 - Indexing Strategy)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.assessment import Assessment
    from backend.models.learning_objective import LearningObjective
    from backend.models.module import Module


class Topic(Base):
    """
    An individual learning topic — the leaf of Course -> Module -> Topic,
    and the anchor point for learning objectives, assessments, and every
    learner-modeling entity (mastery, recommendations, learning paths,
    teaching context, progress history).

    Cascade policy: deleting a Topic cascades to its own structural
    children (LearningObjective, Assessment), since those have no
    meaning without their Topic. It does NOT cascade to learner-side
    entities that merely reference a topic (TopicMastery, Recommendation,
    LearningPath, TeachingContext, ProgressHistory) — those use RESTRICT
    so removing a Topic cannot silently destroy unrelated learner data.
    """

    __tablename__ = "topics"

    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("modules.module_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty_level: Mapped[int] = mapped_column(Integer, nullable=False)

    module: Mapped["Module"] = relationship(back_populates="topics")

    learning_objectives: Mapped[list["LearningObjective"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="topic",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"Topic(topic_id={self.topic_id!r}, title={self.title!r})"
