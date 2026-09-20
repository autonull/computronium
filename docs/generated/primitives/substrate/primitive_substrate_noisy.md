# Noisy Substrate (primitive.substrate.noisy)

**Kind:** primitive
**Axis:** substrate
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Digital substrate with configurable additive Gaussian noise for robustness testing.

## Mathematics


    x' = x + N(0, σ²)
    

## Invariants

- deterministic under fixed seed
- noise level matches config
- finite state
- zero noise recovers digital substrate

## Reference Implementation

**Entrypoint:** `computronium.primitives.substrate.noisy.reference.make_substrate`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.substrate.noisy.kernel.make_substrate`
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
- `digital`
- `noise`
- `robustness`

## Notes

Reference implementation delegates to NoisySubstrate. Kernel falls back to reference (Triton TODO).




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*