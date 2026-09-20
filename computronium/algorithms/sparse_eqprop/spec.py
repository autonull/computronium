"""SparseEqprop Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.sparse_eqprop",
    kind="algorithm",
    name="Sparse Eqprop",
    family="equilibrium_propagation",
    reference_entrypoint="computronium.algorithms.sparse_eqprop.reference.step",
    kernel_entrypoint="computronium.algorithms.sparse_eqprop.kernel.step",
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
        "primitive.substrate.sparse",
    ),
    summary="Sparse Equilibrium Propagation with dynamic sparsity",
    equations="""

    M_t = Bernoulli(1-s)
    W_t = M_t ⊙ W
    Δθ = -η M_t ⊙ ∇_θ E

    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "matches reference implementation",
    ),
    notes="Reference implementation composes primitives.",
    tags=("['equilibrium', 'propagation']",),
)
