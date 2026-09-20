# Euclidean Update (primitive.parameter_update.euclidean)

**Kind:** primitive
**Axis:** parameter_update
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Standard Euclidean parameter update (SGD with optional momentum).

## Mathematics


    v ← μv + g
    Δθ = −lr · v
    

## Invariants

- deterministic under fixed seed
- parameters updated in-place or returned as new dict
- momentum buffers preserved across steps
- global-norm gradient clipping applied if configured

## Reference Implementation

**Entrypoint:** `computronium.primitives.parameter_update.euclidean.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.parameter_update.euclidean.kernel.step`
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

- `sgd`
- `momentum`
- `euclidean`
- `parameter_update`

## Notes

Reference implementation delegates to EuclideanUpdate ontology class. Kernel acceleration targets momentum update and clipping.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*