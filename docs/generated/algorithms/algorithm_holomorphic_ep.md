# Holomorphic Ep (algorithm.holomorphic_ep)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** reference_only
**Kernel Technology:** torch_compile
**Supported Backends:** reference, kernel

## Purpose

Holomorphic Equilibrium Propagation with complex-valued dynamics

## Mathematics



    z = x + iy
    L = |f_θ(z) - y|²
    Δθ = -η ∇_θ L (holomorphic gradient)

    

## Invariants

- deterministic under fixed seed
- state remains finite
- matches reference implementation

## Reference Implementation

**Entrypoint:** `computronium.algorithms.holomorphic_ep.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.holomorphic_ep.kernel.step`
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
- primitive.credit_assignment.thermodynamic_contrast
- primitive.parameter_update.euclidean
- primitive.substrate.quantum

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*