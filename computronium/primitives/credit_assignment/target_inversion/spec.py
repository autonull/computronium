"""Target Inversion Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.target_inversion",
    kind="primitive",
    name="Target Inversion",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.target_inversion.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.target_inversion.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Target Propagation with transpose feedback for local target propagation",
    equations="""
t_l = t_{l+1} @ W_{l+1}^T, ΔW_l = (acts_l - t_l)^T a_{l-1} / batch
    """,
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "target propagation preserves layer structure",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "credit_assignment",
        "target_inversion",
        "target_prop",
        "transpose_feedback",
    ),
)
