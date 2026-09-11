"""Shared synthetic task builders (TODO21 T21.3A.3).

Single source for the gaussian-blob and switching tasks used by the joint
experiments, the lab package, and the probes. Bitwise generation order is
fixed (centers → labels → samples) so downstream parity locks hold.
"""

from __future__ import annotations

import torch
from torch import Tensor

__all__ = ["create_switching_task", "gaussian_blobs"]


def gaussian_blobs(
    n: int,
    input_dim: int,
    num_classes: int,
    *,
    scale: float = 2.0,
    noise: float = 0.5,
    device: torch.device | str | None = None,
    generator: torch.Generator | None = None,
) -> tuple[Tensor, Tensor]:
    """Gaussian-blob classification: each sample clusters around one center.

    Args:
        n: Number of samples.
        input_dim: Feature dimension.
        num_classes: Number of cluster centers (= number of classes).
        scale: Spread of the random cluster centers.
        noise: Per-sample Gaussian noise added around the assigned center.
        device: Target device.
        generator: Optional CPU generator for determinism.

    Returns:
        ``(x, y)`` where ``y`` holds the assigned class (center) ids.
    """
    centers = (
        torch.randn(num_classes, input_dim, device=device, generator=generator) * scale
    )
    labels = torch.randint(0, num_classes, (n,), device=device, generator=generator)
    x = (
        centers[labels]
        + torch.randn(n, input_dim, device=device, generator=generator) * noise
    )
    return x, labels


def create_switching_task(
    batch_size: int,
    seq_len: int,
    input_dim: int,
    phase: str = "A",
    device: torch.device | str | None = None,
) -> tuple[Tensor, Tensor]:
    """Two-phase conflicting task on random sequences.

    Phase A classifies by the sign of the sequence mean; phase B by the sign
    of the last symbol — the two label geometries conflict, which is what
    the ψ switching and local-feedback benchmarks key on.
    """
    x = torch.randn(batch_size, seq_len, input_dim, device=device)
    if phase == "A":
        y = (x.sum(dim=1).mean(dim=-1) > 0).long()
    else:
        y = (x[:, -1, :].mean(dim=-1) > 0).long()
    return x, y
