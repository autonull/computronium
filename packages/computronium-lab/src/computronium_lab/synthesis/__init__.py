"""Synthesis layer (TODO23 Phase 1): ProblemSpec → validated mechanism."""

from __future__ import annotations

from computronium_lab.synthesis.engine import (
    ExplorationBudgetExhausted,
    ParetoOption,
    SynthesisResult,
    explore,
    filter_catalog,
    synthesize,
)
from computronium_lab.synthesis.predictor import (
    MechanismFeatures,
    ViabilityModel,
)
from computronium_lab.synthesis.spec import Constraints, ProblemSpec

__all__ = [
    "Constraints",
    "ExplorationBudgetExhausted",
    "MechanismFeatures",
    "ParetoOption",
    "ProblemSpec",
    "SynthesisResult",
    "ViabilityModel",
    "explore",
    "filter_catalog",
    "synthesize",
]
