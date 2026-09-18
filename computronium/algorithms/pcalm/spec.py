"""PC-ALM Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.pcalm",
    kind="algorithm",
    name="PC-ALM",
    family="predictive_coding",
    reference_entrypoint="computronium.algorithms.pcalm.reference.step",
    kernel_entrypoint="computronium.algorithms.pcalm.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    uses_primitives=(
        "primitive.state_dynamics.pc_alm_settling",
        "primitive.credit_assignment.pc_alm",
    ),
    summary="Augmented Lagrangian Predictive Coding.",
    equations="""
    L_ρ = Σₗ ½‖hₗ − f_θₗ(hₗ₋₁)‖² + Σₗ ⟨λₗ, hₗ − f_θₗ(hₗ₋₁)⟩
          + (ρ/2) Σₗ ‖hₗ − f_θₗ(hₗ₋₁)‖²

    Dynamics (discretized):
        cₗ = hₗ − f_θₗ(hₗ₋₁)         # constraint violation
        λₗ ← λₗ + step_size · cₗ       # dual update (PI controller)
        hₗ ← hₗ − step_size · (cₗ + λₗ + ρ·cₗ − Jₗ₊₁ᵀ·(cₗ₊₁ + λₗ₊₁ + ρ·cₗ₊₁))

    Weight update (local Hebbian):
        ΔWₗ ∝ −λₗ hₗ₋₁ᵀ
    """,
    invariants=(
        "local error signals remain bounded",
        "settling dynamics are deterministic under fixed seed",
        "slow parameters are not mutated during intra-episode steps",
    ),
    notes="Kernel should fuse the primal-dual settle loop where possible.",
    tags=("predictive_coding", "augmented_lagrangian", "local_learning"),
)
