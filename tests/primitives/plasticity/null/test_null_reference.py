"""Tests for Null Plasticity reference implementation."""

import pytest
import torch

from computronium.primitives.plasticity.null import (
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


def test_reference_step_returns_unchanged_psi():
    """Null plasticity should return plastic state unchanged."""
    case = make_case()
    out = reference_step(case)

    assert isinstance(out, dict)
    assert out == case.psi  # Should be empty dict


def test_reference_step_returns_expected_type():
    """Reference step should return dict of tensors."""
    case = make_case()
    out = reference_step(case)

    assert isinstance(out, dict)
    # Null plasticity has no plastic state
    assert len(out) == 0
