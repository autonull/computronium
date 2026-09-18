"""Public factory for Forward-Forward systems.

Wraps computronium.core.presets.create_ff_mlp, adding backend selection.
"""

from typing import Any

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get
from computronium.core.presets import create_ff_mlp as _create_ff_mlp


def create_ff_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    layer_lr: float = 0.03,
    classifier_lr: float = 0.01,
    threshold: float = 2.0,
    num_layers: int | None = None,
    device: str = "cpu",
    backend: str = "auto",
) -> Any:
    """
    Create an FF MLP system.

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    spec = get("algorithm.ff")
    backend = select_backend(spec, backend)

    return _create_ff_mlp(
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        output_dim=output_dim,
        layer_lr=layer_lr,
        classifier_lr=classifier_lr,
        threshold=threshold,
        num_layers=num_layers,
        device=device,
    )
