"""Local Goodness Credit Assignment primitive specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.local_goodness",
    kind="primitive",
    name="Local Goodness Credit",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.local_goodness.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.local_goodness.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_verified",
    summary="Layer-local contrastive credit assignment (Forward-Forward and LEMMA variants).",
    equations="""
    FF mode: ΔW_l ∝ -∇_W (G_free - G_nudged)_l
    LEMMA mode: ΔW_l ∝ -(e₁ @ B_lᵀ)ᵀ a_pre
    """,
    invariants=(
        "pseudo-gradient is deterministic under fixed seed",
        "hidden layer updates are local (no inverse pass)",
        "LEMMA fixed-B uses orthogonal random projections",
    ),
    notes="Two modes: 'ff' (Forward-Forward) uses autograd of goodness contrast; 'lemma' uses closed-form fixed/learned feedback. Kernel acceleration available via ff_kernels Triton backends.",
    tags=("forward_forward", "lemma", "local_credit", "contrastive"),
)
