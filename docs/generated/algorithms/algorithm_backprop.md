# Backpropagation (algorithm.backprop)

**Kind:** algorithm
**Axis:** N/A (algorithm)
**Status:** kernel_verified
**Kernel Technology:** torch_compile
**Supported Backends:** reference, kernel

## Purpose

Standard backpropagation with automatic differentiation.

## Mathematics


    L = loss(f_θ(x), y)
    Δθ = -η ∇_θ L
    

## Invariants

- gradient matches autograd reference
- deterministic under fixed seed
- parameters updated via optimizer step

## Reference Implementation

**Entrypoint:** `computronium.algorithms.backprop.reference.step`

## Kernel Implementation

**Entrypoint:** `computronium.algorithms.backprop.kernel.step`
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

- `backprop`
- `autograd`
- `baseline`

## Notes

Reference implementation uses PyTorch autograd. Kernel may use torch.compile.


## Algorithm Family

**Family:** gradient_descent

## Primitive Dependencies

- primitive.state_dynamics.instantaneous_pass
- primitive.credit_assignment.reverse_mode
- primitive.parameter_update.euclidean

---
*Generated from `ImplementationSpec` metadata. Do not edit manually.*