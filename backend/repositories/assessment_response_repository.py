"""
Assessment Response Repository.

Reference: 03_SOFTWARE_DESIGN/01_Package_Design.md (Section 5.5 - Repository Package)
"""

from sqlalchemy.orm import joinedload

from backend.models import AssessmentResponse
from backend.repositories.base import BaseRepository


class AssessmentResponseRepository(BaseRepository[AssessmentResponse]):
    """
    Persistence for `AssessmentResponse` — the evidence consumed by the
    IRT/BKT engines. Eager-loads its Student and Item via `joinedload`
    (single-row many-to-one lookups, cheaper than a second query).
    """

    model = AssessmentResponse
    default_load_options = (
        joinedload(AssessmentResponse.student),
        joinedload(AssessmentResponse.item),
    )