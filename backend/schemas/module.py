"""
Module Schemas.

Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 5 - Course APIs)
Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.4 - Module API)
"""

import uuid

from pydantic import BaseModel, Field


class ModuleCreate(BaseModel):
    """Request body for POST /modules."""

    course_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    sequence_number: int = Field(ge=1)


class ModuleUpdate(BaseModel):
    """
    Request body for PUT /modules/{id}.

    Full replace of the mutable fields; `course_id` is not
    updatable — moving a module between courses is not documented.
    """

    title: str = Field(min_length=1, max_length=255)
    sequence_number: int = Field(ge=1)


class ModuleResponse(BaseModel):
    """
    Matches the documented Module Response (module_id, course_id,
    title) plus `sequence_number`, a required, non-nullable DB field
    not shown in the doc's abbreviated example but necessary to expose
    and update.
    """

    model_config = {"from_attributes": True}

    module_id: uuid.UUID
    course_id: uuid.UUID
    title: str
    sequence_number: int


class ModuleListResponse(BaseModel):
    """Paginated list of modules."""

    items: list[ModuleResponse]
    total: int
    offset: int
    limit: int