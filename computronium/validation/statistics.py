"""Pure inference statistics for the experiment reporter (architecture §7.1).

Implements the small, dependency-free statistics surface the reporter and the
nightly gate need: bootstrap confidence intervals (percentile + bias-corrected
and accelerated BCa), two-sample effect sizes (Cohen's d, Cliff's δ),
Benjamini-Hochberg FDR control, and a two-sample power estimate.

The shared primitives — bootstrap percentile intervals, paired and unpaired
effect sizes, permutation tests, and power — live in
``computronium.core.statistics`` and are re-exported here so the validation
pillar and the kernel cannot drift apart. Every function is pure and
NumPy-only so the module stays trivially testable and runs anywhere
(including the overnight smoke rail). Hypothesis-based property tests and
golden values live in ``tests/unit/validation/``.
"""

from __future__ import annotations

import math
from fractions import Fraction
from typing import TYPE_CHECKING

import numpy as np

from computronium.core.statistics import (
    Statistic,
    bootstrap_percentile_ci,
    cliffs_delta,
    cohens_d,
    cohens_dz,
    permutation_test_p,
    power_for_two_sample,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = [
    "Statistic",
    "benjamini_hochberg",
    "bootstrap_bca_ci",
    "bootstrap_ci",
    "bootstrap_percentile_ci",
    "cliffs_delta",
    "cohens_d",
    "cohens_dz",
    "fisher_exact_p_one_sided",
    "permutation_test_p",
    "power_for_two_sample",
    "spearman_rho",
]


def bootstrap_bca_ci(  # ruff: ignore[too-many-locals]
    data: Sequence[float],
    stat: Statistic = np.mean,
    *,
    n_boot: int = 10_000,
    alpha: float = 0.05,
    seed: int | None = None,
) -> tuple[float, float]:
    """Bias-corrected and accelerated (BCa) bootstrap confidence interval.

    BCa corrects the percentile interval for both median bias (via the bias
    correction ``z0``) and skew (via the acceleration ``a`` estimated from
    leave-one-out jackknife). Preferred over the plain percentile interval for
    skewed statistics such as ratios and time measurements.

    Args:
        data: Observed sample.
        stat: Statistic to bootstrap.
        n_boot: Number of resamples.
        alpha: Two-sided error rate.
        seed: Optional RNG seed for reproducibility.

    Returns:
        ``(lower, upper)`` BCa interval bounds.
    """
    arr = np.asarray(data, dtype=float)
    n = arr.size
    if n == 0:
        raise ValueError(  # descriptive message is the public API
            "cannot bootstrap an empty sample"
        )
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot, dtype=float)
    for i in range(n_boot):
        resample = arr[rng.integers(0, n, size=n)]
        boot[i] = stat(resample)

    observed = stat(arr)
    theta_hat = np.asarray(observed, dtype=float)
    if not np.isfinite(theta_hat) or boot.size == 0:
        raise ValueError(  # descriptive message is the public API
            f"statistic returned non-finite value {observed!r}"
        )

    from scipy.stats import norm

    z0 = norm.ppf((np.sum(boot < observed) + np.sum(boot == observed) / 2) / n_boot)
    z0 = float(np.clip(z0, -10, 10))

    jack = np.empty(n, dtype=float)
    for i in range(n):
        leave_out = np.delete(arr, i)
        jack[i] = stat(leave_out)
    mean_jack = np.mean(jack)
    num = np.sum((mean_jack - jack) ** 3)
    den = np.sum((mean_jack - jack) ** 2)
    a = 0.0 if den == 0 else float(num / (6 * den**1.5))
    a = float(np.clip(a, -0.5, 0.5))

    z_alpha = float(norm.ppf(alpha / 2))
    z_1_minus = -z_alpha

    def _adjust(z0z: float) -> float:
        num = z0 + z0z
        den = 1 - a * (z0 + z0z)
        return float(norm.cdf(z0 + num / den))

    lo_q = _adjust(z_alpha)
    hi_q = _adjust(z_1_minus)
    return float(np.quantile(boot, lo_q)), float(np.quantile(boot, hi_q))


