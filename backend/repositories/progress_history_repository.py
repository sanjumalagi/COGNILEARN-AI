"""
Progress History Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import joinedload

from backend.models import ProgressHistory
from backend.repositories.base import BaseRepository


class ProgressHistoryRepository(BaseRepository[ProgressHistory]):
    """Persistence for `ProgressHistory`, eager-loading its Student and Topic."""

    model = ProgressHistory
    default_load_options = (
        joinedload(ProgressHistory.student),
        joinedload(ProgressHistory.topic),
    )