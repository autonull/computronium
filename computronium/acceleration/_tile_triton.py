"""Triton kernels for tile_kernels.

Split out of `computronium/acceleration/tile_kernels.py` so the optional triton dependency is guarded by one
import here rather than by a `try` around the whole parent module body.
Importing this module raises ImportError when triton is absent, which is
the signal the parent's `except ImportError` handles.
"""

import triton
import triton.language as tl


# ── Fused Tile Activity Update ─────────────────────────────────────────
# Computes: activity = clamp(activity - step_size * importance * (error + lambda*activity + sum(feedback)))
@triton.jit
def _tile_activity_update_kernel(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
    activity_ptr,
    error_ptr,
    feedback_ptr,  # [num_feedback, B, N] flattened
    feedback_strides,  # [num_feedback, 3] = [stride_b, stride_n, stride_f]
    num_feedback,
    out_ptr,
    step_size,
    importance,
    lambda_error,
    clamp_min,
    clamp_max,
    clamp,
    B,
    N,
    BLOCK_B: tl.constexpr,
    BLOCK_N: tl.constexpr,
):
    """Fused tile activity update for EP/PC/SNN algorithms."""
    pid_b = tl.program_id(0)
    pid_n = tl.program_id(1)

    offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)

    mask_b = offs_b < B
    mask_n = offs_n < N

    # Load activity and error
    activity = tl.load(
        activity_ptr + offs_b[:, None] * N + offs_n[None, :],
        mask=mask_b[:, None] & mask_n[None, :],
        other=0.0,
    )
    error = tl.load(
        error_ptr + offs_b[:, None] * N + offs_n[None, :],
        mask=mask_b[:, None] & mask_n[None, :],
        other=0.0,
    )

    # Accumulate feedback from all sources
    grad = error + lambda_error * activity
    for f in range(num_feedback):
        fb = tl.load(
            feedback_ptr
            + f * feedback_strides[0]
            + offs_b[:, None] * feedback_strides[1]
            + offs_n[None, :] * feedback_strides[2],
            mask=mask_b[:, None] & mask_n[None, :],
            other=0.0,
        )
        grad = grad + fb  # ruff: ignore[non-augmented-assignment]

    delta = step_size * importance * grad
    new_activity = activity - delta

    if clamp:
        new_activity = tl.maximum(new_activity, clamp_min)
        new_activity = tl.minimum(new_activity, clamp_max)

    tl.store(
        out_ptr + offs_b[:, None] * N + offs_n[None, :],
        new_activity,
        mask=mask_b[:, None] & mask_n[None, :],
    )


# ── Fused Tile Prediction ──────────────────────────────────────────────
# Computes: prediction = sum(inputs) + bias  # ruff: ignore[commented-out-code]
@triton.jit
def _tile_prediction_kernel(
    input_ptrs,  # [num_inputs] array of pointers
    input_strides,  # [num_inputs, 2] = [stride_b, stride_n]
    num_inputs,
    bias_ptr,
    out_ptr,
    B,
    N,
    BLOCK_B: tl.constexpr,
    BLOCK_N: tl.constexpr,
):
    """Fused tile prediction: sum of weighted inputs + bias."""
    pid_b = tl.program_id(0)
    pid_n = tl.program_id(1)

    offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)

    mask_b = offs_b < B
    mask_n = offs_n < N

    acc = tl.zeros((BLOCK_B, BLOCK_N), dtype=tl.float32)

    for i in range(num_inputs):
        inp = tl.load(
            input_ptrs[i] + offs_b[:, None] * input_strides[i, 1] + offs_n[None, :],
            mask=mask_b[:, None] & mask_n[None, :],
            other=0.0,
        )
        acc += inp

    if bias_ptr != 0:
        bias = tl.load(bias_ptr + offs_n, mask=mask_n, other=0.0)
        acc += bias[None, :]

    tl.store(
        out_ptr + offs_b[:, None] * N + offs_n[None, :],
        acc,
        mask=mask_b[:, None] & mask_n[None, :],
    )


