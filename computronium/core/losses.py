"""Shared loss and accuracy utilities.

Consolidates duplicate implementations from ``core/trainer.py`` and
``graph/training.py`` into a single canonical source, and declares the loss
inventory every task's ``compute_loss`` must come from (TODO91 S4).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Final, Literal

import torch
from torch import nn

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

__all__ = [
    "LOSS_INVENTORY",
    "LossKind",
    "LossSpec",
    "accuracy_tensor",
    "compute_accuracy",
    "compute_loss",
    "cross_entropy",
    "fold_time",
    "mean_squared_error",
    "perplexity",
    "reshape_for_cross_entropy",
]


class LossKind(StrEnum):
    """The loss families a task may optimize."""

    CROSS_ENTROPY = "cross_entropy"
    MEAN_SQUARED_ERROR = "mean_squared_error"


@dataclass(frozen=True, slots=True)
class LossSpec:
    """One declared loss: its rule, the target it reads, and what it emits."""

    kind: LossKind
    fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor]
    target: Literal["class_index", "continuous"]
    metric_keys: tuple[str, ...]
    notes: str


def cross_entropy(logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    """Softmax cross-entropy over class indices."""
    return torch.nn.functional.cross_entropy(logits, targets)


def mean_squared_error(preds: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
    """Mean squared error over a continuous, value-valued target."""
    return torch.nn.functional.mse_loss(preds, targets.float())


# The one declared loss inventory: a task's ``loss_kind`` names a row here, and
# ``tests/property/test_loss_inventory_lock.py`` fails when a task computes a
# loss its row does not describe. A new objective is a new row, not an override.
LOSS_INVENTORY: Final[Mapping[LossKind, LossSpec]] = {
    LossKind.CROSS_ENTROPY: LossSpec(
        kind=LossKind.CROSS_ENTROPY,
        fn=cross_entropy,
        target="class_index",
        metric_keys=("loss", "val_loss", "val_acc"),
        notes="The target is a class index; accuracy is the match rate.",
    ),
    LossKind.MEAN_SQUARED_ERROR: LossSpec(
        kind=LossKind.MEAN_SQUARED_ERROR,
        fn=mean_squared_error,
        target="continuous",
        metric_keys=("loss", "val_loss", "mse"),
        notes=(
            "The target is a value; accuracy is undefined, so the loss is the "
            "primary number and its ruler is the task's target variance."
        ),
    ),
}


def perplexity(val_loss: float) -> float:
    """Exponentiate a mean cross-entropy into perplexity.

    A diverged arm (val_loss large enough to overflow ``exp``) yields
    ``float('inf')`` — the divergence sentinel — instead of an
    overflow artifact (TODO13 §7 evidence hygiene).
    """
    ppl = torch.exp(torch.tensor(min(val_loss, 1e4))).item()
    return ppl if math.isfinite(ppl) else float("inf")


def reshape_for_cross_entropy(
    logits: torch.Tensor, y: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    """Coerce logits/targets into ``F.cross_entropy`` compatible shapes.

    Models may emit 3-D logits ``[B, L, V]`` (LM autoregressive heads) where
    only the last token's prediction is supervised, and some datasets return
    float ``[B, 1]`` or one-hot targets.  ``F.cross_entropy`` requires logits
    ``[B, C]`` paired with long indices ``[B]``.
    """
    if logits.dim() == 3:
        logits = logits[:, -1, :]
    if y.dim() > 1 and y.size(-1) == 1:
        y = y.squeeze(-1)
    if y.dim() > 1 and y.shape[-1] == logits.shape[-1]:
        y = y.argmax(dim=-1)
    if y.dtype != torch.long:
        y = y.long()
    return logits, y


def fold_time(
    logits: torch.Tensor, y: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    """Fold a time-major head to per-step rows: ``(T, B, C)/(T, B)`` → ``(T·B, C)/(T·B)``.

    A temporal geometry keeps the time axis in its output (TODO93 §19), so
    every step's prediction is supervised. The LM head's ``(B, L, V)`` is a
    different layout and never passes through here: the caller declares the
    sequence geometry, it does not infer the layout from the rank.
    """
    return logits.reshape(-1, logits.shape[-1]), y.reshape(-1)


def compute_loss(
    loss_fn: Callable[..., torch.Tensor] | None,
    logits: torch.Tensor,
    y: torch.Tensor,
) -> torch.Tensor:
    """Compute loss using ``loss_fn`` or fallback cross-entropy.

    Handles 3-D logits (LM autoregressive heads), 2-D targets with singleton
    dimension, and non-long targets.
    """
    if loss_fn is not None:
        loss_input = logits
        loss_target = y
        if logits.dim() == 3:
            loss_input = logits[:, -1, :]
        if isinstance(loss_fn, nn.CrossEntropyLoss):
            if y.dim() > 1 and y.size(-1) == 1:
                loss_target = y.squeeze(-1).long()
            elif y.dtype != torch.long:
                loss_target = y.long()
        return loss_fn(loss_input, loss_target)
    logits_ce, y_ce = reshape_for_cross_entropy(logits, y)
    return torch.nn.functional.cross_entropy(logits_ce, y_ce)


def compute_accuracy(logits: torch.Tensor, y: torch.Tensor, scale: int = 1) -> float:
    """Accuracy via argmax, handling one-hot and reshaped targets.

    Returns a 0-1 ratio by default; pass ``scale=100`` for a percentage.
    """
    logits_ce, y_ce = reshape_for_cross_entropy(logits, y)
    with torch.no_grad():
        return (logits_ce.argmax(1) == y_ce).float().mean().item() * scale


def accuracy_tensor(logits: torch.Tensor, y: torch.Tensor) -> torch.Tensor:
    """Class-match accuracy as a scalar tensor, with an ignore-index sentinel.

    Entries with ``y < 0`` are excluded from both hits and denominator, so a
    full-batch node classification reports accuracy over the labelled nodes.
    A floating-point target declares a regression objective: it has no classes,
    so class-match accuracy is undefined and the result is the declared ``0.0``
    sentinel rather than an argmax over a value vector.
    """
    if y.is_floating_point():
        return torch.zeros((), dtype=logits.dtype, device=logits.device)
    pred = logits.argmax(dim=-1)
    valid = y >= 0
    hits = ((pred == y) & valid).sum()
    return hits.to(logits.dtype) / valid.sum().clamp(min=1).to(logits.dtype)
