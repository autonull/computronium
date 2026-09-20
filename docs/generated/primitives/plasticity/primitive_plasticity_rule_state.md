# Rule State (primitive.plasticity.rule_state)

**Kind:** primitive
**Axis:** plasticity
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Rule State Plasticity (Z3): frozen-θ algorithm switching via ψ

## Mathematics


operator_logits_{t+1} = decay·logits_t + controller(ψ_t, x_t)
    

## Invariants

- deterministic under fixed seed
- ψ remains finite
- θ frozen during eval

## Reference Implementation

**Entrypoint:** `computronium.primitives.plasticity.rule_state.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.plasticity.rule_state.kernel.step`
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

- `plasticity`
- `rule_state`
- `z3`
- `operator_selection`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*