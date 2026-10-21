"""Core statistics utilities shared by the kernel, validation, and evidence pillars.

Single source of truth for the inference statistics the experiment kernel
needs without reaching into the validation pillar. Every function is pure and
NumPy-only at import time: scipy enters only inside the functions that need
it, so the module stays importable wherever the kernel runs.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

import numpy as np

__all__ = [
    "Statistic",
    "bootstrap_percentile_ci",
    "cliffs_delta",
    "cohens_d",
    "cohens_dz",
    "permutation_test_p",
    "power_for_two_sample",
    "required_sample_size",
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

    Raises:
        ValueError: When the sample is empty.
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


def cohens_d(group_a: Sequence[float], group_b: Sequence[float]) -> float:
    """Cohen's d (pooled standard deviation) between two samples.

    Positive values mean ``group_a`` is larger on average. Uses the pooled
    SD with the usual Bessel correction (n - 1) per group, matching scipy
    conventions for the two-sample t-test.

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


def cohens_dz(diffs: Sequence[float]) -> float:
    """One-sample Cohen's dz for paired differences.

    ``dz = mean(diffs) / std(diffs, ddof=1)`` — the effect size matched to
    paired/sign-flip tests, unlike the pooled two-sample :func:`cohens_d`.

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


def cliffs_delta(group_a: Sequence[float], group_b: Sequence[float]) -> float:
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
    from scipy.stats import nct, t

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


def required_sample_size(
    effect_size: float,
    power: float = 0.8,
    alpha: float = 0.05,
    *,
    min_samples: int = 2,
) -> int:
    """Required sample size per group for a two-sample t-test.

    Inverts the power calculation to find the minimum n per group needed
    to achieve the target power for a given effect size (Cohen's d).

    Uses the normal approximation: n = 2 * (z_{1-alpha/2} + z_{power})^2 / d^2

    Args:
        effect_size: Minimum practically significant effect size (Cohen's d).
        power: Required statistical power (default 0.8).
        alpha: Two-sided significance level (default 0.05).
        min_samples: Minimum sample size floor (default 2).

    Returns:
        Required sample size per group (ceiling of calculated value).
    """
    import math

    from scipy.stats import norm

    if effect_size <= 0:
        raise ValueError("effect_size must be positive")
    if not (0 < power < 1):
        raise ValueError("power must be in (0, 1)")
    if not (0 < alpha < 1):
        raise ValueError("alpha must be in (0, 1)")

    z_alpha = norm.ppf(1 - alpha / 2)
    z_power = norm.ppf(power)
    n = 2 * (z_alpha + z_power) ** 2 / (effect_size**2)
    return max(math.ceil(n), min_samples)
