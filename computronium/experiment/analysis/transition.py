"""The system's own transition (TODO69).

The stability machinery measures a *map*. A trajectory is a sequence of
states; a Lyapunov exponent is the growth of a perturbation along that
sequence; a basin is the set of states the map carries to one attractor.
None of those is a property of a set of weights — they are properties of the
map the system actually performs.

The first version of this measured the identity. The forward pass was
computed and thrown away, and the settle was handed the activity the state
already had, so a feedforward cell's "dynamics" was the identity map and its
Lyapunov spectrum was a row of zeros: a picture of nothing, drawn
confidently.

So the transition here is the system's own relaxation: one step of the settle
kernel the EqProp settle performs, over the cell's own activity, with the
input clamped exactly as the settle clamps it. The cell's state is
everything above the input — the hidden layers and the readout — and the
map carries it from one step to the next.

One function, in one place, read by the command and by the dashboard: the
two cannot disagree about what a cell's dynamics are, and a picture of the
dynamics and a number from the command are pictures of the same thing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import torch

if TYPE_CHECKING:
    from collections.abc import Callable

    from stability.state import CompositeState, SystemContext
    from torch import Tensor

# The key the cell's activity is carried under. The stability estimators
# perturb and monitor this one key, so it has to be the whole state.
ACTIVITY_KEY = "x"

# How many relaxation steps a cell is given to reach its attractor.
DEFAULT_STEPS = 60


@dataclass(frozen=True, slots=True)
class CellTransition:
    """A cell's own state evolution: the map, where it starts, and what it is.

    Attributes:
        step: The map: one relaxation step of the system's own settle.
        initial: The state the map starts from — the system's own forward
            pass, with the input clamped as the settle clamps it.
        stateful: Whether the cell has a state that moves. A feedforward cell
            has none, and saying so is more useful than a picture of nothing.
        reason: Why the transition is what it is, in one sentence.
        widths: The width of each layer the state carries, input excluded.
        clamped: The input the settle clamps, or ``None`` when the cell has
            no state to relax.
    """

    step: Callable[[CompositeState, SystemContext], CompositeState]
    initial: CompositeState
    stateful: bool
    reason: str
    widths: tuple[int, ...]
    clamped: Tensor | None = None

    @property
    def width(self) -> int:
        """The width of the packed state: the cell's activity, one column each."""
        return sum(self.widths)

    def layers(self, state: CompositeState) -> list[Tensor]:
        """The cell's own activity, layer by layer, as the state carries it."""
        packed = state.activity[ACTIVITY_KEY]
        if not isinstance(packed, torch.Tensor):
            msg = f"the state must carry a tensor under {ACTIVITY_KEY!r}"
            raise TypeError(msg)
        return list(torch.split(packed, list(self.widths), dim=-1))

    def pack(self, layers: list[Tensor]) -> Tensor:
        """The cell's own activity, layer by layer, as the state carries it."""
        return torch.cat(layers, dim=-1)

    def energy(self, system: Any, state: CompositeState) -> float:
        """The system's own energy of a state, in the system's own units.

        The energy is the one the cell's own dynamics compute; a landscape
        drawn over any other energy is a picture of a different system.
        """
        from computronium.ontology import SystemState

        if self.clamped is None:
            return 0.0
        acts = [self.clamped, *self.layers(state)]
        settled = SystemState(x=self.clamped, y=None, activations=acts)
        return float(system.dynamics.compute_energy(settled, system.geometry).item())


