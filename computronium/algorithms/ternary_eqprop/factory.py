"""Public factory for TernaryEqprop systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import (
    create_ternary_eqprop_mlp as _create_ternary_eqprop_mlp,
)

create_ternary_eqprop_mlp = make_factory(
    _create_ternary_eqprop_mlp,
    "algorithm.ternary_eqprop",
    extra_params=(),
)
