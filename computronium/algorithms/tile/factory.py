"""Public factory for TileNet systems."""

from computronium.acceleration.dispatch import make_factory
from computronium.core.presets import create_tile_mlp as _create_tile_mlp

create_tile_mlp = make_factory(
    _create_tile_mlp,
    "algorithm.tile",
    extra_params=("neurons_per_tile", "tiles_per_layer"),
)
