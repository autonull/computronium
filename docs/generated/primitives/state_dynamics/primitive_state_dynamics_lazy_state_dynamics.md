# Lazy State Dynamics (primitive.state_dynamics.lazy_state_dynamics)

**Kind:** primitive
**Axis:** state_dynamics
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Sequential (Gauss-Seidel) EqProp settle with lazy per-layer activation

## Mathematics


Gauss-Seidel sweep: a_l^{t+1} = f(a_l^t, a_{l-1}^{t+1}, a_{l+1}^t)
    

## Invariants

- deterministic under fixed seed
- state remains finite
- Gauss-Seidel converges to same fixed point as Jacobi

## Reference Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.lazy_state_dynamics.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.lazy_state_dynamics.kernel.step`
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

- `state_dynamics`
- `lazy`
- `gauss_seidel`
- `eqprop`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*