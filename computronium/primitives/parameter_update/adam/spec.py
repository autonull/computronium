"""Adam Update Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.adam",
    kind="primitive",
    name="Adam Update",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.adam.reference.step"
    ),
    kernel_entrypoint=("computronium.primitives.parameter_update.adam.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Per-coordinate first/second-moment adaptive update with bias correction.",
    equations="""
m <- beta1*m + (1-beta1)g;  v <- beta2*v + (1-beta2)g^2
Delta theta = -lr * m_hat / (sqrt(v_hat) + eps)
    """,
    invariants=(
        "deterministic under fixed seed",
        "first and second moment buffers preserved across steps",
        "bias correction applied to both moments",
    ),
    notes="The per-coordinate second-moment family, distinct from euclidean (plain SGD).",
    tags=(
        "adam",
        "adaptive",
        "second_moment",
        "parameter_update",
    ),
)
