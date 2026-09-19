"""Tests for Thermodynamic Contrast reference implementation."""

import pytest
import torch

from computronium.primitives.credit_assignment.thermodynamic_contrast import (
    make_case,
    reference_step,
)


def test_reference_step_deterministic():
    """Reference step should be deterministic with fixed seed."""
    case = make_case(seed=42)
    out1 = reference_step(case)
    out2 = reference_step(case)

    assert len(out1) == len(out2)
    for g1, g2 in zip(out1, out2):
        assert torch.allclose(g1, g2)


def test_reference_step_different_seeds():
    """Reference step should produce different outputs with different seeds."""
    case1 = make_case(seed=0)
    case2 = make_case(seed=1)
    out1 = reference_step(case1)
    out2 = reference_step(case2)

    # At least one gradient should differ
    assert any(not torch.allclose(g1, g2) for g1, g2 in zip(out1, out2))


def test_reference_step_returns_expected_type():
    """Reference step should return list of tensors."""
    case = make_case()
    out = reference_step(case)

    assert isinstance(out, list)
    assert all(isinstance(g, torch.Tensor) for g in out)
    assert len(out) == 2  # 2 weight layers