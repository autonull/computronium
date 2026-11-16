"""Activation checkpointing for the backprop arm (TODO93 T4b).

Backprop retains one activation set per layer, so its peak grows as
``c·L·B·W·4``. A checkpointed forward keeps only the *segment boundaries*
(√L tensors) and recomputes each segment inside backward, bending the curve
down in depth. The wrapped unit is the **geometry forward** -- the phase that
holds activations -- never ``system.train_step``: the step also contains the
parameter update, so recomputing it would apply a different (already updated)
``W_ℓ`` and break gradient parity.

Segments split at Linear starts, never inside a ``(Linear, activation)``
block. A residual skip reads the *Linear's input* while a mid-block split
would resume with the activation's input, which is a different tensor; splitting
on Linear starts keeps the block's internal state inside one segment.

``torch.compile`` is not used on the claim path today, so a checkpointed cell
declares ``compiled=False``. If compile is added, it must be disabled for
checkpointed cells or both variants measured and named separately -- checkpoint
and compile both rewrite the backward graph and their interaction is not a
measurement this plan has.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from torch import nn

if TYPE_CHECKING:
    from computronium.ontology import System

__all__ = [
    "GradientCheckpointing",
    "enable_gradient_checkpointing",
    "segments_for_depth",
]


def segments_for_depth(depth: int) -> int:
    """``√L`` segments, clamped to ``[1, L]``.

    ``√L`` is the minimum of (retained boundaries) + (per-segment recompute);
    more segments retain more boundaries, fewer recompute more layers.
    """
    if depth <= 1:
        return 1
    return max(1, min(depth, math.ceil(math.sqrt(depth))))


@dataclass(frozen=True, slots=True)
class GradientCheckpointing:
    """What a checkpointed arm declares in its identity card."""

    segments: int
    compiled: bool = False

    def to_identity(self) -> dict[str, object]:
        """Row fields that make the checkpointed path distinguishable."""
        return {
            "grad_checkpointing_segments": self.segments,
            "compiled": self.compiled,
        }


def enable_gradient_checkpointing(
    system: System, segments: int | None = None
) -> GradientCheckpointing:
    """Turn on activation checkpointing for ``system``'s geometry forward.

    Args:
        system: A composed system whose geometry implements
            ``set_gradient_checkpointing`` (the claim geometry, Linear+ReLU
            feedforward).
        segments: Explicit segment count, or ``None`` for ``√L``.

    Returns:
        The declaration to record beside the cell's metrics.

    Raises:
        TypeError: The geometry has no measured checkpointed path. A refusal
            with a named trigger, not a silent no-op: a cell that claims
            checkpointing and runs uncheckpointed would report the plain arm's
            memory under the recovered arm's name.
    """
    geometry = system.geometry
    setter = getattr(geometry, "set_gradient_checkpointing", None)
    if not callable(setter):
        raise TypeError(
            f"{type(geometry).__name__} has no measured checkpointed forward; "
            "T4b covers FeedforwardGeometry only. Add the path and a parity "
            "lock before routing a cell here."
        )
    if not getattr(getattr(system, "credit", None), "requires_autograd", False):
        raise TypeError(
            "gradient checkpointing is the backprop arm's instrument; a credit "
            "that does not declare requires_autograd holds no graph to recompute. "
            "Its segment-boundary activation list would silently change what the "
            "credit reads."
        )
    depth = sum(
        1
        for module in getattr(geometry, "_layers", ())
        if isinstance(module, nn.Linear)
    ) or len(getattr(geometry, "_layers", ()))
    resolved = segments_for_depth(depth) if segments is None else max(1, segments)
    setter(resolved)
    return GradientCheckpointing(segments=resolved)
