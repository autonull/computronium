"""Local-feedback — adaptive feedback projections for local credit assignment.

Slowly adapting the feedback pathway onto the forward weight improves descent
quality per unit displacement over fixed random feedback under matched norm
(X-ALI-001 validated scope: EqProp-style random-projection credit, quick
budget, 30-step trajectories, 3 seeds). Extracted from the Computronium
project.
"""

from __future__ import annotations

from local_feedback.adaptive import AdaptiveFeedback
from local_feedback.baselines import FixedFeedback, matched_norm
from local_feedback.metrics import (
    feedback_alignment,
    improvement_per_norm,
    late_half_mean,
    pseudo_gradient_alignment,
)
from local_feedback.trainer import LocalFeedbackTrainer, StepStats

__all__ = [
    "AdaptiveFeedback",
    "FixedFeedback",
    "LocalFeedbackTrainer",
    "StepStats",
    "feedback_alignment",
    "improvement_per_norm",
    "late_half_mean",
    "matched_norm",
    "pseudo_gradient_alignment",
]
