"""Specification for the Adafactor rule (TODO93 §19)."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.parameter_update.adafactor",
    kind="primitive",
    name="Factored Second Moment Update",
    axis="parameter_update",
    reference_entrypoint="computronium.primitives.parameter_update.adafactor.reference.step",
    kernel_entrypoint="computronium.primitives.parameter_update.adafactor.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="A factored row × column second moment per matrix.",
    equations="""
    V ≈ R Cᵀ / mean(R);  ΔW = −lr·m/(√V + eps)
    """,
    invariants=("the optimizer state is O(rows + columns) per matrix", "the factored estimate tracks the full second moment"),
    notes="The reference wraps FactoredSecondMomentUpdate; the kernel falls back to it until a fused device path lands.",
    tags=("adafactor", "factored", "second_moment", "parameter_update"),
)
