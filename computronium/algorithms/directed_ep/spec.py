"""DirectedEp Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.directed_ep",
    kind="algorithm",
    name="Directed Ep",
    family="equilibrium_propagation",
    reference_entrypoint="computronium.algorithms.directed_ep.reference.step",
    kernel_entrypoint="computronium.algorithms.directed_ep.kernel.step",
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
        "primitive.credit_assignment.random_projections",
        "primitive.parameter_update.euclidean",
    ),
    summary="Directed Equilibrium Propagation with Feedback Alignment credit assignment",
    equations="""

    L = loss(f_θ(x), y)
    Δθ = -η B^T ∇_x L  # B is fixed random feedback matrix

    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "matches reference implementation",
    ),
    notes="Reference implementation composes primitives.",
    tags=("['equilibrium', 'propagation']",),
)
