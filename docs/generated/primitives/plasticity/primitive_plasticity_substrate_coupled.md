# Substrate Coupled (primitive.plasticity.substrate_coupled)

**Kind:** primitive
**Axis:** plasticity
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Substrate-coupled plasticity.

## Mathematics


Plasticity coupled to substrate physics (e.g., memristive conductance).
    

## Invariants

- deterministic under fixed seed
- substrate state evolves with plasticity

## Reference Implementation

**Entrypoint:** `computronium.primitives.plasticity.substrate_coupled.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.plasticity.substrate_coupled.kernel.step`
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

- `plasticity`
- `substrate`
- `coupled`
- `memristive`

## Notes

Reference wraps SubstrateCoupledPlasticity; kernel falls back to reference




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*