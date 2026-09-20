# Target Inversion (primitive.credit_assignment.target_inversion)

**Kind:** primitive
**Axis:** credit_assignment
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Target Propagation with transpose feedback for local target propagation

## Mathematics


t_l = t_{l+1} @ W_{l+1}^T, ΔW_l = (acts_l - t_l)^T a_{l-1} / batch
    

## Invariants

- deterministic under fixed seed
- state remains finite
- target propagation preserves layer structure

## Reference Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.target_inversion.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.target_inversion.kernel.step`
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

- `credit_assignment`
- `target_inversion`
- `target_prop`
- `transpose_feedback`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*