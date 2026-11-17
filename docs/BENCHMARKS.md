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
| `hybrid` | 0.100 | 0.000 | 611 | 876 | 0.698 | reported | 4.27 | 34.6 |
| `local` (PEPITA) | 0.100 | 0.000 | 3365 | 3630 | 0.927 | reported | 6.64 | 54.9 |

Controls: the **instrument control passes** (`c = 4.125`, spread 0.0 %, within
10 % of the declared 4.1); the **learning control passes** at L=8 (backprop
0.419 vs checkpointed 0.419, floor 0.409). Ladder at L=8 (200 steps, 1 seed,
`(0.1, 0.3, 1.0)`): backprop 0.351/0.419/0.170, PEPITA 0.393/0.400/0.188,
hybrid 0.100/0.163/0.100. Frozen LR is 0.3 for every arm.

Two findings, both measured, both named:

- **T6b — the composed path paid the pipeline's store-all forward (fixed and
  locked).** The hybrid's credit-level trunk is flat at 81 MB (§2.3), but on the
  composed training path its activation set was 3249 MB against the
  checkpointed arm's 1637 MB (1.98×). Mechanism:
  `core/pipeline._run_train_step_tensor_impl` materialised `forward_pass(...)`
  before the credit ran, and it did so with autograd enabled although
  `HybridCredit.requires_autograd` is `False`; the chain was held by the phase
  states. Fix: a credit may own its free pass (`free_activations`), and the
  pipeline then never materialises the store-all set — neither the pre-forward
  nor the FREE settle nor the post-update free-metrics pass. At the lock's
  smaller point the hybrid now reads **210 MB against the checkpointed arm's
  437 MB (0.48×)**; the `≤0.5×` lock is live (`test_memory_frontier.py`,
  no `xfail`), and a tripwire lock proves the pipeline's forward is gone for
  the hybrid and present for the plain arm.
- **T6c — the plain stack does not leave the plateau at the claim depth.** At
  L=32 every arm reports val_acc 0.100 with σ=0.000 and the backprop loss is
  pinned at 2.2132 from step 200 through step 1000 (measured separately), while
  L=8 reaches 0.419. A depth rung whose own baseline does not learn is not
  evidence. §2.10 records the cheap pass's rung and its refusal.

Ruler: val_acc on the full 10k test split; memory from `EpochResource`'s
decomposition; forward-equivalents measured against one forward pass of the same
batch. The pilot is a screen — its accuracy rows are coordinates at 200 steps,
never a claim.

### 2.5 The batch-1 plasticity ladder (C1)

Two apparatus defects blocked this screen; both are fixed and locked
(CORRECTIONS 9–10). Measured on SplitMNIST at batch 1, one epoch per task, five
tasks in the fixed order, W=256, 2000 held-out samples per task, seed 41 plus a
disjoint confirmation seed 42 (RTX 3080 10 GiB, 2026-11-16):

| arm | LR | mean final acc | last task acc | BWT | forgetting | s |
|---|---|---|---|---|---|---|
| local (PEPITA) | 1e-3 | 0.945 | 0.970 | −0.047 | 0.038 | 259 |
| backprop | 1e-3 | 0.839 | 0.967 | −0.181 | 0.145 | 242 |
| local | 1e-2 | 0.882 | 0.979 | −0.134 | 0.107 | 228 |
| backprop | 1e-2 | 0.803 | 0.986 | −0.235 | 0.188 | 220 |
| local | 1e-1 | 0.569 | 0.982 | −0.529 | 0.423 | 258 |
| backprop | 1e-1 | 0.827 | 0.983 | −0.206 | 0.165 | 233 |
| local (confirm) | 1e-3 | 0.947 | 0.967 | −0.045 | 0.036 | 260 |
| backprop (confirm) | 1e-3 | 0.893 | 0.968 | −0.114 | 0.091 | 287 |

**Verdict: promote.** Local clears the pre-registered floor (0.55, 4.5 σ above
chance) on both seeds, and the control clears it too. C moves to its retention
protocol (C2, the EWC-strength ladder at frozen LR); it is not refused.

