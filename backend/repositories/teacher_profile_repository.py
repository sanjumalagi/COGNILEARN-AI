"""
Teacher Profile Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import selectinload

from backend.models import TeacherProfile
from backend.repositories.base import BaseRepository


class TeacherProfileRepository(BaseRepository[TeacherProfile]):
    """Persistence for `TeacherProfile`, eager-loading the owning User."""

    model = TeacherProfile
    default_load_options = (selectinload(TeacherProfile.user),)