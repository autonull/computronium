"""Public factory for DiffusionEqprop systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import (
    create_diffusion_eqprop_mlp as _create_diffusion_eqprop_mlp,
)

create_diffusion_eqprop_mlp = make_factory(
    _create_diffusion_eqprop_mlp,
    "algorithm.diffusion_eqprop",
    extra_params=(),
)
