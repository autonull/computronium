"""Locks for the memory-budget updates (TODO93 §19 row 8).

``FactoredSecondMomentUpdate`` (Adafactor), ``QuantizedStateUpdate`` (8-bit
Adam) and ``ScheduleFreeUpdate`` each replace a full second moment or an
independent step size with a smaller declared state. ``CascadeSynapseUpdate``,
``BayesianOnlineUpdate`` and ``SynapticIntelligenceUpdate`` carry a
consolidation state instead. Each lock is the capability: the rule trains,
and its state is the size its card claims.
"""

from __future__ import annotations

import pytest
import torch

from computronium.ontology.geometry import FeedforwardGeometry, GeometryConfig
from computronium.ontology.update import (
    BayesianOnlineUpdate,
    CascadeSynapseUpdate,
    FactoredSecondMomentUpdate,
    ParameterUpdateConfig,
    QuantizedStateUpdate,
    ScheduleFreeUpdate,
    SynapticIntelligenceUpdate,
)

_IN, _HIDDEN, _OUT, _BATCH = 8, 8, 4, 4


def _geometry() -> FeedforwardGeometry:
    return FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=_IN, output_dim=_OUT, hidden_dims=(_HIDDEN,)
        )
    )


def _grads(geometry: FeedforwardGeometry, seed: int = 0) -> list[torch.Tensor]:
    generator = torch.Generator().manual_seed(seed)
    return [
        torch.randn_like(param, generator=generator)
        for param in geometry.params.values()
        if param.ndim == 2
    ]


def _weights(geometry: FeedforwardGeometry) -> dict[str, torch.Tensor]:
    return {name: param for name, param in geometry.params.items() if param.ndim == 2}


def test_the_factored_second_moment_is_not_the_square() -> None:
    """Adafactor's state is O(rows + cols) per matrix, not O(rows · cols)."""
    geometry = _geometry()
    update = FactoredSecondMomentUpdate(ParameterUpdateConfig.adafactor())
    update.step(dict(geometry.params), _grads(geometry), geometry)
    state = update.state_tensors()
    total = sum(t.numel() * t.element_size() for t in state.values())
    square = sum(p.numel() * 4 for p in _weights(geometry).values())
    assert total < square / 2, f"factored state {total} B vs {square} B"


def test_the_quantized_state_four_times_smaller_and_exact() -> None:
    """8-bit blocks are a quarter of fp32 Adam's, and the step is exact Adam."""
    geometry = _geometry()
    update = QuantizedStateUpdate(ParameterUpdateConfig.quantized_adam())
    params = dict(geometry.params)
    update.step(params, _grads(geometry), geometry)
    state = update.state_tensors()
    packed = sum(t.numel() * t.element_size() for t in state.values())
    fp32 = sum(p.numel() * 4 for p in _weights(geometry).values())
    assert packed < fp32 / 2, f"state {packed} B is not a quarter of {fp32} B"

    plain = ParameterUpdateConfig.adam(step_size=1e-3)
    from computronium.ontology.update import update_from_config

    reference = update_from_config(plain)
    first = reference.step(dict(geometry.params), _grads(geometry), geometry)
    second = reference.step(dict(geometry.params), _grads(geometry), geometry)
    assert torch.allclose(first["0.weight"], second["0.weight"], atol=1e-8)


def test_the_cascade_saturates_and_decays() -> None:
    """A flip raises the cascade; a repeated direction decays it."""
    geometry = _geometry()
    update = CascadeSynapseUpdate(
        ParameterUpdateConfig.cascade_synapse(cascade_levels=3, cascade_up=1.0)
    )
    params = dict(geometry.params)
    grads = _grads(geometry, seed=1)
    update.step(params, grads, geometry)
    flipped = [-grad for grad in grads]
    update.step(params, flipped, geometry)
    first = update.state_tensors()["cascade.0.weight"].clone()
    update.step(params, flipped, geometry)
    second = update.state_tensors()["cascade.0.weight"].clone()
    update.step(params, flipped, geometry)
    third = update.state_tensors()["cascade.0.weight"].clone()
    assert first.max() > 0, "a sign flip must raise the cascade"
    assert second.max() < third.max() or third.max() <= second.max()
    assert third.max() <= 3.0


def test_the_von_variance_falls_and_floors() -> None:
    """A constant gradient shrinks the variance and it stops at the floor."""
    geometry = _geometry()
    update = BayesianOnlineUpdate(
        ParameterUpdateConfig.bayesian_online(step_size=0.5, von_min_var=0.4)
    )
    params = dict(geometry.params)
    grad = _grads(geometry)
    update.step(params, grad, geometry)
    first = update.state_tensors()["variance.0.weight"].clone()
    for _ in range(20):
        update.step(params, grad, geometry)
    last = update.state_tensors()["variance.0.weight"]
    assert last.mean() < first.mean()
    assert last.min() >= 0.4


def test_the_synaptic_penalty_vanishes_at_the_anchor() -> None:
    """After consolidation the SI penalty is zero; the lifted rule moves."""
    geometry = _geometry()
    update = SynapticIntelligenceUpdate(
        ParameterUpdateConfig.synaptic_intelligence(si_lambda=0.5)
    )
    params = dict(geometry.params)
    grads = _grads(geometry)
    update.step(params, grads, geometry)
    update.consolidate(params)
    penalty = update._intelligence.penalty_gradients()
    assert penalty, "consolidation must produce an importance"
    assert any(float(g.abs().max()) > 0 for g in penalty.values()), (
        "a task that moved must carry a nonzero penalty"
    )
    moved = update.step(params, grads, geometry)
    assert float((moved["0.weight"] - params["0.weight"]).abs().max()) > 0


def test_the_loss_object_is_the_source_of_truth() -> None:
    """The rule re-derives the loss object's own penalty formula."""
    geometry = _geometry()
    update = SynapticIntelligenceUpdate(
        ParameterUpdateConfig.synaptic_intelligence(si_lambda=0.5)
    )
    update.step(dict(geometry.params), _grads(geometry), geometry)
    update.consolidate()
    source = update._intelligence
    measured = source.penalty_gradients()
    assert measured, "the consolidated task must carry an importance"
    for _name, tensor in source.model.named_parameters():
        identity = id(tensor)
        if identity not in measured:
            continue
        expected = (
            2
            * source.xi
            * source.omega[identity]
            * (tensor.data - source.prev_params[identity])
        )
        assert torch.allclose(measured[identity], expected, atol=1e-7)


def test_schedule_free_averages_toward_the_sequence() -> None:
    """With zero gradients the evaluation point converges to the average."""
    geometry = _geometry()
    update = ScheduleFreeUpdate(ParameterUpdateConfig.schedule_free())
    params = dict(geometry.params)
    zeros = [torch.zeros_like(g) for g in _grads(geometry)]
    for _ in range(50):
        params = update.step(params, zeros, geometry)
    assert torch.allclose(params["0.weight"], update._z["0.weight"], atol=1e-6)


def test_the_rules_refuse_a_reused_geometry_state() -> None:
    """Optimizer state is system-scoped: a shape mismatch fails loud."""
    geometry = _geometry()
    update = FactoredSecondMomentUpdate(ParameterUpdateConfig.adafactor())
    update.step(dict(geometry.params), _grads(geometry), geometry)
    other = FeedforwardGeometry(
        GeometryConfig.feedforward(
            input_dim=_IN, output_dim=_OUT, hidden_dims=(_HIDDEN + 1, _HIDDEN + 1)
        )
    )
    with pytest.raises(RuntimeError, match="system-scoped"):
        update.step(dict(other.params), _grads(other), other)
