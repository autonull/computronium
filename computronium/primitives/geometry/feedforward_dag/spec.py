"""Feedforward DAG Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.feedforward_dag",
    kind="primitive",
    name="Feedforward DAG Geometry",
    axis="geometry",
    reference_entrypoint=(
        "computronium.primitives.geometry.feedforward_dag.reference.forward"
    ),
    kernel_entrypoint=(
        "computronium.primitives.geometry.feedforward_dag.kernel.forward"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
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
