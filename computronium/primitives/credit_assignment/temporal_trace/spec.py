"""Specification for Temporal Trace Credit primitive."""

from computronium.acceleration.spec import (
    ImplementationSpec,
    ParityTolerance,
)

SPEC = ImplementationSpec(
    id="primitive.credit_assignment.temporal_trace",
    kind="primitive",
    name="Temporal Trace Credit (STDP)",
    axis="credit_assignment",
    reference_entrypoint=(
        "computronium.primitives.credit_assignment.temporal_trace.reference.step"
    ),
    kernel_entrypoint=(
        "computronium.primitives.credit_assignment.temporal_trace.kernel.step"
    ),
    kernel_technology="triton",
    supported_backends=("reference", "kernel"),
    parity=ParityTolerance(
        max_abs_diff=1e-4,
        max_rel_diff=1e-3,
        min_cosine=0.999,
    ),
    status="kernel_verified",
    summary="Spike-timing correlations (STDP) for credit assignment.",
    equations="""
    Rate-coded fallback: ΔW = a_plus·postᵀ·pre - a_minus·preᵀ·post
    Timing-asymmetric: ΔW = a_plus·postᵀ·pre_trace - a_minus·post_traceᵀ·pre
    pre_trace[t] = τ_pre·pre_trace[t-1] + pre_spikes[t]
    post_trace[t] = τ_post·post_trace[t-1] + post_spikes[t]
    """,
    invariants=(
        "antisymmetry: W(Δt) = -W(-Δt)",
        "causal > 0, anti-causal < 0",
        "exponential decay of traces",
        "deterministic under fixed seed",
    ),
    notes="Supports rate-coded surrogate and timing-asymmetric STDP modes. Kernel falls back to reference.",
    tags=("stdp", "spike_timing", "temporal_credit"),
)
