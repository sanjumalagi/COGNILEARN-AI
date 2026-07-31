"""
Bayesian Knowledge Tracing (BKT) Sub-Package.

Estimates topic mastery probability from response evidence using the
documented four-parameter BKT model.

Reference: 04_ALGORITHM_DESIGN/02_BAYESIAN_KNOWLEDGE_TRACING_DESIGN.md
"""

from backend.algorithms.bkt.estimator import BKTResult, MasteryStatus, classify_mastery, update_mastery

__all__ = ["BKTResult", "MasteryStatus", "classify_mastery", "update_mastery"]