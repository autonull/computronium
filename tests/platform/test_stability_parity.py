"""Stability package parity + registered-artifact lock (TODO20 Phase 2.5)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import stability
import stability.calibration
import stability.guard
import stability.spectral_radius
import torch
from stability.calibration import calibrate_ginibre_harvest, ginibre_run

from computronium.stability import calibration as legacy_calibration
from computronium.stability import guard as legacy_guard
from computronium.stability import spectral_radius as legacy_spectral_radius

ARTIFACT = (
    Path(__file__).resolve().parents[2]
    / "docs/figures/registered/stability_guard_pr5.json"
)


def test_adapter_reexports_package_singletons() -> None:
    """Legacy computronium.stability paths resolve to the package (Rule 6)."""
    assert legacy_guard.attach is stability.guard.attach
    assert legacy_guard.StabilityGuard is stability.guard.StabilityGuard
    assert legacy_calibration.ginibre_run is stability.calibration.ginibre_run
    assert legacy_spectral_radius.dominant_singular_value is (
        stability.spectral_radius.dominant_singular_value
    )


def test_registered_artifact_matches_package_calibration() -> None:
    """PR-5 artifact lock: deployed tau and ROC operating point are pinned."""
    artifact = json.loads(ARTIFACT.read_text())
    windowed = artifact["calibration"]["calibration"]["windowed_growth"]
    deployed = artifact["calibration"]["deployed_tau"]["windowed_growth"]

    assert deployed["tau"] == stability.DEFAULT_TAU == 1.029
    assert deployed["false_kill_rate"] == pytest.approx(0.0, abs=1e-9)
    assert deployed["kill_rate"] == pytest.approx(1.0, abs=1e-9)

    good_max = artifact["calibration"]["good_summary"]["windowed_growth"]["max"]
    bad_min = artifact["calibration"]["bad_summary"]["windowed_growth"]["min"]
    threshold = windowed["threshold"]
    assert good_max <= threshold <= bad_min
    assert windowed["false_kill_rate"] <= 0.05
    assert windowed["kill_rate"] >= 0.95


def test_package_reproduces_artifact_semantics_on_ginibre() -> None:
    """Fresh package-side harvest: stable gains read ≈1.0, explosive > τ."""
    stable, state = ginibre_run(0.9, 0)
    guard = stability.StabilityGuard(statistic="windowed_growth", window=10)
    stat = guard.probe(stable, state, None)  # type: ignore[arg-type]
    assert stat <= stability.DEFAULT_TAU

    explosive, state = ginibre_run(1.4, 0)
    assert guard.probe(explosive, state, None) > stability.DEFAULT_TAU  # type: ignore[arg-type]


def test_ginibre_harvest_roc_acceptance() -> None:
    record = calibrate_ginibre_harvest(
        dim=16, batch=2, good_gains=(0.5, 0.7), bad_gains=(1.2, 1.4), seeds_per_gain=2
    )
    report = record.calibration["windowed_growth"]
    assert report is not None
    assert record.deployed_tau["windowed_growth"][0] <= 0.05
    assert record.deployed_tau["windowed_growth"][1] >= 0.95


def test_guard_state_duck_typing() -> None:
    """computronium CompositeState instances drive the package guard."""
    from computronium.state import CompositeState as CoreState

    def transition(z: CoreState, _context: object | None) -> CoreState:
        x = z.activity["x"]
        return CoreState(
            activity={"x": 2.0 * x if isinstance(x, torch.Tensor) else x},
            plastic=z.plastic,
            substrate=z.substrate,
        )

    z = CoreState(activity={"x": torch.ones(2, 4)}, plastic={}, substrate={})
    guard = stability.StabilityGuard(statistic="windowed_growth", window=5)
    assert guard.probe(transition, z, None) > 1.5  # type: ignore[arg-type]
