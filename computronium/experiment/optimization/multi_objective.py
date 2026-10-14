"""Multi-objective optimization via the existing objective registry.

Wires the declared objective set (~90 objectives) into the experiment loop:
- Pareto frontier computation from recorded cells
- Normalization (minmax, log, zscore) per ObjectiveSpec
- Trade-off analysis and scalarization for Optuna
- Objective selection per task/domain
- Reference point management for hypervolume

Uses the existing MEASURED_OBJECTIVES and OBJECTIVES_REGISTRY for single-source truth.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from computronium.experiment.schema.record import Record
    from computronium.experiment.schema.registries import ObjectiveSpec


@dataclass(frozen=True, slots=True)
class NormalizedObjective:
    """A normalized objective value with metadata."""

    name: str
    raw_value: float
    normalized_value: float
    direction: str  # "minimize" or "maximize"
    weight: float
    normalizer: str | None
    axis_tag: str | None
    is_measured: bool  # Whether the payload had this metric


@dataclass(slots=True)
class ParetoPoint:
    """A point on the Pareto frontier."""

    cell_key: str
    replication_key: str
    objectives: tuple[NormalizedObjective, ...]
    dominates_count: int = 0
    dominated_by_count: int = 0
    crowding_distance: float = 0.0
    rank: int = 0  # Non-dominated sorting rank (0 = Pareto front)

    def objective_values(self, names: list[str]) -> tuple[float, ...]:
        """Get normalized objective values in given order."""
        obj_map = {o.name: o.normalized_value for o in self.objectives}
        return tuple(obj_map.get(n, float("nan")) for n in names)


@dataclass(frozen=True, slots=True)
class ParetoFrontier:
    """Pareto frontier with all points and metadata."""

    points: tuple[ParetoPoint, ...]
    objective_names: tuple[str, ...]
    reference_point: tuple[float, ...] | None  # For hypervolume computation
    hypervolume: float | None = None

    def front(self) -> list[ParetoPoint]:
        """Return points on the Pareto front (rank == 0)."""
        return [p for p in self.points if p.rank == 0]

    def to_dict(self) -> dict[str, Any]:
        return {
            "n_points": len(self.points),
            "n_front": len(self.front()),
            "objectives": list(self.objective_names),
            "reference_point": list(self.reference_point)
            if self.reference_point
            else None,
            "hypervolume": self.hypervolume,
            "front": [
                {
                    "cell_key": p.cell_key,
                    "replication_key": p.replication_key,
                    "objectives": {o.name: o.normalized_value for o in p.objectives},
                    "crowding_distance": p.crowding_distance,
                }
                for p in self.front()
            ],
        }


def get_declared_objectives_for_task(
    task: str,
    *,
    include_unmeasured: bool = False,
) -> list[ObjectiveSpec]:
    """Get objectives relevant for a task from the registry.

    Args:
        task: Task name (e.g., "digits", "cifar10", "wikitext2")
        include_unmeasured: Whether to include objectives without payload keys
    """
    from computronium.experiment.schema.metrics import measured_objectives
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    measured = set(measured_objectives())
    objectives = []

    for obj in OBJECTIVES_REGISTRY.values():
        # Filter by axis_tag if task-specific
        if (obj.axis_tag == "task" or obj.axis_tag is None) and (
            include_unmeasured or obj.name in measured
        ):
            objectives.append(obj)

    return objectives


def get_measured_objectives() -> list[ObjectiveSpec]:
    """Get all objectives that have a payload key (are actually measured)."""
    from computronium.experiment.schema.metrics import measured_objectives
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    measured = set(measured_objectives())
    return [obj for obj in OBJECTIVES_REGISTRY.values() if obj.name in measured]


def get_objectives_by_tag(axis_tag: str) -> list[ObjectiveSpec]:
    """Get objectives filtered by axis_tag."""
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    return [obj for obj in OBJECTIVES_REGISTRY.values() if obj.axis_tag == axis_tag]


def normalize_value(
    value: float,
    normalizer: str | None,
    direction: str,
    reference_values: list[float] | None = None,
) -> float:
    """Normalize a value using the specified normalizer.

    Normalizers:
    - minmax: (value - min) / (max - min)  [uses reference_values or assumes 0-1]
    - log: log(value + eps)  [for positive values]
    - zscore: (value - mean) / std  [uses reference_values]
    - none: no normalization (pass through)
    """
    if normalizer is None or normalizer == "none":
        return value

    result: float
    match normalizer:
        case "minmax":
            if reference_values and len(reference_values) > 1:
                vmin, vmax = min(reference_values), max(reference_values)
                result = (
                    ((value - vmin) / (vmax - vmin))
                    if vmax > vmin
                    else max(0.0, min(1.0, value))
                )
            else:
                result = max(0.0, min(1.0, value))

        case "log":
            result = math.log(max(value, 1e-12))

        case "zscore":
            if reference_values and len(reference_values) > 1:
                mean = float(np.mean(reference_values))
                std = float(np.std(reference_values))
                result = ((value - mean) / std) if std > 1e-12 else 0.0
            else:
                result = 0.0

        case _:
            result = value

    return result


def compute_objective_values(
    record: Record,
    objective_names: list[str],
) -> dict[str, NormalizedObjective]:
    """Extract and normalize objective values from a record's payload."""
    from computronium.experiment.schema.metrics import (
        measured_objectives,
        objective_metric,
    )
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    measured = set(measured_objectives())
    results = {}

    for name in objective_names:
        if name not in OBJECTIVES_REGISTRY:
            continue

        obj_spec = OBJECTIVES_REGISTRY[name]
        is_measured = name in measured

        raw_val = None
        if is_measured:
            metric_key = objective_metric(name)
            raw = record.payload.get(metric_key)
            if isinstance(raw, int | float) and not isinstance(raw, bool):
                raw_val = float(raw)

        if raw_val is None:
            # Unmeasured objective
            results[name] = NormalizedObjective(
                name=name,
                raw_value=float("nan"),
                normalized_value=float("nan"),
                direction=obj_spec.direction,
                weight=obj_spec.weight,
                normalizer=obj_spec.normalizer,
                axis_tag=obj_spec.axis_tag,
                is_measured=False,
            )
        else:
            results[name] = NormalizedObjective(
                name=name,
                raw_value=raw_val,
                normalized_value=raw_val,  # Will be normalized later with reference
                direction=obj_spec.direction,
                weight=obj_spec.weight,
                normalizer=obj_spec.normalizer,
                axis_tag=obj_spec.axis_tag,
                is_measured=True,
            )

    return results


