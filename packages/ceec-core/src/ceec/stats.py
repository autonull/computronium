"""Pure statistics for probe-facing verdicts (TODO26 T26.F.1)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__ = ["ChanceVerdict", "chance_verdict"]


@dataclass(frozen=True, slots=True)
class ChanceVerdict:
    """At-chance statistics for a multi-seed accuracy campaign (TODO25 B.1).

    ``per_seed_band`` is the honest 2·binomial-SE width over the eval
    split; ``mean_at_chance`` carries the certified decision
    (``abs(mean − chance) ≤ 2·SE(n_seeds)``).
    """

    chance: float
    n_eval: int
    accuracies: tuple[float, ...]
    mean: float
    per_seed_band: float
    per_seed_in_band: tuple[bool, ...]
    mean_se: float
    mean_at_chance: bool

    @property
    def at_chance(self) -> bool:
        return self.mean_at_chance


def chance_verdict(
    accuracies: Sequence[float],
    n_eval: int,
    *,
    chance: float = 0.5,
) -> ChanceVerdict:
    """2·binomial-SE per-seed band + across-seed mean rule.

    ``n_eval`` is the per-seed evaluation-set size the accuracies were
    measured over; the band is ``2·sqrt(chance·(1−chance)/n_eval)``.
    """
    if not accuracies:
        raise ValueError("chance_verdict requires at least one accuracy")
    if n_eval < 1:
        raise ValueError("n_eval must be >= 1")
    n = len(accuracies)
    mean = sum(accuracies) / n
    band = 2.0 * math.sqrt(chance * (1.0 - chance) / n_eval)
    in_band = tuple(abs(a - chance) <= band for a in accuracies)
    if n > 1:
        var = sum((a - mean) ** 2 for a in accuracies) / (n - 1)
        se = max(math.sqrt(var / n), 1e-9)
    else:
        se = band / 2.0
    return ChanceVerdict(
        chance=chance,
        n_eval=n_eval,
        accuracies=tuple(accuracies),
        mean=mean,
        per_seed_band=band,
        per_seed_in_band=in_band,
        mean_se=se,
        mean_at_chance=abs(mean - chance) <= 2.0 * se,
    )
