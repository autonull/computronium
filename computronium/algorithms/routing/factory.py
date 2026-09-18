"""Public factory for Routing systems (6-D joint).

Wraps computronium.core.presets.create_routing_mlp, adding backend selection.
"""

from typing import Any

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get
from computronium.core.presets import create_routing_mlp as _create_routing_mlp


def create_routing_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
    backend: str = "auto",
    gate_dim: int = 64,
    gate_init_scale: float = 0.1,
) -> Any:
    """
    Create a Routing MLP system (6-D joint).

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    spec = get("algorithm.routing")
    backend = select_backend(spec, backend)

    return _create_routing_mlp(
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        output_dim=output_dim,
        lr=lr,
        device=device,
        gate_dim=gate_dim,
        gate_init_scale=gate_init_scale,
    )
