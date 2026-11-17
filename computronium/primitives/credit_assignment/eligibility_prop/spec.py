"""Specification for the e-prop temporal estimator (TODO93 §19)."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.eligibility_prop",
    kind="primitive",
    name="Eligibility Propagation Credit",
    axis="credit_assignment",
    reference_entrypoint="computronium.primitives.credit_assignment.eligibility_prop.reference.step",
    kernel_entrypoint="computronium.primitives.credit_assignment.eligibility_prop.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Temporal credit by a decaying eligibility trace times a readout signal.",
    equations="""
    e_t = α e_{t−1} + D_t ψ_t;  ĝ = Σ_t Σ_b L_t e_t
    """,
    invariants=("the learning signal comes from the readout alone", "the trace decays with α at every step", "no reverse-mode graph crosses the recurrence"),
    notes="The reference wraps EligibilityPropCredit; the kernel falls back to it until a fused device path lands.",
    tags=("eligibility_prop", "temporal", "trace", "credit"),
)
