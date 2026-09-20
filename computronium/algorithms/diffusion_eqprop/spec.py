"""DiffusionEqprop Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.diffusion_eqprop",
    kind="algorithm",
    name="Diffusion Eqprop",
    family="equilibrium_propagation",
    reference_entrypoint="computronium.algorithms.diffusion_eqprop.reference.step",
    kernel_entrypoint="computronium.algorithms.diffusion_eqprop.kernel.step",
    kernel_technology="torch_compile",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    uses_primitives=(
        "primitive.state_dynamics.diffusion",
        "primitive.credit_assignment.thermodynamic_contrast",
        "primitive.parameter_update.euclidean",
    ),
    summary="Diffusion Equilibrium Propagation with continuous-time dynamics",
    equations="""

    dx/dt = -∇_x E(x) + √(2β) dW
    Δθ = -η ∇_θ E

    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "matches reference implementation",
    ),
    notes="Reference implementation composes primitives.",
    tags=("['equilibrium', 'propagation']",),
)
