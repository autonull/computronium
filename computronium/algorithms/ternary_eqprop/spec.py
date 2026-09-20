"""TernaryEqprop Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.ternary_eqprop",
    kind="algorithm",
    name="Ternary Eqprop",
    family="equilibrium_propagation",
    reference_entrypoint="computronium.algorithms.ternary_eqprop.reference.step",
    kernel_entrypoint="computronium.algorithms.ternary_eqprop.kernel.step",
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
        "primitive.substrate.ternary",
    ),
    summary="Ternary-Weight Equilibrium Propagation with STE quantization",
    equations="""

    w ∈ {-α, 0, +α}
    L = loss(f_θ(x), y)
    Δθ = -η ∇_θ L (with STE for ternary projection)

    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "matches reference implementation",
    ),
    notes="Reference implementation composes primitives.",
    tags=("['equilibrium', 'propagation']",),
)
