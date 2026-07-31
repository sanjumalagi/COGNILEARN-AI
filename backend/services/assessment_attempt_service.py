"""
Assessment Attempt Service.

Implements the remaining documented Public Services from the Assessment
Intelligence Component: start_assessment(), submit_assessment(),
evaluate_assessment(), calculate_score(), store_results(),
get_assessment_history() — the student attempt flow behind
POST /assessments/generate, POST /assessments/submit,
GET /assessments/results, GET /assessments/history.

Restricted to the Student role only, per the documented Permission
Matrix ("Attempt Assessment: Student only").

"Assessment Generation" here means selecting the most recently created
Assessment already authored (via AssessmentService/AssessmentItemService)
for the given Topic, and returning its item set. No IRT-based or
otherwise adaptive item selection is performed — that belongs to
Learning/Adaptive Intelligence (Modules 7-8), explicitly out of scope
for this module.

Reference: 02_System_Architecture/02_Component_Architecture.md (Section 9 - Assessment Intelligence Component)
Reference: 02_System_Architecture/06_Security_Architecture.md (Section 10 - Permission Matrix)
Reference: 05_DATA_AND_MODEL_DESIGN/06_API_DATA_CONTRACTS.md (Section 6 - Assessment APIs)
"""

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.exceptions import AuthorizationError, NotFoundError, ValidationFailedError
from backend.core.logging import get_logger
from backend.models import AssessmentResponse, StudentProfile, User, UserRole
from backend.repositories import (
    AssessmentItemRepository,
    AssessmentRepository,
    AssessmentResponseRepository,
    Page,
)
from backend.schemas.assessment_attempt import (
    AssessmentHistoryItem,
    AssessmentResultResponse,
    GenerateAssessmentRequest,
    GeneratedAssessmentResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from backend.schemas.assessment_item import AssessmentItemPublic

logger = get_logger(__name__)


class AssessmentAttemptService:
    """Business logic for a student's assessment attempt: generate, submit, evaluate, score, history."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.assessments = AssessmentRepository(db)
        self.items = AssessmentItemRepository(db)
        self.responses = AssessmentResponseRepository(db)

    def start_assessment(
        self, *, actor: User, payload: GenerateAssessmentRequest
    ) -> GeneratedAssessmentResponse:
        """Selects an Assessment for the given topic and returns its
        sanitized items (documented `start_assessment()`)."""
        student = self._require_student(actor, expected_student_id=payload.student_id)

        candidates = self.assessments.find_by_topic(payload.topic_id, offset=0, limit=1)
        if candidates.total == 0:
            raise NotFoundError(f"No assessment is configured for topic id={payload.topic_id!r} yet.")
        assessment = candidates.items[0]

        item_page = self.items.find_all(offset=0, limit=200, assessment_id=assessment.assessment_id)
        logger.info(
            "Assessment started | assessment_id=%s | student_id=%s",
            assessment.assessment_id,
            student.student_id,
        )
        return GeneratedAssessmentResponse(
            assessment_id=assessment.assessment_id,
            topic_id=assessment.topic_id,
            title=assessment.title,
            items=[AssessmentItemPublic.model_validate(item) for item in item_page.items],
        )

    def submit_assessment(self, *, actor: User, payload: SubmitAnswerRequest) -> SubmitAnswerResponse:
        """Records and auto-evaluates one submitted answer (documented
        `submit_assessment()` + `evaluate_assessment()`)."""
        student = self._require_student(actor)

        item = self.items.find_by_id(payload.question_id)
        if item is None:
            raise NotFoundError(f"Assessment item with id={payload.question_id!r} was not found.")

        is_correct = self._normalize(payload.selected_answer) == self._normalize(item.correct_answer)

        response = self.responses.create(
            student_id=student.student_id,
            item_id=item.item_id,
            selected_answer=payload.selected_answer,
            is_correct=is_correct,
            response_time=payload.response_time,
        )
        logger.info(
            "Answer submitted | response_id=%s | student_id=%s | is_correct=%s",
            response.response_id,
            student.student_id,
            is_correct,
        )
        return SubmitAnswerResponse(
            response_id=response.response_id,
            is_correct=is_correct,
            correct_answer=item.correct_answer,
            explanation=item.explanation,
        )

    def get_results(self, *, actor: User, assessment_id: uuid.UUID) -> AssessmentResultResponse:
        """Computes score/total/percentage for the student's latest
        response to each item in the assessment (documented
        `calculate_score()` / `store_results()`)."""
        student = self._require_student(actor)

        assessment = self.assessments.find_by_id(assessment_id)
        if assessment is None:
            raise NotFoundError(f"Assessment with id={assessment_id!r} was not found.")

        item_page = self.items.find_all(offset=0, limit=200, assessment_id=assessment_id)
        total = len(item_page.items)
        item_ids = {item.item_id for item in item_page.items}

        score = self._calculate_score(student_id=student.student_id, item_ids=item_ids)
        percentage = round((score / total) * 100, 2) if total > 0 else 0.0

        return AssessmentResultResponse(
            assessment_id=assessment_id, score=score, total=total, percentage=percentage
        )

    def get_history(self, *, actor: User, offset: int = 0, limit: int = 50) -> Page[AssessmentHistoryItem]:
        """Returns the student's own response history (documented
        `get_assessment_history()`)."""
        student = self._require_student(actor)
        page = self.responses.find_all(
            offset=offset,
            limit=limit,
            student_id=student.student_id,
            order_by=AssessmentResponse.submitted_at,
        )
        return Page(
            items=[AssessmentHistoryItem.model_validate(r) for r in page.items],
            total=page.total,
            offset=page.offset,
            limit=page.limit,
        )

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    def _calculate_score(self, *, student_id: uuid.UUID, item_ids: set[uuid.UUID]) -> int:
        """Counts items answered correctly, using each item's most recent
        response if the student submitted more than one answer for it."""
        if not item_ids:
            return 0
        stmt = (
            select(AssessmentResponse)
            .where(AssessmentResponse.student_id == student_id, AssessmentResponse.item_id.in_(item_ids))
            .order_by(AssessmentResponse.submitted_at)
        )
        latest_by_item: dict[uuid.UUID, bool] = {}
        for response in self.db.execute(stmt).scalars().all():
            latest_by_item[response.item_id] = response.is_correct
        return sum(1 for is_correct in latest_by_item.values() if is_correct)

    def _require_student(
        self, actor: User, *, expected_student_id: uuid.UUID | None = None
    ) -> StudentProfile:
        if actor.role != UserRole.STUDENT:
            raise AuthorizationError("Only students may attempt assessments.")
        if actor.student_profile is None:
            raise ValidationFailedError(
                "A student profile must be created (PATCH /users/{id}) before attempting assessments."
            )
        if expected_student_id is not None and expected_student_id != actor.student_profile.student_id:
            raise AuthorizationError("You may only attempt assessments as yourself.")
        return actor.student_profile

    @staticmethod
    def _normalize(answer: str) -> str:
        return answer.strip().casefold()