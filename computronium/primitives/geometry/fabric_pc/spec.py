"""Fabric PC Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.fabric_pc",
    kind="primitive",
    name="Fabric PC Geometry",
    axis="geometry",
    reference_entrypoint=(
        "computronium.primitives.geometry.fabric_pc.reference.forward"
    ),
    kernel_entrypoint=("computronium.primitives.geometry.fabric_pc.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Arbitrary node-edge graph topology for predictive coding (adapted from FabricPC).",
    equations="""
Graph message passing: h_i = σ(Σ_{j∈N(i)} W_{ij} h_j + b_i)
""",
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "graph structure preserved",
    ),
    notes="Reference implementation delegates to GraphGeometry (adapted from FabricPC graph API).",
    tags=(
        "geometry",
        "fabric_pc",
        "graph",
        "predictive_coding",
    ),
)
