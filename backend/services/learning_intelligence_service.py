"""
Learning Intelligence Service.

Orchestrates the documented pipeline that runs immediately after each
assessment response is evaluated (IRT Design Section 4; BKT Design
Section 4): re-estimate ability via IRT, update topic mastery via BKT,
update the learner's overall mastery via the Mastery Engine, and record
a Progress History snapshot.

Called from `assessment_attempt_service.submit_assessment()` (Module 6)
immediately after an AssessmentResponse is persisted — Assessment
Intelligence produces the evidence; Learning Intelligence consumes it.

Reference: 04_ALGORITHM_DESIGN/01_ITEM_RESPONSE_THEORY_DESIGN.md (Section 4 - Processing Pipeline)
Reference: 04_ALGORITHM_DESIGN/02_BAYESIAN_KNOWLEDGE_TRACING_DESIGN.md (Section 4 - Processing Pipeline)
Reference: 04_ALGORITHM_DESIGN/03_MASTERY_ENGINE_DESIGN.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy.orm import Session

from backend.algorithms.bkt.estimator import BKTResult, update_mastery
from backend.algorithms.irt.estimator import IRTResult, estimate_ability
from backend.algorithms.mastery_engine import calculate_overall_mastery
from backend.core.exceptions import NotFoundError
from backend.core.logging import get_logger
from backend.models import AssessmentResponse
from backend.repositories import (
    AssessmentItemRepository,
    AssessmentRepository,
    AssessmentResponseRepository,
    LearnerProfileRepository,
    ProgressHistoryRepository,
    TopicMasteryRepository,
)

logger = get_logger(__name__)


@dataclass(frozen=True)
class LearningIntelligenceUpdate:
    """Summary of one pipeline run, returned to the caller (e.g. for logging/testing)."""

    topic_id: uuid.UUID
    irt_result: IRTResult
    bkt_result: BKTResult


class LearningIntelligenceService:
    """Business logic for updating a learner's ability and topic mastery from new evidence."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.learner_profiles = LearnerProfileRepository(db)
        self.topic_masteries = TopicMasteryRepository(db)
        self.progress_history = ProgressHistoryRepository(db)
        self.items = AssessmentItemRepository(db)
        self.assessments = AssessmentRepository(db)
        self.responses = AssessmentResponseRepository(db)

    def process_response(
        self, *, student_id: uuid.UUID, response: AssessmentResponse
    ) -> LearningIntelligenceUpdate:
        """
        Runs the full IRT -> BKT -> Mastery Engine -> Progress History
        pipeline for one newly-recorded AssessmentResponse.
        """
        item = self.items.find_by_id(response.item_id)
        if item is None:
            raise NotFoundError(f"Assessment item with id={response.item_id!r} was not found.")
        assessment = self.assessments.find_by_id(item.assessment_id)
        if assessment is None:
            raise NotFoundError(f"Assessment with id={item.assessment_id!r} was not found.")
        topic_id = assessment.topic_id

        learner_profile = self.learner_profiles.find_all(student_id=student_id, limit=1)
        if learner_profile.total == 0:
            profile = self.learner_profiles.create(
                student_id=student_id, ability_theta=0.0, overall_mastery=0.0
            )
        else:
            profile = learner_profile.items[0]

        irt_result = self._update_ability(student_id=student_id, profile_id=profile.learner_profile_id)

        bkt_result = self._update_topic_mastery(
            profile_id=profile.learner_profile_id, topic_id=topic_id, is_correct=response.is_correct
        )

        self._update_overall_mastery(profile_id=profile.learner_profile_id)

        self.progress_history.create(
            student_id=student_id, topic_id=topic_id, mastery_score=bkt_result.mastery_probability
        )

        logger.info(
            "Learning intelligence updated | student_id=%s | topic_id=%s | ability=%s | mastery=%s",
            student_id,
            topic_id,
            irt_result.ability,
            bkt_result.mastery_probability,
        )
        return LearningIntelligenceUpdate(topic_id=topic_id, irt_result=irt_result, bkt_result=bkt_result)

    def get_ability_estimate(self, *, student_id: uuid.UUID) -> IRTResult:
        """
        Computes (without persisting) the full documented IRT output for
        a student from their complete response history. Shared by the
        write path (`_update_ability`, which persists the result) and
        `LearnerService.get_ability` (read-only), so both report the
        exact same ability/confidence/difficulty-recommendation values
        without duplicating the response-gathering logic.
        """
        history_page = self.responses.find_all(student_id=student_id, limit=10_000)

        responses: list[tuple[bool, float]] = []
        for past_response in history_page.items:
            past_item = self.items.find_by_id(past_response.item_id)
            if past_item is not None:
                responses.append((past_response.is_correct, past_item.difficulty))

        learner_page = self.learner_profiles.find_all(student_id=student_id, limit=1)
        previous_theta = learner_page.items[0].ability_theta if learner_page.total > 0 else None

        return estimate_ability(responses=responses, previous_theta=previous_theta)

    def _update_ability(self, *, student_id: uuid.UUID, profile_id: uuid.UUID) -> IRTResult:
        """Re-estimates ability (theta) from the student's full response
        history and persists it onto the LearnerProfile."""
        irt_result = self.get_ability_estimate(student_id=student_id)
        self.learner_profiles.update(profile_id, ability_theta=irt_result.ability)
        return irt_result

    def _update_topic_mastery(
        self, *, profile_id: uuid.UUID, topic_id: uuid.UUID, is_correct: bool
    ) -> BKTResult:
        """Applies one BKT update for the topic the just-answered item belongs to."""
        existing_page = self.topic_masteries.find_all(
            learner_profile_id=profile_id, topic_id=topic_id, limit=1
        )
        previous_mastery = existing_page.items[0].mastery_score if existing_page.total > 0 else None

        bkt_result = update_mastery(previous_mastery=previous_mastery, is_correct=is_correct)

        if existing_page.total > 0:
            self.topic_masteries.update(
                existing_page.items[0].mastery_id, mastery_score=bkt_result.mastery_probability
            )
        else:
            self.topic_masteries.create(
                learner_profile_id=profile_id,
                topic_id=topic_id,
                mastery_score=bkt_result.mastery_probability,
            )
        return bkt_result

    def _update_overall_mastery(self, *, profile_id: uuid.UUID) -> None:
        """Recomputes LearnerProfile.overall_mastery as the mean of all tracked topic masteries."""
        all_masteries = self.topic_masteries.find_all(learner_profile_id=profile_id, limit=10_000)
        overall = calculate_overall_mastery([m.mastery_score for m in all_masteries.items])
        self.learner_profiles.update(profile_id, overall_mastery=overall)