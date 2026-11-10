"""The active search space, computed from a run's own declaration.

The abc3 architecture specifies
``Policy.propose(SearchContext) -> Iterator[Proposal]``: a policy *generates*
cells from the space rather than choosing from a list handed to it
(TODO46 §3.3, WP14). This module is what it generates them from.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from itertools import islice
from typing import TYPE_CHECKING, Any, Final

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
    from computronium.experiment.kernel.evaluate import TaskShape
    from computronium.experiment.legality.dsl import Expr
    from computronium.experiment.schema.axis import AxisSpec
    from computronium.experiment.schema.registries import ConstraintSpec, ObjectiveSpec
    from computronium.experiment.schema.run_spec import RunSpec

# Values a spec-narrowed hyperparameter is swept across. The space is a
# continuum; a run proposes ``limit`` points on it.
_SWEEP_STEPS: Final = 5

type ShapeResolver = Callable[[str], TaskShape]

# Default page size for paging through the candidate space. This is a page
# size, NOT a cap — the stream advances across pages indefinitely.
_PAGE_SIZE: Final = 50_000

# Module-level cache for search_space_from_spec
_search_space_cache: dict[tuple, SearchSpace] = {}

# Module-level cache for _filter_axes_for_validity
_filter_axes_cache: dict[tuple, dict[str, list[str]]] = {}

# Axis positions in the tuple consumed by the compiled constraint evaluators
# (substrate, geometry, dynamics, plasticity, credit, update, task).
_AXIS_INDICES: Final = {
    "substrate": 0,
    "geometry": 1,
    "dynamics": 2,
    "plasticity": 3,
    "credit": 4,
    "update": 5,
    "task": 6,
}


def _compile_expr(expr: Expr) -> Callable[[tuple[str, ...]], Any]:  # ruff: ignore[complex-structure, too-many-return-statements]
    """Compile a legality DSL expression to a function of the axis-value tuple."""
    from computronium.experiment.legality.dsl import (
        And,
        Const,
        Eq,
        Gt,
        HasKey,
        In,
        Not,
        NotIn,
        Or,
        Var,
    )

    match expr:
        case Var(name=name):
            return lambda vals: vals[_AXIS_INDICES[name]]
        case Const(value=value):
            return lambda _vals: value
        case Eq(left=left, right=right):
            lf, rf = _compile_expr(left), _compile_expr(right)
            return lambda vals: lf(vals) == rf(vals)
        case In(left=left, right=right):
            lf, rf = _compile_expr(left), _compile_expr(right)
            return lambda vals: lf(vals) in rf(vals)
        case NotIn(left=left, right=right):
            lf, rf = _compile_expr(left), _compile_expr(right)
            return lambda vals: lf(vals) not in rf(vals)
        case And(left=left, right=right):
            lf, rf = _compile_expr(left), _compile_expr(right)
            return lambda vals: lf(vals) and rf(vals)
        case Or(left=left, right=right):
            lf, rf = _compile_expr(left), _compile_expr(right)
            return lambda vals: lf(vals) or rf(vals)
        case Not(expr=child):
            cf = _compile_expr(child)
            return lambda vals: not cf(vals)
        case Gt(left=left, right=right):
            lf, rf = _compile_expr(left), _compile_expr(right)
            return lambda vals: lf(vals) > rf(vals)
        case HasKey():
            return lambda _vals: True
        case _:
            raise ValueError(f"Unknown expr type: {type(expr)}")


def _compiled_void_constraints() -> tuple[
    list[Callable[[tuple[str, ...]], Any]], list[Callable[[tuple[str, ...]], Any]]
]:
    """Compiled ``(task-independent, task-dependent)`` void constraint evaluators.

    Task-independent constraints never read ``task`` and are checked once per
    candidate; task-dependent ones are checked for the candidate's own task.
    Constraints reading hyperparameters are excluded here — the caller
    evaluates those only once the cell is composed.
    """
    from computronium.experiment.legality.dsl import references_params
    from computronium.experiment.schema.registries import CONSTRAINTS_REGISTRY

    indep: list[Callable[[tuple[str, ...]], Any]] = []
    dep: list[Callable[[tuple[str, ...]], Any]] = []
    for constraint in CONSTRAINTS_REGISTRY.values():
        if constraint.kind.value != "void":
            continue
        pred = constraint.predicate
        if pred is None or references_params(pred):
            continue
        fn = _compile_expr(pred)
        (dep if "task" in str(pred) else indep).append(fn)
    return indep, dep


def _void_pass(
    indep: list[Callable[[tuple[str, ...]], Any]],
    dep: list[Callable[[tuple[str, ...]], Any]],
    values: tuple[str, ...],
    task: str,
) -> bool:
    """Whether a structural selection satisfies every void constraint."""
    indep_vals = (*values, "")
    task_vals = (*values, task)
    return all(fn(indep_vals) for fn in indep) and all(fn(task_vals) for fn in dep)


def _void_cache_key(coordinate: Coordinate) -> tuple[str, ...]:
    """Create a cache key for a coordinate based on structural axes only."""
    return (
        coordinate.substrate,
        coordinate.geometry,
        coordinate.dynamics,
        coordinate.plasticity,
        coordinate.credit,
        coordinate.update,
    )


def _is_substrate_dynamics_compatible(substrate: str, dynamics: str) -> bool:
    """Check if a substrate-dynamics combination is valid.

    This is a defense-in-depth check that mirrors the void constraints in
    CONSTRAINTS_REGISTRY. It catches invalid combinations that might slip
    through the compiled constraint evaluation.

    Args:
        substrate: Substrate primitive name
        dynamics: Dynamics primitive name

    Returns:
        True if the combination is valid, False otherwise.
    """
    # Neuromorphic substrate requires temporal dynamics
    if substrate == "neuromorphic":
        if dynamics not in {"spike_integration", "energy_minimization", "diffusion"}:
            return False

    # Quantum substrate requires compatible dynamics
    if substrate == "quantum":
        if dynamics not in {"energy_minimization", "instantaneous", "diffusion"}:
            return False

    # Ternary substrate incompatible with pc_alm
    if substrate == "ternary" and dynamics == "pc_alm":
        return False

    return True


def _is_geometry_dynamics_compatible(geometry: str, dynamics: str) -> bool:
    """Check if a geometry-dynamics combination is valid.

    Mirrors void constraints: recurrent geometry requires settling dynamics,
    non-layered geometries require instantaneous dynamics.
    """
    # Recurrent geometry requires settling dynamics
    if geometry in {"recurrent", "recurrent_attractor"} and dynamics not in {
        "energy_minimization",
        "predictive_settling",
        "error_predictive_coding",
        "pc_alm",
        "diffusion",
        "instantaneous",
    }:
        return False

    # Non-layered geometries require instantaneous dynamics
    if (
        geometry
        in {
            "attention",
            "spatial_lattice",
            "graph",
            "conv",
            "nca",
            "ntm",
            "causal_transformer",
            "tile",
            "tile_mesh",
        }
        and dynamics != "instantaneous"
    ):
        return False

    return True


def _is_geometry_task_compatible(
    geometry: str, task_shape: TaskShape, task_id: str | None = None
) -> bool:
    """Check if a geometry is compatible with a task's input shape.

    Some geometries require specific input structures (e.g., NTM needs 1D,
    Graph needs graph structure, Tile needs specific spatial dims).
    """
    input_shape = task_shape.input_dim
    if isinstance(input_shape, int):
        ndim = 1
    else:
        ndim = len(input_shape)

    # Graph geometry requires graph structure (edge_index) - only for graph tasks
    if geometry == "graph":
        # Allow graph geometry for graph domain tasks
        if task_id is not None:
            from computronium.experiment.registry.task_registry import get_task_registry

            registry = get_task_registry()
            task_spec = registry.get(task_id)
            if task_spec.domain.value == "graph":
                return True
        return False  # Non-graph tasks don't provide graph structure

    # Causal transformer expects 1D sequence
    if geometry == "causal_transformer":
        return ndim == 1

    # All other geometries can handle vision input (they flatten or process spatially)
    return True


class VoidCache:
    """Persists void combinations across experiment runs.

    A void combination is a 6-axis coordinate that is known to be invalid
    (e.g., fails void constraints). By caching these, we avoid re-evaluating
    them in future runs.

    The cache is persisted to a JSON file for durability across processes.
    When no db_path is provided, the cache is in-memory only and not shared
    between instances (suitable for testing).
    """

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path
        self._void_combos: set[tuple[str, ...]] = set()
        if db_path is not None:
            self._load()

    def _load(self) -> None:
        """Load void cache from disk."""
        if self._db_path is None:
            return
        import json
        from pathlib import Path

        path = Path(self._db_path)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self._void_combos = {tuple(k) for k in data.get("void_combos", [])}
            except json.JSONDecodeError, KeyError, TypeError:
                self._void_combos = set()

    def _save(self) -> None:
        """Save void cache to disk."""
        if self._db_path is None:
            return
        import json
        from pathlib import Path

        path = Path(self._db_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {"void_combos": [list(k) for k in self._void_combos]}
        path.write_text(json.dumps(data), encoding="utf-8")

    def is_known_void(self, coord: Coordinate) -> bool:
        """Check if a coordinate is a known void combination."""
        return _void_cache_key(coord) in self._void_combos

    def record_void(self, coord: Coordinate) -> None:
        """Record a void combination."""
        self._void_combos.add(_void_cache_key(coord))
        self._save()

    def get_void_count(self) -> int:
        """Get the number of known void combinations."""
        return len(self._void_combos)

    def clear(self) -> None:
        """Clear the void cache."""
        self._void_combos.clear()
        if self._db_path is not None:
            from pathlib import Path

            Path(self._db_path).unlink(missing_ok=True)


def get_void_cache(db_path: str | None = None) -> VoidCache:
    """Get a void cache instance.

    If db_path is provided, the cache is persisted to/loaded from that file.
    If db_path is None, an in-memory-only cache is returned (not shared between
    instances, suitable for testing).
    """
    return VoidCache(db_path)


def _search_space_cache_key(spec: RunSpec, tasks: Sequence[str] | None) -> tuple:
    """Create a cache key for search_space_from_spec."""
    # Key includes: selected primitives per axis, tasks, objectives
    axes_key = tuple(
        (axis.value, tuple(sorted(spec.selected_primitives(axis))))
        for axis in StructuralAxis
    )
    tasks_key = tuple(sorted(tasks or spec.task_names))
    objectives_key = tuple(sorted(spec.objectives))
    return (axes_key, tasks_key, objectives_key)


def _filter_axes_cache_key(
    axes_snapshot: list, spec: RunSpec, tasks: Sequence[str] | None = None
) -> tuple:
    """Create a cache key for _filter_axes_for_validity."""
    # Key includes: axis names per axis kind, ALL tasks (not just first)
    axes_key = tuple(
        tuple(sorted(s.name for s in axes_snapshot if s.axis_kind == axis))
        for axis in StructuralAxis
    )
    task_key = (
        tuple(sorted(tasks or spec.task_names)) if (tasks or spec.task_names) else ()
    )
    return (axes_key, task_key)


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

    def primitives(self, axis: StructuralAxis | str) -> tuple[str, ...]:
        """The primitives this space offers on one structural axis."""
        if isinstance(axis, str):
            try:
                axis = StructuralAxis(axis)
            except ValueError:
                return ()
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
    from computronium.experiment.schema.seed_registries import seed_all_registries

    # Ensure all registries are seeded (especially CONSTRAINTS_REGISTRY which isn't lazy)
    seed_all_registries()

    # Check cache
    cache_key = _search_space_cache_key(spec, tasks)
    if cache_key in _search_space_cache:
        return _search_space_cache[cache_key]

    axes_snapshot: list[AxisSpec] = []
    for axis in StructuralAxis:
        for name in spec.selected_primitives(axis):
            axis_spec = AXES_REGISTRIES[axis].get(name)
            if axis_spec is not None and axis_spec.available:
                axes_snapshot.append(axis_spec)

    # Pre-filter structural axes to only include primitives that participate
    # in at least one valid combination (avoids iterating 100k+ invalid combos)
    axes_snapshot = _filter_axes_for_validity(axes_snapshot, spec, tasks)

    objectives = tuple(
        OBJECTIVES_REGISTRY[name]
        for name in spec.objectives
        if name in OBJECTIVES_REGISTRY
    ) or tuple(OBJECTIVES_REGISTRY.values())

    space = SearchSpace(
        axes_snapshot=tuple(axes_snapshot),
        constraints=tuple(CONSTRAINTS_REGISTRY.values()),
        objectives=objectives,
        tasks=tuple(tasks or spec.task_names),
    )

    # Cache the result
    _search_space_cache[cache_key] = space
    return space


def _filter_axes_for_validity(  # ruff: ignore[complex-structure, too-many-statements]
    axes_snapshot: list[AxisSpec],
    spec: RunSpec,
    tasks: Sequence[str] | None = None,
) -> list[AxisSpec]:
    """Filter axis primitives to only those with at least one valid combination.

    Computes valid 6-tuples from all void constraints in CONSTRAINTS_REGISTRY,
    then derives per-axis valid primitives from the valid tuples.

    Uses compiled constraint functions for fast evaluation (~50x speedup over
    interpreter-based evaluation). Conservative: no primitive the exact path
    accepts may be dropped.

    Every primitive is kept only if it participates in at least one legal
    combination of the declared space. A primitive that cannot compose with the
    rest of the declaration is unreachable, whether the declaration named it or
    inherited it.
    """
    from itertools import product

    from computronium.experiment.schema.axis import StructuralAxis

    # Check cache
    cache_key = _filter_axes_cache_key(axes_snapshot, spec, tasks)
    if cache_key in _filter_axes_cache:
        cached = _filter_axes_cache[cache_key]
        valid_names_by_axis = {
            axis.value: set(cached[axis.value]) for axis in StructuralAxis
        }
        return [
            axis_spec
            for axis_spec in axes_snapshot
            if axis_spec.name
            in valid_names_by_axis.get(axis_spec.axis_kind.value, set())
            or not valid_names_by_axis.get(axis_spec.axis_kind.value)
        ]

    # Group primitives by axis
    primitives_by_axis: dict[StructuralAxis, list[str]] = {}
    for axis_spec in axes_snapshot:
        primitives_by_axis.setdefault(axis_spec.axis_kind, []).append(axis_spec.name)

    # Get all void constraints that can be evaluated at search space time
    task_indep_fns, task_dep_fns = _compiled_void_constraints()

    # If no void constraints, keep all primitives
    if not task_indep_fns and not task_dep_fns:
        return axes_snapshot

    axes_order = list(StructuralAxis)
    axis_primitives = [primitives_by_axis.get(axis, []) for axis in axes_order]

    # Quick exit if any axis has no primitives
    if not all(axis_primitives):
        return axes_snapshot

    task_list = tasks or spec.task_names

    valid_tuples: set[tuple[str, ...]] = set()
    valid_by_axis = {axis: set() for axis in axes_order}

    for values in product(*axis_primitives):
        if not all(fn((*values, "")) for fn in task_indep_fns):
            continue
        task_ok = any(
            all(fn((*values, task_name)) for fn in task_dep_fns)
            for task_name in task_list
        )
        if task_ok:
            valid_tuples.add(values)
            for axis, name in zip(axes_order, values, strict=True):
                valid_by_axis[axis].add(name)

    _filter_axes_cache[cache_key] = {
        axis.value: list(names) for axis, names in valid_by_axis.items()
    }

    return [
        axis_spec
        for axis_spec in axes_snapshot
        if axis_spec.name in valid_by_axis.get(axis_spec.axis_kind, set())
        or not valid_by_axis.get(axis_spec.axis_kind)
    ]


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


def _max_hidden_dim(
    param_budget: int, input_dim: int, output_dim: int, num_layers: int = 1
) -> int:
    """Estimate maximum hidden_dim that fits within param_budget.

    For recurrent/feedforward geometry:
    - Parameters ≈ input_dim * hidden_dim + hidden_dim^2 * (num_layers - 1) + hidden_dim * output_dim + hidden_dim (bias)
    - Simplified: hidden_dim * (input_dim + hidden_dim * (num_layers - 1) + output_dim + 1) <= param_budget

    Args:
        param_budget: Maximum parameter count
        input_dim: Input dimension
        output_dim: Output dimension
        num_layers: Number of layers (default 1)

    Returns:
        Maximum hidden_dim that fits within budget
    """
    if param_budget <= 0:
        return 4096  # Unconstrained, use harvested domain max

    if num_layers <= 1:
        denom = input_dim + output_dim + 1
        return max(8, min(4096, param_budget // max(1, denom)))
    a = num_layers - 1
    b = input_dim + output_dim + 1
    c = param_budget
    # Positive root: (-b + sqrt(b^2 + 4ac)) / (2a)
    import math

    disc = b * b + 4 * a * c
    if disc < 0:
        return 8
    root = (-b + math.sqrt(disc)) / (2 * a)
    return max(8, min(4096, int(root)))


def _swept(
    spec: RunSpec, schema: HarvestedSchema, shape: ShapeResolver | None = None
) -> dict[str, tuple[Any, ...]]:
    """Every hyperparameter the spec narrowed, with its ladder of legal values.

    Keys are canonical ``"{axis}.{name}"``. Un-swept hyperparameters stay absent
    from the coordinate and are resolved by ``harvest_schema().active()`` at
    composition time, from prior and domain.
    """
    specs_by_key = schema.by_name()

    # Compute task shape for param_budget-aware domain narrowing
    task_shape = None
    if shape is not None and spec.task_names:
        task_shape = shape(spec.task_names[0])

    # Build effective domains, narrowing geometry.hidden_dim by param_budget
    effective_domains: dict[str, Domain] = dict(spec.hyperparameters)

    if (
        "geometry.hidden_dim" not in effective_domains
        and spec.param_budget > 0
        and task_shape is not None
    ):
        max_h = _max_hidden_dim(
            spec.param_budget, task_shape.input_dim, task_shape.output_dim
        )
        from computronium.experiment.schema.axis import Domain, Scale

        effective_domains["geometry.hidden_dim"] = Domain(
            lo=8, hi=max_h, scale=Scale.LOG
        )

    sweep_steps = getattr(spec, "sweep_steps", 5)
    return {
        key: _ladder(
            narrow_domain(domain, specs_by_key[key].domain, key),
            specs_by_key[key].axis_kind,
            steps=sweep_steps,
        )
        for key, domain in effective_domains.items()
    }


def _cell_params(
    coordinate: Coordinate,
    schema: HarvestedSchema,
    ladders: dict[str, tuple[Any, ...]],
    stride: int,
) -> dict[str, Any]:
    """The swept values this coordinate can actually use, by canonical key.

    A value is carried only when the coordinate's own selection both activates
    the hyperparameter and reads it: carrying it otherwise is dead config,
    which the harvest already refuses elsewhere. "Reads it" is asked of the one
    authority that declares it — ``ActiveSpace.for_axis`` over
    ``AxisSpec.accepted_params`` — which composition reads the same way, so a
    carried value is exactly one composition applies.
    """
    active = schema.active(coordinate)
    by_key = {f"{spec.axis_name}.{spec.name}": spec for spec in schema.hyperparameters}
    usable: dict[str, Any] = {}
    for key, ladder in ladders.items():
        spec = by_key[key]
        axis = StructuralAxis(spec.axis_name)
        if spec.name not in active.for_axis(axis, getattr(coordinate, axis.value)):
            continue
        usable[key] = ladder[stride % len(ladder)]
    return usable


# Module-level cache for _composable results
_composable_cache: dict[tuple, bool] = {}


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

    Uses a module-level cache since the same (coordinate, task, param_budget)
    combinations are checked repeatedly during search space traversal.

    The cache key includes hyperparameters that affect validity checks in
    SystemConfig.validate(): hidden_dim, num_layers, max_steps, beta, residual.
    """
    from computronium.experiment.kernel.compose import (
        compose_configs,
        geometry_param_count,
    )
    from computronium.experiment.kernel.evaluate import _task

    validity_params = frozenset(
        (k, v)
        for k, v in coordinate.params.items()
        if k.split(".", 1)[-1]
        in {"hidden_dim", "num_layers", "max_steps", "beta", "residual"}
    )
    cache_key = (
        coordinate.substrate,
        coordinate.geometry,
        coordinate.dynamics,
        coordinate.plasticity,
        coordinate.credit,
        coordinate.update,
        task,
        param_budget,
        validity_params,
    )

    if cache_key in _composable_cache:
        return _composable_cache[cache_key]

    task_shape = shape(task)
    # Get task instance for graph edge_index extraction (cached)
    task_instance = _task(task, "cpu")
    try:
        config = compose_configs(
            coordinate=coordinate,
            geometry={},
            input_shape=task_shape.input_shape,
            output_dim=task_shape.output_dim,
            param_budget=param_budget,
            task=task_instance,
        )
    except ValueError, TypeError, KeyError:
        _composable_cache[cache_key] = False
        return False

    # The same R25 fairness rule the evaluator's gate applies, asked here so a
    # cell that cannot honour its ceiling is never proposed: a cell that cannot
    # fit is discovered by training, which is the expensive way to find out.
    if param_budget > 0:
        result = geometry_param_count(config.geometry) <= param_budget * (
            1 + PARAM_BUDGET_TOLERANCE
        )
        if not result:
            _composable_cache[cache_key] = False
            return False

    # Dry-run gate: verify the cell can actually train (catches detached graphs,
    # FA contract failures, no-gradient-reached, etc.)
    # Run unconditionally - default param_budget=0 must not disable the gate.
    from computronium.experiment.kernel.compose import _dry_run_trainable

    dry_ok, _dry_reason = _dry_run_trainable(
        coordinate=coordinate,
        geometry={},
        input_shape=task_shape.input_shape,
        output_dim=task_shape.output_dim,
        param_budget=param_budget,
        task=task_instance,
    )
    if not dry_ok:
        _composable_cache[cache_key] = False
        return False

    _composable_cache[cache_key] = True
    return True


