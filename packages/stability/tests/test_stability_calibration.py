"""Tests for the Ginibre ROC calibration machinery."""

from __future__ import annotations

from stability.calibration import (
    EXPLOSION_FACTOR,
    STATISTIC_KINDS,
    calibrate_ginibre_harvest,
    ginibre_run,
    harvest_bad_statistics,
    harvest_good_statistics,
    probe_interval_for_overhead,
    rates_at_tau,
    unrolled_divergence,
)


def test_unrolled_divergence_label_rule() -> None:
    explosive, state = ginibre_run(1.4, 0)
    assert unrolled_divergence(explosive, state, None)
    stable, state = ginibre_run(0.5, 0)
    assert not unrolled_divergence(stable, state, None)


def test_harvest_bad_statistics_only_divergent() -> None:
    stats = harvest_bad_statistics(dim=16, batch=2, gains=(0.5, 1.4), seeds_per_gain=2)
    assert stats["windowed_growth"]
    assert all(value > 1.0 for value in stats["windowed_growth"])


def test_harvest_good_statistics_stable_arms() -> None:
    stats = harvest_good_statistics(dim=16, batch=2, gains=(0.5, 0.7), seeds_per_gain=2)
    assert stats["windowed_growth"]
    assert all(value <= 2.0 for value in stats["windowed_growth"])


def test_probe_interval_for_overhead() -> None:
    assert probe_interval_for_overhead(0.0) == 1
    assert probe_interval_for_overhead(0.05) == 1
    assert probe_interval_for_overhead(13.0) == 130


def test_calibrate_ginibre_harvest_meets_acceptance() -> None:
    record = calibrate_ginibre_harvest(
        dim=16,
        batch=2,
        good_gains=(0.5, 0.7),
        bad_gains=(1.2, 1.4),
        seeds_per_gain=2,
    )
    report = record.calibration["windowed_growth"]
    assert report is not None
    assert report.false_kill_rate <= 0.05
    assert report.kill_rate >= 0.95
    deployed = record.deployed_tau["windowed_growth"]
    assert deployed[0] <= 0.05 and deployed[1] >= 0.95


def test_statistics_cover_both_kinds() -> None:
    assert set(STATISTIC_KINDS) == {"fast_proxy", "windowed_growth"}
    assert EXPLOSION_FACTOR == 1e3


def test_rates_at_tau() -> None:
    assert rates_at_tau([1.0, 1.0], [2.0, 2.0], 1.5) == (0.0, 1.0)
    assert rates_at_tau([2.0], [1.0], 1.5) == (1.0, 0.0)
