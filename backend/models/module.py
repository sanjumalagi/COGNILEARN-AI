"""
Module Model.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Module)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.course import Course
    from backend.models.topic import Topic


class Module(Base):
    """
    A course module — the middle tier of Course -> Module -> Topic.

    Cascade policy: deleting a Module cascades to its Topics, since a
    Topic has no meaning without its owning Module.
    """

    __tablename__ = "modules"

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("courses.course_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)

    course: Mapped["Course"] = relationship(back_populates="modules")

    topics: Mapped[list["Topic"]] = relationship(
        back_populates="module",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"Module(module_id={self.module_id!r}, title={self.title!r})"
