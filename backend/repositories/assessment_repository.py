"""
Assessment Repository.

Matches the documented `IAssessmentRepository` interface: save(),
findById(), update() are provided generically by BaseRepository;
`findByTopic()` is the one documented method beyond generic CRUD,
implemented below as `find_by_topic()`.

Reference: 03_SOFTWARE_DESIGN/03_Interface_Design.md (Section 6 - IAssessmentRepository)
Reference: 03_SOFTWARE_DESIGN/02_Class_Design.md (Section 6 - AssessmentRepository)
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from backend.models import Assessment
from backend.repositories.base import BaseRepository, Page


class AssessmentRepository(BaseRepository[Assessment]):
    """Persistence for `Assessment`, eager-loading its Topic and Assessment Items."""

    model = Assessment
    default_load_options = (
        selectinload(Assessment.topic),
        selectinload(Assessment.items),
    )

    def find_by_topic(self, topic_id: uuid.UUID, *, offset: int = 0, limit: int = 50) -> Page[Assessment]:
        """Returns the Assessments belonging to the given Topic (documented `findByTopic()`)."""
        total = self.db.execute(
            select(func.count()).select_from(Assessment).where(Assessment.topic_id == topic_id)
        ).scalar_one()

        stmt = select(Assessment).where(Assessment.topic_id == topic_id)
        for option in self.default_load_options:
            stmt = stmt.options(option)
        stmt = stmt.offset(offset).limit(limit)

        items = list(self.db.execute(stmt).unique().scalars().all())
        return Page(items=items, total=total, offset=offset, limit=limit)