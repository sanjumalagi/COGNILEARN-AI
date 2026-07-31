"""
Course Repository.

Matches the documented `ICourseRepository` interface: save(), findAll(),
findById() — all provided generically by BaseRepository (create/save,
find_all, find_by_id).

Reference: 03_SOFTWARE_DESIGN/03_Interface_Design.md (Section 6 - ICourseRepository)
"""

from sqlalchemy.orm import selectinload

from backend.models import Course
from backend.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    """Persistence for `Course`, eager-loading its Modules."""

    model = Course
    default_load_options = (selectinload(Course.modules),)