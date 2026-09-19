"""Recurrent Attractor Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.geometry.recurrent_attractor",
    kind="primitive",
    name="Recurrent Attractor",
    axis="geometry",
    reference_entrypoint=(
        "computronium.primitives.geometry.recurrent_attractor.reference.forward"
    ),
    kernel_entrypoint=(
        "computronium.primitives.geometry.recurrent_attractor.kernel.forward"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
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
