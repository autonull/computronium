# Energy Minimization (primitive.state_dynamics.energy_minimization)

**Kind:** primitive
**Axis:** state_dynamics
**Status:** kernel_verified
**Kernel Technology:** torch_compile
**Supported Backends:** reference, kernel

## Purpose

Energy-based settling (Equilibrium Propagation, Hopfield, CHL).

## Mathematics


Free energy: F = -1/2 Σ_ij W_ij s_i s_j - Σ_i b_i s_i
Dynamics: τ ds/dt = -∂F/∂s + noise
Heavy-ball: v ← μ·v - η·∂F/∂s; s ← s + v
    

## Invariants

- free energy decreases or remains bounded
- state remains finite
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.energy_minimization.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.state_dynamics.energy_minimization.kernel.step`
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

- `equilibrium_propagation`
- `hopfield`
- `energy_based`

## Notes

Reference implementation delegates to ontology class.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*