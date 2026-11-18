"""Fabric PC Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.graph",
    kind="primitive",
    name="Graph Geometry",
    axis="geometry",
    reference_entrypoint=("computronium.primitives.geometry.graph.reference.forward"),
    kernel_entrypoint=("computronium.primitives.geometry.graph.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
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
        "graph",
        "predictive_coding",
    ),
    task_families=('graph', 'vision'),
    available=True,
    capability_card="Graph geometry; message passing; node/edge features",
)
