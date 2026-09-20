# Feedback Alignment (algorithm.fa)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Feedback Alignment with fixed random feedback matrices.

## Mathematics


    δ_l = B_{l+1} δ_{l+1} ⊙ σ'(z_l)
    ΔW_l = -η δ_l a_{l-1}^T
    where B are fixed random matrices (not W^T)
    

## Invariants

- feedback matrices are fixed and not transposes
- pseudo-gradients align with reference gradients over time
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.fa.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.fa.kernel.step`
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

- `feedback_alignment`
- `random_feedback`
- `local_learning`

## Notes

Kernel may accelerate the random projection credit computation.


## Algorithm Family

**Family:** random_feedback

## Primitive Dependencies

- primitive.state_dynamics.instantaneous_pass
- primitive.credit_assignment.random_projections
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*