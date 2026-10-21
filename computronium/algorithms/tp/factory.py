"""Public factory for Target Propagation systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_tp_mlp as _create_tp_mlp

create_tp_mlp = make_factory(
    _create_tp_mlp,
    "algorithm.tp",
    extra_params=("beta", "settle_steps", "init_scale"),
)
