# Predictive Settling (primitive.state_dynamics.predictive_settling)

**Kind:** primitive
**Axis:** state_dynamics
**Status:** kernel_verified
**Kernel Technology:** torch_compile
**Supported Backends:** reference, kernel

## Purpose

Predictive coding settling dynamics (PCN).

## Mathematics


    μ_0 = x                    # input clamped
    μ_l ← μ_l - η · (μ_l - f(μ_{l-1} W_{l-1} + b_{l-1}))  # prediction error minimization
    

## Invariants

- prediction errors decrease or remain bounded
- state remains finite
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.predictive_settling.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.predictive_settling.kernel.step`
**Technology:** torch_compile

## Parity Tolerance

| Metric | Threshold |
|--------|-----------|
| Max Absolute Difference | 0.0001 |
| Max Relative Difference | 0.001 |
| Minimum Cosine Similarity | 0.999 |

## Status

Current status: **kernel_verified**

## Tags

- `predictive_coding`
- `pcn`
- `settling`

## Notes

Accelerated kernel should preserve the settled state within tolerance.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*