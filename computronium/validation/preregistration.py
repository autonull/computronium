"""Pre-registration & paired-comparison kit (RESEARCH3 prerequisite PR-4).

Provides the minimal contract every empirical claim must satisfy before it
enters a paper or a campaign gate:

- ``MIN_SEEDS`` policy constant with :func:`require_min_seeds` enforcement.
- :class:`ThresholdRegistration`: the pre-registered threshold template —
  declare metric, superiority margin, error rate, and seed budget *before*
  running; serializable to/from JSON for repo-checked registrations.
- :func:`paired_comparison`: paired-difference harness (bootstrap CI on the
  mean difference, sign-flip permutation p, Cohen's dz) evaluated against a
  registration.

Pure NumPy; reuses the bootstrap/permutation primitives in
``computronium.validation.statistics``.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

import numpy as np

from computronium.experiment.evidence.claims import DEFAULT_MIN_SEEDS
from computronium.validation.statistics import (
    bootstrap_percentile_ci,
    cohens_dz,
    permutation_test_p,
)

if TYPE_CHECKING:
    from computronium.experiment.schema.coordinate import Schedule

__all__ = [
    "DEFAULT_ALPHA",
    "MIN_SEEDS",
    "EquivalenceRegistration",
    "PairedComparison",
    "ThresholdRegistration",
    "paired_comparison",
    "require_min_seeds",
]

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

MIN_SEEDS = DEFAULT_MIN_SEEDS
DEFAULT_ALPHA = 0.05


def require_min_seeds(n_seeds: int, min_seeds: int = MIN_SEEDS) -> None:
    """Raise unless the seed budget meets the pre-registration floor."""
    if n_seeds < min_seeds:
        raise ValueError(
            f"seed budget {n_seeds} below pre-registration floor {min_seeds}"
        )


@dataclass(frozen=True, slots=True)
class ThresholdRegistration:
    """A pre-registered decision threshold for one empirical claim.

    Attributes:
        claim: Statement under test (e.g. "EqProp >= 80% MNIST accuracy").
        metric: Metric name the threshold applies to.
        threshold: Minimum material effect (metric units, treatment minus
            control).
        alpha: Family-wise error rate for the confirmation test.
        min_seeds: Minimum per-arm seed count.
        created: ISO date the registration was committed to the repo.
        box: The declared run box (a subset of ``Schedule.to_dict()``), kept
            because a threshold written for one box does not decide a claim
            measured at another (TODO95 D2).
    """

    claim: str
    metric: str
    threshold: float
    alpha: float = DEFAULT_ALPHA
    min_seeds: int = MIN_SEEDS
    created: str = ""
    box: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON registration files."""
        return asdict(self)

    def box_mismatch(self, schedule: Schedule) -> str | None:
        """The first declared box field the run's schedule disagrees with."""
        if not self.box:
            return None
        actual = schedule.to_dict()
        for key, declared in self.box.items():
            if actual.get(key) != declared:
                return f"{key}: registered {declared!r}, run {actual.get(key)!r}"
        return None

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> ThresholdRegistration:
        """Deserialize from a registration file."""
        box = data.get("box") or data.get("schedule")
        return cls(
            claim=str(data["claim"]),
            metric=str(data["metric"]),
            threshold=float(data["threshold"]),  # type: ignore[arg-type]
            alpha=float(data.get("alpha", DEFAULT_ALPHA)),  # type: ignore[arg-type]
            min_seeds=int(data.get("min_seeds", MIN_SEEDS)),  # type: ignore[arg-type]
            created=str(data.get("created", "")),
            box=dict(box) if isinstance(box, dict) else None,  # type: ignore[arg-type]
        )

    @classmethod
    def load(cls, path: Path) -> ThresholdRegistration:
        """Load a registration from a JSON file in the repo."""
        with path.open(encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


@dataclass(frozen=True, slots=True)
class EquivalenceRegistration:
    """A pre-registered two-sided margin for a parity claim.

    ``ThresholdRegistration`` asks whether a treatment beats a control by at
    least some amount; a tie is not expressible there. This registration
    declares the margin within which the paired difference counts as
    equivalent, so a parity claim is decided by the same file that fixed the
    margin before the run.

    Attributes:
        claim: Statement under test (e.g. "PEPITA matches gradient on MNIST").
        metric: Metric name the margin applies to.
        margin: Half-width of the equivalence interval, in metric units.
        alpha: Error rate of the paired CI the decision reads.
        min_seeds: Minimum per-arm seed count.
        created: ISO date the registration was committed to the repo.
        protocol: How the decision is computed, for the repo record.
    """

    claim: str
    metric: str
    margin: float
    alpha: float = DEFAULT_ALPHA
    min_seeds: int = MIN_SEEDS
    created: str = ""
    protocol: str = ""

    def __post_init__(self) -> None:
        if self.margin <= 0:
            msg = f"equivalence margin must be positive, got {self.margin}"
            raise ValueError(msg)

    def to_dict(self) -> dict[str, str | float | int]:
        """Serialize for JSON registration files."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> EquivalenceRegistration:
        """Deserialize from a registration file."""
        return cls(
            claim=str(data["claim"]),
            metric=str(data["metric"]),
            margin=float(data["margin"]),  # type: ignore[arg-type]
            alpha=float(data.get("alpha", DEFAULT_ALPHA)),  # type: ignore[arg-type]
            min_seeds=int(data.get("min_seeds", MIN_SEEDS)),  # type: ignore[arg-type]
            created=str(data.get("created", "")),
            protocol=str(data.get("protocol", "")),
        )

    @classmethod
    def load(cls, path: Path) -> EquivalenceRegistration:
        """Load a registration from a JSON file in the repo."""
        with path.open(encoding="utf-8") as f:
            return cls.from_dict(json.load(f))


@dataclass(frozen=True, slots=True)
class PairedComparison:
    """Paired-difference result between matched treatment/control seeds."""

    n: int
    mean_diff: float
    ci_lower: float
    ci_upper: float
    p_value: float
    cohens_dz: float

    def passes(
        self, registration: ThresholdRegistration, *, schedule: Schedule | None = None
    ) -> bool:
        """Confirm against a registration: CI excludes the margin at alpha.

        A registration that declares a box decides only a run at that box: a
        missing or disagreeing schedule refuses the claim instead of comparing
        two different instruments (TODO95 D2).
        """
        if registration.box and (
            schedule is None or registration.box_mismatch(schedule) is not None
        ):
            return False
        return self.ci_lower > registration.threshold and self.p_value < (
            registration.alpha
        )

    def passes_equivalence(self, registration: EquivalenceRegistration | float) -> bool:
        """Whether the two-sided CI lies inside the pre-registered margin.

        Args:
            registration: The equivalence registration, or its margin in metric
                units. The interval is ``[-margin, +margin]``, read from the
                harness's two-sided bootstrap CI at ``alpha``.
        """
        margin = (
            registration.margin
            if isinstance(registration, EquivalenceRegistration)
            else registration
        )
        if margin <= 0:
            msg = f"equivalence margin must be positive, got {margin}"
            raise ValueError(msg)
        if (
            isinstance(registration, EquivalenceRegistration)
            and self.n < registration.min_seeds
        ):
            return False
        return self.ci_lower >= -margin and self.ci_upper <= margin


def paired_comparison(
    treatment: list[float],
    control: list[float],
    *,
    n_boot: int = 10_000,
    n_permutations: int = 10_000,
    seed: int | None = None,
) -> PairedComparison:
    """Run the paired-comparison harness over matched seed results.

    Args:
        treatment: Per-seed metric values for the treatment arm.
        control: Per-seed metric values for the control arm (index-matched).
        n_boot: Bootstrap resamples for the CI on the mean difference.
        n_permutations: Sign-flip permutations for the exact p-value.
        seed: RNG seed for resampling reproducibility.

    Returns:
        A :class:`PairedComparison`; evaluate it with ``passes(registration)``.
    """
    require_min_seeds(min(len(treatment), len(control)))
    t = np.asarray(treatment, dtype=float)
    c = np.asarray(control, dtype=float)
    diffs = t - c

    ci_lo, ci_hi = bootstrap_percentile_ci(
        diffs.tolist(), stat=np.mean, n_boot=n_boot, seed=seed
    )
    p_value = permutation_test_p(
        diffs.tolist(),
        [0.0] * diffs.size,
        n_perm=n_permutations,
    )
    # Degenerate identical-arm case has zero-variance diffs (dz undefined);
    # report 0.0 so the harness degrades to "no effect" instead of crashing.
    dz = cohens_dz(diffs.tolist()) if np.std(diffs, ddof=1) > 0 else 0.0

    return PairedComparison(
        n=diffs.size,
        mean_diff=float(np.mean(diffs)),
        ci_lower=ci_lo,
        ci_upper=ci_hi,
        p_value=float(p_value),
        cohens_dz=float(dz),
    )
