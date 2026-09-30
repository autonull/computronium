"""Domain data seeding for experiment registries (WP2 — Gate 1/2 outcomes).

This module populates all registries with the authoritative domain data
from the six implementations' hyperparameter union (Appendix IV),
policy catalog, stage definitions, and capability inventory.
"""

from __future__ import annotations

from typing import Any

from computronium.experiment.execution.stage import STAGE_SPECS as EXEC_STAGE_SPECS
from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CONSTRAINTS_REGISTRY,
    OBJECTIVES_REGISTRY,
    POLICIES_REGISTRY,
    PRIORS_REGISTRY,
    STAGES_REGISTRY,
    CapabilityKind,
    CapabilitySpec,
    ConstraintSpec,
    ObjectiveSpec,
    PolicyKind,
    PolicySpec,
    PriorSpec,
    StageSpec,
    register_capability,
    register_constraint,
    register_objective,
    register_policy,
    register_prior,
    register_stage,
)

# =============================================================================
# OBJECTIVES — Gate 1/2: from six implementations' target metrics
# =============================================================================

OBJECTIVES = [
    ObjectiveSpec(
        name="validation_accuracy",
        description="Validation accuracy (primary metric for classification tasks)",
        direction="maximize",
    ),
    ObjectiveSpec(
        name="test_accuracy",
        description="Test accuracy (held-out evaluation)",
        direction="maximize",
    ),
    ObjectiveSpec(
        name="validation_loss",
        description="Validation loss (primary metric for regression/language tasks)",
        direction="minimize",
    ),
    ObjectiveSpec(
        name="training_time",
        description="Wall-clock training time per epoch",
        direction="minimize",
    ),
    ObjectiveSpec(
        name="memory_usage",
        description="Peak GPU memory usage",
        direction="minimize",
    ),
    ObjectiveSpec(
        name="convergence_steps",
        description="Number of steps to reach convergence threshold",
        direction="minimize",
    ),
    ObjectiveSpec(
        name="energy_efficiency",
        description="Performance per joule (accuracy / energy)",
        direction="maximize",
    ),
    ObjectiveSpec(
        name="generalization_gap",
        description="Train-validation gap (smaller is better)",
        direction="minimize",
    ),
]


# =============================================================================
# CONSTRAINTS — Gate 1/2: from SystemConfig.validate(), task fences, apply_constraints
# =============================================================================

CONSTRAINTS = [
    # Void constraints (logical infeasibility — globally suppressive)
    ConstraintSpec(
        name="substrate_geometry_compatibility",
        kind="void",
        description="Digital substrate incompatible with analog-only geometries",
        params={"incompatible_pairs": [("Digital", "Analog")]},
    ),
    ConstraintSpec(
        name="dynamics_plasticity_compatibility",
        kind="void",
        description="Instantaneous dynamics cannot use fast-weight plasticity",
        params={"incompatible_pairs": [("Instantaneous", "FastWeightPlasticity")]},
    ),
    ConstraintSpec(
        name="credit_update_compatibility",
        kind="void",
        description="Backprop credit requires Euclidean or compatible update rule",
        params={
            "required_updates": {"Backprop": ["Euclidean", "Muon", "NaturalGradient"]}
        },
    ),
    ConstraintSpec(
        name="max_hidden_dim",
        kind="void",
        description="Hidden dimension exceeds hardware limits",
        params={"max_hidden": 8192},
    ),
    ConstraintSpec(
        name="max_layers",
        kind="void",
        description="Layer count exceeds hardware limits",
        params={"max_layers": 64},
    ),
    ConstraintSpec(
        name="max_steps",
        kind="void",
        description="Settling steps exceed budget",
        params={"max_steps": 1000},
    ),
    # Hard constraints (enforced at S4/S6 — resource/budget limits)
    ConstraintSpec(
        name="gpu_memory_budget",
        kind="hard",
        description="Model must fit in GPU memory",
        params={"max_gpu_memory_gb": 80},
    ),
    ConstraintSpec(
        name="training_time_budget",
        kind="hard",
        description="Training must complete within time budget",
        params={"max_hours": 24},
    ),
    ConstraintSpec(
        name="fidelity_schedule_consistency",
        kind="hard",
        description="L2 fidelity requires n_seeds >= 5",
        params={"min_seeds_for_L2": 5},
    ),
    # Soft constraints (preferences — encoded in priors, not here)
    ConstraintSpec(
        name="prefer_digital_substrate",
        kind="soft",
        description="Prefer digital substrate for baseline comparability",
        params={},
    ),
]


