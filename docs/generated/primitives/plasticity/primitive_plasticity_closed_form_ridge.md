# Closed-form Ridge Plasticity (primitive.plasticity.closed_form_ridge)

**Kind:** primitive
**Axis:** plasticity
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Closed-form ridge regression plasticity for supervised fast-weight computation.

## Mathematics


W = Y X^T (X X^T + λI)^{-1}


## Invariants

- deterministic under fixed seed
- state remains finite
- closed-form solution is exact

## Reference Implementation

**Entrypoint:** `computronium.primitives.plasticity.closed_form_ridge.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.plasticity.closed_form_ridge.kernel.step`
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
- `closed_form_ridge`
- `ridge_regression`
- `supervised`

## Notes

Reference implementation delegates to ClosedFormRidgePlasticity.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*