"""Instantaneous Pass Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.instantaneous",
    kind="primitive",
    name="Instantaneous Dynamics",
    axis="state_dynamics",
    reference_entrypoint=(
        "computronium.primitives.state_dynamics.instantaneous.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.state_dynamics.instantaneous.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Single-pass feedforward dynamics for Backprop and Forward-Forward algorithms",
    equations="""
a_{l+1} = σ(W_l a_l + b_l)
    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "no settling iterations required",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "state_dynamics",
        "instantaneous",
        "backprop",
        "forward_forward",
    ),
    task_families=("continual", "vision", "sequence", "tabular", "graph", "rl"),
    available=True,
    capability_card="Single-pass feedforward; compatible with gradient and local credits; baseline for settling dynamics",
)
