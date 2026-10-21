"""Pure inference statistics for the experiment reporter (architecture §7.1).

The inference surface the evidence modules need — bootstrap confidence
intervals, paired effect sizes, permutation tests — is owned by
``computronium.core.statistics`` and re-exported here so the kernel and the
evidence pillar cannot drift apart. What this module adds is the Pareto
front analysis: fronts, hypervolume, and knee detection.

Every function is pure and NumPy-only so the module stays trivially testable
and runs anywhere (including the overnight smoke rail).
"""

from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

import numpy as np

from computronium.core.statistics import (
    Statistic,
    bootstrap_percentile_ci,
    cohens_dz,
    permutation_test_p,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = [
    "Statistic",
    "bootstrap_percentile_ci",
    "cohens_dz",
    "hypervolume",
    "knee_detection",
    "pareto_front",
    "permutation_test_p",
]


# Pareto front analysis helpers


def _validate_maximize(
    maximize: Sequence[bool] | None, n_objectives: int
) -> list[bool]:
    """Validate and return maximize list."""
    if maximize is None:
        return [False] * n_objectives
    if len(maximize) != n_objectives:
        raise ValueError(f"{len(maximize)} directions but {n_objectives} objectives")
    return list(maximize)


def _transform_for_minimization(
    points: np.ndarray, maximize: Sequence[bool]
) -> np.ndarray:
    """Transform points so all objectives are minimized."""
    transformed = points.copy()
    for j, m in enumerate(maximize):
        if m:
            transformed[:, j] = -transformed[:, j]
    return transformed


def _dominates(candidate: np.ndarray, incumbent: np.ndarray) -> bool:
    """Check if candidate dominates incumbent (both minimized)."""
    return bool(np.all(candidate <= incumbent) and np.any(candidate < incumbent))


def pareto_front(
    points: np.ndarray,
    maximize: Sequence[bool] | None = None,
) -> np.ndarray:
    """Return the Pareto front (non-dominated points) of a point set.

    A point is non-dominated if no other point is at least as good on every
    objective and strictly better on at least one.

    Args:
        points: Array of shape (n_points, n_objectives). Each row is a candidate
            solution, each column an objective value.
        maximize: Per-objective direction. ``True`` = maximize, ``False`` =
            minimize. If ``None``, all objectives are minimized.

    Returns:
        Boolean mask of shape (n_points,) where ``True`` indicates a point on
        the Pareto front. The mask preserves the original point ordering.
    """
    arr = np.asarray(points, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"points must be 2D array, got shape {arr.shape}")
    n_points, n_objectives = arr.shape
    if n_points == 0:
        return np.array([], dtype=bool)

    maximize = _validate_maximize(maximize, n_objectives)
    transformed = _transform_for_minimization(arr, maximize)

    is_dominated = np.zeros(n_points, dtype=bool)
    for i in range(n_points):
        if is_dominated[i]:
            continue
        for j in range(n_points):
            if i == j:
                continue
            if _dominates(transformed[j], transformed[i]):
                is_dominated[i] = True
                break

    return ~is_dominated


def _compute_reference(
    transformed: np.ndarray,
    reference: np.ndarray | None,
    maximize: Sequence[bool],
) -> np.ndarray:
    """Compute reference point for hypervolume."""
    n_objectives = transformed.shape[1]
    if reference is None:
        return np.max(transformed, axis=0) + 1e-6
    ref = np.asarray(reference, dtype=float)
    if ref.shape != (n_objectives,):
        raise ValueError(
            f"reference must have shape ({n_objectives},), got {ref.shape}"
        )
    for j, m in enumerate(maximize):
        if m:
            ref[j] = -ref[j]
    if np.any(ref < np.max(transformed, axis=0)):
        raise ValueError("reference point must dominate all front points")
    return ref


def _hv_inclusion_exclusion(front: np.ndarray, ref: np.ndarray) -> float:
    """Hypervolume via inclusion-exclusion principle.

    Exact for any dimension. O(2^n) in number of front points, so suitable
    for small fronts (typical Pareto fronts have < 50 points).
    """
    n_points, _ = front.shape
    if n_points == 0:
        return 0.0

    # Volume of a single box [p_i, ref]
    def box_volume(p: np.ndarray) -> float:
        return float(np.prod(ref - p))

    # Intersection of boxes for a subset of points
    def intersection_volume(indices: tuple[int, ...]) -> float:
        # Intersection box lower bounds are max of lower bounds
        lower = np.max(front[list(indices)], axis=0)
        if np.any(lower > ref):
            return 0.0
        return float(np.prod(ref - lower))

    hv = 0.0
    for k in range(1, n_points + 1):
        sign = 1 if k % 2 == 1 else -1
        for combo in combinations(range(n_points), k):
            hv += sign * intersection_volume(combo)
    return hv


def hypervolume(
    front: np.ndarray,
    reference: np.ndarray | None = None,
    maximize: Sequence[bool] | None = None,
) -> float:
    """Compute the hypervolume indicator of a Pareto front.

    The hypervolume is the volume of the objective space dominated by the front
    and bounded by a reference point. For 2D it's an area; for 3D it's a volume.

    Uses the inclusion-exclusion principle for exact hypervolume
    computation in any dimension. Complexity is O(2^n) in the number of
    front points, suitable for typical Pareto fronts.

    Args:
        front: Array of shape (n_front_points, n_objectives) containing only
            the non-dominated points. If points are not guaranteed to be on the
            front, they will be filtered first.
        reference: Reference point of shape (n_objectives,). Must dominate all
            front points (i.e., be worse on every objective). If ``None``, uses
            the worst value on each objective plus a small margin.
        maximize: Per-objective direction. ``True`` = maximize, ``False`` =
            minimize. If ``None``, all objectives are minimized.

    Returns:
        The hypervolume (non-negative float). Returns 0.0 if front is empty.

    Raises:
        ValueError: If reference point does not dominate the front.
    """
    arr = np.asarray(front, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"front must be 2D array, got shape {arr.shape}")
    n_points, n_objectives = arr.shape
    if n_points == 0:
        return 0.0

    maximize = _validate_maximize(maximize, n_objectives)
    transformed = _transform_for_minimization(arr, maximize)
    ref = _compute_reference(transformed, reference, maximize)

    return float(_hv_inclusion_exclusion(transformed, ref))


def _prepare_front_for_knee(
    front: np.ndarray,
    maximize: Sequence[bool] | None,
    normalize: bool,
) -> np.ndarray:
    """Prepare front for knee detection."""
    arr = np.asarray(front, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"front must be 2D array, got shape {arr.shape}")
    n_points, n_objectives = arr.shape
    if n_points < 2:
        raise ValueError("knee_detection requires at least 2 points")

    maximize = _validate_maximize(maximize, n_objectives)
    transformed = _transform_for_minimization(arr, maximize)

    if normalize:
        mins = np.min(transformed, axis=0)
        maxs = np.max(transformed, axis=0)
        ranges = maxs - mins
        ranges = np.where(ranges == 0, 1.0, ranges)
        transformed = (transformed - mins) / ranges

    return transformed


def _knee_2d(front: np.ndarray) -> int:
    """Find knee in 2D front using neighbor-line distance.

    Only considers interior points (1 to n-2). Endpoints are extremes.
    Returns index in the original front array.
    """
    n_points = front.shape[0]
    sorted_idx = np.argsort(front[:, 0])
    sorted_front = front[sorted_idx]

    max_dist = -1.0
    knee_sorted_idx = 1
    for i in range(1, n_points - 1):
        p = sorted_front[i]
        a = sorted_front[i - 1]
        b = sorted_front[i + 1]
        if np.allclose(a, b):
            d = np.linalg.norm(p - a)
        else:
            line_vec = b - a
            t = np.dot(p - a, line_vec) / np.dot(line_vec, line_vec)
            proj = a + t * line_vec
            d = np.linalg.norm(p - proj)
        if d > max_dist:
            max_dist = d
            knee_sorted_idx = i

    if max_dist < 1e-10:
        knee_sorted_idx = n_points // 2

    return int(sorted_idx[knee_sorted_idx])


def _knee_nd(front: np.ndarray) -> int:
    """Find knee in n-D front by projecting to 2D via PCA."""
    centered = front - np.mean(front, axis=0)
    _, _, Vt = np.linalg.svd(centered, full_matrices=False)
    projected = centered @ Vt[:2].T
    return _knee_2d(projected)


def knee_detection(
    front: np.ndarray,
    maximize: Sequence[bool] | None = None,
    normalize: bool = True,
) -> int:
    """Find the knee (elbow) point of a Pareto front.

    The knee point is the point of maximum curvature on the front, representing
    the best trade-off between objectives. For 2D fronts, this is the point
    furthest from the line connecting its two neighbors. For higher dimensions,
    the front is projected onto the 2D plane of the first two principal
    components before computing curvature.

    Args:
        front: Array of shape (n_front_points, n_objectives) containing the
            Pareto front points. If not guaranteed to be the front, call
            ``pareto_front`` first.
        maximize: Per-objective direction. ``True`` = maximize, ``False`` =
            minimize. If ``None``, all objectives are minimized.
        normalize: Whether to normalize objectives to [0, 1] before computing
            distances. Strongly recommended for objectives with different scales.

    Returns:
        Index of the knee point in the input ``front`` array (0-based).
        Returns -1 if front has fewer than 3 points (no well-defined knee).

    Raises:
        ValueError: If front has fewer than 2 points.
    """
    arr = np.asarray(front, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"front must be 2D array, got shape {arr.shape}")
    n_points, n_objectives = arr.shape
    if n_points < 2:
        raise ValueError("knee_detection requires at least 2 points")
    if n_points < 3:
        return -1

    transformed = _prepare_front_for_knee(front, maximize, normalize)

    if n_objectives == 2:
        return _knee_2d(transformed)
    return _knee_nd(transformed)
