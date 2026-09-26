"""The contrastive-update specification, written before the kernels (TODO36 §4.5).

Seven kernels in the tree compute a maths nobody wrote down anywhere except in the
kernel itself, so there is no oracle to check them against. The rule this file
follows is §4.5's: **write the torch expression first, as a test, and do not port
from the kernel to the test.** The reference is derived from the maths the kernels
name — a difference of batched outer products, scaled by a learning rate and a
nudge strength — and is verified against an explicit loop, so the reference itself
is anchored to something other than the kernel.

**One expression, four kernels**, because they are the same maths. They differ in
exactly two ways: which phase is added and which is subtracted, and whether the
nudge strength ``beta`` is divided out.

==============  =====================  =========  ===================
kernel          added phase            divisor   owning spec
==============  =====================  =========  ===================
``_ff_…``         positive phase         —         ``algorithm.ff``
``_pepita_…``     standard phase        —         ``algorithm.pepita``
``_pc_…``         nudged phase          ``beta``  ``algorithm.pc``
``_hebbian_…``    nudged phase          ``beta``  ``algorithm.hebbian``
==============  =====================  =========  ===================

PEPITA's row is why its phases are *standard* against *error*: PEPITA's error
signal is itself a difference of two phases, so folding it in leaves the standard
phase minus the error phase. The kernel's docstring states the same expression,
which is a second, independent record of the intent.

``_contrastive_hebbian_kernel`` is not a separate specification at all: it is
``contrastive_primitives.contrastive_hebbian_update`` in triton, which is the
composition of two already-written expressions. :func:`_reference_is_the_torch_path`
pins that, so the table below cannot drift from the torch path it mirrors.
"""

from __future__ import annotations

from typing import NamedTuple

import pytest
import torch

from computronium.acceleration.contrastive_primitives import (
    batched_outer_product,
    contrastive_delta,
    contrastive_hebbian_update,
)

# D_in and D_out are deliberately not multiples of BLOCK (48 and 32 against 16),
# so a kernel that reads one program id and stores the other leaves part of its
# output unwritten — silently, with no error. Two of the four kernels below had
# exactly that defect when this table was first measured.
B, D_IN, D_OUT, BLOCK = 8, 48, 32, 16
LR, BETA = 0.01, 0.5


def contrastive_delta_ref(
    subtracted_pre: torch.Tensor,
    subtracted_post: torch.Tensor,
    added_pre: torch.Tensor,
    added_post: torch.Tensor,
    lr: float,
    divisor: float = 1.0,
) -> torch.Tensor:
    """The expression every contrastive-update kernel in this file computes.

    ``dW = lr * (added - subtracted) / divisor``, where each term is a batched
    outer product averaged over the batch.

    Args:
        subtracted_pre: ``[B, D_in]`` layer input of the phase being subtracted.
        subtracted_post: ``[B, D_out]`` its output, subtracted.
        added_pre: ``[B, D_in]`` layer input of the phase being added.
        added_post: ``[B, D_out]`` its output, added.
        lr: learning rate.
        divisor: nudge strength; ``1.0`` when the kernel has no ``beta``.

    Returns:
        ``[D_out, D_in]`` weight delta.
    """
    return (
        lr
        * (
            batched_outer_product(added_pre, added_post)
            - batched_outer_product(subtracted_pre, subtracted_post)
        )
        / divisor
    )


def ff_contrastive_delta(
    pre_pos: torch.Tensor,
    post_pos: torch.Tensor,
    pre_neg: torch.Tensor,
    post_neg: torch.Tensor,
    lr: float,
) -> torch.Tensor:
    """The expression the FF contrastive kernel is meant to equal, in FF's names.

    A layer's weight update is the difference between the positive and negative
    phases' batched outer products, averaged over the batch and scaled by the
    learning rate:

        dW = lr * ( (post_pos.T @ pre_pos) / B - (post_neg.T @ pre_neg) / B )

    Args:
        pre_pos: ``[B, D_in]`` layer input on the positive phase.
        post_pos: ``[B, D_out]`` layer output on the positive phase.
        pre_neg: ``[B, D_in]`` layer input on the negative phase.
        post_neg: ``[B, D_out]`` layer output on the negative phase.
        lr: learning rate.

    Returns:
        ``[D_out, D_in]`` weight delta.
    """
    return contrastive_delta_ref(pre_neg, post_neg, pre_pos, post_pos, lr)


def _loop_reference(
    added_pre: torch.Tensor,
    added_post: torch.Tensor,
    subtracted_pre: torch.Tensor,
    subtracted_post: torch.Tensor,
    lr: float,
) -> torch.Tensor:
    """The same expression written out, as the anchor the reference is checked against."""
    delta = torch.zeros(D_OUT, D_IN, dtype=torch.float64)
    for b in range(added_pre.shape[0]):
        delta += torch.outer(added_post[b].double(), added_pre[b].double())
        delta -= torch.outer(subtracted_post[b].double(), subtracted_pre[b].double())
    return (lr * delta / added_pre.shape[0]).float()


@pytest.fixture
def phases() -> tuple[torch.Tensor, ...]:
    """``(added_pre, added_post, subtracted_pre, subtracted_post)``."""
    generator = torch.Generator().manual_seed(7)
    return tuple(
        torch.randn(B, width, generator=generator)
        for width in (D_IN, D_OUT, D_IN, D_OUT)
    )


def test_the_reference_matches_an_explicit_loop(
    phases: tuple[torch.Tensor, ...],
) -> None:
    """The specification is anchored to a loop, not to a kernel."""
    added_pre, added_post, subtracted_pre, subtracted_post = phases
    assert torch.allclose(
        contrastive_delta_ref(
            subtracted_pre, subtracted_post, added_pre, added_post, LR
        ),
        _loop_reference(*phases, LR),
        atol=1e-6,
    )


