# Instantaneous Pass (primitive.state_dynamics.instantaneous_pass)

**Kind:** primitive
**Axis:** state_dynamics
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Single-pass feedforward dynamics for Backprop and Forward-Forward algorithms

## Mathematics


a_{l+1} = σ(W_l a_l + b_l)
    

## Invariants

- deterministic under fixed seed
- state remains finite
- no settling iterations required

## Reference Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.instantaneous_pass.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.instantaneous_pass.kernel.step`
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
- `instantaneous`
- `backprop`
- `forward_forward`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*