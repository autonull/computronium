"""HolomorphicEp Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.holomorphic_ep",
    kind="algorithm",
    name="Holomorphic Ep",
    family="equilibrium_propagation",
    reference_entrypoint="computronium.algorithms.holomorphic_ep.reference.step",
    kernel_entrypoint="computronium.algorithms.holomorphic_ep.kernel.step",
    kernel_technology="torch_compile",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    uses_primitives=(
        "primitive.state_dynamics.energy_minimization",
        "primitive.credit_assignment.thermodynamic_contrast",
        "primitive.parameter_update.euclidean",
        "primitive.substrate.quantum",
    ),
    summary="Holomorphic Equilibrium Propagation with complex-valued dynamics",
    equations="""

    z = x + iy
    L = |f_θ(z) - y|²
    Δθ = -η ∇_θ L (holomorphic gradient)

    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "matches reference implementation",
    ),
    notes="Reference implementation composes primitives.",
    tags=("['equilibrium', 'propagation']",),
)
