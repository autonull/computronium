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
from itertools import islice, product
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
    from computronium.experiment.execution.budget import Budget, CostModel
    from computronium.experiment.execution.evaluate import TaskShape
    from computronium.experiment.schema.axis import AxisSpec
    from computronium.experiment.schema.registries import ConstraintSpec, ObjectiveSpec
    from computronium.experiment.schema.run_spec import RunSpec

# Values a spec-narrowed hyperparameter is swept across. The space is a
# continuum; a run proposes ``limit`` points on it.
_SWEEP_STEPS: Final = 5

type ShapeResolver = Callable[[str], TaskShape]

# A scan bound, not a space bound: guards against a budget or a predicate that
# admits nothing, which would otherwise make the candidate stream unbounded.
_MAX_SCAN: Final = 50_000

# Module-level cache for search_space_from_spec
_search_space_cache: dict[tuple, SearchSpace] = {}

# Module-level cache for _filter_axes_for_validity
_filter_axes_cache: dict[tuple, dict[str, list[str]]] = {}


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


def _filter_axes_cache_key(axes_snapshot: list, spec: RunSpec) -> tuple:
    """Create a cache key for _filter_axes_for_validity."""
    # Key includes: axis names per axis kind, task
    axes_key = tuple(
        tuple(sorted(s.name for s in axes_snapshot if s.axis_kind == axis))
        for axis in StructuralAxis
    )
    task_key = spec.task_names[0] if spec.task_names else None
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
    axes_snapshot = _filter_axes_for_validity(axes_snapshot, spec)

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


