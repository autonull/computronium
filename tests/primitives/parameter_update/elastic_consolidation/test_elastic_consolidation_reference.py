"""Tests for Elastic Consolidation Update reference implementation."""

import torch

from computronium.primitives.parameter_update.elastic_consolidation import (
    make_case,
    reference_step,
)


def test_reference_step_deterministic():
    """Reference step should be deterministic with fixed seed."""
    case = make_case(seed=42)
    out1 = reference_step(case)
    out2 = reference_step(case)

    assert set(out1.keys()) == set(out2.keys())
    for k in out1:
        assert torch.allclose(out1[k], out2[k])


def test_reference_step_different_seeds():
    """Reference step should produce different outputs with different seeds."""
    case1 = make_case(seed=0)
    case2 = make_case(seed=1)
    out1 = reference_step(case1)
    out2 = reference_step(case2)

    # At least one parameter should differ
    assert any(not torch.allclose(out1[k], out2[k]) for k in out1)


def test_reference_step_returns_expected_type():
    """Reference step should return dict of tensors."""
    case = make_case()
    out = reference_step(case)

    assert isinstance(out, dict)
    assert all(isinstance(v, torch.Tensor) for v in out.values())
    # 2 Linear layers with bias = 4 parameters (2 weights + 2 biases)
    assert len(out) == 4
