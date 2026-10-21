"""Public factory for PEPITA systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_pepita_mlp as _create_pepita_mlp

create_pepita_mlp = make_factory(
    _create_pepita_mlp,
    "algorithm.pepita",
    extra_params=(),
)