def schedule_for(
    spec: RunSpec,
    task: str,
    fidelity: str,
) -> Schedule:
    """Create a Schedule from spec for a given task and fidelity.

    Precedence (highest first):
    1. Explicit spec.n_seeds / spec.epochs (CLI set them)
    2. spec.fidelity_seeds[fidelity] / spec.fidelity_epochs[fidelity]
    3. Ladder defaults: L0=1/1, L1=3/5, L2=5/20
    """
    fidelity_seeds = spec.fidelity_seeds or {}
    fidelity_epochs = spec.fidelity_epochs or {}

    # Ladder defaults
    ladder_seeds = {"L0": 1, "L1": 3, "L2": 5}
    ladder_epochs = {"L0": 1, "L1": 5, "L2": 20}

    # n_seeds: explicit > fidelity > ladder
    if (
        spec.n_seeds is not None and spec.n_seeds != 1
    ):  # 1 is the default, so check if explicitly set
        n_seeds = spec.n_seeds
    elif fidelity in fidelity_seeds:
        n_seeds = fidelity_seeds[fidelity]
    else:
        n_seeds = ladder_seeds.get(fidelity, 1)

    # epochs: explicit > fidelity > ladder
    if spec.epochs is not None and spec.epochs != 1:  # 1 is the default
        epochs = spec.epochs
    elif fidelity in fidelity_epochs:
        epochs = fidelity_epochs[fidelity]
    else:
        epochs = ladder_epochs.get(fidelity, 1)

    return Schedule(
        fidelity=fidelity,
        seed=spec.seed,
        n_seeds=n_seeds,
        epochs=epochs,
        batch_limit=spec.batch_limit,
        budget_id=f"{fidelity}_initial",
        task_id=task,
        param_budget=spec.param_budget,
        device=spec.device,
        deterministic=spec.deterministic,
        num_workers=spec.num_workers,
        precision=spec.precision,  # type: ignore[arg-type]
        checkpoint_every_n=spec.checkpoint_every_n,
        early_stopping_patience=spec.early_stopping_patience,
    )


