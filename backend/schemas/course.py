"""
Course Schemas.

Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 5 - Course APIs)
Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.3 - Course Module)
"""

import uuid

from pydantic import BaseModel, Field


class CourseCreate(BaseModel):
    """Request body for POST /courses."""

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=5000)


class CourseUpdate(BaseModel):
    """
    Request body for PUT /courses/{id}.

    PUT is a full replace (per the documented HTTP method), so both
    fields are required — unlike the PATCH-based partial updates used
    by the User Module.
    """

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=5000)


class CourseResponse(BaseModel):
    """
    Matches the documented Course Response exactly: course_id, title,
    description, modules (a count of the course's modules, not a
    nested list — per the documented example `"modules": 6`).
    """

    model_config = {"from_attributes": True}

    course_id: uuid.UUID
    title: str
    description: str
    modules: int


class CourseListResponse(BaseModel):
    """Paginated list of courses."""

    items: list[CourseResponse]
    total: int
    offset: int
    limit: int