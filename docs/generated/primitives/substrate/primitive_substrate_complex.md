# Complex Substrate (primitive.substrate.complex)

**Kind:** primitive
**Axis:** substrate
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Digital substrate with complex-valued state space for holomorphic/phase-based computation.

## Mathematics


    x = x_real + i * x_imag
    x' = W @ x + b  (complex matmul)
    

## Invariants

- deterministic under fixed seed
- complex dtype preserved
- finite state
- conjugate symmetry for real outputs

## Reference Implementation

**Entrypoint:** `computronium.primitives.substrate.complex.reference.make_substrate`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.substrate.complex.kernel.make_substrate`
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
- `complex`
- `holomorphic`
- `phase`

## Notes

Reference implementation delegates to ComplexSubstrate. Kernel falls back to reference (Triton TODO).




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*