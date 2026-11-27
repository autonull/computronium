"""Joint Architecture Benchmark Experiments.

This package contains the 5 benchmark levels for the joint architecture:
- Level 1: Adaptation Efficiency
- Level 2: Compute Efficiency
- Level 3: Structural Robustness
- Level 3.5: Algorithm Migration
- Level 4: Z3 Fixed Weights

Additional benchmark suites (new):
- Credit Assignment Scaling (depth scaling for credit methods)
- Substrate Precision Scaling (precision vs substrate trade-offs)
- Stability-Plasticity Frontier (ρ sweep × plasticity types)

Each suite result carries a ``claims_scope`` audit status (see
``_claims.py``): L3.5 and L3 are ``plumbing_only`` (no ψ mediation in the
forward loop today); L1 and L2 are ``psi_wired_uncontrolled`` — ψ is stepped
inside forward and modulates computation (plasticity types empirically
differentiate), but θ trains concurrently and no frozen-θ control exists, so
they are suggestive rather than clean ψ evidence. Z3 is ``psi_engaged``
(R8 gate landed 2026-09-01): every ``evaluate_z3`` run embeds its own
engagement gate + planted-ψ control and downgrades itself to
``plumbing_only`` when the gate fails. Rewiring L1/L2 with frozen-θ phases +
``ThetaInvarianceAudit`` remains open and would upgrade their status.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from computronium.benchmarks.joint._claims import (
    CLAIMS_SCOPE_PLUMBING_ONLY,
    CLAIMS_SCOPE_PSI_ENGAGED,
    CLAIMS_SCOPE_PSI_WIRED_UNCONTROLLED,
)

if TYPE_CHECKING:
    # Pyright and the IDE resolve the suites through these names. At runtime
    # they are imported by `from computronium.benchmarks.joint import *`, which
    # imports each name in ``__all__``; the block itself never runs.
    from computronium.benchmarks.joint import (  # ruff: ignore[runtime-import-in-type-checking-block]
        adaptation_efficiency,
        algorithm_migration,
        compute_efficiency,
        credit_assignment_scaling,
        stability_plasticity_frontier,
        structural_robustness,
        substrate_precision_scaling,
        z3_fixed_weights,
    )

__all__ = [
    "CLAIMS_SCOPE_PLUMBING_ONLY",
    "CLAIMS_SCOPE_PSI_ENGAGED",
    "CLAIMS_SCOPE_PSI_WIRED_UNCONTROLLED",
    "adaptation_efficiency",
    "algorithm_migration",
    "compute_efficiency",
    "credit_assignment_scaling",
    "stability_plasticity_frontier",
    "structural_robustness",
    "substrate_precision_scaling",
    "z3_fixed_weights",
]
