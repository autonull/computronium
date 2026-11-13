"""Local Adam Update Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.local_adam",
    kind="primitive",
    name="Local Adam Update",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.local_adam.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.parameter_update.local_adam.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Per-tensor scalar second moment (LAMB-style) over a first-moment direction.",
    equations="""
v <- beta2*v + (1-beta2)*mean(g^2) per tensor
Delta theta = -lr * m_hat / (sqrt(v_hat) + eps)
    """,
    invariants=(
        "deterministic under fixed seed",
        "one scalar second moment per tensor",
        "bias correction applied",
    ),
    notes="Local (per-tensor) adaptivity rather than per-coordinate.",
    tags=(
        "adam",
        "local",
        "lamb",
        "parameter_update",
    ),
)
