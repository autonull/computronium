# Routing Plasticity (primitive.plasticity.routing)

**Kind:** primitive
**Axis:** plasticity
**Status:** kernel_unverified
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

State-dependent pathway gating with Gumbel-Softmax routing and per-unit modulation.

## Mathematics


    gate_logits_{t+1} = decay * gate_logits_t + lr * (x @ G)
    active_routes = GumbelSoftmax(gate_logits, temperature)  # training
              = top_k(gate_logits)                          # eval
    mask_ℓ = sigmoid(gate_logits @ U_ℓ)  # per-layer modulation
    

## Invariants

- gate logits remain bounded
- active routes sum to 1 per sample (training) or match top_k (eval)
- deterministic under fixed seed

## Reference Implementation

**Entrypoint:** `computronium.primitives.plasticity.routing.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.plasticity.routing.kernel.step`
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

- `routing`
- `gating`
- `sparse_routing`
- `conditional_computation`
- `moe`

## Notes

Accelerated kernel could fuse gate logit update with routing selection.




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*