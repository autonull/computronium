"""Temporal ψ Plasticity Primitive Specification."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.plasticity.temporal_psi",
    kind="primitive",
    name="Temporal ψ Plasticity",
    axis="plasticity",
    reference_entrypoint=(
        "computronium.primitives.plasticity.temporal_psi.reference.step"
    ),
    kernel_entrypoint=("computronium.primitives.plasticity.temporal_psi.kernel.step"),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="reference_only",
    summary="Trace-decayed ridge regression plasticity for task-switching under frozen θ.",
    equations="""
G_t = ρ·G_{t−1} + HᵀH
C_t = ρ·C_{t−1} + Hᵀ(onehot(y) − ½)
M_t = (G_t + λ·mean(diag G_t)·I)⁻¹C_t
""",
    invariants=(
        "deterministic under fixed seed",
        "state remains finite",
        "trace decay enables task migration",
    ),
    notes="Reference implementation delegates to TemporalPsiPlasticity.",
    tags=(
        "plasticity",
        "temporal_psi",
        "trace_decay",
        "task_switching",
    ),
)
