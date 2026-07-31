"""
Assessment Attempt Schemas.

Covers the student-facing attempt flow: POST /assessments/generate,
POST /assessments/submit, GET /assessments/results,
GET /assessments/history.

`ability_theta` and `mastery` on `AssessmentResultResponse` are
documented fields, but computing them requires the IRT/BKT engines
built in Module 7 (Learning Intelligence), which this module explicitly
excludes. They are included as nullable and left `None` here rather
than populated with fabricated values.

Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 6 - Assessment APIs)
Reference: 02_System_Architecture/02_Component_Architecture.md (Section 9 - Assessment Intelligence Component)
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from backend.schemas.assessment_item import AssessmentItemPublic


class GenerateAssessmentRequest(BaseModel):
    """
    Request body for POST /assessments/generate.

    Matches the documented Start Assessment Request (student_id,
    topic_id). `student_id` must match the authenticated user — enforced
    in the service layer, not accepted as an arbitrary target, so one
    student cannot generate an attempt "as" another.
    """

    student_id: uuid.UUID
    topic_id: uuid.UUID


class GeneratedAssessmentResponse(BaseModel):
    """Response for POST /assessments/generate: the selected Assessment's
    sanitized item set (no answer key) for the student to attempt."""

    assessment_id: uuid.UUID
    topic_id: uuid.UUID
    title: str
    items: list[AssessmentItemPublic]


class SubmitAnswerRequest(BaseModel):
    """Matches the documented Submit Answer Request exactly: question_id,
    selected_answer, response_time."""

    question_id: uuid.UUID
    selected_answer: str = Field(min_length=1, max_length=2000)
    response_time: int = Field(ge=0)


class SubmitAnswerResponse(BaseModel):
    """
    Immediate auto-evaluation feedback for one submitted answer.

    Not itself named in the API Data Contracts document (which only
    shows the request), but returning evaluation feedback is the
    documented "Automatic Evaluation" / "Response validation"
    responsibility of this component.
    """

    response_id: uuid.UUID
    is_correct: bool
    correct_answer: str
    explanation: str


class AssessmentResultResponse(BaseModel):
    """
    Matches the documented Assessment Result Response fields (score,
    total, percentage, ability_theta, mastery). `ability_theta` and
    `mastery` are always `None` in this module — see module docstring.
    """

    assessment_id: uuid.UUID
    score: int
    total: int
    percentage: float
    ability_theta: float | None = None
    mastery: float | None = None


class AssessmentHistoryItem(BaseModel):
    """One past response, for GET /assessments/history."""

    model_config = {"from_attributes": True}

    response_id: uuid.UUID
    item_id: uuid.UUID
    selected_answer: str
    is_correct: bool
    response_time: int
    submitted_at: datetime


class AssessmentHistoryResponse(BaseModel):
    """Paginated response history for the current student."""

    items: list[AssessmentHistoryItem]
    total: int
    offset: int
    limit: int