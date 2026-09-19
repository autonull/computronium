"""Null Plasticity Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.plasticity.null",
    kind="primitive",
    name="Null Plasticity",
    axis="plasticity",
    reference_entrypoint=("computronium.primitives.plasticity.null.reference.step"),
    kernel_entrypoint=("computronium.primitives.plasticity.null.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Null plasticity (zero-extension): plastic state unchanged, makes 5-D systems valid 6-D coordinates.",
    equations="""
    ψ_{t+1} = ψ_t
    """,
    invariants=(
        "deterministic under fixed seed",
        "plastic state returned unchanged",
        "no plastic state allocated initially",
    ),
    notes="Reference implementation delegates to NullPlasticity ontology class. This is the identity primitive for plasticity axis.",
    tags=("null", "zero_extension", "identity", "plasticity"),
)
