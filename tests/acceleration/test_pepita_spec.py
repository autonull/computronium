"""The PEPITA error-modulation specification (TODO36 §4.5).

``_pepita_error_modulation_kernel`` was the one triton kernel in the tree whose
intent existed in three places that did not agree: its docstring said
``scale * error.T @ feedback``, the torch twin
``contrastive_primitives.pepita_error_modulation`` said
``scale * (error.T @ feedback_matrix)``, and neither expression is even
type-correct for the shapes both of them declare (``error`` is ``[B, D_out]``,
``feedback`` is ``[D_in, D_out]``, and the declared output is ``[D_out, D_in]``).
The kernel's own arithmetic was the only surviving record, and it is what the
specification below is written from.

The specification, in full:

    dW[o, i] = scale * (sum_b error[b, o]) * feedback[i, o]
             = scale * error.sum(dim=0)[:, None] * feedback.T

Three facts make this the reading rather than a preference:

1. It is the **only** one of the three under which all three declarations hold at
   once. The batch and the output unit cannot both index the error, so the batch
   is reduced per output unit *before* the product, and what remains is rank 1.
2. The kernel's ``for b`` loop accumulated ``err[b, o] * feedback[i, o]`` — this
   expression, exactly, in the wrong order to see it.
3. The batch is **summed**, not averaged. That is the defect the specification
   found: the kernel divided by ``B``, and the division is invisible in shape and
   in sign. :func:`test_there_is_no_batch_mean` states it as a property.

The kernel therefore needs no ``tl.dot``: the feedback is transposed and each row
scaled, which is a broadcast, not a contraction. The version that did have one
used a contraction of length 1, which is why the kernel did not compile for its
whole life.
"""

from __future__ import annotations

import pytest
import torch

B, D_IN, D_OUT, BLOCK = 8, 48, 32, 16
SCALE = 0.5


def error_modulation_ref(
    error: torch.Tensor, feedback: torch.Tensor, scale: float
) -> torch.Tensor:
    """The expression the kernel is meant to equal, derived from the maths.

    Output unit ``o`` gates the feedback column it belongs to, so the error is
    summed over the batch per output unit and the result is a rank-1 outer
    product in the weight's own ``[D_out, D_in]`` orientation.

    Args:
        error: ``[B, D_out]`` per-sample error signal.
        feedback: ``[D_in, D_out]`` the fixed feedback weights.
        scale: modulation scale.

    Returns:
        ``[D_out, D_in]`` weight delta.
    """
    return scale * error.sum(dim=0)[:, None] * feedback.T


def _loop_reference(
    error: torch.Tensor, feedback: torch.Tensor, scale: float
) -> torch.Tensor:
    """The same expression, one output unit at a time, as the reference's anchor."""
    delta = torch.zeros(D_OUT, D_IN, dtype=torch.float64)
    for o in range(D_OUT):
        for b in range(error.shape[0]):
            delta[o] += error[b, o].double() * feedback[:, o].double()
    return (scale * delta).float()


@pytest.fixture
def pepita_inputs() -> tuple[torch.Tensor, torch.Tensor]:
    generator = torch.Generator().manual_seed(13)
    return (
        torch.randn(B, D_OUT, generator=generator),
        torch.randn(D_IN, D_OUT, generator=generator),
    )


def test_the_reference_matches_an_explicit_loop(pepita_inputs) -> None:
    """The specification is anchored to a loop, not to the kernel."""
    error, feedback = pepita_inputs
    assert torch.allclose(
        error_modulation_ref(error, feedback, SCALE),
        _loop_reference(error, feedback, SCALE),
        atol=1e-4,
    )


def test_the_reference_is_the_torch_twin(pepita_inputs) -> None:
    """The rung exists to replace this function; the two must not diverge."""
    from computronium.acceleration.contrastive_primitives import pepita_error_modulation

    error, feedback = pepita_inputs
    assert torch.allclose(
        error_modulation_ref(error, feedback, SCALE),
        pepita_error_modulation(error, feedback, SCALE),
        atol=0.0,
    )


def test_the_three_declarations_agree(pepita_inputs) -> None:
    """The expression is type-correct for the shapes every record declares.

    The two records that were not the kernel said ``error.T @ feedback``, which
    multiplies ``[D_out, B]`` by ``[D_in, D_out]`` and is a shape error for every
    ``B`` that is not also ``D_in``. Pinning the shapes is what stops a reader
    from "restoring" that expression.
    """
    error, feedback = pepita_inputs
    assert error.shape == (B, D_OUT)
    assert feedback.shape == (D_IN, D_OUT)
    assert error_modulation_ref(error, feedback, SCALE).shape == (D_OUT, D_IN)


def test_there_is_no_batch_mean(pepita_inputs) -> None:
    """The defect the kernel carried, stated as a property.

    Duplicating the batch is what distinguishes a sum from a mean, and it is a
    factor of ``B`` in every element of the answer — invisible in shape, invisible
    in sign, and invisible to any parity check written against the kernel itself.
    """
    error, feedback = pepita_inputs
    doubled = torch.cat([error, error], dim=0)
    assert torch.allclose(
        error_modulation_ref(doubled, feedback, SCALE),
        2 * error_modulation_ref(error, feedback, SCALE),
        atol=1e-4,
    )


def test_each_output_unit_scales_only_its_own_feedback_column(pepita_inputs) -> None:
    """The precise structural claim, so the expression cannot be misread.

    "Output unit ``o`` gates feedback column ``o``" means the feedback matrix is
    transposed and each of its rows scaled by that output unit's batch-summed
    error. It is a row scaling, not an outer product — which is why the kernel's
    ``err[:, None] * tl.trans(fb)`` is a full-rank result and not the rank-1
    thing a looser reading of "sums over the batch" would suggest.
    """
    error, feedback = pepita_inputs
    delta = error_modulation_ref(error, feedback, SCALE)
    assert torch.allclose(
        delta, SCALE * torch.diag(error.sum(dim=0)) @ feedback.T, atol=1e-5
    )


def test_a_zero_scale_is_a_zero_update(pepita_inputs) -> None:
    error, feedback = pepita_inputs
    assert torch.allclose(
        error_modulation_ref(error, feedback, 0.0),
        torch.zeros(D_OUT, D_IN),
        atol=0.0,
    )


def _run(error, feedback, scale: float) -> torch.Tensor:
    import triton

    from computronium.acceleration.ff_kernels import _pepita_error_modulation_kernel

    if _pepita_error_modulation_kernel is False:
        pytest.skip("triton is unavailable, so the PEPITA kernel was never defined")
    delta = torch.empty(D_OUT, D_IN, device=error.device, dtype=torch.float32)
    _pepita_error_modulation_kernel[
        triton.cdiv(D_OUT, BLOCK), triton.cdiv(D_IN, BLOCK)
    ](
        error,
        feedback,
        delta,
        scale,
        B,
        D_IN,
        D_OUT,
        BLOCK_IN=BLOCK,
        BLOCK_OUT=BLOCK,
    )
    return delta


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
def test_the_error_modulation_kernel_equals_its_specification(pepita_inputs) -> None:
    """§4.5's done-when: the kernel matches the expression written above it."""
    from computronium.acceleration.parity import assert_parity
    from computronium.acceleration.registry import get

    error, feedback = (t.cuda() for t in pepita_inputs)
    assert_parity(
        _run(error, feedback, SCALE),
        error_modulation_ref(error, feedback, SCALE),
        get("algorithm.pepita").parity,
    )
