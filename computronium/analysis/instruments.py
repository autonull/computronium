"""Calibrated instruments for the discovery campaign (TODO27 Phase 0.2).

Instruments over narratives: every number a verdict rests on comes from
one of these readers, and each reader carries a self-check against a
system with *known* properties (backprop credit on a shallow net must
read the BP gradient itself — a self-check, not a prior).

- ``credit_trace``: per-weight-layer credit norm + split-half cosine
  reliability + optional BP-reference cosine.
- ``settle_horizon``: steps the dynamics actually used to settle.
"""

from typing import TYPE_CHECKING, Final, cast

import torch
from torch import Tensor

from computronium.core.pipeline import forward_pass, task_loss
from computronium.ontology import Phase, SystemState

if TYPE_CHECKING:
    from computronium.ontology import (
        CreditAssignment,
        Geometry,
        StateDynamics,
        Substrate,
        System,
    )

__all__ = [
    "BP_COSINE_GATE",
    "credit_trace",
    "settle_horizon",
    "settle_phases",
]

#: Identity-card gate: gradient-equivalence for CE losses (GradientCredit).
BP_COSINE_GATE: Final[float] = 0.9


def settle_phases(
    system: System, x: Tensor, y: Tensor
) -> tuple[dict[Phase, SystemState], Tensor | None]:
    """Run the credit's declared settle phases once; return states + output loss."""
    substrate = cast("Substrate", system.substrate)
    geometry = cast("Geometry", system.geometry)
    dynamics = cast("StateDynamics", system.dynamics)
    credit = cast("CreditAssignment", system.credit)

    grad_ctx = torch.enable_grad() if credit.requires_autograd else torch.no_grad()
    states: dict[Phase, SystemState] = {}
    with grad_ctx:
        initial = forward_pass(substrate, geometry, x)
        loss: Tensor | None = None
        for phase in credit.phases:
            state = SystemState(x=x, y=y)
            state.activations = initial
            settled = cast(
                "SystemState",
                dynamics.settle(
                    state,  # type: ignore[arg-type] (duck-typed state)
                    geometry,
                    substrate,
                    target=y if phase is Phase.NUDGED else None,
                ),
            )
            if phase is Phase.NUDGED:
                settled.loss = task_loss(settled, y)
                loss = settled.loss
            settled.energy = dynamics.compute_energy(settled, geometry)  # type: ignore[arg-type]
            states[phase] = settled
    return states, loss


def _layer_cosine(a: Tensor, b: Tensor) -> float:
    a = a.flatten().float()
    b = b.flatten().float()
    denom = a.norm() * b.norm()
    if denom == 0:
        return 0.0
    return float((a @ b / denom).item())


def _weight_names(system: System) -> list[str]:
    return [
        n for n, p in cast("Geometry", system.geometry).params.items() if p.ndim >= 2
    ]


def _bp_reference(system: System, x: Tensor, y: Tensor) -> list[Tensor]:
    """Autograd ∂CE/∂W through a plain routed forward pass (the BP ruler)."""
    geometry = cast("Geometry", system.geometry)
    substrate = cast("Substrate", system.substrate)
    names = _weight_names(system)
    params = [geometry.params[n] for n in names]
    acts = geometry.forward(x, substrate)
    logits = acts[-1] if isinstance(acts, list) else acts
    grads = torch.autograd.grad(
        torch.nn.functional.cross_entropy(logits, y),
        params,
        allow_unused=True,
    )
    return [
        g if g is not None else torch.zeros_like(p)
        for g, p in zip(grads, params, strict=True)
    ]


def credit_trace(
    system: System,
    x: Tensor,
    y: Tensor,
    *,
    bp_reference: bool = False,
) -> dict[str, object]:
    """Read the credit signal for one batch.

    Args:
        system: Composed 5-D system.
        x: Input batch.
        y: Target batch.
        bp_reference: Also report per-layer cosine against the plain-BP
            gradient of the same batch (ruler calibration; the gradient
            credit must read ≈1.0, other families report their deviation).

    Returns:
        ``layer_norms`` (weight-name → L2 norm of the credit pseudo-
        gradient), ``split_half_cosine`` (batch-halves reliability),
        and optionally ``bp_cosine`` per layer plus ``bp_min_cosine``.
    """
    credit = cast("CreditAssignment", system.credit)
    names = _weight_names(system)

    def _trace(xb: Tensor, yb: Tensor) -> dict[str, Tensor]:
        states, loss = settle_phases(system, xb, yb)
        pseudo = credit.compute_pseudo_gradient(states, loss, system.geometry)
        # Some families learn a strict subset of the ≥2-D params (e.g.
        # frozen recurrent matrices); report only what the credit reached.
        return dict(zip(names[: len(pseudo)], pseudo, strict=False))

    full = _trace(x, y)
    if not full:
        raise ValueError(
            "credit_trace read an empty pseudo-gradient: the credit rule "
            "reached no learnable weight on this batch"
        )
    half = x.size(0) // 2
    if half == 0:
        raise ValueError("credit_trace needs batch >= 2 for split-half reliability")
    first = _trace(x[:half], y[:half])
    second = _trace(x[half:], y[half:])

    trace: dict[str, object] = {
        "layer_norms": {n: float(v.norm()) for n, v in full.items()},
        "split_half_cosine": {n: _layer_cosine(first[n], second[n]) for n in full},
    }
    if bp_reference:
        ref_list = _bp_reference(system, x, y)
        ref = dict(zip(names[: len(ref_list)], ref_list, strict=False))
        per_layer = {n: _layer_cosine(full[n], ref[n]) for n in full}
        trace["bp_cosine"] = per_layer
        trace["bp_min_cosine"] = min(per_layer.values())
    return trace


def settle_horizon(system: System, x: Tensor, y: Tensor | None = None) -> int | None:
    """Steps the dynamics used on its last settle (None if untracked)."""
    geometry = cast("Geometry", system.geometry)
    substrate = cast("Substrate", system.substrate)
    dynamics = cast("StateDynamics", system.dynamics)
    state = SystemState(x=x, y=y)
    state.activations = forward_pass(substrate, geometry, x)
    dynamics.settle(state, geometry, substrate, target=y)  # type: ignore[arg-type]
    get_history = getattr(dynamics, "get_free_energy_history", None)
    if get_history is None:
        return None
    history = get_history()
    return len(history) if history is not None else None
