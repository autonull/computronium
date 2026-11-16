# Benchmarks — published parity and measured complexity

Two tables, one purpose: every number a claim rests on is named with the
coordinate it was measured at, so a reader can rerun it and a defect can be told
apart from a result.

TODO93 §3 (P1) owns the parity table; §1/§9.1 own the complexity table. A row
enters either table in the commit that measures it. An unmeasured row is absent,
never guessed, and a row whose backend is a stub is `unavailable` with the
reason — never measured.

## 1. Published parity (P1, scoped)

Scope is the three publishables plus the arm the memory frontier actually uses:
`pepita`, `local_goodness`, `random_projections`, and the hybrid trunk's local
rule. Auditing all eight rules is cost without a decision.

| Credit | Dataset | Architecture | Backend path | Published | Ours | Δ | σ | Seeds | Command | Date |
|---|---|---|---|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — | — | — | — | — |

**Tolerance.** Within ±1 pp, or the published run-to-run σ when that is larger.
A gap beyond tolerance opens a defect ticket before any new measurement. A
second failure after the fix pass is a refusal with a written reason, never a
quiet exclusion.

**Protocol note.** Published local-rule numbers are frequently single-seed or
best-of. Reproduce their protocol, compare means, record σ, and state when ours
is a mean over more seeds than theirs.

## 2. Measured complexity (claimed vs actual)

Declared class: `KernelBackend.memory_complexity`. Measured: activation bytes
from the depth ladder. `verified` is `True` only when the measured ladder
supports the declared class on that path; until then it is `False` and
`get_memory_stats()` reports `activations_mb=None`.

| Backend | Path | Declared | Measured | Verified | Cell geometry | Date |
|---|---|---|---|---|---|---|
| `BackpropKernelBackend` | `acceleration/backprop_kernels.py` | O(L) | `c·L·B·W·4`, c=4.1 | n/a (kernel stats unmeasured) | Linear+ReLU fp32, W=256, B=2048, L=4/8/16 | 2026-11-15 |
| `PEPITAContrastiveKernel` | `acceleration/contrastive_kernels.py` | O(1) | ≈2× forward (two full activation lists) | **no** | read of `contrastive_step` | 2026-11-15 |
| `FFContrastiveKernel` | `acceleration/contrastive_kernels.py` | O(1) | unavailable (no label channel → zero update) | no | — | 2026-11-15 |
| `SNNContrastiveKernel` | `acceleration/contrastive_kernels.py` | O(1) | unavailable (nudge is a no-op) | no | — | 2026-11-15 |
| `FFKernelBackend` | `acceleration/ff_kernels.py` (lockstep) | O(1) | **flat** 66.3 MB at L=4/8/16/32 | **yes** | Linear+ReLU fp32, W=512, B=4096 | 2026-11-16 |
| `PEPITAKernelBackend` | `acceleration/ff_kernels.py` (lockstep) | O(1) | **flat** 58.5 MB at L=4/8/16/32 | **yes** | Linear+ReLU fp32, W=512, B=4096 | 2026-11-16 |
| `HebbianKernelBackend` | `acceleration/hebbian_kernels.py` | O(1) | one layer at a time | pending | — | — |
| `TPKernelBackend` | `acceleration/tp_kernels.py` | O(1) | stores inverses (≈2× params) | no | — | 2026-11-15 |

### 2.1 The claim-path decomposition (T4a)

`EpochResources.record` now decomposes the CUDA peak into parameters, optimizer
state, and the remainder. Measured on the claim geometry (plain backprop,
Linear+ReLU, fp32, no norm):

| Depth | Peak | Params | Optimizer | Activations | Share |
|---|---|---|---|---|---|
| 4 | 36.8 MB | 0.8 MB | 0.8 MB | 35.3 MB | 0.96 |
| 8 | 71.8 MB | 1.8 MB | 1.8 MB | 68.3 MB | 0.95 |
| 16 | 141.8 MB | 3.8 MB | 3.8 MB | 134.3 MB | 0.95 |

W=256, B=2048, 10 classes. The gate reads the **plain backprop** row; a
checkpointed arm's share is reported, never gated (TODO93 B1). A cell whose
share is below 0.5 is `[regime-mismatch]` and enters no claim table.

`auxiliary_mb` is `None` until a mechanism declares state held outside both the
geometry parameters and the optimizer (feedback matrices, consolidation
buffers); until then such state sits inside the reported remainder, and the
claim row must use a geometry where the remainder is activations.

### 2.2 The lockstep rung (T3)

Both two-pass families now run **lockstep**: pass 1 keeps only the output, pass 2
recomputes the standard and perturbed chains layer-by-layer and applies each
layer's update before the next layer is produced. Peak is the two chains'
working set, not `L` layers' worth, and the update is exact against the store-all
schedule because each `W_l` is used once per pass before its update.

| Arm | L=4 | L=8 | L=16 | L=32 | Class |
|---|---|---|---|---|---|
| Forward-Forward, lockstep | 66.3 MB | 66.3 MB | 66.3 MB | 66.3 MB | flat |
| Forward-Forward, retained stream | 100.3 MB | 168.3 MB | 304.4 MB | 576.4 MB | O(L) |
| PEPITA, lockstep | 58.5 MB | 58.5 MB | 58.5 MB | 58.5 MB | flat |
| PEPITA, retained stream | 92.5 MB | 160.5 MB | 296.5 MB | 568.5 MB | O(L) |

CUDA peak above the allocated parameters, one step, W=512, B=4096, 10 classes,
RTX 3080 10 GiB. The retained row is the **negative control**: it materializes
the contrast stream, which is the mechanism the lockstep removes. Deliberate
cost of the rung: PEPITA recomputes the standard chain in pass 2, so it makes
three layer sweeps per step where the store-all made two — compute bought for
memory, and named here rather than discovered later.

## 3. Open locks

| Lock | Test | Cost |
|---|---|---|
| No fabricated activation measurement | `tests/property/test_kernel_truth_lock.py` | 9 s |
| Stub detector (nudged ≠ free) | `tests/property/test_kernel_truth_lock.py` | 9 s |
| Decomposition sums to peak; measured c | `tests/property/test_memory_binding.py` | 10 s (CUDA) |
| Every credit row declares its estimator coordinate | `tests/property/test_estimator_lock.py` | 9 s |
| Lockstep ≡ store-all, per layer, `atol=0`; peak flat in depth | `tests/property/test_lockstep_parity.py` | 9 s (4 s CUDA) |
