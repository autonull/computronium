"""Closed-form Ridge Plasticity Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.plasticity.closed_form_ridge",
    kind="primitive",
    name="Closed-form Ridge Plasticity",
    axis="plasticity",
    reference_entrypoint=(
        "computronium.primitives.plasticity.closed_form_ridge.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.plasticity.closed_form_ridge.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Closed-form ridge regression plasticity for supervised fast-weight computation.",
    equations="""
W = Y X^T (X X^T + λI)^{-1}
""",
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "closed-form solution is exact",
    ),
    notes="Reference implementation delegates to ClosedFormRidgePlasticity.",
    tags=(
        "plasticity",
        "closed_form_ridge",
        "ridge_regression",
        "supervised",
    ),
)
