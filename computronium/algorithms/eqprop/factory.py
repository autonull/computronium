"""Public factory for Equilibrium Propagation systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_eqprop_mlp as _create_eqprop_mlp

create_eqprop_mlp = make_factory(
    _create_eqprop_mlp,
    "algorithm.eqprop",
    extra_params=("beta", "inference_steps"),
)
