"""Spatial Lattice 3D Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.spatial_lattice_3d",
    kind="primitive",
    name="Spatial Lattice 3D Geometry",
    axis="geometry",
    reference_entrypoint=(
        "computronium.primitives.geometry.spatial_lattice_3d.reference.forward"
    ),
    kernel_entrypoint=(
        "computronium.primitives.geometry.spatial_lattice_3d.kernel.forward"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="3D spatial lattice topology with local connectivity for neural cellular automata and spatial computation.",
    equations="""
    x_{i,j,k}' = σ(Σ_{n∈N(i,j,k)} W_n · x_n + b)
    N(i,j,k) = neighbors within radius r in 3D lattice
    """,
    invariants=(
        "output shape matches (batch, output_dim)",
        "deterministic under fixed seed",
        "activations remain finite",
        "local connectivity preserved",
    ),
    notes="Reference implementation delegates to SpatialLattice3DGeometry. Kernel falls back to reference (Triton TODO).",
    tags=("spatial", "lattice", "3d", "local_connectivity", "nca"),
)
