"""Feedforward DAG Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.feedforward",
    kind="primitive",
    name="Feedforward Geometry",
    axis="geometry",
    reference_entrypoint=(
        "computronium.primitives.geometry.feedforward.reference.forward"
    ),
    kernel_entrypoint=("computronium.primitives.geometry.feedforward.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Standard feedforward DAG topology (MLP/CNN) with configurable depth and width.",
    equations="""
    h_l = σ(W_l · h_{l-1} + b_l)  # layer-wise computation
    forward: sequential application of Linear + activation layers
    """,
    invariants=(
        "output shape matches (batch, output_dim)",
        "deterministic under fixed seed",
        "activations remain finite",
    ),
    notes="Reference implementation delegates to FeedforwardGeometry. Kernel falls back to reference (Triton TODO).",
    tags=("feedforward", "mlp", "dag", "sequential"),
)
