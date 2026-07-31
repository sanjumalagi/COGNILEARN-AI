"""
Learner Profile Repository.

Matches the documented `ILearnerRepository` interface: save(),
findById(), update(), delete() — all provided generically by
BaseRepository.

Reference: 03_SOFTWARE_DESIGN/03_Interface_Design.md (Section 6 - ILearnerRepository)
Reference: 03_SOFTWARE_DESIGN/02_Class_Design.md (Section 7 - LearnerRepository)
"""

from sqlalchemy.orm import selectinload

from backend.models import LearnerProfile
from backend.repositories.base import BaseRepository


class LearnerProfileRepository(BaseRepository[LearnerProfile]):
    """Persistence for `LearnerProfile`, eager-loading its Student and Topic Masteries."""

    model = LearnerProfile
    default_load_options = (
        selectinload(LearnerProfile.student),
        selectinload(LearnerProfile.topic_masteries),
    )