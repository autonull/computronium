"""Wire real plasticity primitives into plain-``nn.Module`` benchmark harnesses.

The joint benchmark suites build lightweight models; the 6-D plasticity
primitives speak the ``CompositeState``/``SystemContext`` protocol. This
adapter advances the real plasticity law per batch and modulates hidden
activations, so suite results condition on the P-axis coordinate instead
of measuring the same vanilla network for every arm (TODO16 Phase 5
defect: identical metrics across coordinates).
"""

from __future__ import annotations

from typing import Any

import torch
from torch import Tensor

from computronium.state.composite import CompositeState


class _HarnessContext:
    """Minimal SystemContext stand-in.

    The plasticity laws read only ``context.theta`` (to decide
    differentiable vs hard selection); ``theta`` must contain at least
    one ``requires_grad`` parameter during training.
    """

    def __init__(self, params: dict[str, Tensor]) -> None:
        self.theta = params


def step_psi(
    plasticity: Any,
    psi: dict[str, Tensor],
    x: Tensor,
    y: Tensor | None = None,
    training: bool = False,
    live_param: Tensor | None = None,
) -> dict[str, Tensor]:
    """Advance the plasticity law one step on harness activity.

    Args:
        plasticity: Primitive exposing the initial_psi/step protocol.
        psi: Current plastic state (from ``initial_psi``).
        x: Batch input activity, [batch, ...].
        y: Optional post activity (Hebbian pre/post pair for fast weights).
        training: True during harness training (differentiable selection).
        live_param: A model parameter; only its ``requires_grad`` flag is
            read, so any live parameter works.
    """
    activity: dict[str, Any] = {"x": x}
    if y is not None:
        activity["y"] = y
    z = CompositeState(activity=activity, plastic={}, substrate={})
    psi = {k: v.to(x.device) for k, v in psi.items()}
    for m in vars(plasticity).values():
        if isinstance(m, torch.nn.Module):
            m.to(x.device)
    theta = {"live": live_param} if live_param is not None else {}
    return plasticity.step(psi, z, _HarnessContext(theta))


def modulate_hidden(
    plasticity: Any, activations: Tensor, psi: dict[str, Tensor]
) -> Tensor:
    """Apply the primitive's modulation to hidden activations (no-op for
    primitives without a ``modulate`` operator, e.g. Null)."""
    modulate = getattr(plasticity, "modulate", None)
    if modulate is None or not psi:
        return activations
    out = modulate(activations, psi)
    return out if isinstance(out, Tensor) else activations
