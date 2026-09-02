"""
Teaching Engine Service.

Coordinates Educational Intelligence and Teaching Intelligence to produce
the Teaching Context consumed by the AI Service Layer.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from backend.algorithms.adaptive_engine.adaptive_decision_engine import (
    AdaptiveDecision,
)
from backend.algorithms.irt.estimator import classify_ability
from backend.algorithms.mastery_engine import (
    classify_mastery_level,
    is_weak_topic,
)
from backend.algorithms.teaching_engine.teaching_engine import (
    TeachingContextData,
    generate_teaching_context,
)
from backend.algorithms.teaching_engine.teaching_strategy_engine import (
    select_teaching_strategy,
)
from backend.core.exceptions import NotFoundError
from backend.models import User
from backend.repositories import (
    LearnerProfileRepository,
    TopicMasteryRepository,
    TopicRepository,
)
from backend.services.adaptive_decision_service import AdaptiveDecisionService


class TeachingEngineService:
    """Business service for generating learner-specific Teaching Context."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.learner_profiles = LearnerProfileRepository(db)
        self.topic_masteries = TopicMasteryRepository(db)
        self.topics = TopicRepository(db)
        self.adaptive_decision_service = AdaptiveDecisionService(db)

    def generate_context(
        self,
        *,
        actor: User,
        topic_id: uuid.UUID,
        course_id: uuid.UUID | None = None,
    ) -> TeachingContextData:
        """
        Generate Teaching Context for the requested topic.

        The AI request specifies the topic being discussed. Teaching
        Intelligence therefore evaluates that topic's learner state,
        rather than silently switching to another recommended topic.
        """

        # ---------------------------------------------------------
        # Validate requested topic
        # ---------------------------------------------------------

        topic = self.topics.find_by_id(topic_id)

        if topic is None:
            raise NotFoundError("Topic not found.")

        # ---------------------------------------------------------
        # Get learner profile / IRT ability
        # ---------------------------------------------------------

        if actor.student_profile is None:
            raise NotFoundError(
                "A student profile is required before generating "
                "a Teaching Context."
            )

        student_id = actor.student_profile.student_id

        profile_page = self.learner_profiles.find_all(
            student_id=student_id,
            limit=1,
        )

        if profile_page.total == 0:
            raise NotFoundError(
                "No learner data yet — attempt an assessment first."
            )

        profile = profile_page.items[0]

        ability_category = classify_ability(
            profile.ability_theta
        )

        # ---------------------------------------------------------
        # Get BKT mastery for requested topic
        # ---------------------------------------------------------

        mastery_page = self.topic_masteries.find_all(
            learner_profile_id=profile.learner_profile_id,
            limit=10_000,
        )

        topic_mastery = next(
            (
                mastery.mastery_score
                for mastery in mastery_page.items
                if mastery.topic_id == topic_id
            ),
            None,
        )

        mastery_level = classify_mastery_level(
            topic_mastery
        )

        # ---------------------------------------------------------
        # Gather weak concepts
        # ---------------------------------------------------------

        weak_concepts: list[str] = []

        for mastery in mastery_page.items:
            if (
                mastery.mastery_score is not None
                and is_weak_topic(mastery.mastery_score)
            ):
                weak_topic = self.topics.find_by_id(
                    mastery.topic_id
                )

                if weak_topic is not None:
                    weak_concepts.append(
                        weak_topic.title
                    )

        # ---------------------------------------------------------
        # Get the global adaptive decision
        # ---------------------------------------------------------

        adaptive_decision = (
            self.adaptive_decision_service.get_next_decision(
                actor=actor,
                course_id=course_id,
            )
        )

        # ---------------------------------------------------------
        # Make the decision topic-safe
        # ---------------------------------------------------------

        if adaptive_decision.topic_id == topic_id:
            decision = adaptive_decision

        else:
            decision = AdaptiveDecision(
                next_action=adaptive_decision.next_action,
                topic_id=topic_id,
                difficulty=adaptive_decision.difficulty,
                reason=(
                    f"{adaptive_decision.reason} "
                    "Teaching context is being generated for the "
                    "topic requested by the learner."
                ),
                ai_support=adaptive_decision.ai_support,
                assessment_required=adaptive_decision.assessment_required,
                learning_objective=(
                    self._learning_objective_description(
                        topic_id
                    )
                ),
            )

        # ---------------------------------------------------------
        # Generate Teaching Context
        # ---------------------------------------------------------

        return generate_teaching_context(
            decision=decision,
            mastery_level=mastery_level,
            ability_category=ability_category,
            weak_concepts=weak_concepts,
        )

    def _learning_objective_description(
        self,
        topic_id: uuid.UUID,
    ) -> str | None:
        """
        Get the learning objective for the requested topic.
        """

        from backend.repositories import LearningObjectiveRepository

        page = LearningObjectiveRepository(
            self.db
        ).find_all(
            topic_id=topic_id,
            limit=1,
        )

        if page.total > 0:
            return page.items[0].description

        return None