"""Legacy ModelConfig for deployments package.

This is a frozen copy of the legacy ModelConfig from computronium.config.unified
(REFACTOR.md §1.1) kept for backward compatibility with the deployments package.
New code should use computronium.config.experiment.ModelConfig instead.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

#: Role of a layer within a model: "hidden" or "output".
LayerRole = Literal["hidden", "output"]


@dataclass(frozen=True, slots=True)
class ModelConfig:
    """Legacy configuration for a bio-plausible model.

    Kept for backward compatibility with the deployments package.
    New code should use computronium.config.experiment.ModelConfig instead.
    """

    name: str
    input_dim: int
    output_dim: int
    hidden_dims: list[int] = field(default_factory=list)

    # Training hyperparameters
    learning_rate: float = 0.001
    beta: float = 0.2  # For EqProp
    # Maximum number of equilibrium steps
    max_steps: int = 30
    # Equilibrium settling early-stop parameters
    convergence_threshold: float = 1e-3
    convergence_start: int = 5

    # Architecture
    use_spectral_norm: bool = True
    # Power iterations for the spectral-norm parametrization. Lower = cheaper
    # equilibrium settles (each power iteration is a forward+tranpose multiply);
    # the coarse sweep can set 0 to drop spectral-norm cost from the map.
    spectral_norm_power_iterations: int = 5
    activation: str = "silu"
    lipschitz_mode: str = "power_iteration"  # "power_iteration" or "svd"

    # μPC (Maximal Update Parameterization) output-node scaling
    # "mupc": output layer skips the √L scaling factor applied to hidden layers
    # "uniform": all layers get the same scaling (backward compat / ablation)
    output_scaling_mode: Literal["uniform", "mupc"] = "mupc"

    # Additional kwargs
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate configuration."""
        # input_dim can be 0 for Conv models (placeholder)
        val = self.input_dim
        if isinstance(val, tuple):
            import math

            val = math.prod(val)
        if val < 0:
            raise ValueError(f"input_dim must be >= 0, got {val}")
        # Use object.__setattr__ because frozen=True
        if isinstance(self.input_dim, tuple):
            object.__setattr__(self, "input_dim", val)
        if self.output_dim <= 0:
            raise ValueError(f"output_dim must be > 0, got {self.output_dim}")


def _build_model_config(
    spec,
    input_dim: int,
    output_dim: int,
    hidden_dim: int | None,
    num_layers: int,
    kwargs: dict[str, object],
    *,
    learning_rate: float | None = None,
    beta: float | None = None,
    max_steps: int | None = None,
    use_spectral_norm: bool | None = None,
    convergence_threshold: float | None = None,
    convergence_start: int | None = None,
) -> ModelConfig:
    """Construct a ``ModelConfig`` from the standard ``build`` classmethod parameters.

    Handles the common ``spec.name``, ``compute_hidden_dims``, and
    ``kwargs`` wiring. Optional overrides are passed through to the
    ``ModelConfig`` constructor; if *not* provided, the corresponding
    ``ModelConfig`` defaults apply.
    """
    # Collect overrides that match ModelConfig fields so they can be applied to
    # the (frozen) config after construction. ``None`` entries are filtered by
    # the apply loop below, so named ``build`` params that weren't provided are
    # harmless; explicit kwargs take precedence over them.
    overrides: dict[str, object] = {
        "learning_rate": learning_rate,
        "beta": beta,
        "max_steps": max_steps,
        "convergence_threshold": convergence_threshold,
        "convergence_start": convergence_start,
        "use_spectral_norm": use_spectral_norm,
    }

    kw_beta = kwargs.get("beta")
    if isinstance(kw_beta, float | int):
        overrides["beta"] = kw_beta

    kw_max_steps = kwargs.get("max_steps")
    if isinstance(kw_max_steps, int):
        overrides["max_steps"] = kw_max_steps

    kw_threshold = kwargs.get("convergence_threshold")
    if isinstance(kw_threshold, float | int):
        overrides["convergence_threshold"] = float(kw_threshold)

    kw_start = kwargs.get("convergence_start")
    if isinstance(kw_start, int):
        overrides["convergence_start"] = kw_start

    config = ModelConfig(
        name=spec.name,
        input_dim=input_dim if input_dim is not None else 0,
        output_dim=output_dim,
        hidden_dims=compute_hidden_dims(hidden_dim, num_layers),
        extra=kwargs,
    )
    # Apply overrides after construction (frozen — use object.__setattr__).
    for field_name, value in overrides.items():
        if value is not None:
            object.__setattr__(config, field_name, value)

    return config


def resolve_hidden_dims(config: Any | None, hidden_dim: int | None) -> list[int]:
    """Resolve the ``hidden_dims`` list from a config or fallback.

    Returns ``config.hidden_dims`` if non-empty; otherwise falls back to
    ``[hidden_dim]`` if set; otherwise ``[]``.
    """
    if config is not None and getattr(config, "hidden_dims", None):
        return config.hidden_dims
    if hidden_dim is not None:
        return [hidden_dim]
    return []


def compute_hidden_dims(
    hidden_dim: int | None, num_layers: int, max_layers: int = 5
) -> list[int]:
    """Compute a ``hidden_dims`` list for a ``build`` classmethod.

    Returns ``[hidden_dim] * min(num_layers, max_layers)`` when
    ``hidden_dim`` is set, else ``[]``.
    """
    if hidden_dim is None:
        return []
    return [hidden_dim] * min(num_layers, max_layers)


def config_to_dict(obj: Any) -> dict[str, Any]:
    """Convert a dataclass config to a plain dict, omitting ``None`` values.

    Like :meth:`~computronium.core.metrics.BaseMetrics.to_dict`, this
    strips ``None`` entries so the result is JSON-serialisable and
    losslessly reconstructable.
    """
    return {k: v for k, v in asdict(obj).items() if v is not None}


__all__ = [
    "LayerRole",
    "ModelConfig",
    "_build_model_config",
    "compute_hidden_dims",
    "config_to_dict",
    "resolve_hidden_dims",
]
