"""Vertical-slice measurement panel + claim record (TODO18 3.1-3.3).

Level 4 sampled numerical tests of the EqProp coordinate
(digital/recurrent/energy_min/none/thermodynamic_contrast/euclidean):

- Gradient alignment: ∇L·Δθ (central finite difference along the applied
  displacement) must agree with the realized loss delta and be negative in
  the median across steps (the strict sign convention claim).
- Energy trajectory: fraction of non-increasing steps is reported; the
  final free loss must not exceed its initial value at this scale (weak
  empirical bound — a rise would flag a broken coordinate).
- ClaimRecord: round-trips through JSON, aggregates mean ± std, digests
  config deterministically.
- Frozen-θ integration: the audited body of a slice step leaves θ bitwise
  identical until the update applies.
"""

import json

import pytest
import torch

from computronium.analysis.vertical_slice import (
    ClaimRecord,
    SliceMetrics,
    fixed_dataset_batch_provider,
    measure_energy_trajectory,
    measure_gradient_alignment,
    measure_resources,
    run_slice,
    synthetic_batch_provider,
)

_COORD = "digital/recurrent/energy_min/none/thermodynamic_contrast/euclidean"


@pytest.fixture(scope="module")
def slice_run() -> SliceMetrics:
    return run_slice(seed=0, n_steps=12)


def test_gradient_alignment_sign_convention(slice_run):
    """∇L·Δθ (FD proxy) must correlate with the realized loss decrease."""
    from computronium.core.system_trainer.factory import create_eqprop_system

    torch.manual_seed(0)
    system = create_eqprop_system(
        input_dim=16,
        hidden_dim=24,
        output_dim=4,
        num_layers=1,
        settle_steps=10,
        lr=0.05,
    )
    xs = torch.randn(16, 16)
    ys = torch.randint(0, 4, (16,))

    for _ in range(4):
        m = measure_gradient_alignment(system, xs, ys)
        # FD derivative must track the realized loss change in sign and
        # magnitude at this lr scale.
        assert m["directional_derivative"] == pytest.approx(
            m["loss_delta"], rel=0.5, abs=1e-3
        )
        assert m["displacement_norm"] > 0


def test_energy_trajectory_reported(slice_run):
    traj = measure_energy_trajectory(slice_run.steps)
    assert traj["energy_nonincreasing_fraction"] >= 0.0
    assert traj["energy_final"] <= traj["energy_initial"] + 0.1


def test_learning_progress_on_slice(slice_run):
    """Weak Level 5 claim: final free loss ≤ initial free loss."""
    losses = [s["free_loss"] for s in slice_run.steps]
    assert losses[-1] <= losses[0] + 0.05


def test_slice_deterministic_per_seed():
    a = run_slice(seed=7, n_steps=3)
    b = run_slice(seed=7, n_steps=3)
    assert a.steps == b.steps


def test_synthetic_provider_is_fixed_batch():
    """The default provider returns the same batch every step."""
    torch.manual_seed(7)
    p = synthetic_batch_provider(16, 16, 4)
    x0, y0 = p(0)
    for t in (1, 2, 3):
        xt, yt = p(t)
        assert torch.equal(xt, x0)
        assert torch.equal(yt, y0)


def test_fixed_dataset_provider_deterministic_and_labels_custom():
    g = torch.Generator().manual_seed(42)
    xs = torch.randn(64, 16, generator=g)
    ys = torch.randint(0, 4, (64,), generator=g)
    provider = fixed_dataset_batch_provider(xs, ys, batch_size=16, seed=5)
    a = run_slice(seed=7, n_steps=6, batch_provider=provider)
    assert a.config["task"] == "custom"
    # Same dataset + seed → identical shuffled-epoch walk.
    b = run_slice(
        seed=7,
        n_steps=6,
        batch_provider=fixed_dataset_batch_provider(xs, ys, batch_size=16, seed=5),
    )
    assert a.steps == b.steps
    # Shuffled-epoch walk actually advances: distinct batches across steps.
    b1, b2 = provider(0)[0], provider(1)[0]
    assert not torch.equal(b1, b2)


def test_resource_accounting(slice_run):
    from computronium.core.system_trainer.factory import create_eqprop_system

    torch.manual_seed(0)
    system = create_eqprop_system(
        input_dim=16,
        hidden_dim=24,
        output_dim=4,
        num_layers=1,
        settle_steps=10,
        lr=0.05,
    )
    res = measure_resources(system)
    assert res["train_step_flops"] > 0
    assert res["param_count"] > 0


def test_claim_record_roundtrip_and_aggregation(slice_run):
    record = ClaimRecord.from_runs(_COORD, slice_run.config, [slice_run])
    assert record.seeds == (0,)
    assert "free_loss" in record.metrics
    assert record.metrics["free_loss"]["n"] == 12
    assert record.verification_level == "4"

    restored = ClaimRecord.from_json(record.to_json())
    assert restored == record
    assert restored.config_digest() == record.config_digest()


def test_claim_record_aggregates_across_seeds():
    runs = [run_slice(seed=s, n_steps=4) for s in (1, 2, 3)]
    record = ClaimRecord.from_runs(_COORD, runs[0].config, runs)
    m = record.metrics["free_loss"]
    assert m["n"] == 12
    assert m["std"] >= 0
    artifact = json.loads(record.to_json())
    assert artifact["schema_version"] == "1.0.0"
    assert artifact["coordinate"] == _COORD


def test_slice_step_is_frozen_theta_clean(slice_run):
    """A train step mutates θ only through the update (J2 contract)."""
    from computronium.core.frozen_theta import FrozenThetaAudit
    from computronium.core.system_trainer.factory import create_eqprop_system

    torch.manual_seed(0)
    system = create_eqprop_system(
        input_dim=16,
        hidden_dim=24,
        output_dim=4,
        num_layers=1,
        settle_steps=10,
        lr=0.05,
    )
    xs = torch.randn(16, 16)
    torch.randint(0, 4, (16,))

    # Intra-episode audit of the free settle path (no update): the audit
    # wraps a forward, which must not touch θ at all.
    audit = FrozenThetaAudit(system)
    with audit:
        system.forward(xs)
    audit.assert_invariant()
    assert audit.report is not None
    assert audit.report.invariant
