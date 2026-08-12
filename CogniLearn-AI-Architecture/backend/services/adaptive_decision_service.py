"""
Adaptive Decision Service.

Composes RecommendationService and LearningPathService outputs into the
single Adaptive Decision Engine output
(algorithms/adaptive_engine/adaptive_decision_engine.py), consistent
with the documented pipeline order (Recommendation Engine and Learning
Path Engine feed the Adaptive Decision Engine) — reuses their public
methods rather than recomputing evidence gathering itself.

Reference: 04_ALGORITHM_DESIGN/06_Adaptive_Decision_Engine.md
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.algorithms.adaptive_engine.adaptive_decision_engine import AdaptiveDecision, decide
from backend.algorithms.irt.estimator import classify_ability
from backend.core.exceptions import NotFoundError
from backend.core.logging import get_logger
from backend.models import User
from backend.repositories import LearnerProfileRepository, LearningObjectiveRepository
from backend.services.learning_path_service import LearningPathService
from backend.services.recommendation_service import RecommendationService

logger = get_logger(__name__)


class AdaptiveDecisionService:
    """Business logic for computing a student's single next-action decision."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.learner_profiles = LearnerProfileRepository(db)
        self.learning_objectives = LearningObjectiveRepository(db)
        self.recommendation_service = RecommendationService(db)
        self.learning_path_service = LearningPathService(db)

    def get_next_decision(self, *, actor: User, course_id: uuid.UUID | None = None) -> AdaptiveDecision:
        candidates = self.recommendation_service.compute_candidates(actor=actor)
        top_recommendation = candidates[0] if candidates else None

        next_topic_id = self.learning_path_service.find_next_unencountered_topic_id(
            actor=actor, course_id=course_id
        )

        student_id = actor.student_profile.student_id
        learner_page = self.learner_profiles.find_all(student_id=student_id, limit=1)
        if learner_page.total == 0:
            raise NotFoundError("No learner data yet — attempt an assessment first.")
        ability_category = classify_ability(learner_page.items[0].ability_theta)

        target_topic_id = (top_recommendation.topic_id if top_recommendation else None) or next_topic_id
        learning_objective = self._learning_objective_description(target_topic_id)

        decision = decide(
            top_recommendation=top_recommendation,
            next_unencountered_topic_id=next_topic_id,
            ability_category=ability_category,
            learning_objective=learning_objective,
        )
        logger.info(
            "Adaptive decision computed | student_id=%s | next_action=%s", student_id, decision.next_action
        )
        return decision

    def _learning_objective_description(self, topic_id: uuid.UUID | None) -> str | None:
        if topic_id is None:
            return None
        page = self.learning_objectives.find_all(topic_id=topic_id, limit=1)
        return page.items[0].description if page.total > 0 else None