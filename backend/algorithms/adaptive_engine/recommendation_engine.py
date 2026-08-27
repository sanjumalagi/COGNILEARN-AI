"""
Recommendation Engine.

Implements the documented rule-based recommendation strategy (Section
15's examples table and Section 11's priority order) — no formula is
specified for this component ("Uses predefined educational rules",
Section 18), so this implements exactly those documented rules
deterministically, reusing the mastery thresholds already established
in Module 7 (backend.algorithms.mastery_engine) rather than inventing
new ones.

Rule mapping (Section 15 "Recommendation Examples" -> Section 8
categories -> Section 11 priority order):

    mastery < 0.40 (weak)              -> Revision      (priority 1)
    weak AND >=2 incorrect responses   -> AI Support     (priority 2)
    0.40 <= mastery < 0.80 (moderate)  -> Practice       (priority 3)
    mastery >= 0.80, ability Advanced  -> Challenge      (priority 5)
    mastery >= 0.80, ability not Adv.  -> Progression    (priority 4)

"Reinforcement" (Section 8) describes the same weak-mastery condition
as "Revision" with no documented rule distinguishing them, so only one
recommendation is emitted per weak topic rather than firing both for
an identical trigger.

"Topic Dependencies" / prerequisite relationships are a documented
input (Section 5) with no backing table in the finalized database
schema (Module 1) — no prerequisite-aware rule is applied here as a
result; flagged in the Module 8 report.

Reference: 04_ALGORITHM_DESIGN/04_RECOMMENDATION_ENGINE_DESIGN.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from backend.algorithms.irt.estimator import AbilityCategory
from backend.algorithms.mastery_engine import STRONG_TOPIC_THRESHOLD, WEAK_TOPIC_THRESHOLD

# Not given a documented numeric value; a reasonable, minimal signal
# for "persistent misconceptions" (Section 15) beyond a single wrong
# answer, without over-fitting to an arbitrary large count.
PERSISTENT_MISCONCEPTION_INCORRECT_COUNT = 2


class RecommendationType(str, Enum):
    """The documented Recommendation Categories (Section 8) this engine emits."""

    REVISION = "Revision"
    PRACTICE = "Practice"
    PROGRESSION = "Progression"
    AI_SUPPORT = "AI Support"
    CHALLENGE = "Challenge"


@dataclass(frozen=True)
class TopicEvidence:
    """One topic's evidence, as consumed by the Recommendation Engine."""

    topic_id: uuid.UUID
    mastery_score: float
    incorrect_response_count: int


@dataclass(frozen=True)
class RecommendationCandidate:
    """One generated recommendation, ready for persistence."""

    topic_id: uuid.UUID
    recommendation_type: RecommendationType
    priority: int
    reason: str


# Priority values follow Section 11's documented order (1 = most urgent).
_PRIORITY_BY_TYPE = {
    RecommendationType.REVISION: 1,
    RecommendationType.AI_SUPPORT: 2,
    RecommendationType.PRACTICE: 3,
    RecommendationType.PROGRESSION: 4,
    RecommendationType.CHALLENGE: 5,
}


def generate_recommendations(
    *, topics: list[TopicEvidence], ability_category: AbilityCategory
) -> list[RecommendationCandidate]:
    """
    Generates recommendations for every topic with mastery evidence,
    per the documented rules, sorted by priority (most urgent first).
    """
    candidates: list[RecommendationCandidate] = []

    for topic in topics:
        if topic.mastery_score < WEAK_TOPIC_THRESHOLD:
            candidates.append(
                RecommendationCandidate(
                    topic_id=topic.topic_id,
                    recommendation_type=RecommendationType.REVISION,
                    priority=_PRIORITY_BY_TYPE[RecommendationType.REVISION],
                    reason=f"Mastery below threshold ({topic.mastery_score:.2f}).",
                )
            )
            if topic.incorrect_response_count >= PERSISTENT_MISCONCEPTION_INCORRECT_COUNT:
                candidates.append(
                    RecommendationCandidate(
                        topic_id=topic.topic_id,
                        recommendation_type=RecommendationType.AI_SUPPORT,
                        priority=_PRIORITY_BY_TYPE[RecommendationType.AI_SUPPORT],
                        reason=(
                            f"Persistent misconceptions detected "
                            f"({topic.incorrect_response_count} incorrect responses)."
                        ),
                    )
                )
        elif topic.mastery_score < STRONG_TOPIC_THRESHOLD:
            candidates.append(
                RecommendationCandidate(
                    topic_id=topic.topic_id,
                    recommendation_type=RecommendationType.PRACTICE,
                    priority=_PRIORITY_BY_TYPE[RecommendationType.PRACTICE],
                    reason=(
                        f"Moderate mastery ({topic.mastery_score:.2f}) — "
                        "additional practice recommended."
                    ),
                )
            )
        else:
            if ability_category == AbilityCategory.ADVANCED:
                candidates.append(
                    RecommendationCandidate(
                        topic_id=topic.topic_id,
                        recommendation_type=RecommendationType.CHALLENGE,
                        priority=_PRIORITY_BY_TYPE[RecommendationType.CHALLENGE],
                        reason="High ability and mastery — advanced assessment recommended.",
                    )
                )
            else:
                candidates.append(
                    RecommendationCandidate(
                        topic_id=topic.topic_id,
                        recommendation_type=RecommendationType.PROGRESSION,
                        priority=_PRIORITY_BY_TYPE[RecommendationType.PROGRESSION],
                        reason=(
                            f"High mastery ({topic.mastery_score:.2f}) — "
                            "ready to proceed to the next topic."
                        ),
                    )
                )

    return sorted(candidates, key=lambda c: c.priority)
