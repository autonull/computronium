"""Euclidean Update Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.parameter_update.euclidean",
    kind="primitive",
    name="Euclidean Update",
    axis="parameter_update",
    reference_entrypoint=(
        "computronium.primitives.parameter_update.euclidean.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.parameter_update.euclidean.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Standard Euclidean parameter update (SGD with optional momentum).",
    equations="""
    v ← μv + g
    Δθ = −lr · v
    """,
    invariants=(
        "deterministic under fixed seed",
        "parameters updated in-place or returned as new dict",
        "momentum buffers preserved across steps",
        "global-norm gradient clipping applied if configured",
    ),
    notes="Reference implementation delegates to EuclideanUpdate ontology class. Kernel acceleration targets momentum update and clipping.",
    tags=("sgd", "momentum", "euclidean", "parameter_update"),
)
