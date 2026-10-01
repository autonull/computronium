"""Learning priors: PriorSpec registry with ruler-LR and step-size override data.

Implements WP6 deliverable: convert ruler-LR table and step-size override tables
into prior *data*; delete the source code tables (R52, Q4, Q12).

PRIORS registry becomes the single source. Accessor functions
use `prior_value(name, context)` from the registry.
"""

from __future__ import annotations

from computronium.experiment.schema.registries import (
    PriorSpec,
    prior_value,
    register_prior,
)

# =============================================================================
# Registration Functions (populate PRIORS_REGISTRY from inline data)
# =============================================================================


def _register_ruler_lr_priors() -> None:
    """Register ruler LR priors for each task."""
    # Task-specific ruler LRs (feedforward topology)
    ruler_lr_data: dict[str, float] = {
        "digits": 0.01,
        "mnist": 0.01,
        "fashion_mnist": 0.01,
        "kmnist": 0.01,
        "usps": 0.01,
        "xor": 0.001,
        "spiral": 0.01,
        "circles": 0.01,
        "iris": 0.001,
        "wine": 0.001,
        "breast_cancer": 0.01,
    }

    for task, lr in ruler_lr_data.items():
        prior = PriorSpec(
            name=f"ruler_lr_{task}",
            distribution="log_uniform",
            params={
                "low": lr * 0.1,
                "high": lr * 10.0,
                "center": lr,
            },
            description=f"Ruler-calibrated learning rate for task '{task}' (feedforward topology)",
            confidence=0.9,
            uncertainty=0.0,
            override_scope="coordinate",
        )
        register_prior(prior)

    # Catch-all default for unknown tasks (feedforward)
    default_lr = 0.01
    prior = PriorSpec(
        name="ruler_lr_catchall",
        distribution="log_uniform",
        params={
            "low": default_lr * 0.1,
            "high": default_lr * 10.0,
            "center": default_lr,
        },
        description="Catch-all ruler-calibrated learning rate for unknown tasks (feedforward)",
        confidence=0.9,
        uncertainty=0.0,
        override_scope="coordinate",
    )
    register_prior(prior)

    # Non-feedforward default (from topology LR probe)
    nf_lr = 0.01
    prior = PriorSpec(
        name="ruler_lr_non_feedforward",
        distribution="log_uniform",
        params={
            "low": nf_lr * 0.1,
            "high": nf_lr * 10.0,
            "center": nf_lr,
        },
        description="Default learning rate for non-feedforward topologies (from topology LR probe)",
        confidence=0.8,
        uncertainty=0.0,
        override_scope="coordinate",
    )
    register_prior(prior)


def _register_step_size_override_priors() -> None:
    """Register step size override priors for (dynamics, credit) combinations."""
    step_size_overrides: dict[tuple[str, str], float] = {
        ("energy_minimization", "random_projections"): 0.1,
        ("energy_minimization", "gradient"): 0.5,
        ("energy_minimization", "thermodynamic_contrast"): 0.00005,
        ("energy_minimization", "pepita"): 0.0001,
        ("energy_minimization", "local_goodness"): 0.0005,
        ("energy_minimization", "temporal_trace"): 0.0001,
        ("energy_minimization", "target_inversion"): 0.1,
        ("diffusion", "random_projections"): 0.05,
        ("diffusion", "spectral_constrained"): 0.1,
        ("diffusion", "homeostatic"): 0.1,
        ("diffusion", "temporal_trace"): 0.0001,
        ("diffusion", "target_inversion"): 0.1,
        ("lazy", "temporal_trace"): 0.0001,
        ("lazy", "thermodynamic_contrast"): 0.001,
        ("lazy", "random_projections"): 0.1,
        ("lazy", "local_contrastive"): 0.0005,
        ("lazy", "local_goodness"): 0.1,
        ("lazy", "pepita"): 0.001,
        ("lazy", "gradient"): 0.01,
        ("instantaneous", "temporal_trace"): 0.0001,
        ("instantaneous", "pepita"): 0.01,
        ("pc_alm", "thermodynamic_contrast"): 0.001,
        ("pc_alm", "pc_alm"): 0.001,
        ("instantaneous", "homeostatic"): 0.001,
        ("spike_integration", "temporal_trace"): 0.0001,
        ("predictive_settling", "thermodynamic_contrast"): 0.5,
        ("predictive_settling", "local_goodness"): 0.001,
        ("error_predictive_coding", "thermodynamic_contrast"): 0.1,
        ("error_predictive_coding", "local_goodness"): 0.1,
    }

    for (dynamics, credit), multiplier in step_size_overrides.items():
        prior = PriorSpec(
            name=f"step_size_override_{dynamics}_{credit}",
            distribution="log_normal",
            params={
                "mean": multiplier,
                "sigma": 0.5,
            },
            description=f"Step size multiplier for dynamics={dynamics}, credit={credit}",
            confidence=0.8,
            uncertainty=0.0,
            override_scope="coordinate",
        )
        register_prior(prior)


