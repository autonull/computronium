# Fabric PC Geometry (primitive.geometry.fabric_pc)

**Kind:** primitive
**Axis:** geometry
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Arbitrary node-edge graph topology for predictive coding (adapted from FabricPC).

## Mathematics


Graph message passing: h_i = σ(Σ_{j∈N(i)} W_{ij} h_j + b_i)


## Invariants

- deterministic under fixed seed
- state remains finite
- graph structure preserved

## Reference Implementation

**Entrypoint:** `computronium.primitives.geometry.fabric_pc.reference.forward`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.geometry.fabric_pc.kernel.forward`
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
- `fabric_pc`
- `graph`
- `predictive_coding`

## Notes

Reference implementation delegates to GraphGeometry (adapted from FabricPC graph API).




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*