# =============================================================================
# PRIORS — Gate 1/2: ruler-LR table + step-size overrides (Appendix IV + §13.2)
# =============================================================================

PRIORS = [
    # Ruler learning rate priors (from 11 tasks)
    PriorSpec(
        name="lr_ruler_mnist",
        distribution="log_uniform",
        params={"low": 1e-4, "high": 1e-1},
        description="Ruler LR prior for MNIST",
    ),
    PriorSpec(
        name="lr_ruler_cifar10",
        distribution="log_uniform",
        params={"low": 1e-4, "high": 1e-1},
        description="Ruler LR prior for CIFAR-10",
    ),
    PriorSpec(
        name="lr_ruler_cifar100",
        distribution="log_uniform",
        params={"low": 1e-4, "high": 1e-1},
        description="Ruler LR prior for CIFAR-100",
    ),
    PriorSpec(
        name="lr_ruler_imagenet",
        distribution="log_uniform",
        params={"low": 1e-5, "high": 1e-2},
        description="Ruler LR prior for ImageNet",
    ),
    PriorSpec(
        name="lr_ruler_sst2",
        distribution="log_uniform",
        params={"low": 1e-5, "high": 1e-2},
        description="Ruler LR prior for SST-2",
    ),
    PriorSpec(
        name="lr_ruler_squad",
        distribution="log_uniform",
        params={"low": 1e-5, "high": 1e-2},
        description="Ruler LR prior for SQuAD",
    ),
    PriorSpec(
        name="lr_ruler_wikitext2",
        distribution="log_uniform",
        params={"low": 1e-5, "high": 1e-2},
        description="Ruler LR prior for WikiText-2",
    ),
    PriorSpec(
        name="lr_ruler_ptb",
        distribution="log_uniform",
        params={"low": 1e-5, "high": 1e-2},
        description="Ruler LR prior for PTB",
    ),
    PriorSpec(
        name="lr_ruler_copyshake",
        distribution="log_uniform",
        params={"low": 1e-4, "high": 1e-1},
        description="Ruler LR prior for CopyShake",
    ),
    PriorSpec(
        name="lr_ruler_arithmetic",
        distribution="log_uniform",
        params={"low": 1e-4, "high": 1e-1},
        description="Ruler LR prior for Arithmetic",
    ),
    PriorSpec(
        name="lr_ruler_listops",
        distribution="log_uniform",
        params={"low": 1e-4, "high": 1e-1},
        description="Ruler LR prior for ListOps",
    ),
    # Step-size override priors (28 dynamics×credit combos)
    PriorSpec(
        name="step_size_energy_minimization_backprop",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for EnergyMinimization × Backprop",
    ),
    PriorSpec(
        name="step_size_energy_minimization_fa",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for EnergyMinimization × FeedbackAlignment",
    ),
    PriorSpec(
        name="step_size_predictive_settling_backprop",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for PredictiveSettling × Backprop",
    ),
    PriorSpec(
        name="step_size_predictive_settling_fa",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for PredictiveSettling × FeedbackAlignment",
    ),
    PriorSpec(
        name="step_size_error_predictive_coding_backprop",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for ErrorPredictiveCoding × Backprop",
    ),
    PriorSpec(
        name="step_size_error_predictive_coding_fa",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for ErrorPredictiveCoding × FeedbackAlignment",
    ),
    PriorSpec(
        name="step_size_spike_integration_backprop",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for SpikeIntegration × Backprop",
    ),
    PriorSpec(
        name="step_size_instantaneous_backprop",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for Instantaneous × Backprop",
    ),
    PriorSpec(
        name="step_size_diffusion_backprop",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for Diffusion × Backprop",
    ),
    PriorSpec(
        name="step_size_lazy_backprop",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for Lazy × Backprop",
    ),
    PriorSpec(
        name="step_size_pc_alm_backprop",
        distribution="log_uniform",
        params={"low": 1e-3, "high": 1.0},
        description="Step size prior for PC-ALM × Backprop",
    ),
    # Dynamics-specific step-size priors (2 dynamics)
    PriorSpec(
        name="step_size_energy_minimization",
        distribution="log_uniform",
        params={"low": 1e-2, "high": 0.5},
        description="Dynamics-level step size prior for EnergyMinimization",
    ),
    PriorSpec(
        name="step_size_predictive_settling",
        distribution="log_uniform",
        params={"low": 1e-2, "high": 0.5},
        description="Dynamics-level step size prior for PredictiveSettling",
    ),
    # Gate 2 additions: batch_size, optimizer betas, apply_constraints
    PriorSpec(
        name="batch_size",
        distribution="categorical",
        params={"choices": [32, 64, 128, 256, 512]},
        description="Batch size prior (Gate 2 addition)",
    ),
    PriorSpec(
        name="adam_beta1",
        distribution="uniform",
        params={"low": 0.8, "high": 0.99},
        description="Adam beta1 prior (Gate 2 addition)",
    ),
    PriorSpec(
        name="adam_beta2",
        distribution="uniform",
        params={"low": 0.99, "high": 0.9999},
        description="Adam beta2 prior (Gate 2 addition)",
    ),
    PriorSpec(
        name="muon_momentum",
        distribution="uniform",
        params={"low": 0.8, "high": 0.99},
        description="Muon momentum prior (Gate 2 addition)",
    ),
]


