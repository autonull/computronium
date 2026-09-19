"""Tests for Target Propagation algorithm factory."""

from computronium.algorithms.tp import create_tp_mlp


def test_factory_creates_system():
    system = create_tp_mlp(
        input_dim=4,
        hidden_dims=(4,),
        output_dim=4,
        lr=1e-3,
        device="cpu",
        backend="reference",
    )

    assert system is not None
    assert hasattr(system, "train_step")


def test_factory_backend_auto():
    system = create_tp_mlp(
        input_dim=4,
        hidden_dims=(4,),
        output_dim=4,
        lr=1e-3,
        device="cpu",
        backend="auto",
    )

    assert system is not None
