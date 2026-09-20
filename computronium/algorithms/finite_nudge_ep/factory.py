"""Public factory for FiniteNudgeEp systems.

Wraps computronium.core.presets.create_finite_nudge_ep_mlp, adding backend selection.
"""

from typing import Any

from computronium.acceleration.dispatch import select_backend
from computronium.acceleration.registry import get
from computronium.core.presets import (
    create_finite_nudge_ep_mlp as _create_finite_nudge_ep_mlp,
)


def create_finite_nudge_ep_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
    backend: str = "auto",
) -> Any:
    """
    Create a FiniteNudgeEp system.

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    spec = get("algorithm.finite_nudge_ep")
    backend = select_backend(spec, backend)

    return _create_finite_nudge_ep_mlp(
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        output_dim=output_dim,
        lr=lr,
        device=device,
    )
