"""Random Projections Credit Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.random_projections",
    kind="primitive",
    name="Random Projections Credit",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.random_projections.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.random_projections.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_verified",
    summary="Fixed random feedback matrix credit assignment (Feedback Alignment).",
    equations="""
    δ_l = B_{l+1} δ_{l+1} ⊙ f'(h_l)       # error signal via fixed random feedback
    ΔW_l = η · δ_l h_{l-1}^T               # weight update
    """,
    invariants=(
        "feedback matrices are fixed (not learned)",
        "feedback matrices are not transposes of forward weights",
        "deterministic under fixed seed",
    ),
    notes="Accelerated kernel should preserve the pseudo-gradient within tolerance.",
    tags=("feedback_alignment", "dfa", "random_feedback"),
)