def _schedule(spec: RunSpec, task: str) -> Schedule:
    """The cell's schedule, from the spec rather than from a literal.

    Deprecated: use schedule_for(spec, task, spec.fidelity) instead.
    """
    return schedule_for(spec, task, spec.fidelity)


def declared_cell_count(spec: RunSpec, space: SearchSpace) -> int:
    """How many cells the spec declares, before legality or budget filter it.

    A consumer that wants a bounded window of the space needs this to stride
    it: the head of a factorial is one setting of its outer axes, so a prefix
    is not a sample of the space, it is a corner of it.
    """
    per_axis = [len(space.primitives(axis)) for axis in AXIS_KIND_ORDER]
    if not space.tasks or not all(per_axis):
        return 0
    ladders = _swept(spec, harvest_schema(), None)
    steps = max((len(ladder) for ladder in ladders.values()), default=1)
    return math.prod(per_axis) * len(space.tasks) * steps


def _decode_index(index: int, radices: Sequence[int]) -> tuple[int, ...]:
    """Mixed-radix decode; the last radix varies fastest."""
    digits = [0] * len(radices)
    for i in range(len(radices) - 1, -1, -1):
        digits[i] = index % radices[i]
        index //= radices[i]
    return tuple(digits)


_GOLDEN: Final = 0.6180339887498949


