"""
Assessment Schemas.

Note: this entity's read schema is named `AssessmentDetail`, not
`AssessmentResponse`, to avoid colliding with the existing
`AssessmentResponse` ORM model (a student's answer to an item).

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.8 - Assessment Module)
Reference: 02_System_Architecture/02_Component_Architecture.md (Section 9 - Assessment Intelligence Component)
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AssessmentCreate(BaseModel):
    """Request body for POST /assessments (authoring; not part of the
    documented 5-endpoint attempt flow, added per Module 6's explicit
    'Assessment CRUD' scope)."""

    topic_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    assessment_type: str = Field(min_length=1, max_length=100)


class AssessmentUpdate(BaseModel):
    """Request body for PUT /assessments/{id} (full replace, matching the
    PUT convention already established for Course/Module/Topic)."""

    title: str = Field(min_length=1, max_length=255)
    assessment_type: str = Field(min_length=1, max_length=100)


class AssessmentDetail(BaseModel):
    """Assessment metadata, matching the documented DB fields."""

    model_config = {"from_attributes": True}

    assessment_id: uuid.UUID
    topic_id: uuid.UUID
    title: str
    assessment_type: str
    created_at: datetime
    item_count: int


class AssessmentListResponse(BaseModel):
    """Paginated list of assessments."""

    items: list[AssessmentDetail]
    total: int
    offset: int
    limit: int