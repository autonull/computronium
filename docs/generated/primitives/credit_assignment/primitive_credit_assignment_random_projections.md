# Random Projections Credit (primitive.credit_assignment.random_projections)

**Kind:** primitive
**Axis:** credit_assignment
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Fixed random feedback matrix credit assignment (Feedback Alignment).

## Mathematics


    δ_l = B_{l+1} δ_{l+1} ⊙ f'(h_l)       # error signal via fixed random feedback
    ΔW_l = η · δ_l h_{l-1}^T               # weight update
    

## Invariants

- feedback matrices are fixed (not learned)
- feedback matrices are not transposes of forward weights
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.random_projections.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.random_projections.kernel.step`
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
- `dfa`
- `random_feedback`

## Notes

Accelerated kernel should preserve the pseudo-gradient within tolerance.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*