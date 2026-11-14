"""Tests for Rule State Plasticity reference implementation."""

import torch

from computronium.primitives.plasticity.rule_state import (
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


def test_reference_step_updates_psi():
    """Rule state plasticity should update plastic state."""
    case = make_case()
    out = reference_step(case)

    assert isinstance(out, dict)
    assert "operator_logits" in out
    assert "controller_state" in out
    assert out["operator_logits"].shape == case.psi["operator_logits"].shape
    assert out["controller_state"].shape == case.psi["controller_state"].shape


def test_reference_step_different_seeds():
    """Reference step should produce different outputs with different seeds."""
    case1 = make_case(seed=0)
    case2 = make_case(seed=1)
    out1 = reference_step(case1)
    out2 = reference_step(case2)

    # At least one tensor should differ
    assert not torch.allclose(out1["operator_logits"], out2["operator_logits"])
