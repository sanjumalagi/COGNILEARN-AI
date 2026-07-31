"""
Learning Objective ("Learning Outcome") Schemas.

The database schema (05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md)
names this entity `Learning Objective`; architecture-level documents
call the same concept "Learning Outcome" and route it at
`/api/v1/learning-outcomes`. Both names refer to the one
`learning_objectives` table implemented in Module 1 — no separate
entity or table exists for "Learning Outcome".

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.6 - Learning Outcome API)
Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Learning Objective)
"""

import uuid

from pydantic import BaseModel, Field


class LearningObjectiveCreate(BaseModel):
    """Request body for POST /learning-outcomes."""

    topic_id: uuid.UUID
    description: str = Field(min_length=1, max_length=5000)


class LearningObjectiveUpdate(BaseModel):
    """
    Request body for PUT /learning-outcomes/{id}.

    `topic_id` is not updatable — moving a learning objective between
    topics is not documented.
    """

    description: str = Field(min_length=1, max_length=5000)


class LearningObjectiveResponse(BaseModel):
    """Response shape inferred from the DB fields (no explicit JSON
    example is given in the API Data Contracts document)."""

    model_config = {"from_attributes": True}

    objective_id: uuid.UUID
    topic_id: uuid.UUID
    description: str


class LearningObjectiveListResponse(BaseModel):
    """Paginated list of learning objectives."""

    items: list[LearningObjectiveResponse]
    total: int
    offset: int
    limit: int