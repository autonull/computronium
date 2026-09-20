# Spatial Lattice 3D Geometry (primitive.geometry.spatial_lattice_3d)

**Kind:** primitive
**Axis:** geometry
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

3D spatial lattice topology with local connectivity for neural cellular automata and spatial computation.

## Mathematics


    x_{i,j,k}' = σ(Σ_{n∈N(i,j,k)} W_n · x_n + b)
    N(i,j,k) = neighbors within radius r in 3D lattice
    

## Invariants

- output shape matches (batch, output_dim)
- deterministic under fixed seed
- activations remain finite
- local connectivity preserved

## Reference Implementation

**Entrypoint:** `computronium.primitives.geometry.spatial_lattice_3d.reference.forward`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.geometry.spatial_lattice_3d.kernel.forward`
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

- `spatial`
- `lattice`
- `3d`
- `local_connectivity`
- `nca`

## Notes

Reference implementation delegates to SpatialLattice3DGeometry. Kernel falls back to reference (Triton TODO).




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*