"""Canonical search space and proposal abstractions (WP14).

The abc3 architecture specifies:
    Policy.propose(SearchContext) -> Iterator[Proposal]

with the wrapper applying legality and novelty uniformly.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass, field
from itertools import islice
from typing import TYPE_CHECKING, Any, Final, Protocol, runtime_checkable

from computronium.experiment.schema.axis import (
    AXES_REGISTRIES,
    AxisKind,
    Domain,
    Scale,
    StructuralAxis,
)
from computronium.experiment.schema.coordinate import Coordinate, Schedule
from computronium.experiment.schema.harvest import (
    AXIS_KIND_ORDER,
    HarvestedSchema,
    harvest_schema,
)
from computronium.experiment.schema.registries import PARAM_BUDGET_TOLERANCE

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.execution.evaluate import TaskShape
    from computronium.experiment.execution.policy import Policy
    from computronium.experiment.schema.axis import AxisSpec
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.registries import ConstraintSpec, ObjectiveSpec
    from computronium.experiment.schema.run_spec import RunSpec

# Values a spec-narrowed hyperparameter is swept across. The space is a
# continuum; a run proposes ``limit`` points on it.
_SWEEP_STEPS: Final = 5

type ShapeResolver = Callable[[str], TaskShape]

# A scan bound, not a space bound: guards against a budget or a predicate that
# admits nothing, which would otherwise make the candidate stream unbounded.
_MAX_SCAN: Final = 10_000


@dataclass(frozen=True, slots=True)
class SearchSpace:
    """The active space of one run: the primitives, objectives and tasks it may use.

    Built by :func:`search_space_from_spec`, so the snapshot is what the spec
    permits — not every registry row.
    """

    axes_snapshot: tuple[AxisSpec, ...]
    constraints: tuple[ConstraintSpec, ...]
    objectives: tuple[ObjectiveSpec, ...]
    tasks: tuple[str, ...]

    def primitives(self, axis: StructuralAxis) -> tuple[str, ...]:
        """The primitives this space offers on one structural axis."""
        return tuple(s.name for s in self.axes_snapshot if s.axis_kind is axis)


def search_space_from_spec(
    spec: RunSpec, *, tasks: Sequence[str] | None = None
) -> SearchSpace:
    """The run's active space, read from its spec and the registries.

    Args:
        spec: The validated run declaration.
        tasks: Task override; defaults to the spec's own task names.

    Returns:
        SearchSpace whose axes snapshot holds exactly the primitives the spec
        permits, and whose objectives are the ones it names (all, if it names
        none).
    """
    from computronium.experiment.schema.registries import (
        CONSTRAINTS_REGISTRY,
        OBJECTIVES_REGISTRY,
    )

    axes_snapshot: list[AxisSpec] = []
    for axis in StructuralAxis:
        for name in spec.selected_primitives(axis):
            axis_spec = AXES_REGISTRIES[axis].get(name)
            if axis_spec is not None and axis_spec.available:
                axes_snapshot.append(axis_spec)

    objectives = tuple(
        OBJECTIVES_REGISTRY[name]
        for name in spec.objectives
        if name in OBJECTIVES_REGISTRY
    ) or tuple(OBJECTIVES_REGISTRY.values())

    return SearchSpace(
        axes_snapshot=tuple(axes_snapshot),
        constraints=tuple(CONSTRAINTS_REGISTRY.values()),
        objectives=objectives,
        tasks=tuple(tasks or spec.task_names),
    )


def _lerp(lo: float, hi: float, t: float) -> float:
    return lo + (hi - lo) * t


def narrow_domain(spec_domain: Domain, harvested: Domain, name: str) -> Domain:
    """Intersect a spec's domain with the harvested one.

    The harvested declaration is the primitive's truth; the spec may only
    narrow it. A spec asking for values the primitive does not declare is a
    typo, not a wider search.
    """
    if spec_domain.members is not None or harvested.members is not None:
        members = tuple(spec_domain.members or harvested.members or ())
        legal = set(harvested.members or members)
        illegal = [m for m in members if m not in legal]
        if illegal:
            msg = (
                f"hyperparameter {name!r} has no member(s) {illegal} in the "
                f"harvested domain {list(harvested.members or members)}"
            )
            raise ValueError(msg)
        return Domain(members=members)
    lo = max(float(spec_domain.lo), float(harvested.lo))  # type: ignore[arg-type]
    hi = min(float(spec_domain.hi), float(harvested.hi))  # type: ignore[arg-type]
    if lo >= hi:
        msg = (
            f"hyperparameter {name!r} domain "
            f"({spec_domain.lo}, {spec_domain.hi}) lies outside the harvested "
            f"domain ({harvested.lo}, {harvested.hi})"
        )
        raise ValueError(msg)
    return Domain(
        lo=lo,
        hi=hi,
        scale=(
            Scale.LOG
            if {spec_domain.scale, harvested.scale} == {Scale.LOG}
            else Scale.LINEAR
        ),
    )


def _ladder(
    domain: Domain, kind: AxisKind, steps: int = _SWEEP_STEPS
) -> tuple[Any, ...]:
    """Evenly spaced legal values across a domain, log-spaced when it declares LOG."""
    if domain.members is not None:
        return tuple(domain.members[:steps])
    lo, hi = float(domain.lo), float(domain.hi)  # type: ignore[arg-type]
    fractions = [i / (steps - 1) for i in range(steps)]
    if domain.scale is Scale.LOG:
        values = [10 ** _lerp(math.log10(lo), math.log10(hi), t) for t in fractions]
    else:
        values = [_lerp(lo, hi, t) for t in fractions]
    if kind is AxisKind.INTEGER:
        return tuple(dict.fromkeys(round(v) for v in values))
    return tuple(values)


def _swept(spec: RunSpec, schema: HarvestedSchema) -> dict[str, tuple[Any, ...]]:
    """Every hyperparameter the spec narrowed, with its ladder of legal values.

    Un-swept hyperparameters stay absent from the coordinate and are resolved
    by ``harvest_schema().active()`` at composition time, from prior and domain.
    """
    specs_by_name = schema.by_name()
    return {
        name: _ladder(
            narrow_domain(domain, specs_by_name[name].domain, name),
            specs_by_name[name].axis_kind,
        )
        for name, domain in spec.hyperparameters.items()
    }


def _cell_params(
    coordinate: Coordinate,
    schema: HarvestedSchema,
    ladders: dict[str, tuple[Any, ...]],
    stride: int,
) -> dict[str, Any]:
    """The swept values this coordinate can actually use.

    A value is carried only when the coordinate's own selection both activates
    the hyperparameter and reads it: carrying it otherwise is dead config,
    which the harvest already refuses elsewhere.
    """
    active = schema.active(coordinate)
    axis_of = {
        spec.name: StructuralAxis(spec.axis_name) for spec in schema.hyperparameters
    }
    usable: dict[str, Any] = {}
    for name, ladder in ladders.items():
        axis = axis_of[name]
        if name not in active.for_axis(axis, getattr(coordinate, axis.value)):
            continue
        usable[name] = ladder[stride % len(ladder)]
    return usable


def _composable(
    coordinate: Coordinate, task: str, shape: ShapeResolver, param_budget: int
) -> bool:
    """Whether the cell's configs compose and validate for this task's shape.

    Legality is asked of the one mechanism that owns it —
    ``SystemConfig.validate``, reached through ``compose_configs`` — rather than
    re-declared here as availability predicates, which would be a second source
    of truth for the same rules. A cell that cannot compose is not a cheap
    failure to discover after a training run.

    ``param_budget`` is the schedule's ceiling, so the space screens a cell at
    the size the evaluator will train it; a space that screens a small cell and
    a large one is the two-channel defect D5 named.
    """
    from computronium.experiment.execution.compose import (
        compose_configs,
        geometry_param_count,
    )

    task_shape = shape(task)
    try:
        config = compose_configs(
            coordinate=coordinate,
            geometry={},
            input_shape=task_shape.input_shape,
            output_dim=task_shape.output_dim,
            param_budget=param_budget,
        )
    except ValueError, TypeError, KeyError:
        return False
    if param_budget <= 0:
        return True
    # The same R25 fairness rule the evaluator's gate applies, asked here so a
    # cell that cannot honour its ceiling is never proposed: a cell that cannot
    # fit is discovered by training, which is the expensive way to find out.
    return geometry_param_count(config.geometry) <= param_budget * (
        1 + PARAM_BUDGET_TOLERANCE
    )


def _schedule(spec: RunSpec, task: str) -> Schedule:
    """The cell's schedule, from the spec rather than from a literal."""
    return Schedule(
        fidelity=spec.fidelity,
        seed=spec.seed,
        n_seeds=spec.n_seeds,
        epochs=spec.epochs,
        batch_limit=spec.batch_limit,
        budget_id="initial",
        task_id=task,
        param_budget=spec.param_budget,
    )


