"""
Item Response Theory (IRT) Engine.

Implements exactly the documented 1PL (Rasch) model:

    P(theta) = 1 / (1 + e^-(theta - b))

where theta is learner ability and b is item difficulty.

The design document specifies this model and says to "estimate ability
(theta)" but does not specify the numerical estimation procedure. This
implements the standard Maximum Likelihood Estimation (MLE) via
Newton-Raphson iteration for the 1PL model — the canonical estimator
for exactly this documented formula, not a substitute for it:

    score(theta)      = sum(u_i - P_i)
    information(theta) = sum(P_i * (1 - P_i))
    theta_new = theta_old + score(theta_old) / information(theta_old)

Ability is re-estimated from the learner's FULL response history each
time (not incrementally from a single new response), consistent with
IRT Section 5 listing both "Assessment Responses" (plural) and an
optional "Historical Ability" as inputs. The iterative solver always
starts from theta=0.0 (the scale's stable center): seeding it from a
previous estimate that happened to sit at an extreme value produces
near-zero local curvature there, which can leave Newton-Raphson
numerically stuck at that boundary instead of converging on the true
estimate for the full response set. `previous_theta` is used instead
as the documented "Historical Ability" fallback — the value returned
when there is no fresh response evidence to estimate from at all.

Reference: 04_ALGORITHM_DESIGN/01_ITEM_RESPONSE_THEORY_DESIGN.md
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

from backend.config import settings


class AbilityCategory(str, Enum):
    """Matches IRT Design Section 8 exactly: theta < -1.0 / -1.0 <= theta <= 1.0 / theta > 1.0."""

    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


@dataclass(frozen=True)
class IRTResult:
    """The documented IRT Engine outputs (Section 6): Ability (theta),
    Ability Category, Confidence Score, Difficulty Recommendation."""

    ability: float
    category: AbilityCategory
    confidence_score: float
    difficulty_recommendation: float


def probability_correct(theta: float, difficulty: float) -> float:
    """The documented 1PL (Rasch) item response function P(theta)."""
    return 1.0 / (1.0 + math.exp(-(theta - difficulty)))


def classify_ability(theta: float) -> AbilityCategory:
    """Matches IRT Design Section 8's exact thresholds."""
    if theta < -1.0:
        return AbilityCategory.BEGINNER
    if theta > 1.0:
        return AbilityCategory.ADVANCED
    return AbilityCategory.INTERMEDIATE


def estimate_ability(
    *, responses: list[tuple[bool, float]], previous_theta: float | None = None
) -> IRTResult:
    """
    Estimates learner ability (theta) via Newton-Raphson MLE for the 1PL
    model, from a list of (is_correct, item_difficulty) pairs.

    `previous_theta` (the documented, optional "Historical Ability"
    input) is returned as-is when there are no responses to estimate
    from; otherwise the solver always starts from 0.0 regardless of
    `previous_theta` (see module docstring for why).

    Confidence Score and Difficulty Recommendation are not given
    explicit formulas in the design document. Both are computed here
    from the standard IRT quantities directly implied by the one
    documented model:
    - Confidence Score: derived from Fisher information
      I(theta) = sum(P_i(1-P_i)); more/more-informative responses
      shrink the standard error 1/sqrt(I), which is transformed to a
      bounded (0, 1] score via 1 / (1 + SE).
    - Difficulty Recommendation: the standard adaptive-testing result
      that a Rasch item provides maximum information at b = theta, so
      the recommended next-item difficulty is the current estimate
      itself.

    Returns `previous_theta` (or 0.0 if that too is None), minimum
    confidence, if `responses` is empty (no fresh evidence).
    """
    if not responses:
        fallback_theta = previous_theta if previous_theta is not None else 0.0
        return IRTResult(
            ability=fallback_theta,
            category=classify_ability(fallback_theta),
            confidence_score=0.0,
            difficulty_recommendation=round(fallback_theta, 4),
        )

    theta = 0.0

    information = 0.0
    for _ in range(settings.IRT_MAX_ITERATIONS):
        probabilities = [probability_correct(theta, b) for _, b in responses]
        score = sum(
            (1.0 if is_correct else 0.0) - p
            for (is_correct, _), p in zip(responses, probabilities, strict=True)
        )
        information = sum(p * (1.0 - p) for p in probabilities)

        if information == 0.0:
            break  # All responses saturated (P near 0 or 1); further iteration would divide by zero.

        step = score / information
        theta += step
        # Clamp after every step (not just at the end): starting near an
        # extreme value produces near-zero information (flat curvature),
        # which can otherwise produce a huge, unstable step that never
        # recovers within the iteration budget.
        theta = max(settings.IRT_ABILITY_MIN, min(settings.IRT_ABILITY_MAX, theta))

        if abs(step) < settings.IRT_CONVERGENCE_THRESHOLD:
            break

    standard_error = 1.0 / math.sqrt(information) if information > 0.0 else float("inf")
    confidence_score = 1.0 / (1.0 + standard_error) if math.isfinite(standard_error) else 0.0

    return IRTResult(
        ability=theta,
        category=classify_ability(theta),
        confidence_score=round(confidence_score, 4),
        difficulty_recommendation=round(theta, 4),
    )