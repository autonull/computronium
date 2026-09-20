# Homeostatic (primitive.credit_assignment.homeostatic)

**Kind:** primitive
**Axis:** credit_assignment
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Homeostatic synaptic scaling with timing-asymmetric STDP

## Mathematics


Weight scaling: w_ij *= target_norm / ‖w_i‖
    

## Invariants

- deterministic under fixed seed
- state remains finite
- homeostatic target norm maintained

## Reference Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.homeostatic.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.homeostatic.kernel.step`
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
- `homeostatic`
- `synaptic_scaling`
- `stdp`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*