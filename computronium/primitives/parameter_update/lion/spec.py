"""Lion Update Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.lion",
    kind="primitive",
    name="Lion Update",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.lion.reference.step"
    ),
    kernel_entrypoint=("computronium.primitives.parameter_update.lion.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Sign of the momentum interpolant with one O(1) buffer and no second moment.",
    equations="""
Delta theta = -lr * sign(beta1*m + (1-beta1)g);  m <- beta2*m + (1-beta2)g
    """,
    invariants=(
        "deterministic under fixed seed",
        "one momentum buffer only",
        "no bias correction and no second moment",
    ),
    notes="Per-coordinate sign steps; the effective displacement is lr-driven.",
    tags=(
        "lion",
        "sign",
        "momentum",
        "parameter_update",
    ),
    task_families=('vision', 'sequence'),
    available=True,
    capability_card="Lion optimizer; sign-based; memory efficient",
)
