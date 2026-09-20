# Photonic (primitive.substrate.photonic)

**Kind:** primitive
**Axis:** substrate
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Optical/photonic substrate with phase/amplitude encoding

## Mathematics


Complex-valued operations via phase interference
    

## Invariants

- deterministic under fixed seed
- complex-valued operations

## Reference Implementation

**Entrypoint:** `computronium.primitives.substrate.photonic.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.substrate.photonic.kernel.step`
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

- `substrate`
- `photonic`
- `optical`
- `phase`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*