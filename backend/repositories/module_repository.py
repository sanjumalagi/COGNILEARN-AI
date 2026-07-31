"""
Module Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import selectinload

from backend.models import Module
from backend.repositories.base import BaseRepository


class ModuleRepository(BaseRepository[Module]):
    """Persistence for `Module`, eager-loading its Course and Topics."""

    model = Module
    default_load_options = (
        selectinload(Module.course),
        selectinload(Module.topics),
    )