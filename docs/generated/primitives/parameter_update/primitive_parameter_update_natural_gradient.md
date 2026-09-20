# Natural Gradient (primitive.parameter_update.natural_gradient)

**Kind:** primitive
**Axis:** parameter_update
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Natural gradient parameter update with Fisher geometry preconditioning.

## Mathematics


Δθ = −lr · (F + λI)⁻¹ · g


## Invariants

- deterministic under fixed seed
- parameters updated in-place or returned as new dict
- momentum buffers preserved across steps
- Fisher diagonal EMA updated per step

## Reference Implementation

**Entrypoint:** `computronium.primitives.parameter_update.natural_gradient.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.parameter_update.natural_gradient.kernel.step`
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

- `natural_gradient`
- `fisher`
- `parameter_update`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*