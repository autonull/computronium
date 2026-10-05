"""Domain data seeding for experiment registries (WP2 — Gate 1/2 outcomes).

This module populates all registries with the authoritative domain data
from the six implementations' hyperparameter union (Appendix IV),
policy catalog, stage definitions, and capability inventory.
"""

from __future__ import annotations

import inspect
from dataclasses import replace
from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

from computronium.experiment.execution.stage import STAGE_SPECS as EXEC_STAGE_SPECS
from computronium.experiment.legality.dsl import (
    and_,
    const,
    eq,
    ge,
    gt,
    has_key,
    implies,
    in_,
    le,
    mul,
    not_,
    not_in,
    or_,
    var,
)
from computronium.experiment.schema.axis import (
    AXES_REGISTRIES,
    AxisKind,
    AxisSpec,
    Domain,
    HyperparameterSpec,
    Scale,
    StructuralAxis,
    register_axis_spec,
)
from computronium.experiment.schema.metrics import MEASURED_OBJECTIVES
from computronium.experiment.schema.registries import (
    CAPABILITIES_REGISTRY,
    CONSTRAINTS_REGISTRY,
    OBJECTIVES_REGISTRY,
    PARAM_BUDGET_TOLERANCE,
    POLICIES_REGISTRY,
    PRIORS_REGISTRY,
    STAGES_REGISTRY,
    CapabilityKind,
    CapabilitySpec,
    CapabilityStatus,
    ConstraintKind,
    ConstraintSpec,
    ObjectiveSpec,
    PolicyKind,
    PolicySpec,
    PriorSpec,
    ProofKind,
    StageSpec,
    register_capability,
    register_constraint,
    register_objective,
    register_policy,
    register_prior,
    register_stage,
)

# =============================================================================
# AXIS PRIMITIVES — Seed AXES_REGISTRIES with AxisSpec for each primitive
# Required for codegen (WP11.2) - listings, validators, stubs, flag tables
# Sources: primitives.ALL_PRIMITIVES (primitive ids per axis) +
# config-class hyperparameters() for availability/topology params.
# =============================================================================

# Substrate primitives: no primitive-specific topology; all share the
# SubstrateConfig surface. device/precision are structural (dataset/runtime
# determined), searchable substrate params carry availability predicates.
_SUBSTRATE_PRIMS: list[tuple[str, str]] = [
    ("digital", "Digital substrate: exact arithmetic, full precision"),
    ("analog", "Analog substrate: continuous-valued physical state"),
    ("memristive", "Memristive substrate: conductance, IR-drop, noise"),
    ("neuromorphic", "Neuromorphic substrate: asynchronous spike events"),
    ("optical", "Photonic substrate: phase/amplitude modulation"),
    ("quantum", "Quantum substrate: unitary gate simulation"),
    ("complex", "Complex-valued substrate"),
    ("sparse", "Sparse substrate: sparsity-masked state"),
    ("ternary", "Ternary substrate: weights in {-alpha, 0, +alpha}"),
]

# Geometry primitives: topology params are fixed by the primitive choice
# (Appendix C: only hidden_dim/num_layers/cube_size/init_scale are searched).
_GEOMETRY_PRIMS: list[tuple[str, str, tuple[str, ...]]] = [
    (
        "feedforward",
        "Feedforward DAG (MLP/CNN)",
        ("input_dim", "output_dim", "hidden_dim", "num_layers"),
    ),
    (
        "recurrent",
        "Recurrent attractor (Hopfield/EqProp)",
        ("input_dim", "output_dim", "hidden_dim", "num_layers"),
    ),
    (
        "causal_transformer",
        "Causal transformer with KV cache",
        ("input_dim", "output_dim", "hidden_dim", "num_heads", "seq_len"),
    ),
    (
        "tile",
        "TileNet modular tile mesh",
        ("input_dim", "output_dim", "neurons_per_tile", "tiles_per_layer"),
    ),
    (
        "tile_mesh",
        "TileNet mesh topology",
        ("input_dim", "output_dim", "neurons_per_tile", "tiles_per_layer"),
    ),
    (
        "conv",
        "Convolutional geometry",
        ("input_dim", "output_dim", "conv_channels", "kernel_size"),
    ),
    (
        "graph",
        "Arbitrary node-edge fabric (FabricPC)",
        ("input_dim", "output_dim", "hidden_dim"),
    ),
    ("attention", "Attention geometry", ("input_dim", "output_dim", "num_heads")),
    (
        "spatial_lattice",
        "3-D spatial lattice (neural_cube)",
        ("input_dim", "output_dim", "lattice_dims"),
    ),
    ("nca", "Neural cellular automaton fabric", ("input_dim", "output_dim", "grid_hw")),
    (
        "ntm",
        "Neural Turing Machine tape",
        ("input_dim", "output_dim", "mem_slots", "mem_width"),
    ),
]

# Dynamics primitives: settling-specific params become topology of the primitive
_DYNAMICS_PRIMS: list[tuple[str, str, tuple[str, ...]]] = [
    (
        "energy_minimization",
        "Equilibrium propagation energy minimization",
        ("max_steps", "convergence_threshold"),
    ),
    (
        "predictive_settling",
        "Predictive coding settling",
        ("max_steps", "convergence_threshold"),
    ),
    (
        "error_predictive_coding",
        "Error predictive coding",
        ("max_steps", "convergence_threshold"),
    ),
    ("spike_integration", "LIF/Izhikevich spike integration", ("max_steps",)),
    ("instantaneous", "Instantaneous pass (FF/Backprop)", ()),
    ("diffusion", "Continuous-time diffusion settling", ("max_steps",)),
    ("lazy", "Lazy/on-demand state dynamics", ()),
    ("pc_alm", "Augmented Lagrangian predictive coding", ("max_steps",)),
]

# Credit primitives: STDP/contrastive/feedback-specific params are structural
_CREDIT_PRIMS: list[tuple[str, str, tuple[str, ...]]] = [
    ("thermodynamic_contrast", "EqProp free/nudged contrast (Scellier-Bengio)", ()),
    ("random_projections", "Fixed random feedback (FA/DFA)", ("feedback_scale",)),
    ("local_goodness", "Forward-Forward / PEPITA goodness", ()),
    (
        "local_contrastive",
        "Local contrastive credit",
        ("ema_beta", "contrast_threshold", "contrast_objective"),
    ),
    (
        "temporal_trace",
        "Hebbian/STDP temporal trace",
        ("a_plus", "a_minus", "tau_pre", "tau_post"),
    ),
    ("target_inversion", "Target propagation inversion", ()),
    ("homeostatic", "Autonomous Lipschitz scaling", ()),
    ("pepita", "PEPITA input-modulation credit", ("feedback_scale",)),
    ("gradient", "Backprop gradient credit (ruler reference)", ()),
    ("pc_alm", "PC-ALM primal-dual credit", ()),
]

# Update primitives: rule-specific optimizer params are structural
_UPDATE_PRIMS: list[tuple[str, str, tuple[str, ...]]] = [
    ("euclidean", "SGD/Adam Euclidean update", ()),
    ("adam", "Adam adaptive moment", ("beta2", "eps")),
    ("local_adam", "Local Adam", ("beta2", "eps")),
    ("ortho_adam", "Orthogonal Adam", ("beta2", "eps", "ortho_lr")),
    (
        "riemannian_orthogonal",
        "Riemannian orthogonal update (Muon-family)",
        ("ortho_steps",),
    ),
    ("muon", "Muon update", ("ortho_steps", "momentum")),
    ("lion", "Lion optimizer", ("beta2", "eps")),
    ("spectral_constrained", "Spectral-norm constrained update", ("spectral_norm",)),
    ("mean_norm", "Mean-norm update", ()),
    (
        "elastic_consolidation",
        "EWC elastic consolidation",
        ("ewc_lambda", "fisher_damping"),
    ),
    ("natural_gradient", "Natural gradient (Fisher)", ("fisher_damping",)),
    ("role_split", "Role-split update", ()),
]

# Plasticity primitives: psi-specific dims are structural to the primitive
_PLASTICITY_PRIMS: list[tuple[str, str, tuple[str, ...]]] = [
    ("null", "Null plasticity (5-D slice)", ()),
    ("routing", "Routing plasticity: state-dependent gating", ("gate_dim",)),
    ("fast_weights", "Fast-weight episode-local memory", ("fast_weight_dim",)),
    ("substrate_coupled", "Physical substrate-coupled plasticity", ()),
    ("rule_state", "Rule-state plasticity (Z3)", ("num_operators",)),
    ("temporal_psi", "Trace-decayed supervised psi", ("trace_decay",)),
    (
        "conflict_adaptive",
        "Conflict-adaptive psi",
        ("trace_decay", "conflict_threshold"),
    ),
]


def _hyperparameter_spec(
    name: str, axis_name: str, kind: AxisKind
) -> HyperparameterSpec:
    """Build a HyperparameterSpec for a topology (structural) param.

    Topology params are fixed by the primitive choice; they carry a permissive
    domain because they are not searched — only recorded in AxisSpec.
    """
    defaults: dict[str, tuple[float, float, Scale]] = {
        "input_dim": (1, 8192, Scale.LINEAR),
        "output_dim": (1, 8192, Scale.LINEAR),
        "hidden_dim": (8, 4096, Scale.LOG),
        "num_layers": (1, 12, Scale.LINEAR),
        "num_heads": (1, 32, Scale.LINEAR),
        "seq_len": (16, 4096, Scale.LOG),
        "neurons_per_tile": (2, 64, Scale.LINEAR),
        "tiles_per_layer": (1, 8, Scale.LINEAR),
        "conv_channels": (4, 256, Scale.LINEAR),
        "kernel_size": (1, 7, Scale.LINEAR),
        "lattice_dims": (2, 32, Scale.LINEAR),
        "grid_hw": (4, 64, Scale.LINEAR),
        "mem_slots": (4, 128, Scale.LOG),
        "mem_width": (4, 128, Scale.LOG),
        "max_steps": (1, 200, Scale.LINEAR),
        "convergence_threshold": (1e-6, 0.01, Scale.LOG),
        "feedback_scale": (0.001, 10.0, Scale.LOG),
        "ema_beta": (0.9, 0.999, Scale.LINEAR),
        "contrast_threshold": (0.5, 10.0, Scale.LINEAR),
        "a_plus": (0.1, 5.0, Scale.LINEAR),
        "a_minus": (0.1, 5.0, Scale.LINEAR),
        "tau_pre": (0.1, 2.0, Scale.LINEAR),
        "tau_post": (0.1, 2.0, Scale.LINEAR),
        "beta2": (0.9, 0.9999, Scale.LINEAR),
        "eps": (1e-10, 1e-4, Scale.LOG),
        "ortho_lr": (1e-5, 1.0, Scale.LOG),
        "ortho_steps": (0, 10, Scale.LINEAR),
        "spectral_norm": (0.1, 10.0, Scale.LOG),
        "ewc_lambda": (0.1, 1e4, Scale.LOG),
        "fisher_damping": (1e-6, 1.0, Scale.LOG),
        "momentum": (0.0, 0.99, Scale.LINEAR),
        "gate_dim": (8, 512, Scale.LINEAR),
        "fast_weight_dim": (64, 2048, Scale.LOG),
        "num_operators": (2, 32, Scale.LINEAR),
        "trace_decay": (0.5, 1.0, Scale.LINEAR),
        "conflict_threshold": (0.1, 0.9, Scale.LINEAR),
    }
    if name in defaults:
        lo, hi, scale = defaults[name]
        return HyperparameterSpec(
            name=name,
            domain=Domain(lo=lo, hi=hi, scale=scale),
            axis_kind=kind,
            axis_name=axis_name,
        )
    return HyperparameterSpec(
        name=name,
        domain=Domain(members=("unknown",)),
        axis_kind=AxisKind.CATEGORICAL,
        axis_name=axis_name,
    )


