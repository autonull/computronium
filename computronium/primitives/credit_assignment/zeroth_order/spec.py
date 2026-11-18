"""Zeroth-order estimator primitive specification."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.zeroth_order",
    kind="primitive",
    name="Zeroth Order Credit",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.zeroth_order.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.zeroth_order.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Gradient-free SPSA finite-difference estimator (two forwards).",
    equations="""
    Δ ~ Rademacher(θ)
    ĝ = (1/n) Σ (L(θ + cΔ_i) − L(θ − cΔ_i)) / (2c) · Δ_i
    """,
    invariants=(
        "deterministic under fixed seed",
        "no reverse-mode graph",
        "unbiased on a quadratic objective",
        "variance falls as 1/√n pairs",
    ),
    notes=(
        "Reference wraps ZerothOrderCredit; the kernel falls back to it "
        "until a fused two-forward device path lands."
    ),
    tags=("zeroth_order", "spsa", "finite_difference", "gradient_free", "estimator"),
    task_families=('vision',),
    available=True,
    capability_card="Zeroth-order (ES) credit; gradient-free; high query complexity",
)
