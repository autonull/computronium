"""Routing Algorithm Specification (6-D joint)."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="algorithm.routing",
    kind="algorithm",
    name="Routing (6-D Joint)",
    family="routing",
    reference_entrypoint="computronium.algorithms.routing.reference.step",
    kernel_entrypoint="computronium.algorithms.routing.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_unverified",
    uses_primitives=(
        "primitive.state_dynamics.instantaneous_pass",
        "primitive.credit_assignment.reverse_mode",
        "primitive.parameter_update.euclidean",
        "primitive.plasticity.routing",
    ),
    summary="6-D Joint: state-dependent gating with RoutingPlasticity.",
    equations="""
    Gate logits: g = W_g h + b_g
    Routing weights: α = softmax(g / τ)
    Sparse forward: h_out = Σ α_i h_i
    """,
    invariants=(
        "routing gates are dynamic and state-dependent",
        "sparsity constraint on active pathways",
        "frozen-θ contract during intra-episode routing",
        "deterministic under fixed seed",
    ),
    notes="6-D algorithm with plastic routing variables (ψ). Kernel may accelerate gating computation.",
    tags=("routing", "6d_joint", "plasticity", "gating", "sparse"),
)
