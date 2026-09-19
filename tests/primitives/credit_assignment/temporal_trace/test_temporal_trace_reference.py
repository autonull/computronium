"""Tests for Temporal Trace Credit reference implementation."""

import torch

from computronium.primitives.credit_assignment.temporal_trace import (
    make_case,
    reference_step,
)


def test_reference_step_deterministic():
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    output1 = reference_step(case1)
    output2 = reference_step(case2)

    assert len(output1) == len(output2)
    for o1, o2 in zip(output1, output2, strict=True):
        assert o1.allclose(o2)


def test_reference_step_different_seeds():
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    output1 = reference_step(case1)
    output2 = reference_step(case2)

    assert len(output1) == len(output2)
    # At least one output should differ
    assert not all(o1.allclose(o2) for o1, o2 in zip(output1, output2, strict=True))


def test_reference_step_returns_list():
    case = make_case(seed=0)
    output = reference_step(case)

    assert isinstance(output, list)
    assert len(output) > 0
    for o in output:
        assert isinstance(o, torch.Tensor)
