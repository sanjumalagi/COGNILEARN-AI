"""
Topic Repository.

Matches the documented `ITopicRepository` interface: save(), update()
are provided generically by BaseRepository; `findByModule()` is the one
documented method beyond generic CRUD, implemented below as
`find_by_module()`.

Reference: 03_SOFTWARE_DESIGN/03_Interface_Design.md (Section 6 - ITopicRepository)
"""

import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from backend.models import Topic
from backend.repositories.base import BaseRepository, Page


class TopicRepository(BaseRepository[Topic]):
    """Persistence for `Topic`, eager-loading its Module, Learning Objectives, and Assessments."""

    model = Topic
    default_load_options = (
        selectinload(Topic.module),
        selectinload(Topic.learning_objectives),
        selectinload(Topic.assessments),
    )

    def find_by_module(self, module_id: uuid.UUID, *, offset: int = 0, limit: int = 50) -> Page[Topic]:
        """Returns the Topics belonging to the given Module (documented `findByModule()`)."""
        total = self.db.execute(
            select(func.count()).select_from(Topic).where(Topic.module_id == module_id)
        ).scalar_one()

        stmt = select(Topic).where(Topic.module_id == module_id)
        for option in self.default_load_options:
            stmt = stmt.options(option)
        stmt = stmt.offset(offset).limit(limit)

        items = list(self.db.execute(stmt).unique().scalars().all())
        return Page(items=items, total=total, offset=offset, limit=limit)