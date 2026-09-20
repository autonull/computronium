# Equilibrium Propagation (algorithm.eqprop)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Equilibrium Propagation: energy-based local contrastive learning.

## Mathematics


    Free phase:  ∂E/∂x = 0  →  x*
    Nudged phase:  ∂(E + β·C)/∂x = 0  →  x*_β

    Δθ ∝ -β (∂C/∂θ|_{x*_β} - ∂C/∂θ|_{x*})
    

## Invariants

- free energy decreases during settling
- nudged phase converges to nearby equilibrium
- local contrastive update approximates true gradient
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.eqprop.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.eqprop.kernel.step`
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

- `equilibrium_propagation`
- `energy_based`
- `local_learning`
- `contrastive`

## Notes

Kernel may accelerate the energy minimization settling dynamics.


## Algorithm Family

**Family:** energy_based

## Primitive Dependencies

- primitive.state_dynamics.energy_minimization
- primitive.credit_assignment.thermodynamic_contrast
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*