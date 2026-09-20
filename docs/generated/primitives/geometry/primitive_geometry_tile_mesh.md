# Tile Mesh Geometry (primitive.geometry.tile_mesh)

**Kind:** primitive
**Axis:** geometry
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

TileNet mesh topology with modular independent tiles and local routing.

## Mathematics


    h_l = σ(W_l · h_{l-1} + b_l)  # per-tile computation
    routing: parallel within layer, sequential across layers
    

## Invariants

- output shape matches (batch, output_dim)
- deterministic under fixed seed
- tile activities remain finite

## Reference Implementation

**Entrypoint:** `computronium.primitives.geometry.tile_mesh.reference.forward`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.geometry.tile_mesh.kernel.forward`
**Technology:** triton

## Parity Tolerance

| Metric | Threshold |
|--------|-----------|
| Max Absolute Difference | 0.0001 |
| Max Relative Difference | 0.001 |
| Minimum Cosine Similarity | 0.999 |

## Status

Current status: **kernel_unverified**

## Tags

- `tilenet`
- `modular`
- `local_routing`
- `async`

## Notes

Accelerated kernel uses Triton for fused tile activity updates.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*