"""Bioplausible Experiments Package.

Flagship experiments for publishable bio-plausible learning results.
"""

from .joint import (
    adaptation_efficiency,
    algorithm_migration,
    compute_efficiency,
    structural_robustness,
    z3_fixed_weights,
)

__all__ = [
    # Joint architecture experiments
    "adaptation_efficiency",
    "algorithm_migration",
    "compute_efficiency",
    "structural_robustness",
    "z3_fixed_weights",
]
