"""
AI Tutor Schemas.

Request/response models for the five documented AI Module endpoints
(POST /ai/explain, /ai/hint, /ai/feedback, /ai/summary, /ai/chat).
Matches the documented API Data Contracts (Section 10 - AI Tutor APIs).

Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 10)
Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.11 - AI Module)
"""

import uuid

from pydantic import BaseModel, Field


class AITutorRequest(BaseModel):
    """Request body shared by all five AI tutor endpoints."""

    topic_id: uuid.UUID = Field(..., description="The topic the learner is asking about.")
    message: str = Field(
        ..., min_length=1, max_length=2000,
        description="The learner's question or request.",
    )


class AITutorResponse(BaseModel):
    """Response body shared by all five AI tutor endpoints."""

    response: str = Field(..., description="The AI-generated educational content.")
    teaching_strategy: str = Field(..., description="The teaching strategy used for this response.")
    generated_by: str = Field(..., description="The AI provider that generated the response.")
