# Ternary Substrate (primitive.substrate.ternary)

**Kind:** primitive
**Axis:** substrate
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Digital substrate with ternary weight quantization {-α, 0, +α} for efficient inference.

## Mathematics


    w_ternary = sign(w) * max(|w|)
    x' = w_ternary @ x + b
    

## Invariants

- deterministic under fixed seed
- weights constrained to ternary values
- finite state
- STE gradient for training

## Reference Implementation

**Entrypoint:** `computronium.primitives.substrate.ternary.reference.make_substrate`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.substrate.ternary.kernel.make_substrate`
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
- `ternary`
- `quantization`
- `inference`

## Notes

Reference implementation delegates to TernarySubstrate. Kernel falls back to reference (Triton TODO).




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*