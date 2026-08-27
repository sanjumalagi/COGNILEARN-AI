"""
Topic API.

Implements exactly the documented endpoints for the Topic Module:
GET /topics, POST /topics, PUT /topics/{id}, DELETE /topics/{id}.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.5 - Topic API)
"""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models import Topic, User
from backend.schemas.topic import TopicCreate, TopicListResponse, TopicResponse, TopicUpdate
from backend.services.topic_service import TopicService

router = APIRouter()


def _to_response(topic: Topic) -> TopicResponse:
    return TopicResponse(
        topic_id=topic.topic_id,
        module_id=topic.module_id,
        title=topic.title,
        description=topic.description,
        difficulty_level=topic.difficulty_level,
    )


@router.get("/", response_model=TopicListResponse, summary="List topics")
def list_topics(
    module_id: uuid.UUID | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TopicListResponse:
    page = TopicService(db).list_topics(offset=offset, limit=limit, module_id=module_id)
    return TopicListResponse(
        items=[_to_response(t) for t in page.items], total=page.total, offset=page.offset, limit=page.limit
    )


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED, summary="Create a topic")
def create_topic(
    payload: TopicCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TopicResponse:
    topic = TopicService(db).create_topic(actor=current_user, payload=payload)
    db.commit()
    return _to_response(topic)


@router.put("/{topic_id}", response_model=TopicResponse, summary="Update a topic")
def update_topic(
    topic_id: uuid.UUID,
    payload: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TopicResponse:
    topic = TopicService(db).update_topic(actor=current_user, topic_id=topic_id, payload=payload)
    db.commit()
    return _to_response(topic)


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a topic")
def delete_topic(
    topic_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    TopicService(db).delete_topic(actor=current_user, topic_id=topic_id)
    db.commit()
