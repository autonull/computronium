"""Locks for the local supervision credit (TODO93 §19 row 5).

Every hidden layer trains against its own auxiliary head, so no gradient
crosses a layer boundary. The locks are the capability: a hidden layer moves
without the readout, and the readout's weights do not enter its signal.
"""

from __future__ import annotations

import pytest
import torch

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    LocalSupervisionCredit,
    Phase,
)
from computronium.ontology.geometry import GeometryConfig, RecurrentGeometry
from computronium.state import CompositeState

_IN, _HIDDEN, _OUT, _BATCH = 8, 8, 4, 3


def _geometry() -> object:
    from computronium.ontology.geometry import FeedforwardGeometry

    return FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=_IN, output_dim=_OUT, hidden_dims=(_HIDDEN, _HIDDEN)
        )
    )


def _states() -> dict[Phase, CompositeState]:
    generator = torch.Generator().manual_seed(3)
    x = torch.randn((_BATCH, _IN), generator=generator)
    y = torch.randint(0, _OUT, (_BATCH,), generator=generator)
    return {
        Phase.FREE: CompositeState(
            activity={"x": x, "y": y}, plastic={}, substrate={}
        )
    }


def _credit() -> LocalSupervisionCredit:
    return LocalSupervisionCredit(
        CreditAssignmentConfig.local_supervision(aux_head_scale=0.25)
    )


def _grads(geometry, states, credit=None) -> list[torch.Tensor]:
    return (credit or _credit()).compute_pseudo_gradient(states, None, geometry)


def test_a_hidden_layer_trains_without_the_readout_weight() -> None:
    """The readout's weights never enter a hidden layer's signal."""
    geometry = _geometry()
    torch.manual_seed(5)
    states = _states()
    credit = _credit()
    before = _grads(geometry, states, credit)
    readout = geometry._layers[-1]
    with torch.no_grad():
        readout.weight.mul_(0.0)
    after = _grads(geometry, states, credit)
    for measured, expected in zip(before[:-1], after[:-1], strict=True):
        assert torch.allclose(measured, expected, atol=1e-7), (
            "a hidden gradient read the readout weight"
        )


def test_the_auxiliary_gradient_descends_its_own_loss() -> None:
    """One step along the hidden gradient lowers that layer's aux loss."""
    geometry = _geometry()
    credit = _credit()
    states = _states()
    grads = credit.compute_pseudo_gradient(states, None, geometry)
    state = states[Phase.FREE]
    hidden = geometry._layers[0]
    head = credit._aux_heads[0]

    def loss() -> torch.Tensor:
        from computronium.core.losses import cross_entropy

        with torch.no_grad():
            out = torch.relu(state.x @ hidden.weight.T + hidden.bias)
        return cross_entropy(out @ head.T, state.y)

    before = loss()
    with torch.no_grad():
        hidden.weight.sub_(0.5 * grads[0])
    after = loss()
    assert float(after) < float(before), f"{float(before)} -> {float(after)}"


def test_the_credit_refuses_a_non_feedforward_geometry() -> None:
    """A recurrent geometry has no layer stack for a local head."""
    geometry = RecurrentGeometry(
        GeometryConfig.feedforward(
            input_dim=_IN, output_dim=_OUT, hidden_dims=(_HIDDEN,)
        )
    )
    with pytest.raises(TypeError, match="FeedforwardGeometry"):
        _grads(geometry, _states())
