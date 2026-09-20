"""Fast-Weight Algorithm Specification (6-D joint)."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.fast_weight",
    kind="algorithm",
    name="Fast-Weight (6-D Joint)",
    family="fast_weight",
    reference_entrypoint="computronium.algorithms.fast_weight.reference.step",
    kernel_entrypoint="computronium.algorithms.fast_weight.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_verified",
    uses_primitives=(
        "primitive.state_dynamics.instantaneous_pass",
        "primitive.credit_assignment.reverse_mode",
        "primitive.parameter_update.euclidean",
        "primitive.plasticity.fast_weight",
    ),
    summary="6-D Joint: episode-local associative memory via fast-weight matrices.",
    equations="""
    Fast weight matrix: A = λ A + η h h^T
    Effective weight: W_eff = W + A
    """,
    invariants=(
        "fast weights decay within episode",
        "associative memory property",
        "frozen-θ contract during intra-episode updates",
        "deterministic under fixed seed",
    ),
    notes="6-D algorithm with plastic fast-weight variables (ψ). Kernel may accelerate outer-product updates.",
    tags=("fast_weight", "6d_joint", "plasticity", "associative_memory", "episodic"),
)
