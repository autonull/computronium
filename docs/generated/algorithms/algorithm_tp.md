# Target Propagation (algorithm.tp)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Target Propagation with transpose feedback and predictive settling.

## Mathematics


    t_L = one_hot(y)                           # output target
    t_l = t_{l+1} @ W_{l+1}^T                   # propagated targets via transpose
    ΔW_l = (a_l - t_l)^T @ a_{l-1} / batch     # layer-local pseudo-gradient
    

## Invariants

- targets propagated via transpose of forward weights
- output target is one-hot label
- pseudo-gradients use local layer activations and targets
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.tp.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.tp.kernel.step`
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

- `target_propagation`
- `transpose_feedback`
- `predictive_coding`

## Notes

Kernel may accelerate the target propagation and pseudo-gradient computation.


## Algorithm Family

**Family:** target_propagation

## Primitive Dependencies

- primitive.state_dynamics.predictive_settling
- primitive.credit_assignment.target_inversion
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*