"""Hard top-k Routing Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.routing",
    kind="primitive",
    name="Routing Geometry",
    axis="geometry",
    reference_entrypoint=("computronium.primitives.geometry.routing.reference.forward"),
    kernel_entrypoint=("computronium.primitives.geometry.routing.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary=(
        "Hard top-k mixture-of-experts topology: a trunk, a gate, and one "
        "readout over k selected experts."
    ),
    equations="""
    h = φ(W_trunk x + b_trunk)
    g = W_gate h + b_gate
    w = topk(softmax(g / τ)) / k        # hard selection, renormalized
    z = Σ_i w_i φ(W_i h + b_i)
    y = W_readout z + b_readout
    """,
    invariants=(
        "output shape matches (batch, output_dim)",
        "exactly top_k selection weights are non-zero per sample",
        "selection weights sum to 1 per sample",
        "deterministic under fixed seed",
        "activations remain finite",
    ),
    notes=(
        "Reference delegates to RoutingGeometry. The straight-through "
        "relaxation is the credit's pass (SurrogateCredit); the forward "
        "stays hard. Kernel falls back to reference (Triton TODO)."
    ),
    tags=("routing", "moe", "top_k", "sparse_selection", "gating"),
)
