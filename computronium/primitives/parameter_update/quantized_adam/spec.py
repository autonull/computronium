"""Specification for the 8-bit Adam rule (TODO93 §19)."""

from computronium.acceleration.spec import ImplementationSpec

SPEC = ImplementationSpec(
    id="primitive.parameter_update.quantized_adam",
    kind="primitive",
    name="Quantized State Update",
    axis="parameter_update",
    reference_entrypoint="computronium.primitives.parameter_update.quantized_adam.reference.step",
    kernel_entrypoint="computronium.primitives.parameter_update.quantized_adam.kernel.step",
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Blockwise int8 first and second moments with per-block scales.",
    equations="""
    ΔW = −lr·m̂/(√v̂ + eps),  m̂ v̂ = dequantized int8 blocks
    """,
    invariants=("the optimizer state is 4× smaller than fp32 Adam", "the step is exact Adam on the dequantized moments"),
    notes="The reference wraps QuantizedStateUpdate; the kernel falls back to it until a fused device path lands.",
    tags=("quantized_adam", "int8", "blockwise", "parameter_update"),
    task_families=("vision", "sequence"),
    available=True,
    capability_card="8-bit Adam; blockwise quantization; 4x memory reduction; exact on dequantized",
)