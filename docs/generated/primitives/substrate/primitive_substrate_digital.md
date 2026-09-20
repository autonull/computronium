# Digital (primitive.substrate.digital)

**Kind:** primitive
**Axis:** substrate
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Digital substrate with configurable precision, noise, and sparsity

## Mathematics


x' = quantize(x, precision) + noise
    

## Invariants

- deterministic under fixed seed
- bitwise reproducibility at same precision
- finite state

## Reference Implementation

**Entrypoint:** `computronium.primitives.substrate.digital.reference.make_substrate`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.substrate.digital.kernel.make_substrate`
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
- `quantization`

## Notes

Reference implementation delegates to ontology SubstrateSpec.make_substrate.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*