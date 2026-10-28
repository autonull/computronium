# Beyond Backpropagation

<!-- gen:matrix_total --> carded implementations — <!-- gen:matrix_primitive_count --> primitives and <!-- gen:matrix_algorithm_count --> composed algorithms — each with an identity card: reference, declared deviations, objective, pseudo-gradient, and symmetry.

## The kernel ladder

An implementation earns its rung. Nothing starts verified.

| Rung | Count | What the rung asserts |
|---|---:|---|
| `reference_only` | <!-- gen:reference_only_count --> | readable, tested semantics; no accelerated path |
| `kernel_unverified` | <!-- gen:kernel_unverified_count --> | a kernel exists; parity is not yet proven |
| `kernel_verified` | <!-- gen:kernel_verified_count --> | parity against the reference plus a micro-benchmark |

At the top rung today:

<!-- gen:kernel_verified_table -->

The top rung is deliberately small. The large `reference_only` count is the honest state of the art, published rather than hidden: a scientific record needs the slow, readable implementation more than it needs a fast unverified one.

<!-- notes -->
The ladder is the answer to "why should I trust the fast path". A rung is a claim with a test behind it: parity to the reference implementation, then a micro-benchmark that proves the kernel is worth dispatching.

If asked why so few are verified: because verification is ranked by use, and an unverified kernel is still a documented, runnable system. Say the number out loud rather than implying everything is optimized.
<!-- /notes -->
