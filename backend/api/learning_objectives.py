"""
Learning Objective ("Learning Outcome") API.

Implements exactly the documented Learning Outcome API operations:
Create, Update, View, List — at `/api/v1/learning-outcomes`. No Delete
operation is documented for this resource, so none is implemented here.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.6 - Learning Outcome API)
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas.learning_objective import (
    LearningObjectiveCreate,
    LearningObjectiveListResponse,
    LearningObjectiveResponse,
    LearningObjectiveUpdate,
)
from backend.services.learning_objective_service import LearningObjectiveService

router = APIRouter()


@router.get("/", response_model=LearningObjectiveListResponse, summary="List learning outcomes")
def list_learning_objectives(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    topic_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningObjectiveListResponse:
    page = LearningObjectiveService(db).list_learning_objectives(
        offset=offset, limit=limit, topic_id=topic_id
    )
    return LearningObjectiveListResponse(
        items=page.items, total=page.total, offset=page.offset, limit=page.limit
    )


@router.post(
    "/",
    response_model=LearningObjectiveResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a learning outcome",
)
def create_learning_objective(
    payload: LearningObjectiveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningObjectiveResponse:
    objective = LearningObjectiveService(db).create_learning_objective(actor=current_user, payload=payload)
    db.commit()
    return objective


@router.get(
    "/{objective_id}", response_model=LearningObjectiveResponse, summary="View a learning outcome by ID"
)
def get_learning_objective(
    objective_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningObjectiveResponse:
    return LearningObjectiveService(db).get_learning_objective(objective_id=objective_id)


@router.put(
    "/{objective_id}", response_model=LearningObjectiveResponse, summary="Replace a learning outcome"
)
def update_learning_objective(
    objective_id: uuid.UUID,
    payload: LearningObjectiveUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LearningObjectiveResponse:
    objective = LearningObjectiveService(db).update_learning_objective(
        actor=current_user, objective_id=objective_id, payload=payload
    )
    db.commit()
    return objective