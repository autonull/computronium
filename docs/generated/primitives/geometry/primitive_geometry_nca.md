# NCA Geometry (primitive.geometry.nca)

**Kind:** primitive
**Axis:** geometry
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Neural Cellular Automaton: shared cell MLP on 2D grid with local perception.

## Mathematics


Perception: p = [3×3 neighborhood of all channels]
State update: s ← s + mask · tanh(MLP(p)) · δ_scale


## Invariants

- deterministic under fixed seed
- state remains finite
- grid topology preserved

## Reference Implementation

**Entrypoint:** `computronium.primitives.geometry.nca.reference.forward`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.geometry.nca.kernel.forward`
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
- `nca`
- `cellular_automaton`
- `emergent_spatial`

## Notes

Reference implementation delegates to NcaGeometry.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*