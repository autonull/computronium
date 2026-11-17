"""Locks for the straight-through surrogate credit (TODO93 §19 row 4).

A hard top-k selection has no useful derivative: its exact gradient is zero
almost everywhere. ``SurrogateCredit`` is the capability the system did not
have — a hard selection that trains without a soft relaxation. Each lock fails
when its mechanism is removed: the exact parabola's zero, the smoothed
reference, the top-k invariant, or the tiny-task capability.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, cast

import torch

from computronium import (
    DigitalSubstrate,
    EuclideanUpdate,
    GeometryConfig,
    InstantaneousDynamics,
    ParameterUpdateConfig,
    RoutingGeometry,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
    compose_system,
)
from computronium.core.system_trainer.spec import (
    credit_identity_card,
    estimator_coordinate,
)
from computronium.ontology._utils import _learnable_weight_names
from computronium.ontology.credit import (
    CreditAssignmentConfig,
    Phase,
    SurrogateCredit,
)
from computronium.state import CompositeState

if TYPE_CHECKING:
    from computronium.core.identity_card import AlgorithmIdentityCard

NUM_EXPERTS = 4
TOP_K = 1
ROUTING_TEMPERATURE = 0.1


def _routing() -> RoutingGeometry:
    return RoutingGeometry(
        GeometryConfig.routing(
            input_dim=8,
            output_dim=4,
            hidden_dims=(8,),
            num_experts=NUM_EXPERTS,
            top_k=TOP_K,
            routing_temperature=ROUTING_TEMPERATURE,
        )
    )


def _weights(geometry: RoutingGeometry) -> list[torch.Tensor]:
    return [geometry.params[name] for name in _learnable_weight_names(geometry.params)]


def _free_state(x: torch.Tensor, y: torch.Tensor) -> dict[Phase, CompositeState]:
    return {
        Phase.FREE: CompositeState(
            activity={"x": x, "y": y, "activations": []},
            plastic={},
            substrate={},
        )
    }


def _flat(tensors) -> torch.Tensor:
    return torch.cat([tensor.reshape(-1) for tensor in tensors])


def _cos(left: torch.Tensor, right: torch.Tensor) -> float:
    return float(
        torch.nn.functional.cosine_similarity(left.reshape(1, -1), right.reshape(1, -1))
    )


def test_the_surrogate_declares_its_coordinate() -> None:
    """The card, the axis row, and the dispatcher name one taxonomy."""
    card = cast("AlgorithmIdentityCard | None", credit_identity_card("surrogate"))
    assert card is not None
    assert card.estimator_kind == "surrogate"
    assert card.bias_reference == "smoothed_objective"
    assert estimator_coordinate("surrogate") == ("surrogate", "smoothed_objective")
    assert card.approximation_parameters
    assert "top_k" in card.approximation_parameters
    assert "routing_temperature" in card.approximation_parameters


def test_the_surrogate_settles_only_the_free_phase() -> None:
    """A surrogate reads the task loss at the FREE-phase input/target."""
    credit = SurrogateCredit()
    assert credit.phases == (Phase.FREE,)
    assert credit.requires_autograd is False
    assert credit.error_blind is False


def test_the_geometry_selects_exactly_top_k_and_sums_to_one() -> None:
    """Hard selection: ``top_k`` non-zero weights per sample, summing to 1."""
    geometry = _routing()
    x = torch.randn(32, 8)
    weights = geometry.selection_weights(geometry._gate(geometry._trunk(x)))
    assert torch.all((weights > 0).sum(dim=-1) == TOP_K)
    assert torch.allclose(weights.sum(dim=-1), torch.ones(32))


def test_the_hard_selection_has_no_gradient_almost_everywhere() -> None:
    """A sub-margin gate perturbation leaves the hard forward bit-identical."""
    torch.manual_seed(0)
    geometry = _routing()
    x = torch.randn(16, 8)
    before = geometry(x)
    with torch.no_grad():
        geometry._gate.bias.add_(1e-3)
    assert torch.equal(before, geometry(x))


def test_the_surrogate_is_the_straight_through_gradient() -> None:
    """cos = 1 against autograd of the same straight-through forward."""
    torch.manual_seed(0)
    geometry = _routing()
    x = torch.randn(16, 8)
    y = torch.randint(0, 4, (16,))
    estimate = _flat(
        SurrogateCredit().compute_pseudo_gradient(_free_state(x, y), None, geometry)
    )
    loss = torch.nn.functional.cross_entropy(geometry(x, surrogate="ste"), y)
    exact = _flat(torch.autograd.grad(loss, _weights(geometry)))
    assert _cos(estimate, exact) > 0.999


def test_the_surrogate_tracks_the_smoothed_objective() -> None:
    """cos > 0.9 against the temperature-smoothed routing reference."""
    for seed in range(4):
        torch.manual_seed(seed)
        geometry = _routing()
        x = torch.randn(32, 8)
        y = torch.randint(0, 4, (32,))
        estimate = _flat(
            SurrogateCredit().compute_pseudo_gradient(_free_state(x, y), None, geometry)
        )
        loss = torch.nn.functional.cross_entropy(geometry(x, surrogate="soft"), y)
        reference = _flat(torch.autograd.grad(loss, _weights(geometry)))
        assert _cos(estimate, reference) > 0.9, (seed, _cos(estimate, reference))


def _tiny_task() -> list[tuple[torch.Tensor, torch.Tensor]]:
    """A linearly separable two-class task; the separator is the capability."""
    torch.manual_seed(0)
    samples = torch.randn(128, 8)
    labels = (samples[:, 0] > 0).long()
    return [(samples[i : i + 16], labels[i : i + 16]) for i in range(0, 128, 16)]


def test_a_hard_top_k_gate_trains_without_a_soft_relaxation() -> None:
    """Capability card: hard top-k trains above chance with no soft forward.

    A 128-sample separable task, an 8-16-2 routing cell (4 experts, top-1),
    one epoch on CPU at LR 0.2. A below-floor cell is a regime/knob finding,
    not a verdict on the surrogate.
    """
    torch.manual_seed(0)
    system = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=RoutingGeometry(
            GeometryConfig.routing(
                input_dim=8,
                output_dim=2,
                hidden_dims=(16,),
                num_experts=NUM_EXPERTS,
                top_k=TOP_K,
                routing_temperature=ROUTING_TEMPERATURE,
            )
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=SurrogateCredit(CreditAssignmentConfig.surrogate()),  # type: ignore[arg-type]
        update=EuclideanUpdate(
            ParameterUpdateConfig.euclidean(step_size=0.2, grad_clip=1e9)
        ),
    )
    history = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(max_epochs=1, device="cpu", seed=0),
        train_data=_tiny_task(),
    ).fit()
    assert math.isfinite(history[-1]["train_loss"])
    assert history[-1]["train_acc"] > 0.6, history[-1]