# ── Fused Contrastive Hebbian Update ───────────────────────────────────
# Computes: delta = lr/beta * (src_free.T @ dst_free - src_nudged.T @ dst_nudged) / B  # ruff: ignore[commented-out-code]
@triton.jit
def _tile_contrastive_update_kernel(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
    src_free_ptr,
    dst_free_ptr,
    src_nudged_ptr,
    dst_nudged_ptr,
    delta_ptr,
    lr,
    beta,
    B,
    D_in,
    D_out,
    BLOCK_IN: tl.constexpr,
    BLOCK_OUT: tl.constexpr,
):
    """Fused contrastive Hebbian weight update per tile."""
    pid_in = tl.program_id(0)
    pid_out = tl.program_id(1)

    offs_in = pid_in * BLOCK_IN + tl.arange(0, BLOCK_IN)
    offs_out = pid_out * BLOCK_OUT + tl.arange(0, BLOCK_OUT)

    mask_in = offs_in < D_in
    mask_out = offs_out < D_out

    acc_free = tl.zeros((BLOCK_OUT, BLOCK_IN), dtype=tl.float32)
    acc_nudged = tl.zeros((BLOCK_OUT, BLOCK_IN), dtype=tl.float32)

    for b in range(B):
        # Free phase
        pre_f = tl.load(
            src_free_ptr + b * D_in + offs_in[None, :],
            mask=mask_in[None, :],
            other=0.0,
        )
        post_f = tl.load(
            dst_free_ptr + b * D_out + offs_out[:, None],
            mask=mask_out[:, None],
            other=0.0,
        )
        acc_free += tl.dot(tl.trans(post_f), pre_f)

        # Nudged phase
        pre_n = tl.load(
            src_nudged_ptr + b * D_in + offs_in[None, :],
            mask=mask_in[None, :],
            other=0.0,
        )
        post_n = tl.load(
            dst_nudged_ptr + b * D_out + offs_out[:, None],
            mask=mask_out[:, None],
            other=0.0,
        )
        acc_nudged += tl.dot(tl.trans(post_n), pre_n)

    acc_free = acc_free / B  # ruff: ignore[non-augmented-assignment]
    acc_nudged = acc_nudged / B  # ruff: ignore[non-augmented-assignment]

    delta = (lr / beta) * (acc_free - acc_nudged)

    tl.store(
        delta_ptr + offs_out[:, None] * D_in + offs_in[None, :],
        delta,
        mask=mask_out[:, None] & mask_in[None, :],
    )


# ── Fused Hebbian Update ───────────────────────────────────────────────
# Computes: delta = importance * (src.T @ dst) / B  # ruff: ignore[commented-out-code]
@triton.jit
def _tile_hebbian_update_kernel(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
    src_ptr,
    dst_ptr,
    weight_ptr,
    delta_ptr,
    importance,
    B,
    D_in,
    D_out,
    BLOCK_IN: tl.constexpr,
    BLOCK_OUT: tl.constexpr,
):
    """Fused Hebbian weight update per tile."""
    pid_in = tl.program_id(0)
    pid_out = tl.program_id(1)

    offs_in = pid_in * BLOCK_IN + tl.arange(0, BLOCK_IN)
    offs_out = pid_out * BLOCK_OUT + tl.arange(0, BLOCK_OUT)

    mask_in = offs_in < D_in
    mask_out = offs_out < D_out

    acc = tl.zeros((BLOCK_OUT, BLOCK_IN), dtype=tl.float32)

    for b in range(B):
        pre = tl.load(
            src_ptr + b * D_in + offs_in[None, :],
            mask=mask_in[None, :],
            other=0.0,
        )
        post = tl.load(
            dst_ptr + b * D_out + offs_out[:, None],
            mask=mask_out[:, None],
            other=0.0,
        )
        acc += tl.dot(tl.trans(post), pre)

    acc = acc / B  # ruff: ignore[non-augmented-assignment]
    delta = importance * acc

    # Oja's subtraction term if weight provided
    if weight_ptr != 0:
        post_sq = tl.zeros((BLOCK_OUT, 1), dtype=tl.float32)
        for b in range(B):
            post = tl.load(
                dst_ptr + b * D_out + offs_out[:, None],
                mask=mask_out[:, None],
                other=0.0,
            )
            post_sq += post * post
        post_sq = post_sq / B  # ruff: ignore[non-augmented-assignment]
        weight = tl.load(
            weight_ptr + offs_out[:, None] * D_in + offs_in[None, :],
            mask=mask_out[:, None] & mask_in[None, :],
            other=0.0,
        )
        delta = delta - post_sq * weight  # ruff: ignore[non-augmented-assignment]

    tl.store(
        delta_ptr + offs_out[:, None] * D_in + offs_in[None, :],
        delta,
        mask=mask_out[:, None] & mask_in[None, :],
    )


