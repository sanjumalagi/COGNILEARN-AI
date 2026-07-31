"""
AI Interaction Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import joinedload

from backend.models import AIInteraction
from backend.repositories.base import BaseRepository


class AIInteractionRepository(BaseRepository[AIInteraction]):
    """Persistence for `AIInteraction`, eager-loading its TeachingContext."""

    model = AIInteraction
    default_load_options = (joinedload(AIInteraction.context),)