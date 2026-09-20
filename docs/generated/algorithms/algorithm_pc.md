# Predictive Coding (algorithm.pc)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Predictive Coding: hierarchical prediction error minimization.

## Mathematics


    ε_l = h_l - f_θ_l(h_{l+1})  # prediction error
    h_l ← h_l - η (∂ε_l/∂h_l + ∂ε_{l-1}/∂h_l)  # state update

    Δθ_l ∝ -ε_l ∂f_θ_l/∂θ_l  # weight update
    

## Invariants

- prediction errors decrease during settling
- hierarchical error propagation
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.pc.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.pc.kernel.step`
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
- `hierarchical`
- `error_minimization`
- `settling`

## Notes

Kernel may accelerate the predictive settling dynamics.


## Algorithm Family

**Family:** predictive_coding

## Primitive Dependencies

- primitive.state_dynamics.predictive_settling
- primitive.credit_assignment.local_goodness
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*