# ── Tile Routing Kernels (MoT) ─────────────────────────────────────────


@triton.jit
def _tile_topk_routing_kernel(
    logits_ptr,
    topk_indices_ptr,
    topk_values_ptr,
    B,
    N,
    K,
    BLOCK_B: tl.constexpr,
):
    """Top-K tile routing: select top K tiles per sample."""
    pid_b = tl.program_id(0)

    offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)
    mask_b = offs_b < B

    for b_idx in range(BLOCK_B):
        b = pid_b * BLOCK_B + b_idx
        if not mask_b[b_idx]:
            continue

        # Load logits for this sample
        logits = tl.load(
            logits_ptr + b * N + tl.arange(0, N),
            mask=tl.arange(0, N) < N,
            other=-float("inf"),
        )

        # Simple top-k via selection (for small K, N)
        # In practice, use a more efficient algorithm
        for k in range(K):
            max_val = -float("inf")
            max_idx = 0
            for n in range(N):
                if logits[n] > max_val:
                    max_val = logits[n]
                    max_idx = n
            topk_indices_ptr[b * K + k] = max_idx
            topk_values_ptr[b * K + k] = max_val
            logits[max_idx] = -float("inf")


@triton.jit
def _tile_random_routing_kernel(
    logits_ptr,
    topk_indices_ptr,
    topk_values_ptr,
    B,
    N,
    K,
    seed,
    BLOCK_B: tl.constexpr,
):
    """Random tile routing: sample K tiles per sample."""
    pid_b = tl.program_id(0)

    offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)
    mask_b = offs_b < B

    for b_idx in range(BLOCK_B):
        b = pid_b * BLOCK_B + b_idx
        if not mask_b[b_idx]:
            continue

        # Use deterministic random based on seed + batch index
        rng_state = seed + b * 12345 + 67890
        for k in range(K):
            rng_state = rng_state * 1664525 + 1013904223
            idx = rng_state % N
            topk_indices_ptr[b * K + k] = idx
            # Value from logits
            val = tl.load(logits_ptr + b * N + idx)
            topk_values_ptr[b * K + k] = val


@triton.jit
def _tile_learned_routing_kernel(  # ruff: ignore[too-many-arguments, too-many-positional-arguments]
    logits_ptr,
    router_weights_ptr,
    router_bias_ptr,
    topk_indices_ptr,
    topk_values_ptr,
    B,
    N,
    K,
    router_dim,
    BLOCK_B: tl.constexpr,
):
    """Learned tile routing: small MLP router."""
    pid_b = tl.program_id(0)

    offs_b = pid_b * BLOCK_B + tl.arange(0, BLOCK_B)
    mask_b = offs_b < B

    for b_idx in range(BLOCK_B):
        b = pid_b * BLOCK_B + b_idx
        if not mask_b[b_idx]:
            continue

        # Load logits
        logits = tl.load(
            logits_ptr + b * N + tl.arange(0, N),
            mask=tl.arange(0, N) < N,
            other=0.0,
        )

        # Router: logits -> router_weights -> router_bias -> softmax
        # Simplified: use logits directly with learned temperature
        # Full MLP would require more shared memory
        temp = tl.load(router_weights_ptr) if router_weights_ptr != 0 else 1.0
        logits = logits * temp  # ruff: ignore[non-augmented-assignment]

        if router_bias_ptr != 0:
            bias = tl.load(
                router_bias_ptr + tl.arange(0, N),
                mask=tl.arange(0, N) < N,
                other=0.0,
            )
            logits = logits + bias  # ruff: ignore[non-augmented-assignment]

        # Softmax
        max_logit = tl.max(logits, axis=0)
        exp_logits = tl.exp(logits - max_logit)
        sum_exp = tl.sum(exp_logits, axis=0)
        probs = exp_logits / sum_exp

        # Top-k from probs
        for k in range(K):
            max_val = -float("inf")
            max_idx = 0
            for n in range(N):
                if probs[n] > max_val:
                    max_val = probs[n]
                    max_idx = n
            topk_indices_ptr[b * K + k] = max_idx
            topk_values_ptr[b * K + k] = max_val
            probs[max_idx] = -float("inf")


HAS_TRITON_TILE = True
