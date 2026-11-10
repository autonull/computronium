"""Metrics computation utilities extracted from evaluate.py.

This module contains all the metrics computation functions that were previously
in evaluate.py, keeping the main evaluation logic clean and focused.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

import torch

from computronium.core.logging import get_logger
from computronium.experiment.execution.settle_operator import (
    settle_step_operator_at_state,
)
from computronium.experiment.schema.metrics import HISTORY_METRICS

if TYPE_CHECKING:
    from collections.abc import Callable

    from computronium.experiment.schema.coordinate import Coordinate, Schedule

logger = get_logger(__name__)

# An exact Jacobian costs d backward passes and an O(d^3) eigen-decomposition.
# Measured on CUDA at the campaign's widest cell (hidden 256 x 5 layers, d=1536):
# 2.6s to build, 0.4s to factor — 3% of the cell it describes, so the cap sits
# above the declared space rather than truncating it. A cap, not a silent
# wrong number: past it the settle telemetry is reported without a Jacobian.
_MAX_JACOBIAN_WIDTH: int = 1536


def history_metrics(history: list[dict[str, float]]) -> dict[str, float]:
    """Final-epoch observations, flattened to the metric namespace.

    The kernel-owned history→metrics extraction. The lab's certificates path
    consumes this rather than re-implementing the filter (TODO47 T6): two
    extractions is how the fallback chain hid dead keys from itself.
    """
    if not history:
        msg = "training produced no epochs"
        from computronium.experiment.kernel.evaluate import EvaluationError

        raise EvaluationError("runtime_error", msg)
    final = history[-1]
    metrics = {
        key: float(value) for key, value in final.items() if key in HISTORY_METRICS
    }
    metrics["epochs_run"] = float(final.get("global_step", 0))
    return metrics


def _within_ceiling(param_count: int, param_budget: int) -> bool:
    """Whether a cell honoured the parameter ceiling its schedule declared."""
    from computronium.experiment.schema.registries import PARAM_BUDGET_TOLERANCE

    if param_budget <= 0:
        return True
    return param_count <= param_budget * (1 + PARAM_BUDGET_TOLERANCE)


def _defect(
    complete: bool, within_ceiling: bool, param_count: int, param_budget: int
) -> str:
    match (complete, within_ceiling):
        case (True, True):
            return ""
        case (False, True):
            return "training stopped before the requested epochs"
        case (True, False):
            return (
                f"{param_count} parameters exceeds the declared ceiling {param_budget}"
            )
        case _:
            return (
                "training stopped before the requested epochs; "
                f"{param_count} parameters exceeds the declared ceiling {param_budget}"
            )


def _finite(metrics: Mapping[str, float]) -> bool:
    return all(math.isfinite(v) for v in metrics.values())


def _energy_family(dynamics_type: str) -> str:
    """Map a dynamics type to its energy family for metric naming."""
    if dynamics_type in {"energy_minimization", "lazy", "diffusion"}:
        return "hopfield"
    if dynamics_type in {"predictive_settling", "error_predictive_coding"}:
        return "pc"
    if dynamics_type == "pc_alm":
        return "augmented_lagrangian"
    if dynamics_type == "spike_integration":
        return "spike_proxy"
    if dynamics_type == "instantaneous":
        return "instantaneous_proxy"
    return "unknown"


def _record_family_energy(
    metrics: dict[str, float],
    dynamics: Any,
    settled: Any,
    geometry: Any,
    family: str,
) -> None:
    """Record the energy metric under the dynamics-family-specific key."""
    try:
        energy = dynamics.compute_energy(settled, geometry)
    except Exception as exc:  # ruff: ignore[blind-except] - a proxy energy is optional
        logger.debug("free energy unavailable: %s", exc)
        return
    if energy is None:
        return
    energy_val = float(energy.item() if hasattr(energy, "item") else energy)

    # Detect energy clamping: if energy is at or near the clamp boundary,
    # it's a warning (numerical stability measure), not a failure.
    max_energy = getattr(getattr(dynamics, "config", None), "max_energy", 1e6)
    if abs(energy_val) >= max_energy * 0.999:  # Near clamp boundary
        metrics["energy_clamped"] = True

    if family == "pc":
        metrics["pc_free_energy"] = energy_val
    elif family == "augmented_lagrangian":
        metrics["augmented_lagrangian"] = energy_val
    else:
        metrics[f"{family}_energy"] = energy_val
    if family == "hopfield":
        metrics["free_energy"] = energy_val


def _free_settle_metrics_and_state(
    system: Any, x: torch.Tensor
) -> tuple[dict[str, float], list[torch.Tensor] | None]:
    """The free phase's own telemetry and the settled activations."""
    from computronium.core.pipeline import forward_pass
    from computronium.ontology import SystemState

    metrics: dict[str, float] = {}
    device = _param_device(system)
    dynamics_type = getattr(system.dynamics.config, "dynamics_type", "unknown")
    family = _energy_family(dynamics_type)
    settled_acts: list[torch.Tensor] | None = None
    try:  # ruff: ignore[too-many-statements-in-try-clause]
        with torch.no_grad():
            state = SystemState(x=x.to(device), y=None)
            state.activations = forward_pass(
                system.substrate, system.geometry, x.to(device)
            )
            settled = system.dynamics.settle(
                state, system.geometry, system.substrate, target=None
            )
            metrics["settle_steps"] = float(
                getattr(system.dynamics, "_settle_steps_used", 0)
            )
            metrics["settle_converged"] = float(
                bool(getattr(system.dynamics, "_converged", False))
            )
            metrics["settle_horizon"] = float(
                getattr(system.dynamics, "_settle_horizon", 0)
            )
            # Ensure geometry is on the same device as settled activations
            # to avoid device mismatch in compute_energy
            if hasattr(system.geometry, "to"):
                system.geometry.to(device)
            _record_family_energy(
                metrics, system.dynamics, settled, system.geometry, family
            )
            # Extract settled activations for stability analysis
            settled_acts = settled.activations
            if isinstance(settled_acts, torch.Tensor):
                settled_acts = [settled_acts]
    except Exception as exc:  # ruff: ignore[blind-except] - a metric must not fail the cell
        logger.warning("free settle telemetry failed: %s", exc)
    return metrics, settled_acts


