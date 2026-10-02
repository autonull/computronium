"""Canonical search space and proposal abstractions (WP14).

The abc3 architecture specifies:
    Policy.propose(SearchContext) -> Iterator[Proposal]

with the wrapper applying legality and novelty uniformly.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

from computronium.experiment.legality.dsl import Expr, evaluate
from computronium.experiment.schema.axis import StructuralAxis
from computronium.experiment.schema.coordinate import Coordinate, Schedule

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.execution.policy import Policy
    from computronium.experiment.schema.axis import AxisSpec
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.registries import ConstraintSpec, ObjectiveSpec


@dataclass(frozen=True, slots=True)
class Domain:
    """Parameter domain specification."""

    lo: float | int
    hi: float | int
    scale: str = "LINEAR"  # LINEAR | LOG
    members: tuple[str, ...] = field(default_factory=tuple)  # For CATEGORICAL


@dataclass(frozen=True, slots=True)
class SearchSpace:
    """Canonical search space derived from RunSpec."""

    axes_snapshot: tuple[AxisSpec, ...]
    constraints: tuple[ConstraintSpec, ...]
    objectives: tuple[ObjectiveSpec, ...]
    tasks: tuple[str, ...]

    def active_axes_for(self, coord: Coordinate) -> frozenset[AxisSpec]:
        """Get active axes for a given coordinate."""
        active = []
        for axis in self.axes_snapshot:
            if axis.axis_kind.value == "structural":
                continue
            if axis.availability_predicate is None or _evaluate_predicate(
                axis.availability_predicate, coord
            ):
                active.append(axis)
        return frozenset(active)


def _evaluate_predicate(predicate: Expr, coord: Coordinate) -> bool:
    """Evaluate an availability predicate against a coordinate."""
    from computronium.experiment.legality.dsl import EvaluationContext
    from computronium.experiment.schema.coordinate import Provenance, Schedule
    from computronium.experiment.schema.record import (
        FailureCause,
        GateVerdict,
        Maturity,
        Record,
        ReproducibilityClass,
        Severity,
        Status,
    )

    # Create a minimal record for evaluation
    schedule = Schedule(
        fidelity="L0",
        seed=42,
        n_seeds=1,
        epochs=1,
        batch_limit=0,
        budget_id="eval",
        task_id="default",
    )
    record = Record.create(
        run_id="eval",
        coordinate=coord,
        schedule=schedule,
        provenance=Provenance(
            env={},
            dataset="test",
            dataset_version="1.0",
            code_sha="test",
            policy="test",
            links={},
        ),
        status=Status(
            gate_verdict=GateVerdict.PENDING,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L0,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload={},
    )
    ctx = EvaluationContext(record)
    try:
        return evaluate(predicate, ctx)
    except Exception:
        return False


def generate_initial_candidates(
    search_space: SearchSpace,
    budget: Budget | None = None,
    cost_model: CostModel | None = None,
    max_candidates: int = 100,
) -> list[tuple[Coordinate, Schedule]]:
    """Generate initial candidates from the SearchSpace.

    Enumerates valid combinations of structural axis primitives,
    applies constraints, and returns (Coordinate, Schedule) pairs.

    Args:
        search_space: The canonical search space
        budget: Optional budget for cost filtering
        cost_model: Optional cost model for cost estimation
        max_candidates: Maximum number of candidates to return

    Returns:
        List of (Coordinate, Schedule) pairs for initial exploration.
    """
    # Group axes by kind (all axes in snapshot are structural axes)
    axes_by_kind: dict[StructuralAxis, list[AxisSpec]] = {}
    for axis in search_space.axes_snapshot:
        if axis.available:
            kind = axis.axis_kind
            if kind not in axes_by_kind:
                axes_by_kind[kind] = []
            axes_by_kind[kind].append(axis)

    # Get available primitives for each structural axis
    substrate_primitives = [
        a.name for a in axes_by_kind.get(StructuralAxis.SUBSTRATE, [])
    ]
    geometry_primitives = [
        a.name for a in axes_by_kind.get(StructuralAxis.GEOMETRY, [])
    ]
    dynamics_primitives = [
        a.name for a in axes_by_kind.get(StructuralAxis.DYNAMICS, [])
    ]
    plasticity_primitives = [
        a.name for a in axes_by_kind.get(StructuralAxis.PLASTICITY, [])
    ]
    credit_primitives = [a.name for a in axes_by_kind.get(StructuralAxis.CREDIT, [])]
    update_primitives = [a.name for a in axes_by_kind.get(StructuralAxis.UPDATE, [])]

    # Ensure we have at least one primitive per axis
    if not all([
        substrate_primitives,
        geometry_primitives,
        dynamics_primitives,
        plasticity_primitives,
        credit_primitives,
        update_primitives,
    ]):
        return []

    # Generate combinations (limit to avoid explosion)
    candidates = []
    for substrate in substrate_primitives[:3]:  # Limit per axis
        for geometry in geometry_primitives[:3]:
            for dynamics in dynamics_primitives[:3]:
                for plasticity in plasticity_primitives[:2]:
                    for credit in credit_primitives[:2]:
                        for update in update_primitives[:2]:
                            # Build default params for this combination
                            params = _build_default_params(
                                substrate,
                                geometry,
                                dynamics,
                                plasticity,
                                credit,
                                update,
                                search_space,
                            )

                            coord = Coordinate(
                                substrate=substrate,
                                geometry=geometry,
                                dynamics=dynamics,
                                plasticity=plasticity,
                                credit=credit,
                                update=update,
                                params=params,
                            )

                            # The schedule's task is the space's task: the
                            # evaluator resolves a task by name, so "default"
                            # would fail every cell (TODO46 §D2).
                            schedule = Schedule(
                                fidelity="L0",
                                seed=42,
                                n_seeds=1,
                                epochs=1,
                                batch_limit=0,
                                budget_id="initial",
                                task_id=search_space.tasks[0],
                            )

                            # Check budget
                            if budget and cost_model:
                                cost = cost_model.estimate_cost(
                                    (
                                        substrate,
                                        geometry,
                                        dynamics,
                                        plasticity,
                                        credit,
                                        update,
                                        params,
                                    ),
                                    schedule.to_dict(),
                                )
                                if budget.target_cost and cost > budget.target_cost:
                                    continue

                            candidates.append((coord, schedule))

                            if len(candidates) >= max_candidates:
                                return candidates

    return candidates

    return candidates


def _build_default_params(
    substrate: str,
    geometry: str,
    dynamics: str,
    plasticity: str,
    credit: str,
    update: str,
    search_space: SearchSpace,
) -> dict[str, Any]:
    """Build default topology params for a coordinate."""
    params = {}

    # Default values for common topology params
    defaults = {
        "input_dim": 784,
        "output_dim": 10,
        "hidden_dim": 64,
        "num_layers": 2,
        "num_heads": 4,
        "seq_len": 128,
        "neurons_per_tile": 16,
        "tiles_per_layer": 2,
        "conv_channels": 32,
        "kernel_size": 3,
        "lattice_dims": (4, 4, 4),
        "grid_hw": (8, 8),
        "mem_slots": 16,
        "mem_width": 32,
        "max_steps": 10,
        "convergence_threshold": 1e-3,
        "feedback_scale": 1.0,
        "ema_beta": 0.99,
        "contrast_threshold": 1.0,
        "a_plus": 0.5,
        "a_minus": 0.5,
        "tau_pre": 1.0,
        "tau_post": 1.0,
        "beta2": 0.999,
        "eps": 1e-8,
        "ortho_lr": 0.01,
        "ortho_steps": 5,
        "spectral_norm": 1.0,
        "ewc_lambda": 1000,
        "fisher_damping": 1e-3,
        "momentum": 0.9,
        "gate_dim": 32,
        "fast_weight_dim": 128,
        "num_operators": 4,
        "trace_decay": 0.9,
        "conflict_threshold": 0.5,
    }

    # Add params based on axis primitives
    # Geometry params
    if geometry in ("feedforward", "recurrent", "causal_transformer"):
        params.update({
            "input_dim": 784,
            "output_dim": 10,
            "hidden_dim": 64,
            "num_layers": 2,
        })
        if geometry == "causal_transformer":
            params["num_heads"] = 4
            params["seq_len"] = 128
    elif geometry in ("tile", "tile_mesh"):
        params.update({
            "input_dim": 784,
            "output_dim": 10,
            "neurons_per_tile": 16,
            "tiles_per_layer": 2,
        })
    elif geometry == "conv":
        params.update({
            "input_dim": 784,
            "output_dim": 10,
            "conv_channels": 32,
            "kernel_size": 3,
        })
    elif geometry == "spatial_lattice":
        params.update({
            "input_dim": 784,
            "output_dim": 10,
            "lattice_dims": (4, 4, 4),
        })
    elif geometry == "nca":
        params.update({
            "input_dim": 784,
            "output_dim": 10,
            "grid_hw": (8, 8),
        })
    elif geometry == "ntm":
        params.update({
            "input_dim": 784,
            "output_dim": 10,
            "mem_slots": 16,
            "mem_width": 32,
        })

    # Dynamics params
    if dynamics in (
        "energy_minimization",
        "predictive_settling",
        "error_predictive_coding",
        "diffusion",
        "pc_alm",
    ):
        params.update({
            "max_steps": 10,
            "convergence_threshold": 1e-3,
        })

    # Credit params
    if credit == "random_projections":
        params["feedback_scale"] = 1.0
    elif credit == "local_contrastive":
        params.update({
            "ema_beta": 0.99,
            "contrast_threshold": 1.0,
            "contrast_objective": "goodness",
        })
    elif credit == "temporal_trace":
        params.update({
            "a_plus": 0.5,
            "a_minus": 0.5,
            "tau_pre": 1.0,
            "tau_post": 1.0,
        })
    elif credit == "pepita":
        params["feedback_scale"] = 1.0

    # Update params
    if update in ("adam", "local_adam"):
        params.update({"beta2": 0.999, "eps": 1e-8})
    elif update == "ortho_adam":
        params.update({"beta2": 0.999, "eps": 1e-8, "ortho_lr": 0.01})
    elif update in ("riemannian_orthogonal", "muon"):
        params.update({"ortho_steps": 5, "momentum": 0.9})
    elif update == "lion":
        params.update({"beta2": 0.99, "eps": 1e-8})
    elif update == "spectral_constrained":
        params["spectral_norm"] = 1.0
    elif update == "elastic_consolidation":
        params.update({"ewc_lambda": 1000, "fisher_damping": 1e-3})
    elif update == "natural_gradient":
        params["fisher_damping"] = 1e-3

    # Plasticity params
    if plasticity == "routing":
        params["gate_dim"] = 32
    elif plasticity == "fast_weights":
        params["fast_weight_dim"] = 128
    elif plasticity == "rule_state":
        params["num_operators"] = 4
    elif plasticity in ("temporal_psi", "conflict_adaptive"):
        params["trace_decay"] = 0.9
        if plasticity == "conflict_adaptive":
            params["conflict_threshold"] = 0.5

    return params


def _satisfies_constraints(
    coord: Coordinate,
    constraints: tuple[ConstraintSpec, ...],
    schedule: Schedule | None = None,
) -> bool:
    """Check if a coordinate satisfies all constraints."""
    from computronium.experiment.legality.dsl import EvaluationContext
    from computronium.experiment.schema.coordinate import Provenance
    from computronium.experiment.schema.record import (
        FailureCause,
        GateVerdict,
        Maturity,
        Record,
        ReproducibilityClass,
        Severity,
        Status,
    )

    # Create a minimal record for constraint evaluation
    if schedule is None:
        schedule = Schedule(
            fidelity="L0",
            seed=42,
            n_seeds=1,
            epochs=1,
            batch_limit=0,
            budget_id="initial",
            task_id="default",
        )

    record = Record.create(
        run_id="constraint_check",
        coordinate=coord,
        schedule=schedule,
        provenance=Provenance(
            env={},
            dataset="test",
            dataset_version="1.0",
            code_sha="test",
            policy="test",
            links={},
        ),
        status=Status(
            gate_verdict=GateVerdict.PENDING,
            defect="",
            cause=FailureCause.UNKNOWN,
            severity=Severity.LOW,
            quarantine=False,
            maturity=Maturity.L0,
            uncertainty={},
            reproducibility=ReproducibilityClass.REPLAYABLE,
            assessment_procedure_version="1.0",
            ceec_link=None,
        ),
        payload={},
    )

    ctx = EvaluationContext(record)
    for constraint in constraints:
        if constraint.predicate is not None:
            try:
                result = evaluate(constraint.predicate, ctx)
                if not result:
                    return False
            except Exception:
                return False
    return True


@dataclass(frozen=True, slots=True)
class ProposalContext:
    """Context passed to every policy's propose()."""

    search_space: SearchSpace
    budget: Budget
    cost_model: CostModel
    evidence: RecordStore
    run_id: str


