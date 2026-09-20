"""Diffusion Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.diffusion",
    kind="primitive",
    name="Diffusion",
    axis="state_dynamics",
    reference_entrypoint=(
        "computronium.primitives.state_dynamics.diffusion.reference.step"
    ),
    kernel_entrypoint=("computronium.primitives.state_dynamics.diffusion.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Langevin dynamics over the geometry's Hopfield energy with stochastic sampling",
    equations="""
dh = -∇E dt + sqrt(2·D)·dW
    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "stochastic sampler over fixed points",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "state_dynamics",
        "diffusion",
        "langevin",
        "stochastic",
    ),
)
