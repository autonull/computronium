"""Specification for the UORO temporal estimator (TODO93 §19)."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.unbiased_rtrl",
    kind="primitive",
    name="Unbiased Online RTRL Credit",
    axis="credit_assignment",
    reference_entrypoint="computronium.primitives.credit_assignment.unbiased_rtrl.reference.step",
    kernel_entrypoint="computronium.primitives.credit_assignment.unbiased_rtrl.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Unbiased rank-1 factored Jacobian for a recurrent cell.",
    equations="""
    θ̃_t = D_t (W_rec θ̃_{t−1}) + ν_t D_t u_t;  ĝ = Σ_t Σ_b L_t ⊙ θ̃_t ρ̃_t
    """,
    invariants=("the estimate is unbiased over the sign/row draws", "the rank-1 factors share one scale", "the learning signal comes from the readout alone"),
    notes="The reference wraps UnbiasedOnlineRTRLCredit; the kernel falls back to it until a fused device path lands.",
    tags=("unbiased_rtrl", "uoro", "temporal", "credit"),
    task_families=('sequence',),
    available=True,
    capability_card="Unbiased RTRL; exact online gradient for RNNs; high memory cost",
)
