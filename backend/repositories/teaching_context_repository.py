"""
Teaching Context Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import joinedload, selectinload

from backend.models import TeachingContext
from backend.repositories.base import BaseRepository


class TeachingContextRepository(BaseRepository[TeachingContext]):
    """
    Persistence for `TeachingContext`, eager-loading its Student, Topic,
    and AI Interaction history.
    """

    model = TeachingContext
    default_load_options = (
        joinedload(TeachingContext.student),
        joinedload(TeachingContext.topic),
        selectinload(TeachingContext.ai_interactions),
    )