"""
Learning Objective Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import selectinload

from backend.models import LearningObjective
from backend.repositories.base import BaseRepository


class LearningObjectiveRepository(BaseRepository[LearningObjective]):
    """Persistence for `LearningObjective`, eager-loading its Topic."""

    model = LearningObjective
    default_load_options = (selectinload(LearningObjective.topic),)