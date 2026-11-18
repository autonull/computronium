"""Conflict-Adaptive Plasticity Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
)

SPEC = ImplementationSpec(
    id="primitive.plasticity.conflict_adaptive",
    kind="primitive",
    name="Conflict-Adaptive Plasticity",
    axis="plasticity",
    reference_entrypoint=(
        "computronium.primitives.plasticity.conflict_adaptive.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.plasticity.conflict_adaptive.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    status="reference_only",
    summary="Trace-decayed ridge readout whose decay is driven by detected readout/target conflict.",
    equations="""
a_t = mean(argmax(h_t M_{t−1} + b_{t−1}) == y_t)
ρ_t = forget_decay if a_t < threshold else 1.0
    """,
    invariants=(
        "deterministic under fixed seed",
        "trace statistics accumulate over steps",
        "agreement and rho_used recorded in ψ",
    ),
    notes="Conflict is detected from the readout, not from task boundaries.",
    tags=(
        "plasticity",
        "psi",
        "ridge",
        "continual",
    ),
    task_families=('continual',),
    available=True,
    capability_card="Conflict-adaptive plasticity; detects interference; modulates learning",
)