def build_transition(system: Any, sample_x: Tensor) -> CellTransition:
    """The cell's own transition, and the state it starts from.

    The map is the relaxation the cell's own settle performs, one step at a
    time. A dynamics that has no relaxation — an instantaneous pass, say —
    has no state that moves, and the transition says so rather than
    measuring the identity.

    Args:
        system: The composed cell: its substrate, geometry and dynamics.
        sample_x: One batch of the task's own input, to drive the forward
            pass that starts the state.

    Returns:
        The transition, its initial state, and whether the cell has a state
        that moves at all.
    """
    from stability.state import CompositeState

    from computronium.ontology._settle_kernel import extract_layered_params

    params = extract_layered_params(system.geometry)
    x = sample_x.flatten(1) if sample_x.dim() > 2 else sample_x
    # The cell may live on another device than the sample that drives it:
    # the command composes the cell onto the device it was asked for and
    # reads the data from a loader that hands back the host's tensors.
    weights = next(iter(system.geometry.parameters()), None)
    if weights is not None:
        x = x.to(weights.device)

    if params is None or not params.transitions:
        return _still(system, x, "its geometry has no layers to relax")

    # The system's own forward pass: the input, and the activity above it.
    acts = list(system.geometry.forward_with_intermediates(x, system.substrate))
    if len(acts) != len(params.weights) + 1:
        msg = (
            f"the forward pass gave {len(acts)} layers for "
            f"{len(params.weights)} weights; the cell's layers do not line up"
        )
        raise ValueError(msg)

    clamped = acts[0]
    state_layers = acts[1:]
    widths = tuple(int(layer.shape[-1]) for layer in state_layers)
    initial = CompositeState(
        activity={ACTIVITY_KEY: torch.cat(state_layers, dim=-1)},
        plastic={},
        substrate={},
    )

    relax = _relaxation_for(system)
    if relax is None:
        return _still(
            system,
            x,
            f"its dynamics ({system.dynamics.config.dynamics_type}) has no "
            "relaxation the dashboard can step",
            initial=initial,
            widths=widths,
        )

    def step(state: CompositeState, context: Any) -> CompositeState:
        """One relaxation step of the system's own settle."""
        packed = state.activity[ACTIVITY_KEY]
        if not isinstance(packed, torch.Tensor):
            msg = f"the state must carry a tensor under {ACTIVITY_KEY!r}"
            raise TypeError(msg)
        layers = list(torch.split(packed, list(widths), dim=-1))
        with torch.no_grad():
            new_layers = relax([clamped, *layers])
        return CompositeState(
            activity={ACTIVITY_KEY: torch.cat(new_layers[1:], dim=-1)},
            plastic={},
            substrate={},
        )

    return CellTransition(
        step=step,
        initial=initial,
        stateful=True,
        reason=(
            "One step of the cell's own settle: the hidden layers and the "
            "readout relax, with the input clamped as the settle clamps it."
        ),
        widths=widths,
        clamped=clamped,
    )


def _relaxation_for(system: Any) -> Callable[[list[Tensor]], list[Tensor]] | None:
    """The cell's own relaxation, as a map from the layer stack to itself.

    Each dynamics relaxes its state in its own way, and the map has to be
    that one: a relaxation borrowed from another dynamics measures a system
    that does not exist.
    """
    from computronium.ontology._settle_kernel import (
        SubstrateSettleKernel,
        extract_layered_params,
    )
    from computronium.ontology.dynamics._relaxation import prediction_relaxation

    kind = system.dynamics.config.dynamics_type
    params = extract_layered_params(system.geometry)
    if params is None:
        return None
    op = system.substrate.get_forward_operator()

    if kind == "energy_minimization":
        kernel = SubstrateSettleKernel(
            substrate=system.substrate,
            params=params,
            step_size=system.dynamics.config.step_size,
            momentum=0.0,
            residual=params.residual,
        )

        def relax(acts: list[Tensor]) -> list[Tensor]:
            new_acts, _ = kernel.step(acts, 0.0, None, None)
            return new_acts

        return relax

    if kind == "predictive_settling":
        step_size = system.dynamics.config.step_size

        def relax(acts: list[Tensor]) -> list[Tensor]:
            new_acts, _ = prediction_relaxation(
                acts, params.weights, params.recurrent_weight, op, step_size
            )
            return new_acts

        return relax

    return None


def _still(
    system: Any,
    x: Tensor,
    why: str,
    *,
    initial: CompositeState | None = None,
    widths: tuple[int, ...] | None = None,
) -> CellTransition:
    """A cell that has no state to move: the map that does nothing."""
    from stability.state import CompositeState

    state = initial or CompositeState(
        activity={ACTIVITY_KEY: x}, plastic={}, substrate={}
    )
    return CellTransition(
        step=_identity_step,
        initial=state,
        stateful=False,
        reason=f"This cell has no state that moves: {why}.",
        widths=widths or (int(x.shape[-1]),),
    )


def _identity_step(state: CompositeState, context: Any) -> CompositeState:
    """The map of a cell that has no state: it does not move."""
    return state


__all__ = [
    "ACTIVITY_KEY",
    "DEFAULT_STEPS",
    "CellTransition",
    "build_transition",
]
