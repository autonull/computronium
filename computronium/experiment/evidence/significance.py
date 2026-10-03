"""Is the difference between two axis values real, or is it the spread? (E2)

A claim states a difference; a *significant* claim states a difference the
evidence cannot explain away. The two are not the same, so the report names
the test beside the number: a paired sign-flip permutation over the cells the
two axis values share, bootstrap CI on the mean difference, Cohen's dz.

Pairing is what makes this affordable. A factorial's two arms are compared on
the cells that differ *only* in the axis under test (see ``pairing_key``), so
each cell's own across-seed variance cancels out of the difference instead of
inflating it.

Fewer than ``MIN_SHARED_CELLS`` shared cells is **a finding, not a failure**:
the honest statement is "insufficient coverage", which is expressible here
(``p_value is None``) and rendered as such. A run that measured one arm twice
has no test to run, and saying so costs nothing.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from computronium.validation.statistics import (
    bootstrap_percentile_ci,
    cohens_dz,
    permutation_test_p,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from computronium.experiment.evidence.claims import CellMetrics

__all__ = [
    "DEFAULT_ALPHA",
    "MIN_SHARED_CELLS",
    "SIGNIFICANCE_TEST",
    "Resampling",
    "Significance",
    "paired_significance",
]

#: Shared cells a paired test needs before its p-value means anything.
MIN_SHARED_CELLS = 2
DEFAULT_ALPHA = 0.05
CI_ALPHA = 0.05
#: The name the report prints: a claim's p-value without its test is not a claim.
SIGNIFICANCE_TEST = "paired sign-flip permutation"


@dataclass(frozen=True, slots=True)
class Resampling:
    """How much resampling the test spends — a cost knob, not a claim knob.

    Attributes:
        alpha: Declared error rate for the verdict.
        n_boot: Bootstrap resamples for the CI on the mean difference.
        n_permutations: Sign flips for the paired permutation p-value.
        seed: RNG seed, so a report's p-value is reproducible.
    """

    alpha: float = DEFAULT_ALPHA
    n_boot: int = 10_000
    n_permutations: int = 10_000
    seed: int = 0


@dataclass(frozen=True, slots=True)
class Significance:
    """Whether the best arm's advantage over the worst is distinguishable.

    Attributes:
        axis: The structural axis the two arms differ on.
        metric: The payload key the difference was measured on.
        best_value: The arm with the higher mean.
        worst_value: The arm with the lower mean.
        shared_cells: Cells measured at *both* values — the pairs.
        mean_diff: Mean of the per-cell paired differences (best − worst).
        ci_lower: Lower bound of the bootstrap CI on ``mean_diff``.
        ci_upper: Upper bound of the bootstrap CI on ``mean_diff``.
        cohens_dz: Paired effect size, ``mean_diff / std(diffs)``.
        p_value: The permutation p-value, or ``None`` when coverage was too
            thin to run the test (a finding, not a failure).
        alpha: The declared error rate the verdict is read against.
    """

    axis: str
    metric: str
    best_value: str
    worst_value: str
    shared_cells: int
    mean_diff: float
    ci_lower: float
    ci_upper: float
    cohens_dz: float
    p_value: float | None
    alpha: float = DEFAULT_ALPHA

    def __post_init__(self) -> None:
        if self.p_value is None:
            return
        if not 0.0 <= self.p_value <= 1.0:
            msg = f"Significance.p_value must lie in [0, 1], got {self.p_value}"
            raise ValueError(msg)
        if self.shared_cells < MIN_SHARED_CELLS:
            msg = (
                f"Significance claims a p-value from {self.shared_cells} shared "
                f"cells, below the floor of {MIN_SHARED_CELLS}"
            )
            raise ValueError(msg)
        if self.ci_lower > self.ci_upper:
            msg = f"Significance CI is inverted: [{self.ci_lower}, {self.ci_upper}]"
            raise ValueError(msg)

    @property
    def tested(self) -> bool:
        """Whether a test ran at all (as opposed to coverage being refused)."""
        return self.p_value is not None

    @property
    def significant(self) -> bool:
        """Whether the difference clears the declared error rate."""
        return self.p_value is not None and self.p_value < self.alpha

    def render(self) -> str:
        """The verdict as one report line, with the test named beside it."""
        head = f"{self.axis}={self.best_value} vs {self.worst_value} on {self.metric}:"
        if not self.tested:
            return (
                f"{head} insufficient coverage "
                f"({self.shared_cells} shared cell(s), "
                f"{MIN_SHARED_CELLS} required) — no test run"
            )
        return (
            f"{head} {SIGNIFICANCE_TEST} p={self.p_value:.4f} "
            f"(alpha={self.alpha}, shared_cells={self.shared_cells}, "
            f"mean_diff={self.mean_diff:+.4f}, "
            f"CI{1 - CI_ALPHA:.0%}=[{self.ci_lower:+.4f}, {self.ci_upper:+.4f}], "
            f"dz={self.cohens_dz:+.2f}) — "
            f"{'significant' if self.significant else 'not significant'}"
        )

    @classmethod
    def insufficient(
        cls,
        *,
        axis: str,
        metric: str,
        best_value: str,
        worst_value: str,
        shared_cells: int,
        alpha: float = DEFAULT_ALPHA,
    ) -> Significance:
        """The honest null: too few shared cells to run a paired test."""
        return cls(
            axis=axis,
            metric=metric,
            best_value=best_value,
            worst_value=worst_value,
            shared_cells=shared_cells,
            mean_diff=math.nan,
            ci_lower=math.nan,
            ci_upper=math.nan,
            cohens_dz=math.nan,
            p_value=None,
            alpha=alpha,
        )


def paired_significance(
    best: Mapping[str, CellMetrics],
    worst: Mapping[str, CellMetrics],
    *,
    axis: str,
    metric: str,
    best_value: str,
    worst_value: str,
    resampling: Resampling = Resampling(),
) -> Significance:
    """Test one arm's advantage over another on the cells they share.

    Args:
        best: The higher arm's per-pair cell means, keyed by pair identity.
        worst: The lower arm's, keyed the same way.
        axis: The structural axis the two arms differ on.
        metric: The payload key the difference was measured on.
        best_value: The higher arm's axis value.
        worst_value: The lower arm's axis value.
        resampling: Error rate and resampling budget.

    Returns:
        A tested :class:`Significance`, or an ``insufficient`` one when fewer
        than ``MIN_SHARED_CELLS`` pairs exist.
    """
    shared = sorted(best.keys() & worst.keys())
    if len(shared) < MIN_SHARED_CELLS:
        return Significance.insufficient(
            axis=axis,
            metric=metric,
            best_value=best_value,
            worst_value=worst_value,
            shared_cells=len(shared),
            alpha=resampling.alpha,
        )

    diffs = [best[key].mean - worst[key].mean for key in shared]
    ci_lower, ci_upper = bootstrap_percentile_ci(
        diffs,
        n_boot=resampling.n_boot,
        alpha=CI_ALPHA,
        seed=resampling.seed,
    )
    p_value = permutation_test_p(
        diffs,
        [0.0] * len(diffs),
        n_perm=resampling.n_permutations,
        seed=resampling.seed,
    )
    dz = cohens_dz(diffs) if float(np.std(diffs, ddof=1)) > 0.0 else 0.0
    return Significance(
        axis=axis,
        metric=metric,
        best_value=best_value,
        worst_value=worst_value,
        shared_cells=len(shared),
        mean_diff=float(np.mean(diffs)),
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        cohens_dz=dz,
        p_value=p_value,
        alpha=resampling.alpha,
    )
