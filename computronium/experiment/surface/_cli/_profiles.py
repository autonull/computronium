"""The run profiles the surface CLI offers, as data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

from computronium.experiment.schema.axis import Domain, Scale, StructuralAxis
from computronium.experiment.schema.run_spec import (
    BROAD_PARAM_BUDGET,
    MEASURED_BATCH_LIMIT,
    MEASURED_PARAM_BUDGET,
    AxisSelection,
    Fidelity,
)


@dataclass(frozen=True, slots=True)
class RunProfile:
    """Run profile configuration (data-driven)."""

    name: str
    description: str
    stages: list[str]  # Stage IDs to execute
    fidelity: Fidelity  # L0, L1, L2
    task: str  # The task this profile measures
    n_seeds: int
    epochs: int
    batch_limit: int
    budget_seconds: float | None
    param_budget: int  # Parameter ceiling for derived geometry sizing
    objectives: tuple[str, ...]  # Names from the OBJECTIVES registry
    policy: str  # Name from the POLICY catalog
    promotion_threshold: float  # Pareto frontier promotion threshold
    maturation: bool  # Whether to run maturation after
    deep_tier: bool  # Whether to run deep-tier claim-grade
    axes: tuple[AxisSelection, ...] = ()
    checkpoint_every_n: int = 0  # Save checkpoint every N epochs (0 = disabled)
    # The hyperparameters this profile searches, keyed canonically
    # ``"{axis}.{name}"``. Empty means "structural axes only" — a profile that
    # searches no knob (a smoke, a geometry sweep) declares none. A profile that
    # measures learning declares the knobs it varies, so the policy has something
    # to optimise and the cells carry their identity (TODO61 §0 B2).
    hyperparameters: Mapping[str, Domain] = field(default_factory=dict)


# The hyperparameters the search profiles vary. A single shared stride walks
# these diagonally (`_walk`'s ``steps`` is the longest ladder), so declaring
# several knobs adds one axis of length ``sweep_steps``, not a product. The
# chosen knobs are the ones the campaign found decisive; ``geometry.hidden_dim``
# is deliberately absent — ``RunSpec`` auto-narrows it to the ceiling.
_SEARCH_SWEEP: dict[str, Domain] = {
    "update.step_size": Domain(lo=1e-4, hi=1e-1, scale=Scale.LOG),
    "dynamics.step_size": Domain(lo=0.01, hi=0.5, scale=Scale.LOG),
    "dynamics.beta": Domain(lo=0.1, hi=1.0, scale=Scale.LOG),
    "dynamics.max_steps": Domain(lo=10, hi=100, scale=Scale.LINEAR),
}


# Run profiles as data — single source of truth for CLI behavior
RUN_PROFILES: dict[str, RunProfile] = {
    "quick-verify": RunProfile(
        name="quick-verify",
        description="Fast sanity check: L0 smoke + L1 evidence on few seeds",
        stages=[
            "s1_frame",
            "s2_space",
            "s3_schedule",
            "s4_gate",
            "s5_compose",
            "s6_train",
            "s7_measure",
            "s8_record",
        ],
        fidelity="L1",
        n_seeds=1,
        epochs=3,
        batch_limit=MEASURED_BATCH_LIMIT,
        budget_seconds=300.0,
        task="digits",
        policy="round_robin_grid",
        param_budget=MEASURED_PARAM_BUDGET,
        objectives=("validation_accuracy", "walltime_total"),
        promotion_threshold=0.5,
        maturation=False,
        deep_tier=False,
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(
                axis=StructuralAxis.GEOMETRY, primitives=("feedforward", "recurrent")
            ),
            AxisSelection(
                axis=StructuralAxis.DYNAMICS,
                primitives=("energy_minimization", "instantaneous", "lazy"),
            ),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
            AxisSelection(
                axis=StructuralAxis.CREDIT,
                primitives=(
                    "gradient",
                    "thermodynamic_contrast",
                    "random_projections",
                    "pepita",
                    "local_goodness",
                ),
            ),
            AxisSelection(
                axis=StructuralAxis.UPDATE, primitives=("euclidean", "adam", "muon")
            ),
        ),
        checkpoint_every_n=0,
    ),
    "production-map": RunProfile(
        name="production-map",
        description="Full broad mapping: L0→L1→L2 maturation with multi-objective Pareto",
        stages=[
            "s1_frame",
            "s2_space",
            "s3_schedule",
            "s4_gate",
            "s5_compose",
            "s6_train",
            "s7_measure",
            "s8_record",
            "s9_attribute",
            "s10_decide",
            "s11_report",
        ],
        fidelity="L0",
        n_seeds=1,
        epochs=1,
        batch_limit=MEASURED_BATCH_LIMIT,
        budget_seconds=3600.0,
        task="digits",
        policy="model_based",
        param_budget=BROAD_PARAM_BUDGET,
        objectives=(
            "validation_accuracy",
            "walltime_total",
            "param_count",
        ),
        promotion_threshold=0.7,
        maturation=True,
        deep_tier=True,
        hyperparameters=dict(_SEARCH_SWEEP),
    ),
    "maturation": RunProfile(
        name="maturation",
        description="Re-run front cells at higher fidelity (L1→L2)",
        stages=[
            "s3_schedule",
            "s4_gate",
            "s5_compose",
            "s6_train",
            "s7_measure",
            "s8_record",
            "s9_attribute",
            "s10_decide",
        ],
        fidelity="L2",
        n_seeds=5,
        epochs=10,
        batch_limit=0,  # Full training
        budget_seconds=7200.0,
        task="digits",
        policy="evolution",
        param_budget=BROAD_PARAM_BUDGET,
        objectives=("validation_accuracy", "walltime_total", "param_count"),
        promotion_threshold=0.8,
        maturation=False,
        deep_tier=False,
        hyperparameters=dict(_SEARCH_SWEEP),
    ),
    "claim": RunProfile(
        name="claim",
        description="Claim-grade L2 re-runs with CEEC governance (N≥10 seeds)",
        stages=[
            "s3_schedule",
            "s4_gate",
            "s5_compose",
            "s6_train",
            "s7_measure",
            "s8_record",
            "s9_attribute",
            "s10_decide",
            "s11_report",
        ],
        fidelity="L2",
        n_seeds=10,
        epochs=20,
        batch_limit=0,  # Full training
        budget_seconds=86400.0,  # 24 hours
        task="digits",
        policy="evolution",
        param_budget=BROAD_PARAM_BUDGET,
        objectives=(
            "validation_accuracy",
            "walltime_total",
            "param_count",
        ),
        promotion_threshold=0.9,
        maturation=False,
        deep_tier=True,
        hyperparameters=dict(_SEARCH_SWEEP),
    ),
    "demo": RunProfile(
        name="demo",
        description="One controlled contrast: four credit rules, five axes fixed",
        stages=[
            "s1_frame",
            "s2_space",
            "s3_schedule",
            "s4_gate",
            "s5_compose",
            "s6_train",
            "s7_measure",
            "s8_record",
            "s9_attribute",
            "s10_decide",
            "s11_report",
        ],
        fidelity="L1",
        n_seeds=5,
        epochs=3,
        batch_limit=0,
        budget_seconds=120.0,
        task="digits",
        policy="round_robin_grid",
        param_budget=MEASURED_PARAM_BUDGET,
        objectives=("validation_accuracy", "walltime_total"),
        promotion_threshold=0.8,
        maturation=False,
        deep_tier=False,
        axes=(
            AxisSelection(axis=StructuralAxis.SUBSTRATE, primitives=("digital",)),
            AxisSelection(axis=StructuralAxis.GEOMETRY, primitives=("feedforward",)),
            AxisSelection(axis=StructuralAxis.DYNAMICS, primitives=("instantaneous",)),
            AxisSelection(axis=StructuralAxis.PLASTICITY, primitives=("null",)),
            AxisSelection(
                axis=StructuralAxis.CREDIT,
                primitives=(
                    "gradient",
                    "random_projections",
                    "pepita",
                    "local_goodness",
                ),
            ),
            AxisSelection(axis=StructuralAxis.UPDATE, primitives=("adam",)),
        ),
        hyperparameters={"geometry.hidden_dim": Domain(members=(32,))},
        checkpoint_every_n=0,
    ),
}


# The six commands that tell the story. The rest stay reachable under
# ``comp --help-all``; the surface is grouped for presentation, not deleted.
CORE_COMMANDS: frozenset[str] = frozenset({
    "run",
    "report",
    "status",
    "demo",
    "coverage",
    "gallery",
    "dashboard",
})
