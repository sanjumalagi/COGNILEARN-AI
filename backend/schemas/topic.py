"""
Topic Schemas.

Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 5 - Course APIs)
Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.5 - Topic API)
"""

import uuid

from pydantic import BaseModel, Field


class TopicCreate(BaseModel):
    """Request body for POST /topics."""

    module_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=5000)
    difficulty_level: int = Field(ge=1)


class TopicUpdate(BaseModel):
    """
    Request body for PUT /topics/{id}.

    Full replace of the mutable fields; `module_id` is not
    updatable — moving a topic between modules is not documented.
    """

    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=5000)
    difficulty_level: int = Field(ge=1)


class TopicResponse(BaseModel):
    """
    Matches the documented Topic Response's fields (topic_id, module_id,
    title) plus `description` (a required DB field) and
    `difficulty_level: int` — the canonical Database Schema types this
    column as INTEGER; the API Data Contracts example shows a string
    category ("Medium") with no documented integer-to-label mapping, so
    the actual stored integer is exposed rather than an invented scale.
    """

    model_config = {"from_attributes": True}

    topic_id: uuid.UUID
    module_id: uuid.UUID
    title: str
    description: str
    difficulty_level: int


class TopicListResponse(BaseModel):
    """Paginated list of topics."""

    items: list[TopicResponse]
    total: int
    offset: int
    limit: int