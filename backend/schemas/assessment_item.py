"""
Assessment Item Schemas.

Two response shapes are deliberately distinct:
- `AssessmentItemDetail` — full detail including `correct_answer` and
  `explanation`, for content authors (Teacher/Admin) doing Assessment
  Item CRUD / Question Bank management.
- `AssessmentItemPublic` — sanitized, WITHOUT `correct_answer` or
  `explanation`, returned to a student during an active attempt
  (POST /assessments/generate) so the answer key never leaks.

Note: the documented AssessmentItem Response example includes an
"options" field (multiple-choice answer options). The finalized
Database Schema (Module 1, approved) has no such column on
`assessment_items` — only question_text, difficulty, bloom_level,
correct_answer, explanation. No "options" field is exposed here since
there is no data source for it; adding one would mean inventing an
undocumented schema change outside this module's scope.

Reference: 05_DATA_AND_MODEL_DESIGN/01_DATABASE_SCHEMA.md (Section 5 - Assessment Item)
Reference: 05_DATA_AND_MODEL_DESIGN/04_ASSESSMENT_ITEM_MODEL.md (Section 8 - Bloom Levels)
"""

import uuid

from pydantic import BaseModel, Field, field_validator

# The six documented Bloom's Taxonomy levels (04_ASSESSMENT_ITEM_MODEL.md Section 8).
BLOOM_LEVELS = ("Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create")


def _validate_bloom_level(value: str) -> str:
    if value not in BLOOM_LEVELS:
        raise ValueError(f"bloom_level must be one of {BLOOM_LEVELS}.")
    return value


class AssessmentItemCreate(BaseModel):
    """Request body for POST /assessment-items (Teacher/Admin only)."""

    assessment_id: uuid.UUID
    question_text: str = Field(min_length=1, max_length=5000)
    # A normalized 0.0-1.0 difficulty convention (matching the values
    # used throughout this project's own test data); not an explicit
    # documented bound, applied as reasonable input validation.
    difficulty: float = Field(ge=0.0, le=1.0)
    bloom_level: str
    correct_answer: str = Field(min_length=1, max_length=2000)
    explanation: str = Field(min_length=1, max_length=5000)

    @field_validator("bloom_level")
    @classmethod
    def _check_bloom_level(cls, value: str) -> str:
        return _validate_bloom_level(value)


class AssessmentItemUpdate(BaseModel):
    """Request body for PUT /assessment-items/{id} (full replace);
    `assessment_id` is not updatable — not documented."""

    question_text: str = Field(min_length=1, max_length=5000)
    difficulty: float = Field(ge=0.0, le=1.0)
    bloom_level: str
    correct_answer: str = Field(min_length=1, max_length=2000)
    explanation: str = Field(min_length=1, max_length=5000)

    @field_validator("bloom_level")
    @classmethod
    def _check_bloom_level(cls, value: str) -> str:
        return _validate_bloom_level(value)


class AssessmentItemDetail(BaseModel):
    """Full item detail, including the answer key — Teacher/Admin only."""

    model_config = {"from_attributes": True}

    item_id: uuid.UUID
    assessment_id: uuid.UUID
    question_text: str
    difficulty: float
    bloom_level: str
    correct_answer: str
    explanation: str


class AssessmentItemListResponse(BaseModel):
    """Paginated list of assessment items (Teacher/Admin only)."""

    items: list[AssessmentItemDetail]
    total: int
    offset: int
    limit: int


class AssessmentItemPublic(BaseModel):
    """
    Sanitized item shown to a student during an active attempt — no
    `correct_answer` or `explanation`, so the answer key never leaks
    before submission.
    """

    model_config = {"from_attributes": True}

    item_id: uuid.UUID
    question_text: str
    difficulty: float
    bloom_level: str