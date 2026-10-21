"""NCA Geometry Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.nca",
    kind="primitive",
    name="NCA Geometry",
    axis="geometry",
    reference_entrypoint=("computronium.primitives.geometry.nca.reference.forward"),
    kernel_entrypoint=("computronium.primitives.geometry.nca.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Neural Cellular Automaton: shared cell MLP on 2D grid with local perception.",
    equations="""
Perception: p = [3×3 neighborhood of all channels]
State update: s ← s + mask · tanh(MLP(p)) · δ_scale
""",
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "grid topology preserved",
    ),
    notes="Reference implementation delegates to NcaGeometry.",
    tags=(
        "geometry",
        "nca",
        "cellular_automaton",
        "emergent_spatial",
    ),
)
