"""Equilibrium Propagation (EqProp) Algorithm Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="algorithm.eqprop",
    kind="algorithm",
    name="Equilibrium Propagation",
    reference_entrypoint="computronium.algorithms.eqprop.reference.step",
    kernel_entrypoint="computronium.algorithms.eqprop.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="kernel_verified",
    uses_primitives=(
        "primitive.state_dynamics.energy_minimization",
        "primitive.credit_assignment.thermodynamic_contrast",
        "primitive.parameter_update.euclidean",
    ),
    summary="Equilibrium Propagation: energy-based local contrastive learning.",
    equations="""
    Free phase:  ∂E/∂x = 0  →  x*
    Nudged phase:  ∂(E + β·C)/∂x = 0  →  x*_β

    Δθ ∝ -β (∂C/∂θ|_{x*_β} - ∂C/∂θ|_{x*})
    """,
    invariants=(
        "free energy decreases during settling",
        "nudged phase converges to nearby equilibrium",
        "local contrastive update approximates true gradient",
        "deterministic under fixed seed",
    ),
    notes=(
        "Kernel may accelerate the energy minimization settling dynamics. "
        "Reference-only on a composed relu cell: the tanh kernel cannot reproduce "
        "a relu geometry, and the attach guard detaches to the reference "
        "(TODO107 D5)."
    ),
    tags=("equilibrium_propagation", "energy_based", "local_learning", "contrastive"),
)
