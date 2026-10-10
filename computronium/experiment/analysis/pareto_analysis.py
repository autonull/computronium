"""Pareto Analysis (Phase D4).

Computes Pareto frontiers, scalarization sweeps, and hypervolume tracking
for multi-objective optimization analysis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore


@dataclass(frozen=True, slots=True)
class ParetoResult:
    """Result of Pareto analysis."""

    pareto_points: list[dict[str, Any]]  # Non-dominated points
    dominated_points: list[dict[str, Any]]  # Dominated points
    objectives: list[str]
    maximize: list[bool]
    hypervolume: float
    scalarization_results: dict[str, list[dict[str, Any]]]  # weight -> ranked points
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ParetoConfig:
    """Configuration for Pareto analysis."""

    reference_point: list[float] | None = None  # For hypervolume
    n_weight_samples: int = 20


def compute_pareto_frontier(
    records: list[Any],
    objectives: list[str],
    maximize: list[bool] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Compute Pareto frontier from records.

    Returns:
        (pareto_points, dominated_points)
    """
    if maximize is None:
        maximize = [True] * len(objectives)

    # Extract objective values
    points = []
    for r in records:
        obj_vals = {}
        valid = True
        for obj in objectives:
            val = r.payload.get(obj)
            if val is None:
                valid = False
                break
            obj_vals[obj] = float(val)
        if valid:
            points.append({
                "record_id": r.record_id,
                "cell_key": r.cell_key(),
                "objectives": obj_vals,
                "coordinate": {
                    "substrate": r.substrate,
                    "geometry": r.geometry,
                    "dynamics": r.dynamics,
                    "plasticity": r.plasticity,
                    "credit": r.credit,
                    "update": r.update,
                },
            })

    if not points:
        return [], []

    # Convert to array for efficient comparison
    obj_matrix = np.array([[p["objectives"][o] for o in objectives] for p in points])

    # Apply maximization/minimization
    for i, max_flag in enumerate(maximize):
        if not max_flag:
            obj_matrix[:, i] = -obj_matrix[:, i]

    # Non-dominated sorting
    n = len(points)
    is_dominated = np.zeros(n, dtype=bool)

    for i in range(n):
        if is_dominated[i]:
            continue
        for j in range(n):
            if i == j or is_dominated[j]:
                continue
            # Check if j dominates i
            if np.all(obj_matrix[j] >= obj_matrix[i]) and np.any(
                obj_matrix[j] > obj_matrix[i]
            ):
                is_dominated[i] = True
                break

    pareto_points = [points[i] for i in range(n) if not is_dominated[i]]
    dominated_points = [points[i] for i in range(n) if is_dominated[i]]

    return pareto_points, dominated_points


def compute_hypervolume(
    pareto_points: list[dict[str, Any]],
    objectives: list[str],
    maximize: list[bool],
    reference_point: list[float] | None = None,
) -> float:
    """Compute hypervolume indicator for Pareto front.

    For 2D case, computes area dominated by Pareto front.
    For higher dimensions, uses Monte Carlo approximation.
    """
    if not pareto_points:
        return 0.0

    obj_matrix = np.array([
        [p["objectives"][o] for o in objectives] for p in pareto_points
    ])

    # Apply maximization/minimization
    for i, max_flag in enumerate(maximize):
        if not max_flag:
            obj_matrix[:, i] = -obj_matrix[:, i]

    if reference_point is None:
        # Use nadir point + small buffer
        reference_point_arr = np.max(obj_matrix, axis=0) + 1.0
    else:
        reference_point_arr = np.array(reference_point)

    # Simple 2D case
    if len(objectives) == 2:
        # Sort by first objective
        idx = np.argsort(obj_matrix[:, 0])
        sorted_obj = obj_matrix[idx]

        hv = 0.0
        prev_x = reference_point_arr[0]
        for pt in sorted_obj:
            width = prev_x - pt[0]
            height = max(0, reference_point_arr[1] - pt[1])
            if width > 0 and height > 0:
                hv += width * height
            prev_x = pt[0]
        return float(hv)

    # Higher dimensions: Monte Carlo
    n_samples = 10000
    samples = np.random.uniform(
        low=np.min(obj_matrix, axis=0),
        high=reference_point_arr,
        size=(n_samples, len(objectives)),
    )

    dominated = 0
    for sample in samples:
        for pt in obj_matrix:
            if np.all(sample <= pt):
                dominated += 1
                break

    # Volume of bounding box
    box_volume = np.prod(reference_point - np.min(obj_matrix, axis=0))
    return float(box_volume * dominated / n_samples)


