"""Public factory for TileNet systems.

Wraps computronium.core.presets.create_tile_mlp, adding backend selection.
"""

from typing import Any

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get
from computronium.core.presets import create_tile_mlp as _create_tile_mlp


def create_tile_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
    backend: str = "auto",
    neurons_per_tile: int = 8,
    tiles_per_layer: int = 2,
) -> Any:
    """
    Create a TileNet MLP system.

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    spec = get("algorithm.tile")
    backend = select_backend(spec, backend)

    return _create_tile_mlp(
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        output_dim=output_dim,
        lr=lr,
        device=device,
        neurons_per_tile=neurons_per_tile,
        tiles_per_layer=tiles_per_layer,
    )
