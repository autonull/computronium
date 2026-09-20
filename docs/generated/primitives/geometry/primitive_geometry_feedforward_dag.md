# Feedforward DAG Geometry (primitive.geometry.feedforward_dag)

**Kind:** primitive
**Axis:** geometry
**Status:** reference_only
**Kernel Technology:** triton
**Supported Backends:** reference, kernel

## Purpose

Standard feedforward DAG topology (MLP/CNN) with configurable depth and width.

## Mathematics


    h_l = σ(W_l · h_{l-1} + b_l)  # layer-wise computation
    forward: sequential application of Linear + activation layers
    

## Invariants

- output shape matches (batch, output_dim)
- deterministic under fixed seed
- activations remain finite

## Reference Implementation

**Entrypoint:** `computronium.primitives.geometry.feedforward_dag.reference.forward`

## Kernel Implementation

**Entrypoint:** `computronium.primitives.geometry.feedforward_dag.kernel.forward`
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

- `feedforward`
- `mlp`
- `dag`
- `sequential`

## Notes

Reference implementation delegates to FeedforwardGeometry. Kernel falls back to reference (Triton TODO).




---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*