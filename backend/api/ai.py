"""
AI Tutor API.

Implements the five documented AI Module endpoints:
POST /explain, POST /hint, POST /feedback, POST /summary, POST /chat
at `/api/v1/ai`.

Each endpoint delegates to `AIService`, which handles the full
documented AI Request Lifecycle (context building, prompt construction,
provider invocation, response parsing/validation, persistence).

The API layer never calls the AI provider directly.

Reference: 02_System_Architecture/05_API_Architecture.md (Section 23.11 - AI Module)
Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 10 - AI Tutor APIs)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.dependencies import get_current_user
from backend.database import get_db
from backend.models import User
from backend.schemas.ai import AITutorRequest, AITutorResponse
from backend.services.ai.ai_service import AIService

router = APIRouter()


@router.post(
    "/explain",
    response_model=AITutorResponse,
    summary="Get an AI-generated explanation for a topic",
)
def explain_topic(
    body: AITutorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AITutorResponse:
    result = AIService(db).explain(actor=current_user, topic_id=body.topic_id, user_message=body.message)
    db.commit()
    return AITutorResponse(response=result.response, teaching_strategy=result.teaching_strategy, generated_by=result.generated_by)


@router.post(
    "/hint",
    response_model=AITutorResponse,
    summary="Get an AI-generated hint for a question",
)
def get_hint(
    body: AITutorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AITutorResponse:
    result = AIService(db).hint(actor=current_user, topic_id=body.topic_id, user_message=body.message)
    db.commit()
    return AITutorResponse(response=result.response, teaching_strategy=result.teaching_strategy, generated_by=result.generated_by)


@router.post(
    "/feedback",
    response_model=AITutorResponse,
    summary="Get AI-generated feedback on assessment performance",
)
def get_feedback(
    body: AITutorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AITutorResponse:
    result = AIService(db).feedback(actor=current_user, topic_id=body.topic_id, user_message=body.message)
    db.commit()
    return AITutorResponse(response=result.response, teaching_strategy=result.teaching_strategy, generated_by=result.generated_by)


@router.post(
    "/summary",
    response_model=AITutorResponse,
    summary="Get an AI-generated summary for a topic",
)
def get_summary(
    body: AITutorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AITutorResponse:
    result = AIService(db).summary(actor=current_user, topic_id=body.topic_id, user_message=body.message)
    db.commit()
    return AITutorResponse(response=result.response, teaching_strategy=result.teaching_strategy, generated_by=result.generated_by)


@router.post(
    "/chat",
    response_model=AITutorResponse,
    summary="Chat with the AI tutor about a topic",
)
def chat_with_tutor(
    body: AITutorRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AITutorResponse:
    result = AIService(db).chat(actor=current_user, topic_id=body.topic_id, user_message=body.message)
    db.commit()
    return AITutorResponse(response=result.response, teaching_strategy=result.teaching_strategy, generated_by=result.generated_by)
