"""Public factory for MomentumEqprop systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import (
    create_momentum_eqprop_mlp as _create_momentum_eqprop_mlp,
)

create_momentum_eqprop_mlp = make_factory(
    _create_momentum_eqprop_mlp,
    "algorithm.momentum_eqprop",
    extra_params=(),
)
