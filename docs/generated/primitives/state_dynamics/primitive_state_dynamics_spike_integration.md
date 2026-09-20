# Spike Integration (primitive.state_dynamics.spike_integration)

**Kind:** primitive
**Axis:** state_dynamics
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Spike integration dynamics (LIF/Izhikevich).

## Mathematics


tau * dv/dt = -v + I; v = v + dt/tau * (-v + I)
    

## Invariants

- state remains finite
- deterministic under fixed seed
- spike times are deterministic

## Reference Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.spike_integration.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.spike_integration.kernel.step`
**Technology:** triton

## Parity Tolerance

| Metric | Threshold |
|--------|-----------|
| Max Absolute Difference | 0.0001 |
| Max Relative Difference | 0.001 |
| Minimum Cosine Similarity | 0.999 |

## Status

Current status: **reference_only**

## Tags

- `spiking`
- `lif`
- `izhikevich`
- `settling`

## Notes

Reference wraps SpikeIntegrationDynamics; kernel falls back to reference (Triton TODO in snn_kernels.py)




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*