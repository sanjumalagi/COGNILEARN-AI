"""
Assessment API.

Implements the documented endpoints (POST /generate, POST /submit,
GET /{id}, GET /history, GET /results) plus full CRUD
(GET /, POST /, PUT /{id}, DELETE /{id}) added per Module 6's explicit
"Assessment CRUD" scope — the documented endpoint table for this module
only enumerates the 5 student-attempt-flow operations.

Route order matters: literal paths (/generate, /submit, /history,
/results) are registered before the dynamic /{assessment_id} route, so
a request to e.g. GET /history is not swallowed by GET /{assessment_id}.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.8 - Assessment Module)
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models import Assessment, User
from backend.schemas.assessment import (
    AssessmentCreate,
    AssessmentDetail,
    AssessmentListResponse,
    AssessmentUpdate,
)
from backend.schemas.assessment_attempt import (
    AssessmentHistoryResponse,
    AssessmentResultResponse,
    GenerateAssessmentRequest,
    GeneratedAssessmentResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from backend.services.assessment_attempt_service import AssessmentAttemptService
from backend.services.assessment_service import AssessmentService

router = APIRouter()


def _to_detail(assessment: Assessment) -> AssessmentDetail:
    return AssessmentDetail(
        assessment_id=assessment.assessment_id,
        topic_id=assessment.topic_id,
        title=assessment.title,
        assessment_type=assessment.assessment_type,
        created_at=assessment.created_at,
        item_count=len(assessment.items),
    )


# ----------------------------------------------------------------------
# Authoring / CRUD (added per Module 6 scope, beyond the 5 documented routes)
# ----------------------------------------------------------------------


@router.get("/", response_model=AssessmentListResponse, summary="List assessments")
def list_assessments(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    topic_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentListResponse:
    page = AssessmentService(db).list_assessments(offset=offset, limit=limit, topic_id=topic_id)
    return AssessmentListResponse(
        items=[_to_detail(a) for a in page.items], total=page.total, offset=page.offset, limit=page.limit
    )


@router.post(
    "/",
    response_model=AssessmentDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create an assessment",
)
def create_assessment(
    payload: AssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentDetail:
    assessment = AssessmentService(db).create_assessment(actor=current_user, payload=payload)
    db.commit()
    return _to_detail(assessment)


@router.put("/{assessment_id}", response_model=AssessmentDetail, summary="Replace an assessment")
def update_assessment(
    assessment_id: uuid.UUID,
    payload: AssessmentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentDetail:
    assessment = AssessmentService(db).update_assessment(
        actor=current_user, assessment_id=assessment_id, payload=payload
    )
    db.commit()
    return _to_detail(assessment)


@router.delete(
    "/{assessment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an assessment (Admin only)",
)
def delete_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    AssessmentService(db).delete_assessment(actor=current_user, assessment_id=assessment_id)
    db.commit()


# ----------------------------------------------------------------------
# Documented student attempt flow
# ----------------------------------------------------------------------


@router.post(
    "/generate", response_model=GeneratedAssessmentResponse, summary="Start an assessment attempt"
)
def generate_assessment(
    payload: GenerateAssessmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GeneratedAssessmentResponse:
    return AssessmentAttemptService(db).start_assessment(actor=current_user, payload=payload)


@router.post(
    "/submit", response_model=SubmitAnswerResponse, summary="Submit an answer for auto-evaluation"
)
def submit_answer(
    payload: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubmitAnswerResponse:
    result = AssessmentAttemptService(db).submit_assessment(actor=current_user, payload=payload)
    db.commit()
    return result


@router.get(
    "/history",
    response_model=AssessmentHistoryResponse,
    summary="Get the current student's response history",
)
def get_history(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentHistoryResponse:
    page = AssessmentAttemptService(db).get_history(actor=current_user, offset=offset, limit=limit)
    return AssessmentHistoryResponse(items=page.items, total=page.total, offset=page.offset, limit=page.limit)


@router.get(
    "/results",
    response_model=AssessmentResultResponse,
    summary="Get the current student's result for an assessment",
)
def get_results(
    assessment_id: uuid.UUID = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentResultResponse:
    return AssessmentAttemptService(db).get_results(actor=current_user, assessment_id=assessment_id)


@router.get("/{assessment_id}", response_model=AssessmentDetail, summary="Get an assessment by ID")
def get_assessment(
    assessment_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentDetail:
    assessment = AssessmentService(db).get_assessment(assessment_id=assessment_id)
    return _to_detail(assessment)