def _param_device(system: Any) -> torch.device:
    """The device the cell's weights live on, wherever it was trained."""
    return next(system.geometry.parameters()).device


def compute_stability_metrics(
    system: Any,
    x: torch.Tensor,
    max_steps: int = 50,
) -> dict[str, float]:
    """Stability of one relaxation step, measured on the trained system."""
    metrics: dict[str, float] = {}
    free_energy, settled_acts = _free_settle_metrics_and_state(system, x)
    metrics.update(free_energy)

    if settled_acts is None or len(settled_acts) < 3:
        logger.debug("no settled hidden activations; reporting settle telemetry only")
        return metrics

    operator = settle_step_operator_at_state(system, settled_acts)
    if operator is None:
        logger.debug("geometry is not layered; reporting settle telemetry only")
        return metrics

    step, width = operator
    if width > _MAX_JACOBIAN_WIDTH:
        logger.info(
            "hidden width %d exceeds the Jacobian cap %d; reporting settle telemetry",
            width,
            _MAX_JACOBIAN_WIDTH,
        )
        return metrics

    # Compute Jacobian at the settled hidden activations (the fixed point)
    settled_hidden = torch.cat([h[0] for h in settled_acts[1:-1]])

    _compute_jacobian_metrics(step, settled_hidden, system, metrics)

    return metrics


def _compute_jacobian_metrics(
    step: Callable[[torch.Tensor], torch.Tensor],
    settled_hidden: torch.Tensor,
    system: Any,
    metrics: dict[str, float],
) -> None:
    """Compute Jacobian-based stability metrics using the stability package."""
    from computronium.stability import drift_metrics, jacobian_spectral_metrics

    # Define step function for stability package
    def step_fn(h: torch.Tensor) -> torch.Tensor:
        return step(h)

    # Use canonical stability package for spectral metrics
    spectral = jacobian_spectral_metrics(
        step_fn,
        settled_hidden,
        compute_min_singular=True,
        use_lowrank_for_large=True,
    )
    metrics.update(spectral)

    # Drift metrics
    step_size = float(getattr(system.dynamics.config, "step_size", 0.0))
    if step_size > 0:
        drift = drift_metrics(step_fn, settled_hidden, step_size)
        metrics.update(drift)


def compute_energy_metrics(system: Any, *, batch_size: int) -> dict[str, float]:
    """Per-step energy from the substrate's own per-MAC model."""
    from computronium.experiment.execution.settle_operator import layer_weight_shapes

    metrics: dict[str, float] = {}
    estimator = getattr(system.substrate, "estimate_energy", None)
    if estimator is None:
        return metrics

    shapes = layer_weight_shapes(system.geometry)
    if not shapes:
        return metrics

    forward = update = 0.0
    per_sample = 0.0
    for out_features, in_features in shapes:
        estimate = estimator(
            input_shape=(batch_size, in_features),
            weight_shape=(out_features, in_features),
            batch_size=batch_size,
        )
        forward += float(estimate.get("forward_energy_per_batch", 0.0))
        update += float(estimate.get("update_energy_per_batch", 0.0))
        per_sample += float(estimate.get("energy_per_sample", 0.0))

    metrics["forward_energy_per_batch"] = forward
    metrics["update_energy_per_batch"] = update
    metrics["energy_per_batch"] = forward + update
    metrics["energy_per_sample"] = per_sample
    metrics["macs_per_step"] = float(
        batch_size * 2 * sum(out * inn for out, inn in shapes)
    )
    metrics["energy_per_mac"] = (
        (forward + update) / metrics["macs_per_step"]
        if metrics["macs_per_step"] > 0
        else 0.0
    )
    return metrics


