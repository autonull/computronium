# Quantum (primitive.substrate.quantum)

**Kind:** primitive
**Axis:** substrate
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Quantum substrate with unitary gate operations

## Mathematics


Unitary evolution: U = exp(-iHt)
    

## Invariants

- deterministic under fixed seed
- unitary operations preserve norm

## Reference Implementation

**Entrypoint:** `computronium.primitives.substrate.quantum.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.substrate.quantum.kernel.step`
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
- `quantum`
- `unitary`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*