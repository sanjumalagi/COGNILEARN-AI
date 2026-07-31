"""
Topic Mastery Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import joinedload

from backend.models import TopicMastery
from backend.repositories.base import BaseRepository


class TopicMasteryRepository(BaseRepository[TopicMastery]):
    """Persistence for `TopicMastery`, eager-loading its LearnerProfile and Topic."""

    model = TopicMastery
    default_load_options = (
        joinedload(TopicMastery.learner_profile),
        joinedload(TopicMastery.topic),
    )