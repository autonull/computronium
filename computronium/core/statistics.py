"""Core statistics utilities for kernel packages.

Pure, dependency-minimal statistics functions that the experiment kernel
(surface/cli) can use without importing from the validation pillar.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import nct, t


def cohens_d(
    group_a: np.ndarray | list[float], group_b: np.ndarray | list[float]
) -> float:
    """Cohen's d (pooled standard deviation) between two samples.

    Positive values mean ``group_a`` is larger on average. Uses the pooled
    SD with the usual Bessel correction (n - 1) per group.

    Args:
        group_a: First sample.
        group_b: Second sample.

    Returns:
        Cohen's d effect size.

    Raises:
        ValueError: When either group is empty or has zero variance.
    """
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size < 2 or b.size < 2:
        raise ValueError("Cohen's d requires at least 2 observations per group")
    var_a = np.var(a, ddof=1)
    var_b = np.var(b, ddof=1)
    pooled = (var_a + var_b) / 2
    if pooled == 0:
        raise ValueError("Cohen's d undefined: both samples have zero variance")
    mean_diff = float(np.mean(a) - np.mean(b))
    return mean_diff / float(np.sqrt(pooled))


def cliffs_delta(
    group_a: np.ndarray | list[float], group_b: np.ndarray | list[float]
) -> float:
    """Cliff's delta (dominance measure) between two samples.

    ``δ = P(a > b) - P(a < b)``, bounded in ``[-1, 1]``. Non-parametric, so it
    is robust to outliers and skewed distributions where Cohen's d is fragile.

    Args:
        group_a: First sample.
        group_b: Second sample.

    Returns:
        Cliff's delta in ``[-1, 1]``.

    Raises:
        ValueError: When either group is empty.
    """
    a = np.asarray(group_a, dtype=float)
    b = np.asarray(group_b, dtype=float)
    if a.size == 0 or b.size == 0:
        raise ValueError("Cliff's delta requires two non-empty samples")
    wins = sum(1 for x in a for y in b if x > y)
    losses = sum(1 for x in a for y in b if x < y)
    return float((wins - losses) / (a.size * b.size))


def power_for_two_sample(
    d: float,
    n_per_group: int,
    alpha: float = 0.05,
) -> float:
    """Statistical power of a two-sample t-test for effect size ``d``.

    Closed-form approximation for the (equal-n, equal-variance) two-sample
    t-test: the test statistic is non-central t with ``2n - 2`` degrees of
    freedom and non-centrality ``d * sqrt(n / 2)``.

    Args:
        d: Population effect size (Cohen's d).
        n_per_group: Observations in each group.
        alpha: Two-sided significance level.

    Returns:
        Power (probability of rejecting the null) in ``[0, 1]``.
    """
    if n_per_group < 2:
        raise ValueError("power requires at least 2 observations per group")
    df = 2 * n_per_group - 2
    ncp = d * np.sqrt(n_per_group / 2)
    crit = float(t.ppf(1 - alpha / 2, df))
    # scipy's nct.cdf is numerically unstable for large |ncp| (returns NaN).
    # Use the survival function of the reflected statistic for the lower tail:
    #   P(T_ncp < -crit) = P(-T_ncp > crit) = sf(crit; df, -ncp)
    lower = float(nct.sf(crit, df, -ncp))
    upper = float(nct.sf(crit, df, ncp))
    power = float(np.clip(lower + upper, 0.0, 1.0))
    return power


__all__ = ["cliffs_delta", "cohens_d", "power_for_two_sample"]
