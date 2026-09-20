# PC-ALM Settling (primitive.state_dynamics.pc_alm_settling)

**Kind:** primitive
**Axis:** state_dynamics
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Primal-dual settling dynamics for PC-ALM.

## Mathematics


    c_l = h_l - f_θ_l(h_{l-1})                  # constraint violation
    λ_l ← λ_l + step_size · (c_l + α·λ_l)       # dual update (PI controller)
    h_l ← h_l - step_size · [c_l + λ_l + ρ·c_l
          - J_{l+1}^T·(c_{l+1} + λ_{l+1} + ρ·c_{l+1})]  # primal update
    

## Invariants

- settling residual decreases or remains bounded
- state remains finite
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.pc_alm_settling.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.pc_alm_settling.kernel.step`
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

- `predictive_coding`
- `augmented_lagrangian`
- `settling`

## Notes

Accelerated kernel should preserve the settled state within tolerance.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*