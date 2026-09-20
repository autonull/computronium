# Temporal ψ Plasticity (primitive.plasticity.temporal_psi)

**Kind:** primitive
**Axis:** plasticity
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Trace-decayed ridge regression plasticity for task-switching under frozen θ.

## Mathematics


G_t = ρ·G_{t−1} + HᵀH
C_t = ρ·C_{t−1} + Hᵀ(onehot(y) − ½)
M_t = (G_t + λ·mean(diag G_t)·I)⁻¹C_t


## Invariants

- deterministic under fixed seed
- state remains finite
- trace decay enables task migration

## Reference Implementation

**Entrypoint:** `computronium.primitives.plasticity.temporal_psi.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.plasticity.temporal_psi.kernel.step`
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

- `plasticity`
- `temporal_psi`
- `trace_decay`
- `task_switching`

## Notes

Reference implementation delegates to TemporalPsiPlasticity.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*