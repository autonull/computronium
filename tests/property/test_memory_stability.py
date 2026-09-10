"""Property tests for the Stability × Memory campaign (TODO18 5.2).

The hypothesis — "useful adaptation needs selective preservation of
state, not global instability" — is *measured* by the campaign; these
tests pin the instrument's invariants and the first-record direction.
"""

from __future__ import annotations

import pytest

from computronium.analysis.memory_stability import (
    retention_contraction_scatter,
    run_memory_trial,
    run_stability_memory_campaign,
)

_REDUCED = {
    "contractions": (0.5, 1.05),
    "noises": (0.0, 0.1),
    "delays": (1, 8),
}


@pytest.fixture(scope="module")
def campaign_record():
    return run_stability_memory_campaign(seeds=(0, 1), n_trials=4, **_REDUCED)


def test_selective_retention_invariant_to_delay():
    """Gated memory is frozen post-write: retention independent of delay."""
    kw = {
        "seed": 0,
        "contraction": 0.9,
        "precision": "float32",
        "noise_level": 0.0,
        "readout_constraint": "full",
        "gate_mode": "selective",
        "coupling": "open",
    }
    r1 = run_memory_trial(**kw, delay=1)["retention"]
    r8 = run_memory_trial(**kw, delay=8)["retention"]
    assert r1 == pytest.approx(r8, abs=0.02)
    assert r1 > 0.95


def test_ungated_retention_decays_with_distractors():
    kw = {
        "seed": 0,
        "contraction": 0.9,
        "precision": "float32",
        "noise_level": 0.0,
        "readout_constraint": "full",
        "gate_mode": "ungated",
        "coupling": "open",
    }
    assert run_memory_trial(**kw, delay=8)["retention"] < 0.2
    assert run_memory_trial(**kw, delay=1)["retention"] < 0.6


def test_coupled_selective_retention_survives_noise_and_delay():
    """Coupling routes noise into the state arm but gated memory holds."""
    kw = {
        "seed": 0,
        "contraction": 0.9,
        "precision": "float32",
        "noise_level": 0.1,
        "readout_constraint": "full",
        "gate_mode": "selective",
        "coupling": "coupled",
    }
    r32 = run_memory_trial(**kw, delay=32)["retention"]
    assert r32 > 0.9


def test_hypothesis_direction(campaign_record):
    """Selective beats ungated on retention at every swept cell."""
    for cell, exps in campaign_record.cells.items():
        if "/delay8" not in cell:
            continue
        gate = cell.split("/")[0]
        retention = exps["retention"].metrics["retention"]["mean"]
        if gate == "selective":
            assert retention > 0.9, cell
        else:
            assert retention < 0.6, cell


def test_grid_shape_and_record_round_trip(campaign_record):
    from computronium.analysis.mechanistic_study import MechanisticStudyRecord

    gates, couplings, precisions, readouts = 2, 2, 3, 3
    expected = gates * couplings * precisions * readouts * 2 * 2 * 2
    assert len(campaign_record.cells) == expected

    revived = MechanisticStudyRecord.from_json(campaign_record.to_json())
    assert revived.cells.keys() == campaign_record.cells.keys()


def test_measured_contraction_tracks_nominal():
    """Perturbation decay recovers the nominal spectral radius scale."""
    kw = {
        "seed": 0,
        "precision": "float32",
        "noise_level": 0.0,
        "readout_constraint": "full",
        "gate_mode": "selective",
        "coupling": "open",
        "delay": 8,
    }
    lo = run_memory_trial(**kw, contraction=0.5)["measured_contraction"]
    mid = run_memory_trial(**kw, contraction=0.9)["measured_contraction"]
    hi = run_memory_trial(**kw, contraction=1.05)["measured_contraction"]
    # Values sit below nominal: the tanh Jacobian (1 − x²) shrinks the
    # linearized gain along the trajectory — monotone tracking is the claim.
    assert lo < mid < hi
    assert hi > 0.8


def test_scatter_points_match_cells_and_axes(campaign_record):
    points = retention_contraction_scatter(campaign_record)
    assert len(points) == len(campaign_record.cells)
    by_gate = {p["gate_mode"] for p in points}
    assert by_gate == {"selective", "ungated"}
    assert {p["coupling"] for p in points} == {"open", "coupled"}
    for p in points:
        assert 0.0 <= float(p["retention"]) <= 1.0
        assert float(p["measured_contraction"]) > 0.0


def test_coupling_reaches_state_arm():
    """Coupling must route episode noise into the state block.

    With a paired zero-noise replay per episode, the noisy-vs-quiet
    final-state divergence is strictly larger when memory feeds back
    into the state block (the noisy memory term is an extra noise path
    into x, absent in open mode).
    """
    base = {
        "seed": 0,
        "contraction": 0.9,
        "precision": "float32",
        "readout_constraint": "full",
        "gate_mode": "ungated",
        "noise_level": 0.5,
        "delay": 8,
    }
    div_open = run_memory_trial(**base, coupling="open")["state_noise_divergence"]
    div_coupled = run_memory_trial(**base, coupling="coupled")["state_noise_divergence"]
    assert div_open > 0.0
    assert div_coupled > div_open