def _filter_axes_for_validity(  # ruff: ignore[complex-structure]
    axes_snapshot: list[AxisSpec],
    spec: RunSpec,
) -> list[AxisSpec]:
    """Filter axis primitives to only those with at least one valid combination.

    Computes valid 6-tuples from all void constraints in CONSTRAINTS_REGISTRY,
    then derives per-axis valid primitives from the valid tuples.

    For large spaces (>100k combinations), uses per-primitive validation
    instead of full Cartesian product to avoid 50s+ startup.
    """
    from computronium.experiment.legality.dsl import (
        CoordinateContext,
        Expr,
        Var,
        evaluate,
    )
    from computronium.experiment.schema.axis import StructuralAxis
    from computronium.experiment.schema.registries import CONSTRAINTS_REGISTRY

    # Check cache
    cache_key = _filter_axes_cache_key(axes_snapshot, spec)
    if cache_key in _filter_axes_cache:
        # Convert cached names back to AxisSpec objects
        valid_names_by_axis: dict[StructuralAxis, set[str]] = {}
        for axis in StructuralAxis:
            valid_names_by_axis[axis] = set(_filter_axes_cache[cache_key][axis.value])

        filtered_snapshot = []
        for axis_spec in axes_snapshot:
            if axis_spec.name in valid_names_by_axis.get(
                axis_spec.axis_kind, set()
            ) or not valid_names_by_axis.get(axis_spec.axis_kind):
                filtered_snapshot.append(axis_spec)
        return filtered_snapshot

    def _references_params(expr: Expr) -> bool:
        """Check if expression references params.* variables."""
        if isinstance(expr, Var) and expr.name.startswith("params."):
            return True
        # Recursively check nested expressions
        for field_name in ("expr", "left", "right", "obj", "key"):
            child = getattr(expr, field_name, None)
            if isinstance(child, Expr) and _references_params(child):
                return True
        # Check for Call.args (Call has args attribute)
        if hasattr(expr, "args"):
            args = getattr(expr, "args", None)
            if args is not None:
                for arg in args:
                    if isinstance(arg, Expr) and _references_params(arg):
                        return True
        return False

    # Group primitives by axis
    primitives_by_axis: dict[StructuralAxis, list[str]] = {}
    for axis_spec in axes_snapshot:
        primitives_by_axis.setdefault(axis_spec.axis_kind, []).append(axis_spec.name)

    # Get all void constraints that can be evaluated at search space time
    # (structural axes only, no hyperparameters needed)
    void_constraints = [
        c
        for c in CONSTRAINTS_REGISTRY.values()
        if c.kind.value == "void"
        and c.predicate is not None
        and not _references_params(c.predicate)
    ]

    # If no void constraints, keep all primitives
    if not void_constraints:
        return axes_snapshot

    axes_order = list(StructuralAxis)
    axis_primitives = [primitives_by_axis.get(axis, []) for axis in axes_order]

    # Quick exit if any axis has no primitives
    if not all(axis_primitives):
        return axes_snapshot

    total_combos = math.prod(len(p) for p in axis_primitives)

    # For small spaces, use full Cartesian product (exact)
    # For large spaces, use per-primitive validation (approximate but fast)
    if total_combos <= 100_000:
        # Exact: enumerate all combinations
        valid_tuples: set[tuple[str, ...]] = set()
        for values in product(*axis_primitives):
            selection = {
                axis.value: name for axis, name in zip(axes_order, values, strict=True)
            }
            coordinate = Coordinate(**selection, params={})
            ctx = CoordinateContext(
                coordinate, task=spec.task_names[0] if spec.task_names else None
            )

            all_pass = True
            for constraint in void_constraints:
                pred = constraint.predicate
                if pred is None:
                    continue
                if not evaluate(pred, ctx):
                    all_pass = False
                    break

            if all_pass:
                valid_tuples.add(values)

        valid_by_axis: dict[StructuralAxis, set[str]] = {
            axis: set() for axis in axes_order
        }
        for tup in valid_tuples:
            for axis, name in zip(axes_order, tup, strict=True):
                valid_by_axis[axis].add(name)
    else:
        # Approximate: for each primitive, check if it can be part of ANY valid combination
        # by searching combinations with that primitive fixed
        valid_by_axis: dict[StructuralAxis, set[str]] = {
            axis: set() for axis in axes_order
        }

        # Pre-compute default values for other axes (first primitive each)
        default_selection = {}
        for axis in axes_order:
            primitives = primitives_by_axis.get(axis, [])
            default_selection[axis.value] = primitives[0] if primitives else ""

        # Max combinations to check per primitive
        max_checks_per_primitive = 500

        for axis in axes_order:
            for primitive in primitives_by_axis.get(axis, []):
                # Try to find a valid combination with this primitive fixed
                found = False

                # Build list of other axes' primitives
                other_axes = [a for a in axes_order if a != axis]
                other_primitives = [primitives_by_axis.get(a, []) for a in other_axes]

                if not all(other_primitives):
                    # Some axis has no primitives - skip
                    continue

                # Quick check: try default combination first
                test_selection = default_selection.copy()
                test_selection[axis.value] = primitive
                coordinate = Coordinate(**test_selection, params={})
                ctx = CoordinateContext(
                    coordinate, task=spec.task_names[0] if spec.task_names else None
                )

                all_pass = True
                for constraint in void_constraints:
                    pred = constraint.predicate
                    if pred is None:
                        continue
                    if not evaluate(pred, ctx):
                        all_pass = False
                        break

                if all_pass:
                    valid_by_axis[axis].add(primitive)
                    continue

                # If default failed, search other combinations (limited)
                checks = 0
                for values in product(*other_primitives):
                    if checks >= max_checks_per_primitive:
                        break
                    test_selection = default_selection.copy()
                    test_selection[axis.value] = primitive
                    for other_axis, val in zip(other_axes, values, strict=True):
                        test_selection[other_axis.value] = val
                    coordinate = Coordinate(**test_selection, params={})
                    ctx = CoordinateContext(
                        coordinate, task=spec.task_names[0] if spec.task_names else None
                    )

                    all_pass = True
                    for constraint in void_constraints:
                        pred = constraint.predicate
                        if pred is None:
                            continue
                        if not evaluate(pred, ctx):
                            all_pass = False
                            break

                    if all_pass:
                        valid_by_axis[axis].add(primitive)
                        found = True
                        break
                    checks += 1

    # Cache the result (store as dict of axis -> set of names)
    _filter_axes_cache[cache_key] = {
        axis.value: list(names) for axis, names in valid_by_axis.items()
    }

    # Filter axes_snapshot to only primitives that appear in at least one valid tuple
    filtered_snapshot = []
    for axis_spec in axes_snapshot:
        if axis_spec.name in valid_by_axis.get(
            axis_spec.axis_kind, set()
        ) or not valid_by_axis.get(axis_spec.axis_kind):
            filtered_snapshot.append(axis_spec)

    return filtered_snapshot


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

    # Solve quadratic: hidden_dim^2 * (num_layers - 1) + hidden_dim * (input_dim + output_dim + 1) - param_budget <= 0
    if num_layers <= 1:
        # Linear: hidden_dim * (input_dim + output_dim + 1) <= param_budget
        denom = input_dim + output_dim + 1
        return max(8, min(4096, param_budget // max(1, denom)))
    else:
        # Quadratic: a * x^2 + b * x - c <= 0
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

    Un-swept hyperparameters stay absent from the coordinate and are resolved
    by ``harvest_schema().active()`` at composition time, from prior and domain.
    """
    specs_by_name = schema.by_name()

    # Compute task shape for param_budget-aware domain narrowing
    task_shape = None
    if shape is not None and spec.task_names:
        task_shape = shape(spec.task_names[0])

    # Build effective domains, narrowing hidden_dim by param_budget if possible
    effective_domains: dict[str, Domain] = {}
    for name, domain in spec.hyperparameters.items():
        effective_domains[name] = domain

    # If hidden_dim is not explicitly swept but param_budget is set, add a constraint
    if (
        "hidden_dim" not in effective_domains
        and spec.param_budget > 0
        and task_shape is not None
    ):
        max_h = _max_hidden_dim(
            spec.param_budget, task_shape.input_shape[-1], task_shape.output_dim
        )
        from computronium.experiment.schema.axis import Domain, Scale

        effective_domains["hidden_dim"] = Domain(lo=8, hi=max_h, scale=Scale.LOG)

    sweep_steps = getattr(spec, "sweep_steps", 5)
    return {
        name: _ladder(
            narrow_domain(domain, specs_by_name[name].domain, name),
            specs_by_name[name].axis_kind,
            steps=sweep_steps,
        )
        for name, domain in effective_domains.items()
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
    from computronium.experiment.schema.harvest import config_field_name

    active = schema.active(coordinate)
    axis_of = {
        spec.name: StructuralAxis(spec.axis_name) for spec in schema.hyperparameters
    }
    usable: dict[str, Any] = {}
    for name, ladder in ladders.items():
        axis = axis_of[name]
        config_name = config_field_name(name)
        if config_name not in active.for_axis(axis, getattr(coordinate, axis.value)):
            continue
        usable[name] = ladder[stride % len(ladder)]
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
    from computronium.experiment.execution.compose import (
        compose_configs,
        geometry_param_count,
    )

    # Create cache key from structural axes + task + param_budget + relevant hyperparameters
    # Hyperparameters that affect validity (checked in void constraints):
    # - hidden_dim (max_hidden_dim)
    # - num_layers (max_layers)
    # - max_steps (max_steps)
    # - beta (gradient_credit_beta_clamp)
    # - residual (residual_connections)
    validity_params = frozenset(
        (k, v)
        for k, v in coordinate.params.items()
        if k in {"hidden_dim", "num_layers", "max_steps", "beta", "residual"}
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
    try:
        config = compose_configs(
            coordinate=coordinate,
            geometry={},
            input_shape=task_shape.input_shape,
            output_dim=task_shape.output_dim,
            param_budget=param_budget,
        )
    except ValueError, TypeError, KeyError:
        _composable_cache[cache_key] = False
        return False
    if param_budget <= 0:
        _composable_cache[cache_key] = True
        return True
    # The same R25 fairness rule the evaluator's gate applies, asked here so a
    # cell that cannot honour its ceiling is never proposed: a cell that cannot
    # fit is discovered by training, which is the expensive way to find out.
    result = geometry_param_count(config.geometry) <= param_budget * (
        1 + PARAM_BUDGET_TOLERANCE
    )
    _composable_cache[cache_key] = result
    return result


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
        device=spec.device,
        deterministic=spec.deterministic,
        num_workers=spec.num_workers,
        precision=spec.precision,
    )


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


def _walk(  # ruff: ignore[complex-structure]
    spec: RunSpec, space: SearchSpace, shape: ShapeResolver | None = None
) -> Iterator[tuple[Coordinate, str]]:
    """Every cell the spec declares, as ``(coordinate, task)``.

    The axes are walked with round-robin interleaving on the first axis
    (substrate) to ensure early diversity across substrates. Within each
    substrate, the remaining axes follow Cartesian product order.

    This avoids the pathological case where the first axis has many values
    and the rest have few, causing the stream to exhaust all combinations
    of the first value before ever reaching the second value.

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

    # Round-robin interleaving on the first axis (substrate)
    first_axis_values = per_axis[0]
    other_axes_values = per_axis[1:]

    # If only one value on first axis, fall back to simple product
    if len(first_axis_values) == 1:
        for values in product(*per_axis):
            selection = {
                axis.value: name
                for axis, name in zip(AXIS_KIND_ORDER, values, strict=True)
            }
            for task in tasks:
                for step in range(steps):
                    params = _cell_params(
                        Coordinate(**selection, params={}), schema, ladders, step
                    )
                    yield Coordinate(**selection, params=params), task
        return

    # Build lazy iterators for each first-axis value
    def _substrate_iterator(first_val: str):
        """Lazy iterator for all combinations with a fixed first-axis value."""
        for other_vals_tuple in product(*other_axes_values):
            selection = {AXIS_KIND_ORDER[0].value: first_val}
            for axis, val in zip(AXIS_KIND_ORDER[1:], other_vals_tuple, strict=True):
                selection[axis.value] = val
            for task in tasks:
                for step in range(steps):
                    params = _cell_params(
                        Coordinate(**selection, params={}), schema, ladders, step
                    )
                    yield Coordinate(**selection, params=params), task

    # Create iterator for each substrate
    substrate_iterators = [_substrate_iterator(fv) for fv in first_axis_values]
    exhausted = [False] * len(substrate_iterators)
    active_count = len(substrate_iterators)

    # Round-robin yield: take one from each substrate iterator in turn
    while active_count > 0:
        for i, it in enumerate(substrate_iterators):
            if exhausted[i]:
                continue
            try:
                yield next(it)
            except StopIteration:
                exhausted[i] = True
                active_count -= 1


def iter_candidates(  # ruff: ignore[complex-structure]
    spec: RunSpec,
    search_space: SearchSpace,
    *,
    budget: Budget | None = None,
    cost_model: CostModel | None = None,
    shape: ShapeResolver | None = None,
    max_scan: int | None = None,
    check_composable: bool = True,
) -> Iterator[tuple[Coordinate, Schedule]]:
    """Walk the harvested schema under the spec, yielding legal cells.

    The active space is computed, never tabulated: each axis offers the
    primitives the spec permits, the harvested availability predicates decide
    which hyperparameters a selection can use, and the spec's own domains are
    swept, as a Cartesian product over the axes rather than a diagonal.

    Args:
        spec: The run declaration; names the task, fidelity, seed plan and the
            hyperparameters to sweep.
        search_space: The run's active space.
        budget: Optional ceiling; a cell estimated above it is skipped.
        cost_model: Required with ``budget`` to estimate a cell's cost.
        shape: Resolves a task's ``(input_dim, output_dim)``. When given, a
            cell whose configs cannot compose or validate for that shape is
            skipped instead of proposed.
        max_scan: Stop after this many candidates *examined*, not yielded. A
            caller that prices or samples a factorial — where the illegal
            candidates are the expensive majority — bounds the examination; a
            caller that walks the space for what it can measure leaves it
            ``None`` and takes the module's own scan bound.
        check_composable: If True (default), verify that configs compose and
            validate via ``_composable``. If False, skip this check for faster
            candidate generation (validation will happen at Gate/Compose stages).

    Yields:
        ``(coordinate, schedule)`` pairs, in a deterministic order.
    """
    from computronium.experiment.legality.dsl import (
        CoordinateContext,
        Expr,
        Var,
        evaluate,
    )
    from computronium.experiment.schema.registries import CONSTRAINTS_REGISTRY

    def _references_params(expr: Expr) -> bool:
        """Check if expression references params.* variables."""
        if isinstance(expr, Var) and expr.name.startswith("params."):
            return True
        for field_name in ("expr", "left", "right", "obj", "key"):
            child = getattr(expr, field_name, None)
            if isinstance(child, Expr) and _references_params(child):
                return True
        # Check for Call.args (Call has args attribute)
        if hasattr(expr, "args"):
            args = getattr(expr, "args", None)
            if args is not None:
                for arg in args:
                    if isinstance(arg, Expr) and _references_params(arg):
                        return True
        return False

    # Use ALL void constraints that don't require hyperparameters
    void_constraints = [
        c
        for c in CONSTRAINTS_REGISTRY.values()
        if c.kind.value == "void"
        and c.predicate is not None
        and not _references_params(c.predicate)
    ]

    seen: set[str] = set()
    scanned = 0
    for coordinate, task in _walk(spec, search_space, shape):
        scanned += 1
        if scanned > (max_scan if max_scan is not None else _MAX_SCAN):
            return
        schedule = _schedule(spec, task)
        if coordinate.measurement_key(schedule) in seen:
            continue
        seen.add(coordinate.measurement_key(schedule))

        # Fast void constraint check (DSL evaluation, no composition)
        if void_constraints:
            ctx = CoordinateContext(coordinate, task=task)
            failed = False
            for constraint in void_constraints:
                pred = constraint.predicate
                if pred is None:
                    continue  # Should not happen, filtered above
                if not evaluate(pred, ctx):
                    failed = True
                    break
            if failed:
                continue

        if (
            check_composable
            and shape is not None
            and not _composable(
                coordinate, schedule.task_id, shape, schedule.param_budget
            )
        ):
            continue
        if budget is not None and cost_model is not None:
            cost = cost_model.estimate_cost(
                (
                    coordinate.substrate,
                    coordinate.geometry,
                    coordinate.dynamics,
                    coordinate.plasticity,
                    coordinate.credit,
                    coordinate.update,
                    coordinate.params,
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


__all__ = [
    "SearchSpace",
    "ShapeResolver",
    "declared_cell_count",
    "generate_candidates",
    "iter_candidates",
    "narrow_domain",
    "search_space_from_spec",
]
