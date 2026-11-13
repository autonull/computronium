"""Causal Transformer Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.causal_transformer",
    kind="primitive",
    name="Causal Transformer Geometry",
    axis="geometry",
    reference_entrypoint=(
        "computronium.primitives.geometry.causal_transformer.reference.forward"
    ),
    kernel_entrypoint=(
        "computronium.primitives.geometry.causal_transformer.kernel.forward"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Causal transformer language-model topology over token ids with a causal mask.",
    equations="""
h_0 = embed(ids);  h_B = block_B(h_{B−1});  logits = h_B W_out
    """,
    invariants=(
        "deterministic under fixed seed",
        "causal mask applied",
        "state remains finite",
    ),
    notes="Vision mode (patch_size > 0) patchifies images instead of embedding token ids.",
    tags=(
        "geometry",
        "transformer",
        "causal",
        "language_model",
    ),
)
