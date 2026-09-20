# Ternary Eqprop (algorithm.ternary_eqprop)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** reference_only
**Kernel Technology:** torch_compile
**Supported Backends:** reference, kernel

## Purpose

Ternary-Weight Equilibrium Propagation with STE quantization

## Mathematics



    w ∈ {-α, 0, +α}
    L = loss(f_θ(x), y)
    Δθ = -η ∇_θ L (with STE for ternary projection)

    

## Invariants

- deterministic under fixed seed
- state remains finite
- matches reference implementation

## Reference Implementation

**Entrypoint:** `computronium.algorithms.ternary_eqprop.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.ternary_eqprop.kernel.step`
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
- primitive.substrate.ternary

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*