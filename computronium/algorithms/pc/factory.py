"""Public factory for Predictive Coding systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_pc_mlp as _create_pc_mlp

create_pc_mlp = make_factory(
    _create_pc_mlp,
    "algorithm.pc",
    extra_params=("beta", "settle_steps"),
)
