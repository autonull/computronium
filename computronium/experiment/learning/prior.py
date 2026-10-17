"""Learning priors: accessors over PRIORS_REGISTRY.

The prior *data* (dynamics settling steps, geometry sizes) lives in
``schema/seed_registries.PRIORS`` — one registration path, one registry. The
accessors here are the semantic layer over ``prior_value``.
"""

from __future__ import annotations

from computronium.experiment.schema.registries import prior_value


def get_dynamics_step_size(dynamics: str) -> float | None:
    """Get dynamics step size override.

    Returns None if no override exists (use default).
    """
    result = prior_value(f"dynamics_step_size_{dynamics}")
    if result is not None:
        center, _, _ = result
        return center
    return None


def apply_dynamics_step_size(
    base_step_size: float,
    dynamics: str | None,
) -> float:
    """Apply dynamics step size override."""
    if dynamics is None:
        return base_step_size
    override = get_dynamics_step_size(dynamics)
    if override is not None:
        return override
    return base_step_size


__all__ = [
    "apply_dynamics_step_size",
    "get_dynamics_step_size",
]
