"""
User Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
Reference: 03_SOFTWARE_DESIGN/05_Sequence_Design.md (Section 2 - UserRepository.findByEmail())
"""

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models import User
from backend.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Persistence for `User`, eager-loading its Student/Teacher profile."""

    model = User
    default_load_options = (
        selectinload(User.student_profile),
        selectinload(User.teacher_profile),
    )

    def find_by_email(self, email: str) -> User | None:
        """
        Returns the User with the given email, or None.

        Documented explicitly in the Authentication sequence
        (`UserRepository.findByEmail()`), used by AuthService to look up
        a user during login.
        """
        stmt = select(User)
        for option in self.default_load_options:
            stmt = stmt.options(option)
        stmt = stmt.where(User.email == email)
        return self.db.execute(stmt).unique().scalar_one_or_none()