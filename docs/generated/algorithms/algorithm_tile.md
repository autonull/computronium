# TileNet (algorithm.tile)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

TileNet: modular tiled architecture with local connectivity.

## Mathematics


    Tiles: groups of neurons with local connectivity
    Routing: sparse inter-tile connections
    

## Invariants

- structured sparsity within tiles
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.tile.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.tile.kernel.step`
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

- `tile_net`
- `modular`
- `structured_sparsity`
- `geometry`

## Notes

Kernel may accelerate tile routing operations.


## Algorithm Family

**Family:** modular

## Primitive Dependencies

- primitive.geometry.tile_mesh
- primitive.state_dynamics.instantaneous_pass
- primitive.credit_assignment.reverse_mode
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*