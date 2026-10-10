"""Weight Evolution Analysis (Phase D3).

Tracks weight evolution: spectral norm, effective rank, and plasticity metrics
across training.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
import torch

if TYPE_CHECKING:
    from torch import Tensor, nn


@dataclass(frozen=True, slots=True)
class WeightEvolutionResult:
    """Result of weight evolution analysis."""

    spectral_norms: dict[str, list[float]]  # layer -> list of norms per epoch
    effective_ranks: dict[str, list[float]]  # layer -> list of effective ranks
    plasticity_metrics: dict[str, list[float]]  # layer -> plasticity over time
    weight_distances: dict[str, list[float]]  # layer -> distance from init
    metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class WeightEvolutionConfig:
    """Configuration for weight evolution analysis."""

    track_every_n_epochs: int = 1
    max_layers: int = 20
    rank_threshold: float = 0.99


def compute_weight_spectral_norm(
    weight: Tensor,
) -> float:
    """Compute spectral norm (largest singular value) of a weight matrix."""
    if weight.dim() < 2:
        return float(weight.norm().item())
    try:
        svals = torch.linalg.svdvals(weight)
        return float(svals[0].item())
    except Exception:
        return float(weight.norm().item())


def compute_effective_rank(
    weight: Tensor,
    threshold: float = 0.99,
) -> float:
    """Compute effective rank: number of singular values needed to

    capture threshold of total.
    """
    if weight.dim() < 2:
        return 1.0
    try:
        svals = torch.linalg.svdvals(weight)
        svals_np = svals.cpu().numpy()
        cumsum = np.cumsum(svals_np) / np.sum(svals_np)
        effective_rank = int(np.searchsorted(cumsum, threshold)) + 1
        return float(effective_rank)
    except Exception:
        return float(min(weight.shape))


def compute_plasticity_metrics(
    weight: Tensor,
    weight_init: Tensor | None = None,
) -> dict[str, float]:
    """Compute plasticity metrics for a weight matrix."""
    metrics = {}

    # Distance from initialization
    if weight_init is not None:
        dist = (weight - weight_init).norm().item()
        metrics["distance_from_init"] = float(dist)
        rel_dist = dist / (weight_init.norm().item() + 1e-8)
        metrics["relative_distance"] = float(rel_dist)

    # Spectral norm
    metrics["spectral_norm"] = compute_weight_spectral_norm(weight)

    # Effective rank
    metrics["effective_rank"] = compute_effective_rank(weight)

    # Frobenius norm
    metrics["frobenius_norm"] = float(weight.norm().item())

    # Condition number (ratio of max/min singular value)
    if weight.dim() >= 2:
        try:
            svals = torch.linalg.svdvals(weight)
            if svals[-1] > 1e-8:
                metrics["condition_number"] = float((svals[0] / svals[-1]).item())
            else:
                metrics["condition_number"] = float("inf")
        except Exception:
            metrics["condition_number"] = float("inf")

    return metrics


class WeightEvolutionAnalyzer:
    """Track weight evolution across training epochs."""

    def __init__(
        self,
        model: nn.Module,
        config: WeightEvolutionConfig | None = None,
    ):
        self.model = model
        self.config = config or WeightEvolutionConfig()
        self._initial_weights: dict[str, Tensor] = {}
        self._history: dict[str, list[dict[str, float]]] = {}

    def snapshot(self, epoch: int) -> None:
        """Record weight snapshot at current epoch."""
        if epoch % self.config.track_every_n_epochs != 0:
            return

        for name, param in self.model.named_parameters():
            if len(self._initial_weights) < self.config.max_layers:
                if name not in self._initial_weights:
                    self._initial_weights[name] = param.detach().clone().cpu()

            weight = param.detach().cpu()
            metrics = compute_plasticity_metrics(
                weight, self._initial_weights.get(name)
            )

            if name not in self._history:
                self._history[name] = []

            metrics["epoch"] = float(epoch)
            self._history[name].append(metrics)

    def get_results(self) -> WeightEvolutionResult:
        """Get compiled results."""
        spectral_norms = {}
        effective_ranks = {}
        plasticity_metrics = {}
        weight_distances = {}

        for name, history in self._history.items():
            spectral_norms[name] = [h.get("spectral_norm", 0.0) for h in history]
            effective_ranks[name] = [h.get("effective_rank", 0.0) for h in history]
            plasticity_metrics[name] = [
                h.get("distance_from_init", 0.0) for h in history
            ]
            weight_distances[name] = [h.get("distance_from_init", 0.0) for h in history]

        return WeightEvolutionResult(
            spectral_norms=spectral_norms,
            effective_ranks=effective_ranks,
            plasticity_metrics=plasticity_metrics,
            weight_distances=weight_distances,
            metadata={
                "n_layers_tracked": len(self._history),
                "track_every_n_epochs": self.config.track_every_n_epochs,
            },
        )

    def reset(self) -> None:
        """Reset analyzer state."""
        self._initial_weights = {}
        self._history = {}
