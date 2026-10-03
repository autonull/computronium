"""computronium_lab — one-line composition, training, comparison, reporting.

High-level API over the Computronium 6-axis ontology. Wraps existing
validated factories only; CEEC evidence recording is optional and off by
default.

Retired modules (2026-10-02, R78): presets, recipes, campaign, deployment,
ecosystem, sequential, state_prediction, research/, ceec_profile.
See USAGE.md for census and retirement records.
"""

from __future__ import annotations

from computronium_lab.adaptation import (
    AdaptationMode,
    AdaptationResult,
    PsiProgram,
    PsiStep,
    TaskBoundary,
    TaskBoundaryDetector,
    ThetaInvarianceProof,
    Z3Selection,
    adapt,
    probe_campaign,
    select_z3_operator,
)
from computronium_lab.lab import ComparisonResult, Lab
from computronium_lab.synthesis import (
    Constraints,
    ExplorationBudgetExhausted,
    ProblemSpec,
    SynthesisResult,
    ViabilityModel,
    explore,
    synthesize,
)
from computronium_lab.synthesis.engine import register_objective
from computronium_lab.training import (
    DeterminismSeal,
    StabilityCertificate,
    StabilityGuardKill,
    TrainingResult,
    TrainOptions,
)

__all__ = [
    "AdaptationMode",
    "AdaptationResult",
    "ComparisonResult",
    "Constraints",
    "DeterminismSeal",
    "ExplorationBudgetExhausted",
    "Lab",
    "ProblemSpec",
    "PsiProgram",
    "PsiStep",
    "StabilityCertificate",
    "StabilityGuardKill",
    "SynthesisResult",
    "TaskBoundary",
    "TaskBoundaryDetector",
    "ThetaInvarianceProof",
    "TrainOptions",
    "TrainingResult",
    "ViabilityModel",
    "Z3Selection",
    "adapt",
    "explore",
    "probe_campaign",
    "register_objective",
    "select_z3_operator",
    "synthesize",
]
