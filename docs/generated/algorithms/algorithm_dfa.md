# Direct Feedback Alignment (algorithm.dfa)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Direct Feedback Alignment with output-to-all-layers fixed random feedback.

## Mathematics


    δ_L = ∂L/∂a_L                             # output error via autograd
    δ_l = δ_L @ B_l                            # direct feedback from output
    ΔW_l = δ_l @ a_{l-1}^T / batch             # layer-local weight update
    where B_l are fixed random matrices (not W^T)
    

## Invariants

- feedback matrices are fixed and not transposes
- all hidden layers receive feedback directly from output layer
- pseudo-gradients align with reference gradients over time
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.dfa.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.dfa.kernel.step`
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

- `direct_feedback_alignment`
- `random_feedback`
- `local_learning`

## Notes

DFA uses direct feedback from output to each layer. Kernel may accelerate the random projection credit computation.


## Algorithm Family

**Family:** random_feedback

## Primitive Dependencies

- primitive.state_dynamics.instantaneous_pass
- primitive.credit_assignment.random_projections
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*