@dataclass(frozen=True, slots=True)
class Proposal:
    """Single proposal from a policy."""

    coordinate: Coordinate
    schedule: Schedule
    rationale: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def proposal_id(self) -> str:
        """Generate a unique ID for this proposal."""
        content = f"{self.coordinate.cell_key()}|{self.schedule.fidelity}|{self.schedule.seed}|{self.rationale}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class ProposalPolicy(Protocol):
    """Protocol for proposal policies."""

    def propose(self, ctx: ProposalContext) -> Iterator[Proposal]:
        """Generate proposals from the search space."""
        ...

    def observe(self, record: Record) -> None:
        """Incorporate a completed record into the policy's evidence base."""
        ...

    def get_name(self) -> str:
        """Return the policy name."""
        ...


@dataclass(frozen=True, slots=True)
class Decision:
    """Decision from S10 Decide stage."""

    transition: str  # CONTINUE | COMPLETE | PAUSE | STOP
    new_proposals: list[Proposal] = field(default_factory=list)
    promotions: list[Any] = field(default_factory=list)  # Promotion
    abandonments: list[Any] = field(default_factory=list)  # Abandonment
    replications: list[Any] = field(default_factory=list)  # Replication
    rationale: str = ""
    budget_impact: float = 0.0


@runtime_checkable
class Stage(Protocol):
    """Protocol for pipeline stages."""

    stage_id: StageId

    async def run(self, ctx: StageContext) -> Fragment:
        """Execute the stage and return a fragment."""
        ...