def iter_candidates(
    spec: RunSpec,
    search_space: SearchSpace,
    *,
    budget: Budget | None = None,
    cost_model: CostModel | None = None,
    shape: ShapeResolver | None = None,
) -> Iterator[tuple[Coordinate, Schedule]]:
    """Walk the harvested schema under the spec, yielding legal cells.

    The active space is computed, never tabulated: each axis offers the
    primitives the spec permits, the harvested availability predicates decide
    which hyperparameters a selection can use, and the spec's own domains are
    swept. Candidate ``k`` takes the ``k``-th primitive on every axis, so a
    short prefix of the stream varies every axis rather than exhausting one.

    Args:
        spec: The run declaration; names the task, fidelity, seed plan and the
            hyperparameters to sweep.
        search_space: The run's active space.
        budget: Optional ceiling; a cell estimated above it is skipped.
        cost_model: Required with ``budget`` to estimate a cell's cost.
        shape: Resolves a task's ``(input_dim, output_dim)``. When given, a
            cell whose configs cannot compose or validate for that shape is
            skipped instead of proposed.

    Yields:
        ``(coordinate, schedule)`` pairs, in a deterministic order.
    """
    per_axis = {axis: search_space.primitives(axis) for axis in AXIS_KIND_ORDER}
    if not search_space.tasks or not all(per_axis.values()):
        return
    schema = harvest_schema()
    ladders = _swept(spec, schema)
    tasks = search_space.tasks
    seen: set[str] = set()

    for k in range(_MAX_SCAN):
        selection = {
            axis.value: names[k % len(names)] for axis, names in per_axis.items()
        }
        coordinate = Coordinate(**selection, params={})
        params = _cell_params(coordinate, schema, ladders, k // len(selection))
        coordinate = Coordinate(**selection, params=params)
        schedule = _schedule(spec, tasks[k % len(tasks)])
        if coordinate.measurement_key(schedule) in seen:
            continue
        seen.add(coordinate.measurement_key(schedule))

        if shape is not None and not _composable(
            coordinate, schedule.task_id, shape, schedule.param_budget
        ):
            continue
        if budget is not None and cost_model is not None:
            cost = cost_model.estimate_cost(
                (
                    selection["substrate"],
                    selection["geometry"],
                    selection["dynamics"],
                    selection["plasticity"],
                    selection["credit"],
                    selection["update"],
                    params,
                ),
                schedule.to_dict(),
            )
            if budget.target_cost and cost > budget.target_cost:
                continue
        yield coordinate, schedule


def generate_candidates(
    spec: RunSpec,
    search_space: SearchSpace,
    *,
    budget: Budget | None = None,
    cost_model: CostModel | None = None,
    shape: ShapeResolver | None = None,
    limit: int = 10,
) -> list[tuple[Coordinate, Schedule]]:
    """The first ``limit`` cells of :func:`iter_candidates`."""
    stream = iter_candidates(
        spec, search_space, budget=budget, cost_model=cost_model, shape=shape
    )
    return list(islice(stream, limit))


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
    run_spec: RunSpec
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
    "Fragment",
    "Proposal",
    "ProposalContext",
    "ProposalPolicy",
    "SearchSpace",
    "Stage",
    "StageContext",
    "generate_candidates",
    "iter_candidates",
    "narrow_domain",
    "search_space_from_spec",
]
