# Routing (6-D Joint) (algorithm.routing)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

6-D Joint: state-dependent gating with RoutingPlasticity.

## Mathematics


    Gate logits: g = W_g h + b_g
    Routing weights: α = softmax(g / τ)
    Sparse forward: h_out = Σ α_i h_i
    

## Invariants

- routing gates are dynamic and state-dependent
- sparsity constraint on active pathways
- frozen-θ contract during intra-episode routing
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.routing.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.routing.kernel.step`
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

- `routing`
- `6d_joint`
- `plasticity`
- `gating`
- `sparse`

## Notes

6-D algorithm with plastic routing variables (ψ). Kernel may accelerate gating computation.


## Algorithm Family

**Family:** routing

## Primitive Dependencies

- primitive.state_dynamics.instantaneous_pass
- primitive.credit_assignment.reverse_mode
- primitive.parameter_update.euclidean
- primitive.plasticity.routing

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*