type PrimitiveRow = tuple[str, str, tuple[str, ...]]


# Primitives the kernel registers but cannot honour, with the reason recorded
# (R78). An unavailable row is excluded from every space, so the run stops
# proposing cells it would only fail: ``nca`` composes and validates, then dies
# in ``NcaGeometry.step`` because the trainer hands a geometry the batch
# (``(B, F)``) rather than the state grid (``(B, C, H, W)``) its contract names.
# Restoring it needs a reshape and read-out in ``NcaGeometry.route``, which is a
# geometry feature rather than a config row.
_UNAVAILABLE: Final[Mapping[tuple[StructuralAxis, str], str]] = {
    (StructuralAxis.GEOMETRY, "nca"): (
        "NcaGeometry.step requires a (B, C, H, W) state grid; the kernel's "
        "trainer supplies a flattened batch, so every nca cell fails at "
        "runtime. Retired 2026-10-02 pending a route-level reshape."
    ),
}


def _axis_primitives() -> tuple[tuple[StructuralAxis, tuple[PrimitiveRow, ...]], ...]:
    """Every axis primitive with its description and structural topology params."""
    substrate: tuple[PrimitiveRow, ...] = tuple((n, d, ()) for n, d in _SUBSTRATE_PRIMS)
    geometry = tuple(_GEOMETRY_PRIMS)
    dynamics = tuple(_DYNAMICS_PRIMS)
    credit = tuple(_CREDIT_PRIMS)
    update = tuple(_UPDATE_PRIMS)
    plasticity = tuple(_PLASTICITY_PRIMS)
    return (
        (StructuralAxis.SUBSTRATE, substrate),
        (StructuralAxis.GEOMETRY, geometry),
        (StructuralAxis.DYNAMICS, dynamics),
        (StructuralAxis.PLASTICITY, plasticity),
        (StructuralAxis.CREDIT, credit),
        (StructuralAxis.UPDATE, update),
    )


def _accepted_params(axis: StructuralAxis, primitive: str) -> frozenset[str]:
    """The knob names a primitive's config factory accepts.

    Harvested once, here, so composition never reflects on a signature. Every
    factory mirrors its config dataclass, so a wide signature is not evidence of
    use; this is the narrower truth about which names a call may carry.
    """
    from computronium.experiment.schema.harvest import load_axis_config

    config_cls = load_axis_config(axis)
    factory = getattr(config_cls, primitive, None)
    if not callable(factory):
        return frozenset()
    return frozenset(inspect.signature(factory).parameters)


def _seed_axis_primitives() -> None:
    """Register one AxisSpec per primitive in AXES_REGISTRIES.

    Structural topology params are attached per primitive; searchable
    hyperparameters remain the harvest layer's concern (L2).
    """
    for axis, primitives in _axis_primitives():
        for name, description, topology in primitives:
            register_axis_spec(
                AxisSpec(
                    name=name,
                    axis_kind=axis,
                    description=description,
                    available=(axis, name) not in _UNAVAILABLE,
                    unavailable_reason=_UNAVAILABLE.get((axis, name)),
                    accepted_params=_accepted_params(axis, name),
                    topology_params=tuple(
                        _hyperparameter_spec(p, axis.value, AxisKind.STRUCTURAL)
                        for p in topology
                    ),
                )
            )


# =============================================================================
# OBJECTIVES — Gate 1/2: full Appendix B.7 union (~39 objectives)
# Task, cost, substrate, ruler-relative, stability, plasticity objectives
# Extended with weight, normalizer, axis_tag (L16)
#
# Whether a row is measurable is NOT decided here: `schema.metrics` owns that
# single declaration, and `_measured` stamps each row with the payload key that
# satisfies it or the reason no measurement produces it.
# =============================================================================


def _measured(objectives: list[ObjectiveSpec]) -> list[ObjectiveSpec]:
    """Stamp each objective with its measurement, or the reason it lacks one."""
    measured = list(MEASURED_OBJECTIVES)
    return [
        replace(
            objective,
            metric_key=MEASURED_OBJECTIVES[objective.name],
        )
        if objective.name in MEASURED_OBJECTIVES
        else replace(
            objective,
            unavailable_reason=(
                "registered ahead of measurement: the evaluator emits no payload "
                f"key for it. Measured objectives: {measured}"
            ),
        )
        for objective in objectives
    ]


