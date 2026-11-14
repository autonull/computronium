"""Null Plasticity Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.plasticity.null",
    kind="primitive",
    name="Null Plasticity",
    axis="plasticity",
    batch_axis="unused",
    batch_axis_reason="returns the plastic state unchanged, by design",
    seed_sensitive=False,
    seed_free_reason="the returned state is the input state",
    reference_entrypoint=("computronium.primitives.plasticity.null.reference.step"),
    kernel_entrypoint=("computronium.primitives.plasticity.null.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
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
