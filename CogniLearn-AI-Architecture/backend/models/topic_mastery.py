"""
Topic Mastery Model.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Topic Mastery)
Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 8 - Indexing Strategy)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.learner_profile import LearnerProfile
    from backend.models.topic import Topic


class TopicMastery(Base):
    """
    A learner's mastery score for one Topic.

    Cascade policy: deleting the owning LearnerProfile cascades here
    (enforced on the LearnerProfile side). The `topic_id` foreign key
    uses RESTRICT — a Topic cannot be deleted while learner mastery
    data still references it.
    """

    __tablename__ = "topic_masteries"

    mastery_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    learner_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("learner_profiles.learner_profile_id", ondelete="CASCADE"),
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

    learner_profile: Mapped["LearnerProfile"] = relationship(back_populates="topic_masteries")
    topic: Mapped["Topic"] = relationship(passive_deletes="all")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"TopicMastery(mastery_id={self.mastery_id!r}, mastery_score={self.mastery_score!r})"
