# PEPITA (algorithm.pepita)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

PEPITA: fixed random B, error-modulated second forward pass, autograd update.

## Mathematics


    h_l = σ(W_l h_{l-1})
    h_l^e = σ(W_l h_{l-1} + B_l e)  # error-modulated pass

    ΔW_l ∝ (h_l^e - h_l) h_{l-1}^T
    

## Invariants

- single fixed random feedback matrix B
- error modulation in second forward pass
- autograd update on perturbed states
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.algorithms.pepita.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.pepita.kernel.step`
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

- `pepita`
- `local_learning`
- `error_modulated`
- `random_feedback`

## Notes

Distinct from Forward-Forward: uses error signal, not label injection.


## Algorithm Family

**Family:** local_goodness

## Primitive Dependencies

- primitive.state_dynamics.instantaneous_pass
- primitive.credit_assignment.local_goodness
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*