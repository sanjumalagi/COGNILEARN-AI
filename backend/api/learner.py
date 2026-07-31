"""
Learner API.

Implements exactly the documented endpoints: GET /profile, GET /mastery,
GET /ability, GET /progress, GET /history — at `/api/v1/learner`.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.9 - Learner Module)
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas.learner import (
    AbilityDetail,
    LearnerProfileDetail,
    ProgressListResponse,
    TopicMasteryListResponse,
)
from backend.services.learner_service import LearnerService

router = APIRouter()


@router.get("/profile", response_model=LearnerProfileDetail, summary="Get the current learner's profile")
def get_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> LearnerProfileDetail:
    return LearnerService(db).get_profile(actor=current_user)


@router.get(
    "/mastery",
    response_model=TopicMasteryListResponse,
    summary="List the current learner's topic mastery",
)
def get_mastery(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TopicMasteryListResponse:
    page = LearnerService(db).get_mastery(actor=current_user, offset=offset, limit=limit)
    return TopicMasteryListResponse(
        items=page.items, total=page.total, offset=page.offset, limit=page.limit
    )


@router.get("/ability", response_model=AbilityDetail, summary="Get the current learner's ability estimate")
def get_ability(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> AbilityDetail:
    return LearnerService(db).get_ability(actor=current_user)


@router.get(
    "/progress", response_model=ProgressListResponse, summary="Get the current learner's progress log"
)
def get_progress(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    topic_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProgressListResponse:
    page = LearnerService(db).get_progress(
        actor=current_user, offset=offset, limit=limit, topic_id=topic_id
    )
    return ProgressListResponse(items=page.items, total=page.total, offset=page.offset, limit=page.limit)


@router.get(
    "/history",
    response_model=ProgressListResponse,
    summary="Get the current learner's full progress history",
)
def get_history(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProgressListResponse:
    page = LearnerService(db).get_history(actor=current_user, offset=offset, limit=limit)
    return ProgressListResponse(items=page.items, total=page.total, offset=page.offset, limit=page.limit)