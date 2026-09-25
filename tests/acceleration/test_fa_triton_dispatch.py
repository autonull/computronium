"""The standalone ``fa_*_triton`` entry points must resolve their own capability flag.

Both helpers branched on a bare ``HAS_TRITON`` while the module defined
``HAS_TRITON_FA``, so each raised ``NameError`` before reaching its first line
of work, on the GPU credit path no test reached. Calling them surfaced two
further defects the same untested path was hiding, both now fixed:

* ``_fa_batched_outer_kernel`` called ``tl.dot`` where the contraction is an
  outer product (batch-major ``post[b] ⊗ pre[b]``), which failed to compile.
* A duplicate "with transpose" projection whose Triton kernel and eager
  fallback disagreed with each other and with their only callers. It had zero
  callers and was deleted; the surviving projection is ``error @ feedback``,
  matching ``local_goodness`` and ``random_projections``.

The parity tests below are what would catch their return.
"""

import pytest
import torch

from computronium.acceleration.fa_kernels import (
    HAS_TRITON_FA,
    fa_batched_outer_triton,
    fa_feedback_projection_triton,
)

DEVICES = ["cpu"] + (["cuda"] if torch.cuda.is_available() else [])


@pytest.mark.parametrize("device", DEVICES)
def test_feedback_projection_matches_eager(device: str) -> None:
    error = torch.randn(8, 16, device=device)
    feedback = torch.randn(16, 32, device=device)
    torch.testing.assert_close(
        fa_feedback_projection_triton(error, feedback), error @ feedback
    )


@pytest.mark.parametrize("device", DEVICES)
def test_batched_outer_matches_eager(device: str) -> None:
    pre = torch.randn(8, 16, device=device)
    post = torch.randn(8, 32, device=device)
    torch.testing.assert_close(
        fa_batched_outer_triton(pre, post), (post.T @ pre) / pre.shape[0]
    )


@pytest.mark.parametrize("device", DEVICES)
def test_batched_outer_handles_non_multiples_of_block_size(device: str) -> None:
    """The kernel's block tiling must not assume power-of-two leading dims."""
    pre = torch.randn(3, 17, device=device)
    post = torch.randn(3, 40, device=device)
    torch.testing.assert_close(
        fa_batched_outer_triton(pre, post), (post.T @ pre) / pre.shape[0]
    )


def test_feedback_projection_preserves_grad() -> None:
    error = torch.randn(8, 16, requires_grad=True)
    feedback = torch.randn(16, 32)
    fa_feedback_projection_triton(error, feedback).sum().backward()
    assert error.grad is not None
    torch.testing.assert_close(
        error.grad,
        torch.ones(error.shape[0], feedback.shape[1], device="cpu") @ feedback.T,
    )


def test_cuda_path_is_gated_on_triton() -> None:
    """The CUDA branch is only reachable with Triton; assert the flag agrees."""
    if not torch.cuda.is_available():
        pytest.skip("no CUDA")
    assert HAS_TRITON_FA, "CUDA present but triton FA kernels unavailable"
