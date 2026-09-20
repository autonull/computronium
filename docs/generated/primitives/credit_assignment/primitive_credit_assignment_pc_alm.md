# PC-ALM Credit Assignment (primitive.credit_assignment.pc_alm)

**Kind:** primitive
**Axis:** credit_assignment
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Local Hebbian credit assignment using dual variables from PCALMDynamics.

## Mathematics


    ΔW_l = -λ_l @ h_{l-1}^T / batch

    where λ_l are the dual variables (Lagrange multipliers) from the
    primal-dual settling dynamics of PCALMDynamics.
    

## Invariants

- dual variables are produced by PCALMDynamics settling
- weight updates are local Hebbian (pre × post)
- deterministic under fixed seed
- credit_norm normalization options: relative, rms, spectral

## Reference Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.pc_alm.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.pc_alm.kernel.step`
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
- `local_learning`
- `hebbian`

## Notes

Accelerated kernel should preserve the pseudo-gradient within tolerance. Requires PCALMDynamics to provide dual_vars in state.metrics or state.dual_vars.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*