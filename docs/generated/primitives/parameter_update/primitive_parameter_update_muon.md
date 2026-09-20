# Muon (Riemannian Orthogonal Update) (primitive.parameter_update.muon)

**Kind:** primitive
**Axis:** parameter_update
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Orthogonal parameter updates via Riemannian optimization on Stiefel manifold.

## Mathematics


    ΔW = -lr · polar(μ·buf + g)  for matrices
    ΔW = -lr · g                 for vectors (biases)
    polar(M) = U @ Vh where M = U @ S @ Vh (SVD)
    buf ← μ·buf + g  (momentum buffer)
    

## Invariants

- orthogonal updates preserve Frobenius norm of weight matrices
- momentum accumulates signal before orthogonalization
- vectors (biases) ride plain SGD
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.primitives.parameter_update.muon.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.parameter_update.muon.kernel.step`
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

- `muon`
- `orthogonal_update`
- `riemannian_optimization`

## Notes

Uses exact SVD polar factor (ortho_steps=0) for full-spectrum whitening. Newton-Schulz iteration available as opt-in.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*