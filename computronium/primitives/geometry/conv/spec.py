"""Convolutional Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.conv",
    kind="primitive",
    name="Convolutional Geometry",
    axis="geometry",
    reference_entrypoint=("computronium.primitives.geometry.conv.reference.forward"),
    kernel_entrypoint=("computronium.primitives.geometry.conv.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Shared convolutional kernels applied to im2col patches, routed through the substrate operator.",
    equations="""
p = im2col(x);  h_i = fold(op(p, W_i) + b_i);  y = head(pool(h))
    """,
    invariants=(
        "deterministic under fixed seed",
        "grid topology preserved",
        "state remains finite",
    ),
    notes="Even kernel sizes are auto-corrected to the next odd value.",
    tags=(
        "geometry",
        "conv",
        "im2col",
    ),
    task_families=('vision',),
    available=True,
    capability_card="Convolutional geometry; translation equivariance; spatial hierarchies",
)
