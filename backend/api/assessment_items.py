"""
Assessment Item API (Question Bank).

Not an explicitly named base path in the API Architecture document
(which only enumerates the Assessment Module's 5 attempt-flow routes);
added at `/api/v1/assessment-items` per Module 6's explicit "Assessment
Item CRUD" scope, using the same REST conventions established for
Course/Module/Topic in Module 5.

All endpoints are Teacher/Admin only — full item detail includes the
answer key, which must never reach students outside the sanitized
attempt flow (POST /assessments/generate).

Reference: 02_System_Architecture/02_Component_Architecture.md (Section 9 - Assessment Intelligence Component)
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas.assessment_item import (
    AssessmentItemCreate,
    AssessmentItemDetail,
    AssessmentItemListResponse,
    AssessmentItemUpdate,
)
from backend.services.assessment_item_service import AssessmentItemService

router = APIRouter()


@router.get(
    "/", response_model=AssessmentItemListResponse, summary="List assessment items (Teacher/Admin only)"
)
def list_items(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    assessment_id: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentItemListResponse:
    page = AssessmentItemService(db).list_items(
        actor=current_user, offset=offset, limit=limit, assessment_id=assessment_id
    )
    return AssessmentItemListResponse(
        items=page.items, total=page.total, offset=page.offset, limit=page.limit
    )


@router.post(
    "/",
    response_model=AssessmentItemDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create an assessment item (Teacher/Admin only)",
)
def create_item(
    payload: AssessmentItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentItemDetail:
    item = AssessmentItemService(db).create_item(actor=current_user, payload=payload)
    db.commit()
    return item


@router.get(
    "/{item_id}",
    response_model=AssessmentItemDetail,
    summary="Get an assessment item by ID (Teacher/Admin only)",
)
def get_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentItemDetail:
    return AssessmentItemService(db).get_item(actor=current_user, item_id=item_id)


@router.put(
    "/{item_id}",
    response_model=AssessmentItemDetail,
    summary="Replace an assessment item (Teacher/Admin only)",
)
def update_item(
    item_id: uuid.UUID,
    payload: AssessmentItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssessmentItemDetail:
    item = AssessmentItemService(db).update_item(actor=current_user, item_id=item_id, payload=payload)
    db.commit()
    return item


@router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an assessment item (Admin only)",
)
def delete_item(
    item_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    AssessmentItemService(db).delete_item(actor=current_user, item_id=item_id)
    db.commit()