def compute_plasticity_metrics(system: Any) -> dict[str, float]:
    """Plasticity objectives: psi capacity, consolidation cost, rewrite rate."""
    metrics: dict[str, float] = {}
    plasticity = getattr(system, "plasticity", None)
    if plasticity is None:
        return metrics

    # Check if it's a NullPlasticity (5-D system)
    from computronium.state import NullPlasticity

    if isinstance(plasticity, NullPlasticity):
        return metrics

    # Get plastic state dimensions from config
    plastic_dims = getattr(plasticity, "config", None)
    if plastic_dims is None:
        return metrics

    # Handle both PlasticityConfig (with plastic_state_dims) and specific
    # plasticity configs (like ConflictAdaptivePsiConfig) that don't have it
    plastic_state_dims = getattr(plastic_dims, "plastic_state_dims", None)
    if plastic_state_dims is None:
        # Try to get from consolidation_config for temporal_psi types
        consolidation = getattr(plastic_dims, "consolidation_config", None)
        if consolidation and "trace_decay" in consolidation:
            # temporal_psi / conflict_adaptive: plastic state is implicit in trace
            # Return 0 for now; would need to track actual ψ dimensions
            return metrics
        return metrics

    # psi_capacity: sum of all plastic state dimensions
    psi_capacity = sum(plastic_state_dims.values())
    metrics["psi_capacity"] = float(psi_capacity)

    # consolidation_cost: estimate FLOPs for ψ→θ consolidation
    # For fast_weights: consolidation is a low-rank update (fast_weight_dim * param_count)
    # For routing: consolidation is gate logit integration (gate_dim * param_count)
    # For rule_state: consolidation is operator selection (num_operators * operator_dim)
    # Use a heuristic: psi_capacity * hidden_dim (typical consolidation cost)
    hidden_dim = 256  # Typical hidden dimension
    if hasattr(system.geometry, "config") and hasattr(
        system.geometry.config, "hidden_dim"
    ):
        hidden_dim = system.geometry.config.hidden_dim
    consolidation_flops = psi_capacity * hidden_dim * 2  # 2 FLOPs per MAC
    metrics["consolidation_cost"] = float(consolidation_flops)

    # rewrite_rate: placeholder (requires tracking psi over episodes)
    # Set to 0.0 for now; would need multi-episode tracking
    metrics["rewrite_rate"] = 0.0

    return metrics


def _compute_substrate_objectives(
    coordinate: Coordinate,
    metrics: dict[str, float],
    walltime_s: float,
) -> dict[str, float]:
    """Compute substrate-specific objectives."""
    from computronium.ontology.substrate._substrate import SubstrateConfig
    from computronium.ontology.substrate.spec import (
        SubstrateSpec,
        compute_substrate_objectives,
    )

    name_lower = coordinate.substrate.lower()
    factory_map = {
        "digital": SubstrateConfig.digital,
        "analog": SubstrateConfig.analog,
        "memristive": SubstrateConfig.memristive,
        "neuromorphic": SubstrateConfig.neuromorphic,
        "optical": SubstrateConfig.optical,
        "quantum": SubstrateConfig.quantum,
        "sparse": SubstrateConfig.sparse,
        "ternary": SubstrateConfig.ternary,
        "complex": SubstrateConfig.complex,
    }
    factory = factory_map.get(name_lower, SubstrateConfig.digital)
    dynamics_name = coordinate.dynamics
    if dynamics_name in {"diffusion", "spike_integration", "pc_alm"}:
        substrate_config = factory(noise_level=0.05)
    else:
        substrate_config = factory()
    substrate_spec = SubstrateSpec.from_config(substrate_config)
    settle_telemetry = {
        "energy_per_step": metrics.get("energy_per_step", 0.0),
        "settle_steps_used": metrics.get("settle_steps", 0),
        "free_energy_final": metrics.get(
            "hopfield_energy", metrics.get("free_energy", 0.0)
        ),
        "spike_rate": metrics.get("spike_rate", 0.0),
        "event_density": metrics.get("event_density", 0.0),
    }
    runtime_stats = {
        "walltime_s": walltime_s,
        "memory_mb": metrics.get("memory_usage", 0.0),
        "flops": metrics.get("flops", 0.0),
        "latency_ms": metrics.get("latency_ms", 0.0),
    }
    substrate_objectives = compute_substrate_objectives(
        substrate_spec, settle_telemetry, runtime_stats
    )
    return substrate_objectives


def _extract_convergence_curve(
    schedule: Schedule, history: list[dict[str, float]]
) -> list[dict[str, float]] | None:
    """Extract convergence curve for L1/L2 fidelity."""
    if schedule.fidelity not in {"L1", "L2", "L3"} or not history:
        return None
    curve_keys = {"train_loss", "val_loss", "train_acc", "val_acc", "learning_rate"}
    return [
        {
            **{k: float(v) for k, v in epoch.items() if k in curve_keys},
            "epoch": i + 1,
        }
        for i, epoch in enumerate(history)
    ]
