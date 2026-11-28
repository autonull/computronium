"""Ternary substrate + BackpropCredit: the fail-loud contract."""

import sys

sys.path.insert(0, ".")
import torch

from computronium.core.pipeline import phase_states
from computronium.core.system_trainer import compose_system
from computronium.ontology import (
    BackpropCredit,
    CreditAssignmentConfig,
    EuclideanUpdate,
    FeedforwardGeometry,
    GeometryConfig,
    InstantaneousDynamics,
    ParameterUpdateConfig,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemState,
    TernarySubstrate,
)

g = FeedforwardGeometry(
    GeometryConfig.feedforward(input_dim=32, output_dim=10, hidden_dims=(32, 32))
)
s = TernarySubstrate(SubstrateConfig.ternary())
d = InstantaneousDynamics(StateDynamicsConfig.instantaneous())
c = BackpropCredit(CreditAssignmentConfig.gradient())
u = EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.01))
sys = compose_system(s, g, d, c, u)
x = torch.randn(4, 32)
y = torch.randint(0, 10, (4,))
acts = g.forward(x, s)
free = SystemState(x=x, activations=acts)
nudged = SystemState(x=x, y=y, activations=acts)
try:
    pg = c.compute_pseudo_gradient(phase_states(free=free, nudged=nudged), None, g)
    print(
        "no raise; grads:",
        len(pg),
        [None if p is None else p.abs().max().item() for p in pg],
    )
except Exception as e:
    print("raised:", type(e).__name__, e)
