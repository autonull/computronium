"""Homeostatic Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.homeostatic",
    kind="primitive",
    name="Homeostatic",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.homeostatic.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.homeostatic.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Homeostatic synaptic scaling with timing-asymmetric STDP",
    equations="""
Weight scaling: w_ij *= target_norm / ‖w_i‖
    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "homeostatic target norm maintained",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "credit_assignment",
        "homeostatic",
        "synaptic_scaling",
        "stdp",
    ),
)
