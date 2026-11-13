"""Attention Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.attention",
    kind="primitive",
    name="Attention Geometry",
    axis="geometry",
    reference_entrypoint=(
        "computronium.primitives.geometry.attention.reference.forward"
    ),
    kernel_entrypoint=("computronium.primitives.geometry.attention.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Multi-head self-attention blocks with residual connections and layer norm.",
    equations="""
h = x;  h ← h + MHA(LN(h));  h ← h + FFN(LN(h))
    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "attention weights preserved",
    ),
    notes="Attention projections are routed through the substrate forward operator.",
    tags=(
        "geometry",
        "attention",
        "transformer",
    ),
)