def _register_dynamics_step_size_priors() -> None:
    """Register dynamics step size override priors."""
    dynamics_step_sizes: dict[str, float] = {
        "diffusion": 0.001,
        "predictive_settling": 0.01,
    }

    for dynamics, step_size in dynamics_step_sizes.items():
        prior = PriorSpec(
            name=f"dynamics_step_size_{dynamics}",
            distribution="log_uniform",
            params={
                "low": step_size * 0.1,
                "high": step_size * 10.0,
                "center": step_size,
            },
            description=f"Dynamics settling step size for {dynamics}",
            confidence=0.85,
            uncertainty=0.0,
            override_scope="coordinate",
        )
        register_prior(prior)


def register_all_priors() -> None:
    """Register all migrated priors. Call once at module import."""
    _register_ruler_lr_priors()
    _register_step_size_override_priors()
    _register_dynamics_step_size_priors()


# =============================================================================
# Accessor Functions (L11: single-source via PRIORS_REGISTRY)
# =============================================================================


def get_ruler_lr(task: str | None, topology: str | None = None) -> float:
    """Get ruler LR for a task (migrated from campaign._ruler_lr).

    L11: Now uses PRIORS_REGISTRY via prior_value() as single source.
    """
    # Try task-specific prior first
    if task:
        result = prior_value(f"ruler_lr_{task}")
        if result is not None:
            center, _, _ = result
            return center

    # Fallback to non-feedforward or catchall
    if topology not in {None, "feedforward"}:
        result = prior_value("ruler_lr_non_feedforward")
        if result is not None:
            center, _, _ = result
            return center

    result = prior_value("ruler_lr_catchall")
    if result is not None:
        center, _, _ = result
        return center

    # Ultimate fallback (should never reach here if registry is properly seeded)
    return 0.01


def get_step_size_multiplier(dynamics: str, credit: str) -> float | None:
    """Get step size multiplier for (dynamics, credit) combination.

    L11: Now uses PRIORS_REGISTRY via prior_value() as single source.

    Returns None if no override exists (use base step_size).
    """
    result = prior_value(f"step_size_override_{dynamics}_{credit}")
    if result is not None:
        center, _, _ = result
        return center
    return None


def get_dynamics_step_size(dynamics: str) -> float | None:
    """Get dynamics step size override.

    L11: Now uses PRIORS_REGISTRY via prior_value() as single source.

    Returns None if no override exists (use default).
    """
    result = prior_value(f"dynamics_step_size_{dynamics}")
    if result is not None:
        center, _, _ = result
        return center
    return None


def apply_step_size_overrides(
    base_step_size: float,
    dynamics: str | None,
    credit: str | None,
) -> float:
    """Apply adaptive step_size overrides for (dynamics, credit) combos.

    L11: Uses PRIORS_REGISTRY via get_step_size_multiplier().
    """
    if dynamics is None or credit is None:
        return base_step_size
    multiplier = get_step_size_multiplier(dynamics, credit)
    if multiplier is not None:
        return base_step_size * multiplier
    return base_step_size


def apply_dynamics_step_size(
    base_step_size: float,
    dynamics: str | None,
) -> float:
    """Apply dynamics step size override.

    L11: Uses PRIORS_REGISTRY via get_dynamics_step_size().
    """
    if dynamics is None:
        return base_step_size
    override = get_dynamics_step_size(dynamics)
    if override is not None:
        return override
    return base_step_size


# Register all priors at import time
register_all_priors()


__all__ = [
    "apply_dynamics_step_size",
    "apply_step_size_overrides",
    "get_dynamics_step_size",
    "get_ruler_lr",
    "get_step_size_multiplier",
    "prior_value",
    "register_all_priors",
]
