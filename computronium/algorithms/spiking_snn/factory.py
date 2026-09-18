"""Public factory for Spiking SNN systems.

Wraps computronium.core.presets.create_spiking_snn_mlp, adding backend selection.
"""

from typing import Any

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get
from computronium.core.presets import create_spiking_snn_mlp as _create_spiking_snn_mlp


def create_spiking_snn_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
    backend: str = "auto",
    max_steps: int = 30,
    beta: float = 0.1,
    threshold: float = 0.5,
) -> Any:
    """
    Create a Spiking SNN MLP system.

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    spec = get("algorithm.spiking_snn")
    backend = select_backend(spec, backend)

    return _create_spiking_snn_mlp(
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        output_dim=output_dim,
        lr=lr,
        device=device,
        max_steps=max_steps,
        beta=beta,
        threshold=threshold,
    )
