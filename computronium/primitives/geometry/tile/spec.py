"""Tile Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.tile",
    kind="primitive",
    name="Tile Geometry",
    axis="geometry",
    reference_entrypoint=("computronium.primitives.geometry.tile.reference.forward"),
    kernel_entrypoint=("computronium.primitives.geometry.tile.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="TileNet with a tile graph the tile count is derived into.",
    equations="""
h ← route_tiles(input), tile-local weights, layer-wise routing
    """,
    invariants=(
        "deterministic under fixed seed",
        "tile graph preserved",
        "state remains finite",
    ),
    notes="`tile_mesh` is the fixed-mesh variant of this same class; this coordinate derives the tile count from the graph.",
    tags=(
        "geometry",
        "tile",
        "tilenet",
        "modular",
    ),
)
