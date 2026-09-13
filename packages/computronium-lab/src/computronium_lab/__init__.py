"""computronium_lab — one-line composition, training, comparison, reporting.

High-level API over the Computronium 6-axis ontology. Wraps existing
validated factories only; CEEC evidence recording is optional and off by
default.
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
from computronium_lab.campaign import (
    CampaignReport,
    MechanismBelief,
    ledger_audit,
    promote_mechanism,
    run_campaign,
)
from computronium_lab.deployment import (
    EnergyEstimate,
    ExportResult,
    SubstrateReport,
    compile_substrate,
    estimate_energy,
    export_system,
    serve_system,
    substrate_report,
)
from computronium_lab.ecosystem import (
    BenchmarkReport,
    BenchmarkRow,
    HuggingFaceCallback,
    LightningStabilityCallback,
    report_json,
    run_benchmark,
)
from computronium_lab.lab import ComparisonResult, Lab
from computronium_lab.presets import PRESETS
from computronium_lab.recipes import RECIPES, build_recipe
from computronium_lab.synthesis import (
    Constraints,
    ExplorationBudgetExhausted,
    ProblemSpec,
    SynthesisResult,
    ViabilityModel,
    explore,
    synthesize,
)
from computronium_lab.training import (
    DeterminismSeal,
    StabilityCertificate,
    StabilityGuardKill,
    TrainingResult,
    TrainOptions,
)

__all__ = [
    "PRESETS",
    "RECIPES",
    "AdaptationMode",
    "AdaptationResult",
    "BenchmarkReport",
    "BenchmarkRow",
    "CampaignReport",
    "ComparisonResult",
    "Constraints",
    "DeterminismSeal",
    "EnergyEstimate",
    "ExplorationBudgetExhausted",
    "ExportResult",
    "HuggingFaceCallback",
    "Lab",
    "LightningStabilityCallback",
    "MechanismBelief",
    "ProblemSpec",
    "PsiProgram",
    "PsiStep",
    "StabilityCertificate",
    "StabilityGuardKill",
    "SubstrateReport",
    "SynthesisResult",
    "TaskBoundary",
    "TaskBoundaryDetector",
    "ThetaInvarianceProof",
    "TrainOptions",
    "TrainingResult",
    "ViabilityModel",
    "Z3Selection",
    "adapt",
    "build_recipe",
    "compile_substrate",
    "estimate_energy",
    "explore",
    "export_system",
    "ledger_audit",
    "probe_campaign",
    "promote_mechanism",
    "report_json",
    "run_benchmark",
    "run_campaign",
    "select_z3_operator",
    "serve_system",
    "substrate_report",
    "synthesize",
]
