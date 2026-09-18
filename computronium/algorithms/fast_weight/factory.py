"""Public factory for Fast-Weight systems (6-D joint).

Wraps computronium.core.presets.create_fast_weight_mlp, adding backend selection.
"""

from typing import Any

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get
from computronium.core.presets import create_fast_weight_mlp as _create_fast_weight_mlp


def create_fast_weight_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
    backend: str = "auto",
    fast_weight_dim: int = 512,
    decay: float = 0.9,
    learning_rate: float = 0.1,
) -> Any:
    """
    Create a Fast-Weight MLP system (6-D joint).

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    spec = get("algorithm.fast_weight")
    backend = select_backend(spec, backend)

    return _create_fast_weight_mlp(
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        output_dim=output_dim,
        lr=lr,
        device=device,
        fast_weight_dim=fast_weight_dim,
        decay=decay,
        learning_rate=learning_rate,
    )
