# Recurrent Attractor (primitive.geometry.recurrent_attractor)

**Kind:** primitive
**Axis:** geometry
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Recurrent attractor geometry for energy-based models like Equilibrium Propagation

## Mathematics


x_{t+1} = f(W x_t + U u_t + b)
    

## Invariants

- deterministic under fixed seed
- state remains finite
- symmetric topology enables Lyapunov analysis

## Reference Implementation

**Entrypoint:** `computronium.primitives.geometry.recurrent_attractor.reference.forward`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.geometry.recurrent_attractor.kernel.forward`
**Technology:** triton

## Parity Tolerance

| Metric | Threshold |
|--------|-----------|
| Max Absolute Difference | 0.0001 |
| Max Relative Difference | 0.001 |
| Minimum Cosine Similarity | 0.999 |

## Status

Current status: **reference_only**

## Tags

- `geometry`
- `recurrent`
- `energy_based`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*