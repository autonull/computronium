"""PC-ALM Settling Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.pc_alm_settling",
    kind="primitive",
    name="PC-ALM Settling",
    axis="state_dynamics",
    reference_entrypoint=(
        "computronium.primitives.state_dynamics.pc_alm_settling.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.state_dynamics.pc_alm_settling.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    summary="Primal-dual settling dynamics for PC-ALM.",
    equations="""
    c_l = h_l - f_θ_l(h_{l-1})                  # constraint violation
    λ_l ← λ_l + step_size · (c_l + α·λ_l)       # dual update (PI controller)
    h_l ← h_l - step_size · [c_l + λ_l + ρ·c_l
          - J_{l+1}^T·(c_{l+1} + λ_{l+1} + ρ·c_{l+1})]  # primal update
    """,
    invariants=(
        "settling residual decreases or remains bounded",
        "state remains finite",
        "deterministic under fixed seed",
    ),
    notes="Accelerated kernel should preserve the settled state within tolerance.",
    tags=("predictive_coding", "augmented_lagrangian", "settling"),
)
