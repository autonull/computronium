"""TileNet Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.tile",
    kind="algorithm",
    name="TileNet",
    family="modular",
    reference_entrypoint="computronium.algorithms.tile.reference.step",
    kernel_entrypoint="computronium.algorithms.tile.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    uses_primitives=(
        "primitive.geometry.tile_mesh",
        "primitive.state_dynamics.instantaneous",
        "primitive.credit_assignment.backprop",
        "primitive.parameter_update.euclidean",
    ),
    summary="TileNet: modular tiled architecture with local connectivity.",
    equations="""
    Tiles: groups of neurons with local connectivity
    Routing: sparse inter-tile connections
    """,
    invariants=(
        "structured sparsity within tiles",
        "deterministic under fixed seed",
    ),
    notes="Kernel may accelerate tile routing operations.",
    tags=("tile_net", "modular", "structured_sparsity", "geometry"),
)
