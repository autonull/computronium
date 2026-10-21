"""Public factory for Backprop systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_backprop_mlp as _create_backprop_mlp

create_backprop_mlp = make_factory(
    _create_backprop_mlp,
    "algorithm.backprop",
    extra_params=(),
)
