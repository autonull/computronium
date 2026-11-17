"""Locks for the temporal credits (TODO93 §19 rows 6).

``EligibilityPropCredit`` (e-prop) and ``UnbiasedOnlineRTRLCredit`` (UORO)
both estimate the exact RTRL Jacobian; ``RTRLReference`` is the fixture the
two are checked against. The locks are the capability: each rule trains a
recurrent cell, and its estimate is compared to the exact gradient at a
declared fixture.
"""

from __future__ import annotations

import pytest
import torch

from computronium.ontology.credit import (
    CreditAssignmentConfig,
    EligibilityPropCredit,
    Phase,
    RTRLReference,
    UnbiasedOnlineRTRLCredit,
)
from computronium.ontology.geometry import GeometryConfig, RecurrentGeometry
from computronium.state import CompositeState

_IN, _HIDDEN, _CLASSES, _TIME, _BATCH = 3, 4, 2, 2, 2


def _geometry() -> RecurrentGeometry:
    return RecurrentGeometry(
        GeometryConfig.feedforward(
            input_dim=_IN,
            output_dim=_CLASSES,
            hidden_dims=(_HIDDEN,),
            init_scale=0.3,
        )
    )


def _sequence(geometry: RecurrentGeometry) -> tuple[torch.Tensor, torch.Tensor]:
    generator = torch.Generator().manual_seed(7)
    x = torch.randn((_TIME, _BATCH, _IN), generator=generator)
    y = torch.randint(0, _CLASSES, (_TIME, _BATCH), generator=generator)
    return x, y


def _states(x: torch.Tensor, y: torch.Tensor) -> dict[Phase, CompositeState]:
    return {
        Phase.FREE: CompositeState(
            activity={"x": x, "y": y}, plastic={}, substrate={}
        )
    }


def _bptt(
    geometry: RecurrentGeometry, x: torch.Tensor, y: torch.Tensor
) -> list[torch.Tensor]:
    """The exact gradient by backpropagation through time (the reference)."""
    from computronium.core.losses import cross_entropy

    linear_in = geometry._layers[0]
    linear_out = geometry._layers[2]
    bias = linear_in.bias.detach()
    bias_out = linear_out.bias.detach()
    weight_in = linear_in.weight.detach().clone().requires_grad_(True)
    weight_out = linear_out.weight.detach().clone().requires_grad_(True)
    recurrent = geometry._recurrent_weight.detach().clone().requires_grad_(True)
    h = torch.zeros((_BATCH, _HIDDEN))
    logits = []
    for step in range(_TIME):
        h = torch.tanh(x[step] @ weight_in.T + h @ recurrent.T + bias)
        logits.append(h @ weight_out.T + bias_out)
    loss = cross_entropy(
        torch.stack(logits).reshape(-1, _CLASSES), y.reshape(-1)
    )
    grads = torch.autograd.grad(loss, (weight_in, weight_out, recurrent))
    return list(grads)


def _grads(credit, geometry, states) -> list[torch.Tensor]:
    return credit.compute_pseudo_gradient(states, None, geometry)


def test_the_recurrent_reference_is_backpropagation_through_time() -> None:
    """RTRL's exact Jacobian equals BPTT on the same cell."""
    geometry = _geometry()
    x, y = _sequence(geometry)
    reference = _bptt(geometry, x, y)
    exact = _grads(
        RTRLReference(CreditAssignmentConfig.rtrl_reference()),
        geometry,
        _states(x, y),
    )
    for measured, expected in zip(exact, reference, strict=True):
        assert torch.allclose(measured, expected, atol=1e-6), (
            f"RTRL {measured} != BPTT {expected}"
        )


def test_e_prop_is_exact_on_a_one_step_fixture() -> None:
    """A one-step trace with no decay is the exact Jacobian."""
    geometry = _geometry()
    generator = torch.Generator().manual_seed(11)
    x = torch.randn((1, _BATCH, _IN), generator=generator)
    y = torch.randint(0, _CLASSES, (1, _BATCH), generator=generator)
    exact = _grads(
        RTRLReference(CreditAssignmentConfig.rtrl_reference()),
        geometry,
        _states(x, y),
    )
    traced = _grads(
        EligibilityPropCredit(
            CreditAssignmentConfig.eligibility_prop(trace_decay=0.0)
        ),
        geometry,
        _states(x, y),
    )
    for measured, expected in zip(traced, exact, strict=True):
        assert torch.allclose(measured, expected, atol=1e-6)


def test_uoro_is_unbiased_over_its_draws() -> None:
    """The mean over 128 sign/row draws matches the exact Jacobian."""
    geometry = _geometry()
    x, y = _sequence(geometry)
    exact = _grads(
        RTRLReference(CreditAssignmentConfig.rtrl_reference()),
        geometry,
        _states(x, y),
    )
    draws = [
        _grads(
            UnbiasedOnlineRTRLCredit(
                CreditAssignmentConfig.unbiased_rtrl(uoro_seed=seed)
            ),
            geometry,
            _states(x, y),
        )
        for seed in range(128)
    ]
    for index, expected in enumerate(exact):
        estimate = torch.stack([draw[index] for draw in draws]).mean(dim=0)
        cosine = torch.nn.functional.cosine_similarity(
            estimate.flatten(), expected.flatten(), dim=0
        )
        assert cosine > 0.9, f"draw mean cos {cosine:.3f} on weight {index}"


def test_the_temporal_credits_refuse_a_seqenceless_state() -> None:
    """A 2-D FREE state has no time axis; the credit says so."""
    geometry = _geometry()
    x = torch.randn((_BATCH, _IN))
    y = torch.randint(0, _CLASSES, (_BATCH,))
    states = {
        Phase.FREE: CompositeState(
            activity={"x": x, "y": y}, plastic={}, substrate={}
        )
    }
    with pytest.raises(RuntimeError, match="sequence"):
        _grads(
            RTRLReference(CreditAssignmentConfig.rtrl_reference()),
            geometry,
            states,
        )