# =============================================================================
# POLICIES — Gate 1/2: eight-policy catalog (abc3 §5.3)
# =============================================================================

POLICIES = [
    PolicySpec(
        name="stratified_random",
        kind=PolicyKind.STRATIFIED_RANDOM,
        description="Stratified random sampling across 6 axes for coverage",
        params={"per_stratum": 50},
    ),
    PolicySpec(
        name="round_robin_grid",
        kind=PolicyKind.ROUND_ROBIN_GRID,
        description="Round-robin grid traversal for systematic enumeration",
        params={},
    ),
    PolicySpec(
        name="uniform_random",
        kind=PolicyKind.UNIFORM_RANDOM,
        description="Uniform random sampling over all candidates",
        params={},
    ),
    PolicySpec(
        name="model_based_tpe",
        kind=PolicyKind.MODEL_BASED,
        description="Model-based optimization using Optuna TPE sampler",
        params={"sampler": "tpe", "n_startup_trials": 10},
    ),
    PolicySpec(
        name="model_based_gp",
        kind=PolicyKind.MODEL_BASED,
        description="Model-based optimization using Optuna GP sampler",
        params={"sampler": "gp", "n_startup_trials": 10},
    ),
    PolicySpec(
        name="evolution",
        kind=PolicyKind.EVOLUTION,
        description="Evolutionary search with mutation and crossover",
        params={"population_size": 20, "mutation_rate": 0.1, "crossover_rate": 0.5},
    ),
    PolicySpec(
        name="synthesis",
        kind=PolicyKind.SYNTHESIS,
        description="Synthesis of multiple policies with weighted combination",
        params={"weights": [1.0, 1.0, 1.0, 1.0]},
    ),
    PolicySpec(
        name="strategy_progression",
        kind=PolicyKind.STRATEGY_PROGRESSION,
        description="Progressive strategy: exploration → exploitation → refinement",
        params={},
    ),
    PolicySpec(
        name="trainer_driven",
        kind=PolicyKind.TRAINER_DRIVEN,
        description="Trainer-driven proposals from external learned policy",
        params={},
    ),
]


# =============================================================================
# STAGES — S1-S11 pipeline stages (abc3 §5.2)
# =============================================================================


