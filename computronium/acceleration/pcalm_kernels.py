"""PC-ALM fused primal-dual kernels (Seely & Gould 2026, arXiv:2605.31022).

Two acceleration surfaces for ``PCALMDynamics``:

1. ``pcalm_settle_loop`` — the whole T-step primal-dual relaxation as one
   function, compiled via ``torch.compile`` (``_compiled_pcalm_settle``) so a
   settle is one graph launch instead of ``T * L`` eager kernel launches.
   Digital-substrate arithmetic is inlined (``x @ w.T``), bitwise-equal to
   the eager path (verified by the compiled-settle lock).
2. ``fused_dual_primal_update`` — a Triton kernel fusing the per-layer
   elementwise dual update + primal update (matmuls stay on torch). Device
   agnostic: CUDA via stock Triton, CPU via triton-cpu
   (``triton.runtime.driver.set_active_to_cpu()`` or
   ``TRITON_DEFAULT_BACKEND=cpu``); eager fallback otherwise.

# Portions of this module are derived from PC-ALM.
# Copyright (c) 2026 Sakana AI
# Original Authors: Jeffrey Seely, Julian Gould
# License: MIT
# Paper: https://arxiv.org/abs/2605.31022
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

import torch
from torch import Tensor, nn

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    class _TritonKernel(Protocol):
        """Triton JITFunction launch surface: kernel[grid](...args)."""

        def __getitem__(self, grid: tuple[int]) -> Callable[..., object]: ...


def _one_hot(target: Tensor, like: Tensor) -> Tensor:
    if target.dim() == 1:
        out = torch.zeros_like(like)
        out.scatter_(1, target.unsqueeze(1), 1.0)
        return out
    return target


def pcalm_settle_loop(  # ruff: ignore[too-many-arguments, too-many-positional-arguments] (mirrors the eager settle loop)
    acts: list[Tensor],
    dual_vars: list[Tensor],
    weights: Sequence[Tensor],
    biases: Sequence[Tensor | None],
    activations: Sequence[nn.Module],
    step_size: float,
    rho: float,
    alpha: float,
    beta: float,
    target: Tensor | None,
    n_steps: int,
) -> tuple[list[Tensor], list[Tensor]]:
    """Whole primal-dual relaxation as one callable.

    Bitwise-mirrors ``PCALMDynamics.settle``'s eager loop: constraints
    ``c_l = h_l - f(h_{l-1})``, dual update
    ``lam_l += eta * (c_l + alpha * lam_l)``, primal update with analytical
    ReLU Jacobian-transpose top-down coupling, per-step output nudge.
    """
    num_layers = len(weights)
    for _ in range(n_steps):
        constraints: list[Tensor] = []
        for i in range(num_layers):
            predicted = acts[i] @ weights[i].T
            b = biases[i]
            if b is not None:
                predicted = predicted + b  # ruff: ignore[non-augmented-assignment] (graph-safe out-of-place)
            if i < len(activations):
                predicted = activations[i](predicted)
            constraints.append(acts[i + 1] - predicted)

        for i in range(num_layers):
            dual_vars[i] = dual_vars[i] + step_size * (  # ruff: ignore[non-augmented-assignment]
                constraints[i] + alpha * dual_vars[i]
            )

        new_acts: list[Tensor] = [acts[0]]
        for i in range(num_layers):
            grad = constraints[i] + dual_vars[i] + rho * constraints[i]
            if i < num_layers - 1:
                z = acts[i + 1] @ weights[i + 1].T
                b = biases[i + 1]
                if b is not None:
                    z = z + b  # ruff: ignore[non-augmented-assignment]
                v = constraints[i + 1] + dual_vars[i + 1] + rho * constraints[i + 1]
                grad = grad - (v * (z > 0).to(v.dtype)) @ weights[i + 1]  # ruff: ignore[non-augmented-assignment]
            new_acts.append(acts[i + 1] - step_size * grad)

        if beta > 0 and target is not None:
            out = new_acts[-1]
            new_acts[-1] = out + beta * (_one_hot(target, out) - out)

        acts = new_acts
    return acts, dual_vars


_compiled_pcalm_settle = torch.compile(pcalm_settle_loop, dynamic=False)


def _triton_available(device: torch.device) -> bool:
    """True when a Triton driver is active for ``device``.

    CUDA tensors: stock Triton. CPU tensors: triton-cpu (active when the
    CPU driver is selected automatically, via ``set_active_to_cpu()``, or
    ``TRITON_DEFAULT_BACKEND=cpu``).
    """
    if not HAS_TRITON_PCALM:
        return False
    if device.type == "cuda":
        return True
    if device.type == "cpu":
        try:
            import triton

            target = triton.runtime.driver.active.get_current_target()
            return getattr(target, "backend", "") == "cpu"
        except Exception:
            return False
    return False


def _eager_dual_primal_update(
    h: Tensor,
    c: Tensor,
    lam: Tensor,
    topdown: Tensor,
    step_size: float,
    rho: float,
    alpha: float,
) -> tuple[Tensor, Tensor]:
    lam_new = lam + step_size * (c + alpha * lam)
    h_new = h - step_size * (c + lam_new + rho * c - topdown)
    return lam_new, h_new


HAS_TRITON_PCALM = False
try:
    import triton  # ruff: ignore[unused-import]

    HAS_TRITON_PCALM = True
except ImportError:
    HAS_TRITON_PCALM = False


def _build_fused_kernel() -> _TritonKernel | None:
    """Compile the fused elementwise update kernel, or None without Triton."""
    if not HAS_TRITON_PCALM:
        return None
    import triton
    import triton.language as tl

    @triton.jit
    def _fused_update_kernel(  # ruff: ignore[too-many-arguments, too-many-positional-arguments] (kernel ABI)
        h_ptr,
        c_ptr,
        lam_ptr,
        topdown_ptr,
        lam_out_ptr,
        h_out_ptr,
        step_size,
        rho,
        alpha,
        n_elements,
        BLOCK_SIZE: tl.constexpr,
    ):
        pid = tl.program_id(0)
        offs = pid * BLOCK_SIZE + tl.arange(0, BLOCK_SIZE)
        mask = offs < n_elements

        h = tl.load(h_ptr + offs, mask=mask)
        c = tl.load(c_ptr + offs, mask=mask)
        lam = tl.load(lam_ptr + offs, mask=mask)
        topdown = tl.load(topdown_ptr + offs, mask=mask)

        lam_new = lam + step_size * (c + alpha * lam)
        h_new = h - step_size * (c + lam_new + rho * c - topdown)

        tl.store(lam_out_ptr + offs, lam_new, mask=mask)
        tl.store(h_out_ptr + offs, h_new, mask=mask)

    return cast("_TritonKernel", _fused_update_kernel)


_FUSED_UPDATE_KERNEL: _TritonKernel | None = _build_fused_kernel()


def fused_dual_primal_update(
    h: Tensor,
    c: Tensor,
    lam: Tensor,
    topdown: Tensor,
    step_size: float,
    rho: float,
    alpha: float,
) -> tuple[Tensor, Tensor]:
    """One layer's fused elementwise dual + primal update.

    ``lam_new = lam + eta * (c + alpha * lam)``
    ``h_new = h - eta * (c + lam_new + rho * c - topdown)``

    Triton path when a driver is active for the tensors' device (CUDA via
    stock Triton, CPU via triton-cpu); bitwise-equal eager fallback
    otherwise. The top-down matmul term is precomputed by the caller.
    """
    kernel = _FUSED_UPDATE_KERNEL
    if kernel is not None and _triton_available(h.device):
        lam_out = torch.empty_like(lam)
        h_out = torch.empty_like(h)
        n = h.numel()
        BLOCK_SIZE = 1024
        grid = ((n + BLOCK_SIZE - 1) // BLOCK_SIZE,)
        kernel[grid](
            h,
            c,
            lam,
            topdown,
            lam_out,
            h_out,
            step_size,
            rho,
            alpha,
            n,
            BLOCK_SIZE=BLOCK_SIZE,
        )
        return lam_out, h_out
    return _eager_dual_primal_update(h, c, lam, topdown, step_size, rho, alpha)


__all__ = [
    "HAS_TRITON_PCALM",
    "_compiled_pcalm_settle",
    "fused_dual_primal_update",
    "pcalm_settle_loop",
]
