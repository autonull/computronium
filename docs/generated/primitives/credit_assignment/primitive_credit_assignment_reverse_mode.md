# Reverse Mode (primitive.credit_assignment.reverse_mode)

**Kind:** primitive
**Axis:** credit_assignment
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Reverse-mode autograd credit (backprop baseline).

## Mathematics


∂L/∂W via torch.autograd.grad
    

## Invariants

- deterministic under fixed seed
- exact gradient match with autograd

## Reference Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.reverse_mode.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.credit_assignment.reverse_mode.kernel.step`
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

- `backprop`
- `gradient`
- `autograd`
- `baseline`

## Notes

Reference wraps GradientCredit; kernel falls back to reference




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*