# Convert execution StageSpec to registry StageSpec
def _convert_stage_spec(exec_stage: Any) -> StageSpec:
    """Convert execution.stage.StageSpec to schema.registries.StageSpec."""
    return StageSpec(
        stage_id=exec_stage.stage_id,
        name=exec_stage.name,
        description=exec_stage.description,
        required_fidelity=exec_stage.required_fidelity,
        min_n_seeds=exec_stage.min_n_seeds,
        gate=exec_stage.gate,
    )


# Import STAGE_SPECS after defining conversion

STAGES = [_convert_stage_spec(s) for s in EXEC_STAGE_SPECS]


# =============================================================================
# CAPABILITIES — Gate 1/2: capability registry for conformance (abc3 §9.3)
# =============================================================================

CAPABILITIES = [
    # Core capabilities (C1-C20)
    CapabilitySpec(
        capability_id="C1",
        kind=CapabilityKind.CORE,
        name="Six-axis coordinate space",
        description="Full Substrate×Geometry×Dynamics×Plasticity×Credit×Update coordinate space",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C2",
        kind=CapabilityKind.CORE,
        name="Unified record schema",
        description="Single record schema with four identity sections and three identity keys",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C3",
        kind=CapabilityKind.CORE,
        name="Content-addressed records",
        description="Records identified by content hash (record_id)",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C4",
        kind=CapabilityKind.CORE,
        name="Measurement key deduplication",
        description="Unique measurement_key prevents duplicate evaluations",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C5",
        kind=CapabilityKind.CORE,
        name="Cell key grouping",
        description="cell_key groups repeated evaluations of same coordinate",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C6",
        kind=CapabilityKind.CORE,
        name="Schema versioning",
        description="Append-only schema evolution with UnknownField preservation",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C7",
        kind=CapabilityKind.CORE,
        name="Legality engine",
        description="Predicate-based constraint engine with void/defect classification",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C8",
        kind=CapabilityKind.CORE,
        name="S1-S11 pipeline",
        description="Eleven-stage pipeline with wrapper obligations",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C9",
        kind=CapabilityKind.CORE,
        name="Eight-policy catalog",
        description="StratifiedRandom, RoundRobinGrid, UniformRandom, ModelBased, Evolution, Synthesis, StrategyProgression, TrainerDriven",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C10",
        kind=CapabilityKind.CORE,
        name="Evidence-driven allocation",
        description="Non-uniform compute allocation with divergence/stagnation detection",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C11",
        kind=CapabilityKind.CORE,
        name="Replay and resume",
        description="Deterministic replay via replay_hash; resume via measurement_key",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C12",
        kind=CapabilityKind.CORE,
        name="Three-tier status model",
        description="Observations, Assessments (procedure-versioned), Derived Claims",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C13",
        kind=CapabilityKind.CORE,
        name="Claim eligibility predicates",
        description="Pure query predicates for claim_eligible, promoted, beats_baseline",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C14",
        kind=CapabilityKind.CORE,
        name="Failure intelligence",
        description="FailureCause taxonomy, clustering, reproducer emission",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C15",
        kind=CapabilityKind.CORE,
        name="Unified artifact storage",
        description="Atomic record+artifact transactions in DuckDB",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C16",
        kind=CapabilityKind.CORE,
        name="Vector retrieval",
        description="Brute-force cosine/dot + optional HNSW via vss",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C17",
        kind=CapabilityKind.CORE,
        name="Prior registry",
        description="Ruler LR + step-size overrides as PriorSpec data",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C18",
        kind=CapabilityKind.CORE,
        name="Surrogate policy wrapper",
        description="EI/EHVI/UCB/PI/LOG_EI over any base Policy",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C19",
        kind=CapabilityKind.CORE,
        name="I(C,U) metamodel",
        description="Input-conditional uncertainty metamodel with leakage guard",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C20",
        kind=CapabilityKind.CORE,
        name="Reasoning records",
        description="Hypothesis/literature records with provenance linkage",
        required=True,
    ),
    # Acceleration capabilities
    CapabilitySpec(
        capability_id="C21",
        kind=CapabilityKind.ACCELERATION,
        name="torch.compile settle loop",
        description="Compiled settle loop for digital substrate (2x speedup)",
        required=False,
    ),
    CapabilitySpec(
        capability_id="C22",
        kind=CapabilityKind.ACCELERATION,
        name="Gradient checkpointing",
        description="Memory-compute tradeoff for deep settling",
        required=False,
    ),
    CapabilitySpec(
        capability_id="C23",
        kind=CapabilityKind.ACCELERATION,
        name="Gain control homeostasis",
        description="μPC-style unit RMS and spectral renormalization",
        required=False,
    ),
    # Scaling capabilities
    CapabilitySpec(
        capability_id="C24",
        kind=CapabilityKind.SCALING,
        name="Multiprocess backend",
        description="Parallel evaluation via multiprocessing",
        required=False,
    ),
    CapabilitySpec(
        capability_id="C25",
        kind=CapabilityKind.SCALING,
        name="Async orchestration",
        description="asyncio.TaskGroup for concurrent evaluation",
        required=False,
    ),
    # Reproducibility capabilities
    CapabilitySpec(
        capability_id="C26",
        kind=CapabilityKind.REPRODUCIBILITY,
        name="Computational reproducibility",
        description="Same env reproduces numerics within tolerance",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C27",
        kind=CapabilityKind.REPRODUCIBILITY,
        name="Scientific reproducibility",
        description="Independent env reproduces reported effect",
        required=False,
    ),
    # Governance capabilities
    CapabilitySpec(
        capability_id="C28",
        kind=CapabilityKind.GOVERNANCE,
        name="Assessment procedure registry",
        description="Content-addressed immutable assessment procedures",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C29",
        kind=CapabilityKind.GOVERNANCE,
        name="Matched-cost comparison guard",
        description="Refuses unmatched budget tier/hardware class comparisons",
        required=True,
    ),
    CapabilitySpec(
        capability_id="C30",
        kind=CapabilityKind.GOVERNANCE,
        name="I(C,U) leakage audit",
        description="Periodic calibration audit for bounded degradation",
        required=True,
    ),
    # Learning capabilities
    CapabilitySpec(
        capability_id="C31",
        kind=CapabilityKind.LEARNING,
        name="Surrogate-driven acquisition",
        description="EI/EHVI acquisition functions for efficient search",
        required=False,
    ),
    CapabilitySpec(
        capability_id="C32",
        kind=CapabilityKind.LEARNING,
        name="Cross-task transfer",
        description="Transfer learning with explicit provenance",
        required=False,
    ),
]


