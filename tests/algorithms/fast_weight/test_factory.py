"""Factory tests for Fast-Weight algorithm."""

import torch

from computronium.algorithms.fast_weight import create_fast_weight_mlp


def test_create_fast_weight_mlp():
    """Test that create_fast_weight_mlp returns a system."""
    system = create_fast_weight_mlp(
        input_dim=4,
        hidden_dims=(8,),
        output_dim=4,
        lr=1e-3,
        device="cpu",
        backend="reference",
    )

    assert system is not None
    assert hasattr(system, "train_step")


def test_create_fast_weight_mlp_different_backends():
    """Test that create_fast_weight_mlp works with different backends."""
    for backend in ["reference", "auto"]:
        system = create_fast_weight_mlp(
            input_dim=4,
            hidden_dims=(8,),
            output_dim=4,
            lr=1e-3,
            device="cpu",
            backend=backend,
        )
        assert system is not None
        assert hasattr(system, "train_step")


def test_create_fast_weight_mlp_train_step():
    """Test that the created system can run a train step."""
    system = create_fast_weight_mlp(
        input_dim=4,
        hidden_dims=(8,),
        output_dim=4,
        lr=1e-3,
        device="cpu",
        backend="reference",
    )

    x = torch.randn(2, 4)
    y = torch.randint(0, 4, (2,))
    metrics = system.train_step(x, y)

    assert isinstance(metrics, dict)
    assert "loss" in metrics
