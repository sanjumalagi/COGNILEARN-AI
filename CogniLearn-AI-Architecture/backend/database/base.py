"""
Declarative Base.

Provides the single SQLAlchemy declarative base that every ORM model in
the application inherits from, plus a reusable timestamp mixin for the
one timestamp field documented consistently across multiple entities.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5)
Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.3 - Database Package)
"""

from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Shared declarative base for all ORM models.

    All entities in `backend.models` must inherit from this class so
    they register on the same `MetaData` object, which Alembic's
    autogenerate support and `Base.metadata.create_all()` both rely on.
    """


def utcnow() -> datetime:
    """Returns the current UTC time as a timezone-aware datetime."""
    return datetime.now(timezone.utc)


class TimestampMixin:
    """
    Adds a `created_at` column to a model.

    Applied only to entities whose documented schema includes a
    creation timestamp (User.created_at, Assessment.created_at,
    AIInteraction.created_at). Other documented timestamp fields
    (e.g. LearnerProfile.last_updated, Recommendation.generated_at,
    AssessmentResponse.submitted_at, ProgressHistory.recorded_at) are
    semantically distinct per the schema and are declared directly on
    their owning model instead of through this shared mixin.

    Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow, server_default=func.now(), index=True
    )
