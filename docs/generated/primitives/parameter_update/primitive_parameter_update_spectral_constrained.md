# Spectral Constrained (primitive.parameter_update.spectral_constrained)

**Kind:** primitive
**Axis:** parameter_update
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Spectral-constrained parameter update.

## Mathematics


ΔW = -η * P(W) where P projects onto spectral norm ball
    

## Invariants

- deterministic under fixed seed
- spectral norm of update is bounded

## Reference Implementation

**Entrypoint:** `computronium.primitives.parameter_update.spectral_constrained.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.parameter_update.spectral_constrained.kernel.step`
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

- `spectral`
- `constrained`
- `update`
- `regularization`

## Notes

Reference wraps SpectralConstrainedUpdate; kernel falls back to reference




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*