def _diverse_permutation(total: int, seed: int) -> tuple[int, int]:
    """An affine bijection ``k -> (a*k + b) mod total`` spread by the golden ratio.

    ``a`` is coprime to ``total`` (so the map visits every index exactly once)
    and near ``total * phi`` (so consecutive k land far apart in the space).
    This replaces a row-major Cartesian sweep, whose first ~124k cells were all
    illegal for ``production-map`` because the slowest axis (geometry) locked
    into the non-layered values while dynamics cycled. A golden-spaced walk
    samples all axes at once and reaches legal cells within the first handful.

    ``b`` is a seeded offset so two seeds traverse the same space differently.

    Returns:
        ``(a, b)`` with ``gcd(a, total) == 1``.
    """
    if total <= 1:
        return 1, 0
    b = (seed * 2654435761) % total
    a = max(1, int(total * _GOLDEN))
    while math.gcd(a, total) != 1:
        a += 1
        if a >= total:
            a = 1
    return a, b


def _walk(
    spec: RunSpec, space: SearchSpace, shape: ShapeResolver | None = None
) -> Iterator[tuple[Coordinate, str]]:
    """Every cell the spec declares, as ``(coordinate, task)``, in diverse order.

    The space is a mixed-radix hypergrid (one radix per axis, plus task and
    sweep-step). It is traversed by a seeded affine permutation rather than a
    row-major product, so early cells vary every axis at once — a diverse,
    unbiased sample of the ontology rather than a corner of it. Each cell is
    still visited exactly once, so the traversal remains a complete enumeration.

    Yields:
        ``(coordinate, task)`` for every cell the spec declares.
    """
    per_axis = [space.primitives(axis) for axis in AXIS_KIND_ORDER]
    if not space.tasks or not all(per_axis):
        return
    schema = harvest_schema()
    ladders = _swept(spec, schema, shape)
    tasks = space.tasks
    steps = max((len(ladder) for ladder in ladders.values()), default=1)

    radices = [len(values) for values in per_axis] + [len(tasks), steps]
    total = math.prod(radices)
    a, b = _diverse_permutation(total, spec.seed)
    axis_count = len(AXIS_KIND_ORDER)

    for k in range(total):
        digits = _decode_index((a * k + b) % total, radices)
        selection = {
            axis.value: per_axis[i][digits[i]] for i, axis in enumerate(AXIS_KIND_ORDER)
        }
        task = tasks[digits[axis_count]]
        step = digits[axis_count + 1]
        params = _cell_params(Coordinate(**selection, params={}), schema, ladders, step)
        yield Coordinate(**selection, params=params), task


