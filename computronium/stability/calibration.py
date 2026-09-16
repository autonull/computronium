"""Adapter: PR-5 demo-harvest orchestration + generic calibration re-exports.

The generic ROC machinery (PR-5 acceptance triple, Ginibre harvest, rate
math) lives in the standalone ``stability`` package (Rule 6). What remains
here is computronium-coupled by nature: the demo-suite coordinate family
and the harvest drivers that build internal campaign systems.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
from stability.calibration import (
    EXPLOSION_FACTOR,
    GINIBRE_BATCH,
    GINIBRE_DIM,
    GINIBRE_GAINS,
    GINIBRE_SEEDS_PER_GAIN,
    HARVEST_SEED,
    OVERHEAD_BUDGET,
    STATISTIC_KINDS,
    UNROLL_STEPS,
    PR5Calibration,
    calibrate_ginibre_harvest,
    ginibre_run,
    harvest_bad_statistics,
    overhead_and_interval,
    probe_interval_for_overhead,
    rates_at_tau,
    unrolled_divergence,
)
from stability.guard import (
    DEFAULT_TAU,
    CalibrationReport,
    DisagreementReport,
    ProbeSpec,
    StabilityGuard,
    StatisticKind,
    calibrate_threshold,
    measure_guard_overhead,
    quantify_proxy_disagreement,
)

from computronium.state import CompositeState

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from computronium.state import SystemContext

    Transition = Callable[[CompositeState, "SystemContext | None"], CompositeState]

# The demo-suite coordinate family, expressed in campaign-builder syntax:
# D1/D2 (recurrent settling + credit arms), D6 (substrate arms), D7 (spike
# settle), D3-family P-axis arms, and the quickstart instantaneous arm.
DEMO_GOOD_COORDINATES: tuple[str, ...] = (
    "digital/recurrent/energy_minimization/null/thermodynamic_contrast/euclidean",
    "digital/recurrent/energy_minimization/null/gradient/euclidean",
    "digital/recurrent/energy_minimization/null/random_projections/euclidean",
    "memristive/recurrent/energy_minimization/null/thermodynamic_contrast/euclidean",
    "neuromorphic/recurrent/energy_minimization/null/thermodynamic_contrast/euclidean",
    "digital/feedforward/spike_integration/null/gradient/euclidean",
    "digital/feedforward/instantaneous/null/gradient/euclidean",
    "digital/recurrent/instantaneous/routing/gradient/euclidean",
    "digital/recurrent/instantaneous/fast_weights/gradient/euclidean",
)

# Representative coordinates for the proxy-disagreement quantification:
# the digital baseline and the two noisy substrates (D6 arms).
DISAGREEMENT_COORDINATES: tuple[str, ...] = (
    "digital/recurrent/energy_minimization/null/thermodynamic_contrast/euclidean",
    "memristive/recurrent/energy_minimization/null/thermodynamic_contrast/euclidean",
    "neuromorphic/recurrent/energy_minimization/null/thermodynamic_contrast/euclidean",
)

_DISAGREEMENT_BATCH = 16


def harvest_good_statistics(
    *,
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    batch_size: int,
    episodes: Sequence[int],
    window: int = 10,
    coordinates: tuple[str, ...] = DEMO_GOOD_COORDINATES,
    seed: int = HARVEST_SEED,
) -> dict[StatisticKind, list[float]]:
    """Guard statistics over the known-good demo-suite coordinate arms."""
    from computronium.core.campaign.evaluation import (
        activity_transition,
        build_coordinate_system,
        episode_batch,
    )

    stats: dict[StatisticKind, list[float]] = {kind: [] for kind in STATISTIC_KINDS}
    for index, coordinate in enumerate(coordinates):
        with torch.random.fork_rng():
            torch.manual_seed(seed + index)
            joint = build_coordinate_system(
                coordinate,
                input_dim=input_dim,
                output_dim=output_dim,
                hidden_dims=hidden_dims,
            )
        transition = activity_transition(joint)
        context = joint.context
        for episode in episodes:
            x, _ = episode_batch(episode, input_dim=input_dim, batch_size=batch_size)
            z = CompositeState(activity={"x": x}, plastic={}, substrate={})
            for kind in STATISTIC_KINDS:
                guard = StabilityGuard(
                    threshold=float("inf"), statistic=kind, window=window
                )
                stats[kind].append(guard.probe(transition, z, context))  # type: ignore[arg-type]
    return stats


def _quantify_disagreement(
    coordinates: tuple[str, ...],
    *,
    input_dim: int,
    hidden_dims: tuple[int, ...],
    probes: ProbeSpec,
    seed: int,
) -> dict[str, DisagreementReport]:
    from computronium.core.campaign.evaluation import (
        activity_transition,
        build_coordinate_system,
        episode_batch,
    )

    reports: dict[str, DisagreementReport] = {}
    for index, coordinate in enumerate(coordinates):
        with torch.random.fork_rng():
            torch.manual_seed(seed + index)
            joint = build_coordinate_system(
                coordinate,
                input_dim=input_dim,
                output_dim=input_dim,
                hidden_dims=hidden_dims,
            )
        x, _ = episode_batch(0, input_dim=input_dim, batch_size=_DISAGREEMENT_BATCH)
        z = CompositeState(activity={"x": x}, plastic={}, substrate={})
        reports[coordinate] = quantify_proxy_disagreement(
            activity_transition(joint),  # type: ignore[arg-type]
            z,  # type: ignore[arg-type]
            joint.context,  # type: ignore[arg-type]
            probes=probes,
        )
    return reports


def calibrate_demo_harvest(  # ruff: ignore[too-many-arguments]
    *,
    input_dim: int = 784,
    hidden_dims: tuple[int, ...] = (32,),
    output_dim: int = 10,
    batch_size: int = 64,
    episodes: Sequence[int] = (0, 1, 2, 3),
    window: int = 10,
    max_false_kill: float = 0.05,
    min_kill_rate: float = 0.95,
    overhead_budget: float = OVERHEAD_BUDGET,
    disagreement_input_dim: int = 8,
    disagreement_hidden_dims: tuple[int, ...] = (16,),
    disagreement_probes: ProbeSpec | None = None,
    include_demo_cost_probe: bool = True,
    ginibre_dim: int = GINIBRE_DIM,
    ginibre_batch: int = GINIBRE_BATCH,
    ginibre_gains: tuple[float, ...] = GINIBRE_GAINS,
    ginibre_seeds: int = GINIBRE_SEEDS_PER_GAIN,
    seed: int = HARVEST_SEED,
) -> PR5Calibration:
    """Run the full PR-5 calibration over the demo-harvest.

    See the standalone ``stability`` package for the generic machinery;
    this driver supplies the computronium demo-suite known-good arms and
    the campaign coordinate builder. The registered artifact is
    ``docs/figures/registered/stability_guard_pr5.json``.
    """
    from computronium.core.campaign.evaluation import (
        activity_transition,
        build_coordinate_system,
        episode_batch,
    )

    good = harvest_good_statistics(
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        output_dim=output_dim,
        batch_size=batch_size,
        episodes=episodes,
        window=window,
        seed=seed,
    )
    bad = harvest_bad_statistics(
        dim=ginibre_dim,
        batch=ginibre_batch,
        gains=ginibre_gains,
        seeds_per_gain=ginibre_seeds,
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

    with torch.random.fork_rng():
        torch.manual_seed(seed)
        overhead_joint = build_coordinate_system(
            DEMO_GOOD_COORDINATES[0],
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_dims=hidden_dims,
        )
    overhead_x, _ = episode_batch(0, input_dim=input_dim, batch_size=batch_size)
    overhead_z = CompositeState(activity={"x": overhead_x}, plastic={}, substrate={})
    overhead, interval = overhead_and_interval(
        activity_transition(overhead_joint),  # type: ignore[arg-type]
        overhead_z,  # type: ignore[arg-type]
        overhead_joint.context,  # type: ignore[arg-type]
        window,
        overhead_budget,
        n_steps=5,
    )

    disagreement = _quantify_disagreement(
        DISAGREEMENT_COORDINATES,
        input_dim=disagreement_input_dim,
        hidden_dims=disagreement_hidden_dims,
        probes=disagreement_probes or ProbeSpec(n_probes=10, seed=seed),
        seed=seed,
    )
    if include_demo_cost_probe:
        with torch.random.fork_rng():
            torch.manual_seed(seed)
            cost_joint = build_coordinate_system(
                DEMO_GOOD_COORDINATES[0],
                input_dim=input_dim,
                output_dim=output_dim,
                hidden_dims=hidden_dims,
            )
        cost_x, _ = episode_batch(0, input_dim=input_dim, batch_size=batch_size)
        cost_z = CompositeState(activity={"x": cost_x}, plastic={}, substrate={})
        disagreement[f"demo_dims_cost/{DEMO_GOOD_COORDINATES[0]}"] = (
            quantify_proxy_disagreement(
                activity_transition(cost_joint),  # type: ignore[arg-type]
                cost_z,  # type: ignore[arg-type]
                cost_joint.context,  # type: ignore[arg-type]
                probes=ProbeSpec(n_probes=1, seed=seed),
            )
        )

    family: dict[str, object] = {
        "good_coordinates": list(DEMO_GOOD_COORDINATES),
        "input_dim": input_dim,
        "hidden_dims": list(hidden_dims),
        "output_dim": output_dim,
        "batch_size": batch_size,
        "episodes": list(episodes),
        "window": window,
        "bad_family": {
            "type": "ginibre_linear",
            "dim": ginibre_dim,
            "batch": ginibre_batch,
            "gains": list(ginibre_gains),
            "seeds_per_gain": ginibre_seeds,
            "label_rule": (
                f"norm > {EXPLOSION_FACTOR:.0e}x initial over {UNROLL_STEPS} steps"
            ),
        },
        "overhead_budget": overhead_budget,
        "max_false_kill": max_false_kill,
        "min_kill_rate": min_kill_rate,
        "seed": seed,
    }
    return PR5Calibration(
        good=good,
        bad=bad,
        calibration=calibration,
        deployed_tau=deployed,
        overhead_ratio=overhead,
        probe_interval=interval,
        disagreement=disagreement,
        family=family,
    )


__all__ = [  # ruff: ignore[unsorted-dunder-all]
    "DEMO_GOOD_COORDINATES",
    "DISAGREEMENT_COORDINATES",
    "calibrate_demo_harvest",
    "harvest_good_statistics",
    "EXPLOSION_FACTOR",
    "UNROLL_STEPS",
    "GINIBRE_DIM",
    "GINIBRE_BATCH",
    "GINIBRE_GAINS",
    "GINIBRE_SEEDS_PER_GAIN",
    "HARVEST_SEED",
    "OVERHEAD_BUDGET",
    "PR5Calibration",
    "STATISTIC_KINDS",
    "calibrate_ginibre_harvest",
    "ginibre_run",
    "harvest_bad_statistics",
    "overhead_and_interval",
    "probe_interval_for_overhead",
    "rates_at_tau",
    "unrolled_divergence",
    "calibrate_threshold",
    "measure_guard_overhead",
    "quantify_proxy_disagreement",
]
