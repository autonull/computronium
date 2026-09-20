"""Reference implementation tests for Spatial Lattice 3D Geometry primitive."""

import torch

from computronium.primitives.geometry.spatial_lattice_3d import (
    make_case,
    reference_forward,
)


def test_reference_forward_returns_tensor():
    """Test that reference_forward returns a tensor."""
    case = make_case(device="cpu", seed=0)
    output = reference_forward(case)

    assert isinstance(output, torch.Tensor)
    assert output.shape == (2, 8)  # batch=2, output_dim=8


def test_reference_forward_deterministic():
    """Test that reference_forward is deterministic with fixed seed."""
    case1 = make_case(device="cpu", seed=42)
    case2 = make_case(device="cpu", seed=42)

    output1 = reference_forward(case1)
    output2 = reference_forward(case2)

    assert torch.allclose(output1, output2)


def test_reference_forward_different_seeds():
    """Test that reference_forward produces different outputs with different seeds."""
    case1 = make_case(device="cpu", seed=1)
    case2 = make_case(device="cpu", seed=2)

    output1 = reference_forward(case1)
    output2 = reference_forward(case2)

    # With different seeds, geometry weights differ, so outputs should differ
    assert not torch.allclose(output1, output2)