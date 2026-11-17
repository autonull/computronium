"""Locks for the estimator family: forward tangent, score, zeroth order.

Three credits the system did not have (TODO93 §19 row 1): an unbiased
pathwise gradient at O(1) activation memory, an unbiased gradient of an
expected loss, and a gradient-free update from two forwards. Each lock
fails when its mechanism is removed: the identity row, the parity cosine,
the variance fall, or the tiny-task capability.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, cast

import pytest
import torch

from computronium import (
    DigitalSubstrate,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
    compose_system,
)
from computronium.core.losses import cross_entropy, mean_squared_error
from computronium.core.system_trainer.spec import (
    credit_identity_card,
    estimator_coordinate,
)
from computronium.ontology._utils import _learnable_weight_names
from computronium.ontology.credit import (
    CreditAssignmentConfig,
    ForwardTangentCredit,
    Phase,
    ScoreFunctionCredit,
    ZerothOrderCredit,
)
from computronium.primitives._common import make_activation_primitive_case
from computronium.primitives.credit_assignment.forward_tangent import (
    cases as ft_cases,
)
from computronium.primitives.credit_assignment.forward_tangent import (
    reference as ft_reference,
)
from computronium.state import CompositeState

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from computronium.core.identity_card import AlgorithmIdentityCard

_ESTIMATORS = {
    "forward_tangent": ("forward_mode", "unbiased_pathwise"),
    "score_function": ("score_function", "unbiased_expected"),
    "zeroth_order": ("zeroth_order", "finite_difference"),
}


def _params(geometry: Any) -> tuple[list[str], list[torch.Tensor]]:
    names = _learnable_weight_names(geometry.params)
    return names, [geometry.params[name] for name in names]


def _concat(grads: Sequence[torch.Tensor]) -> torch.Tensor:
    return torch.cat([grad.reshape(-1) for grad in grads])


def _cos(left: torch.Tensor, right: torch.Tensor) -> float:
    return float(
        torch.nn.functional.cosine_similarity(left.reshape(1, -1), right.reshape(1, -1))
    )


def _exact_case_gradient(case: Any) -> torch.Tensor:
    _names, params = _params(case.geometry)
    loss = cross_entropy(case.activations[-1], case.config["target"])
    return _concat(torch.autograd.grad(loss, params))


def _free_state(
    state: torch.Tensor,
    activations: list[torch.Tensor],
    target: torch.Tensor,
) -> dict[Phase, CompositeState]:
    return {
        Phase.FREE: CompositeState(
            activity={"x": state, "y": target, "activations": activations},
            plastic={},
            substrate={},
        )
    }


def test_the_estimator_family_declares_its_coordinate() -> None:
    """The card, the axis row, and the dispatcher name one taxonomy."""
    for name, (kind, reference) in _ESTIMATORS.items():
        card = cast("AlgorithmIdentityCard | None", credit_identity_card(name))
        assert card is not None, name
        assert card.estimator_kind == kind, name
        assert card.bias_reference == reference, name
        assert estimator_coordinate(name) == (kind, reference), name
        assert card.symmetry_requirements, name
        assert card.approximation_parameters, name


def test_every_estimator_settles_only_the_free_phase() -> None:
    """A forward-only estimator must not ask the pipeline to settle a nudge."""
    for cls in (ForwardTangentCredit, ScoreFunctionCredit, ZerothOrderCredit):
        credit = cls()
        assert credit.phases == (Phase.FREE,), cls.__name__
        assert credit.requires_autograd is False, cls.__name__
        assert credit.error_blind is False, cls.__name__


def _variance_mse(estimator_samples: int, seeds: range) -> float:
    errors = []
    for seed in seeds:
        case = ft_cases.make_case(seed=seed, estimator_samples=estimator_samples)
        estimate = _concat(ft_reference.step(case))
        exact = _exact_case_gradient(case)
        errors.append(float((estimate - exact).square().mean()))
    return sum(errors) / len(errors)


def test_forward_tangent_parity_and_variance_fall() -> None:
    """cos > 0.3 at 8 tangents; the MSE falls as 1/n."""
    case = ft_cases.make_case(seed=0, estimator_samples=8)
    estimate = _concat(ft_reference.step(case))
    exact = _exact_case_gradient(case)
    assert _cos(estimate, exact) > 0.3

    coarse = _variance_mse(1, range(8))
    fine = _variance_mse(16, range(8))
    assert coarse / fine > 8.0, (coarse, fine)


def _quadratic_case(seed: int = 0) -> tuple[Any, dict[Phase, CompositeState]]:
    case = make_activation_primitive_case(
        geometry_factory=lambda: FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=4, output_dim=4, hidden_dims=())
        ),
        config={"estimator_samples": 256, "fd_step": 1e-2},
        seed=seed,
        requires_grad=False,
    )
    generator = torch.Generator().manual_seed(seed + 3)
    case.config["target"] = torch.randn(2, 4, generator=generator)
    return case, _free_state(case.state, case.activations, case.config["target"])


def test_zeroth_order_parity_on_a_quadratic_fixture() -> None:
    """Finite differences match the exact gradient (cos > 0.9 at 256 pairs)."""
    case, states = _quadratic_case()
    names, params = _params(case.geometry)
    exact = _concat(
        torch.autograd.grad(
            mean_squared_error(case.activations[-1], case.config["target"]),
            params,
        )
    )
    credit = ZerothOrderCredit(
        CreditAssignmentConfig.zeroth_order(estimator_samples=256, fd_step=1e-2)
    )
    estimate = _concat(credit.compute_pseudo_gradient(states, None, case.geometry))
    assert _cos(estimate, exact) > 0.9
    assert names


def test_score_function_parity_on_a_two_action_fixture() -> None:
    """1024 samples match the exact expected-loss gradient (cos > 0.9)."""
    torch.manual_seed(0)
    geometry = FeedforwardGeometry(
        GeometryConfig.feedforward(input_dim=4, output_dim=2, hidden_dims=(4,))
    )
    state = torch.randn(2, 4)
    target = torch.tensor([0, 1])
    activations = [state]
    x = state
    for layer in geometry._layers:
        x = layer(x)
        activations.append(x)
    names, params = _params(geometry)
    probs = torch.softmax(activations[-1], dim=-1)
    expected_reward = probs.gather(1, target.reshape(-1, 1)).sum()
    exact_reward_gradient = _concat(torch.autograd.grad(expected_reward, params))
    credit = ScoreFunctionCredit(
        CreditAssignmentConfig.score_function(estimator_samples=1024)
    )
    estimate = _concat(
        credit.compute_pseudo_gradient(
            _free_state(state, activations, target),
            None,
            geometry,
        )
    )
    assert _cos(-estimate, exact_reward_gradient) > 0.9
    assert names


def _tiny_task() -> list[tuple[torch.Tensor, torch.Tensor]]:
    """A linearly separable two-class task; the separator is the capability."""
    torch.manual_seed(0)
    samples = torch.randn(256, 8)
    labels = (torch.arange(256) % 2).long()
    samples[:, 0] += torch.where(labels == 0, 2.0, -2.0)
    return [(samples[i : i + 16], labels[i : i + 16]) for i in range(0, 128, 16)]


@pytest.mark.parametrize(
    ("credit_cls", "config_factory", "label"),
    [
        pytest.param(
            ForwardTangentCredit,
            lambda: CreditAssignmentConfig.forward_tangent(estimator_samples=8),
            "forward_tangent",
            id="forward_tangent",
        ),
        pytest.param(
            ScoreFunctionCredit,
            lambda: CreditAssignmentConfig.score_function(estimator_samples=64),
            "score_function",
            id="score_function",
        ),
        pytest.param(
            ZerothOrderCredit,
            lambda: CreditAssignmentConfig.zeroth_order(estimator_samples=8),
            "zeroth_order",
            id="zeroth_order",
        ),
    ],
)
def test_each_estimator_trains_a_tiny_task_above_chance(
    credit_cls: type,
    config_factory: Callable[[], CreditAssignmentConfig],
    label: str,
) -> None:
    """Capability card: task, memory, steps, and what stops it.

    The card is the deliverable: 128 samples of a separable two-class task,
    an 8-16-2 MLP, one epoch, and a chance floor of 0.5. A below-floor
    cell is a regime/knob finding, not an algorithm verdict.
    """
    torch.manual_seed(0)
    system = compose_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=FeedforwardGeometry(
            GeometryConfig.feedforward(input_dim=8, output_dim=2, hidden_dims=(16,))
        ),
        dynamics=InstantaneousDynamics(StateDynamicsConfig.instantaneous()),
        credit=credit_cls(config_factory()),  # type: ignore[arg-type]
        update=EuclideanUpdate(
            ParameterUpdateConfig.euclidean(
                step_size=0.05,
                grad_clip=1e9,
            )
        ),
    )
    history = SystemTrainer(
        system=system,
        config=SystemTrainerConfig(max_epochs=1, device="cpu", seed=0),
        train_data=_tiny_task(),
    ).fit()
    assert math.isfinite(history[-1]["train_loss"])
    assert history[-1]["train_acc"] > 0.6, (label, history[-1])