@dataclass(slots=True)
class StageContext:
    """Context passed to each stage during execution."""

    run_id: str
    run_spec: dict[str, Any]
    stage_id: StageId
    store: RecordStore
    budget: Budget
    cost_model: CostModel
    policy: Policy
    allocator: EvidenceDrivenAllocator | None
    backend: ExecutionBackend
    search_space: SearchSpace
    completed_keys: set[str]
    pending_proposals: list[Proposal]
    pending_candidates: list[tuple[Coordinate, Schedule]]
    in_progress: list[tuple[Coordinate, Schedule]]
    stage_params: dict[str, Any]
    provenance: Any  # Provenance
    system_context: SystemContext


@dataclass(frozen=True, slots=True)
class Fragment:
    """Output fragment from a stage execution."""

    stage_id: StageId
    records: list[Record] = field(default_factory=list)
    proposals: list[Proposal] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    coverage: dict[str, Any] = field(default_factory=dict)
    classification: dict[str, Any] = field(default_factory=dict)
    decisions: list[Any] = field(default_factory=list)  # Decision objects


# Forward references resolved at runtime
from computronium.experiment.execution.allocator import (
    EvidenceDrivenAllocator,  # noqa: E402
)
from computronium.experiment.execution.backends import ExecutionBackend  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.execution.stage import StageId  # ruff: ignore[module-import-not-at-top-of-file]
from computronium.experiment.execution.sysctx import SystemContext  # ruff: ignore[module-import-not-at-top-of-file]

__all__ = [
    "Decision",
    "Domain",
    "Fragment",
    "Proposal",
    "ProposalContext",
    "ProposalPolicy",
    "SearchSpace",
    "Stage",
    "StageContext",
    "generate_initial_candidates",
]
