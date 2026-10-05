"""The settle step as a differentiable operator, for stability metrics.

The stability of a relaxing system is a property of one relaxation step, not
of the whole settle. A loop that runs ``N`` steps composes the step Jacobian
``N`` times, so a genuinely contracting ``rho=0.9`` at ``N=30`` measures
``0.9**30 = 4e-2``: a *contraction* reads as a *collapse*, and a transient
amplification ``sigma_max > 1`` is invisible because it decays below 1 by the
time the loop ends. That is what TODO51 §2 measured: ``rho=0.0087`` on a cell
whose step operator is ``rho=0.997, sigma_max=1.003`` — the frontier's whole
subject (contracting yet transiently amplifying) was erased by the horizon.

So this module exposes the step. ``settle_step_operator`` returns a callable
over the flattened hidden activation stack, which the caller differentiates.
The hidden stack is the state the step actually updates: the input is re-read
every step, and the output layer is recomputed from it rather than relaxed
against.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

import torch
from torch import Tensor

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["hidden_stack_operator", "layer_weight_shapes", "settle_step_operator"]


def _layered(geometry: Any) -> Any:
    """The geometry's linear layer stack, or ``None`` if it has none.

    Read through ``extract_layered_params`` because that is the one place the
    "is this geometry layered?" question is answered — a second reader is how
    tile geometries end up half-supported by the metrics path.
    """
    from computronium.ontology._settle_kernel import extract_layered_params

    return extract_layered_params(geometry)


def _initial_acts(system: Any, x: Tensor) -> list[Tensor]:
    """One sample's activation stack, on the geometry's device.

    The caller's batch is moved to the device the weights are on, not assumed
    to be there: the evaluator is called from thread pools whose device differs
    from the one the system was built on.
    """
    geometry = system.geometry
    device = next(geometry.parameters()).device
    sample = x[:1].to(device)
    builder = getattr(geometry, "settle_blocks", None)
    acts = (
        builder(sample, system.substrate)
        if callable(builder)
        else geometry.forward_with_intermediates(sample, system.substrate)
    )
    return [a[:1] for a in cast("list[Tensor]", acts)]


def hidden_stack_operator(
    system: Any,
    x: Tensor,
) -> Callable[[Tensor], Tensor] | None:
    """One settle step as a map on the flattened hidden stack.

    Args:
        system: The composed cell's system.
        x: A batch; one sample is taken from it.

    Returns:
        ``h -> h'`` for the flattened hidden activations, or ``None`` when the
        geometry is not layered (nothing to relax, so nothing to measure).
    """
    from computronium.ontology._settle_kernel import SubstrateSettleKernel

    params = _layered(system.geometry)
    if params is None:
        return None
    config = system.dynamics.config
    kernel = SubstrateSettleKernel(
        substrate=system.substrate,
        params=params,
        step_size=config.step_size,
        momentum=config.momentum,
        residual=params.residual,
    )

    base = _initial_acts(system, x)
    hidden = base[1:-1]
    if not hidden:
        return None
    widths = tuple(h.shape[1] for h in hidden)

    def step(flat: Tensor) -> Tensor:
        acts = [base[0]]
        offset = 0
        for width in widths:
            acts.append(flat[offset : offset + width].unsqueeze(0))
            offset += width
        acts.append(base[-1])
        advanced, _ = kernel.step(acts, 0.0, None, None)
        return torch.cat([h[0] for h in advanced[1:-1]])

    return step


def settle_step_operator(
    system: Any,
    x: Tensor,
) -> tuple[Callable[[Tensor], Tensor], int] | None:
    """``(step operator, hidden width)``, or ``None`` if not layered."""
    step = hidden_stack_operator(system, x)
    if step is None:
        return None
    return step, sum(h.shape[1] for h in _initial_acts(system, x)[1:-1])


def layer_weight_shapes(geometry: Any) -> list[tuple[int, int]]:
    """``(out_features, in_features)`` per linear layer, in forward order.

    The real shapes, so a substrate's per-MAC energy model sees the arithmetic
    the cell actually performs. A single hardcoded ``(out, in)`` reports the
    same joules for every cell, which is how a constant reached five records
    with 36k parameters and five with 305k.
    """
    params = _layered(geometry)
    if params is None:
        return []
    shapes = [
        (int(w.shape[0]), int(w.shape[1]))
        for w in params.weights
        if isinstance(w, Tensor)
    ]
    recurrent = params.recurrent_weight
    if isinstance(recurrent, Tensor):
        shapes.append((int(recurrent.shape[0]), int(recurrent.shape[1])))
    return shapes
