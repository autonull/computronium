# Diffusion Eqprop (algorithm.diffusion_eqprop)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** reference_only
**Kernel Technology:** torch_compile
**Supported Backends:** reference, kernel

## Purpose

Diffusion Equilibrium Propagation with continuous-time dynamics

## Mathematics



    dx/dt = -∇_x E(x) + √(2β) dW
    Δθ = -η ∇_θ E

    

## Invariants

- deterministic under fixed seed
- state remains finite
- matches reference implementation

## Reference Implementation

**Entrypoint:** `computronium.algorithms.diffusion_eqprop.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.diffusion_eqprop.kernel.step`
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

- primitive.state_dynamics.diffusion
- primitive.credit_assignment.thermodynamic_contrast
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*