"""Public factory for Direct Feedback Alignment systems.

Wraps computronium.core.presets.create_fa_mlp with DFA configuration, adding backend selection.
"""

from typing import Any

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get
from computronium.core.presets import create_fa_mlp as _create_fa_mlp


def create_dfa_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
    backend: str = "auto",
    feedback_scale: float = 0.01,
) -> Any:
    """
    Create a Direct Feedback Alignment (DFA) MLP system.

    DFA is a variant of FA where feedback goes directly from output
    to all hidden layers, rather than layer-by-layer.

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    spec = get("algorithm.dfa")
    backend = select_backend(spec, backend)

    return _create_fa_mlp(
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        output_dim=output_dim,
        lr=lr,
        device=device,
        feedback_scale=feedback_scale,
    )
