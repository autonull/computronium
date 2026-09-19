"""Public factory for Target Propagation systems.

Wraps computronium.core.presets.create_tp_mlp, adding backend selection.
"""

from typing import Any

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get
from computronium.core.presets import create_tp_mlp as _create_tp_mlp


def create_tp_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
    backend: str = "auto",
    beta: float = 0.1,
    settle_steps: int = 30,
    init_scale: float = 0.1,
) -> Any:
    """
    Create a Target Propagation MLP system.

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    spec = get("algorithm.tp")
    backend = select_backend(spec, backend)

    return _create_tp_mlp(
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        output_dim=output_dim,
        lr=lr,
        device=device,
        beta=beta,
        settle_steps=settle_steps,
        init_scale=init_scale,
    )
