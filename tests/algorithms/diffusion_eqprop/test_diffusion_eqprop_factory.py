"""Factory tests for DiffusionEqprop algorithm."""

import torch

from computronium.algorithms.diffusion_eqprop import create_diffusion_eqprop_mlp


def test_create_diffusion_eqprop_mlp_creates_system():
    """Test that factory creates a working system."""
    system = create_diffusion_eqprop_mlp(
        input_dim=4,
        hidden_dims=(8,),
        output_dim=4,
        lr=1e-3,
        device="cpu",
    )

    assert system is not None
    assert hasattr(system, "train_step")
    assert hasattr(system, "forward")


def test_create_diffusion_eqprop_mlp_train_step():
    """Test that factory system can run train_step."""
    system = create_diffusion_eqprop_mlp(
        input_dim=4,
        hidden_dims=(8,),
        output_dim=4,
        lr=1e-3,
        device="cpu",
    )

    x = torch.randn(2, 4)
    y = torch.randint(0, 4, (2,))

    result = system.train_step(x, y)

    assert result is not None
    assert isinstance(result, dict)
    assert "loss" in result


def test_create_diffusion_eqprop_mlp_backend_selection():
    """Test that backend parameter is accepted."""
    # Test reference backend
    system_ref = create_diffusion_eqprop_mlp(
        input_dim=4,
        hidden_dims=(8,),
        output_dim=4,
        lr=1e-3,
        device="cpu",
        backend="reference",
    )
    assert system_ref is not None

    # Test auto backend
    system_auto = create_diffusion_eqprop_mlp(
        input_dim=4,
        hidden_dims=(8,),
        output_dim=4,
        lr=1e-3,
        device="cpu",
        backend="auto",
    )
    assert system_auto is not None
