"""
Recommendation Service.

Orchestrates the Recommendation Engine: gathers each student's topic
mastery evidence and per-topic incorrect-response counts, applies the
documented rules (algorithms/adaptive_engine/recommendation_engine.py),
and persists the result — replacing any previously-generated
recommendations for the student, since recommendations reflect current
evidence, not a historical log (unlike ProgressHistory).

Reference: 04_ALGORITHM_DESIGN/04_RECOMMENDATION_ENGINE_DESIGN.md
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.algorithms.adaptive_engine.recommendation_engine import (
    RecommendationCandidate,
    TopicEvidence,
    generate_recommendations,
)
from backend.algorithms.irt.estimator import classify_ability
from backend.core.exceptions import AuthorizationError, NotFoundError, ValidationFailedError
from backend.core.logging import get_logger
from backend.models import Recommendation, StudentProfile, User, UserRole
from backend.repositories import (
    AssessmentItemRepository,
    AssessmentRepository,
    AssessmentResponseRepository,
    LearnerProfileRepository,
    RecommendationRepository,
    TopicMasteryRepository,
)

logger = get_logger(__name__)


class RecommendationService:
    """Business logic for generating and retrieving a student's recommendations."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.recommendations = RecommendationRepository(db)
        self.learner_profiles = LearnerProfileRepository(db)
        self.topic_masteries = TopicMasteryRepository(db)
        self.responses = AssessmentResponseRepository(db)
        self.items = AssessmentItemRepository(db)
        self.assessments = AssessmentRepository(db)

    def compute_candidates(self, *, actor: User) -> list[RecommendationCandidate]:
        """
        Computes (without persisting) the current recommendation
        candidates for a student, with full reason text. Shared by
        `refresh_and_get_recommendations` (which persists a summarized
        version — the Recommendation table has no free-text reason
        column) and `AdaptiveDecisionService` (which needs the full
        detail), so neither duplicates evidence-gathering logic.
        """
        student = self._require_student(actor)
        evidence = self._gather_topic_evidence(student)

        learner_page = self.learner_profiles.find_all(student_id=student.student_id, limit=1)
        if learner_page.total == 0:
            raise NotFoundError("No learner data yet — attempt an assessment first.")
        ability_category = classify_ability(learner_page.items[0].ability_theta)

        return generate_recommendations(topics=evidence, ability_category=ability_category)

    def refresh_and_get_recommendations(self, *, actor: User) -> list[Recommendation]:
        """Regenerates and persists recommendations from the student's
        current evidence, replacing any previous set, and returns them."""
        student = self._require_student(actor)
        candidates = self.compute_candidates(actor=actor)

        existing = self.recommendations.find_all(student_id=student.student_id, limit=10_000)
        for old in existing.items:
            self.recommendations.delete(old.recommendation_id)

        created = [
            self.recommendations.create(
                student_id=student.student_id,
                topic_id=candidate.topic_id,
                recommendation_type=candidate.recommendation_type.value,
                priority=candidate.priority,
            )
            for candidate in candidates
        ]
        logger.info(
            "Recommendations refreshed | student_id=%s | count=%d", student.student_id, len(created)
        )
        return created

    def get_revision_recommendations(self, *, actor: User) -> list[Recommendation]:
        """The documented revision-plan view: only Revision/AI Support
        recommendations (the two categories addressing weak topics)."""
        all_recommendations = self.refresh_and_get_recommendations(actor=actor)
        return [r for r in all_recommendations if r.recommendation_type in ("Revision", "AI Support")]

    def _gather_topic_evidence(self, student: StudentProfile) -> list[TopicEvidence]:
        masteries_page = self.topic_masteries.find_all(
            learner_profile_id=self._learner_profile_id(student), limit=10_000
        )
        incorrect_counts = self._incorrect_response_counts_by_topic(student.student_id)

        return [
            TopicEvidence(
                topic_id=mastery.topic_id,
                mastery_score=mastery.mastery_score,
                incorrect_response_count=incorrect_counts.get(mastery.topic_id, 0),
            )
            for mastery in masteries_page.items
        ]

    def _incorrect_response_counts_by_topic(self, student_id: uuid.UUID) -> dict[uuid.UUID, int]:
        counts: dict[uuid.UUID, int] = {}
        response_page = self.responses.find_all(student_id=student_id, limit=10_000)
        for response in response_page.items:
            if response.is_correct:
                continue
            item = self.items.find_by_id(response.item_id)
            if item is None:
                continue
            assessment = self.assessments.find_by_id(item.assessment_id)
            if assessment is None:
                continue
            counts[assessment.topic_id] = counts.get(assessment.topic_id, 0) + 1
        return counts

    def _learner_profile_id(self, student: StudentProfile) -> uuid.UUID:
        page = self.learner_profiles.find_all(student_id=student.student_id, limit=1)
        if page.total == 0:
            raise NotFoundError("No learner data yet — attempt an assessment first.")
        return page.items[0].learner_profile_id

    def _require_student(self, actor: User) -> StudentProfile:
        if actor.role != UserRole.STUDENT:
            raise AuthorizationError("Only students receive recommendations.")
        if actor.student_profile is None:
            raise ValidationFailedError(
                "A student profile must be created (PATCH /users/{id}) before viewing recommendations."
            )
        return actor.student_profile