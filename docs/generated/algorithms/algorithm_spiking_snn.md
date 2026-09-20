# Spiking SNN (STDP) (algorithm.spiking_snn)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Spiking Neural Network: LIF neurons with STDP credit assignment.

## Mathematics


    LIF: τ_m dv/dt = -v + I_syn,  spike if v > θ
    STDP: ΔW ∝ Σ_{t_pre, t_post} F(t_post - t_pre)
    

## Invariants

- spike timing determines weight updates
- membrane potential dynamics are deterministic
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.spiking_snn.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.spiking_snn.kernel.step`
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

- `spiking`
- `snn`
- `stdp`
- `lif`
- `temporal`

## Notes

Kernel may accelerate spike integration and STDP computation.


## Algorithm Family

**Family:** spiking

## Primitive Dependencies

- primitive.state_dynamics.spike_integration
- primitive.credit_assignment.temporal_trace
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*