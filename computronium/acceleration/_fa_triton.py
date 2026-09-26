"""Triton kernels for fa_kernels.

Split out of `computronium/acceleration/fa_kernels.py` so the optional triton dependency is guarded by one
import here rather than by a `try` around the whole parent module body.
Importing this module raises ImportError when triton is absent, which is
the signal the parent's `except ImportError` handles.
"""

import triton
import triton.language as tl


@triton.jit
def _fa_feedback_projection_kernel(
    error_ptr,
    feedback_ptr,
    out_ptr,
    B,
    D_in,
    D_out,
    BLOCK_B: tl.constexpr,
    BLOCK_D: tl.constexpr,
):
    """Fused feedback weight projection: error @ B (no transpose).

    feedback matrix has shape [D_out, D_in] (row-major, stride D_in).
    Computes error @ feedback where error: [B, D_out], feedback: [D_out, D_in].
    Output: [B, D_in]
    """
    pid_b = tl.program_id(0)
    pid_d = tl.program_id(1)

    offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)
    offs_d = pid_d * BLOCK_D + tl.arange(0, BLOCK_D)

    mask_b = offs_b < B
    mask_d = offs_d < D_in

    # Accumulate error @ feedback
    acc = tl.zeros((BLOCK_B, BLOCK_D), dtype=tl.float32)
    for k in range(0, D_out, BLOCK_D):
        offs_k = k + tl.arange(0, BLOCK_D)
        mask_k = offs_k < D_out

        # Load error tile [BLOCK_B, BLOCK_D] from error[offs_b, offs_k]
        error_tile = tl.load(
            error_ptr + offs_b[:, None] * D_out + offs_k[None, :],
            mask=mask_b[:, None] & mask_k[None, :],
            other=0.0,
        )

        # Load feedback tile [BLOCK_D, BLOCK_D] from feedback[offs_k, offs_d]
        # feedback is [D_out, D_in], so feedback[offs_k, offs_d]
        fb_tile = tl.load(
            feedback_ptr + offs_k[:, None] * D_in + offs_d[None, :],
            mask=mask_k[:, None] & mask_d[None, :],
            other=0.0,
        )

        acc += tl.dot(error_tile, fb_tile, input_precision="ieee")

    tl.store(
        out_ptr + offs_b[:, None] * D_in + offs_d[None, :],
        acc,
        mask=mask_b[:, None] & mask_d[None, :],
    )


@triton.jit
def _fa_batched_outer_kernel(
    pre_ptr,
    post_ptr,
    grad_ptr,
    B,
    D_in,
    D_out,
    BLOCK_IN: tl.constexpr,
    BLOCK_OUT: tl.constexpr,
):
    """Fused batched outer product for weight gradients."""
    pid_in = tl.program_id(0)
    pid_out = tl.program_id(1)

    offs_in = pid_in * BLOCK_IN + tl.arange(0, BLOCK_IN)
    offs_out = pid_out * BLOCK_OUT + tl.arange(0, BLOCK_OUT)

    mask_in = offs_in < D_in
    mask_out = offs_out < D_out

    acc = tl.zeros((BLOCK_OUT, BLOCK_IN), dtype=tl.float32)

    for b in range(B):
        pre = tl.load(
            pre_ptr + b * D_in + offs_in[None, :],
            mask=mask_in[None, :],
            other=0.0,
        )
        post = tl.load(
            post_ptr + b * D_out + offs_out[:, None],
            mask=mask_out[:, None],
            other=0.0,
        )
        acc += post * pre

    acc = acc / B  # ruff: ignore[non-augmented-assignment]
    tl.store(
        grad_ptr + offs_out[:, None] * D_in + offs_in[None, :],
        acc,
        mask=mask_out[:, None] & mask_in[None, :],
    )


HAS_TRITON_FA = True