# =============================================================================
# Registration functions
# =============================================================================


def seed_all_registries() -> None:
    """Seed all registries with Gate 1/2 domain data.

    Idempotent: clears registries before seeding.
    """
    # Clear registries first (idempotent)
    OBJECTIVES_REGISTRY.clear()
    CONSTRAINTS_REGISTRY.clear()
    PRIORS_REGISTRY.clear()
    POLICIES_REGISTRY.clear()
    STAGES_REGISTRY.clear()
    CAPABILITIES_REGISTRY.clear()

    # Objectives
    for obj in OBJECTIVES:
        register_objective(obj)

    # Constraints
    for constraint in CONSTRAINTS:
        register_constraint(constraint)

    # Priors
    for prior in PRIORS:
        register_prior(prior)

    # Policies
    for policy in POLICIES:
        register_policy(policy)

    # Stages
    for stage in STAGES:
        register_stage(stage)

    # Capabilities
    for cap in CAPABILITIES:
        register_capability(cap)


def verify_registry_completeness() -> dict[str, int]:
    """Verify all registries have expected counts.

    Returns:
        Dictionary with registry names and their entry counts.
    """
    return {
        "objectives": len(OBJECTIVES_REGISTRY),
        "constraints": len(CONSTRAINTS_REGISTRY),
        "priors": len(PRIORS_REGISTRY),
        "policies": len(POLICIES_REGISTRY),
        "stages": len(STAGES_REGISTRY),
        "capabilities": len(CAPABILITIES_REGISTRY),
    }


__all__ = [
    "CAPABILITIES",
    "CONSTRAINTS",
    "OBJECTIVES",
    "POLICIES",
    "PRIORS",
    "seed_all_registries",
    "verify_registry_completeness",
]
