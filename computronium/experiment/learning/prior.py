"""Learning priors: PriorSpec registry with ruler-LR and step-size override data.

Implements WP6 deliverable: convert ruler-LR table and step-size override tables
into prior *data*; delete the source code tables (R52, Q4, Q12).

This module migrates the following legacy code tables to PriorSpec records:
- `_ruler_lr` table from `computronium.autoscientist.campaign` (per-task LR)
- `_STEP_SIZE_OVERRIDES` from `computronium.ontology.update` (dynamics×credit multipliers)
- `_DYNAMICS_STEP_SIZE_OVERRIDES` from `computronium.autoscientist.compose` (dynamics step sizes)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from computronium.experiment.schema.registries import (
    PriorSpec,
    register_prior,
)


class PriorDomain(StrEnum):
    """Domain of a prior (which axis/tunable it applies to)."""

    LEARNING_RATE = "learning_rate"  # Per-task LR (ruler table)
    UPDATE_STEP_SIZE = "update_step_size"  # Per (dynamics, credit) multiplier
    DYNAMICS_STEP_SIZE = "dynamics_step_size"  # Per dynamics step size


class PriorSource(StrEnum):
    """Source of the prior data."""

    RULER_TABLE = "ruler_table"  # Calibrated per-task LR from ruler experiments
    STEP_SIZE_OVERRIDES = "step_size_overrides"  # Empirical stability overrides
    DYNAMICS_STEP_SIZE_OVERRIDES = (
        "dynamics_step_size_overrides"  # Settling stability overrides
    )
    MANUAL = "manual"  # Manually specified


@dataclass(frozen=True, slots=True)
class PriorMetadata:
    """Metadata for a prior specification."""

    domain: PriorDomain
    source: PriorSource
    # For ruler LR: task name
    # For step_size_overrides: "dynamics|credit"
    # For dynamics_step_size_overrides: dynamics name
    key: str
    # Additional context
    confidence: float = 1.0  # 0-1, how confident we are in this prior
    provenance: str = ""  # Source experiment/run ID
    notes: str = ""


# =============================================================================
# Ruler LR Table Migration (from computronium.autoscientist.campaign)
# =============================================================================

_RULER_LR_DATA: dict[str, float] = {
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
    # Default for unknown tasks (feedforward)
    "*": 0.01,
    # Non-feedforward default (from topology LR probe)
    "non_feedforward_default": 0.01,
}


def _load_ruler_table() -> dict[str, float]:
    """Load ruler table from JSON file if available."""
    try:
        path = (
            Path(__file__).parent.parent.parent / "autoscientist" / "ruler_table.json"
        )
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            result = {}
            for row in data.get("rows", []):
                task = row.get("task")
                lr = row.get("lr")
                if task and isinstance(lr, int | float):
                    result[str(task)] = float(lr)
            return result
    except OSError, ValueError, KeyError:
        pass
    return _RULER_LR_DATA


# =============================================================================
# Step Size Overrides Migration (from computronium.ontology.update)
# =============================================================================

# Key: (dynamics, credit) -> multiplier
_STEP_SIZE_OVERRIDES_DATA: dict[tuple[str, str], float] = {
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


# =============================================================================
# Dynamics Step Size Overrides Migration (from computronium.autoscientist.compose)
# =============================================================================

_DYNAMICS_STEP_SIZE_OVERRIDES_DATA: dict[str, float] = {
    "diffusion": 0.001,
    "predictive_settling": 0.01,
}


# =============================================================================
# Registration Functions
# =============================================================================


def _register_ruler_lr_priors() -> None:
    """Register ruler LR priors for each task."""
    ruler_data = _load_ruler_table()

    for task, lr in ruler_data.items():
        if task == "non_feedforward_default":
            continue  # Handled separately

        _ = PriorMetadata(
            domain=PriorDomain.LEARNING_RATE,
            source=PriorSource.RULER_TABLE,
            key=task,
            confidence=0.9,  # Calibrated but topology-specific (feedforward only)
            provenance="ruler_table.json",
            notes=f"Per-task LR calibrated for feedforward topology; non-feedforward uses {_RULER_LR_DATA.get('non_feedforward_default', 0.01)}",
        )

        # Create PriorSpec with distribution params for log-uniform around the calibrated value
        # Using log_uniform with the calibrated LR as the center
        prior = PriorSpec(
            name=f"ruler_lr_{task}",
            distribution="log_uniform",
            params={
                "low": lr * 0.1,
                "high": lr * 10.0,
                "center": lr,
            },
            description=f"Ruler-calibrated learning rate for task '{task}' (feedforward topology)",
        )
        register_prior(prior)

    # Register default for unknown tasks
    default_lr = ruler_data.get("*", 0.01)
    prior = PriorSpec(
        name="ruler_lr_default",
        distribution="log_uniform",
        params={
            "low": default_lr * 0.1,
            "high": default_lr * 10.0,
            "center": default_lr,
        },
        description="Default ruler-calibrated learning rate for unknown tasks (feedforward)",
    )
    register_prior(prior)

    # Register non-feedforward default
    nf_lr = _RULER_LR_DATA.get("non_feedforward_default", 0.01)
    prior = PriorSpec(
        name="ruler_lr_non_feedforward",
        distribution="log_uniform",
        params={
            "low": nf_lr * 0.1,
            "high": nf_lr * 10.0,
            "center": nf_lr,
        },
        description="Default learning rate for non-feedforward topologies (from topology LR probe)",
    )
    register_prior(prior)


def _register_step_size_override_priors() -> None:
    """Register step size override priors for (dynamics, credit) combinations."""
    for (dynamics, credit), multiplier in _STEP_SIZE_OVERRIDES_DATA.items():
        key = f"{dynamics}|{credit}"
        _ = PriorMetadata(
            domain=PriorDomain.UPDATE_STEP_SIZE,
            source=PriorSource.STEP_SIZE_OVERRIDES,
            key=key,
            confidence=0.8,  # Empirical stability overrides
            provenance="ontology/update.py::_STEP_SIZE_OVERRIDES",
            notes=f"Multiplier for base step_size when dynamics={dynamics}, credit={credit}",
        )

        # The prior is a log-normal around the multiplier
        # Base step_size is typically 0.01, so effective step_size = 0.01 * multiplier
        prior = PriorSpec(
            name=f"step_size_override_{dynamics}_{credit}",
            distribution="log_normal",
            params={
                "mean": multiplier,
                "sigma": 0.5,  # Allow some variation
            },
            description=f"Step size multiplier for dynamics={dynamics}, credit={credit}",
        )
        register_prior(prior)


def _register_dynamics_step_size_priors() -> None:
    """Register dynamics step size override priors."""
    for dynamics, step_size in _DYNAMICS_STEP_SIZE_OVERRIDES_DATA.items():
        key = dynamics
        _ = PriorMetadata(
            domain=PriorDomain.DYNAMICS_STEP_SIZE,
            source=PriorSource.DYNAMICS_STEP_SIZE_OVERRIDES,
            key=key,
            confidence=0.85,  # Empirical settling stability
            provenance="autoscientist/compose.py::_DYNAMICS_STEP_SIZE_OVERRIDES",
            notes="Step size for dynamics settling (not update step_size)",
        )

        prior = PriorSpec(
            name=f"dynamics_step_size_{dynamics}",
            distribution="log_uniform",
            params={
                "low": step_size * 0.1,
                "high": step_size * 10.0,
                "center": step_size,
            },
            description=f"Dynamics settling step size for {dynamics}",
        )
        register_prior(prior)


def register_all_priors() -> None:
    """Register all migrated priors. Call once at module import."""
    _register_ruler_lr_priors()
    _register_step_size_override_priors()
    _register_dynamics_step_size_priors()


def get_ruler_lr(task: str | None, topology: str | None = None) -> float:
    """Get ruler LR for a task (migrated from campaign._ruler_lr).

    This is the data-driven replacement for the code function.
    """
    ruler_data = _load_ruler_table()

    if topology not in {None, "feedforward"}:
        return ruler_data.get("non_feedforward_default", 0.01)

    if task and task in ruler_data:
        return ruler_data[task]

    return ruler_data.get("*", 0.01)


def get_step_size_multiplier(dynamics: str, credit: str) -> float | None:
    """Get step size multiplier for (dynamics, credit) combination.

    Returns None if no override exists (use base step_size).
    """
    return _STEP_SIZE_OVERRIDES_DATA.get((dynamics, credit))


def get_dynamics_step_size(dynamics: str) -> float | None:
    """Get dynamics step size override.

    Returns None if no override exists (use default).
    """
    return _DYNAMICS_STEP_SIZE_OVERRIDES_DATA.get(dynamics)


def apply_step_size_overrides(
    base_step_size: float,
    dynamics: str | None,
    credit: str | None,
) -> float:
    """Apply adaptive step_size overrides for (dynamics, credit) combos.

    Migrated from ontology.update::_apply_step_size_overrides
    """
    if dynamics is None or credit is None:
        return base_step_size
    multiplier = _STEP_SIZE_OVERRIDES_DATA.get((dynamics, credit))
    if multiplier is not None:
        return base_step_size * multiplier
    return base_step_size


def apply_dynamics_step_size(
    base_step_size: float,
    dynamics: str | None,
) -> float:
    """Apply dynamics step size override.

    Migrated from autoscientist.compose
    """
    if dynamics is None:
        return base_step_size
    override = _DYNAMICS_STEP_SIZE_OVERRIDES_DATA.get(dynamics)
    if override is not None:
        return override
    return base_step_size


# Register all priors at import time
register_all_priors()


__all__ = [
    "_DYNAMICS_STEP_SIZE_OVERRIDES_DATA",
    "_RULER_LR_DATA",
    "_STEP_SIZE_OVERRIDES_DATA",
    "PriorDomain",
    "PriorMetadata",
    "PriorSource",
    "apply_dynamics_step_size",
    "apply_step_size_overrides",
    "get_dynamics_step_size",
    "get_ruler_lr",
    "get_step_size_multiplier",
    "register_all_priors",
]