def bootstrap_ci(
    data: Sequence[float],
    stat: Statistic = np.mean,
    *,
    n_boot: int = 10_000,
    alpha: float = 0.05,
    method: str = "percentile",
    seed: int | None = None,
) -> tuple[float, float]:
    """Dispatch to the requested bootstrap interval method.

    Args:
        data: Observed sample.
        stat: Statistic to bootstrap.
        n_boot: Number of resamples.
        alpha: Two-sided error rate.
        method: ``"percentile"`` or ``"bca"``.
        seed: Optional RNG seed.

    Returns:
        ``(lower, upper)`` interval bounds.

    Raises:
        ValueError: For an unknown ``method``.
    """
    if method == "percentile":
        return bootstrap_percentile_ci(
            data, stat, n_boot=n_boot, alpha=alpha, seed=seed
        )
    if method == "bca":
        return bootstrap_bca_ci(data, stat, n_boot=n_boot, alpha=alpha, seed=seed)
    raise ValueError(  # descriptive message is the public API
        f"unknown bootstrap method {method!r} (use 'percentile'|'bca')"
    )


def benjamini_hochberg(p_values: Sequence[float]) -> list[float]:
    """Apply Benjamini-Hochberg FDR control to a list of p-values.

    Returns the q-values (adjusted p-values) in the same order as the input.
    A comparison is significant at FDR ``q`` when ``q_value <= q``.

    Args:
        p_values: Raw p-values (one per comparison).

    Returns:
        Adjusted q-values, same order as input.

    Raises:
        ValueError: For negative or out-of-range p-values.
    """
    ps = np.asarray(p_values, dtype=float)
    if np.any((ps < 0) | (ps > 1)):
        raise ValueError(  # descriptive message is the public API
            "p-values must lie in [0, 1]"
        )
    n = ps.size
    if n == 0:
        return []
    order = np.argsort(ps, kind="stable")
    ranked = np.arange(1, n + 1)
    adjusted = ps[order] * n / ranked
    # Enforce monotonicity from the largest p-value down.
    for i in range(n - 2, -1, -1):
        adjusted[i] = min(adjusted[i], adjusted[i + 1])
    q = np.empty_like(adjusted)
    q[order] = np.minimum(adjusted, 1.0)
    return q.tolist()


def fisher_exact_p_one_sided(
    failures_treatment: int, failures_control: int, arm_size: int
) -> float:
    """Exact one-sided Fisher p-value that the control fails more often.

    Conditional on the observed total failure count, the control's failure
    count follows a hypergeometric distribution; the p-value is the
    probability of drawing at least ``failures_control`` failures into the
    control arm. Exact rational arithmetic (no scipy dependency).

    Args:
        failures_treatment: Seeds in the treatment arm failing the event.
        failures_control: Seeds in the control arm failing the event.
        arm_size: Per-arm seed count.

    Returns:
        P(control failures >= observed | margins), in [0, 1].
    """
    if not 0 <= failures_treatment <= arm_size or not 0 <= failures_control <= arm_size:
        raise ValueError("failure counts must lie within [0, arm_size]")
    total_failures = failures_treatment + failures_control
    total = 2 * arm_size
    p = Fraction(0)
    for k in range(failures_control, min(total_failures, arm_size) + 1):
        if total_failures - k > arm_size:
            continue
        p += Fraction(
            math.comb(total_failures, k)
            * math.comb(total - total_failures, arm_size - k),
            math.comb(total, arm_size),
        )
    return float(p)


def _average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    ranks = np.empty(values.size, dtype=float)
    sorted_vals = values[order]
    i = 0
    while i < values.size:
        j = i
        while j + 1 < values.size and sorted_vals[j + 1] == sorted_vals[i]:
            j += 1
        ranks[order[i : j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return ranks


def spearman_rho(a: Sequence[float], b: Sequence[float]) -> float:
    """Spearman rank correlation with average ranks for ties.

    Constant inputs (zero rank variance) return 0.0 rather than NaN — the
    TODO25 surrogate comparison degenerates to "no measured association"
    under saturation, not an error.
    """
    if len(a) != len(b):
        raise ValueError("spearman_rho requires equal-length inputs")
    if len(a) < 2:
        raise ValueError("spearman_rho requires at least 2 points")
    ra, rb = (
        _average_ranks(np.asarray(a, dtype=float)),
        _average_ranks(np.asarray(b, dtype=float)),
    )
    da, db = ra - ra.mean(), rb - rb.mean()
    denom = float(np.sqrt((da**2).sum() * (db**2).sum()))
    if denom == 0.0:
        return 0.0
    return float((da * db).sum() / denom)
