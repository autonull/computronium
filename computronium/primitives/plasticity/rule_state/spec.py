"""Rule State Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.plasticity.rule_state",
    kind="primitive",
    name="Rule State",
    axis="plasticity",
    reference_entrypoint=(
        "computronium.primitives.plasticity.rule_state.reference.step"
    ),
    kernel_entrypoint=("computronium.primitives.plasticity.rule_state.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Rule State Plasticity (Z3): frozen-θ algorithm switching via ψ",
    equations="""
operator_logits_{t+1} = decay·logits_t + controller(ψ_t, x_t)
    """,
    invariants=(
        "deterministic under fixed seed",
        "ψ remains finite",
        "θ frozen during eval",
    ),
    notes="Reference implementation delegates to ontology class.",
    tags=(
        "plasticity",
        "rule_state",
        "z3",
        "operator_selection",
    ),
)
