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

Numeric values for P(T)/P(G)/P(S) are not given in the design
document; `backend.config.settings` supplies the widely-cited BKT
literature defaults (see settings.py for the citation), configurable
without code changes.

Initial mastery is NOT established from a fixed P(L0) constant.
Instead, `compute_initial_mastery()` derives an evidence-based initial
mastery from a student's diagnostic assessment responses for a topic.
See the function docstring for the full rationale.

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


def compute_initial_mastery(*, diagnostic_responses: list[bool]) -> float:
    """
    Derives an evidence-based initial mastery estimate from a student's
    diagnostic assessment responses for a topic.

    Uses iterative Bayesian updating: starts from a non-informative
    prior (0.5 — maximum uncertainty) and applies the BKT evidence step
    (Bayes' rule with P(G) and P(S)) for each diagnostic response.

    The learning transition P(T) is deliberately NOT applied during
    diagnostic computation, because the diagnostic measures *existing*
    knowledge — the student is not learning during the diagnostic, they
    are demonstrating what they already know.

    The result captures the student's demonstrated knowledge level
    across multiple questions, not a single arbitrary response. A
    student scoring 3/4 correct will receive a materially different
    initial mastery than one scoring 1/4 correct.

    This is the ONLY sanctioned way to establish initial mastery for a
    new learner on a topic. The adaptive engine must call this before
    the first ``update_mastery()`` call.

    The non-informative 0.5 prior is mathematically justified: it
    expresses maximum uncertainty before any evidence, and it is
    quickly overwhelmed by even 2-3 responses. It is NOT the same as
    a hardcoded P(L0)=0.3 baseline — it is a Bayesian starting point
    that exists only to bootstrap the first evidence update.

    Future milestone: A teacher-created diagnostic assessment will
    provide these responses. For now, the student's initial assessment
    responses for a topic serve as the diagnostic evidence.

    Args:
        diagnostic_responses: Ordered list of correct/incorrect results
            from the student's diagnostic assessment for this topic.
            Must contain at least one response.

    Returns:
        Initial mastery probability in [0.0, 1.0].

    Raises:
        ValueError: If diagnostic_responses is empty.
    """
    if not diagnostic_responses:
        raise ValueError(
            "At least one diagnostic response is required to establish "
            "initial mastery. Cannot compute initial mastery from zero evidence."
        )

    p_slip = settings.BKT_PROB_SLIP
    p_guess = settings.BKT_PROB_GUESS

    # Start from maximum-uncertainty non-informative prior.
    mastery = 0.5

    for is_correct in diagnostic_responses:
        if is_correct:
            numerator = mastery * (1.0 - p_slip)
            denominator = numerator + (1.0 - mastery) * p_guess
        else:
            numerator = mastery * p_slip
            denominator = numerator + (1.0 - mastery) * (1.0 - p_guess)

        mastery = numerator / denominator if denominator > 0.0 else mastery

    return max(0.0, min(1.0, round(mastery, 4)))


def update_mastery(*, previous_mastery: float | None, is_correct: bool) -> BKTResult:
    """
    Applies one BKT update for a single observed response.

    ``previous_mastery`` is the documented "Historical Mastery" input.
    It MUST be provided — either from a persisted TopicMastery record
    (for returning learners) or from ``compute_initial_mastery()`` (for
    new learners whose diagnostic evidence has just been processed).

    Raises:
        ValueError: If ``previous_mastery`` is None. Initial mastery
            must be established from diagnostic evidence via
            ``compute_initial_mastery()`` before BKT updates can begin.
    """
    if previous_mastery is None:
        raise ValueError(
            "Initial mastery must be established from diagnostic evidence "
            "before BKT updates can begin. Use compute_initial_mastery() "
            "to derive an evidence-based initial mastery estimate first."
        )

    prior = previous_mastery

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