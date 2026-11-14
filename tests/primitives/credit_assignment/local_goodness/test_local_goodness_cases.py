"""Tests for local_goodness cases."""

import torch

from computronium.primitives.credit_assignment.local_goodness import make_case


def test_make_case_deterministic() -> None:
    case1 = make_case(seed=42)
    case2 = make_case(seed=42)

    for w1, w2 in zip(case1.weights, case2.weights, strict=True):
        assert torch.allclose(w1, w2)

    for a1, a2 in zip(case1.free_activations, case2.free_activations, strict=True):
        assert torch.allclose(a1, a2)

    for a1, a2 in zip(case1.nudged_activations, case2.nudged_activations, strict=True):
        assert torch.allclose(a1, a2)

    EXCLUDE_KEYS = {"seed", "target"}

    config1 = {k: v for k, v in case1.config.items() if k not in EXCLUDE_KEYS}
    config2 = {k: v for k, v in case2.config.items() if k not in EXCLUDE_KEYS}
    assert config1 == config2


def test_make_case_different_seeds() -> None:
    case1 = make_case(seed=42)
    case2 = make_case(seed=43)

    # At least one weight should differ
    assert not all(
        torch.allclose(w1, w2)
        for w1, w2 in zip(case1.weights, case2.weights, strict=True)
    )
