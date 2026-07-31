"""
Bayesian Knowledge Tracing (BKT) Engine.

Implements the standard four-parameter BKT update (Corbett & Anderson),
which is exactly the model the design document names in Section 7
(P(L0), P(T), P(G), P(S)) without restating its equations. This
implements the canonical two-step Bayesian update associated with
those four named parameters — not a substitute for it:

Step 1 (evidence update — Bayes' rule given the observed response):

    if correct:
        P(L | correct)   = P(L)*(1-P(S)) / [P(L)*(1-P(S)) + (1-P(L))*P(G)]
    if incorrect:
        P(L | incorrect) = P(L)*P(S) / [P(L)*P(S) + (1-P(L))*(1-P(G))]

Step 2 (learning transition — the opportunity to learn just given):

    P(L_new) = P(L | observation) + (1 - P(L | observation)) * P(T)

Numeric values for P(L0)/P(T)/P(G)/P(S) are not given in the design
document; `backend.config.settings` supplies the widely-cited BKT
literature defaults (see settings.py for the citation), configurable
without code changes.

Reference: 04_ALGORITHM_DESIGN/02_BAYESIAN_KNOWLEDGE_TRACING_DESIGN.md
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.config import settings


class MasteryStatus(str, Enum):
    """Matches BKT Design Section 8 exactly: < 0.40 / 0.40-0.80 / > 0.80."""

    NEEDS_IMPROVEMENT = "Needs Improvement"
    DEVELOPING = "Developing"
    MASTERED = "Mastered"


@dataclass(frozen=True)
class BKTResult:
    """The documented BKT Engine outputs (Section 6): Mastery
    Probability, Mastery Status, and whether a Recommendation Trigger
    is warranted."""

    mastery_probability: float
    status: MasteryStatus
    recommendation_trigger: bool


def classify_mastery(probability: float) -> MasteryStatus:
    """Matches BKT Design Section 8's exact thresholds."""
    if probability < 0.40:
        return MasteryStatus.NEEDS_IMPROVEMENT
    if probability > 0.80:
        return MasteryStatus.MASTERED
    return MasteryStatus.DEVELOPING


def update_mastery(*, previous_mastery: float | None, is_correct: bool) -> BKTResult:
    """
    Applies one BKT update for a single observed response.

    `previous_mastery` is the documented "Historical Mastery" input; if
    this is the learner's first observed response for this knowledge
    component, `previous_mastery` is None and P(L0) is used as the
    starting prior (documented as "Initial probability that the learner
    already knows the concept").
    """
    prior = previous_mastery if previous_mastery is not None else settings.BKT_PRIOR_L0

    p_slip = settings.BKT_PROB_SLIP
    p_guess = settings.BKT_PROB_GUESS
    p_transition = settings.BKT_PROB_TRANSITION

    if is_correct:
        numerator = prior * (1.0 - p_slip)
        denominator = numerator + (1.0 - prior) * p_guess
    else:
        numerator = prior * p_slip
        denominator = numerator + (1.0 - prior) * (1.0 - p_guess)

    posterior_given_evidence = numerator / denominator if denominator > 0.0 else prior

    new_mastery = posterior_given_evidence + (1.0 - posterior_given_evidence) * p_transition
    new_mastery = max(0.0, min(1.0, new_mastery))

    status = classify_mastery(new_mastery)
    return BKTResult(
        mastery_probability=round(new_mastery, 4),
        status=status,
        recommendation_trigger=status == MasteryStatus.NEEDS_IMPROVEMENT,
    )