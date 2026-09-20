# Diffusion (primitive.state_dynamics.diffusion)

**Kind:** primitive
**Axis:** state_dynamics
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Langevin dynamics over the geometry's Hopfield energy with stochastic sampling

## Mathematics


dh = -∇E dt + sqrt(2·D)·dW
    

## Invariants

- deterministic under fixed seed
- state remains finite
- stochastic sampler over fixed points

## Reference Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.diffusion.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.diffusion.kernel.step`
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

- `state_dynamics`
- `diffusion`
- `langevin`
- `stochastic`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*