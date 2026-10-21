"""Public factory for Hebbian systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_hebbian_mlp as _create_hebbian_mlp

create_hebbian_mlp = make_factory(
    _create_hebbian_mlp,
    "algorithm.hebbian",
    extra_params=(),
)
