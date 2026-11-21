"""Lock: a recurrent geometry's weight is in the forward graph at every depth.

TODO97 S5k: the recurrent cell was declared void with instantaneous dynamics
and gradient credit because "the recurrent weights are not in the feedforward
loss graph". The real defect was an off-by-one: ``forward`` applied the
recurrent connection after every hidden layer *except the last*, so a
single-hidden-layer geometry never touched its recurrent weight and
``GradientCredit`` refused to zero-fill it. Two hidden layers happened to reach
it through the first hidden layer, which hid the defect from the map.

Each test below fails if the recurrence leaves the forward pass again.
"""

from __future__ import annotations

import pytest
import torch

from computronium.ontology.credit import CreditAssignmentConfig
from computronium.ontology.dynamics import StateDynamicsConfig
from computronium.ontology.geometry import GeometryConfig
from computronium.ontology.substrate import SubstrateConfig
from computronium.ontology.system import SystemConfig
from computronium.ontology.update import ParameterUpdateConfig
from computronium.state import PlasticityConfig


def _system(depth: int):
    from computronium.core.system_trainer.factory import compose_system_from_configs

    geometry = GeometryConfig.recurrent(
        input_dim=3, output_dim=27, hidden_dims=(128,) * depth
    )
    return compose_system_from_configs(
        SubstrateConfig.digital(),
        geometry,
        StateDynamicsConfig.instantaneous(),
        CreditAssignmentConfig.gradient(),
        ParameterUpdateConfig.euclidean(step_size=0.01),
    )


def test_recurrent_instantaneous_gradient_is_declared_legal() -> None:
    SystemConfig(
        substrate=SubstrateConfig.digital(),
        geometry=GeometryConfig.recurrent(
            input_dim=3, output_dim=27, hidden_dims=(128, 128)
        ),
        dynamics=StateDynamicsConfig.instantaneous(),
        plasticity=PlasticityConfig.null(),
        credit=CreditAssignmentConfig.gradient(),
        update=ParameterUpdateConfig.euclidean(),
    ).validate()


@pytest.mark.parametrize("depth", [1, 2])
def test_the_recurrent_weight_receives_gradient_at_every_depth(depth: int) -> None:
    system = _system(depth)
    recurrent = system.geometry._recurrent_weight
    before = recurrent.detach().clone()
    x = torch.randint(0, 27, (16, 3)).float()
    y = torch.randint(0, 27, (16,))

    system.train_step(x, y)

    delta = (recurrent.detach() - before).norm().item()
    assert delta > 0.0, (
        f"depth={depth}: the recurrent weight did not move; the forward pass "
        "does not touch it, so the gradient credit cannot train it"
    )
