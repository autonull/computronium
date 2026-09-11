"""stability — Calibrated stability guard for dynamical neural systems.

Calibrated on:
- Settling/energy-based dynamics (energy minimization, predictive settling)
- Non-normal linear dynamics (Ginibre ensemble)
- 16 real substrate × settling-dynamics coordinates
  (windowed growth = 1.000, FKR 0% at τ=1.029)

Scope statement (mandatory v1):
This guard is calibrated for energy-minimization
coordinates and non-normal linear dynamics.
General-transformer collapse detection is future calibration
work, not a v1 claim.

Quick start:
    import torch
    from stability import attach, StabilityVerdict

    model = torch.nn.Linear(10, 10)
    guard = attach(model)

    for step in range(100):
        x = torch.randn(32, 10)
        y = model(x)
        verdict = guard.check({"x": x, "y": y, "loss": y.pow(2).mean()})
        if verdict.kill:
            print(f"Killed at step {step}: {verdict}")
            break

CLI:
    stability check --gain 1.2
    stability calibrate
    stability statistic --kind windowed_growth --gain 1.2
"""

from stability.basin import (
    BasinStabilityEstimator,
    estimate_basin_stability,
    estimate_basin_stability_multistart,
)
from stability.calibration import (
    OVERHEAD_BUDGET,
    PR5Calibration,
    calibrate_ginibre_harvest,
    ginibre_run,
    harvest_bad_statistics,
    harvest_good_statistics,
    probe_interval_for_overhead,
    unrolled_divergence,
)
from stability.config import (
    BasinConfig,
    GuardConfig,
    JacobianAmplificationConfig,
    LyapunovConfig,
    SettlingConfig,
    create_basin_estimator,
    create_guard,
    create_jacobian_amplification_estimator,
    create_lyapunov_estimator,
    create_settling_monitor,
)
from stability.frontier import (
    FrontierAggregator,
    FrontierRecord,
)
from stability.guard import (
    DEFAULT_TAU,
    ExternalTransitionFn,
    GuardDecision,
    GuardHandle,
    StabilityGuard,
    StabilityVerdict,
    StatisticKind,
    StepState,
    attach,
    calibrate_threshold,
    measure_guard_overhead,
    quantify_proxy_disagreement,
)
from stability.lyapunov import (
    LyapunovEstimator,
    estimate_lyapunov_exponent,
    estimate_lyapunov_spectrum,
)
from stability.matrices import (
    jordan_block,
    linear_transition,
    realized_rho,
    realized_sigma_max,
    rotation,
    verify_spectrum,
)
from stability.resources import ResourceUsage
from stability.settling import (
    SettlingMonitor,
    measure_settling_time,
    measure_settling_time_full_state,
)
from stability.spectral_radius import (
    JacobianAmplificationEstimator,
    dominant_singular_value,
    estimate_directional_amplification,
    spectral_radius_from_jacobian,
)

__version__ = "0.1.0"

__all__ = [  # ruff: ignore[unsorted-dunder-all]
    # Guard API (primary)
    "attach",
    "StabilityGuard",
    "StabilityVerdict",
    "GuardHandle",
    "GuardDecision",
    "DEFAULT_TAU",
    "calibrate_threshold",
    "quantify_proxy_disagreement",
    "measure_guard_overhead",
    # Spectral radius
    "JacobianAmplificationEstimator",
    "estimate_directional_amplification",
    "dominant_singular_value",
    "spectral_radius_from_jacobian",
    # Lyapunov
    "LyapunovEstimator",
    "estimate_lyapunov_exponent",
    "estimate_lyapunov_spectrum",
    # Settling
    "SettlingMonitor",
    "measure_settling_time",
    "measure_settling_time_full_state",
    # Basin stability
    "BasinStabilityEstimator",
    "estimate_basin_stability",
    "estimate_basin_stability_multistart",
    # Frontier
    "FrontierRecord",
    "FrontierAggregator",
    # Resources
    "ResourceUsage",
    # Config + Factories
    "JacobianAmplificationConfig",
    "LyapunovConfig",
    "SettlingConfig",
    "BasinConfig",
    "GuardConfig",
    "create_jacobian_amplification_estimator",
    "create_lyapunov_estimator",
    "create_settling_monitor",
    "create_basin_estimator",
    "create_guard",
    # Type aliases
    "StepState",
    "ExternalTransitionFn",
    "StatisticKind",
    # Ginibre calibration
    "PR5Calibration",
    "calibrate_ginibre_harvest",
    "harvest_good_statistics",
    "harvest_bad_statistics",
    "probe_interval_for_overhead",
    "unrolled_divergence",
    "ginibre_run",
    "OVERHEAD_BUDGET",
    # Stable-matrix helpers (Phase 6A)
    "jordan_block",
    "rotation",
    "linear_transition",
    "realized_rho",
    "realized_sigma_max",
    "verify_spectrum",
]
