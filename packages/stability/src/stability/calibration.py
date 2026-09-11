"""PR-5 ROC calibration machinery for the stability guard.

Known-bad statistics come from a Ginibre linear ensemble whose runs are
labeled by unrolled divergence (norm explosion); known-good statistics are
supplied by the host application's own known-good coordinate arms (see the
host-side demo-harvest adapter). The ROC calibration certifies the max-margin
operating point and the deployed ``DEFAULT_TAU``.

Measured findings recorded by the registered calibration artifact
(``stability_guard_pr5.json``, tiny and demo scale):
- ``windowed_growth`` reads ≈ 1.0 on every known-good arm — bounded
  activations — and fires only on genuinely explosive maps; it is the
  deployed kill statistic.
- ``fast_proxy`` is calibration-only: its one-step Jacobian-vector gain
  under-estimates σ_max on non-normal maps and is inflated by substrate
  noise on memristive/neuromorphic arms.
- Per-probe cost is a multiple of a transition step (2-13x measured), so the
  <10% overhead bar is met through the calibrated probe interval.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, cast

import torch
from torch import Tensor

from stability.guard import (
    DEFAULT_TAU,
    CalibrationReport,
    DisagreementReport,
    StabilityGuard,
    StatisticKind,
    calibrate_threshold,
    measure_guard_overhead,
)
from stability.state import CompositeState

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from stability.state import SystemContext

    Transition = Callable[[CompositeState, "SystemContext | None"], CompositeState]

STATISTIC_KINDS: tuple[StatisticKind, ...] = ("fast_proxy", "windowed_growth")

GINIBRE_GAINS: tuple[float, ...] = (0.95, 1.0, 1.05, 1.1, 1.2, 1.4)
GINIBRE_SEEDS_PER_GAIN = 3
GINIBRE_DIM = 32
GINIBRE_BATCH = 4
UNROLL_STEPS = 200
EXPLOSION_FACTOR = 1e3
OVERHEAD_BUDGET = 0.10
HARVEST_SEED = 0


@dataclass(frozen=True, slots=True)
class PR5Calibration:
    """The PR-5 acceptance triple over one calibration harvest run.

    Attributes:
        good: Harvested known-good statistics per statistic kind.
        bad: Harvested known-bad (divergence-labeled) statistics per kind.
        calibration: ROC report per kind (``None`` = infeasible classes).
        deployed_tau: False-kill / kill-rate at ``DEFAULT_TAU`` per kind.
        overhead_ratio: Probe-cost / transition-step-cost per kind.
        probe_interval: Episodes between probes meeting the overhead budget.
        disagreement: Proxy-vs-full-Jacobian reports keyed by coordinate.
        family: Harvest metadata (dims, label rule, budgets).
    """

    good: dict[StatisticKind, list[float]]
    bad: dict[StatisticKind, list[float]]
    calibration: dict[StatisticKind, CalibrationReport | None]
    deployed_tau: dict[StatisticKind, tuple[float, float]]
    overhead_ratio: dict[StatisticKind, float]
    probe_interval: dict[StatisticKind, int]
    disagreement: dict[str, DisagreementReport]
    family: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        """JSON-serializable artifact shape."""
        return {
            "good_summary": {kind: _summarize(v) for kind, v in self.good.items()},
            "bad_summary": {kind: _summarize(v) for kind, v in self.bad.items()},
            "calibration": {
                kind: asdict(report) if report is not None else None
                for kind, report in self.calibration.items()
            },
            "deployed_tau": {
                kind: {
                    "tau": DEFAULT_TAU,
                    "false_kill_rate": false_kill,
                    "kill_rate": kill_rate,
                }
                for kind, (false_kill, kill_rate) in self.deployed_tau.items()
            },
            "overhead_ratio": dict(self.overhead_ratio),
            "probe_interval": dict(self.probe_interval),
            "disagreement": {
                coordinate: asdict(report)
                for coordinate, report in self.disagreement.items()
            },
            "family": dict(self.family),
        }


def _summarize(values: list[float]) -> dict[str, float | int]:
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "min": min(values),
        "max": max(values),
        "mean": sum(values) / len(values),
    }


def _activity_norm(z: CompositeState) -> float:
    x = z.activity.get("x")
    return float(torch.linalg.vector_norm(x)) if isinstance(x, Tensor) else 0.0


def ginibre_run(
    gain: float,
    seed: int,
    dim: int = GINIBRE_DIM,
    batch: int = GINIBRE_BATCH,
) -> tuple[Transition, CompositeState]:
    """One closed-form linear run: ``gain/sqrt(dim)``-scaled Ginibre weight."""
    generator = torch.Generator().manual_seed(seed)
    weight = torch.randn(dim, dim, generator=generator) * (gain / dim**0.5)
    state = CompositeState(
        activity={"x": torch.randn(batch, dim, generator=generator)},
        plastic={},
        substrate={},
    )

    def transition(z: CompositeState, _context: SystemContext | None) -> CompositeState:
        x = z.activity["x"]
        return CompositeState(
            activity={"x": x @ weight.T if isinstance(x, Tensor) else x},
            plastic=z.plastic,
            substrate=z.substrate,
        )

    return transition, state


def unrolled_divergence(
    transition: Transition,
    z: CompositeState,
    context: SystemContext | None,
    *,
    steps: int = UNROLL_STEPS,
    factor: float = EXPLOSION_FACTOR,
) -> bool:
    """Label rule: activity norm explodes past ``factor`` x initial or NaNs."""
    base = _activity_norm(z)
    current = z
    for _ in range(steps):
        current = transition(current, context)
        norm = _activity_norm(current)
        if not math.isfinite(norm) or norm > factor * base:
            return True
    return False


def harvest_bad_statistics(
    *,
    dim: int = GINIBRE_DIM,
    batch: int = GINIBRE_BATCH,
    gains: tuple[float, ...] = GINIBRE_GAINS,
    seeds_per_gain: int = GINIBRE_SEEDS_PER_GAIN,
    window: int = 10,
) -> dict[StatisticKind, list[float]]:
    """Guard statistics over verified-divergent Ginibre runs.

    Non-diverging (marginal) runs enter neither set: they are not known-good
    coordinates and not verified-unstable.
    """
    stats: dict[StatisticKind, list[float]] = {kind: [] for kind in STATISTIC_KINDS}
    for gain in gains:
        for seed in range(seeds_per_gain):
            transition, state = ginibre_run(gain, seed, dim, batch)
            if not unrolled_divergence(transition, state, None):
                continue
            # The closed-form transition ignores its context; the probe's
            # declared signature still requires a (typed-null) context.
            context = cast("SystemContext", None)
            for kind in STATISTIC_KINDS:
                guard = StabilityGuard(
                    threshold=float("inf"), statistic=kind, window=window
                )
                stats[kind].append(guard.probe(transition, state, context))
    return stats


def harvest_good_statistics(
    *,
    dim: int = GINIBRE_DIM,
    batch: int = GINIBRE_BATCH,
    gains: tuple[float, ...] = (0.5, 0.7, 0.9),
    seeds_per_gain: int = GINIBRE_SEEDS_PER_GAIN,
    window: int = 10,
) -> dict[StatisticKind, list[float]]:
    """Guard statistics over verified-stable Ginibre runs (generic arms)."""
    stats: dict[StatisticKind, list[float]] = {kind: [] for kind in STATISTIC_KINDS}
    for gain in gains:
        for seed in range(seeds_per_gain):
            transition, state = ginibre_run(gain, seed, dim, batch)
            if unrolled_divergence(transition, state, None):
                continue
            context = cast("SystemContext", None)
            for kind in STATISTIC_KINDS:
                guard = StabilityGuard(
                    threshold=float("inf"), statistic=kind, window=window
                )
                stats[kind].append(guard.probe(transition, state, context))
    return stats


def rates_at_tau(
    good: Sequence[float], bad: Sequence[float], tau: float
) -> tuple[float, float]:
    """False-kill and kill rates of threshold ``tau`` over harvested stats."""
    good_arr = torch.tensor(good, dtype=torch.float64)
    bad_arr = torch.tensor(bad, dtype=torch.float64)
    false_kill = float((good_arr > tau).float().mean()) if good_arr.numel() else 0.0
    kill = float((bad_arr > tau).float().mean()) if bad_arr.numel() else 0.0
    return false_kill, kill


def probe_interval_for_overhead(ratio: float, budget: float = OVERHEAD_BUDGET) -> int:
    """Episodes between guard probes so amortized cost stays within budget."""
    if ratio <= 0.0:
        return 1
    return max(1, math.ceil(ratio / budget))


def overhead_and_interval(
    transition: Callable[[CompositeState, SystemContext | None], CompositeState],
    z: CompositeState,
    context: SystemContext | None,
    window: int,
    budget: float,
    n_steps: int,
) -> tuple[dict[StatisticKind, float], dict[StatisticKind, int]]:
    """Per-kind probe-cost ratio and the probe interval meeting the budget."""
    overhead: dict[StatisticKind, float] = {}
    interval: dict[StatisticKind, int] = {}
    for kind in STATISTIC_KINDS:
        guard = StabilityGuard(threshold=float("inf"), statistic=kind, window=window)
        ratio = measure_guard_overhead(transition, z, context, guard, n_steps=n_steps)  # type: ignore[arg-type]
        overhead[kind] = ratio
        interval[kind] = probe_interval_for_overhead(ratio, budget)
    return overhead, interval


def calibrate_ginibre_harvest(
    *,
    dim: int = GINIBRE_DIM,
    batch: int = GINIBRE_BATCH,
    good_gains: tuple[float, ...] = (0.5, 0.7, 0.9),
    bad_gains: tuple[float, ...] = GINIBRE_GAINS,
    seeds_per_gain: int = GINIBRE_SEEDS_PER_GAIN,
    window: int = 10,
    max_false_kill: float = 0.05,
    min_kill_rate: float = 0.95,
    seed: int = HARVEST_SEED,
) -> PR5Calibration:
    """Run the ROC calibration over the self-contained Ginibre harvest.

    A framework-free calibration path: known-good and known-bad statistics
    both come from closed-form linear runs (stable gains vs verified-divergent
    gains). Host applications with their own known-good arms should harvest
    those instead and call :func:`stability.guard.calibrate_threshold`.
    """
    good = harvest_good_statistics(
        dim=dim,
        batch=batch,
        gains=good_gains,
        seeds_per_gain=seeds_per_gain,
        window=window,
    )
    bad = harvest_bad_statistics(
        dim=dim,
        batch=batch,
        gains=bad_gains,
        seeds_per_gain=seeds_per_gain,
        window=window,
    )
    calibration: dict[StatisticKind, CalibrationReport | None] = {
        kind: calibrate_threshold(good[kind], bad[kind], max_false_kill, min_kill_rate)
        for kind in STATISTIC_KINDS
    }
    deployed: dict[StatisticKind, tuple[float, float]] = {
        kind: rates_at_tau(good[kind], bad[kind], DEFAULT_TAU)
        for kind in STATISTIC_KINDS
    }
    family: dict[str, object] = {
        "bad_family": {
            "type": "ginibre_linear",
            "dim": dim,
            "batch": batch,
            "gains": list(bad_gains),
            "seeds_per_gain": seeds_per_gain,
            "label_rule": (
                f"norm > {EXPLOSION_FACTOR:.0e}x initial over {UNROLL_STEPS} steps"
            ),
        },
        "good_gains": list(good_gains),
        "window": window,
        "max_false_kill": max_false_kill,
        "min_kill_rate": min_kill_rate,
        "seed": seed,
    }
    return PR5Calibration(
        good=good,
        bad=bad,
        calibration=calibration,
        deployed_tau=deployed,
        overhead_ratio={},
        probe_interval={},
        disagreement={},
        family=family,
    )


__all__ = [
    "EXPLOSION_FACTOR",
    "GINIBRE_BATCH",
    "GINIBRE_DIM",
    "GINIBRE_GAINS",
    "GINIBRE_SEEDS_PER_GAIN",
    "OVERHEAD_BUDGET",
    "STATISTIC_KINDS",
    "UNROLL_STEPS",
    "PR5Calibration",
    "calibrate_ginibre_harvest",
    "ginibre_run",
    "harvest_bad_statistics",
    "harvest_good_statistics",
    "overhead_and_interval",
    "probe_interval_for_overhead",
    "rates_at_tau",
    "unrolled_divergence",
]
