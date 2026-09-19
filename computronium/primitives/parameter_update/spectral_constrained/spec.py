"""Spectral Constrained Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.spectral_constrained",
    kind="primitive",
    name="Spectral Constrained",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.spectral_constrained.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.parameter_update.spectral_constrained.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Spectral-constrained parameter update.",
    equations="""
ΔW = -η * P(W) where P projects onto spectral norm ball
    """,
    invariants=(
        "deterministic under fixed seed",
        "spectral norm of update is bounded",
    ),
    notes="Reference wraps SpectralConstrainedUpdate; kernel falls back to reference",
    tags=(
        "spectral",
        "constrained",
        "update",
        "regularization",
    ),
)
