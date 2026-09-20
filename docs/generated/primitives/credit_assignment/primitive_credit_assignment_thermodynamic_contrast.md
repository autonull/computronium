# Thermodynamic Contrast (primitive.credit_assignment.thermodynamic_contrast)

**Kind:** primitive
**Axis:** credit_assignment
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Equilibrium Propagation contrastive credit assignment using free/nudged phase difference.

## Mathematics


    ΔW_l = (free_pre_lᵀ free_post_l − nudged_pre_lᵀ nudged_post_l)ᵀ / (β·batch)
    ε_l = (free_post_l − nudged_post_l) / β
    

## Invariants

- deterministic under fixed seed
- pseudo-gradients finite
- energy non-increasing on symmetric topology

## Reference Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.thermodynamic_contrast.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.thermodynamic_contrast.kernel.step`
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

- `equilibrium_propagation`
- `contrastive`
- `local_learning`

## Notes

Reference implementation delegates to ThermodynamicContrast ontology class. Kernel acceleration targets contrastive Hebbian computation.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*