def test_the_reference_is_the_difference_of_the_two_phases(
    phases: tuple[torch.Tensor, ...],
) -> None:
    """Zero learning rate is zero update; a zero subtracted phase is the other one."""
    added_pre, added_post, subtracted_pre, subtracted_post = phases
    zero = torch.zeros_like(subtracted_post)
    assert torch.allclose(
        ff_contrastive_delta(
            added_pre, added_post, subtracted_pre, subtracted_post, 0.0
        ),
        torch.zeros(D_OUT, D_IN),
        atol=0.0,
    )
    assert torch.allclose(
        ff_contrastive_delta(added_pre, added_post, added_pre, zero, 1.0),
        batched_outer_product(added_pre, added_post),
        atol=1e-6,
    )


def test_the_reference_is_the_torch_path_it_replaces(
    phases: tuple[torch.Tensor, ...],
) -> None:
    """The table below must not diverge from `contrastive_hebbian_update`.

    The hebbian rung is that function in triton, so if the reference here ever
    stops agreeing with it, one of the two has become a specification of
    something else.
    """
    added_pre, added_post, subtracted_pre, subtracted_post = phases
    assert torch.allclose(
        contrastive_delta_ref(
            subtracted_pre, subtracted_post, added_pre, added_post, LR, BETA
        ),
        contrastive_hebbian_update(
            subtracted_pre, subtracted_post, added_pre, added_post, LR, BETA
        ),
        atol=0.0,
    )
    assert torch.allclose(
        contrastive_delta_ref(
            subtracted_pre, subtracted_post, added_pre, added_post, LR, BETA
        ),
        LR
        * contrastive_delta(
            batched_outer_product(subtracted_pre, subtracted_post),
            batched_outer_product(added_pre, added_post),
            BETA,
        ),
        atol=0.0,
    )


class Rung(NamedTuple):
    """One kernel's rung of this expression, and how to launch it."""

    label: str
    module: str
    attr: str
    spec_id: str
    scalars: tuple[str, ...]
    """The kernel's trailing scalar parameters, in signature order, by name."""

    added_first: bool
    """Whether the kernel's first phase pair is the added one.

    Half the rungs take ``(free, nudged)`` and half ``(positive, negative)``, and
    passing them the wrong way round produces the exact negation of the right
    answer — a cosine of −1, which is as unambiguous a failure as this tree has
    produced. The flag is the kernel's own parameter order, not a preference.
    """


RUNGS = (
    Rung(
        "ff",
        "ff_kernels",
        "_ff_contrastive_update_kernel",
        "algorithm.ff",
        ("lr",),
        True,
    ),
    Rung(
        "pepita",
        "ff_kernels",
        "_pepita_contrastive_update_kernel",
        "algorithm.pepita",
        ("lr",),
        True,
    ),
    Rung(
        "pc",
        "pc_kernels",
        "_pc_contrastive_update_kernel",
        "algorithm.pc",
        ("beta", "lr"),
        False,
    ),
    Rung(
        "hebbian",
        "hebbian_kernels",
        "_contrastive_hebbian_kernel",
        "algorithm.hebbian",
        ("lr", "beta"),
        False,
    ),
)
_SCALARS = {"lr": LR, "beta": BETA}


def _in_kernel_order(
    rung: Rung, phases: tuple[torch.Tensor, ...]
) -> tuple[torch.Tensor, ...]:
    """Reorder ``(added, subtracted)`` phases into the order the kernel's signature takes."""
    if rung.added_first:
        return phases
    return phases[2], phases[3], phases[0], phases[1]


def _run(rung: Rung, *phase_tensors: torch.Tensor) -> torch.Tensor:
    import importlib

    import triton

    kernel = getattr(
        importlib.import_module(f"computronium.acceleration.{rung.module}"), rung.attr
    )
    if kernel is False:
        pytest.skip("triton is unavailable, so the kernel was never defined")
    delta = torch.empty(
        D_OUT, D_IN, device=phase_tensors[0].device, dtype=torch.float32
    )
    kernel[
        # Grid is (out, in) to match the store, which is row-major over [D_out, D_in].
        triton.cdiv(D_OUT, BLOCK), triton.cdiv(D_IN, BLOCK)
    ](
        *phase_tensors,
        delta,
        B,
        D_IN,
        D_OUT,
        *(_SCALARS[name] for name in rung.scalars),
        BLOCK_IN=BLOCK,
        BLOCK_OUT=BLOCK,
    )
    return delta


@pytest.mark.skipif(
    not torch.cuda.is_available(), reason="a triton kernel needs a device tensor"
)
@pytest.mark.parametrize("rung", RUNGS, ids=lambda r: r.label)
def test_the_contrastive_kernel_equals_its_specification(
    rung: Rung, phases: tuple[torch.Tensor, ...]
) -> None:
    """§4.5's done-when, for every rung of this expression."""
    from computronium.acceleration.parity import assert_parity
    from computronium.acceleration.registry import get

    on_device = tuple(t.cuda() for t in phases)
    added_pre, added_post, subtracted_pre, subtracted_post = on_device
    divisor = BETA if "beta" in rung.scalars else 1.0
    assert_parity(
        _run(rung, *_in_kernel_order(rung, on_device)),
        contrastive_delta_ref(
            subtracted_pre, subtracted_post, added_pre, added_post, LR, divisor
        ),
        get(rung.spec_id).parity,
    )
