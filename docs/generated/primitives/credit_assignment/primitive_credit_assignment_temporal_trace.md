# Temporal Trace Credit (STDP) (primitive.credit_assignment.temporal_trace)

**Kind:** primitive
**Axis:** credit_assignment
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Spike-timing correlations (STDP) for credit assignment.

## Mathematics


    Rate-coded fallback: ΔW = a_plus·postᵀ·pre - a_minus·preᵀ·post
    Timing-asymmetric: ΔW = a_plus·postᵀ·pre_trace - a_minus·post_traceᵀ·pre
    pre_trace[t] = τ_pre·pre_trace[t-1] + pre_spikes[t]
    post_trace[t] = τ_post·post_trace[t-1] + post_spikes[t]
    

## Invariants

- antisymmetry: W(Δt) = -W(-Δt)
- causal > 0, anti-causal < 0
- exponential decay of traces
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.temporal_trace.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.temporal_trace.kernel.step`
**Technology:** triton

## Parity Tolerance

| Metric | Threshold |
|--------|-----------|
| Max Absolute Difference | 0.0001 |
| Max Relative Difference | 0.001 |
| Minimum Cosine Similarity | 0.999 |

## Status

Current status: **kernel_unverified**

## Tags

- `stdp`
- `spike_timing`
- `temporal_credit`

## Notes

Supports rate-coded surrogate and timing-asymmetric STDP modes. Kernel falls back to reference.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*