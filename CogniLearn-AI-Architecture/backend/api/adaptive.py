"""
Adaptive Learning API.

Implements exactly the documented endpoints: GET /recommendations,
GET /learning-path, GET /next-learning-outcome, GET /revision-plan —
at `/api/v1/adaptive`.

`course_id` is accepted as an optional query parameter on
/learning-path and /next-learning-outcome (not shown in the
documented endpoint table, which lists no parameters) because
determining the "next unencountered topic in curriculum order"
requires knowing which course's structure to consult — there is no
course-enrollment concept in the finalized schema to infer this
automatically. Without it, both endpoints still work, limited to the
student's already-encountered topics (no "next new topic" step).

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.10 - Adaptive Learning Module)
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas.adaptive import (
    AdaptiveDecisionResponse,
    LearningPathListResponse,
    RecommendationListResponse,
)
from backend.services.adaptive_decision_service import AdaptiveDecisionService
from backend.services.learning_path_service import LearningPathService
from backend.services.recommendation_service import RecommendationService

router = APIRouter()


@router.get(
    "/recommendations",
    response_model=RecommendationListResponse,
    summary="Get the current learner's recommendations",
)
def get_recommendations(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> RecommendationListResponse:
    items = RecommendationService(db).refresh_and_get_recommendations(actor=current_user)
    db.commit()
    return RecommendationListResponse(items=items, total=len(items))


@router.get(
    "/learning-path",
    response_model=LearningPathListResponse,
    summary="Get the current learner's personalized learning path",
)
def get_learning_path(
    course_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningPathListResponse:
    items = LearningPathService(db).refresh_and_get_path(actor=current_user, course_id=course_id)
    db.commit()
    return LearningPathListResponse(items=items, total=len(items))


@router.get(
    "/next-learning-outcome",
    response_model=AdaptiveDecisionResponse,
    summary="Get the current learner's next recommended action",
)
def get_next_learning_outcome(
    course_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AdaptiveDecisionResponse:
    decision = AdaptiveDecisionService(db).get_next_decision(actor=current_user, course_id=course_id)
    db.commit()
    return AdaptiveDecisionResponse(
        next_action=decision.next_action,
        topic_id=decision.topic_id,
        difficulty=decision.difficulty,
        reason=decision.reason,
        ai_support=decision.ai_support,
        assessment_required=decision.assessment_required,
        learning_objective=decision.learning_objective,
    )


@router.get(
    "/revision-plan",
    response_model=RecommendationListResponse,
    summary="Get the current learner's revision plan (weak topics only)",
)
def get_revision_plan(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> RecommendationListResponse:
    items = RecommendationService(db).get_revision_recommendations(actor=current_user)
    db.commit()
    return RecommendationListResponse(items=items, total=len(items))