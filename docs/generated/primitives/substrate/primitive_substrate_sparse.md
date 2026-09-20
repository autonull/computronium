# Sparse Substrate (primitive.substrate.sparse)

**Kind:** primitive
**Axis:** substrate
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Digital substrate with configurable sparsity constraints for efficient computation.

## Mathematics


    W_sparse = W_dense * mask
    x' = W_sparse @ x + b
    

## Invariants

- deterministic under fixed seed
- sparsity level matches config
- finite state
- zero sparsity recovers dense digital substrate

## Reference Implementation

**Entrypoint:** `computronium.primitives.substrate.sparse.reference.make_substrate`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.substrate.sparse.kernel.make_substrate`
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
- `sparse`
- `efficiency`

## Notes

Reference implementation delegates to SparseSubstrate. Kernel falls back to reference (Triton TODO).




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*