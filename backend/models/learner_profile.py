"""
Learner Profile Model.

Stores learner state used by Educational Intelligence.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Learner Profile)
Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 8 - Indexing Strategy)
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
    from backend.models.topic_mastery import TopicMastery


class LearnerProfile(Base):
    """
    Overall learner state — ability estimate and aggregate mastery — one
    per StudentProfile.

    Cascade policy: deleting the owning StudentProfile cascades here
    (enforced on the StudentProfile side). Deleting a LearnerProfile
    cascades to its TopicMastery records, since per-topic mastery has
    no meaning without the learner profile it belongs to.
    """

    __tablename__ = "learner_profiles"

    learner_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("student_profiles.student_id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    ability_theta: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    overall_mastery: Mapped[float] = mapped_column(Float, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow
    )

    student: Mapped["StudentProfile"] = relationship(back_populates="learner_profile")

    topic_masteries: Mapped[list["TopicMastery"]] = relationship(
        back_populates="learner_profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return (
            f"LearnerProfile(learner_profile_id={self.learner_profile_id!r}, "
            f"ability_theta={self.ability_theta!r})"
        )
