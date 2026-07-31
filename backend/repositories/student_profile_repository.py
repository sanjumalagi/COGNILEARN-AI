"""
Student Profile Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import selectinload

from backend.models import StudentProfile
from backend.repositories.base import BaseRepository


class StudentProfileRepository(BaseRepository[StudentProfile]):
    """
    Persistence for `StudentProfile`, eager-loading the owning User and
    the LearnerProfile.

    Large, unbounded per-student collections (assessment responses,
    recommendations, learning paths, teaching contexts, progress
    history) are intentionally NOT eager-loaded here — fetch those
    through their own repository's `find_all(student_id=...)` instead.
    """

    model = StudentProfile
    default_load_options = (
        selectinload(StudentProfile.user),
        selectinload(StudentProfile.learner_profile),
    )