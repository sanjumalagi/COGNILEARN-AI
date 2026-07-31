"""
Assessment Item Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import selectinload

from backend.models import AssessmentItem
from backend.repositories.base import BaseRepository


class AssessmentItemRepository(BaseRepository[AssessmentItem]):
    """Persistence for `AssessmentItem`, eager-loading its owning Assessment."""

    model = AssessmentItem
    default_load_options = (selectinload(AssessmentItem.assessment),)