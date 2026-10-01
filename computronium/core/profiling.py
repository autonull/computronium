"""
Profiling utilities for Computronium.
"""

from typing import TYPE_CHECKING

import torch
from torch import nn

from computronium.stability.resources import MAC_ENERGY_J, ResourceUsage

if TYPE_CHECKING:
    from computronium.ontology.system import System


_SETTLE_MATMUL_MULTIPLIER = {
    "instantaneous": 1,
    "energy_minimization": -1,  # scale by max_steps
    "predictive_settling": -1,  # scale by max_steps
    "spike_integration": -1,    # scale by timesteps
    "pc_alm": -1,
    "lazy": -1,
    "diffusion": -1,
}

_TRAIN_STEP_MULTIPLIER = 2  # forward + backward (approx)


def estimate_train_step_flops(system: "System", batch_size: int) -> int:
    """Deterministic FLOP estimate for one ``train_step`` (latency proxy).

    Structure-derived only — no measurement, no RNG, no device dependence:
    for each weight matrix, ``2 * batch * fan_in * fan_out`` FLOPs per
    matmul round, scaled by the dynamics' settle structure. Intended as a
    *relative* comparator between systems (ordering, ratios); absolute
    latency needs the repeated-timing path in :func:`analyze_joint_system`.
    """
    from computronium.ontology._settle_kernel import extract_layered_params

    layered = extract_layered_params(system.geometry)
    if layered is None:
        raise ValueError("estimate_train_step_flops requires a layered geometry")
    dynamics_type = system.dynamics.config.dynamics_type
    multiplier = _SETTLE_MATMUL_MULTIPLIER.get(dynamics_type)
    if multiplier is None:
        raise ValueError(f"no settle matmul model for {dynamics_type!r}")
    if multiplier < 0:
        multiplier = float(system.dynamics.config.max_steps)
    forward = sum(
        2 * batch_size * int(w.shape[0]) * int(w.shape[1]) for w in layered.weights
    )
    return int(forward * multiplier * _TRAIN_STEP_MULTIPLIER)


def count_flops(model: nn.Module, input_shape: tuple[int, ...]) -> int:
    """Estimate FLOPs for a model using parameter counting.

    Counts ALL parameters — frozen (``requires_grad=False``) parameters
    still incur forward (and backward-through) FLOPs; a ψ-only migration
    with frozen θ is not free compute.

    For a more accurate count, use torch.profiler with record_function.
    """
    batch_size = input_shape[0] if input_shape else 1
    params = sum(p.numel() for p in model.parameters())
    return 2 * params * batch_size


def measure_suite_resources(
    model: nn.Module,
    *,
    coordinate: str,
    device: str,
    batch_size: int,
    elapsed_s: float,
    effective_flops: float | None = None,
) -> ResourceUsage:
    """Proxy-tier resource capture for benchmark suite runners.

    FLOPs are parameter-count estimates (forward + 2x backward); no hardware
    counters required.

    Args:
        model: The model to profile.
        coordinate: System coordinate identifier.
        device: Device string.
        batch_size: Batch size used.
        elapsed_s: Wall-clock time in seconds.
        effective_flops: Optional gate-entropy-aware effective FLOPs
            (overrides computed FLOPs for routing/sparse models).
    """
    forward_flops = count_flops(model, (batch_size,))
    if effective_flops is not None:
        forward_flops = int(effective_flops)
    return ResourceUsage(
        coordinate=coordinate,
        device=str(device),
        batch_size=batch_size,
        latency=elapsed_s,
        wall_time_ms=elapsed_s * 1000.0,
        compute=float(3 * forward_flops),
        forward_flops=forward_flops,
        backward_flops=2 * forward_flops,
        param_count=sum(p.numel() for p in model.parameters()),
        effective_flops=effective_flops if effective_flops is not None else 0.0,
        energy=float(3 * forward_flops * MAC_ENERGY_J),
    )