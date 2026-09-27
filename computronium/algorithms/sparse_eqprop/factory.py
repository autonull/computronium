"""Public factory for SparseEqprop systems.

Wraps computronium.core.presets.create_sparse_eqprop_mlp, attaching the selected backend.
"""

from typing import Any

from computronium.acceleration.dispatch import finish_with_backend
from computronium.acceleration.registry import get
from computronium.core.presets import (
    create_sparse_eqprop_mlp as _create_sparse_eqprop_mlp,
)


def create_sparse_eqprop_mlp(
    input_dim: int,
    hidden_dims: tuple[int, ...],
    output_dim: int,
    *,
    lr: float = 1e-3,
    device: str = "cpu",
    backend: str = "auto",
) -> Any:
    """
    Create a SparseEqprop system.

    The backend argument selects the implementation backend where supported:

        auto: use kernel if verified and available, otherwise reference
        reference: force reference implementation
        kernel: force accelerated kernel
    """
    return finish_with_backend(
        _create_sparse_eqprop_mlp(
            input_dim=input_dim,
            hidden_dims=hidden_dims,
            output_dim=output_dim,
            lr=lr,
            device=device,
        ),
        get("algorithm.sparse_eqprop"),
        backend,
    )