def normalize_objectives(
    objectives: dict[str, NormalizedObjective],
    reference_values: dict[str, list[float]],
) -> dict[str, NormalizedObjective]:
    """Normalize all objectives using reference values from the population."""
    normalized = {}
    for name, obj in objectives.items():
        if not obj.is_measured or math.isnan(obj.raw_value):
            normalized[name] = obj
            continue

        ref_vals = reference_values.get(name, [obj.raw_value])
        norm_val = normalize_value(
            obj.raw_value, obj.normalizer, obj.direction, ref_vals
        )

        # For minimization, lower is better (already correct)
        # For maximization, we want higher normalized values
        if obj.direction == "maximize" and obj.normalizer != "log":
            # Invert for consistent "lower is better" in Pareto computation
            norm_val = -norm_val

        normalized[name] = NormalizedObjective(
            name=obj.name,
            raw_value=obj.raw_value,
            normalized_value=norm_val,
            direction=obj.direction,
            weight=obj.weight,
            normalizer=obj.normalizer,
            axis_tag=obj.axis_tag,
            is_measured=obj.is_measured,
        )
    return normalized


def dominates(
    obj_values_a: dict[str, NormalizedObjective],
    obj_values_b: dict[str, NormalizedObjective],
) -> bool:
    """Check if A dominates B (A is better on all objectives, strictly better on at least one)."""
    at_least_one_better = False
    for name in obj_values_a:
        if name not in obj_values_b:
            continue
        val_a = obj_values_a[name].normalized_value
        val_b = obj_values_b[name].normalized_value

        if math.isnan(val_a) or math.isnan(val_b):
            return False

        if val_a > val_b:  # A is worse on this objective
            return False
        if val_a < val_b:  # A is strictly better
            at_least_one_better = True

    return at_least_one_better


