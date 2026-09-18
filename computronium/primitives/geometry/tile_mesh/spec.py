"""Tile Mesh Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.tile_mesh",
    kind="primitive",
    name="Tile Mesh Geometry",
    axis="geometry",
    reference_entrypoint=(
        "computronium.primitives.geometry.tile_mesh.reference.forward"
    ),
    kernel_entrypoint=("computronium.primitives.geometry.tile_mesh.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    summary="TileNet mesh topology with modular independent tiles and local routing.",
    equations="""
    h_l = σ(W_l · h_{l-1} + b_l)  # per-tile computation
    routing: parallel within layer, sequential across layers
    """,
    invariants=(
        "output shape matches (batch, output_dim)",
        "deterministic under fixed seed",
        "tile activities remain finite",
    ),
    notes="Accelerated kernel uses Triton for fused tile activity updates.",
    tags=("tilenet", "modular", "local_routing", "async"),
)
