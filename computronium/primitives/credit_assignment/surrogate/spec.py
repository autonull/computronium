"""Straight-through surrogate credit primitive specification."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.surrogate",
    kind="primitive",
    name="Surrogate Credit",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.surrogate.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.surrogate.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Straight-through gradient of a hard top-k expert selection.",
    equations="""
    h = φ(W_trunk x + b_trunk)
    g = W_gate h + b_gate
    w = topk(softmax(g / τ)) / k
    w̃ = w + softmax(g / τ) − softmax(g / τ).detach()
    ĝ = ∇_θ L(θ; w̃)
    """,
    invariants=(
        "deterministic under fixed seed",
        "the hard forward is unchanged; only its derivative is relaxed",
        "the true gradient of the hard selection is zero almost everywhere",
    ),
    notes=(
        "Reference wraps SurrogateCredit; the kernel falls back to it until a "
        "fused top-k surrogate lands. Reuses the routing geometry's gate and "
        "temperature — the exact parabola has no derivative to estimate."
    ),
    tags=("surrogate", "straight_through", "gumbel", "top_k", "routing", "biased"),
)
