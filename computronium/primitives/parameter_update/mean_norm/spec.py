"""Mean-Norm Update Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.mean_norm",
    kind="primitive",
    name="Mean-Norm Update",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.mean_norm.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.parameter_update.mean_norm.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Per-tensor mean-absolute-gradient normalization (the magnitude-only rung).",
    equations="""
Delta theta = -lr * g / (mean|g| + eps) per tensor
    """,
    invariants=(
        "deterministic under fixed seed",
        "direction preserved, magnitude normalized per tensor",
    ),
    notes="Simplified Fisher-geometry stand-in, not an inverse-Fisher preconditioner.",
    tags=(
        "mean_norm",
        "magnitude",
        "natural_gradient",
        "parameter_update",
    ),
)