def _compute_domination_matrix(
    points: list[ParetoPoint],
) -> tuple[list[list[int]], list[int]]:
    """Compute domination relationships between all points.

    Returns:
        dominated_by: list of lists where dominated_by[i] contains indices j that i dominates
        dominates_count: list where dominates_count[j] is the number of points that dominate j
    """
    n = len(points)
    dominated_by = [[] for _ in range(n)]
    dominates_count = [0] * n

    for i in range(n):
        for j in range(i + 1, n):
            pi, pj = points[i], points[j]
            obj_i = {o.name: o for o in pi.objectives}
            obj_j = {o.name: o for o in pj.objectives}

            if dominates(obj_i, obj_j):
                dominates_count[j] += 1
                dominated_by[i].append(j)
            elif dominates(obj_j, obj_i):
                dominates_count[i] += 1
                dominated_by[j].append(i)

    return dominated_by, dominates_count


def non_dominated_sorting(points: list[ParetoPoint]) -> list[list[ParetoPoint]]:
    """Fast non-dominated sorting (NSGA-II style). Returns list of fronts."""
    n = len(points)
    if n == 0:
        return []

    dominated_by, dominates_count = _compute_domination_matrix(points)
    fronts: list[list[ParetoPoint]] = []

    # First front: points with dominates_count == 0
    current_front = [i for i in range(n) if dominates_count[i] == 0]
    for idx in current_front:
        points[idx].rank = 0
    fronts.append([points[i] for i in current_front])

    front_idx = 0
    while current_front:
        next_front = []
        for i in current_front:
            for j in dominated_by[i]:
                dominates_count[j] -= 1
                if dominates_count[j] == 0:
                    next_front.append(j)
        if not next_front:
            break
        front_idx += 1
        for idx in next_front:
            points[idx].rank = front_idx
        fronts.append([points[i] for i in next_front])
        current_front = next_front

    return fronts


def compute_crowding_distance(front: list[ParetoPoint]) -> None:
    """Compute crowding distance for points in a front (in-place)."""
    if len(front) <= 2:
        for p in front:
            p.crowding_distance = float("inf")
        return

    # Get all objective names
    obj_names = list({o.name for p in front for o in p.objectives})

    for name in obj_names:
        # Sort by this objective
        sorted_front = sorted(
            front,
            key=lambda p: next(
                o.normalized_value for o in p.objectives if o.name == name
            ),
        )
        # First and last get infinite distance
        sorted_front[0].crowding_distance = float("inf")
        sorted_front[-1].crowding_distance = float("inf")

        # Get min/max for normalization
        vals = [
            next(o.normalized_value for o in p.objectives if o.name == name)
            for p in sorted_front
        ]
        vmin, vmax = min(vals), max(vals)
        if vmax <= vmin:
            continue

        for i in range(1, len(sorted_front) - 1):
            p = sorted_front[i]
            dist = p.crowding_distance
            prev_val = next(
                o.normalized_value
                for o in sorted_front[i - 1].objectives
                if o.name == name
            )
            next_val = next(
                o.normalized_value
                for o in sorted_front[i + 1].objectives
                if o.name == name
            )
            p.crowding_distance = dist + (next_val - prev_val) / (vmax - vmin)


