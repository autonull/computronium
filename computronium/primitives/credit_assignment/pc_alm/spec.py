"""PC-ALM Credit Assignment Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.pc_alm",
    kind="primitive",
    name="PC-ALM Credit Assignment",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.pc_alm.reference.step"
    ),
    kernel_entrypoint=("computronium.primitives.credit_assignment.pc_alm.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    summary="Local Hebbian credit assignment using dual variables from PCALMDynamics.",
    equations="""
    ΔW_l = -λ_l @ h_{l-1}^T / batch

    where λ_l are the dual variables (Lagrange multipliers) from the
    primal-dual settling dynamics of PCALMDynamics.
    """,
    invariants=(
        "dual variables are produced by PCALMDynamics settling",
        "weight updates are local Hebbian (pre × post)",
        "deterministic under fixed seed",
        "credit_norm normalization options: relative, rms, spectral",
    ),
    notes="Accelerated kernel should preserve the pseudo-gradient within tolerance. "
    "Requires PCALMDynamics to provide dual_vars in state.metrics or state.dual_vars.",
    tags=("predictive_coding", "augmented_lagrangian", "local_learning", "hebbian"),
)
