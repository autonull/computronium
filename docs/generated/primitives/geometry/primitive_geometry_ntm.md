# NTM Geometry (primitive.geometry.ntm)

**Kind:** primitive
**Axis:** geometry
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Neural Turing Machine with LSTM controller and content-addressed memory.

## Mathematics


Controller: h_t = LSTM([x_t; r_{t-1}])
Read: r_t = Σ_s softmax(β cos(m_s, k_r)) m_s
Write: m_s ← m_s ⊙ (1 - w_s ⊙ e) + w_s ⊙ a


## Invariants

- deterministic under fixed seed
- state remains finite
- memory slots maintain identity

## Reference Implementation

**Entrypoint:** `computronium.primitives.geometry.ntm.reference.forward`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.geometry.ntm.kernel.forward`
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

- `geometry`
- `ntm`
- `external_memory`
- `content_addressing`

## Notes

Reference implementation delegates to NtmGeometry.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*