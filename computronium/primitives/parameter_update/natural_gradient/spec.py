"""Natural Gradient Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.natural_gradient",
    kind="primitive",
    name="Natural Gradient",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.natural_gradient.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.parameter_update.natural_gradient.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Natural gradient parameter update with Fisher geometry preconditioning.",
    equations="""
Δθ = −lr · (F + λI)⁻¹ · g
""",
    invariants=(
        "deterministic under fixed seed",
        "parameters updated in-place or returned as new dict",
        "momentum buffers preserved across steps",
        "Fisher diagonal EMA updated per step",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "natural_gradient",
        "fisher",
        "parameter_update",
    ),
)
