"""Energy Minimization Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.energy_minimization",
    kind="primitive",
    name="Energy Minimization",
    axis="state_dynamics",
    reference_entrypoint=(
        "computronium.primitives.state_dynamics.energy_minimization.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.state_dynamics.energy_minimization.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Energy-based settling (Equilibrium Propagation, Hopfield, CHL).",
    equations="""
Free energy: F = -1/2 Σ_ij W_ij s_i s_j - Σ_i b_i s_i
Dynamics: τ ds/dt = -∂F/∂s + noise
Heavy-ball: v ← μ·v - η·∂F/∂s; s ← s + v
    """,
    invariants=(
        "free energy decreases or remains bounded",
        "state remains finite",
        "deterministic under fixed seed",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "equilibrium_propagation",
        "hopfield",
        "energy_based",
    ),
)
