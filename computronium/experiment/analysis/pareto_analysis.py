"""Pareto Analysis (Phase D4).

Computes Pareto frontiers, scalarization sweeps, and hypervolume tracking
for multi-objective optimization analysis.

This module wraps the canonical Pareto implementation from
`computronium.experiment.optimization.multi_objective` and provides
additional analysis utilities (scalarization sweeps, hypervolume).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from computronium.experiment.evidence.store import RecordStore
    from computronium.experiment.schema.record import Record


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
    records: list[Record],
    objectives: list[str],
    maximize: list[bool] | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Compute Pareto frontier from records using canonical implementation.

    Returns:
        (pareto_points, dominated_points)
    """
    from computronium.experiment.optimization.multi_objective import (
        ParetoFrontier,
    )
    from computronium.experiment.optimization.multi_objective import (
        compute_pareto_frontier as canonical_compute_pareto_frontier,
    )

    if maximize is None:
        maximize = [True] * len(objectives)

    # Use canonical Pareto computation (directions come from OBJECTIVE_REGISTRY)
    frontier: ParetoFrontier = canonical_compute_pareto_frontier(records, objectives)

    # Convert to analysis format
    pareto_points = []
    dominated_points = []

    for point in frontier.points:
        obj_dict = {o.name: o.raw_value for o in point.objectives}
        point_dict = {
            "record_id": point.replication_key,
            "cell_key": point.cell_key,
            "objectives": obj_dict,
            "coordinate": {},  # Coordinate info not in canonical ParetoPoint
        }
        if point.rank == 0:
            pareto_points.append(point_dict)
        else:
            dominated_points.append(point_dict)

    return pareto_points, dominated_points


def compute_hypervolume(
    pareto_points: list[dict[str, Any]],
    objectives: list[str],
    maximize: list[bool],
    reference_point: list[float] | None = None,
) -> float:
    """Compute hypervolume indicator for Pareto front using canonical implementation."""
    from computronium.experiment.optimization.multi_objective import (
        NormalizedObjective,
        ParetoFrontier,
        ParetoPoint,
    )
    from computronium.experiment.optimization.multi_objective import (
        compute_hypervolume as canonical_compute_hypervolume,
    )

    if not pareto_points:
        return 0.0

    # Reconstruct ParetoPoint objects from analysis format
    points = []
    for p in pareto_points:
        obj_tuple = tuple(
            NormalizedObjective(
                name=name,
                raw_value=p["objectives"][name],
                normalized_value=p["objectives"][name],
                direction="maximize" if maximize[i] else "minimize",
                weight=1.0,
                normalizer=None,
                axis_tag=None,
                is_measured=True,
            )
            for i, name in enumerate(objectives)
            if name in p["objectives"]
        )
        points.append(
            ParetoPoint(
                cell_key=p["cell_key"],
                replication_key=p["record_id"],
                objectives=obj_tuple,
            )
        )

    # Create a minimal ParetoFrontier for canonical hypervolume
    frontier = ParetoFrontier(
        points=tuple(points),
        objective_names=tuple(objectives),
        reference_point=tuple(reference_point) if reference_point else None,
    )

    # Use canonical hypervolume (need reference point)
    if reference_point is None:
        # Compute reference point from pareto points
        obj_matrix = np.array([
            [p["objectives"][o] for o in objectives] for p in pareto_points
        ])
        # Apply maximization/minimization
        for i, max_flag in enumerate(maximize):
            if not max_flag:
                obj_matrix[:, i] = -obj_matrix[:, i]
        ref = np.max(obj_matrix, axis=0) + 1.0
        ref_tuple = tuple(ref)
    else:
        ref_tuple = tuple(reference_point)

    return canonical_compute_hypervolume(list(frontier.front()), objectives, ref_tuple)


def compute_scalarization_sweep(
    records: list[Record],
    objectives: list[str],
    maximize: list[bool],
    n_weight_samples: int = 20,
) -> dict[str, list[dict[str, Any]]]:
    """Compute weighted scalarization for multiple weight vectors.

    This is an analysis-specific utility not in the canonical implementation.
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
                "cell_key": r.cell_key,
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
        """Run Pareto analysis using canonical Pareto implementation."""
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
