# Directed Ep (algorithm.directed_ep)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** reference_only
**Kernel Technology:** torch_compile
**Supported Backends:** reference, kernel

## Purpose

Directed Equilibrium Propagation with Feedback Alignment credit assignment

## Mathematics



    L = loss(f_θ(x), y)
    Δθ = -η B^T ∇_x L  # B is fixed random feedback matrix

    

## Invariants

- deterministic under fixed seed
- state remains finite
- matches reference implementation

## Reference Implementation

**Entrypoint:** `computronium.algorithms.directed_ep.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.directed_ep.kernel.step`
**Technology:** torch_compile

## Parity Tolerance

| Metric | Threshold |
|--------|-----------|
| Max Absolute Difference | 0.0001 |
| Max Relative Difference | 0.001 |
| Minimum Cosine Similarity | 0.999 |

## Status

Current status: **reference_only**

## Tags

- `['equilibrium', 'propagation']`

## Notes

Reference implementation composes primitives.


## Algorithm Family

**Family:** equilibrium_propagation

## Primitive Dependencies

- primitive.state_dynamics.energy_minimization
- primitive.credit_assignment.random_projections
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*