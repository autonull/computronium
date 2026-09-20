# Hebbian/STDP (algorithm.hebbian)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Hebbian learning: neurons that fire together, wire together.

## Mathematics


    ΔW_l ∝ h_l h_{l-1}^T  # Hebbian
    ΔW_l ∝ (h_l - ⟨h_l⟩)(h_{l-1} - ⟨h_{l-1}⟩)^T  # Covariance
    

## Invariants

- local weight updates only
- no global error signal required
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.hebbian.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.hebbian.kernel.step`
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

- `hebbian`
- `stdp`
- `local_learning`
- `correlation`

## Notes

Uses LocalGoodnessCredit as a proxy for Hebbian correlation.


## Algorithm Family

**Family:** hebbian

## Primitive Dependencies

- primitive.state_dynamics.instantaneous_pass
- primitive.credit_assignment.local_goodness
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*