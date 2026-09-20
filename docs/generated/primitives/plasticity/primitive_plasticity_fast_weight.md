# Fast Weight Plasticity (primitive.plasticity.fast_weight)

**Kind:** primitive
**Axis:** plasticity
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Episode-local associative memory via Hebbian outer-product with random projection.

## Mathematics


    A_{t+1} = decay * A_t + lr * Proj(outer(pre_t, post_t))
    pre = settled input x, post = settled output y (F3-audit fix)
    

## Invariants

- fast weights remain bounded
- deterministic under fixed seed
- projection is non-expansive (||P v|| <= ||v||)

## Reference Implementation

**Entrypoint:** `computronium.primitives.plasticity.fast_weight.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.plasticity.fast_weight.kernel.step`
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

- `fast_weights`
- `hebbian`
- `associative_memory`
- `episode_local`

## Notes

Accelerated kernel could fuse Hebbian update with projection.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*