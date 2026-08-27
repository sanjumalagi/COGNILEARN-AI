"""
Course Model.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Course)
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.base import Base

if TYPE_CHECKING:
    from backend.models.module import Module


class Course(Base):
    """
    A course — the top of the content hierarchy (Course -> Module -> Topic).

    Cascade policy: deleting a Course cascades to its Modules, since a
    Module has no meaning without its owning Course.
    """

    __tablename__ = "courses"

    course_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    modules: Mapped[list["Module"]] = relationship(
        back_populates="course",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Module.sequence_number",
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging aid only
        return f"Course(course_id={self.course_id!r}, title={self.title!r})"
