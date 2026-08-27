"""
Learning Objective Model.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Learning Objective)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.topic import Topic


class LearningObjective(Base):
    """
    An outcome associated with a Topic.

    Cascade policy: deleting the owning Topic cascades here (enforced
    on the Topic side).
    """

    __tablename__ = "learning_objectives"

    objective_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.topic_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)

    topic: Mapped["Topic"] = relationship(back_populates="learning_objectives")

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"LearningObjective(objective_id={self.objective_id!r})"
