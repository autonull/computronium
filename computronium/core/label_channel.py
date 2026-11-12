"""The label-augmented input channel a credit may read its target from.

``local_contrastive`` declares ``label_channel``: it slices the last
``label_dim`` input features as the one-hot target, because under instantaneous
settle the FREE/NUDGED phases are bit-identical at hidden layers and carry no
contrast (measured 2026-09-07). The harness must therefore widen the input layer
by ``label_dim`` and append the target to every batch it presents.

:class:`LabelChannelSystem` is that seam, once. Training batches carry the true
label; inference sweeps every candidate label and scores it with the readout's
own logit for that candidate — the readout is the only supervised discriminator
the credit trains, so the sweep asks the question the readout was trained to
answer, and never sees the true label. ``forward`` therefore returns
``[B, output_dim]`` sweep scores rather than the head's logits for one input.

Nothing else in the pipeline changes: the trainer, ``task.evaluate``, and the
post-training probes all call ``forward``/``train_step``, so the adapter is the
single place the channel exists.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

import torch
import torch.nn.functional as F  # ruff: ignore[lowercase-imported-as-non-lowercase]

if TYPE_CHECKING:
    from torch import Tensor

__all__ = [
    "LabelChannelSystem",
    "augmented_input_shape",
    "label_augmented",
    "probe_input",
]


def augmented_input_shape(
    input_shape: tuple[int, ...], label_dim: int
) -> tuple[int, ...]:
    """The geometry's input shape with the label channel appended.

    The channel is a flat stream — the credit recomputes a linear stack — so a
    task's ``(C, H, W)`` shape becomes its flattened width plus the label.
    """
    if label_dim <= 0:
        return input_shape
    return (math.prod(input_shape) + label_dim,)


def _flat(x: Tensor) -> Tensor:
    return x.reshape(x.size(0), -1) if x.dim() > 2 else x


def label_augmented(x: Tensor, y: Tensor, label_dim: int) -> Tensor:
    """``[x | one_hot(y)]`` over a flat row, as the credit's contract reads it."""
    flat = _flat(x)
    labels = y.reshape(-1)
    if labels.numel() != flat.size(0):
        msg = (
            f"label channel needs one label per row: {labels.numel()} labels "
            f"for {flat.size(0)} rows"
        )
        raise ValueError(msg)
    if labels.is_floating_point() or labels.dtype == torch.bool:
        msg = f"label channel needs integer class indices, got {labels.dtype}"
        raise ValueError(msg)
    if labels.numel() and (int(labels.min()) < 0 or int(labels.max()) >= label_dim):
        msg = (
            f"label channel is {label_dim} wide but labels span "
            f"[{int(labels.min())}, {int(labels.max())}]"
        )
        raise ValueError(msg)
    return torch.cat((flat, F.one_hot(labels, label_dim).to(flat.dtype)), dim=-1)


def probe_input(system: Any, x: Tensor) -> Tensor:
    """``x`` with an all-zero label channel, for label-free diagnostics.

    A zero channel carries no label information, which is what a settle-energy
    or Jacobian probe needs: it measures the geometry at the task's input width
    without pretending to know the class.
    """
    label_dim = getattr(system, "label_dim", 0)
    if not label_dim:
        return x
    flat = _flat(x)
    return torch.cat((flat, flat.new_zeros(flat.size(0), label_dim)), dim=-1)


class LabelChannelSystem:
    """System proxy that appends the label channel and sweeps it at inference.

    Reads and writes delegate to the composed system: this is a seam over its
    data path, not a second place to hold state — a write that landed here
    would silently diverge from the geometry the pipeline uses.
    """

    def __init__(self, inner: Any, *, output_dim: int, label_dim: int) -> None:
        object.__setattr__(self, "_inner", inner)
        object.__setattr__(self, "output_dim", int(output_dim))
        object.__setattr__(self, "label_dim", int(label_dim))

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(self._inner, name, value)

    def __repr__(self) -> str:
        return (
            f"LabelChannelSystem({self._inner!r}, output_dim={self.output_dim}, "
            f"label_dim={self.label_dim})"
        )

    def train_step(self, x: Tensor, y: Tensor, **graph_kwargs: Any) -> dict[str, float]:
        """Train on the true-label-augmented stream (the credit's contract)."""
        return self._inner.train_step(
            label_augmented(x, y, self.label_dim), y, **graph_kwargs
        )

    def forward(self, x: Tensor, *args: Any, **kwargs: Any) -> Tensor:
        """``[B, C]`` scores: the readout's logit for each candidate label."""
        return self._sweep(x, *args, **kwargs)

    def __call__(self, x: Tensor, *args: Any, **kwargs: Any) -> Tensor:
        """Tasks call the system as a module; special methods bypass ``__getattr__``."""
        return self.forward(x, *args, **kwargs)

    def _sweep(self, x: Tensor, *args: Any, **kwargs: Any) -> Tensor:
        flat = _flat(x)
        rows, classes = flat.size(0), self.output_dim
        candidates = torch.arange(classes, device=flat.device)
        # One forward for the whole sweep: the candidate axis rides the batch
        # axis, so inference costs one pass of C·B rows rather than C passes.
        z = label_augmented(
            flat.repeat(classes, 1), candidates.repeat_interleave(rows), self.label_dim
        )
        logits = self._inner.forward(z, *args, **kwargs)
        scores = logits.reshape(classes, rows, classes)[candidates, :, candidates]
        return scores.T
