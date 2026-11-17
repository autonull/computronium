"""Specification for the exact RTRL reference (TODO93 §19)."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.rtrl_reference",
    kind="primitive",
    name="RTRL Reference",
    axis="credit_assignment",
    reference_entrypoint="computronium.primitives.credit_assignment.rtrl_reference.reference.step",
    kernel_entrypoint="computronium.primitives.credit_assignment.rtrl_reference.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Exact per-step recurrent Jacobian; the temporal parity reference.",
    equations="""
    J_t = D_t (W_rec J_{t−1} + Γ_t);  ĝ = Σ_t Σ_b L_t J_t
    """,
    invariants=("the Jacobian is retained for every step", "the reference fixes the temporal credits' parity", "the learning signal comes from the readout alone"),
    notes="The reference wraps RTRLReference; the kernel falls back to it until a fused device path lands.",
    tags=("rtrl", "reference", "temporal", "credit"),
)
