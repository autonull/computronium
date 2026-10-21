"""MomentumEqprop Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="algorithm.momentum_eqprop",
    kind="algorithm",
    name="Momentum Eqprop",
    reference_entrypoint="computronium.algorithms.momentum_eqprop.reference.step",
    kernel_entrypoint="computronium.algorithms.momentum_eqprop.kernel.step",
    kernel_technology="torch_compile",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    uses_primitives=(
        "primitive.state_dynamics.energy_minimization",
        "primitive.credit_assignment.thermodynamic_contrast",
        "primitive.parameter_update.euclidean",
    ),
    summary="Momentum Equilibrium Propagation with heavy-ball dynamics",
    equations="""

    v_{t+1} = μ v_t - η ∇_θ E
    θ_{t+1} = θ_t + v_{t+1}

    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "matches reference implementation",
    ),
    notes="Reference implementation composes primitives.",
    tags=("['equilibrium', 'propagation']",),
)
