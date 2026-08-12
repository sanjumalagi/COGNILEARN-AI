"""
Adaptive Intelligence Schemas.

Matches the four documented GET /adaptive/* endpoints and the decision
output shape shown in the Adaptive Decision Engine design document's
Section 16 example (next_action, topic_id, difficulty, reason,
ai_support, assessment_required, learning_objective).

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.10 - Adaptive Learning Module)
Reference: 04_ALGORITHM_DESIGN/06_Adaptive_Decision_Engine.md (Section 16)
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.algorithms.adaptive_engine.adaptive_decision_engine import Difficulty, NextAction
from backend.algorithms.adaptive_engine.learning_path_engine import PathStepStatus


class RecommendationDetail(BaseModel):
    """One recommendation, for GET /adaptive/recommendations and GET /adaptive/revision-plan."""

    model_config = {"from_attributes": True}

    recommendation_id: uuid.UUID
    topic_id: uuid.UUID
    recommendation_type: str
    priority: int
    generated_at: datetime


class RecommendationListResponse(BaseModel):
    """Response for GET /adaptive/recommendations and GET /adaptive/revision-plan."""

    items: list[RecommendationDetail]
    total: int


class LearningPathStepDetail(BaseModel):
    """One step, for GET /adaptive/learning-path."""

    model_config = {"from_attributes": True}

    path_id: uuid.UUID
    topic_id: uuid.UUID
    sequence_order: int
    status: PathStepStatus


class LearningPathListResponse(BaseModel):
    """Response for GET /adaptive/learning-path."""

    items: list[LearningPathStepDetail]
    total: int


class AdaptiveDecisionResponse(BaseModel):
    """Response for GET /adaptive/next-learning-outcome — matches the
    documented decision output shape exactly."""

    next_action: NextAction
    topic_id: uuid.UUID | None
    difficulty: Difficulty
    reason: str
    ai_support: bool
    assessment_required: bool
    learning_objective: str | None