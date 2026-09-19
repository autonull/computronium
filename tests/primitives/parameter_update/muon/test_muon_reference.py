"""Tests for Muon reference implementation."""

import torch

from computronium.primitives.parameter_update.muon import (
    make_case,
    reference_step,
)


def test_reference_step_deterministic():
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    output1 = reference_step(case1)
    output2 = reference_step(case2)

    assert set(output1.keys()) == set(output2.keys())
    for k in output1:
        assert output1[k].allclose(output2[k])


def test_reference_step_different_seeds():
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    output1 = reference_step(case1)
    output2 = reference_step(case2)

    assert set(output1.keys()) == set(output2.keys())
    # At least one output should differ
    assert not all(output1[k].allclose(output2[k]) for k in output1)


def test_reference_step_returns_dict():
    case = make_case(seed=0)
    output = reference_step(case)

    assert isinstance(output, dict)
    assert len(output) > 0
    for k, v in output.items():
        assert isinstance(k, str)
        assert isinstance(v, torch.Tensor)
