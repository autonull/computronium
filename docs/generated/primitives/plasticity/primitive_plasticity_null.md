# Null Plasticity (primitive.plasticity.null)

**Kind:** primitive
**Axis:** plasticity
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Null plasticity (zero-extension): plastic state unchanged, makes 5-D systems valid 6-D coordinates.

## Mathematics


    ψ_{t+1} = ψ_t
    

## Invariants

- deterministic under fixed seed
- plastic state returned unchanged
- no plastic state allocated initially

## Reference Implementation

**Entrypoint:** `computronium.primitives.plasticity.null.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.plasticity.null.kernel.step`
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

- `null`
- `zero_extension`
- `identity`
- `plasticity`

## Notes

Reference implementation delegates to NullPlasticity ontology class. This is the identity primitive for plasticity axis.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*