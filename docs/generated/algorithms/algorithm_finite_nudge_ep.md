# Finite Nudge Ep (algorithm.finite_nudge_ep)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** reference_only
**Kernel Technology:** torch_compile
**Supported Backends:** reference, kernel

## Purpose

Finite-Nudge Equilibrium Propagation with large β

## Mathematics



    L = loss(f_θ(x), y)
    ∂L/∂θ = lim_{β→∞} (x_β - x_0) / β

    

## Invariants

- deterministic under fixed seed
- state remains finite
- matches reference implementation

## Reference Implementation

**Entrypoint:** `computronium.algorithms.finite_nudge_ep.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.finite_nudge_ep.kernel.step`
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

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*