def compute_scalarization_sweep(
    records: list[Any],
    objectives: list[str],
    maximize: list[bool],
    n_weight_samples: int = 20,
) -> dict[str, list[dict[str, Any]]]:
    """Compute weighted scalarization for multiple weight vectors."""
    if maximize is None:
        maximize = [True] * len(objectives)

    # Extract objective values
    points = []
    for r in records:
        obj_vals = {}
        valid = True
        for obj in objectives:
            val = r.payload.get(obj)
            if val is None:
                valid = False
                break
            obj_vals[obj] = float(val)
        if valid:
            points.append({
                "record_id": r.record_id,
                "cell_key": r.cell_key(),
                "objectives": obj_vals,
                "coordinate": {
                    "substrate": r.substrate,
                    "geometry": r.geometry,
                    "dynamics": r.dynamics,
                    "plasticity": r.plasticity,
                    "credit": r.credit,
                    "update": r.update,
                },
            })

    if not points:
        return {}

    # Generate weight vectors (simplex sampling)
    weight_results = {}
    for _ in range(n_weight_samples):
        # Dirichlet distribution for weights
        weights = np.random.dirichlet(np.ones(len(objectives)))
        weight_key = "_".join(f"{w:.3f}" for w in weights)

        # Compute scalarized scores
        scored_points = []
        for p in points:
            score = sum(
                w * (p["objectives"][o] if max_flag else -p["objectives"][o])
                for w, o, max_flag in zip(weights, objectives, maximize)
            )
            scored_points.append({**p, "scalarized_score": float(score)})

        # Sort by score
        scored_points.sort(key=lambda x: x["scalarized_score"], reverse=True)
        weight_results[weight_key] = scored_points[:20]  # Top 20

    return weight_results


class ParetoAnalyzer:
    """Analyze Pareto frontiers from experiment records."""

    def __init__(
        self,
        store: RecordStore,
        run_id: str,
        config: ParetoConfig | None = None,
    ):
        self.store = store
        self.run_id = run_id
        self.config = config or ParetoConfig()

    def analyze(
        self,
        objectives: list[str] = ["val_acc", "energy_per_step"],
        maximize: list[bool] | None = None,
    ) -> ParetoResult:
        """Run Pareto analysis."""
        from computronium.experiment.surface.report import ReportGenerator

        generator = ReportGenerator(self.store)
        records = generator._store.query_records(run_id=self.run_id)

        if maximize is None:
            maximize = [True, False]  # Maximize accuracy, minimize energy

        pareto_points, dominated_points = compute_pareto_frontier(
            records, objectives, maximize
        )

        hv = compute_hypervolume(
            pareto_points, objectives, maximize, self.config.reference_point
        )

        scalarization = compute_scalarization_sweep(
            records, objectives, maximize, self.config.n_weight_samples
        )

        return ParetoResult(
            pareto_points=pareto_points,
            dominated_points=dominated_points,
            objectives=objectives,
            maximize=maximize,
            hypervolume=hv,
            scalarization_results=scalarization,
            metadata={
                "n_records": len(records),
                "n_pareto": len(pareto_points),
                "n_dominated": len(dominated_points),
            },
        )
