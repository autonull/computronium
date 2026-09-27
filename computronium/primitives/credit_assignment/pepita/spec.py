"""PEPITA Credit Assignment Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.pepita",
    kind="primitive",
    name="PEPITA Credit Assignment",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.pepita.reference.step"
    ),
    kernel_entrypoint=("computronium.primitives.credit_assignment.pepita.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    summary="Published PEPITA (Dellaferrera & Kreiman 2022): input-modulated second forward pass, exact autograd gradient.",
    equations="""
    δ = y − softmax(logits₁)  # output error from first pass
    x̃ = x + γ·δBᵀ             # modulated input with fixed random B
    ΔW = ∇_W CE(f(x̃), y)      # exact autograd gradient of modulated pass
    """,
    invariants=(
        "single fixed random feedback matrix B (out×in)",
        "error modulation in second forward pass",
        "autograd update on perturbed states",
        "deterministic under fixed seed",
        "peak memory is backprop-class",
    ),
    notes="Distinct from Forward-Forward: uses error signal, not label injection. Distinct from LEMMA: uses autograd of modulated pass, not closed-form per-layer update.",
    tags=("pepita", "local_learning", "error_modulated", "random_feedback", "autograd"),
)