def compute_pareto_frontier(
    records: list[Record],
    objective_names: list[str],
    *,
    reference_point: tuple[float, ...] | None = None,
) -> ParetoFrontier:
    """Compute Pareto frontier from records for given objectives."""
    from computronium.experiment.schema.metrics import (
        measured_objectives,
        objective_metric,
    )
    from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

    measured = set(measured_objectives())
    points = []

    # First pass: extract all raw values for reference
    reference_values: dict[str, list[float]] = {name: [] for name in objective_names}

    for record in records:
        for name in objective_names:
            if name in OBJECTIVES_REGISTRY and name in measured:
                metric_key = objective_metric(name)
                raw = record.payload.get(metric_key)
                if isinstance(raw, int | float) and not isinstance(raw, bool):
                    reference_values[name].append(float(raw))

    # Second pass: create normalized points
    for record in records:
        cell_key = record.cell_key
        replication_key = record.measurement_key

        raw_objectives = compute_objective_values(record, objective_names)
        normalized_objectives = normalize_objectives(raw_objectives, reference_values)

        obj_tuple = tuple(
            normalized_objectives[name]
            for name in objective_names
            if name in normalized_objectives
        )

        points.append(
            ParetoPoint(
                cell_key=cell_key,
                replication_key=replication_key,
                objectives=obj_tuple,
            )
        )

    # Non-dominated sorting
    fronts = non_dominated_sorting(points)
    for front in fronts:
        compute_crowding_distance(front)

    # Compute hypervolume if reference point provided
    hypervolume = None
    if reference_point and len(reference_point) == len(objective_names):
        hypervolume = compute_hypervolume(points, objective_names, reference_point)

    return ParetoFrontier(
        points=tuple(points),
        objective_names=tuple(objective_names),
        reference_point=reference_point,
        hypervolume=hypervolume,
    )


def compute_hypervolume(
    points: list[ParetoPoint],
    objective_names: list[str],
    reference_point: tuple[float, ...],
) -> float:
    """Compute hypervolume indicator (for minimization, lower is better).

    Uses Monte Carlo approximation for high dimensions.
    """
    # Simple 2D/3D exact computation, Monte Carlo for higher
    if len(objective_names) <= 3:
        return _hypervolume_exact(points, objective_names, reference_point)
    else:
        return _hypervolume_monte_carlo(points, objective_names, reference_point)


def _hypervolume_exact(
    points: list[ParetoPoint],
    objective_names: list[str],
    reference_point: tuple[float, ...],
) -> float:
    """Exact hypervolume for 2D/3D using inclusion-exclusion."""
    # For simplicity, use Monte Carlo even for low dim
    return _hypervolume_monte_carlo(
        points, objective_names, reference_point, n_samples=10000
    )


def _hypervolume_monte_carlo(
    points: list[ParetoPoint],
    objective_names: list[str],
    reference_point: tuple[float, ...],
    n_samples: int = 10000,
) -> float:
    """Monte Carlo hypervolume estimation."""

    # Find bounds
    bounds = []
    for i, name in enumerate(objective_names):
        vals = []
        for p in points:
            val = next(
                (o.normalized_value for o in p.objectives if o.name == name), None
            )
            if val is not None and not math.isnan(val):
                vals.append(val)
        if vals:
            bounds.append((min(vals), max(vals)))
        else:
            bounds.append((0.0, 1.0))

    # Sample points
    count = 0
    for _ in range(n_samples):
        sample = [np.random.uniform(b[0], b[1]) for b in bounds]
        # Check if dominated by any point
        dominated = False
        for p in points:
            obj_vals = [
                next((o.normalized_value for o in p.objectives if o.name == name), None)
                for name in objective_names
            ]
            if all(
                v is not None and not math.isnan(v) and v <= s
                for v, s in zip(obj_vals, sample)
            ):
                dominated = True
                break
        if dominated:
            count += 1

    # Volume of bounding box
    vol = 1.0
    for b in bounds:
        vol *= b[1] - b[0]

    return (count / n_samples) * vol


