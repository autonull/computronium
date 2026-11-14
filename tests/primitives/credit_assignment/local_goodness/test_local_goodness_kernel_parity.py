"""Tests for local_goodness kernel parity."""

from computronium.acceleration.parity import assert_parity
from computronium.primitives.credit_assignment.local_goodness import (
    SPEC,
    kernel_step,
    make_case,
    reference_step,
)


def test_kernel_parity() -> None:
    # FF consumes the case's autograd graph; each rung gets its own case.
    reference_output = reference_step(make_case(seed=42))
    kernel_output = kernel_step(make_case(seed=42))

    assert_parity(reference_output, kernel_output, SPEC.parity)


def test_kernel_parity_different_seeds() -> None:
    for seed in [42, 43, 44]:
        reference_output = reference_step(make_case(seed=seed))
        kernel_output = kernel_step(make_case(seed=seed))

        assert_parity(reference_output, kernel_output, SPEC.parity)


def test_kernel_parity_lemma_mode() -> None:
    reference_output = reference_step(make_case(seed=42, local_objective="lemma"))
    kernel_output = kernel_step(make_case(seed=42, local_objective="lemma"))

    assert_parity(reference_output, kernel_output, SPEC.parity)
