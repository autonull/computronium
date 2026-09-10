"""Property tests for the C × U mechanistic study (TODO18 5.1).

Level 4 sampled-numerical checks: sign convention, norm-matching
calibration, record round-trip, and trajectory-arm invariants. The
hypotheses themselves are measured, not asserted — the study is the
instrument.
"""

from __future__ import annotations

import math

import pytest

from computronium.analysis.mechanistic_study import (
    _credit_configs,
    _reference_norm,
    _update_configs,
    run_mechanistic_study,
)

_SEEDS = (0, 1)
_N_TRAJ_STEPS = 6


@pytest.fixture(scope="module")
def study_record():
    return run_mechanistic_study(seeds=_SEEDS, n_traj_steps=_N_TRAJ_STEPS)


def test_all_grid_cells_present(study_record):
    expected = {f"{c}x{u}" for c in _credit_configs() for u in _update_configs()}
    assert set(study_record.cells) == expected


def test_one_step_strict_sign_convention(study_record):
    """ΔL < 0 means descent; improvement_per_norm = mean(−ΔL_i/‖Δθ‖_i).

    The aggregate ratio-of-means identity does NOT hold (per-seed ratios
    aggregate as a mean of ratios), so only per-metric finiteness, sign
    sanity, and positive displacement are asserted here.
    """
    for cell, exps in study_record.cells.items():
        o = exps["one_step_reset"].metrics
        dd, dl, dn = (
            o["displacement_norm"]["mean"],
            o["loss_delta"]["mean"],
            o["improvement_per_norm"]["mean"],
        )
        assert dd > 0.0, cell
        assert math.isfinite(dl) and math.isfinite(dn), cell
        assert (dn > 0.0) == (dl < 0.0) or abs(dl) < 1e-6, cell


def test_norm_matching_calibrated_to_credit_reference(study_record):
    """Non-euclidean cells match their credit's euclidean ‖Δθ‖ within 15%."""
    for credit in _credit_configs():
        ref = _reference_norm(_credit_configs()[credit](), 0.05, *_ref_batch())
        for update in _update_configs():
            if update == "euclidean":
                continue
            cell = study_record.cells[f"{credit}x{update}"]
            got = cell["one_step_reset"].metrics["displacement_norm"]["mean"]
            assert got == pytest.approx(ref, rel=0.15), (credit, update, got, ref)


def test_determinism(study_record):
    """Same seeds → identical metrics and seeds (walltime/commit excluded)."""

    def strip(raw: str) -> str:
        import json as _json

        d = _json.loads(raw)
        d.pop("walltime_s", None)
        d.pop("commit_hash", None)
        for exps in d["cells"].values():
            for name, rec_raw in exps.items():
                rec = _json.loads(rec_raw)
                rec.pop("walltime_s", None)
                rec.pop("commit_hash", None)
                exps[name] = rec
        return _json.dumps(d, sort_keys=True)

    again = run_mechanistic_study(seeds=_SEEDS, n_traj_steps=_N_TRAJ_STEPS)
    assert strip(study_record.to_json()) == strip(again.to_json())


def test_record_round_trip(study_record):
    from computronium.analysis.mechanistic_study import MechanisticStudyRecord

    rev = MechanisticStudyRecord.from_json(study_record.to_json())
    assert rev.cells.keys() == study_record.cells.keys()
    for cell, exps in rev.cells.items():
        for exp, rec in exps.items():
            assert rec.config_digest() == (
                study_record.cells[cell][exp].config_digest()
            )


def test_trajectory_arm_invariants(study_record):
    """Best loss never exceeds the initial loss (descent visits exist)."""
    for cell, exps in study_record.cells.items():
        t = exps["trajectory"].metrics
        assert t["loss_best"]["mean"] <= t["loss_initial"]["mean"] + 1e-6, cell
        assert t["tuning_budget_params_steps"]["mean"] > 0.0, cell


def _ref_batch():
    import torch

    torch.manual_seed(0)
    return torch.randn(16, 16), torch.randint(0, 4, (16,))
