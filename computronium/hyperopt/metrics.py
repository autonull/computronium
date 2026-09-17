"""
Multi-Objective Metrics

Implements Pareto dominance, non-dominated sorting, and composite scoring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from computronium.autoscientist.objectives import ObjectiveSpec

import pandas as pd

__all__ = [
    "TrialMetrics",
    "crowding_distance",
    "get_pareto_frontier",
    "non_dominated_indices",
    "non_dominated_sort",
    "rank_trials",
    "scalarize_objectives",
    "scalarize_row",
]


@dataclass(frozen=True, slots=True)
class TrialMetrics:
    """Metrics for a single trial."""

    trial_id: int
    model_name: str
    config: dict[str, object]

    # Objectives (4D)
    accuracy: float  # Maximize (0-1)
    perplexity: float  # Minimize
    iteration_time: float  # Minimize (seconds)
    param_count: float  # Minimize (millions)

    # Training metadata
    epochs_completed: int
    final_loss: float
    status: str  # 'completed', 'failed', 'running'

    # Computed objectives (not part of init)
    objectives: np.ndarray | None = field(init=False, repr=False, default=None)

    def __post_init__(self):
        # Normalize for comparison
        object.__setattr__(
            self,
            "objectives",
            np.array([
                self.accuracy,  # Higher is better
                -self.perplexity,  # Convert to maximization (higher is better)
                -self.iteration_time,  # Convert to maximization
                -self.param_count,  # Convert to maximization
            ]),
        )

    def dominates(self, other: TrialMetrics) -> bool:
        """Check if this trial Pareto-dominates another.

        A dominates B if A is >= B on all objectives AND strictly > on at least one.
        """
        better_or_equal = np.all(self.objectives >= other.objectives)
        strictly_better = np.any(self.objectives > other.objectives)
        return better_or_equal and strictly_better

    def composite_score(self, weights: dict[str, float] | None = None) -> float:
        """Calculate weighted composite score for ranking.

        Default weights balance all objectives equally.
        """
        if weights is None:
            weights = {"accuracy": 0.4, "perplexity": 0.3, "speed": 0.2, "params": 0.1}

        # Normalize each objective to [0, 1] scale (roughly)
        norm_acc = self.accuracy  # Already 0-1
        norm_ppl = max(0, 1 - self.perplexity / 10.0)  # PPL ~0-10
        norm_speed = max(0, 1 - self.iteration_time / 1.0)  # Time ~0-1s
        norm_params = max(0, 1 - self.param_count / 10.0)  # Params ~0-10M

        score = (
            weights["accuracy"] * norm_acc
            + weights["perplexity"] * norm_ppl
            + weights["speed"] * norm_speed
            + weights["params"] * norm_params
        )
        return score


def non_dominated_sort(trials: list[TrialMetrics]) -> list[list[int]]:
    """Non-dominated sorting (NSGA-II).

    Returns:
        fronts: List of fronts, where each front is a list of trial indices.
                Front 0 = Pareto frontier (best).
    """
    n = len(trials)
    domination_count = np.zeros(n, dtype=int)  # How many dominate this trial
    dominated_by = [[] for _ in range(n)]  # Which trials does this dominate

    # Build domination relationships
    for i in range(n):
        for j in range(i + 1, n):
            if trials[i].dominates(trials[j]):
                dominated_by[i].append(j)
                domination_count[j] += 1
            elif trials[j].dominates(trials[i]):
                dominated_by[j].append(i)
                domination_count[i] += 1

    # Extract fronts
    fronts = []
    current_front = [i for i in range(n) if domination_count[i] == 0]

    while current_front:
        fronts.append(current_front)
        next_front = []

        for i in current_front:
            for j in dominated_by[i]:
                domination_count[j] -= 1
                if domination_count[j] == 0:
                    next_front.append(j)

        current_front = next_front

    return fronts


def non_dominated_indices(
    values: list[tuple[float, ...]],
    *,
    maximize: tuple[bool, ...],
    tol: tuple[float, ...] | None = None,
) -> list[int]:
    """Indices of the Pareto-optimal points in ``values`` (order-preserving).

    Generic non-dominated filter over a list of fixed-width objective tuples.
    ``maximize[i]`` says whether axis ``i`` is to be maximised (True) or
    minimised (False). ``tol[i]`` is an epsilon applied to the *at-least-as-good*
    and *strictly-better* comparisons on axis ``i`` (default ``0.0``): a tuple
    only dominates another if it is ``>=`` (resp ``<=``) on every axis under the
    tolerance and strictly better on at least one. This is the single
    dominance predicate shared by the various frontier sinks in the codebase
    (``analysis.results``, ``experiment.reporting``, ``hyperopt.frontier``).

    Args:
        values: Objective tuples, all of the same width as ``maximize``.
        maximize: Per-axis maximisation flag (True = higher is better).
        tol: Per-axis tolerance; default all-zero.

    Returns:
        Indices of non-dominated points, in input order. An empty input yields
        ``[]``.
    """
    n = len(values)
    if n == 0:
        return []
    if tol is None:
        tol = (0.0,) * len(maximize)
    tol = tuple(tol)
    m = len(maximize)
    non_dominated: list[int] = []
    for i, a in enumerate(values):
        dominated = False
        for j, b in enumerate(values):
            if i == j:
                continue
            at_least_all = True
            strictly_any = False
            for k in range(m):
                if maximize[k]:
                    at_least, strict = (
                        b[k] >= a[k] - tol[k],
                        b[k] > a[k] + tol[k],
                    )
                else:
                    at_least, strict = (
                        b[k] <= a[k] + tol[k],
                        b[k] < a[k] - tol[k],
                    )
                at_least_all = at_least_all and at_least
                strictly_any = strictly_any or strict
            if at_least_all and strictly_any:
                dominated = True
                break
        if not dominated:
            non_dominated.append(i)
    return non_dominated


def crowding_distance(
    trials: list[TrialMetrics], front_indices: list[int]
) -> np.ndarray:
    """Calculate crowding distance for diversity preservation.

    Higher distance = more isolated = should be preserved.
    """
    n = len(front_indices)
    if n <= 2:
        return np.full(n, np.inf)

    distances = np.zeros(n)
    n_objectives = 4

    for obj_idx in range(n_objectives):
        # Sort by this objective
        sorted_indices = sorted(
            range(n), key=lambda i: trials[front_indices[i]].objectives[obj_idx]
        )

        # Boundary points get infinite distance
        distances[sorted_indices[0]] = np.inf
        distances[sorted_indices[-1]] = np.inf

        # Calculate distances for interior points
        obj_range = (
            trials[front_indices[sorted_indices[-1]]].objectives[obj_idx]
            - trials[front_indices[sorted_indices[0]]].objectives[obj_idx]
        )

        if obj_range > 0:
            for i in range(1, n - 1):
                distances[sorted_indices[i]] += (
                    trials[front_indices[sorted_indices[i + 1]]].objectives[obj_idx]
                    - trials[front_indices[sorted_indices[i - 1]]].objectives[obj_idx]
                ) / obj_range

    return distances


def get_pareto_frontier(trials: list[TrialMetrics]) -> list[int]:
    """Get indices of trials on the Pareto frontier (front 0)."""
    fronts = non_dominated_sort(trials)
    return fronts[0] if fronts else []


def rank_trials(
    trials: list[TrialMetrics], top_k: int | None = None
) -> list[tuple[int, float]]:
    """Rank trials by composite score.

    Returns:
        List of (trial_index, score) tuples, sorted best to worst.
    """
    scores = [(i, trial.composite_score()) for i, trial in enumerate(trials)]
    scores.sort(key=lambda x: x[1], reverse=True)

    if top_k is not None:
        scores = scores[:top_k]

    return scores


# --- Multi-objective scalarization (TODO31 Phase 3.1) -------------------------


def scalarize_row(
    values: dict[str, float],
    objectives: Sequence[ObjectiveSpec],
    *,
    normalizers: dict[str, Callable[[float], float]] | None = None,
) -> float:
    """Compute scalarized score for a single objective vector.

    Args:
        values: Dict of objective_name -> raw value.
        objectives: Configured objectives with weights and normalizers.
        normalizers: Optional override normalizers (defaults to ObjectiveSpec.normalizer).

    Returns:
        Scalar score where higher is better (all objectives normalized to
        maximize direction and weighted).
    """
    score = 0.0
    total_weight = 0.0
    for obj in objectives:
        name = obj.name.value
        if name not in values:
            continue
        raw_val = values[name]
        normalizer = (normalizers or {}).get(name) or obj.normalizer
        if normalizer is None:
            # Default: identity for maximize, reciprocal for minimize
            norm_val = raw_val if obj.direction == "maximize" else (1.0 / (1.0 + raw_val))
        else:
            norm_val = normalizer(raw_val)
        # Ensure maximize direction: normalizers already produce [0,1] where higher=better
        score += obj.weight * norm_val
        total_weight += obj.weight
    return score / total_weight if total_weight > 0 else 0.0


def scalarize_objectives(
    df: pd.DataFrame,
    objectives: Sequence[ObjectiveSpec],
    *,
    normalizers: dict[str, Callable[[float], float]] | None = None,
) -> pd.Series:
    """Add scalarized score column to a DataFrame of objective vectors.

    Args:
        df: DataFrame with columns matching objective names.
        objectives: Configured objectives with weights and normalizers.
        normalizers: Optional override normalizers.

    Returns:
        Series of scalar scores (higher is better).
    """
    scores = []
    for _, row in df.iterrows():
        vals = {o.name.value: float(row[o.name.value]) for o in objectives if o.name.value in row}
        scores.append(scalarize_row(vals, objectives, normalizers=normalizers))
    return pd.Series(scores, index=df.index, name="scalarized_score")
