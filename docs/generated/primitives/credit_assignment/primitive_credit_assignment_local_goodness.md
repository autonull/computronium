# Local Goodness Credit (primitive.credit_assignment.local_goodness)

**Kind:** primitive
**Axis:** credit_assignment
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Layer-local contrastive credit assignment (Forward-Forward and LEMMA variants).

## Mathematics


    FF mode: ΔW_l ∝ -∇_W (G_free - G_nudged)_l
    LEMMA mode: ΔW_l ∝ -(e₁ @ B_lᵀ)ᵀ a_pre
    

## Invariants

- pseudo-gradient is deterministic under fixed seed
- hidden layer updates are local (no inverse pass)
- LEMMA fixed-B uses orthogonal random projections

## Reference Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.local_goodness.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.local_goodness.kernel.step`
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

- `forward_forward`
- `lemma`
- `local_credit`
- `contrastive`

## Notes

Two modes: 'ff' (Forward-Forward) uses autograd of goodness contrast; 'lemma' uses closed-form fixed/learned feedback. Kernel acceleration available via ff_kernels Triton backends.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*