def iter_candidates(  # ruff: ignore[complex-structure]
    spec: RunSpec,
    search_space: SearchSpace,
    *,
    deadline=None,  # Deadline | None
    cost_model=None,  # CostModel | None
    shape: ShapeResolver | None = None,
    max_scan: int | None = None,
    check_composable: bool = True,
    offset: int = 0,
    page_size: int = _PAGE_SIZE,
    use_void_cache: bool = True,
) -> Iterator[tuple[Coordinate, Schedule]]:
    """Walk the harvested schema under the spec, yielding legal cells.

            The active space is computed, never tabulated: each axis offers the
            primitives the spec permits, the harvested availability predicates decide
            which hyperparameters a selection can use, and the spec's own domains are
            swept, as a Cartesian product over the axes rather than a diagonal.

            Supports paging via ``offset`` and ``page_size`` for unbounded traversal.

            Args:
                spec: The run declaration; names the task, fidelity, seed plan and the
                    hyperparameters to sweep.
                search_space: The run's active space.
                deadline: Optional hard deadline; if soft-expired, no cells are yielded.
                cost_model: Optional cost model (not used in deadline system).
                shape: Resolves a task's ``(input_dim, output_dim)``. When given, a
                    cell whose configs cannot compose or validate for that shape is
                    skipped instead of proposed.
                max_scan: Stop after this many candidates *examined*, not yielded. A
                    caller that prices or samples a factorial — where the illegal
                    candidates are the expensive majority — bounds the examination; a
                    caller that walks the space for what it can measure leaves it
                    ``None`` and takes the module's page size.
                check_composable: If True (default), verify that configs compose and
                    validate via ``_composable``. If False, skip this check for faster
        candidate generation (validation will happen at Gate/Compose stages).
                offset: Number of candidates to skip before yielding (for paging).
                page_size: Maximum candidates to examine per page (default 50k).
                use_void_cache: Whether to use the persistent void cache (default True).
    Disable for tests that need a clean search space.

            Yields:
                ``(coordinate, schedule)`` pairs, in a deterministic order.
    """
    task_indep_fns, task_dep_fns = _compiled_void_constraints()

    # Get void cache for this run (persisted across runs)
    void_cache = get_void_cache() if use_void_cache else None

    seen: set[str] = set()
    scanned = 0
    for coordinate, task in _walk(spec, search_space, shape):
        if deadline is not None and deadline.soft_expired():
            return
        scanned += 1
        if scanned <= offset:
            continue
        if scanned > offset + (max_scan if max_scan is not None else page_size):
            return
        schedule = _schedule(spec, task)
        if coordinate.measurement_key(schedule) in seen:
            continue
        seen.add(coordinate.measurement_key(schedule))

        # Check void cache first (fast path - avoids DSL evaluation)
        if use_void_cache and void_cache and void_cache.is_known_void(coordinate):
            continue

        # Fast void constraint check (compiled predicates, no composition)
        if task_indep_fns or task_dep_fns:
            values = (
                coordinate.substrate,
                coordinate.geometry,
                coordinate.dynamics,
                coordinate.plasticity,
                coordinate.credit,
                coordinate.update,
            )
            if not _void_pass(task_indep_fns, task_dep_fns, values, task):
                # Record in void cache for future runs
                if use_void_cache and void_cache:
                    void_cache.record_void(coordinate)
                continue

        # Explicit substrate-dynamics compatibility filter (defense-in-depth for
        # void constraints that may not be evaluated correctly)
        if not _is_substrate_dynamics_compatible(
            coordinate.substrate, coordinate.dynamics
        ):
            if use_void_cache and void_cache:
                void_cache.record_void(coordinate)
            continue

        # Explicit geometry-dynamics compatibility filter
        if not _is_geometry_dynamics_compatible(
            coordinate.geometry, coordinate.dynamics
        ):
            if use_void_cache and void_cache:
                void_cache.record_void(coordinate)
            continue

        # Explicit geometry-task compatibility filter
        if shape is not None:
            task_shape = shape(task)
            if not _is_geometry_task_compatible(
                coordinate.geometry, task_shape, schedule.task_id
            ):
                if use_void_cache and void_cache:
                    void_cache.record_void(coordinate)
                continue

        if (
            check_composable
            and shape is not None
            and not _composable(
                coordinate, schedule.task_id, shape, schedule.param_budget
            )
        ):
            continue
        if deadline is not None and deadline.soft_expired():
            return
        yield coordinate, schedule


def generate_candidates(
    spec: RunSpec,
    search_space: SearchSpace,
    *,
    deadline=None,
    cost_model=None,
    shape: ShapeResolver | None = None,
    limit: int = 10,
    use_void_cache: bool = True,
) -> list[tuple[Coordinate, Schedule]]:
    """The first ``limit`` cells of :func:`iter_candidates`."""
    stream = iter_candidates(
        spec,
        search_space,
        deadline=deadline,
        cost_model=cost_model,
        shape=shape,
        use_void_cache=use_void_cache,
    )
    return list(islice(stream, limit))


__all__ = [
    "SearchSpace",
    "ShapeResolver",
    "VoidCache",
    "declared_cell_count",
    "generate_candidates",
    "get_void_cache",
    "iter_candidates",
    "narrow_domain",
    "search_space_from_spec",
]
