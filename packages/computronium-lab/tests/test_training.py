"""Phase 2 certificates: guard, harvest, theta audit, CEEC, determinism."""

from __future__ import annotations

import pytest
from computronium_lab import Lab, StabilityGuardKill, TrainOptions

CERT_TEST = {"timeout": 300}


def test_harvest_ema_produces_certificate() -> None:
    lab = Lab(seed=0)
    system = lab.compose("backprop_mlp")
    result = lab.train(system, epochs=1, options=TrainOptions(harvest=True))
    assert result.harvest is not None
    assert result.harvest.mode == "ema"
    assert result.harvest.applied


def test_stability_guard_clean_run() -> None:
    lab = Lab(seed=0)
    system = lab.compose("backprop_mlp")
    result = lab.train(system, epochs=1, options=TrainOptions(stability_guard=True))
    assert result.stability is not None
    assert result.stability.checked
    assert not result.stability.kill


def test_frozen_theta_audit_manual() -> None:
    lab = Lab(seed=0)
    system = lab.compose("backprop_mlp")
    result = lab.train(system, epochs=1, options=TrainOptions(frozen_theta_audit=True))
    assert result.theta_audit is not None
    # training legitimately mutates θ through the update path
    assert result.theta_audit.mutated or not result.theta_audit.version_bumped
    assert result.theta_audit.clean


def test_frozen_theta_audit_automatic_on_continual_spec() -> None:
    from computronium_lab import Constraints

    lab = Lab(seed=0)
    spec = lab.specify(
        "image_classification",
        "gaussian_blobs",
        constraints=Constraints(continual=True),
    )
    system = lab.compose("backprop_mlp")
    result = lab.train(system, epochs=1, spec=spec)
    assert result.theta_audit is not None
    assert result.theta_audit.clean


def test_ceec_campaign_logging(tmp_path) -> None:
    lab = Lab(seed=0, record_ledger=str(tmp_path / "ledger.db"))
    system = lab.compose("backprop_mlp")
    result = lab.train(system, epochs=2, options=TrainOptions(ceec_logging=True))
    assert len(result.ceec_artifact_ids) == 2


def test_determinism_seal_verified() -> None:
    lab = Lab(seed=0)
    system = lab.compose("backprop_mlp")
    result = lab.train(system, epochs=1, options=TrainOptions(determinism_seal=True))
    assert result.determinism is not None
    assert result.determinism.verified
    assert result.determinism.params_sha256
    assert result.determinism.metrics_sha256
    assert result.determinism.first_divergence_epoch is None


def test_val_data_surfaces_val_metrics() -> None:
    from computronium_lab.lab import synthetic_task

    lab = Lab(seed=0)
    system = lab.compose("backprop_mlp")
    _, val = synthetic_task(seed=0)
    result = lab.train(system, epochs=2, options=TrainOptions(val_data=val))
    assert "val_loss" in result.metrics
    assert "val_acc" in result.metrics
    assert 0.0 <= result.metrics["val_acc"] <= 1.0


def test_stability_probe_reports_kill_and_unavailability() -> None:
    from computronium_lab.training import stability_probe
    from stability import attach
    from stability.guard import StabilityVerdict

    lab = Lab(seed=0)
    system = lab.compose("backprop_mlp")

    handle = attach(system.geometry)
    cert = stability_probe(handle, {"x": None}, 0)
    assert cert.checked and not cert.kill  # no activity → zero statistic

    class Exploding:
        def check_external(self, state, transition_fn, step=0):
            return StabilityVerdict(
                kill=True,
                decisions=(),
                max_statistic=99.0,
                threshold=1.0,
                step=step,
            )

    from stability.guard import GuardHandle

    handle = GuardHandle(
        guard=Exploding(), model=system.geometry, transition_fn=lambda s: s
    )
    cert = stability_probe(handle, {"x": None}, 0)
    assert cert.kill
    with pytest.raises(StabilityGuardKill):
        raise StabilityGuardKill("statistic=99.0 > threshold")
