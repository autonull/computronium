# Fast-Weight (6-D Joint) (algorithm.fast_weight)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

6-D Joint: episode-local associative memory via fast-weight matrices.

## Mathematics


    Fast weight matrix: A = λ A + η h h^T
    Effective weight: W_eff = W + A
    

## Invariants

- fast weights decay within episode
- associative memory property
- frozen-θ contract during intra-episode updates
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.fast_weight.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.fast_weight.kernel.step`
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

- `fast_weight`
- `6d_joint`
- `plasticity`
- `associative_memory`
- `episodic`

## Notes

6-D algorithm with plastic fast-weight variables (ψ). Kernel may accelerate outer-product updates.


## Algorithm Family

**Family:** fast_weight

## Primitive Dependencies

- primitive.state_dynamics.instantaneous_pass
- primitive.credit_assignment.reverse_mode
- primitive.parameter_update.euclidean
- primitive.plasticity.fast_weight

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*