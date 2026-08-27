"""
AI Interaction Model.

Stores AI communication history.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - AI Interaction)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from backend.models.teaching_context import TeachingContext


class AIInteraction(TimestampMixin, Base):
    """
    One prompt/response exchange with an AI provider, generated from a
    TeachingContext.

    Cascade policy: this is an educational/audit record. Its
    `context_id` foreign key uses RESTRICT — a TeachingContext cannot
    be deleted while AI interaction history still references it.
    """

    __tablename__ = "ai_interactions"

    interaction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    context_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("teaching_contexts.context_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    ai_provider: Mapped[str] = mapped_column(String, nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    # created_at: Mapped[datetime] — provided by TimestampMixin

    context: Mapped["TeachingContext"] = relationship(
        back_populates="ai_interactions", passive_deletes="all"
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"AIInteraction(interaction_id={self.interaction_id!r}, ai_provider={self.ai_provider!r})"
