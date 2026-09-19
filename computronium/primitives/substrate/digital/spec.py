"""Digital Substrate Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.digital",
    kind="primitive",
    name="Digital",
    axis="substrate",
    reference_entrypoint=(
        "computronium.primitives.substrate.digital.reference.make_substrate"
    ),
    kernel_entrypoint=(
        "computronium.primitives.substrate.digital.kernel.make_substrate"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Digital substrate with configurable precision, noise, and sparsity",
    equations="""
x' = quantize(x, precision) + noise
    """,
    invariants=(
        "deterministic under fixed seed",
        "bitwise reproducibility at same precision",
        "finite state",
    ),
    notes="Reference implementation delegates to ontology SubstrateSpec.make_substrate.",
    tags=(
        "substrate",
        "digital",
        "quantization",
    ),
)
