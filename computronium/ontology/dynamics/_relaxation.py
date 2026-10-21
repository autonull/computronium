"""The relaxations a settle performs, in one place (TODO69).

A settle is a loop over a relaxation step, and the step is the system's own
state evolution: the hidden layers move toward what predicts them. The
stability analysis measures that same step — a trajectory, a spectrum and a
basin are all properties of the map the settle iterates — so the step lives
here rather than inside the settle that loops over it. One function, one
place: the picture and the number are pictures of the same thing.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from torch import Tensor


def prediction_relaxation(
    acts: list[Tensor],
    weights: tuple[Tensor, ...],
    recurrent_weight: Tensor | None,
    op: Callable[[Tensor, Tensor], Tensor],
    step_size: float,
) -> tuple[list[Tensor], list[Tensor]]:
    """One step of the layered prediction relaxation.

    Each layer moves toward what predicts it: the layer above predicts the
    layer below, and the error of that prediction is the layer's own share
    of the drive. The input layer is clamped, and the recurrent connection
    is the last hidden layer's own feedback.

    Args:
        acts: The layers, input first.
        weights: The layer weights, bottom-up.
        recurrent_weight: The recurrent connection, when the geometry has one.
        op: The substrate's forward operator.
        step_size: How far a layer moves per step.

    Returns:
        The relaxed layers, and each layer's prediction error.
    """
    new_acts = [acts[0]]
    errors: list[Tensor] = []
    for index, weight in enumerate(weights):
        h_upper = acts[index + 1]
        prediction = op(h_upper, weight.T)
        error = acts[index] - prediction
        errors.append(error)
        new_acts.append(h_upper + step_size * op(error, weight))

    if recurrent_weight is not None and len(new_acts) >= 3:
        hidden = len(new_acts) - 2
        h_hidden = new_acts[hidden]
        new_acts[hidden] = h_hidden + step_size * op(h_hidden, recurrent_weight)

    return new_acts, errors


__all__ = ["prediction_relaxation"]
