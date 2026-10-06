"""Pure inference statistics for the experiment reporter (architecture §7.1).

Kernel-internal copy of the statistics surface needed by evidence modules.
Implements bootstrap confidence intervals, paired effect sizes, and permutation
tests — pure and NumPy-only so the module stays trivially testable and runs
anywhere (including the overnight smoke rail).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence

import numpy as np

__all__ = [
    "bootstrap_percentile_ci",
    "cohens_dz",
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