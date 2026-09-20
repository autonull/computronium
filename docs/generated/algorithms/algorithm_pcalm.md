# PC-ALM (algorithm.pcalm)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Augmented Lagrangian Predictive Coding.

## Mathematics


    L_ρ = Σₗ ½‖hₗ − f_θₗ(hₗ₋₁)‖² + Σₗ ⟨λₗ, hₗ − f_θₗ(hₗ₋₁)⟩
          + (ρ/2) Σₗ ‖hₗ − f_θₗ(hₗ₋₁)‖²

    Dynamics (discretized):
        cₗ = hₗ − f_θₗ(hₗ₋₁)         # constraint violation
        λₗ ← λₗ + step_size · cₗ       # dual update (PI controller)
        hₗ ← hₗ − step_size · (cₗ + λₗ + ρ·cₗ − Jₗ₊₁ᵀ·(cₗ₊₁ + λₗ₊₁ + ρ·cₗ₊₁))

    Weight update (local Hebbian):
        ΔWₗ ∝ −λₗ hₗ₋₁ᵀ
    

## Invariants

- local error signals remain bounded
- settling dynamics are deterministic under fixed seed
- slow parameters are not mutated during intra-episode steps

## Reference Implementation

**Entrypoint:** `computronium.algorithms.pcalm.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.pcalm.kernel.step`
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

- `predictive_coding`
- `augmented_lagrangian`
- `local_learning`

## Notes

Kernel should fuse the primal-dual settle loop where possible.


## Algorithm Family

**Family:** predictive_coding

## Primitive Dependencies

- primitive.state_dynamics.pc_alm_settling
- primitive.credit_assignment.pc_alm

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*