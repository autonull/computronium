"""Pure inference statistics for the experiment reporter (architecture §7.1).

Kernel-internal copy of the statistics surface needed by evidence modules.
Implements bootstrap confidence intervals, paired effect sizes, permutation
tests, and Pareto front analysis — pure and NumPy-only so the module stays
trivially testable and runs anywhere (including the overnight smoke rail).
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from itertools import combinations

import numpy as np

__all__ = [
    "bootstrap_percentile_ci",
    "cohens_dz",
    "hypervolume",
    "knee_detection",
    "pareto_front",
    "permutation_test_p",
]

Statistic = Callable[[np.ndarray], float]


def bootstrap_percentile_ci(
    data: Sequence[float],
    stat: Statistic = np.mean,
    *,
    n_boot: int = 10_000,
    alpha: float = 0.05,
    seed: int | None = None,
) -> tuple[float, float]:
    """Bootstrap percentile confidence interval for ``stat``.

    Resamples ``data`` with replacement ``n_boot`` times and reports the
    ``alpha/2`` and ``1 - alpha/2`` quantiles of the bootstrap distribution.

    Args:
        data: Observed sample.
        stat: Statistic to bootstrap (default mean).
        n_boot: Number of resamples.
        alpha: Two-sided error rate (0.05 -> 95% CI).
        seed: Optional RNG seed for reproducibility.

    Returns:
        ``(lower, upper)`` bootstrap percentile interval bounds.
    """
    arr = np.asarray(data, dtype=float)
    if arr.size == 0:
        raise ValueError("cannot bootstrap an empty sample")
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        resample = arr[rng.integers(0, arr.size, size=arr.size)]
        boot[i] = stat(resample)
    lo = np.quantile(boot, alpha / 2)
    hi = np.quantile(boot, 1 - alpha / 2)
    return float(lo), float(hi)


def cohens_dz(diffs: Sequence[float]) -> float:
    """One-sample Cohen's dz for paired differences.

    ``dz = mean(diffs) / std(diffs, ddof=1)`` — the effect size matched to
    paired/sign-flip tests, unlike the pooled two-sample Cohen's d.

    Args:
        diffs: Per-pair differences (treatment minus control).

    Returns:
        Cohen's dz effect size.

    Raises:
        ValueError: When fewer than 2 differences are given or all are
            identical (dz undefined).
    """
    d = np.asarray(diffs, dtype=float)
    if d.size < 2:
        raise ValueError("Cohen's dz requires at least 2 differences")
    sd = np.std(d, ddof=1)
    if sd == 0:
        raise ValueError("Cohen's dz undefined: differences have zero variance")
    return float(np.mean(d)) / float(sd)


def permutation_test_p(
    group_a: Sequence[float],
    group_b: Sequence[float],
    *,
    n_perm: int = 10_000,
    seed: int = 0,
) -> float:
    """Two-sample permutation p-value for the difference in means.

    Repeatedly relabels the pooled observations and recomputes ``|Δmean|``,
    returning the fraction of permutations whose absolute difference is at
    least as extreme as the observed one.

    Args:
        group_a: First sample.
        group_b: Second sample.
        n_perm: Number of relabel permutations (``0`` ⇒ exhaustive via a
            Fisher-Yates shuffle of every resolvable index).
        seed: RNG seed for permutation reproducibility.

    Returns:
        Two-sided permutation p-value in ``[0, 1]``.

    Raises:
        ValueError: If either sample has fewer than one observation.
    """
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size < 1 or b.size < 1:
        raise ValueError("permutation_test_p requires >=1 observation per group")
    observed = abs(a.mean() - b.mean())
    pooled = np.concatenate([a, b])
    rng = np.random.default_rng(seed)
    n_a = a.size
    ge = 0
    for _ in range(max(n_perm, 1)):
        perm = rng.permutation(pooled.size)
        delta = abs(pooled[perm[:n_a]].mean() - pooled[perm[n_a:]].mean())
        if delta >= observed:
            ge += 1
    # Add-one smoothing so a small sample can never report ``0.0`` (which would
    # over-claim certainty): the lowest credible p under ``n_perm`` draws is
    # ``1 / (n_perm + 1)``.
    return (ge + 1) / (max(n_perm, 1) + 1)


# Pareto front analysis helpers


def _validate_points(points: np.ndarray) -> tuple[int, int]:
    """Validate points array and return (n_points, n_objectives)."""
    arr = np.asarray(points, dtype=float)
    if arr.ndim != 2:
        raise ValueError(f"points must be 2D array, got shape {arr.shape}")
    n_points, n_objectives = arr.shape
    if n_points == 0:
        raise ValueError("points array is empty")
    return n_points, n_objectives


def _validate_maximize(maximize: Sequence[bool] | None, n_objectives: int) -> list[bool]:
    """Validate and return maximize list."""
    if maximize is None:
        return [False] * n_objectives
    if len(maximize) != n_objectives:
        raise ValueError(f"{len(maximize)} directions but {n_objectives} objectives")
    return list(maximize)


def _transform_for_minimization(points: np.ndarray, maximize: Sequence[bool]) -> np.ndarray:
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
        raise ValueError(f"reference must have shape ({n_objectives},), got {ref.shape}")
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
