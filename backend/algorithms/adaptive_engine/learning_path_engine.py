"""
Learning Path Engine.

Implements the documented path-generation strategy: weak topics first
(revision), then developing/proficient topics (practice), then the
next not-yet-encountered topic in curriculum order (progression).
Mastered topics are excluded — no action is needed for them.

No formula is specified for path ordering (rule-based, like the
Recommendation Engine); this reuses the same mastery thresholds
(backend.algorithms.mastery_engine) for consistency between the two
engines, per the documented pipeline where both consume the same
mastery evidence.

Curriculum order ("Course Structure", a documented input) is derived
from Module.sequence_number and each Topic's position within its
Module — the finalized database schema (Module 1) has no separate
topic-prerequisite/dependency table, so this is the best available,
already-persisted ordering signal.

Reference: 04_ALGORITHM_DESIGN/05_LEARNING_PATH_ENGINE_DESIGN.md
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum

from backend.algorithms.mastery_engine import STRONG_TOPIC_THRESHOLD, WEAK_TOPIC_THRESHOLD


class PathStepStatus(str, Enum):
    """Status values for a LearningPath entry. Not given an explicit
    documented enumeration (the DB column is a plain VARCHAR); these are
    the minimal, standard states needed to represent a path step."""

    PENDING = "pending"
    COMPLETED = "completed"


@dataclass(frozen=True)
class TopicMasteryEvidence:
    """One topic's mastery evidence, as consumed by the Learning Path Engine."""

    topic_id: uuid.UUID
    mastery_score: float


@dataclass(frozen=True)
class PathStep:
    """One step in the generated learning path, ready for persistence."""

    topic_id: uuid.UUID
    sequence_order: int
    status: PathStepStatus


def build_learning_path(
    *, encountered_topics: list[TopicMasteryEvidence], next_unencountered_topic_id: uuid.UUID | None
) -> list[PathStep]:
    """
    Builds an ordered, near-term learning path:
    1. Weak topics (mastery < 0.40), worst first — revision priority.
    2. Developing/proficient topics (0.40-0.80) — practice priority.
    3. The single next not-yet-encountered topic in curriculum order, if any.

    Mastered topics (mastery >= 0.80) are omitted — already achieved,
    no path action needed.
    """
    weak = sorted(
        (t for t in encountered_topics if t.mastery_score < WEAK_TOPIC_THRESHOLD),
        key=lambda t: t.mastery_score,
    )
    developing = sorted(
        (t for t in encountered_topics if WEAK_TOPIC_THRESHOLD <= t.mastery_score < STRONG_TOPIC_THRESHOLD),
        key=lambda t: t.mastery_score,
    )

    ordered_topic_ids: list[uuid.UUID] = [t.topic_id for t in weak] + [t.topic_id for t in developing]
    if next_unencountered_topic_id is not None:
        ordered_topic_ids.append(next_unencountered_topic_id)

    return [
        PathStep(topic_id=topic_id, sequence_order=index, status=PathStepStatus.PENDING)
        for index, topic_id in enumerate(ordered_topic_ids, start=1)
    ]
