"""Recurrent Attractor Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.recurrent",
    kind="primitive",
    name="Recurrent Geometry",
    axis="geometry",
    reference_entrypoint=(
        "computronium.primitives.geometry.recurrent.reference.forward"
    ),
    kernel_entrypoint=("computronium.primitives.geometry.recurrent.kernel.forward"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Recurrent attractor geometry for energy-based models like Equilibrium Propagation",
    equations="""
x_{t+1} = f(W x_t + U u_t + b)
    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "symmetric topology enables Lyapunov analysis",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "geometry",
        "recurrent",
        "energy_based",
    ),
)
