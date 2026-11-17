"""Forward-tangent estimator primitive specification."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.forward_tangent",
    kind="primitive",
    name="Forward Tangent Credit",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.forward_tangent.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.forward_tangent.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Unbiased pathwise gradient from random forward-mode tangents.",
    equations="""
    v ~ Rademacher(θ)
    d = jvp(f, θ, v)
    ĝ = (1/n) Σ d_i · v_i
    """,
    invariants=(
        "deterministic under fixed seed",
        "unbiased: E[ĝ] = ∇f(θ)",
        "variance falls as 1/√n tangents",
    ),
    notes=(
        "Reference wraps ForwardTangentCredit; the kernel falls back to it "
        "until a batched Triton jvp lands."
    ),
    tags=("forward_mode", "jvp", "pathwise", "unbiased", "estimator"),
)
