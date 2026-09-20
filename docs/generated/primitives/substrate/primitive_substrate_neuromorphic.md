# Neuromorphic (primitive.substrate.neuromorphic)

**Kind:** primitive
**Axis:** substrate
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Neuromorphic substrate with async spikes.

## Mathematics


Spike-based computation with event-driven updates.
    

## Invariants

- deterministic under fixed seed
- spike timing is deterministic

## Reference Implementation

**Entrypoint:** `computronium.primitives.substrate.neuromorphic.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.substrate.neuromorphic.kernel.step`
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
- `neuromorphic`
- `spikes`
- `async`

## Notes

Reference wraps NeuromorphicSubstrate; kernel falls back to reference




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*