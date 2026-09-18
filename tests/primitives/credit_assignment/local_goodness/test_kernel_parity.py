"""Tests for local_goodness kernel parity."""


from computronium.acceleration.parity import assert_parity
from computronium.primitives.credit_assignment.local_goodness import (
    SPEC,
    kernel_step,
    make_case,
    reference_step,
)


def test_kernel_parity() -> None:
    case = make_case(seed=42)

    reference_output = reference_step(case)
    kernel_output = kernel_step(case)

    assert_parity(reference_output, kernel_output, SPEC.parity)


def test_kernel_parity_different_seeds() -> None:
    for seed in [42, 43, 44]:
        case = make_case(seed=seed)

        reference_output = reference_step(case)
        kernel_output = kernel_step(case)

        assert_parity(reference_output, kernel_output, SPEC.parity)


def test_kernel_parity_lemma_mode() -> None:
    case = make_case(seed=42, local_objective="lemma")

    reference_output = reference_step(case)
    kernel_output = kernel_step(case)

    assert_parity(reference_output, kernel_output, SPEC.parity)