**What the defect probes measured.** (a) With the credit's second pass reading
task-local labels, local scored 0.405/0.426/0.445/0.652/**0.030** per task on
task-local geometry; on task 1 alone after the label-channel fix it reached
0.964. The label channel, not the algorithm, produced the chance-level cell.
(b) Before the data order got its own seeded generator, backprop at LR 1e-3 read
0.926; with the seeded order it read 0.839 — a 9 pp swing, so a single row is a
coordinate, never a claim.

**Box and rulers.** Task/architecture fixed (SplitMNIST, 784-256-256-10,
`init_scale=0.1`, no dropout); the knob is LR ∈ (1e-3, 1e-2, 1e-1); neither
C1 arm reads an EWC strength (that knob belongs to C2), epochs/task = 1,
batch = 1. The ladder's best
local point is its lower edge (1e-3), so the box is not exhausted: a downward
extension (3e-4, 1e-4) is the next rung before any *optimum* is named. The
accuracy ruler is a 2000-sample held-out split (1 σ = 0.011); the cost is the
measured cell walltime.

Command: `uv run python -m computronium.validation.plasticity_ladder --stage
plasticity --device cuda`

### 2.6 The consolidation-strength ladder (C2)

C1 promotes plasticity at the lower edge of its LR ladder (1e-3). C2 asks the
retention question at that frozen point: at a matched per-step cost, does
local × EWC forget less than backprop × EWC? The gate was pre-registered
before the first cell: floor 0.55 on both seeds, per-step cost ratio ≤1.5×,
retention margin δ = 2√2σ ≈ 3.2 pp, and saturation when the top rung reduces
local forgetting by less than δ over the rung below.

Two apparatus facts bound the box before any number: the λ ladder is the only
knob (1/10/100), and the frozen LR is the best C1 *local* point, itself the
ladder's lower edge, so no interior optimum is named here. The first launch
found a live defect (CORRECTION 12): the runner re-consolidated at every task
start, overwriting the drift importance with uniform damping, so the ladder
measured one point three times. Those two cells are kept as the defect probe
(`results/t93_c1/consolidation.inert.cells.jsonl`), never as a ladder. After
the fix (`ElasticConsolidationUpdate.anchor`), the ladder was restarted and
one kill was resumed from its cell log (the last confirmation cell reused the
seven measured cells).

Measured on SplitMNIST at batch 1, one epoch/task, five tasks in the fixed
order, W=256, 2000 held-out samples/task, seed 41 plus the disjoint
confirmation seed 42 at the best λ (RTX 3080 10 GiB, 2026-11-16):

| arm | λ | mean final acc | last task acc | BWT | forgetting | state MiB | s |
|---|---|---|---|---|---|---|---|
| local × EWC | 1 | 0.950 | 0.951 | −0.025 | 0.021 | 3.1 | 298 |
| backprop × EWC | 1 | 0.943 | 0.971 | −0.053 | 0.042 | 3.1 | 311 |
| local × EWC | 10 | 0.951 | 0.952 | −0.024 | 0.020 | 3.1 | 311 |
| backprop × EWC | 10 | 0.945 | 0.970 | −0.049 | 0.040 | 3.1 | 274 |
| local × EWC | 100 | 0.952 | 0.943 | −0.017 | 0.015 | 3.1 | 279 |
| backprop × EWC | 100 | 0.963 | 0.967 | −0.024 | 0.020 | 3.1 | 262 |
| local × EWC (confirm) | 100 | 0.951 | 0.939 | −0.016 | 0.016 | 3.1 | 263 |
| backprop × EWC (confirm) | 100 | 0.958 | 0.965 | −0.029 | 0.024 | 3.1 | 233 |

**Verdict: close.** At the saturation point λ=100, local forgets 0.015
against the control's 0.020 (gain +0.005, below the 3.2 pp margin), and its
mean final accuracy is 1.1 pp *lower* (0.952 vs 0.963). The confirmation
seed repeats the direction: 0.016 vs 0.024 forgetting, 0.951 vs 0.958
accuracy. The per-step cost ratio is 1.07–1.13× (the matched-cost guard runs
at ≤1.5×), and both arms carry 3.1 MiB of consolidation state.

**What saturated.** The local arm's forgetting falls from 0.021 (λ=1) to 0.015
(λ=100) — 0.6 pp, below δ — and the control's from 0.042 to 0.020 (2.2 pp,
also below δ). So EWC strength stops buying retention beyond λ=10 on the local
arm, and the local-vs-control retention gap stays below the pre-registered
margin at the best point. The ladder's best point is at its upper edge for both
arms; a further extension cannot change the verdict (the top rung already moved
the cell by less than δ), so C closes here rather than promoting to C2b.

**What the row means for the thesis.** EWC closes most of plain backprop's
forgetting gap at this point (C1: 0.145 → 0.020 at λ=100), and it does so
without lowering accuracy (0.839 → 0.963). That is a composition result for
the *control*, not for local credit: the local arm already forgot little
without EWC (C1: 0.038), and consolidation moves it by 2.3 pp in total. The
residual local advantage (0.5–0.7 pp) is below the box's resolution, so it is
a coordinate, not a claim. C closes at its saturation point with its re-open
probes kept: a 5-seed retention protocol (rung 3), a matched-byte replay
composition, or SI/cascade at the same frozen LR.

Command: `uv run python -m computronium.validation.plasticity_ladder --stage
consolidation --device cuda`; replay from the cell log without training:
`... --stage consolidation --replay --device cuda`.

### 2.7 The routing ladder (B1)

The screen asked whether the straight-through (STE) surrogate's bias on the
router grows with the number of stacked hard selections. The question decides
the track: a gap that compounds would justify a matched pair of credits
(B2, STE+aux vs a local credit); a flat gap refuses the track with a
trigger.

Three apparatus facts bound the measurement before any number, all of them found
and fixed in this session (CORRECTIONS 13–15):

- the selections are **parallel and averaged**, not chained — a chained stack's
  joint gradient vanishes with depth, so a joint ratio measures the depth of the
  stack (CORRECTION 13);
- the gap is probed at declared optimiser steps (8/16/32), not at the end —
  once the router saturates, both gradients vanish and their ratio measures the
  one-hot limit (CORRECTION 14);
- the held-out split and the gap share the task's blob centers; only the
  samples move, or the accuracy ruler reads a different task (CORRECTION 15).

**What the gap is, and what it is not.** It is the relative norm between the
STE's per-selection router gradient and its declared reference, the
temperature-smoothed routing gradient at the same τ. The finite-difference probe
on the same smoothed objective validates the **reference**, not the STE: 0.000–0.013
against a 0.10 tolerance. Its level (~0.6–0.8) is structural — the STE's credit
runs through the selected experts only, the reference through all eight — so the
ladder's question is the **trend**, not the level.

Measured on the 4-class blob task (4096 train / 2000 held-out, 8 experts, k=2,
W=256 trunk, probe batch 512, RTX 3080 10 GiB, 2026-11-16):

| stage | depth | τ | seed | end-task acc | router acc | STE gap | ref. gap | s |
|---|---|---|---|---|---|---|---|---|
| temperature | 2 | 0.25 | 51 | 1.000 | 1.000 | 0.573 | 0.008 | 4.2 |
| temperature | 2 | 0.5 | 51 | 1.000 | 1.000 | 0.743 | 0.001 | 3.9 |
| temperature | 2 | 1.0 | 51 | 1.000 | 1.000 | 0.844 | 0.000 | 2.8 |
| depth | 1 | 0.25 | 51 | 0.933 | 1.000 | 0.819 | 0.003 | 1.8 |
| depth | 2 | 0.25 | 51 | 1.000 | 1.000 | 0.573 | 0.008 | 2.6 |
| depth | 4 | 0.25 | 51 | 0.999 | 0.999 | 0.655 | 0.008 | 5.3 |
| depth | 8 | 0.25 | 51 | 1.000 | 1.000 | 0.660 | 0.013 | 9.1 |
| confirmation | 1 | 0.25 | 52 | 0.999 | 1.000 | 0.681 | 0.004 | 1.5 |
| confirmation | 8 | 0.25 | 52 | 1.000 | 1.000 | 0.644 | 0.011 | 8.2 |

**Verdict: refuse.** The gap does not grow with the stack: 0.819 → 0.660
(−0.159) from depth 1 to depth 8 on the ladder seed, and −0.037 on the disjoint
confirmation seed, against the pre-registered margin δ = 0.05. Both ends of the
ladder are trained arms (end-task accuracy 0.933 / 1.000), the learning control
clears the 0.40 floor, and the router routes above its 0.25 chance level, so the
refusal is not an invalid arm. The depth-1 point is the ladder's highest and the
fall to depth 2 is consistent with responsibility dilution by the averaged
stack; no depth makes the surrogate's bias compound at this box.

**Box and rulers.** Task/architecture fixed (4-class blobs, 8 experts, k=2,
W=256, no dropout); the knobs are τ ∈ (0.25, 0.5, 1.0) at depth 2 and the
depth ladder at the best τ, and the LR is frozen at 1e-3 for both ladders. The
accuracy ruler is a 2000-sample held-out split (1 σ = 0.010); router accuracy's
chance is k/n = 0.25; the gap is a relative norm on a fixed probe batch, with
FD tolerance 0.10 and step 1e-2. The cost is 1.5–9.1 s per cell.

Command: `uv run python -m computronium.validation.routing_ladder --device
cuda`; replay from the cell log without training: `... --replay`.

**What the refusal means, and its trigger.** B does not promote to its matched
pair. The reversal trigger is a different box, not a rerun: a **chained** stack
at per-depth matched LR, the canonical full-support STE with Gumbel noise as the
treatment, or a wider expert count (k ≥ 4). The re-open command is this module
with that box, and §14 carries the trigger.

The defect probe (the chained, end-of-training cells at LR 1e-2) is kept as
`results/t93_b1/defect_probe/`; it is evidence of the apparatus defects, never
a ladder.

### 2.8 The estimator atlas (E1)

The screen asked what each estimator kind's bias/variance/compute coordinates
are at matched compute on one task. It is not a competition: the table is the
artifact, publishable whether or not an arm wins, and it makes later estimator
comparisons commensurable.

**The reference, and what "bias" means.** The exact arm (`BackpropCredit`) is
the declared reference; a finite-difference probe on a small net validates the
autograd reference itself at cos = 1.0000. A gradient-approximation arm's angle
is its update direction against that reference. An objective-local arm declares
`bias_reference="none"`: its angle is update-direction alignment, never bias.

**The fair chance is per arm, not one shared LR.** A single LR is not a fair
box: at 1e-3 the FA default's update is ~500× smaller than the exact gradient
and the arm collapses to 0.093; at 1e-1 the hybrid's local trunk diverges to
0.097. Each arm therefore gets a 3-point LR ladder (1e-3/1e-2/1e-1) at ladder
seed 59, a confirmation at the best point (seed 60), and disjoint claim seeds
61/62/63. The selected LR is part of the row; compute is matched (600 batches
of 32, one epoch, the same architecture). This is the apparatus defect found
and fixed in this session (CORRECTION 16).

Measured on MNIST quick mode (feedforward 784-32-10, Linear+ReLU, batch 32, 600
batches, one epoch, CPU, 2026-11-16); held-out full test split (10,000 samples,
1σ = 0.3 pp), chance 0.1, floor 0.25:

| arm | kind | bias ref | LR | angle (mean ± σ) | magnitude (mean ± σ) | val acc (mean ± σ) | fwd-eq | s/epoch |
|---|---|---|---|---|---|---|---|---|
| gradient | exact | exact_tractable | 1e-2 | +1.000 ± 0.000 | 1.000 ± 0.000 | 0.914 ± 0.006 | 6 | 6.8 |
| random_projections | gradient_approx | exact_tractable | 1e-1 | +0.125 ± 0.079 | 0.002 ± 0.000 | 0.821 ± 0.007 | 6 | 6.4 |
| pepita | objective_local | none | 1e-2 | +0.972 ± 0.001 | 1.604 ± 0.110 | 0.923 ± 0.003 | 6 | 6.5 |
| hybrid | hybrid | none | 1e-2 | +0.185 ± 0.007 | 0.395 ± 0.020 | 0.827 ± 0.007 | 6 | 6.3 |
| local_goodness | objective_local | none | 1e-1 | +0.143 ± 0.109 | 1.211 ± 0.308 | 0.816 ± 0.089 | 6 | 7.2 |
| pc_alm | gradient_approx | exact_tractable | 1e-3 | +0.071 ± 0.029 | 0.040 ± 0.006 | 0.105 ± 0.013 | — | 8.1 |

**Verdict: atlas, not a promotion or a refusal.** The reference control (FD vs
autograd 1.0000) and the learning control (exact arm 0.914 ± 0.006, floor 0.25)
both pass, and every measured arm updates. The table is the artifact.

**What the coordinates say.** PEPITA's update aligns with the exact direction
(0.972 ± 0.001) and is 1.60× its scale; its accuracy is +0.9 pp above the exact
arm (0.923 vs 0.914), which is 1.3σ at this ruler and is a coordinate, not a
claim. The FA default's update is 0.002× the exact scale with alignment
0.125 ± 0.079 — the default feedback scale is an optimisation knob, not a bias
claim, and the arm still learns 0.821. Forward-Forward (`local_goodness`)
aligns 0.143 and has the widest seed variance (0.089 in accuracy, 0.308 in
scale), so its mean is a coordinate at n=3, not an ordering. The hybrid aligns
0.185 and is stable across seeds (0.007 accuracy, 0.020 scale), but at 0.827 it
is not a win over its PEPITA trunk (0.923): the lockstep trunk/head split is
the mechanism, not a free accuracy gain. The structural fwd-eq ruler is 6
(2 × `max_steps`) for every settle-based arm; PCALM's is `None` because its
FLOP counter fell back to parameter counting (1.0), an honest gap, never a
matched-budget claim.

**The one refusal row.** PC-ALM is outside its card's validated limit at this
box: the card validates depth 100, and at depth 2 the settle diverges at LR
1e-2/1e-1 (NaN at step 1/2) and reads chance at 1e-3 (0.105 ± 0.013; one seed
refused outright). The row is a **regime-mismatch/refusal**, not a verdict on
the algorithm. The trigger is a depth-100 box with its validated init; the
re-open command is this module with that box. No E2 primitive is admitted by
this table: the empty unbiased cells (score-function, forward-mode, zeroth
order) are visible, not pulled.

Command: `uv run python -m computronium.validation.estimator_atlas --device
cpu`; full rung: `... --full`; replay from the cell log without training:
`... --replay`. The per-seed table is `results/t93_e1/estimator.md`.

### 2.9 The substrate ladder (D1)

**Question.** On a constrained substrate model, does an energy-minimisation
learner reach digital parity at lower state per step? The parity reference is
the same rule on a digital substrate; the learning control is digital backprop
at the same budget. The box is MNIST quick mode, 784-32-10, batch 32, 600
batches, one epoch, beta 0.5, full 10k test split (1 sigma = 0.3 pp), CPU.

**The state ruler.** Device state per step is the declared width (32 bits/weight
digital, 2 bits/weight ternary + one fp32 scale per layer, 16 bits/weight for a
differential int8 pair). Train state is the fp32 latent set + optimizer buffer
(0.2 MB, equal for every arm) and is **declared, not claimed** as a saving: an
in-situ device would hold the weights, not a second fp32 copy.

| arm | LR ladder (1e-3 / 3e-3 / 1e-2) | settle 5 / 10 / 20 | confirmation | device B/weight |
|---|---|---|---|---|
| digital rule (control) | 0.858 / 0.896 / **0.914** | 0.913 / 0.914 / 0.916 | 0.913 @10, 0.910 @20 | 4.00 |
| memristive | 0.856 / 0.894 / **0.911** | 0.893 / 0.911 / **0.915** | **0.9097 @20** | **2.00** |
| ternary | 0.801 / **0.835** / 0.728 | 0.821 / **0.835** / 0.796 | 0.861 @10 | **0.25** |
| digital backprop (learning control) | — | — | **0.9234** | 4.00 |

**Verdict: promote the memristive arm to D2.** At settle 20 the memristive arm
reads **0.9097** against the digital rule's **0.9097** on the confirmation seed
(0.05 pp), at **2 B/weight against 4 B/weight**. The parity margin was
pre-registered at 1 pp on both seeds, and the ladder and confirmation seeds
agree. The best settle is the ladder's upper edge, so D2 includes an extension.

**One refusal at this box.** Ternary reaches 0.835 at settle 10 / LR 3e-3 and
0.861 on the confirmation seed, **5.2 pp below** the digital rule's 0.913. At
2 bits/weight (16x less state) it does not buy parity at width 32. The refusal
keeps its knob box, its trigger (a wider hidden layer or a learnable alpha per
layer), and its re-open command (the cell log with that box).

**Two apparatus corrections.** A shared LR is not a fair box: at 1e-2 ternary
reads 0.381 while digital/memristive read 0.909/0.905, so each arm gets its own
LR viability ladder (CORRECTION 17). A frozen-alpha probe rejected itself: the
cell moves by at most 7 pp at 1e-2 and under 0.5 pp where it is alive, so the
moving scale was not the degradation's mechanism and no code fix was applied.

Command: `uv run python -m computronium.validation.substrate_ladder --device
cpu`; replay from the cell log without training: `... --replay`. The table is
`results/t93_d1/substrate.md`.

### 2.10 The depth rung (T6c) — refused at its box

**Question.** Does the depth-stable pass leave the L=32 plateau and reach the
L=8 floor at one box? The cheap pass is `GeometryConfig.feedforward(
stream_norm=True)`: Hinton's unit-scale stream (length sqrt(width) per
post-activation), no parameters and no new primitive. The floor is the learning
control's (`checkpointed L=8 − 1 pp`), never a second number. Box: CIFAR-10
10k-image train subset / full 10k test, **W=512, B=2048, 200 steps**,
`backprop` + `EuclideanUpdate`, ladder seed 21, confirmation seed 23.

| cell | depth | pass | LR | val_acc | activations MB |
|---|---|---|---|---|---|
| plain | 8 | off | 0.3 | 0.385 | 157 |
| plain | 32 | off | 0.3 | **0.100** | 565 |
| normalized (shallow) | 8 | on | 3e-2 | 0.376 | 217 |
| normalized | 32 | on | 3e-3 | 0.253 | 817 |
| normalized | 32 | on | 1e-2 | 0.290 | 817 |
| normalized | 32 | on | **3e-2** | **0.314** | 817 |
| confirmation (seed 23) | 32 | on | 3e-2 | **0.326** | 817 |

Floor 0.375. **Edge extension:** at LR 1e-1 the claim depth reads **0.100**
(L=8 0.390), so the best point is interior at 3e-2 — the ladder's upper edge is
taken and refused, not truncated. **Step extension (3x):** at 600 steps the
normalized claim depth reads **0.360** against its own shallow cell's 0.392,
still 3.2 pp below the L=8 value.

**Verdict: refuse the cheap pass at this box.** It leaves the plateau on both
seeds (0.100 → 0.314/0.326), but it misses the floor by 5.9 pp and 4.9 pp, and
it costs **1.45x** the plain activation set (c ~ 6.2 against 4.1) — at the claim
point (W=1024/B=8192) that is 6281 MB of 6554 MB budget. The refusal keeps the
knob box (LR 3e-3/1e-2/3e-2, 200 steps), the reversal trigger (**LayerNorm,
which sets c ~ 2 and requires the appendix recomputed in the same commit**, or
the Innocenti depth-scaled init on a residual geometry), and the re-open command
`uv run python -m computronium.validation.memory_frontier --rung --depth 32
--width 512 --batch 2048 --steps 200`.

**The claim-point rows** (W=1024, B=8192, 200 steps, seed 11), for the claim
ladder's admission check:

| cell | depth | pass | LR | val_acc | activations MB |
|---|---|---|---|---|---|
| plain | 8 | off | 0.3 | 0.419 | 1061 |
| plain | 32 | off | 0.3 | 0.100 | 4229 |
| normalized | 8 | on | 3e-3 / 1e-2 / 3e-2 | 0.411 / 0.411 / 0.406 | 1602 |
| normalized | 32 | on | 3e-3 / 1e-2 / 3e-2 | 0.315 / 0.336 / **0.341** | 6281 |

The Innocenti pre-screen (residual, W=512/B=2048, 200 steps, seed 11) reads
0.446/0.434 at L=8/L=32 at LR 0.1 — 1.2 pp below its own shallow floor, so
that trigger's first cell is the same point at 400 steps, not a verdict.

**The B=4096 pass (2026-11-17).** The re-registration's ladder at
L=32/W=512/B=4096/`stream_norm` reads **0.364** for the checkpointed arm at
LR 3e-2 (seed 21; 0.357 on the confirmation seed), so the pass carries the
depth to within 1.1 pp of the old floor (0.375). The plain L=32 cell still
reads 0.100 at B=2048. T6c's LayerNorm re-open is therefore a side track:
it can close the stack's last pp, not the hybrid's 17 pp accuracy gap
(§2.14).

### 2.11 The matched substrate comparison (D2)

**Question.** Does D1's saving survive a matched-budget comparison? The memory
arm runs the same rule and architecture against the digital rule at matched
settle compute (the parity reference), against digital backprop at the same
budget (the learning control: it establishes learnability, not parity), and
against the int8 quantise-dequantise control (the same width, no device model:
it prices the representation, so a parity claim can name the constraint that
binds). The box is MNIST quick mode at **2x** D1's width, 784-64-10, batch 32,
600 batches, one epoch, beta 0.5, full 10k test split (1 sigma = 0.3 pp), CPU;
the LR is frozen from D1 at 1e-2, and the settle ladder is 20/40 (D1's best
point sat on the upper edge).

**The settle screen.** At 2x width the memristive arm reads 0.9259 / 0.9276 at
settle 20/40 (seed 57) and 0.9245 / 0.9240 (seed 58): +0.17 and -0.05 pp,
below the 0.5 pp adoption margin, so the matched box stays at settle 20.

**The paired row** (5 paired seeds, settle 20, LR 1e-2; 24 cells, 915 s):

| seed | digital rule | memristive | gap | QDQ control | QDQ gap | backprop | walltime | fwd | device B/weight |
|---|---|---|---|---|---|---|---|---|---|
| 71 | 0.9280 | 0.9237 | -0.43 pp | 0.9278 | -0.02 pp | 0.9367 | 2.18x | 1.00x | 2 vs 4 |
| 72 | 0.9277 | 0.9253 | -0.24 pp | 0.9275 | -0.02 pp | 0.9351 | 2.21x | 1.00x | 2 vs 4 |
| 73 | 0.9322 | 0.9293 | -0.29 pp | 0.9303 | -0.19 pp | 0.9277 | 1.35x | 1.00x | 2 vs 4 |
| 74 | 0.9258 | 0.9224 | -0.34 pp | 0.9263 | +0.05 pp | 0.9377 | 2.26x | 1.00x | 2 vs 4 |
| 75 | 0.9298 | 0.9272 | -0.26 pp | 0.9310 | +0.12 pp | 0.9376 | 2.44x | 1.00x | 2 vs 4 |

**Verdict: refuse the substrate path at this box.** The paired gap is **-0.31
pp, paired 95% interval [-0.41, -0.22]**, so accuracy parity holds; but the
memory arm costs **2.09x** the digital rule's walltime at matched settle
compute (limit 1.2x; 4/5 seeds over the line), with forward-equivalents
**1.00x** — the extra cost is the differential pair's conductance programming
on every forward and update, not extra passes. The QDQ control reads **-0.01
pp**, so the int8 width is harmless and a parity claim cannot be attributed to
it. The measured mechanism is therefore the **programming budget** (host-side
conductance programming), not the conductance levels and not drift. D3 does not
fire: its trigger is parity at matched walltime. The re-open is a device-level
or compiled quantisation of the pair, not another seed.

The learning control reads 0.9367 / 0.9351 / 0.9277 / 0.9377 / 0.9376, far
above the 0.55 floor, so the box is learnable.

**One apparatus correction.** `QuantizedSubstrate` claimed int8 precision, but
its forward cast operands to int8 and never quantised the weights. It now uses
the float forward with asymmetric per-tensor int8 QDQ (256 levels) and a
straight-through gradient, so the control prices the representation;
`DEVICE_BITS` gains `qdq = 8` bits/weight plus one fp32 scale per tensor.
`_build_system`/`_box` take `hidden_dims`, so the 2x box needed no second
runner.

Command: `uv run python -m computronium.validation.matched_substrate --device
cpu`; replay from the cell log without training: `... --replay --device cpu`.
The table is `results/t93_d2/matched.md`; the cells are
`results/t93_d2/matched.cells.jsonl`.

### 2.12 The composition screen (F1)

**Question.** Does any legal 6-axis composition beat the best single-axis
default by δ at matched forward-equivalents? The 6-axis generator and its
legality filter already exist; the screen is one cheap task, 50 legal multi-axis
cells drawn uniformly, with **every legal single-axis arm** as the reference, and
a 2/4/6-width family ladder on the best credit family. A composition cannot be
its own bar, and the reference's second seed plus the ladder's confirmation seed
price the seed spread.

**The box.** `digits` quick mode (1797x64, 10 classes), batch 32, 57 batches
(one epoch, so 57 forward-equivalents per cell), 1 seed, CPU, 50k parameter
ceiling. δ = 1 pp, floor 0.55, and the control band is 10 pp (the pilot
measured a 6.9 pp data-order swing before the run).

**The reference** (41 legal single-axis arms; `plasticity:
conflict_adaptive` refused training and is recorded):

| axis | primitive | val acc | walltime |
|---|---|---|---|
| update | ortho_adam | **0.797** | 1.7 s |
| geometry | attention | 0.792 | 0.9 s |
| geometry | tile_mesh | 0.769 | 0.5 s |
| update | muon | 0.764 | 1.6 s |
| geometry | nca | 0.678 | 0.2 s |
| default | digital MLP | 0.194 | 1.3 s |

The learning control (untuned default at 1e-2) reads 0.194 at this box; the
reference's second seed reads **0.867** (drift 6.9 pp, inside the band).

**The 50 legal compositions** (seeded reservoir; 50/50 measured, no refusals):

| substrate | geometry | dynamics | plasticity | credit | update | width | val acc |
|---|---|---|---|---|---|---|---|
| digital | tile_mesh | instantaneous | temporal_psi | random_projections | riemannian_orthogonal | 4 | **0.669** |
| ternary | conv | instantaneous | temporal_psi | gradient | muon | 4 | 0.481 |
| digital | tile_mesh | instantaneous | null | random_projections | lion | 3 | 0.328 |
| analog | tile | instantaneous | conflict_adaptive | random_projections | local_adam | 5 | 0.306 |
| analog | tile_mesh | instantaneous | routing | gradient | role_split | 4 | 0.269 |
| memristive | feedforward | lazy | temporal_psi | local_contrastive | lion | 5 | 0.189 |

**The family ladder** (credit families, selected by median with n >= 2; the best
is `random_projections`):

| seed | width | val acc | note |
|---|---|---|---|
| 42 | 2 | 0.092 | the width-2 point is near the single-axis level |
| 42 | 4 | 0.783 | the screen seed's ladder best |
| 42 | 6 | refused | `tile_mesh + energy_minimization + random_projections + riemannian_orthogonal + analog + temporal_psi` failed to train |
| 43 | 4 | 0.814 | the confirmation seed; a **3.1 pp** spread from the screen seed |

**Verdict: refuse composition at this box.** The bar is 0.797 + 1 pp = **0.807**.
The screen's best composition reads 0.669 (12.8 pp below the single-axis
default), and the family ladder's best reads 0.783 (1.4 pp below the bar) on the
screen seed. The confirmation seed reads 0.814 (+1.7 pp above the bar), but its
3.1 pp spread from the screen seed is **wider than δ**, so the point did not
reproduce. The seed spread, not the composition, is the binding ruler; F2's five
seeds at the same box are the trigger. Verdict "composition is false" is not
available from one seed. Re-open: F2 (five seeds), a matched-parameter
composition, or a real task family (MNIST/CIFAR, wider axes).

Command: `uv run python -m computronium.validation.composition_ladder --device
cpu`; replay from the cell log without training: `... --replay`. The table is
`results/t93_f1/composition.md`; the cells are
`results/t93_f1/composition.cells.jsonl`; the registration written before the
first cell is `configs/preregistrations/t93_composition_registered.json` (the
21:54 copy preceded the first cell log at 22:12 by 17 minutes). Runtime: 96
cells, about 19 min on CPU (the seeded generator examined 2,000 candidates in
18 s and yielded 321 legal composable cells).

### 2.13 The memory-frontier registration (T6a) — `invalid-box`

**Question.** At one point, does the hybrid reach accuracy within δ of the
checkpointed arm at ≤0.5× its activation bytes? The registration priced 30
claim cells at L=4→8 (W=512/B=2048) because the 4.5 GiB L=32 pilot exceeded
the card, and its rung-2 screen then refused the claim there.

**The triage (2026-11-17).** Two registration defects make that refusal an
`invalid-box`, not a verdict (CORRECTIONS 19–20). Same geometry, only depth or
batch moves, seed 21, four steps:

| depth | batch | hybrid act MB | ckpt act MB | ratio |
|---|---|---|---|---|
| 8 | 2048 | 103.2 | 84.6 | **1.22×** |
| 16 | 2048 | 111.2 | 148.6 | 0.75× |
| 32 | 2048 | 127.2 | 240.6 | 0.53× |
| 8 | 4096 | 186.2 | 149.0 | 1.25× |
| 16 | 4096 | 194.2 | 269.0 | 0.72× |
| 32 | 4096 | 210.2 | 437.0 | **0.48×** |

The checkpointed arm's saving grows with √L, so the ratio crosses 0.5 between
L=16 and L=32. T6b's lock states it at L=32 (0.48×); the registration read it
at L=4→8 — the guard's box, not the claim's.

**The other half is empty.** At 200 steps and LR 0.3 the plain stack trains
only at L=8 (0.385); at L=16 and L=32 **every** arm reads 0.100 (chance, 10
classes) on seeds 21 and 22 at both batches. The memory ratio needs L≈24–32, so
the registered claim has no point where both conditions hold. The shelf that
does train a deep arm is T6c's stream-norm pass (3e-2 → 0.314/0.326 at L=32).

**Verdict: `invalid-box`.** The refusal stands only at L=4→8, where the claim
was never stated. The track is not refused: it re-registers at a pass-carrying
box (L=32, `stream_norm=True` at 3e-2, W=512/B=2048 → ~1.6 GB, fits) or states
the ratio curve as the claim with accuracy read at L=8.

**Open update suspicion, with a test.** The hybrid never moves a bias (eight
bias tensors, 60 steps, movement exactly 0.0) and its trunk movement decays
~6× per layer (0.33 → 0.016 → 0.0026 → 4e-4 → 2e-4 → 5e-5). Its accuracy is
**box-insensitive and low**: 0.164 (W=64/B=128), 0.167 (W=512/B=2048), 0.163
(W=1024/B=8192, §2.4's ladder), while its parts read 0.215-0.419 (backprop) and
0.393-0.400 (local) — the earlier "0.419 at the pilot box" was the *backprop*
control's cell, not the hybrid's (CORRECTION 23). The suspicion is the level gap:
the composition reads ~0.16 at every box while both parts read above it. A test
compares `train_biases=True`, `feedback_scale`, and a head-only control at the
pilot box; a mechanism that moves the hybrid within δ names the defect.

Probes: `scripts/probes/t93_t6c_hybrid_triage.py` (12 cells, W=64/512),
`scripts/probes/t93_t6a_box_triage.py` (6 cells, L=16). Runtime ~90 s each,
peaks 13–597 MB.

### 2.14 The memory-frontier re-registration (T6a₂) — refused at its box

**Question.** At the **pass-carrying** box — L=8→32, W=512/B=4096, the
stream-normalized pass at the frozen per-arm LR, 200 steps — does the hybrid
reach the checkpointed arm's accuracy within δ at ≤0.5× its activation bytes?
The first registration priced L=4→8 because the 4.5 GiB pilot exceeded the
card; its ratio measured the OOM guard's box (1.22×), while the claim's ratio
is depth-declared (0.48× at L=32/B=4096; CORRECTION 21).

**Box (registered before the first claim seed).** CIFAR-10 fixed 10k-image
train subset / full 10k test, L=8→32 at W=512/B=4096, `stream_norm=True`, 200
steps (100 epochs × 2 batches), fp32, seed 21 + confirmation 22; claim seeds
101-105, ladder seeds 21-23, pilot seeds 11-13, data-order seed 7. One
registration run, 21 cells, ~300 s (one probe at the box: 14.0 s/cell, seed 99,
0.183 val_acc, 210 MB activations, 282 MB peak).

**Controls pass.** The instrument control reads **c = 4.125**, spread 0.0 %
(depths 4/8/16, B=4096); the learning control at L=8/B=4096, plain pass,
LR 0.3 reads **0.409** against floor 0.399 (both arms), and the
`LEARNING_FLOOR = 0.25` now bars a chance-level control (CORRECTION 22).

**Ladder at L=32 (200 steps, seed 21).**

| Arm | LR 3e-3 | LR 1e-2 | LR 3e-2 |
|---|---|---|---|
| `backprop` | 0.285 | 0.308 | **0.364** |
| `backprop+ckpt` | 0.285 | 0.308 | **0.364** |
| `hybrid` | 0.182 | **0.184** | 0.171 |
| `local` (PEPITA) | 0.289 | 0.324 | **0.354** |

The best point is the upper edge for every arm except the hybrid, whose best
is the interior point (LR 1e-2); the frozen LR is per arm.

**Screen (best LR per arm, seeds 21 / 22).**

| Arm | val_acc | Activations MB | Peak MB | Fwd-eq | Walltime s |
|---|---|---|---|---|---|
| `hybrid` | 0.184 / 0.201 | 210.2 | 282.3 | 7.56 / 9.02 | 13.4 / 16.1 |
| `backprop+ckpt` | 0.364 / 0.357 | 452.7 | 524.8 | 4.13 / 12.83 | 18.1 / 22.7 |

The activation ratio is **0.46×** on both seeds (the 0.5× bar is met); the
accuracy floor is the checkpointed arm's minus δ (0.354), and the hybrid is
**17 pp below** on both seeds. `verdict = refuse`: this is not `invalid-box` —
the pass trains (0.364, 2.9× chance), the memory bar is met, and the accuracy
gap is the hybrid's own update. At L=8 the same arm reads 0.163 (plain) and
0.167 (W=512/B=2048) while its parts read 0.39-0.42; at L=32 it reads
0.184-0.201 while the parts read 0.354-0.364. So the composition reads below
both parts at every measured box (CORRECTION 23).

**Trigger.** T6d — the hybrid's update diagnostic at the pilot box
(L=8/W=1024/B=8192, LR 0.3): `train_biases`, `feedback_scale`, and a head-only
control; a mechanism that moves the hybrid within δ names the defect. It has
landed and refused (§2.15): no trunk knob reaches the floor, and the same
trunk rule as a whole stack reads 0.405, so the split is the mechanism. T6c's
LayerNorm re-open is a side track: the stack's pass is 1.1 pp below the old
0.375 floor, not the 17 pp hybrid gap. No claim run is scheduled (30 priced
cells, none measured).

Artifacts: `results/t93_a_stream/memory_frontier.registered.{json,md}`;
committed `configs/preregistrations/t93_memory_frontier_stream_registered.json`;
replay `uv run python -m computronium.validation.memory_frontier --re-register`.

### 2.15 The hybrid's update diagnostic (T6d) — refused; the split is the mechanism

**Question.** At the pilot box — L=8, W=1024, B=8192, LR 0.3, 200 steps — which
part of the hybrid's composed update binds the 17 pp gap T6a₂ refused: the
trunk's bias path (`train_biases`), the trunk's modulation scale
(`feedback_scale`), or the head's exact-gradient split?

**Box.** CIFAR-10 fixed 10k-image train subset / full 10k test, L=8/W=1024/B=8192,
200 steps (100 epochs × 2 batches), LR 0.3, fp32, seed 21 and confirmation 22,
data-order seed 7. Twelve measured cells (14 planned), ~200 s (10-15 s/cell; 516-1037 MB peak) on
the RTX 3080 10 GiB. Reference `backprop+ckpt`; sibling `local` — the same
trunk rule as a whole stack, with no head.

**Measured (seed 21 / 22 unless a ladder point).**

| Arm | gamma | train biases | val_acc | activations MB | peak MB | s |
|---|---|---|---|---|---|---|
| `backprop+ckpt` | — | — | **0.419 / 0.416** | 485 | 557 | 11.3 |
| `hybrid` | 0.05 | no | 0.163 / 0.169 | 516 | 589 | 10.2 / 10.3 |
| `hybrid` | 0.05 | **yes** | **0.167 / 0.175** | 516 | 589 | 10.4 / 10.5 |
| `hybrid` | 0.3 | no | **0.100** | 516 | 589 | 10.3 |
| `hybrid` | 1.0 | no | **0.100** | 516 | 589 | 10.4 |
| `hybrid` (head-only) | 0 | no | **0.149** | 516 | 589 | 10.4 |
| `local` (sibling) | 0.05 | no | **0.400** | 965 | 1037 | 15.1 |
| `local` (sibling) | 0.3 | no | **0.405** | 965 | 1037 | 15.1 |
| `local` (sibling) | 1.0 | no | **0.384** | 965 | 1037 | 15.2 |

The reference trains, so the floor is **0.408** (0.418 − 1 pp). The baseline
repeats T6a₂'s level (0.163 / 0.169). **No trunk knob reaches the floor**:
the bias flag adds **+0.5 pp** (the only gain the grid shows); the
`feedback_scale` ladder peaks at the registered scale and **collapses to
chance** (0.100, 10 classes) at 0.3 and 1.0; head-only (gamma=0, zero trunk
contrast, so only the head trains) reads **0.149**.

**The sibling control names the mechanism.** The same trunk rule as a whole
stack (`local`) reads 0.400 / 0.405 / 0.384 — within 1.5 pp of the reference
and **24 pp above the hybrid** — and it does not collapse where the hybrid
does. So the gap is the **split at the boundary** (a 2-layer exact-gradient
head over a slowly trained trunk), not the trunk's rule, its bias path, or its
scale. **CORRECTION 24.**

**The memory half does not hold at this box.** The hybrid's activation set is
516 MB against the checkpointed arm's 485 MB (**1.06×**), so L=8 is an accuracy
diagnostic box; the bar is met at L=32 under the stream-normalized pass
(0.46×, §2.14). The pilot box cannot decide the memory claim.

**Trigger.** T6e — the split's position at the pilot box: `split_layer` on the
last Linear (a readout-only head: 7 trunk layers + 1 exact-gradient layer) at
gamma 0.05, then a decoupled trunk learning rate (gamma × lr as one box). No
claim run is scheduled (12 measured cells (14 planned), no claim cell).

Artifacts: `results/t93_a_stream/hybrid_update.{json,md}` plus the kill-safe
cell log `hybrid_update.cells.jsonl`; replay
`uv run python -m computronium.validation.hybrid_update --replay`.

## 3. Open locks

| Lock | Test | Cost |
|---|---|---|
| No fabricated activation measurement | `tests/property/test_kernel_truth_lock.py` | 9 s |
| Stub detector (nudged ≠ free) | `tests/property/test_kernel_truth_lock.py` | 9 s |
| Decomposition sums to peak; measured c | `tests/property/test_memory_binding.py` | 10 s (CUDA) |
| Every credit row declares its estimator coordinate | `tests/property/test_estimator_lock.py` | 9 s |
| Estimator atlas: six declared coordinates, lite/full, control/refusal verdicts | `tests/unit/validation/test_estimator_atlas.py` | 9 s |
| Kill-safe atlas cell log: resume/replay and dedup | `tests/unit/validation/test_estimator_atlas.py` | 1 s |
| Lockstep ≡ store-all, per layer, `atol=0`; peak flat in depth | `tests/property/test_lockstep_parity.py` | 9 s (4 s CUDA) |
| Substrate device state is a declared width (2/16/32 bits/weight), not a zero | `tests/unit/validation/test_substrate_ladder.py` | 10 s |
| D1 gate: two-seed parity with less state promotes; one seed below refuses; chance control invalidates | `tests/unit/validation/test_substrate_ladder.py` | 1 s |
| Kill-safe substrate cell log: resume/replay and dedup | `tests/unit/validation/test_substrate_ladder.py` | 1 s |
| D2 gate: paired interval, cost ruler, QDQ width, extension screen, replay | `tests/unit/validation/test_matched_substrate.py` | 10 s |
| F1 gate: screen/ladder/confirmation, invalid reference/control, median family, 2/4/6 width ladder | `tests/unit/validation/test_composition_ladder.py` | 14 s |
| T6d gate: floor from the reference, ladder confirmation, sibling/composition, head-only refusals, kill-safe cell log | `tests/unit/validation/test_hybrid_update.py` | 9 s |
| Kill-safe composition cell log: replay recomputes the gate; registration precedes the first cell | `tests/unit/validation/test_composition_ladder.py` | 1 s |
| QDQ control quantises (256 levels, float forward, STE) and is not a cast | `tests/unit/validation/test_matched_substrate.py` | 5 s |
| Hybrid trunk ≡ store-all hybrid `atol=1e-7`; head ≡ backprop; peak flat | `tests/property/test_hybrid_parity.py` | 16 s (2 s CUDA) |
| Pilot point: measured c, binding gate, ckpt ≤ 0.5× activations | `tests/property/test_memory_frontier.py` | 20 s (CUDA) |
| **Hybrid ≤ 0.5× ckpt activations on the composed path (T6b, xfail)** | `tests/property/test_memory_frontier.py` | 20 s (CUDA) |
| T6a box: the ratio is depth-declared (1.22 / 0.75 / 0.53 at L=8/16/32) and the claim's two bars never meet | `scripts/probes/t93_t6a_box_triage.py` | 90 s (CUDA, ~600 MB) |
| Re-registration box: its own rung/path/ratio; a 0.53× box refuses itself; a chance-level control fails | `tests/unit/validation/test_memory_frontier_registration.py` | 14 s |
| Hybrid update: biases move, trunk contrast does not decay 6× per layer | `scripts/probes/t93_t6c_hybrid_triage.py` | 90 s (CUDA, ~600 MB) |
| Batch-1 plasticity ladder gate (C1) | `tests/unit/validation/test_plasticity_ladder.py` | 9 s |
| C2 retention gate: floor on two seeds, matched per-step cost, forgetting δ, saturation | `tests/unit/validation/test_plasticity_ladder.py` | 12 s |
| Task start anchors EWC without erasing the Fisher importance | `tests/unit/core/test_cl_credit_arms.py` | 14 s |
| STE gradient differs from its soft reference on a seeded fixture | `tests/unit/validation/test_routing_ladder.py` | 2 s |
| The smoothed reference tracks its own finite difference | `tests/unit/validation/test_routing_ladder.py` | 2 s |
| B1 routing gate: growth on two seeds promotes; flat refuses; chance invalidates | `tests/unit/validation/test_routing_ladder.py` | 1 s |
| Kill-safe routing cell log: resume reuses cells; replay recomputes the gate | `tests/unit/validation/test_routing_ladder.py` | 1 s |
| Kill-safe cell log: resume reuses measured cells; replay recomputes the gate | `tests/unit/validation/test_plasticity_ladder.py` | 12 s |
| Credit label channel carries the task offset | `tests/unit/core/test_cl_credit_arms.py` | 10 s |
| Data order is seeded independently of model RNG | `tests/unit/core/test_cl_credit_arms.py` | 9 s |
| `CLConfig.lr` reaches every arm's update | `tests/unit/core/test_cl_credit_arms.py` | 9 s |