OBJECTIVES = _measured([
    # Task objectives
    ObjectiveSpec(
        name="validation_accuracy",
        description="Validation accuracy (primary metric for classification tasks)",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="task",
    ),
    ObjectiveSpec(
        name="test_accuracy",
        description="Test accuracy (held-out evaluation)",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="task",
    ),
    ObjectiveSpec(
        name="validation_loss",
        description="Validation loss (primary metric for regression/language tasks)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="task",
    ),
    ObjectiveSpec(
        name="test_loss",
        description="Test loss (held-out evaluation)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="task",
    ),
    ObjectiveSpec(
        name="f1_score",
        description="F1 score for classification tasks",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="task",
    ),
    ObjectiveSpec(
        name="perplexity",
        description="Perplexity for language modeling tasks",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="task",
    ),
    ObjectiveSpec(
        name="bleu_score",
        description="BLEU score for translation/generation tasks",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="task",
    ),
    # Cost objectives
    ObjectiveSpec(
        name="training_time",
        description="Wall-clock training time per epoch",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="cost",
    ),
    ObjectiveSpec(
        name="walltime_total",
        description="Total wall-clock time for full training run",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="cost",
    ),
    ObjectiveSpec(
        name="memory_usage",
        description="Peak GPU memory usage",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="cost",
    ),
    ObjectiveSpec(
        name="param_count",
        description="Total parameter count",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="cost",
    ),
    ObjectiveSpec(
        name="flops",
        description="Floating-point operations per training step",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="cost",
    ),
    ObjectiveSpec(
        name="energy_per_step",
        description="Energy consumption per training step (joules)",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="cost",
    ),
    ObjectiveSpec(
        name="energy_per_mac",
        description="Energy per multiply-accumulate (joules): the substrate's efficiency",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="cost",
    ),
    ObjectiveSpec(
        name="macs_per_step",
        description="Multiply-accumulates per training step: the arithmetic the cell performs",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="cost",
    ),
    ObjectiveSpec(
        name="latency_ms",
        description="Inference latency in milliseconds",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="cost",
    ),
    # Substrate objectives
    ObjectiveSpec(
        name="spike_rate",
        description="Average spike rate (neuromorphic substrate)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="substrate",
    ),
    ObjectiveSpec(
        name="ir_drop_variance",
        description="IR drop variance (memristive substrate)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="substrate",
    ),
    ObjectiveSpec(
        name="phase_noise",
        description="Phase noise (photonic substrate)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="substrate",
    ),
    ObjectiveSpec(
        name="gate_fidelity",
        description="Gate fidelity (quantum substrate)",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="substrate",
    ),
    ObjectiveSpec(
        name="coherence_time",
        description="Coherence time (quantum substrate)",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="substrate",
    ),
    # Ruler-relative objectives (C1/R31: preserved per-axis)
    ObjectiveSpec(
        name="bp_deficit",
        description="Backprop ruler accuracy - measured accuracy (lower = closer to ruler)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="ruler",
    ),
    ObjectiveSpec(
        name="ruler_walltime_ratio",
        description="Cell walltime / ruler walltime (lower = faster than ruler)",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="ruler",
    ),
    ObjectiveSpec(
        name="ruler_energy_ratio",
        description="Cell energy / ruler energy (lower = more efficient than ruler)",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="ruler",
    ),
    ObjectiveSpec(
        name="ruler_param_ratio",
        description="Cell param_count / ruler param_count",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="ruler",
    ),
    # Stability objectives
    ObjectiveSpec(
        name="spectral_radius",
        description="Spectral radius ρ(J_F) of Jacobian (asymptotic stability margin)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="stability_margin",
        description="1 − ρ(J): how far the settle step is inside the unit circle",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="nonnormality",
        description="σ_max(J)/ρ(J): transient amplification per unit of contraction",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="drift_spectral_radius",
        description="ρ(f(h)-h): the network's own gain, with the relaxation step size divided out",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="drift_max_singular_value",
        description="σ_max of the drift operator: transient amplification of f(h)-h",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="contraction_rate",
        description="1 - eta*ρ(f(h)-h): the contraction linear theory predicts, not the measured ρ_step",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="max_singular_value",
        description="Maximum singular value σ_max(J_F) (transient amplification bound)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="lyapunov_exponent",
        description="Largest Lyapunov exponent (chaos indicator)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="hopfield_energy",
        description="Hopfield energy at convergence (energy_minimization, lazy, diffusion dynamics)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="pc_free_energy",
        description="Variational free energy at convergence (predictive_settling, error_predictive_coding dynamics)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="augmented_lagrangian",
        description="Augmented Lagrangian at convergence (pc_alm dynamics)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="spike_proxy_energy",
        description="Spike energy proxy (spike_integration dynamics; not a Lyapunov function)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="instantaneous_proxy_energy",
        description="Instantaneous energy proxy (instantaneous dynamics; negative log-likelihood or zero)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    # free_energy retained as alias for hopfield_energy (energy-based family only)
    ObjectiveSpec(
        name="free_energy",
        description="Free energy at convergence (energy-based dynamics; alias for hopfield_energy)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    ObjectiveSpec(
        name="settle_steps",
        description="Number of settle steps to convergence",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="stability",
    ),
    # Plasticity objectives
    ObjectiveSpec(
        name="psi_capacity",
        description="Plastic state capacity (ψ dimensionality)",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="plasticity",
    ),
    ObjectiveSpec(
        name="consolidation_cost",
        description="Compute cost of ψ→θ consolidation",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="plasticity",
    ),
    ObjectiveSpec(
        name="rewrite_rate",
        description="Rate of ψ rewriting (adaptation speed)",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="plasticity",
    ),
    ObjectiveSpec(
        name="stability_plasticity_ratio",
        description="ρ(J_F) / ψ_capacity (stability-plasticity trade-off)",
        direction="minimize",
        weight=1.0,
        normalizer="log",
        axis_tag="composite",
    ),
    ObjectiveSpec(
        name="credit_efficiency",
        description="Credit alignment / FLOPs (credit efficiency)",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="composite",
    ),
    ObjectiveSpec(
        name="convergence_steps",
        description="Number of steps to reach convergence threshold",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="task",
    ),
    ObjectiveSpec(
        name="energy_efficiency",
        description="Performance per joule (accuracy / energy)",
        direction="maximize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="cost",
    ),
    ObjectiveSpec(
        name="generalization_gap",
        description="Train-validation gap (smaller is better)",
        direction="minimize",
        weight=1.0,
        normalizer="minmax",
        axis_tag="task",
    ),
])


# =============================================================================
# CONSTRAINTS — Gate 1/2: from SystemConfig.validate(), task fences, apply_constraints
# Re-expressed as Expr predicates with machine-checkable proof kinds (L5)
# =============================================================================

CONSTRAINTS = [
    # Void constraints (logical infeasibility — globally suppressive at S4)
    # proof_kind: TYPE_MISMATCH | RESOURCE | LOGICAL
    ConstraintSpec(
        name="substrate_geometry_compatibility",
        kind=ConstraintKind.VOID,
        description="Digital substrate incompatible with analog-only geometries",
        predicate=not_(
            and_(
                eq(var("substrate"), const("digital")),
                in_(var("geometry"), const(["analog", "photonic", "quantum"])),
            )
        ),
        proof_kind=ProofKind.LOGICAL,
        origin="DECLARED",
    ),
    ConstraintSpec(
        name="dynamics_plasticity_compatibility",
        kind=ConstraintKind.VOID,
        description="Instantaneous dynamics cannot use fast-weight plasticity",
        predicate=not_(
            and_(
                eq(var("dynamics"), const("instantaneous")),
                eq(var("plasticity"), const("fast_weight")),
            )
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    ConstraintSpec(
        name="credit_update_compatibility",
        kind=ConstraintKind.VOID,
        description="Backprop credit requires Euclidean or compatible update rule",
        predicate=not_(
            and_(
                eq(var("credit"), const("backprop")),
                not_in(
                    var("update"),
                    const([
                        "euclidean",
                        "muon",
                        "natural_gradient",
                        "riemannian_orthogonal",
                    ]),
                ),
            )
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Geometry-Dynamics: recurrent geometry requires energy/PC-family/diffusion/instantaneous dynamics
    ConstraintSpec(
        name="recurrent_geometry_dynamics",
        kind=ConstraintKind.VOID,
        description="Recurrent geometry requires energy-based, PC-family, diffusion, or instantaneous dynamics",
        predicate=or_(
            not_(in_(var("geometry"), const(["recurrent", "recurrent_attractor"]))),
            in_(
                var("dynamics"),
                const([
                    "energy_minimization",
                    "predictive_settling",
                    "error_predictive_coding",
                    "pc_alm",
                    "diffusion",
                    "instantaneous",
                ]),
            ),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Geometry-Dynamics: non-layered geometries cannot host settling dynamics
    ConstraintSpec(
        name="nonlayered_geometry_dynamics",
        kind=ConstraintKind.VOID,
        description="Non-layered geometries (attention, spatial_lattice, graph, conv, nca, ntm, causal_transformer) require instantaneous dynamics",
        predicate=or_(
            eq(var("dynamics"), const("instantaneous")),
            not_(
                in_(
                    var("geometry"),
                    const([
                        "attention",
                        "spatial_lattice",
                        "graph",
                        "conv",
                        "nca",
                        "ntm",
                        "causal_transformer",
                    ]),
                )
            ),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Geometry-Dynamics: tile/tile_mesh requires compatible dynamics
    ConstraintSpec(
        name="tile_mesh_dynamics",
        kind=ConstraintKind.VOID,
        description="Tile mesh geometry requires energy_minimization, pc_alm, or instantaneous dynamics",
        predicate=or_(
            not_(in_(var("geometry"), const(["tile_mesh", "tile"]))),
            in_(
                var("dynamics"),
                const(["energy_minimization", "pc_alm", "instantaneous"]),
            ),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Geometry-Dynamics: NCA/NTM requires instantaneous dynamics
    ConstraintSpec(
        name="nca_ntm_geometry",
        kind=ConstraintKind.VOID,
        description="NCA/NTM geometries require instantaneous dynamics",
        predicate=or_(
            eq(var("dynamics"), const("instantaneous")),
            not_(in_(var("geometry"), const(["nca", "ntm"]))),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Dynamics-Credit: diffusion blocks gradient/backprop
    ConstraintSpec(
        name="diffusion_dynamics_credit",
        kind=ConstraintKind.VOID,
        description="Diffusion dynamics produce non-differentiable state; gradient/backprop credit unsupported",
        predicate=not_(
            and_(
                eq(var("dynamics"), const("diffusion")),
                in_(var("credit"), const(["gradient", "backprop"])),
            )
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Dynamics-Geometry: diffusion requires recurrent geometry
    ConstraintSpec(
        name="diffusion_dynamics_geometry",
        kind=ConstraintKind.VOID,
        description="Diffusion dynamics requires recurrent geometry",
        predicate=or_(
            not_(eq(var("dynamics"), const("diffusion"))),
            in_(var("geometry"), const(["recurrent", "recurrent_attractor"])),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Dynamics-Credit: spike_integration needs temporal trace or target inversion credit
    ConstraintSpec(
        name="spike_integration_credit",
        kind=ConstraintKind.VOID,
        description="Spike integration dynamics requires temporal trace or target inversion credit",
        predicate=or_(
            not_(eq(var("dynamics"), const("spike_integration"))),
            in_(
                var("credit"),
                const(["temporal_trace", "spiking", "target_inversion", "target_prop"]),
            ),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Dynamics-Credit: predictive settling needs compatible credit
    ConstraintSpec(
        name="predictive_settling_credit",
        kind=ConstraintKind.VOID,
        description="Predictive settling/error predictive coding dynamics requires thermodynamic_contrast, local_goodness, or forward_only credit",
        predicate=or_(
            not_(
                in_(
                    var("dynamics"),
                    const(["predictive_settling", "error_predictive_coding"]),
                )
            ),
            in_(
                var("credit"),
                const([
                    "thermodynamic_contrast",
                    "equilibrium",
                    "local_goodness",
                    "forward_only",
                ]),
            ),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Dynamics-Credit-Geometry: pc_alm needs pc_alm/thermodynamic_contrast credit AND layered geometry
    ConstraintSpec(
        name="pc_alm_dynamics",
        kind=ConstraintKind.VOID,
        description="PC-ALM dynamics requires pc_alm or thermodynamic_contrast credit and layered geometry",
        predicate=and_(
            or_(
                not_(eq(var("dynamics"), const("pc_alm"))),
                in_(var("credit"), const(["pc_alm", "thermodynamic_contrast"])),
            ),
            or_(
                not_(eq(var("dynamics"), const("pc_alm"))),
                in_(var("geometry"), const(["feedforward", "recurrent", "tile_mesh"])),
            ),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Geometry: residual connections only on feedforward
    ConstraintSpec(
        name="residual_connections",
        kind=ConstraintKind.VOID,
        description="Residual connections (residual=True) require feedforward geometry",
        predicate=or_(
            not_(has_key(var("params"), const("residual"))),
            eq(var("geometry"), const("feedforward")),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Credit-Dynamics: thermodynamic contrast needs energy/PC-family/lazy/pc_alm dynamics
    ConstraintSpec(
        name="thermodynamic_contrast_dynamics",
        kind=ConstraintKind.VOID,
        description="Thermodynamic contrast/equilibrium credit requires energy-based or PC-family dynamics",
        predicate=or_(
            not_(in_(var("credit"), const(["thermodynamic_contrast", "equilibrium"]))),
            in_(
                var("dynamics"),
                const([
                    "energy_minimization",
                    "predictive_settling",
                    "error_predictive_coding",
                    "lazy",
                    "pc_alm",
                ]),
            ),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Substrate-Dynamics: neuromorphic substrate needs temporal dynamics
    ConstraintSpec(
        name="neuromorphic_substrate_dynamics",
        kind=ConstraintKind.VOID,
        description="Neuromorphic substrate requires temporal dynamics (spike_integration, energy_minimization, or diffusion)",
        predicate=or_(
            not_(eq(var("substrate"), const("neuromorphic"))),
            in_(
                var("dynamics"),
                const(["spike_integration", "energy_minimization", "diffusion"]),
            ),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Substrate-Dynamics: quantum substrate needs compatible dynamics
    ConstraintSpec(
        name="quantum_substrate_dynamics",
        kind=ConstraintKind.VOID,
        description="Quantum substrate requires energy_minimization, instantaneous, or diffusion dynamics",
        predicate=or_(
            not_(eq(var("substrate"), const("quantum"))),
            in_(
                var("dynamics"),
                const(["energy_minimization", "instantaneous", "diffusion"]),
            ),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Credit-Geometry: local contrastive needs feedforward geometry
    ConstraintSpec(
        name="local_contrastive_geometry",
        kind=ConstraintKind.VOID,
        description="Local contrastive/goodness/forward_only/pepita credit requires feedforward geometry",
        predicate=or_(
            not_(
                in_(
                    var("credit"),
                    const([
                        "local_goodness",
                        "forward_only",
                        "pepita",
                        "local_contrastive",
                    ]),
                )
            ),
            in_(var("geometry"), const(["feedforward", "feedforward_dag"])),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Credit-Geometry: attention geometry incompatible with certain credits
    ConstraintSpec(
        name="attention_geometry_compatibility",
        kind=ConstraintKind.VOID,
        description="Attention geometry incompatible with pepita, local_goodness, local_contrastive, forward_only credit",
        predicate=not_(
            and_(
                eq(var("geometry"), const("attention")),
                in_(
                    var("credit"),
                    const([
                        "pepita",
                        "local_goodness",
                        "local_contrastive",
                        "forward_only",
                    ]),
                ),
            )
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    # Credit: gradient/backprop with beta >= 1.0 has zero pseudo-gradient
    ConstraintSpec(
        name="gradient_credit_beta_clamp",
        kind=ConstraintKind.VOID,
        description="Gradient/backprop credit with beta >= 1.0 has zero pseudo-gradient",
        predicate=not_(
            and_(
                in_(var("credit"), const(["gradient", "backprop"])),
                ge(var("params.beta"), const(1.0)),
            )
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="DECLARED",
    ),
    ConstraintSpec(
        name="max_hidden_dim",
        kind=ConstraintKind.VOID,
        description="Hidden dimension exceeds hardware limits",
        predicate=le(var("params.hidden_dim"), const(8192)),
        proof_kind=ProofKind.RESOURCE,
        origin="DECLARED",
    ),
    ConstraintSpec(
        name="max_layers",
        kind=ConstraintKind.VOID,
        description="Layer count exceeds hardware limits",
        predicate=le(var("params.num_layers"), const(64)),
        proof_kind=ProofKind.RESOURCE,
        origin="DECLARED",
    ),
    ConstraintSpec(
        name="max_steps",
        kind=ConstraintKind.VOID,
        description="Settling steps exceed budget",
        predicate=le(var("params.max_steps"), const(1000)),
        proof_kind=ProofKind.RESOURCE,
        origin="DECLARED",
    ),
    # Task fence constraints (from TASK_COMPAT fences)
    ConstraintSpec(
        name="classification_requires_classifier_head",
        kind=ConstraintKind.VOID,
        description="Classification tasks require output_dim matching num_classes",
        predicate=or_(
            not_(eq(var("task"), const("classification"))),
            gt(var("output_dim"), const(1)),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="TASK_FENCE",
    ),
    ConstraintSpec(
        name="language_modeling_requires_causal",
        kind=ConstraintKind.VOID,
        description="Language modeling requires causal attention or recurrent geometry",
        predicate=or_(
            not_(eq(var("task"), const("language_modeling"))),
            in_(var("geometry"), const(["causal_transformer", "recurrent"])),
        ),
        proof_kind=ProofKind.TYPE_MISMATCH,
        origin="TASK_FENCE",
    ),
    # Hard constraints (enforced at S4/S6 — resource/budget limits)
    ConstraintSpec(
        name="gpu_memory_budget",
        kind=ConstraintKind.HARD,
        description="Model must fit in GPU memory",
        predicate=le(var("estimated_gpu_memory_gb"), var("max_gpu_memory_gb")),
        params={"max_gpu_memory_gb": 80},
        proof_kind=ProofKind.RESOURCE,
        origin="DECLARED",
    ),
    ConstraintSpec(
        name="training_time_budget",
        kind=ConstraintKind.HARD,
        description="Training must complete within time budget",
        predicate=le(var("estimated_hours"), var("max_hours")),
        params={"max_hours": 24},
        proof_kind=ProofKind.RESOURCE,
        origin="DECLARED",
    ),
    ConstraintSpec(
        name="fidelity_schedule_consistency",
        kind=ConstraintKind.HARD,
        description="L2 fidelity requires n_seeds >= 5",
        predicate=implies(
            eq(var("fidelity"), const("L2")), ge(var("n_seeds"), const(5))
        ),
        proof_kind=ProofKind.LOGICAL,
        origin="DECLARED",
    ),
    # Fairness constraints (R25: param-budget 25% tolerance)
    ConstraintSpec(
        name="param_budget_fairness",
        kind=ConstraintKind.FAIRNESS,
        description="Param budget tolerance 25% for fair comparison across axes",
        predicate=le(
            var("param_count"),
            mul(var("param_budget"), const(1.0 + PARAM_BUDGET_TOLERANCE)),
        ),
        params={"tolerance": PARAM_BUDGET_TOLERANCE},
        proof_kind=ProofKind.RESOURCE,
        origin="DECLARED",
    ),
    # Operating point constraints (R66)
    ConstraintSpec(
        name="operating_point_min_seeds",
        kind=ConstraintKind.OPERATING_POINT,
        description="Minimum seeds per operating point for statistical validity",
        predicate=ge(var("n_seeds"), const(3)),
        params={"min_seeds": 3},
        proof_kind=ProofKind.RESOURCE,
        origin="APPLY_CONSTRAINTS",
    ),
    ConstraintSpec(
        name="operating_point_max_epochs",
        kind=ConstraintKind.OPERATING_POINT,
        description="Maximum epochs per operating point to prevent overfitting",
        predicate=le(var("epochs"), const(100)),
        params={"max_epochs": 100},
        proof_kind=ProofKind.RESOURCE,
        origin="APPLY_CONSTRAINTS",
    ),
    # apply_constraints derived constraints (from legacy apply_constraints())
    ConstraintSpec(
        name="apply_constraints_max_hidden",
        kind=ConstraintKind.HARD,
        description="Max hidden dim from apply_constraints",
        predicate=le(var("params.hidden_dim"), const(4096)),
        proof_kind=ProofKind.RESOURCE,
        origin="APPLY_CONSTRAINTS",
    ),
    ConstraintSpec(
        name="apply_constraints_max_layers",
        kind=ConstraintKind.HARD,
        description="Max layers from apply_constraints",
        predicate=le(var("params.num_layers"), const(32)),
        proof_kind=ProofKind.RESOURCE,
        origin="APPLY_CONSTRAINTS",
    ),
    ConstraintSpec(
        name="apply_constraints_max_steps",
        kind=ConstraintKind.HARD,
        description="Max settling steps from apply_constraints",
        predicate=le(var("params.max_steps"), const(500)),
        proof_kind=ProofKind.RESOURCE,
        origin="APPLY_CONSTRAINTS",
    ),
]


# =============================================================================
# PRIORS — Gate 1/2: ruler-LR table + step-size overrides (Appendix IV + §13.2)
# =============================================================================

PRIORS = [
    # Ruler learning rate priors (from 11 tasks). The MNIST row lives below
    # with the migrated learning.prior table (explicit measured center).
    PriorSpec(
        name="ruler_lr_cifar10",
        distribution="log_uniform",
        params={"low": 1e-4, "high": 1e-1},
        description="Ruler LR prior for CIFAR-10",
    ),
    PriorSpec(
        name="ruler_lr_cifar100",
        distribution="log_uniform",
        params={"low": 1e-4, "high": 1e-1},
        description="Ruler LR prior for CIFAR-100",
    ),
    PriorSpec(
        name="ruler_lr_imagenet",
        distribution="log_uniform",
        params={"low": 1e-5, "high": 1e-2},
        description="Ruler LR prior for ImageNet",
    ),
    PriorSpec(
        name="ruler_lr_sst2",
        distribution="log_uniform",
        params={"low": 1e-5, "high": 1e-2},
        description="Ruler LR prior for SST-2",
    ),
    PriorSpec(
        name="ruler_lr_squad",
        distribution="log_uniform",
        params={"low": 1e-5, "high": 1e-2},
        description="Ruler LR prior for SQuAD",
    ),
    PriorSpec(
        name="ruler_lr_wikitext2",
        distribution="log_uniform",
        params={"low": 1e-5, "high": 1e-2},
        description="Ruler LR prior for WikiText-2",
    ),
    PriorSpec(
        name="ruler_lr_ptb",
        distribution="log_uniform",
        params={"low": 1e-5, "high": 1e-2},
        description="Ruler LR prior for PTB",
    ),
    PriorSpec(
        name="ruler_lr_copyshake",
        distribution="log_uniform",
        params={"low": 1e-4, "high": 1e-1},
        description="Ruler LR prior for CopyShake",
    ),
    PriorSpec(
        name="ruler_lr_arithmetic",
        distribution="log_uniform",
        params={"low": 1e-4, "high": 1e-1},
        description="Ruler LR prior for Arithmetic",
    ),
    PriorSpec(
        name="ruler_lr_listops",
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
    # Gate 2 additions: optimizer betas, apply_constraints
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
    # Migrated from learning.prior (Q4, TODO48): one PRIORS table, one
    # registration path. Ruler LRs carry explicit measured centers.
    PriorSpec(
        name="ruler_lr_digits",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Ruler-calibrated learning rate for task 'digits' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_mnist",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Ruler-calibrated learning rate for task 'mnist' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_fashion_mnist",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Ruler-calibrated learning rate for task 'fashion_mnist' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_kmnist",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Ruler-calibrated learning rate for task 'kmnist' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_usps",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Ruler-calibrated learning rate for task 'usps' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_xor",
        distribution="log_uniform",
        params={"low": 0.0001, "high": 0.01, "center": 0.001},
        description="Ruler-calibrated learning rate for task 'xor' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_spiral",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Ruler-calibrated learning rate for task 'spiral' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_circles",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Ruler-calibrated learning rate for task 'circles' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_iris",
        distribution="log_uniform",
        params={"low": 0.0001, "high": 0.01, "center": 0.001},
        description="Ruler-calibrated learning rate for task 'iris' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_wine",
        distribution="log_uniform",
        params={"low": 0.0001, "high": 0.01, "center": 0.001},
        description="Ruler-calibrated learning rate for task 'wine' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_breast_cancer",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Ruler-calibrated learning rate for task 'breast_cancer' (feedforward topology)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_catchall",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Catch-all ruler-calibrated learning rate for unknown tasks (feedforward)",
        confidence=0.9,
    ),
    PriorSpec(
        name="ruler_lr_non_feedforward",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Default learning rate for non-feedforward topologies (from topology LR probe)",
        confidence=0.8,
    ),
    # Step-size override priors (dynamics x credit multipliers)
    PriorSpec(
        name="step_size_override_energy_minimization_random_projections",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.1; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_energy_minimization_gradient",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.5; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_energy_minimization_thermodynamic_contrast",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.00005; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_energy_minimization_pepita",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.0001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_energy_minimization_local_goodness",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.0005; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_energy_minimization_temporal_trace",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.0001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_energy_minimization_target_inversion",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.1; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_diffusion_random_projections",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.05; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_diffusion_spectral_constrained",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.1; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_diffusion_homeostatic",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.1; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_diffusion_temporal_trace",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.0001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_diffusion_target_inversion",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.1; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_lazy_temporal_trace",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.0001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_lazy_thermodynamic_contrast",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_lazy_random_projections",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.1; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_lazy_local_contrastive",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.0005; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_lazy_local_goodness",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.1; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_lazy_pepita",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_lazy_gradient",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.01; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_instantaneous_temporal_trace",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.0001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_instantaneous_pepita",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.01; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_pc_alm_thermodynamic_contrast",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_pc_alm_pc_alm",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_instantaneous_homeostatic",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_spike_integration_temporal_trace",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.0001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_predictive_settling_thermodynamic_contrast",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.5; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_predictive_settling_local_goodness",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.001; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_error_predictive_coding_thermodynamic_contrast",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.1; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    PriorSpec(
        name="step_size_override_error_predictive_coding_local_goodness",
        distribution="log_normal",
        params={"mean": 1.0, "sigma": 0.5},
        description="Retired attenuation (TODO48b R4): was 0.1; never measured, and the audited rule learns 4 decades above its registered lr (scripts/probes/step_size_multipliers.py)",
        confidence=0.2,
    ),
    # Dynamics settling step size priors
    PriorSpec(
        name="dynamics_step_size_diffusion",
        distribution="log_uniform",
        params={"low": 0.0001, "high": 0.01, "center": 0.001},
        description="Dynamics settling step size for diffusion",
        confidence=0.85,
    ),
    PriorSpec(
        name="dynamics_step_size_predictive_settling",
        distribution="log_uniform",
        params={"low": 0.001, "high": 0.1, "center": 0.01},
        description="Dynamics settling step size for predictive_settling",
        confidence=0.85,
    ),
    # Harvested geometry size priors: without a prior the unswept value
    # resolved to the domain edge (an 8-unit, 1-layer network).
    PriorSpec(
        name="hidden_width",
        distribution="log_uniform",
        params={"low": 16.0, "high": 256.0, "center": 64.0},
        description="Default geometry width",
        confidence=0.6,
    ),
    PriorSpec(
        name="hidden_depth",
        distribution="log_uniform",
        params={"low": 1.0, "high": 4.0, "center": 2.0},
        description="Default geometry depth",
        confidence=0.6,
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
# STAGES — S1-S11 canonical pipeline stages (TODO43 §3.0 / abc3 §5.1)
# =============================================================================


# Convert execution StageSpec to registry StageSpec
def _convert_stage_spec(exec_stage: Any) -> StageSpec:
    """Convert execution.stage.StageSpec to schema.registries.StageSpec."""
    return StageSpec(
        stage_id=exec_stage.stage_id,
        name=exec_stage.name,  # Canonical ID
        display_name=exec_stage.display_name,
        description=exec_stage.description,
        required_fidelity=exec_stage.required_fidelity,
        min_n_seeds=exec_stage.min_n_seeds,
        gate=exec_stage.gate,
        params=exec_stage.params,
    )


# Import STAGE_SPECS after defining conversion

STAGES = [_convert_stage_spec(s) for s in EXEC_STAGE_SPECS]


CAPABILITIES = [
    CapabilitySpec(
        capability_id="C1",
        name="C1",
        kind=CapabilityKind.CORE,
        display_name="Six-axis coordinate space",
        description="Full Substrate×Geometry×Dynamics×Plasticity×Credit×Update coordinate space",
        required=True,
        stage="S1_FRAME",
        owner="schema",
        verifying_test="tests/property/test_experiment_registries_wiring_lock.py::test_all_registries_dict_completeness",
        flags=("axis", "coordinate"),
    ),
    CapabilitySpec(
        capability_id="C2",
        name="C2",
        kind=CapabilityKind.CORE,
        display_name="Unified record schema",
        description="Single record schema with four identity sections and three identity keys",
        required=True,
        stage="S2_SPACE",
        owner="schema",
        verifying_test="tests/property/test_dynamics_wiring_lock.py::test_registry_classes_round_trip_to_spec_from_spec",
        flags=("schema", "record"),
    ),
    CapabilitySpec(
        capability_id="C3",
        name="C3",
        kind=CapabilityKind.CORE,
        display_name="Content-addressed records",
        description="Records identified by content hash (record_id)",
        required=True,
        stage="S8_RECORD",
        owner="store",
        verifying_test="tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_append_with_artifacts_atomic_on_exception",
        flags=("content_addressed", "dedup"),
    ),
    CapabilitySpec(
        capability_id="C4",
        name="C4",
        kind=CapabilityKind.CORE,
        display_name="Measurement key deduplication",
        description="Unique measurement_key prevents duplicate evaluations",
        required=True,
        stage="S8_RECORD",
        owner="store",
        verifying_test="tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_append_with_artifacts_atomic_on_duplicate_measurement",
        flags=("dedup", "measurement_key"),
    ),
    CapabilitySpec(
        capability_id="C5",
        name="C5",
        kind=CapabilityKind.CORE,
        display_name="Cell key grouping",
        description="cell_key groups repeated evaluations of same coordinate",
        required=True,
        stage="S2_SPACE",
        owner="schema",
        verifying_test="tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_concurrent_append_dedup_by_measurement_key",
        flags=("cell_key", "replication"),
    ),
    CapabilitySpec(
        capability_id="C6",
        name="C6",
        kind=CapabilityKind.CORE,
        display_name="Schema versioning",
        description="Append-only schema evolution with UnknownField preservation",
        required=True,
        stage="S1_FRAME",
        owner="schema",
        verifying_test="tests/property/test_experiment_registries_wiring_lock.py::test_registry_integrity_checks_pass",
        flags=("versioning", "unknown_field"),
    ),
    CapabilitySpec(
        capability_id="C7",
        name="C7",
        kind=CapabilityKind.CORE,
        display_name="Legality engine",
        description="Predicate-based constraint engine with void/defect classification",
        required=True,
        stage="S4_GATE",
        owner="legality",
        verifying_test="tests/property/test_legality_boundary_lock.py",
        flags=("legality", "void", "defect"),
    ),
    CapabilitySpec(
        capability_id="C8",
        name="C8",
        kind=CapabilityKind.CORE,
        display_name="S1-S11 pipeline",
        description="Eleven-stage pipeline with wrapper obligations",
        required=True,
        stage="S1_FRAME",
        owner="pipeline",
        verifying_test="tests/acceptance/test_unified_kernel.py::TestU1_SynthesisPolicyPipeline::test_u1_synthesis_policy_end_to_end",
        flags=("pipeline", "stages"),
    ),
    CapabilitySpec(
        capability_id="C9",
        name="C9",
        kind=CapabilityKind.CORE,
        display_name="Eight-policy catalog",
        description="StratifiedRandom, RoundRobinGrid, UniformRandom, ModelBased, Evolution, Synthesis, StrategyProgression, TrainerDriven",
        required=True,
        stage="S3_SCHEDULE",
        owner="policy",
        verifying_test="tests/property/test_sampler_lock.py::TestTheRunReachesThePolicy::test_the_spec_reaches_a_learning_policy",
        flags=("policy", "catalog"),
    ),
    CapabilitySpec(
        capability_id="C10",
        name="C10",
        kind=CapabilityKind.CORE,
        display_name="Evidence-driven allocation",
        description="Non-uniform compute allocation with divergence/stagnation detection",
        required=True,
        stage="S10_DECIDE",
        owner="allocator",
        verifying_test="tests/property/test_allocator_promotion.py::TestEvidenceDrivenAllocation::test_first_observation_nominates_next_fidelity",
        flags=("allocation", "evidence_driven"),
    ),
    CapabilitySpec(
        capability_id="C11",
        name="C11",
        kind=CapabilityKind.CORE,
        display_name="Replay and resume",
        description="Deterministic replay via replay_hash; resume via measurement_key",
        required=True,
        stage="S6_TRAIN",
        owner="replay",
        verifying_test="tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_monotonic_seq_across_concurrent_writes",
        flags=("replay", "resume"),
    ),
    CapabilitySpec(
        capability_id="C12",
        name="C12",
        kind=CapabilityKind.CORE,
        display_name="Three-tier status model",
        description="Observations, Assessments (procedure-versioned), Derived Claims",
        required=True,
        stage="S7_MEASURE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_claim_eligible_requires_l2_fidelity",
        flags=("status", "three_tier"),
    ),
    CapabilitySpec(
        capability_id="C13",
        name="C13",
        kind=CapabilityKind.CORE,
        display_name="Claim eligibility predicates",
        description="Pure query predicates for claim_eligible, promoted, beats_baseline",
        required=True,
        stage="S7_MEASURE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_claim_eligible_requires_pass_verdict",
        flags=("claims", "predicates"),
    ),
    CapabilitySpec(
        capability_id="C14",
        name="C14",
        kind=CapabilityKind.CORE,
        display_name="Failure intelligence",
        description="FailureCause taxonomy, clustering, reproducer emission",
        required=True,
        stage="S7_MEASURE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestAlertPredicates::test_alert_on_divergence",
        flags=("failure", "clustering"),
    ),
    CapabilitySpec(
        capability_id="C15",
        name="C15",
        kind=CapabilityKind.CORE,
        display_name="Unified artifact storage",
        description="Atomic record+artifact transactions in DuckDB",
        required=True,
        stage="S8_RECORD",
        owner="artifacts",
        verifying_test="tests/property/test_atomic_append_kill_proof.py::TestAtomicAppendKillProof::test_kill_during_atomic_append_no_partial_state",
        flags=("artifacts", "atomic"),
    ),
    CapabilitySpec(
        capability_id="C16",
        name="C16",
        kind=CapabilityKind.CORE,
        display_name="Vector retrieval",
        description="Brute-force cosine/dot + optional HNSW via vss",
        required=True,
        stage="S8_RECORD",
        owner="store",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestStoreIntegration::test_store_supports_vector_index",
        flags=("vector", "vss_optional"),
    ),
    CapabilitySpec(
        capability_id="C17",
        name="C17",
        kind=CapabilityKind.CORE,
        display_name="Prior registry",
        description="Ruler LR + step-size overrides as PriorSpec data",
        required=True,
        stage="S1_FRAME",
        owner="priors",
        verifying_test="tests/property/test_active_space_lock.py::test_every_declared_prior_resolves",
        flags=("priors", "ruler_lr"),
    ),
    CapabilitySpec(
        capability_id="C18",
        name="C18",
        kind=CapabilityKind.CORE,
        display_name="Surrogate policy wrapper",
        description="EI/EHVI/UCB/PI/LOG_EI over any base Policy",
        required=True,
        stage="S5_COMPOSE",
        owner="learning",
        verifying_test="tests/property/test_wp10_learning_integration_lock.py::TestSurrogateStoreWiring::test_training_split_excludes_calibration_test",
        flags=("surrogate", "acquisition"),
    ),
    CapabilitySpec(
        capability_id="C19",
        name="C19",
        kind=CapabilityKind.CORE,
        display_name="I(C,U) metamodel",
        description="Input-conditional uncertainty metamodel with leakage guard",
        required=True,
        stage="S5_COMPOSE",
        owner="learning",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestDataSplitProtocol::test_leakage_detection_calibration_in_training",
        flags=("icu", "leakage_guard"),
    ),
    CapabilitySpec(
        capability_id="C20",
        name="C20",
        kind=CapabilityKind.CORE,
        display_name="Reasoning records",
        description="Hypothesis/literature records with provenance linkage",
        required=True,
        stage="S1_FRAME",
        owner="learning",
        verifying_test="tests/property/test_scientific_validity_protocol_lock.py::TestDataOriginAndTransferProvenance::test_provenance_roundtrip",
        flags=("reasoning", "provenance"),
    ),
    CapabilitySpec(
        capability_id="C21",
        name="C21",
        kind=CapabilityKind.ACCELERATION,
        display_name="torch.compile settle loop",
        description="Compiled settle loop for digital substrate (2x speedup)",
        required=False,
        stage="S6_TRAIN",
        owner="dynamics",
        verifying_test="tests/integration/test_compiled_settle.py",
        flags=("compilation", "experimental"),
    ),
    CapabilitySpec(
        capability_id="C22",
        name="C22",
        kind=CapabilityKind.ACCELERATION,
        display_name="Gradient checkpointing",
        description="Memory-compute tradeoff for deep settling",
        required=False,
        stage="S6_TRAIN",
        owner="dynamics",
        verifying_test="tests/property/test_settle_driver_lock.py::test_gradient_checkpointing_memory",
        flags=("checkpointing", "memory"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="gradient checkpointing: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C23",
        name="C23",
        kind=CapabilityKind.ACCELERATION,
        display_name="Gain control homeostasis",
        description="μPC-style unit RMS and spectral renormalization",
        required=False,
        stage="S6_TRAIN",
        owner="dynamics",
        verifying_test="tests/property/test_settle_driver_lock.py::test_gain_control_unit_rms",
        flags=("gain_control", "homeostasis"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="gain control homeostasis: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C24",
        name="C24",
        kind=CapabilityKind.ACCELERATION,
        display_name="KV cache for transformer",
        description="Key-value cache for autoregressive generation",
        required=False,
        stage="S6_TRAIN",
        owner="geometry",
        verifying_test="tests/property/test_geometry_wiring_lock.py::test_transformer_kv_cache",
        flags=("kv_cache", "transformer"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="transformer KV cache: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C25",
        name="C25",
        kind=CapabilityKind.ACCELERATION,
        display_name="Async orchestration",
        description="asyncio.TaskGroup for concurrent evaluation",
        required=False,
        stage="S6_TRAIN",
        owner="backends",
        verifying_test="tests/property/test_experiment_registries_wiring_lock.py::test_async_backend_works",
        flags=("async", "taskgroup"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="async orchestration: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C26",
        name="C26",
        kind=CapabilityKind.SCALING,
        display_name="Multiprocess backend",
        description="Parallel evaluation via multiprocessing",
        required=False,
        stage="S6_TRAIN",
        owner="backends",
        verifying_test="tests/property/test_experiment_registries_wiring_lock.py::test_multiprocess_backend",
        flags=("multiprocess", "parallel"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="multiprocess backend: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C27",
        name="C27",
        kind=CapabilityKind.SCALING,
        display_name="Multi-GPU DDP/FSDP",
        description="Distributed data parallel and fully sharded data parallel",
        required=False,
        stage="S6_TRAIN",
        owner="backends",
        verifying_test="tests/property/test_experiment_registries_wiring_lock.py::test_ddp_fsdp_works",
        flags=("ddp", "fsdp", "gpu_only"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="multi-GPU DDP/FSDP: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C28",
        name="C28",
        kind=CapabilityKind.SCALING,
        display_name="P2P gossip cluster",
        description="Kademlia-based peer-to-peer worker coordination",
        required=False,
        stage="S6_TRAIN",
        owner="backends",
        verifying_test="tests/property/test_experiment_registries_wiring_lock.py::test_p2p_cluster_works",
        flags=("p2p", "kademlia"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="P2P gossip cluster: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C29",
        name="C29",
        kind=CapabilityKind.SCALING,
        display_name="Batch vectorization",
        description="Vectorized evaluation across batch dimension",
        required=False,
        stage="S6_TRAIN",
        owner="backends",
        verifying_test="tests/property/test_experiment_registries_wiring_lock.py::test_batch_vectorization",
        flags=("vectorization", "batch"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="batch vectorization: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C30",
        name="C30",
        kind=CapabilityKind.SCALING,
        display_name="Pipeline parallelism",
        description="Stage-wise pipeline parallelism for deep networks",
        required=False,
        stage="S6_TRAIN",
        owner="backends",
        verifying_test="tests/property/test_experiment_registries_wiring_lock.py::test_pipeline_parallelism",
        flags=("pipeline_parallel", "experimental"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="pipeline parallelism: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C31",
        name="C31",
        kind=CapabilityKind.REPRODUCIBILITY,
        display_name="Computational reproducibility",
        description="Same env reproduces numerics within tolerance",
        required=True,
        stage="S11_REPORT",
        owner="replay",
        verifying_test="tests/property/test_scientific_validity_protocol_lock.py::TestReproducibilityClasses::test_reproducibility_class_enum",
        flags=("replayable", "computational"),
    ),
    CapabilitySpec(
        capability_id="C32",
        name="C32",
        kind=CapabilityKind.REPRODUCIBILITY,
        display_name="Scientific reproducibility",
        description="Independent env reproduces reported effect",
        required=False,
        stage="S11_REPORT",
        owner="benchmarks",
        verifying_test="tests/property/test_scientific_validity_protocol_lock.py::test_scientific_reproducibility",
        flags=("scientific", "independent_env"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="scientific reproducibility: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C33",
        name="C33",
        kind=CapabilityKind.REPRODUCIBILITY,
        display_name="Reproducibility class tracking",
        description="REPLAYABLE / COMPUTATIONALLY_REPRODUCIBLE / SCIENTIFICALLY_REPRODUCIBLE",
        required=True,
        stage="S7_MEASURE",
        owner="evidence",
        verifying_test="tests/property/test_scientific_validity_protocol_lock.py::TestReproducibilityClasses::test_status_requires_reproducibility_class",
        flags=("reproducibility", "tracking"),
    ),
    CapabilitySpec(
        capability_id="C36",
        name="C36",
        kind=CapabilityKind.REPRODUCIBILITY,
        display_name="Assessment procedure versioning",
        description="Assessments carry procedure version + content hash",
        required=True,
        stage="S7_MEASURE",
        owner="evidence",
        verifying_test="tests/property/test_scientific_validity_protocol_lock.py::TestReproducibilityClasses::test_status_requires_assessment_procedure_version",
        flags=("assessment", "procedure"),
    ),
    CapabilitySpec(
        capability_id="C34",
        name="C34",
        kind=CapabilityKind.REPRODUCIBILITY,
        display_name="Data origin tags",
        description="EXPLORATION / CALIBRATION / TEST tags on every record",
        required=True,
        stage="S3_SCHEDULE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestDataSplitProtocol::test_no_leakage_clean_split",
        flags=("data_origin", "i_cu"),
    ),
    CapabilitySpec(
        capability_id="C35",
        name="C35",
        kind=CapabilityKind.REPRODUCIBILITY,
        display_name="Transfer provenance",
        description="training_tasks, transfer_source_ids, transfer_cutoff, target_task, transfer_mode",
        required=True,
        stage="S1_FRAME",
        owner="evidence",
        verifying_test="tests/property/test_scientific_validity_protocol_lock.py::TestDataOriginAndTransferProvenance::test_transfer_mode_enum",
        flags=("transfer", "provenance"),
    ),
    CapabilitySpec(
        capability_id="C37",
        name="C37",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Comparison guard",
        description="Refuses or labels unmatched cost-tier comparisons",
        required=True,
        stage="S10_DECIDE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestComparisonGuards::test_matched_cost_comparison",
        flags=("comparison", "guard"),
    ),
    CapabilitySpec(
        capability_id="C38",
        name="C38",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Stratification guard",
        description="Requires hardware_class match for walltime comparisons",
        required=True,
        stage="S10_DECIDE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestComparisonGuards::test_same_hardware_class_for_walltime",
        flags=("stratification", "hardware_class"),
    ),
    CapabilitySpec(
        capability_id="C39",
        name="C39",
        kind=CapabilityKind.GOVERNANCE,
        display_name="ICU calibration audit",
        description="Periodic calibration audit per WP5.5 #3 bounded degradation check",
        required=True,
        stage="S10_DECIDE",
        owner="learning",
        verifying_test="tests/property/test_wp10_learning_integration_lock.py::TestSurrogateStoreWiring::test_effect_size_guards",
        flags=("icu", "calibration"),
    ),
    CapabilitySpec(
        capability_id="C40",
        name="C40",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Alert predicates",
        description="Divergence, stagnation, resource exhaustion, constraint violation alerts",
        required=True,
        stage="S7_MEASURE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestAlertPredicates::test_alert_on_resource_exhaustion",
        flags=("alerts", "predicates"),
    ),
    CapabilitySpec(
        capability_id="C41",
        name="C41",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Promotion predicates",
        description="Promoted records must meet maturity and seed thresholds",
        required=True,
        stage="S10_DECIDE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_promoted_requires_l2_maturity",
        flags=("promotion", "maturity"),
    ),
    CapabilitySpec(
        capability_id="C42",
        name="C42",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Effect size protocol",
        description="Cohen's d with CI, p-value, task-level inference",
        required=True,
        stage="S10_DECIDE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestEffectSizeProtocol::test_effect_size_reports_cohens_d_with_ci",
        flags=("effect_size", "cohens_d"),
    ),
    CapabilitySpec(
        capability_id="C43",
        name="C43",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Budget tier system",
        description="EVAL_COUNT / FLOPS / WALLTIME / ENERGY budget tiers",
        required=True,
        stage="S3_SCHEDULE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestEffectSizeProtocol::test_budget_tier_matching_required",
        flags=("budget_tier", "comparison"),
    ),
    CapabilitySpec(
        capability_id="C44",
        name="C44",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Surface CLI profiles",
        description="Question-first, production-map, maturation, claim profiles",
        required=True,
        stage="S1_FRAME",
        owner="surface",
        verifying_test="tests/property/test_wp11_surface_lock.py::TestDocumentedCommands::test_run_profiles_canonical_stages",
        flags=("cli", "profiles"),
    ),
    CapabilitySpec(
        capability_id="C45",
        name="C45",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Service manager",
        description="Long-running services with auto-restart and webhook alerts",
        required=False,
        stage="S9_ATTRIBUTE",
        owner="operations",
        verifying_test="tests/property/test_public_surface_lock.py::test_service_manager_webhooks",
        flags=("service", "webhooks"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="service manager: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C46",
        name="C46",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Conformance harness gate",
        description="CI gate enforces capability conformance",
        required=True,
        stage="S11_REPORT",
        owner="surface",
        verifying_test="tests/property/test_conformance_harness.py::TestConformanceHarness::test_required_capabilities_have_verifying_tests",
        flags=("conformance", "ci_gate"),
    ),
    CapabilitySpec(
        capability_id="C47",
        name="C47",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Currency lock flags",
        description="Appendix-A flag projection lock tracks capability currency",
        required=True,
        stage="S11_REPORT",
        owner="surface",
        verifying_test="tests/property/test_conformance_harness.py::TestFlagProjectionLock::test_flag_projection_totality",
        flags=("currency_lock", "flags"),
    ),
    CapabilitySpec(
        capability_id="C48",
        name="C48",
        kind=CapabilityKind.GOVERNANCE,
        display_name="Synthesis policy question-first",
        description="Question-first entry profile using Synthesis policy",
        required=True,
        stage="S1_FRAME",
        owner="surface",
        verifying_test="tests/property/test_wp11_surface_lock.py::TestQuestionFirst::test_spec_shape",
        flags=("synthesis", "question_first"),
    ),
    CapabilitySpec(
        capability_id="C49",
        name="C49",
        kind=CapabilityKind.LEARNING,
        display_name="Surrogate-driven acquisition",
        description="EI/EHVI acquisition functions for efficient search",
        required=False,
        stage="S5_COMPOSE",
        owner="learning",
        verifying_test="tests/property/test_statistical_protocol_lock.py::test_surrogate_acquisition_ei",
        flags=("surrogate", "ei"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="surrogate-driven acquisition: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C50",
        name="C50",
        kind=CapabilityKind.LEARNING,
        display_name="Cross-task transfer",
        description="Transfer learning with explicit provenance",
        required=False,
        stage="S1_FRAME",
        owner="learning",
        verifying_test="tests/property/test_statistical_protocol_lock.py::test_cross_task_transfer",
        flags=("transfer", "cross_task"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="cross-task transfer: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C51",
        name="C51",
        kind=CapabilityKind.LEARNING,
        display_name="Prior single source",
        description="PRIORS registry is the single source of prior values",
        required=True,
        stage="S1_FRAME",
        owner="priors",
        verifying_test="tests/property/test_wp10_learning_integration_lock.py::TestPriorSingleSource::test_ruler_tasks_resolve_via_registry",
        flags=("priors", "single_source"),
    ),
    CapabilitySpec(
        capability_id="C52",
        name="C52",
        kind=CapabilityKind.LEARNING,
        display_name="No global singletons",
        description="No module-level mutable state in experiment/ (K10)",
        required=True,
        stage="S1_FRAME",
        owner="kernel",
        verifying_test="tests/property/test_kernel_isolation_lock.py::TestRunScopedState::test_engine_singleton_removed",
        flags=("k10", "singletons"),
    ),
    CapabilitySpec(
        capability_id="C53",
        name="C53",
        kind=CapabilityKind.LEARNING,
        display_name="Reasoning persistence",
        description="Hypothesis/literature records persisted with provenance links",
        required=True,
        stage="S1_FRAME",
        owner="learning",
        verifying_test="tests/property/test_scientific_validity_protocol_lock.py::TestDataOriginAndTransferProvenance::test_provenance_with_data_origin",
        flags=("reasoning", "persistence"),
    ),
    CapabilitySpec(
        capability_id="C54",
        name="C54",
        kind=CapabilityKind.LEARNING,
        display_name="Warm-start from prior runs",
        description="Registered prior/surrogate sources for transfer",
        required=False,
        stage="S5_COMPOSE",
        owner="learning",
        verifying_test="tests/property/test_statistical_protocol_lock.py::test_warm_start_prior_runs",
        flags=("warm_start", "transfer"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="warm-start from prior runs: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C55",
        name="C55",
        kind=CapabilityKind.LEARNING,
        display_name="Coordinate-wide surrogate",
        description="SurrogatePolicy over any Policy, features from full Coordinate",
        required=False,
        stage="S5_COMPOSE",
        owner="learning",
        verifying_test="tests/property/test_statistical_protocol_lock.py::test_coordinate_wide_surrogate",
        flags=("surrogate", "coordinate_wide"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="coordinate-wide surrogate: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C56",
        name="C56",
        kind=CapabilityKind.LEARNING,
        display_name="I(C,U) feature encoder",
        description="Credit×Update interaction surrogate with feature encoder",
        required=False,
        stage="S5_COMPOSE",
        owner="learning",
        verifying_test="tests/property/test_statistical_protocol_lock.py::test_icu_feature_encoder",
        flags=("icu", "feature_encoder"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="I(C,U) feature encoder: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C57",
        name="C57",
        kind=CapabilityKind.LEARNING,
        display_name="Achieved seed claim",
        description="Claim eligibility counts achieved seeds per replication_key",
        required=True,
        stage="S10_DECIDE",
        owner="evidence",
        verifying_test="tests/property/test_statistical_protocol_lock.py::TestClaimPredicates::test_claim_eligible_requires_min_seeds",
        flags=("claims", "achieved_seeds"),
    ),
    CapabilitySpec(
        capability_id="C58",
        name="C58",
        kind=CapabilityKind.LEARNING,
        display_name="Multi-objective Pareto",
        description="Pareto frontier analysis for multi-objective optimization",
        required=True,
        stage="S7_MEASURE",
        owner="learning",
        verifying_test="tests/property/test_wp10_learning_integration_lock.py::TestSurrogateStoreWiring::test_effect_size_guards",
        flags=("pareto", "multi_objective"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="multi-objective Pareto: report.pareto_frontier has no test in the tree; the row's verifying_test asserted an unrelated protocol minimum (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C59",
        name="C59",
        kind=CapabilityKind.LEARNING,
        display_name="Substrate-aware objectives",
        description="Memristive→energy, Neuromorphic→spike_rate, etc.",
        required=False,
        stage="S7_MEASURE",
        owner="substrate",
        verifying_test="tests/property/test_statistical_protocol_lock.py::test_substrate_aware_objectives",
        flags=("substrate", "objectives"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="substrate-aware objectives: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C60",
        name="C60",
        kind=CapabilityKind.LEARNING,
        display_name="Frozen-θ ψ adaptation",
        description="Lab.adapt Pareto over (accuracy, stability, cost) with θ bitwise invariant",
        required=False,
        stage="S10_DECIDE",
        owner="update",
        verifying_test="tests/property/test_statistical_protocol_lock.py::test_frozen_theta_psi_adapt",
        flags=("frozen_theta", "psi"),
        status=CapabilityStatus.UNVERIFIED,
        unverified_reason="frozen-theta psi adaptation: no test in the tree exercises this capability — the row's verifying_test named a test that does not exist (TODO46 D23).",
    ),
    CapabilitySpec(
        capability_id="C61",
        name="C61",
        kind=CapabilityKind.CORE,
        display_name="NTM geometry",
        description="External-memory tape: LSTM controller + content-addressed heads",
        required=False,
        stage="S5_COMPOSE",
        owner="geometry",
        verifying_test="tests/unit/core/test_ntm_geometry.py",
        flags=("ntm", "gate1_accepted", "experimental"),
    ),
    CapabilitySpec(
        capability_id="C62",
        name="C62",
        kind=CapabilityKind.CORE,
        display_name="NCA geometry",
        description="Neural cellular automaton fabric; local credit solves growing NCA",
        required=False,
        stage="S5_COMPOSE",
        owner="geometry",
        verifying_test="tests/unit/core/test_nca_geometry.py",
        flags=("nca", "gate1_accepted", "experimental"),
    ),
    CapabilitySpec(
        capability_id="C63",
        name="C63",
        kind=CapabilityKind.CORE,
        display_name="PEPITA/LEMMA credit",
        description="Published PEPITA input-modulation credit; LEMMA closed-form per-layer",
        required=False,
        stage="S5_COMPOSE",
        owner="credit",
        verifying_test="tests/property/generated/test_algorithm_pepita_invariants.py",
        flags=("pepita", "lemma", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C64",
        name="C64",
        kind=CapabilityKind.CORE,
        display_name="Holomorphic EP",
        description="Complex-valued EP with holomorphic activations and conjugate feedback",
        required=False,
        stage="S5_COMPOSE",
        owner="models_native",
        verifying_test="tests/property/generated/test_algorithm_holomorphic_ep_invariants.py",
        flags=("holomorphic", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C65",
        name="C65",
        kind=CapabilityKind.CORE,
        display_name="Directed EP",
        description="Asymmetric EP implementing Feedback Alignment within energy framework",
        required=False,
        stage="S5_COMPOSE",
        owner="models_native",
        verifying_test="tests/property/generated/test_algorithm_directed_ep_invariants.py",
        flags=("directed_ep", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C66",
        name="C66",
        kind=CapabilityKind.CORE,
        display_name="Finite-nudge EP",
        description="Large β finite nudge instead of infinitesimal limit",
        required=False,
        stage="S5_COMPOSE",
        owner="models_native",
        verifying_test="tests/property/generated/test_algorithm_finite_nudge_ep_invariants.py",
        flags=("finite_nudge", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C67",
        name="C67",
        kind=CapabilityKind.CORE,
        display_name="Ternary EqProp",
        description="Ternary-weight EP with STE-based quantization",
        required=False,
        stage="S5_COMPOSE",
        owner="models_native",
        verifying_test="tests/property/generated/test_algorithm_ternary_eqprop_invariants.py",
        flags=("ternary", "eqprop", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C68",
        name="C68",
        kind=CapabilityKind.CORE,
        display_name="Momentum EqProp",
        description="Heavy-ball settling dynamics for faster equilibrium convergence",
        required=False,
        stage="S5_COMPOSE",
        owner="models_native",
        verifying_test="tests/property/generated/test_algorithm_momentum_eqprop_invariants.py",
        flags=("momentum", "eqprop", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C69",
        name="C69",
        kind=CapabilityKind.CORE,
        display_name="Sparse EqProp",
        description="Dynamic sparsity masks with efficient sparse matmul",
        required=False,
        stage="S5_COMPOSE",
        owner="models_native",
        verifying_test="tests/property/generated/test_algorithm_sparse_eqprop_invariants.py",
        flags=("sparse", "eqprop", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C70",
        name="C70",
        kind=CapabilityKind.CORE,
        display_name="Diffusion EqProp",
        description="Continuous-time diffusion settling dynamics",
        required=False,
        stage="S5_COMPOSE",
        owner="models_native",
        verifying_test="tests/property/generated/test_algorithm_diffusion_eqprop_invariants.py",
        flags=("diffusion", "eqprop", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C71",
        name="C71",
        kind=CapabilityKind.CORE,
        display_name="Routing plasticity",
        description="State-dependent gating, sparse pathway routing",
        required=False,
        stage="S5_COMPOSE",
        owner="plasticity",
        verifying_test="tests/property/generated/test_primitive_plasticity_routing_invariants.py",
        flags=("routing", "plasticity", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C72",
        name="C72",
        kind=CapabilityKind.CORE,
        display_name="Fast-weight plasticity",
        description="Episode-local associative memory via fast-weight matrices",
        required=False,
        stage="S5_COMPOSE",
        owner="plasticity",
        verifying_test="tests/property/generated/test_primitive_plasticity_fast_weight_invariants.py",
        flags=("fast_weight", "plasticity", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C73",
        name="C73",
        kind=CapabilityKind.CORE,
        display_name="Substrate-coupled plasticity",
        description="Physical plasticity (memristive conductance dynamics)",
        required=False,
        stage="S5_COMPOSE",
        owner="plasticity",
        verifying_test="tests/property/generated/test_primitive_plasticity_substrate_coupled_invariants.py",
        flags=("substrate_coupled", "plasticity", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C74",
        name="C74",
        kind=CapabilityKind.CORE,
        display_name="Rule-state plasticity (Z3)",
        description="Rule selection as dynamical variable; frozen-θ ψ benchmarks",
        required=False,
        stage="S5_COMPOSE",
        owner="plasticity",
        verifying_test="tests/property/generated/test_primitive_plasticity_rule_state_invariants.py",
        flags=("z3", "rule_state", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C75",
        name="C75",
        kind=CapabilityKind.CORE,
        display_name="Closed-form ridge plasticity",
        description="Supervised ψ computed, not trained (LEMMA-style)",
        required=False,
        stage="S5_COMPOSE",
        owner="plasticity",
        verifying_test="tests/property/generated/test_primitive_plasticity_closed_form_ridge_invariants.py",
        flags=("closed_form", "ridge", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C76",
        name="C76",
        kind=CapabilityKind.CORE,
        display_name="Temporal ψ plasticity",
        description="Trace-decayed supervised ψ — forgetting enables task migration",
        required=False,
        stage="S5_COMPOSE",
        owner="plasticity",
        verifying_test="tests/property/generated/test_primitive_plasticity_temporal_psi_invariants.py",
        flags=("temporal_psi", "plasticity", "gate1_accepted"),
    ),
    CapabilitySpec(
        capability_id="C77",
        name="C77",
        kind=CapabilityKind.CORE,
        display_name="CEEC core ledger",
        description="Standalone epistemic governance ledger (evidence/beliefs/gates/audit)",
        required=False,
        stage="S8_RECORD",
        owner="ceec_core",
        verifying_test="packages/ceec-core/tests/test_ceec_store.py",
        flags=("ceec", "ledger", "platform"),
    ),
    CapabilitySpec(
        capability_id="C78",
        name="C78",
        kind=CapabilityKind.CORE,
        display_name="Psi-PEFT",
        description="Frozen-backbone task switching via temporal-ψ ridge readouts",
        required=False,
        stage="S10_DECIDE",
        owner="psi_peft",
        verifying_test="packages/psi-peft/tests/test_psi_adaptive.py",
        flags=("psi_peft", "platform"),
    ),
    CapabilitySpec(
        capability_id="C79",
        name="C79",
        kind=CapabilityKind.CORE,
        display_name="Local feedback projections",
        description="Adaptive local feedback for local credit (X-ALI validated)",
        required=False,
        stage="S5_COMPOSE",
        owner="local_feedback",
        verifying_test="packages/local-feedback/tests/test_lf_adaptive.py",
        flags=("local_feedback", "platform"),
    ),
    CapabilitySpec(
        capability_id="C80",
        name="C80",
        kind=CapabilityKind.CORE,
        display_name="Stability guard",
        description="Calibrated stability guard (attach, ROC-calibrated τ=1.029)",
        required=False,
        stage="S6_TRAIN",
        owner="stability",
        verifying_test="packages/stability/tests/test_stability_guard.py",
        flags=("stability", "guard", "platform"),
    ),
    CapabilitySpec(
        capability_id="C81",
        name="C81",
        kind=CapabilityKind.CORE,
        display_name="Computronium Lab synthesis",
        description="ProblemSpec → coordinate + provenance + predicted viability",
        required=False,
        stage="S1_FRAME",
        owner="lab",
        verifying_test="packages/computronium-lab/tests/test_synthesis.py",
        flags=("lab", "synthesis", "platform"),
    ),
    CapabilitySpec(
        capability_id="C82",
        name="C82",
        kind=CapabilityKind.CORE,
        display_name="Computronium Lab evolution",
        description="Budgeted evolution with campaign-backed fitness and audited ledger",
        required=False,
        stage="S10_DECIDE",
        owner="lab",
        verifying_test="packages/computronium-lab/tests/test_lab_integration_loop.py",
        flags=("lab", "evolution", "platform"),
    ),
    CapabilitySpec(
        capability_id="C83",
        name="C83",
        kind=CapabilityKind.CORE,
        display_name="Surface CLI dispatcher",
        description="Single comp-surface dispatcher with run profiles as data",
        required=True,
        stage="S11_REPORT",
        owner="surface",
        verifying_test="tests/property/test_cli_readme_lock.py::TestTierZeroIsReal::test_dry_run_prints_a_plan_and_writes_nothing",
        flags=("cli", "surface"),
    ),
    CapabilitySpec(
        capability_id="C84",
        name="C84",
        kind=CapabilityKind.CORE,
        display_name="Report generator",
        description="Run summaries, claim-eligible queries, Pareto frontier, export bundles",
        required=True,
        stage="S11_REPORT",
        owner="surface",
        verifying_test="tests/property/test_wp11_surface_lock.py::TestPublicExports::test_handoff_mentions_intents",
        flags=("report", "export"),
    ),
    CapabilitySpec(
        capability_id="C85",
        name="C85",
        kind=CapabilityKind.CORE,
        display_name="Codegen from registries",
        description="docs/generated listings, compatibility matrix, JSON-Schema validators",
        required=False,
        stage="S11_REPORT",
        owner="surface",
        verifying_test="tests/property/test_codegen_drift_lock.py",
        flags=("codegen", "drift_lock"),
    ),
    CapabilitySpec(
        capability_id="C86",
        name="C86",
        kind=CapabilityKind.CORE,
        display_name="Documented-command conformance",
        description="R80: every CLI command has conformance test",
        required=True,
        stage="S11_REPORT",
        owner="surface",
        verifying_test="tests/property/test_wp11_surface_lock.py::TestDocumentedCommands::test_commands_parse[argv0]",
        flags=("conformance", "cli"),
    ),
    CapabilitySpec(
        capability_id="C87",
        name="C87",
        kind=CapabilityKind.CORE,
        display_name="Gallery lock",
        description="DEMOS registry + docs/figures/manifest.json pinning (R87)",
        required=True,
        stage="S11_REPORT",
        owner="visualization",
        verifying_test="tests/integration/test_gallery_lock.py::test_figure_lock",
        flags=("gallery", "manifest"),
    ),
    CapabilitySpec(
        capability_id="C88",
        name="C88",
        kind=CapabilityKind.CORE,
        display_name="Probe conventions",
        description="scripts/probes/ throwaway scripts with measured-regime docstrings",
        required=True,
        stage="S11_REPORT",
        owner="probes",
        verifying_test="tests/property/test_wp11_surface_lock.py::TestAlertsAndControl::test_operator_intent_factory",
        flags=("probes", "conventions"),
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
    for axis_registry in AXES_REGISTRIES.values():
        axis_registry.clear()

    # Axis primitives (codegen listings + validators)
    _seed_axis_primitives()

    # Objectives
    for obj in OBJECTIVES:
        register_objective(obj)

    # Constraints
    for constraint in CONSTRAINTS:
        register_constraint(constraint)

    # Priors: the single PRIORS table above is the only registration path
    # (learning.prior's tables migrated here; its accessors read the registry).
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


seed_all_registries()


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
