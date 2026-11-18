"""Analog Substrate Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.substrate.analog",
    kind="primitive",
    name="Analog Substrate",
    axis="substrate",
    reference_entrypoint=(
        "computronium.primitives.substrate.analog.reference.make_substrate"
    ),
    kernel_entrypoint=(
        "computronium.primitives.substrate.analog.kernel.make_substrate"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Analog device model with additive state noise and bounded weights.",
    equations="""
w ← clamp(w, −1, 1);  s ← s + N(0, noise_level)
    """,
    invariants=(
        "deterministic under fixed seed",
        "weights clamped to the declared bounds",
        "noise injected only when noise_level > 0",
    ),
    notes="The analog device model, distinct from `noisy` (a digital substrate with noise configured).",
    tags=(
        "substrate",
        "analog",
        "noise",
    ),
    task_families=("neuromorphic",),
    available=True,
    capability_card="Analog substrate; continuous values; noise and drift",
)