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

### 2.3 The hybrid credit (T3b)

`HybridCredit` composes a lockstep PEPITA trunk with an exact-gradient head.
Steps 1–2 run the trunk under `no_grad`, detach the boundary, and take the
head's true gradients plus the boundary error from one `autograd.grad` call.
Step 3 modulates the input with the boundary error and advances the trunk's
standard and modulated chains layer by layer. Only the head's 2-layer graph is
retained; the trunk's working set is one layer's two chains.

| Arm | L=4 | L=8 | L=16 | L=32 | Class |
|---|---|---|---|---|---|
| Hybrid, lockstep trunk | 81.0 MB | 81.0 MB | 81.0 MB | 81.0 MB | flat |
| Hybrid, store-all trunk | 122.3 MB | 250.3 MB | 506.3 MB | 1018.3 MB | O(L) |

Peak above the weight-gradient set (one parameter-sized tensor per layer is
paid by any pseudo-gradient credit), one credit step, W=512, B=4096, 10 classes,
RTX 3080 10 GiB. The store-all row is the **negative control**: it retains both
trunk activation lists, which is the mechanism the lockstep removes. The
lockstep trunk's per-layer deltas equal the store-all hybrid at `atol=1e-7`
(**measured max|Δ| = 0.0**, bit-exact on the seeded fixture), and the head's
gradients equal plain
backprop's at the same boundary. The measured head graph is the only retained
activation set; the trunk's O(B·W) working set is the measured flat term.

### 2.4 The composed pilot (T6) — and what it found

The claim point is L=32, B=8192, W=1024, fp32, CIFAR-10 (fixed 10k-image train
subset, full 10k test split), 200 steps, 3 pilot seeds. `c` is measured at the
same point, not inherited from §2.1: two depth deltas at this width and batch
give **c = 4.125 with 0.0 % spread** (8→16→32), and the declared appendix is
`c·L·B·W·4` with c=4.1.

| Arm | val_acc | σ | Activations MB | Peak MB | Share | Binding | Fwd-eq | Walltime s |
|---|---|---|---|---|---|---|---|---|
| `backprop` | 0.100 | 0.000 | 4229 | 4494 | 0.941 | yes | 4.19 | 34.3 |
| `backprop+ckpt` | 0.100 | 0.000 | 1637 | 1902 | 0.861 | reported | 4.80 | 39.6 |
| `hybrid` | 0.100 | 0.000 | 3249 | 3513 | 0.925 | reported | 5.50 | 45.5 |
| `local` (PEPITA) | 0.100 | 0.000 | 3365 | 3630 | 0.927 | reported | 6.64 | 54.9 |

Controls: the **instrument control passes** (`c = 4.125`, spread 0.0 %, within
10 % of the declared 4.1); the **learning control passes** at L=8 (backprop
0.419 vs checkpointed 0.419, floor 0.409). Ladder at L=8 (200 steps, 1 seed,
`(0.1, 0.3, 1.0)`): backprop 0.351/0.419/0.170, PEPITA 0.393/0.400/0.188,
hybrid 0.100/0.163/0.100. Frozen LR is 0.3 for every arm.

Two findings, both measured, both named:

- **T6b — the composed path pays the pipeline's store-all forward.** The hybrid's
  credit-level trunk is flat at 81 MB (§2.3), but on the composed training path
  its activation set is 3249 MB against the checkpointed arm's 1637 MB (1.98×).
  Mechanism: `core/pipeline._run_train_step_tensor_impl` materialises
  `forward_pass(...)` before the credit runs, and it does so with autograd
  enabled although `HybridCredit.requires_autograd` is `False`; the chain is
  held by the phase states. The `≤ 0.5×` activation claim is unreachable until a
  credit may own its free pass. Lock:
  `test_memory_frontier.py::test_the_hybrid_activation_set_is_half_the_checkpointed_arms`
  (strict `xfail`; 843 MB vs 437 MB at the lock's smaller point).
- **T6c — the plain stack does not leave the plateau at the claim depth.** At
  L=32 every arm reports val_acc 0.100 with σ=0.000 and the backprop loss is
  pinned at 2.2132 from step 200 through step 1000 (measured separately), while
  L=8 reaches 0.419. A depth rung whose own baseline does not learn is not
  evidence. The plan's stated fallback applies: LayerNorm (c≈2), or a
  depth-stable geometry, with the appendix recomputed in the same commit.

Ruler: val_acc on the full 10k test split; memory from `EpochResource`'s
decomposition; forward-equivalents measured against one forward pass of the same
batch. The pilot is a screen — its accuracy rows are coordinates at 200 steps,
never a claim.

## 3. Open locks

| Lock | Test | Cost |
|---|---|---|
| No fabricated activation measurement | `tests/property/test_kernel_truth_lock.py` | 9 s |
| Stub detector (nudged ≠ free) | `tests/property/test_kernel_truth_lock.py` | 9 s |
| Decomposition sums to peak; measured c | `tests/property/test_memory_binding.py` | 10 s (CUDA) |
| Every credit row declares its estimator coordinate | `tests/property/test_estimator_lock.py` | 9 s |
| Lockstep ≡ store-all, per layer, `atol=0`; peak flat in depth | `tests/property/test_lockstep_parity.py` | 9 s (4 s CUDA) |
| Hybrid trunk ≡ store-all hybrid `atol=1e-7`; head ≡ backprop; peak flat | `tests/property/test_hybrid_parity.py` | 16 s (2 s CUDA) |
| Pilot point: measured c, binding gate, ckpt ≤ 0.5× activations | `tests/property/test_memory_frontier.py` | 20 s (CUDA) |
| **Hybrid ≤ 0.5× ckpt activations on the composed path (T6b, xfail)** | `tests/property/test_memory_frontier.py` | 20 s (CUDA) |
