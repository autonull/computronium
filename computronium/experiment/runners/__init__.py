"""Experiment runners: specialized experiment types built on the shared kernel.

Each runner implements a distinct experiment pattern (ablation, scaling, comparison, replay)
using the shared search space, evaluation, and persistence infrastructure.
"""

from computronium.experiment.runners.ablation import AblationRunner, AblationSpec
from computronium.experiment.runners.comparison import ComparisonRunner, ComparisonSpec
from computronium.experiment.runners.replay import ReplayRunner, ReplaySpec

__all__ = [
    "AblationRunner",
    "AblationSpec",
    "ComparisonRunner",
    "ComparisonSpec",
    "ReplayRunner",
    "ReplaySpec",
]
