"""Public factory for Fast-Weight systems (6-D joint)."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_fast_weight_mlp as _create_fast_weight_mlp

create_fast_weight_mlp = make_factory(
    _create_fast_weight_mlp,
    "algorithm.fast_weight",
    extra_params=("fast_weight_dim", "decay", "learning_rate"),
)
