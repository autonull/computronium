"""Instantaneous Pass Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.state_dynamics.instantaneous_pass",
    kind="primitive",
    name="Instantaneous Pass",
    axis="state_dynamics",
    reference_entrypoint=(
        "computronium.primitives.state_dynamics.instantaneous_pass.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.state_dynamics.instantaneous_pass.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
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
)
