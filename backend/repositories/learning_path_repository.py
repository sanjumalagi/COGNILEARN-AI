"""
Learning Path Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import joinedload

from backend.models import LearningPath
from backend.repositories.base import BaseRepository


class LearningPathRepository(BaseRepository[LearningPath]):
    """Persistence for `LearningPath`, eager-loading its Student and Topic."""

    model = LearningPath
    default_load_options = (
        joinedload(LearningPath.student),
        joinedload(LearningPath.topic),
    )