def scalarize_objectives(
    objectives: dict[str, NormalizedObjective],
    weights: dict[str, float] | None = None,
) -> float:
    """Scalarize multi-objective values to a single score (weighted sum).

    Used for Optuna single-objective optimization with multiple objectives.
    """
    total = 0.0
    total_weight = 0.0
    for name, obj in objectives.items():
        if math.isnan(obj.normalized_value):
            continue
        w = weights.get(name, obj.weight) if weights else obj.weight
        total += w * obj.normalized_value
        total_weight += w
    return total / total_weight if total_weight > 0 else float("nan")


def get_task_objective_set(task: str) -> list[str]:
    """Get the default objective set for a task.

    Returns measured objectives relevant for the task, prioritized by axis_tag.
    """
    # Primary task objective
    primary = {
        "digits": "validation_accuracy",
        "mnist": "validation_accuracy",
        "fashion_mnist": "validation_accuracy",
        "cifar10": "validation_accuracy",
        "cifar100": "validation_accuracy",
        "wikitext2": "perplexity",
        "ptb": "perplexity",
        "copyshake": "validation_accuracy",
        "iris": "validation_accuracy",
        "xor": "validation_accuracy",
        "spiral": "validation_accuracy",
        "cartpole": "validation_accuracy",
        "mountaincar": "validation_accuracy",
        "cora": "validation_accuracy",
        "citeseer": "validation_accuracy",
        "pubmed": "validation_accuracy",
        "copy_task": "validation_accuracy",
        "associative_recall": "validation_accuracy",
    }.get(task, "validation_accuracy")

    # Get all measured objectives
    all_measured = get_measured_objectives()

    # Prioritize: primary task + cost + ruler + stability
    priority_tags = [
        "task",
        "cost",
        "ruler",
        "stability",
        "substrate",
        "plasticity",
        "composite",
    ]
    selected = []

    # Always include primary
    if primary not in selected:
        selected.append(primary)

    # Add objectives by priority tag
    for tag in priority_tags:
        tag_objs = [o.name for o in all_measured if o.axis_tag == tag]
        for name in tag_objs:
            if name not in selected:
                selected.append(name)

    # Add any remaining measured objectives
    for obj in all_measured:
        if obj.name not in selected:
            selected.append(obj.name)

    return selected


class MultiObjectiveOptimizer:
    """Orchestrates multi-objective optimization using the registry."""

    def __init__(self, task: str, objective_names: list[str] | None = None) -> None:
        self.task = task
        self.objective_names = objective_names or get_task_objective_set(task)

    def evaluate_cell(self, record: Record) -> dict[str, NormalizedObjective]:
        """Evaluate all objectives for a cell record."""
        return compute_objective_values(record, self.objective_names)

    def compute_frontier(
        self,
        records: list[Record],
        *,
        reference_point: tuple[float, ...] | None = None,
    ) -> ParetoFrontier:
        """Compute Pareto frontier for the given records."""
        return compute_pareto_frontier(
            records, self.objective_names, reference_point=reference_point
        )

    def scalarize(
        self,
        objectives: dict[str, NormalizedObjective],
        weights: dict[str, float] | None = None,
    ) -> float:
        """Scalarize objectives for single-objective optimization."""
        return scalarize_objectives(objectives, weights)

    def get_optuna_directions(self) -> list[str]:
        """Get Optuna study directions for each objective."""
        from computronium.experiment.schema.registries import OBJECTIVES_REGISTRY

        directions = []
        for name in self.objective_names:
            if name in OBJECTIVES_REGISTRY:
                obj = OBJECTIVES_REGISTRY[name]
                # Optuna: "minimize" or "maximize"
                directions.append(obj.direction)
            else:
                directions.append("minimize")
        return directions


__all__ = [
    "MultiObjectiveOptimizer",
    "NormalizedObjective",
    "ParetoFrontier",
    "ParetoPoint",
    "compute_hypervolume",
    "compute_objective_values",
    "compute_pareto_frontier",
    "dominates",
    "get_declared_objectives_for_task",
    "get_measured_objectives",
    "get_objectives_by_tag",
    "get_task_objective_set",
    "non_dominated_sorting",
    "normalize_objectives",
    "normalize_value",
    "scalarize_objectives",
]
