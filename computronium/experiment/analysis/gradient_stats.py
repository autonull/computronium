"""Gradient Statistics Analysis (Phase D3).

Computes gradient norm, cosine similarity, and layer alignment
for convergence diagnostics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
import torch

if TYPE_CHECKING:
    from torch import Tensor, nn


@dataclass(frozen=True, slots=True)
class GradientStatsResult:
    """Result of gradient statistics analysis."""

    gradient_norms: dict[str, float]  # layer -> norm
    gradient_cosine_similarities: dict[str, float]  # layer pair -> cosine sim
    layer_alignments: dict[str, float]  # layer -> alignment with final gradient
    global_gradient_norm: float
    gradient_snr: float  # signal-to-noise ratio
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class GradientStatsConfig:
    """Configuration for gradient statistics."""

    max_layers: int = 20
    sample_batches: int = 10


def compute_gradient_statistics(
    model: nn.Module,
    dataloader,
    device: str = "cpu",
    config: GradientStatsConfig | None = None,
) -> GradientStatsResult:
    """Compute gradient statistics during training."""
    config = config or GradientStatsConfig()

    model.train()
    model.to(device)

    layer_grads: dict[str, list[Tensor]] = {}

    # Collect gradients over several batches
    for i, (x, y) in enumerate(dataloader):
        if i >= config.sample_batches:
            break

        x, y = x.to(device), y.to(device)
        model.zero_grad()

        output = model(x)
        loss = torch.nn.functional.cross_entropy(output, y)
        loss.backward()

        for name, param in model.named_parameters():
            if param.grad is not None:
                if name not in layer_grads:
                    layer_grads[name] = []
                layer_grads[name].append(param.grad.detach().clone().cpu())

    # Compute statistics
    gradient_norms = {}
    for name, grads in layer_grads.items():
        stacked = torch.stack(grads)
        mean_grad = stacked.mean(dim=0)
        gradient_norms[name] = float(mean_grad.norm().item())

    # Cosine similarity between layer gradients
    gradient_cosine_similarities = {}
    layer_names = list(layer_grads.keys())[: config.max_layers]
    for i, name1 in enumerate(layer_names):
        for name2 in layer_names[i + 1 :]:
            g1 = torch.stack(layer_grads[name1]).mean(dim=0).flatten()
            g2 = torch.stack(layer_grads[name2]).mean(dim=0).flatten()
            if g1.numel() == g2.numel():
                cos_sim = torch.nn.functional.cosine_similarity(
                    g1.unsqueeze(0), g2.unsqueeze(0)
                ).item()
                gradient_cosine_similarities[f"{name1}×{name2}"] = float(cos_sim)

    # Alignment with global gradient
    all_grads = []
    for name in layer_names:
        g = torch.stack(layer_grads[name]).mean(dim=0).flatten()
        all_grads.append(g)

    if all_grads:
        global_grad = torch.cat(all_grads)
        layer_alignments = {}
        for name in layer_names:
            g = torch.stack(layer_grads[name]).mean(dim=0).flatten()
            if g.numel() <= global_grad.numel():
                # Pad or truncate
                if g.numel() < global_grad.numel():
                    g = torch.cat([g, torch.zeros(global_grad.numel() - g.numel())])
                else:
                    g = g[: global_grad.numel()]
                align = torch.nn.functional.cosine_similarity(
                    g.unsqueeze(0), global_grad.unsqueeze(0)
                ).item()
                layer_alignments[name] = float(align)
    else:
        layer_alignments = {}

    # Global gradient norm
    global_gradient_norm = float(global_grad.norm().item()) if all_grads else 0.0

    # Gradient SNR (mean / std of gradient norms across batches)
    all_norms = []
    for name, grads in layer_grads.items():
        for g in grads:
            all_norms.append(g.norm().item())

    if len(all_norms) > 1:
        gradient_snr = float(np.mean(all_norms) / (np.std(all_norms) + 1e-8))
    else:
        gradient_snr = 0.0

    return GradientStatsResult(
        gradient_norms=gradient_norms,
        gradient_cosine_similarities=gradient_cosine_similarities,
        layer_alignments=layer_alignments,
        global_gradient_norm=global_gradient_norm,
        gradient_snr=gradient_snr,
        metadata={
            "n_layers": len(layer_grads),
            "sample_batches": config.sample_batches,
            "device": device,
        },
    )


def compute_gradient_cosine_similarity(
    grad1: Tensor,
    grad2: Tensor,
) -> float:
    """Compute cosine similarity between two gradient tensors."""
    g1 = grad1.flatten()
    g2 = grad2.flatten()
    if g1.numel() != g2.numel():
        return 0.0
    return torch.nn.functional.cosine_similarity(
        g1.unsqueeze(0), g2.unsqueeze(0)
    ).item()


def compute_layer_alignment(
    model: nn.Module,
    target_grad: Tensor | None = None,
) -> dict[str, float]:
    """Compute alignment of each layer's gradient with target (or global)."""
    alignments = {}

    layer_grads = {}
    for name, param in model.named_parameters():
        if param.grad is not None:
            layer_grads[name] = param.grad.detach().flatten()

    if target_grad is None and layer_grads:
        target_grad = torch.cat(list(layer_grads.values()))

    if target_grad is not None:
        for name, grad in layer_grads.items():
            g = grad
            if g.numel() < target_grad.numel():
                g = torch.cat([g, torch.zeros(target_grad.numel() - g.numel())])
            elif g.numel() > target_grad.numel():
                g = g[: target_grad.numel()]

            alignments[name] = compute_gradient_cosine_similarity(g, target_grad)

    return alignments


class GradientStatsAnalyzer:
    """Analyze gradient statistics during training."""

    def __init__(
        self,
        model: nn.Module,
        dataloader,
        device: str = "cpu",
        config: GradientStatsConfig | None = None,
    ):
        self.model = model
        self.dataloader = dataloader
        self.device = device
        self.config = config or GradientStatsConfig()

    def analyze(self) -> GradientStatsResult:
        """Run gradient statistics analysis."""
        return compute_gradient_statistics(
            self.model, self.dataloader, self.device, self.config
        )
