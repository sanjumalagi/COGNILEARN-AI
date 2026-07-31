"""
Learner Schemas.

Matches the documented response shapes from
05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md Section 7 (Learner
Profile Response: student_id, ability_theta, overall_mastery,
completed_topics, current_topic; Topic Mastery Response: topic,
mastery, status) and the GET /learner/* endpoints documented in
02_System_Architecture/05_API_Architecture.md Section 23.9.

The Topic Mastery Response example uses the illustrative label "Needs
Practice", which does not match either of the two concrete,
threshold-based classification schemes actually defined in the
Algorithm Design documents (BKT's 3-level status, Mastery Engine's
5-level scale). `status` here uses the Mastery Engine's 5-level scale
(backend.algorithms.mastery_engine.MasteryLevel) as the authoritative,
precisely-defined classification.

Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 7 - Learner Profile APIs)
Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.9 - Learner Module)
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

from backend.algorithms.irt.estimator import AbilityCategory
from backend.algorithms.mastery_engine import MasteryLevel


class LearnerProfileDetail(BaseModel):
    """Response for GET /learner/profile."""

    student_id: uuid.UUID
    ability_theta: float
    overall_mastery: float
    completed_topics: int
    current_topic: str | None


class AbilityDetail(BaseModel):
    """Response for GET /learner/ability — the full documented IRT Engine output."""

    ability_theta: float
    ability_category: AbilityCategory
    confidence_score: float
    difficulty_recommendation: float


class TopicMasteryDetail(BaseModel):
    """One item in the response for GET /learner/mastery."""

    topic_id: uuid.UUID
    topic: str
    mastery: float
    status: MasteryLevel
    is_weak: bool
    is_strong: bool


class TopicMasteryListResponse(BaseModel):
    """Response for GET /learner/mastery."""

    items: list[TopicMasteryDetail]
    total: int
    offset: int
    limit: int


class ProgressEntry(BaseModel):
    """One entry in the response for GET /learner/progress and GET /learner/history."""

    model_config = {"from_attributes": True}

    progress_id: uuid.UUID
    topic_id: uuid.UUID
    mastery_score: float
    recorded_at: datetime


class ProgressListResponse(BaseModel):
    """Paginated progress log."""

    items: list[ProgressEntry]
    total: int
    offset: int
    limit: int