"""Factory tests for FF algorithm."""

import torch

from computronium.algorithms.ff import create_ff_mlp


def test_create_ff_mlp():
    """Test that create_ff_mlp returns a system."""
    system = create_ff_mlp(
        input_dim=4,
        hidden_dims=(8,),
        output_dim=4,
        layer_lr=0.03,
        classifier_lr=0.01,
        threshold=2.0,
        device="cpu",
        backend="reference",
    )

    assert system is not None
    assert hasattr(system, "train_step")


def test_create_ff_mlp_different_backends():
    """Test that create_ff_mlp works with different backends."""
    for backend in ["reference", "auto"]:
        system = create_ff_mlp(
            input_dim=4,
            hidden_dims=(8,),
            output_dim=4,
            layer_lr=0.03,
            classifier_lr=0.01,
            threshold=2.0,
            device="cpu",
            backend=backend,
        )
        assert system is not None
        assert hasattr(system, "train_step")


def test_create_ff_mlp_train_step():
    """Test that the created system can run a train step."""
    system = create_ff_mlp(
        input_dim=4,
        hidden_dims=(8,),
        output_dim=4,
        layer_lr=0.03,
        classifier_lr=0.01,
        threshold=2.0,
        device="cpu",
        backend="reference",
    )

    x = torch.randn(2, 4)
    y = torch.randint(0, 4, (2,))
    metrics = system.train_step(x, y)

    assert isinstance(metrics, dict)
    assert "loss" in metrics
