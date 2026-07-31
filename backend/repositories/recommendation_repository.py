"""
Recommendation Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import joinedload

from backend.models import Recommendation
from backend.repositories.base import BaseRepository


class RecommendationRepository(BaseRepository[Recommendation]):
    """Persistence for `Recommendation`, eager-loading its Student and Topic."""

    model = Recommendation
    default_load_options = (
        joinedload(Recommendation.student),
        joinedload(Recommendation.topic),
    )