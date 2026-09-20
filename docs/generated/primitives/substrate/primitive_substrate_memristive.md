# Memristive (primitive.substrate.memristive)

**Kind:** primitive
**Axis:** substrate
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Memristive substrate with IR-drop and conductance bounds.

## Mathematics


V = IR; dG/dt = f(V, G)
    

## Invariants

- deterministic under fixed seed
- conductance stays within bounds

## Reference Implementation

**Entrypoint:** `computronium.primitives.substrate.memristive.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.substrate.memristive.kernel.step`
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

- `substrate`
- `memristive`
- `ir-drop`
- `conductance`

## Notes

Reference wraps MemristiveSubstrate; kernel falls back to reference




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*