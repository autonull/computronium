"""FiniteNudgeEp Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.finite_nudge_ep",
    kind="algorithm",
    name="Finite Nudge Ep",
    family="equilibrium_propagation",
    reference_entrypoint="computronium.algorithms.finite_nudge_ep.reference.step",
    kernel_entrypoint="computronium.algorithms.finite_nudge_ep.kernel.step",
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
    ),
    summary="Finite-Nudge Equilibrium Propagation with large β",
    equations="""

    L = loss(f_θ(x), y)
    ∂L/∂θ = lim_{β→∞} (x_β - x_0) / β

    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "matches reference implementation",
    ),
    notes="Reference implementation composes primitives.",
    tags=("['equilibrium', 'propagation']",),
)
