"""Scientific validity protocol for experiment evidence.

Implements WP1.5 deliverables:
- Matched-cost comparison protocol (CostBudget, ComparisonGuard)
- Effect-size + uncertainty representation
- Synthetic known-ground-truth fixture
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from scipy import stats


class CostBudgetKind(StrEnum):
    """Kind of cost budget for matched-cost comparisons."""

    EVAL_COUNT = "eval_count"
    WALLTIME_S = "walltime_s"
    FLOPS = "flops"


@dataclass(frozen=True, slots=True)
class CostBudget:
    """Cost budget for matched-cost comparison protocol.

    Comparisons are only valid within the same budget tier.
    """

    kind: CostBudgetKind
    limit: float

    def __post_init__(self) -> None:
        if self.limit <= 0:
            raise ValueError("CostBudget.limit must be positive")

    def matches(self, other: CostBudget) -> bool:
        """Check if another budget matches this one (same kind and limit)."""
        return self.kind == other.kind and math.isclose(
            self.limit, other.limit, rel_tol=1e-9
        )

    @classmethod
    def eval_count(cls, count: int) -> CostBudget:
        return cls(CostBudgetKind.EVAL_COUNT, float(count))

    @classmethod
    def walltime(cls, seconds: float) -> CostBudget:
        return cls(CostBudgetKind.WALLTIME_S, seconds)

    @classmethod
    def flops(cls, flops: float) -> CostBudget:
        return cls(CostBudgetKind.FLOPS, flops)


class ComparisonError(Exception):
    """Raised when a comparison is invalid per the matched-cost protocol."""


class ComparisonGuard:
    """Guard for matched-cost comparisons.

    Enforces that comparisons only occur within the same budget tier.
    Refuses or labels unmatched pairs per R65.
    """

    def __init__(self, budget: CostBudget) -> None:
        self._budget = budget

    @property
    def budget(self) -> CostBudget:
        return self._budget

    def check(self, other_budget: CostBudget) -> None:
        """Verify that another budget matches the guarded budget.

        Raises:
            ComparisonError: If budgets don't match.
        """
        if not self._budget.matches(other_budget):
            raise ComparisonError(
                f"Budget mismatch: expected {self._budget.kind.value}={self._budget.limit}, "
                f"got {other_budget.kind.value}={other_budget.limit}. "
                "Comparisons only valid within same budget tier."
            )

    def check_or_label(
        self,
        other_budget: CostBudget,
        label_unmatched: bool = True,
    ) -> tuple[bool, str | None]:
        """Check budget match, optionally returning a label instead of raising.

        Args:
            other_budget: Budget to compare against.
            label_unmatched: If True, return (False, label) for mismatches instead of raising.

        Returns:
            Tuple of (matches, label_or_none). If matches, label is None.
            If not matches and label_unmatched=True, label describes the mismatch.
        """
        if self._budget.matches(other_budget):
            return True, None
        label = (
            f"BUDGET_MISMATCH:{self._budget.kind.value}={self._budget.limit}"
            f" vs {other_budget.kind.value}={other_budget.limit}"
        )
        if label_unmatched:
            return False, label
        raise ComparisonError(f"Budget mismatch: {label}")


@dataclass(frozen=True, slots=True)
class EffectSizeResult:
    """Effect size result with confidence interval.

    Primary endpoint: best validation score after B evaluations.
    Secondary: evaluations to reach target τ, area under optimization curve,
    compute-normalized improvement.
    All with confidence intervals (bootstrap over seeds).
    """

    primary_metric: str
    effect_size: float  # Cohen's d
    ci_lower: float  # 95% CI lower bound
    ci_upper: float  # 95% CI upper bound
    p_value: float
    test_used: str  # "paired_t" or "wilcoxon"
    n_tasks: int
    n_seeds: int
    budget: CostBudget
    secondary: dict[str, float] | None = None

    def is_significant(self, alpha: float = 0.05) -> bool:
        return self.p_value < alpha

    def to_dict(self) -> dict[str, Any]:
        return {
            "primary_metric": self.primary_metric,
            "effect_size": self.effect_size,
            "ci_lower": self.ci_lower,
            "ci_upper": self.ci_upper,
            "p_value": self.p_value,
            "test_used": self.test_used,
            "n_tasks": self.n_tasks,
            "n_seeds": self.n_seeds,
            "budget": {"kind": self.budget.kind.value, "limit": self.budget.limit},
            "secondary": self.secondary,
        }


def cohens_d_paired(
    x: list[float], y: list[float]
) -> tuple[float, float, float, float]:
    """Compute Cohen's d for paired samples with 95% CI and p-value.

    Returns:
        Tuple of (d, ci_lower, ci_upper, p_value) for paired t-test.
    """
    if len(x) != len(y):
        raise ValueError("Paired samples must have same length")
    n = len(x)
    if n < 2:
        raise ValueError("Need at least 2 paired samples")

    diffs = [xi - yi for xi, yi in zip(x, y, strict=True)]
    mean_diff = statistics.mean(diffs)
    sd_diff = statistics.stdev(diffs) if n > 1 else 0.0

    d = 0.0 if sd_diff == 0 else mean_diff / sd_diff

    # Standard error of Cohen's d for paired samples
    se_d = math.sqrt((1 / n) + (d**2 / (2 * n)))

    # 95% CI using normal approximation
    z = 1.96
    ci_lower = d - z * se_d
    ci_upper = d + z * se_d

    # Paired t-test p-value
    if sd_diff == 0:
        p_value = 1.0
    else:
        t_stat = mean_diff / (sd_diff / math.sqrt(n))
        p_value = float(2 * stats.t.sf(abs(t_stat), df=n - 1))

    return d, ci_lower, ci_upper, p_value


def wilcoxon_paired(x: list[float], y: list[float]) -> tuple[float, float]:
    """Wilcoxon signed-rank test for paired samples.

    Returns:
        Tuple of (statistic, p_value).
    """
    if len(x) != len(y):
        raise ValueError("Paired samples must have same length")
    return stats.wilcoxon(x, y, alternative="two-sided")


def compute_effect_size(
    treatment: list[float],
    control: list[float],
    primary_metric: str,
    budget: CostBudget,
    n_tasks: int,
    n_seeds: int,
    paired: bool = True,
    use_wilcoxon: bool = False,
) -> EffectSizeResult:
    """Compute effect size with confidence interval and p-value.

    Args:
        treatment: Treatment group scores (best validation score at budget B).
        control: Control group scores (same tasks, same seeds).
        primary_metric: Name of the primary metric.
        budget: Cost budget used for the comparison.
        n_tasks: Number of independent tasks (must be >= 10 per protocol).
        n_seeds: Number of independent seeds per task (must be >= 5 per protocol).
        paired: Whether samples are paired (same seeds, same tasks).
        use_wilcoxon: Use Wilcoxon instead of paired t-test.

    Returns:
        EffectSizeResult with effect size, CI, and p-value.
    """
    if n_tasks < 10:
        raise ValueError(f"Protocol requires N_tasks >= 10, got {n_tasks}")
    if n_seeds < 5:
        raise ValueError(f"Protocol requires N_seeds >= 5, got {n_seeds}")
    if len(treatment) != len(control):
        raise ValueError("Treatment and control must have same length")

    if use_wilcoxon:
        stat, p_value = wilcoxon_paired(treatment, control)
        # For Wilcoxon, compute effect size as rank-biserial correlation
        n = len(treatment)
        d = 2 * stat / (n * (n + 1)) - 1  # rank-biserial
        # Approximate CI for rank-biserial (not standard)
        se = math.sqrt((2 * n + 1) / (6 * n * (n + 1)))
        ci_lower = d - 1.96 * se
        ci_upper = d + 1.96 * se
        test_used = "wilcoxon"
    else:
        d, ci_lower, ci_upper, p_value = cohens_d_paired(treatment, control)
        test_used = "paired_t"

    return EffectSizeResult(
        primary_metric=primary_metric,
        effect_size=d,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        p_value=p_value,
        test_used=test_used,
        n_tasks=n_tasks,
        n_seeds=n_seeds,
        budget=budget,
    )


# =============================================================================
# Synthetic Known-Ground-Truth Fixture
# =============================================================================


@dataclass(frozen=True, slots=True)
class SyntheticGroundTruth:
    """A synthetic experiment with known analytical ground truth.

    The response surface is a quadratic bowl with known optimum:
    f(x) = sum_i (x_i - opt_i)^2 + noise

    True optimum: x* = opt
    True minimum value: 0 (without noise)

    Axis interactions are controlled via the interaction_matrix.
    """

    dimension: int
    optimum: tuple[float, ...]
    interaction_matrix: tuple[tuple[float, ...], ...] | None = None
    noise_std: float = 0.0

    def __post_init__(self) -> None:
        if len(self.optimum) != self.dimension:
            raise ValueError("Optimum length must match dimension")
        if self.interaction_matrix is not None:
            if len(self.interaction_matrix) != self.dimension:
                raise ValueError("Interaction matrix dimension mismatch")
            for row in self.interaction_matrix:
                if len(row) != self.dimension:
                    raise ValueError("Interaction matrix must be square")

    def evaluate(self, params: tuple[float, ...], seed: int = 0) -> float:
        """Evaluate the synthetic function at given parameters.

        Args:
            params: Parameter values (length = dimension).
            seed: Random seed for noise.

        Returns:
            Function value (lower is better).
        """
        if len(params) != self.dimension:
            raise ValueError(f"Expected {self.dimension} params, got {len(params)}")

        rng = random.Random(seed)  # ruff: ignore[suspicious-non-cryptographic-random-usage] - synthetic fixture, not cryptographic

        # Quadratic form: (x - opt)^T A (x - opt)
        diff = [p - o for p, o in zip(params, self.optimum, strict=True)]

        if self.interaction_matrix is None:
            # Diagonal (no interactions)
            value = sum(d * d for d in diff)
        else:
            # Full quadratic form
            value = 0.0
            for i in range(self.dimension):
                for j in range(self.dimension):
                    value += diff[i] * self.interaction_matrix[i][j] * diff[j]

        # Add noise
        if self.noise_std > 0:
            value += rng.gauss(0, self.noise_std)

        return value

    def true_optimum(self) -> tuple[float, ...]:
        return self.optimum

    def true_minimum(self) -> float:
        return 0.0  # Without noise

    def true_effect_size(self, baseline_params: tuple[float, ...]) -> float:
        """True effect size (Cohen's d) of optimum vs baseline.

        Since we know the true values, this is the theoretical effect size
        assuming noise_std as the standard deviation.
        """
        baseline_val = sum(
            (b - o) ** 2 for b, o in zip(baseline_params, self.optimum, strict=True)
        )
        opt_val = 0.0
        if self.noise_std > 0:
            return (baseline_val - opt_val) / self.noise_std
        return float("inf") if baseline_val > 0 else 0.0


def create_synthetic_fixture(
    dimension: int = 6,
    interaction_strength: float = 0.3,
    noise_std: float = 0.1,
) -> SyntheticGroundTruth:
    """Create a standard synthetic fixture for protocol validation.

    The fixture has:
    - Known analytical optimum at [1.0, 2.0, 3.0, 4.0, 5.0, 6.0...]
    - Controlled pairwise interactions (interaction_strength on off-diagonals)
    - Known noise level

    This allows the kernel to recover known effects and validate the
    experimental machinery end-to-end.
    """
    optimum = tuple(float(i + 1) for i in range(dimension))

    # Create interaction matrix: identity + interaction_strength on off-diagonals
    interaction_matrix = []
    for i in range(dimension):
        row = []
        for j in range(dimension):
            if i == j:
                row.append(1.0)
            else:
                row.append(interaction_strength)
        interaction_matrix.append(tuple(row))

    return SyntheticGroundTruth(
        dimension=dimension,
        optimum=optimum,
        interaction_matrix=tuple(interaction_matrix),
        noise_std=noise_std,
    )


# Predefined fixture for protocol lock tests
SYNTHETIC_FIXTURE = create_synthetic_fixture(
    dimension=6,
    interaction_strength=0.3,
    noise_std=0.1,
)


__all__ = [
    "SYNTHETIC_FIXTURE",
    "ComparisonError",
    "ComparisonGuard",
    "CostBudget",
    "CostBudgetKind",
    "EffectSizeResult",
    "SyntheticGroundTruth",
    "cohens_d_paired",
    "compute_effect_size",
    "create_synthetic_fixture",
    "wilcoxon_paired",
]
