"""
Mastery Engine.

Classifies a topic's BKT mastery_score (0.0-1.0) into the Mastery
Engine's own 5-level educational scale (Section 8) — distinct from
BKT's own 3-level per-response classification (Needs Improvement /
Developing / Mastered) — and identifies weak/strong topics.

The design document (Section 8) names five categories (Not Started,
Beginner, Developing, Proficient, Mastered) and states "these
categories are configurable" but gives no numeric thresholds. The
boundaries below are anchored to BKT's own explicit thresholds (0.40
and 0.80, Section 8 of the BKT document) so the two engines agree at
their shared boundary, with the 0.40-0.80 band split at its midpoint:

    No TopicMastery record  -> Not Started
    [0.00, 0.40)            -> Beginner
    [0.40, 0.60)            -> Developing
    [0.60, 0.80)            -> Proficient
    [0.80, 1.00]            -> Mastered

Weak topics are those below the BKT "Needs Improvement" threshold
(< 0.40); strong topics are those at or above the BKT "Mastered"
threshold (>= 0.80) — using BKT's own documented boundaries rather
than inventing separate ones.

Reference: 04_ALGORITHM_DESIGN/03_MASTERY_ENGINE_DESIGN.md
"""

from __future__ import annotations

from enum import Enum

WEAK_TOPIC_THRESHOLD = 0.40
STRONG_TOPIC_THRESHOLD = 0.80


class MasteryLevel(str, Enum):
    """Matches Mastery Engine Design Section 8's five categories."""

    NOT_STARTED = "Not Started"
    BEGINNER = "Beginner"
    DEVELOPING = "Developing"
    PROFICIENT = "Proficient"
    MASTERED = "Mastered"


def classify_mastery_level(mastery_score: float | None) -> MasteryLevel:
    """Classifies a topic mastery score into the 5-level educational scale.
    `None` (no TopicMastery record yet) is "Not Started"."""
    if mastery_score is None:
        return MasteryLevel.NOT_STARTED
    if mastery_score < 0.40:
        return MasteryLevel.BEGINNER
    if mastery_score < 0.60:
        return MasteryLevel.DEVELOPING
    if mastery_score < 0.80:
        return MasteryLevel.PROFICIENT
    return MasteryLevel.MASTERED


def is_weak_topic(mastery_score: float) -> bool:
    """A topic requiring reinforcement (BKT's own "Needs Improvement" boundary)."""
    return mastery_score < WEAK_TOPIC_THRESHOLD


def is_strong_topic(mastery_score: float) -> bool:
    """A topic already mastered (BKT's own "Mastered" boundary)."""
    return mastery_score >= STRONG_TOPIC_THRESHOLD


def calculate_overall_mastery(topic_mastery_scores: list[float]) -> float:
    """
    Aggregates per-topic mastery scores into the LearnerProfile's
    `overall_mastery` — "Overall learner knowledge representation"
    (Section 11). No weighting scheme is documented, so this is the
    unweighted mean of all tracked topics; 0.0 if none are tracked yet.
    """
    if not topic_mastery_scores:
        return 0.0
    return round(sum(topic_mastery_scores) / len(topic_mastery_scores), 4)