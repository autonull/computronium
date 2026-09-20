# Elastic Consolidation (primitive.parameter_update.elastic_consolidation)

**Kind:** primitive
**Axis:** parameter_update
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Elastic Weight Consolidation (EWC) with Fisher information

## Mathematics


Δθ = -η(∇L + λΣ F_i(θ_i - θ_i^*))
    

## Invariants

- deterministic under fixed seed
- parameters remain finite
- EWC regularization applied

## Reference Implementation

**Entrypoint:** `computronium.primitives.parameter_update.elastic_consolidation.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.parameter_update.elastic_consolidation.kernel.step`
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

- `parameter_update`
- `elastic_consolidation`
- `ewc`
- `fisher`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*