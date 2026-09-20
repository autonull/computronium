# Forward-Forward (algorithm.ff)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Forward-Forward: layer-local objectives, no backward pass.

## Mathematics


    Positive pass:  h_l = σ(W_l h_{l-1} + y_l)
    Negative pass:  h_l = σ(W_l h_{l-1} + y'_l)

    L_l = softplus(-g_l^pos + θ) + softplus(g_l^neg - θ)
    where g_l = ||h_l||^2 is the goodness
    

## Invariants

- no backward pass through the network
- layer-local losses and optimizers
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.ff.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.ff.kernel.step`
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

- `forward_forward`
- `local_learning`
- `no_backprop`
- `goodness`

## Notes

Custom train_step with per-layer optimizers. Kernel may accelerate layer-wise operations.


## Algorithm Family

**Family:** local_goodness

## Primitive Dependencies

- primitive.state_dynamics.instantaneous_pass
- primitive.credit_assignment.local_goodness
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*