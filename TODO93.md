# TODO93 — Local learning that wins on the hardware people own
**Status:** 2026-11-16 · **v10 — T1 + T4a + T4c + T4b + T3 + T3b landed, T6 next.** The
truth pass, the memory decomposition, the ladder runner, the checkpointed
baseline, the lockstep two-pass rung, and the hybrid (lockstep-local trunk +
exact-gradient head) are implemented and locked; the measured activation
coefficient is **c≈4.1, not 1**, which re-poses the pilot's binding point (§4.1),
the lockstep is measured **flat in depth** (66.3 MB FF, 58.5 MB PEPITA at
L=4→32, W=512, B=4096), and the hybrid trunk is **flat at 81.0 MB above the
weight-gradient set** with the store-all control bending 122→1018 MB. v1
(composition-wide search, substrate inversion) is condensed into §12 as a
**deferred track with triggers**; v2's premise was corrected in v3; v4 added the
estimator taxonomy and the ticket-bound primitive queue (§19); v5 verified the
plan against the claim path; v6 fixed the binding arithmetic (B1–B6, §20); v7
replaced the assumed arithmetic with the measured one; v8 landed the recovered
arm the pilot compares against; v9 landed the local arm's memory rung and killed
three defects that made both two-pass steps unrunnable; **v10 composes that
rung with an exact-gradient head and locks the composition against the
store-all hybrid at bit-exactness.**
**Successor to TODO92** (closed: 12 claim-grade rows, breadth gate 8/8, parity on
two families, 0 capability wins).
**The pivot.** TODO92 competed with backprop on backprop's home turf: accuracy at
matched parameters on tasks backprop was built for. That contest has a known
outcome and produced 12 uninformative rows. This plan competes on the axes where
local learning is **structurally** advantaged and users actually feel the cost:
activation memory, streaming, non-differentiable computation, depth at fixed
budget — **on digital hardware**, where the compute is.
**The claim we are trying to earn:** a practitioner with a consumer GPU can
train something a *composition* of local and global credit makes possible at
matched memory and matched compute, with a reproducible command.
**The amendment that governs the whole plan.** A contest posed where the
structural advantage cannot bind is as uninformative as one posed where it cannot
lose. That is TODO92's lesson, and the mirror image of it is the failure mode of
every lift-vs-backprop comparison: at width 512, depth ≤64, batch 1k, activations
are ~134 MB next to ~200 MB of params and Adam state, so both arms fit and the
"memory" claim is vacuous. **No cell counts as evidence unless the baseline arm's
activations are ≥50% of its peak memory** (§9 binding gate).
**Execution surface:** §0 (what), §8 (order), §16 (handoff). §1–§7 and §9–§20
are the contract those tickets must satisfy; read them when writing the test, not
when scheduling the work.
---
## 0. Start here
**Three minimum publishable units (MPUs), in order of expected value per session.**
| MPU | Question | Why it is publishable | First evidence |
|---|---|---|---|
| **MPU1 — memory frontier** | On the accuracy-per-GB frontier at iso-walltime, does a *composition* (lockstep-local trunk + small backprop head) dominate `backprop+checkpointing`, and does a pure-local arm reach greater depth at fixed memory? | Practitioners are memory-bound; the contribution is a measured, matched frontier and its decomposition, not virgin territory (InfoPro, TinyFoA, DGL, greedy layerwise already occupy parts) | peak-memory instrument + binding gate + depth/width/batch ladder |
| **MPU2 — non-differentiable architecture** | Does local credit beat the *best backprop-compatible estimator* (STE + load-balancing/z-loss) on hard top-k routing, with the estimator's bias measured against a defined reference? | A capability backprop can only approximate, positioned against the STE and MoE literature | one-epoch STE-gap screen, then one matched pair |
| **MPU3 — streaming** | On batch-1, non-stationary data, does local×consolidation retain more at matched memory than backprop×consolidation ± small replay? | On-device training, edge, privacy-preserving adaptation | plasticity probe, then stream protocol |
**Progress (2026-11-16 — T1, T4a, T4c, T4b, T3, T3b).** Every row is a runnable
check, not a claim, and each fails when its mechanism is removed.

| Ticket | Landed | Lock | Consequence |
|---|---|---|---|
| T1 | `complexity_verified` + `available`/`unavailable_reason` on every kernel backend; `activations_mb=None` at all 14 fabricated-zero sites; PEPITA contrastive nudge rebuilt (two-forward error modulation); FF/SNN contrastive marked unavailable with triggers; `estimator_kind`/`bias_reference` declared on all 10 credit rows via their identity cards | `test_kernel_truth_lock.py` (28), `test_estimator_lock.py` (21) | no memory claim can rest on a self-reported zero; a stub kernel cannot be routed to (`KernelRegistry.get` refuses it); W3's taxonomy is declared, not inferred |
| T4a | `EpochResource` decomposition (params / optimizer / activations / auxiliary / RSS) + `activation_share` + `binding_verdict`; emitted per cell beside `memory_usage` | `test_memory_binding.py` (6, CUDA) | the decomposition sums to the peak; the gate rejects a non-binding cell; **measured c = 4.1** |
| T4c | `run_parity(batch_size=...)` threaded to the driver and the baseline; `pepita` family in the ladder portfolio; **fixed a live defect: `backprop_baseline` referenced a `batch_size` it did not have, so every campaign raised `NameError`** | `test_backprop_parity_runner.py` (2) | one runner for the ladder; 2 cells in 4.9 s |
| T4b | `core/gradient_checkpointing.py` + `FeedforwardGeometry.set_gradient_checkpointing`: √L segments split at Linear starts, `use_reentrant=False`, `preserve_rng_state=True`, geometry forward wrapped (never `train_step`); `create_backprop_mlp(checkpoint_segments=...)` is the arm | `test_checkpoint_parity.py` (7) | checkpointed grads ≡ plain under dropout (bit-exact), RNG-preservation is a negative control, retained set is segment boundaries; **epoch peak 3894 MB < 6554 MB at L=64/W=1024/B=8192** (§4.1) |
| T3 | one `lockstep_contrasts` stream serves both families (FF contrasts positive/negative, PEPITA standard/error-modulated — same expression); `train_step` + `kernel_train_step` run it; store-all `forward_*`/`backward` stay as the reference rung; `complexity_verified=True` for FF and PEPITA | `test_lockstep_parity.py` (8, 4 CUDA) | deltas ≡ store-all at `atol=0` per layer; **peak flat 66.3 MB (FF) / 58.5 MB (PEPITA) at L=4→32** vs 576/568 MB retained; **three live defects fixed**: FF `train_step` called a nonexistent `backward_contrastive`, PEPITA `backward` required an `error` argument no caller passed, and the bespoke PEPITA step used the standard pre-activation for both chains (the Triton twin's tested equation uses each chain's own) |

| T3b | `HybridCredit` in `ontology/credit/_hybrid.py`: `PepitaTrunk` contrast + `GradientCredit.gradient_of` head; `step_layer` threads the residual input across one layer; `split_layer` must land on a Linear; one registry row (`estimator_kind="hybrid"`) and feedforward-geometry refusal | `test_hybrid_parity.py` (8, 2 CUDA) | trunk deltas ≡ store-all hybrid **max\|Δ\| = 0.0**; head ≡ plain backprop; **trunk peak flat 81.0 MB above gradients at L=4→32** vs store-all 122→1018 MB; composed `train_step` decreases loss and moves every weight |

**Next:** **T6 + T6a** (pilot then pre-registration) — the hybrid is the lead
arm and its trunk half is measured flat, so the frontier's matched comparison is
now the only missing piece. T5 (published parity) and the P3 screen can run in
parallel; both need no new primitive.

**The credibility gate comes first (P1).** A low number from a weak implementation
is a defect, not a verdict. Before any claim, each credit we intend to publish
must reproduce its *published* number at the published architecture within
tolerance. P1 is also where the claimed-vs-measured complexity audit lands,
because the audit is what makes the memory thesis checkable at all.
**What changed from v2 and why**
| v2 | v3 | Reason |
|---|---|---|
| §1 cited `contrastive_kernels.py` as the "no stored activations" family | §1 states the measured truth: two full activation passes; only layer-sequential rules are O(1) | the cited file holds `free_acts` + `nudged_acts` and hardcodes `activations_mb: 0.0` |
| lead arm = "the best local rule from P1" | lead arm = hybrid (lockstep-local trunk + 2–4 layer backprop head); pure local is the control | arm selection by accuracy confounds credit quality with memory; the frontier is *within* the local family |
| W2 = "2× depth" | W2 = 2× depth **with an accuracy floor** | depth without learning is gameable |
| W4 vs backprop+replay at matched memory | W4 vs backprop+online EWC/SI ± small replay; plasticity first | batch-1 replay is cheap; forgetting is weight interference, not credit routing |
| "nobody publishes memory-matched comparisons" | deleted; position against InfoPro, TinyFoA, DGL, greedy layerwise | false as written |
| T0/D1 on the critical path | deferred §12; manual `regime` tag now | the search is deferred; the MPUs are targeted and need no proposal bias |
| no primitive admissions | §19 admits only ticket-blocking mechanisms; `estimator_kind` gives the C axis an estimator coordinate | W3 is a bias/variance question, not "local vs weak STE" |
| headline "2× depth at equal walltime" | headline = accuracy per GB at iso-walltime (Pareto) | see §2 |
---
## 1. The scarce-resource thesis (corrected)
**Measured fact (was wrong in v2).** Backprop stores per-layer activations:
O(L·B·W). Local rules as *implemented* store two full activation lists — the free
and nudged passes — so their peak is ≈2× a forward pass, not O(1):

| Path | Declared | What the code holds | Verdict |
|---|---|---|---|
| `acceleration/contrastive_kernels.py` `contrastive_step` (:208–210) | `memory_complexity="O(1)"` (:77), `activations_mb=0.0` (:235) | `free_acts` **and** `nudged_acts`, full per-layer lists | claim false; ≈2× forward |
| `acceleration/ff_kernels.py` `FFKernelBackend` (:90–94) | O(1) (:42), 0.0 (:240) | `pos_acts` + `neg_acts` | claim false |
| `acceleration/ff_kernels.py` `PEPITAKernelBackend` (:373–384) | O(1) (:321), 0.0 (:576) | `std_acts` + `err_acts`; two forwards | claim false; 2 forwards is PEPITA's published design |
| `acceleration/backprop_kernels.py` (:50) | O(L) | O(L) | complexity honest, counter still hardcoded 0.0 (:181) |
| `acceleration/hebbian_kernels.py` (:38), layer-sequential FF | O(1) | one layer at a time | plausible; **must be measured, not asserted** |
| `acceleration/tp_kernels.py` (:60) | O(1) | stores inverses (≈2× params) | complexity claim wrong even where activations are flat |

Only **layer-sequential** rules (FF done properly, Hebbian, STDP) are O(1) in
depth. PEPITA as published requires two forward passes; TinyFoA states it "still
needs to store all the parameters and activations". This is a defect ticket, not
a design choice: a hardcoded `activations_mb: 0.0` is a claim that masquerades as
a measurement, and it would have poisoned every memory verdict in this plan.

**Two implementations per rule.** `algorithms/` holds the faithful
reference paths; `acceleration/*_kernels.py` holds the fused kernels. They are
different implementations with different memory behaviour, and
`contrastive_kernels.py` has `pass` where error modulation belongs
(`PEPITAContrastiveKernel.nudged_phase` :507, `SNNContrastiveKernel._simulate`
:747). Any cell routed there measures nothing. **Backend path is part of the
identity card.**

**Fact (honest, corrected).** `core/checkpoint.py` is save/resume of training
state, not gradient checkpointing. But two assumptions in v4 were wrong:
1. **Peak memory is already measured on the claim path.** `SystemTrainer`
   captures `peak_memory_mb` per epoch in `core/system_trainer/_resources.py`
   (:73, reset at :133, read at :155), `SystemTrainerConfig.track_memory` is on,
   and `_trainer_utils.py:194-207` emits it as `memory_usage` in every cell.
   What is missing is the **decomposition** (params / optimizer / activations /
   auxiliary) and CPU RSS — hours, not 1–2 sessions.
2. **Checkpointing already has a working precedent.** `torch.utils.checkpoint`
   (with `use_reentrant=False`) is used for settle steps in
   `core/local_learning/settling.py:403,446,760` and
   `ontology/dynamics/_settle_driver.py:167,186`. Backprop-activation
   checkpointing is new, but the API risk is retired.
`domains/trainer.py` `_TaskTrainer` (:237) is **not** the claim path; the claim
path is `experiment/kernel/evaluate.py` → `SystemTrainer.train_epoch`. Instrument
the shared trainer, never the domain helper.
So `backprop+checkpointing` is √L segments via `torch.utils.checkpoint`,
`preserve_rng_state=True` for dropout parity, wrapping the **geometry forward**
(not the step, which contains updates), plus the decomposition.

**Compute ruler.** Walltime is hardware-bound; **forward-equivalents** is the
portable compute unit. Backprop ≈3, backprop+ckpt(√L) ≈4, two-pass local ≈2,
lockstep local ≈3, hybrid trunk ≈3L layer-ops vs backprop's ≈4L. Local may buy
*more steps* at iso-walltime; v2 undersold this.

**Where local keeps an advantage even against checkpointing:**
1. **composition**: a local trunk stores no autograd graph; only the head does
   (approximately 4–8·B·W vs 16·B·W for √L checkpointing at L=64, head=4);
2. no batch required → batch-1 streaming has no checkpoint segment to trade;
3. non-differentiable ops need no surrogate → no bias to correct;
4. no global backward channel → shardable, asynchronous, heterogeneous.

**Where local is expected to lose, stated in advance:** accuracy per parameter on
small saturated tasks; walltime on matmul-optimised GPUs where the backward pass
is cheap; anything where the global gradient is the only signal that propagates
credit across many layers; and any comparison whose activation memory never binds.
---
## 2. The four win conditions (falsifiable, with floors)
| # | Prediction | Floor / baseline | Falsifier | If false |
|---|---|---|---|---|
| W1 | **ε-dominance (ε=1 pp):** on ≥1 task family the hybrid or local front improves hypervolume on (accuracy, peak GB) by ≥δ over `backprop+ckpt(√L)`, **or** reaches accuracy ≥ baseline −1 pp at ≤0.5× **activation bytes** (peak reported alongside; the ≤0.5× *peak* form is rejected — params+optimizer is an arm-neutral floor) | reference point fixed in T6a (`(floor−5 pp, max_peak×1.1)`); δ pre-registered; floor per task; binding gate | no arm dominates and no arm reaches the floor | memory frontier closed; the measured frontier is still the artifact |
| W2 | At fixed peak memory (8 GB), max depth at val-acc ≥ floor for local/hybrid ≥ 2× `backprop+ckpt` | floor locked before seed 1; "trainable" must mean "learns" | ratio <2, or floor not met at depth | report the measured ratio; do not claim depth |
| W3 | On hard top-k routing, the local arm beats the **best backprop-compatible estimator** (STE + load-balancing/z-loss) by ≥2 pp at matched walltime. **Bias is measured only among gradient-estimator arms; objective-local arms report update-direction alignment, not bias** | soft-relaxation gradient and/or finite-difference reference for the estimator arms; `bias_reference="none"` for objective-local; expert-choice and dense-backprop-MoE are positioning controls | STE+aux ≥ local−2 pp | negative with the measured mechanism named; no category error |
| W4 | On batch-1 streams under a pre-registered **analytic byte cap** (buffer + consolidation state ≤ cap, enforced in the GPU runner), local×consolidation **BWT** and **avg_forgetting** beat `backprop+EWC/SI` ± replay at matched per-step cost | plasticity gate first; cap and per-step cost in T6a; byte cap is a budget, not an MCU hardware claim | replay saturates BWT, or local fails plasticity | report the buffer size / cap at which replay saturates |
**Pareto-nondominated is not a claim.** A low-accuracy, low-memory point is
trivially non-dominated. W1 is **ε-dominance (ε=1 pp)** with a margin: hypervolume
gain ≥ δ against a pre-registered reference point (reuse
`experiment/analysis/pareto_analysis.py:compute_hypervolume`), or the sharper,
cheaper test — accuracy ≥ baseline −1 pp at **≤0.5× activation bytes**. The
≤0.5× *peak* form is structurally unreachable (params+optimizer is an
arm-neutral floor); do not use it. Pick one and pre-register it.
**Error control and floors.** Fix `n_max=5` paired seeds per depth before the
first run; do not peek. **Floor:** val accuracy at L=8 for the
`backprop+ckpt` arm minus 1 pp, measured on the same task, and then held fixed at
every deeper rung. The floor is set from the **pilot**, and the claim seeds are
**disjoint** from the pilot seeds; otherwise the floor is a peek. If the CI is
inconclusive at `n_max`, that is a coordinate result, not a claim. W1/W2 are
**relative** claims: the repo's absolute vision criterion (>0.95) does not govern
a flat-MLP memory ladder.
**Pre-registration essentials (T6a).** (1) a **per-arm LR viability ladder** at
L=8 — three points, one seed each, **seeds disjoint from the claim**, best point
frozen before the claim (without it, a bad LR is a defect masquerading as a
verdict); (2) fixed epochs and `batches_per_epoch` for both arms; (3) the claim
seed list and the data-order seed, disjoint from pilot and LR-ladder seeds;
(4) **both positive controls** — instrument (calibration cell reads
`c·L·B·W·4` within tol) and learning (backprop at L=8 reaches the pilot floor);
(5) δ **and** the hypervolume reference point, or the ≤0.5× **activation** rule;
(6) the binding arithmetic; (7) the **minimal claim ladder** (see §4), not the
full grid. A claim missing any of these is not registered.
**Estimator taxonomy (the reason §19 exists).** W3 is not "local vs weak STE". It
is: *which bias/variance tradeoff wins at matched compute on hard routing* —
biased-pathwise (`surrogate`), biased gradient-approximation (`gradient_approx`:
FA/DFA/TP/EqProp/PC), unbiased-score-function (`score_function`), unbiased-
pathwise (`forward_mode`), smoothed (`zeroth_order`). **Objective-local rules
(`objective_local`: FF/PEPITA/goodness; `local_supervised`: layerwise/DGL/InfoPro)
do not estimate the global gradient — they optimize a local objective.** Their
`bias_reference` is `"none"`; report **update-direction alignment** against the
reference, not bias. Measure bias/variance only among the gradient-estimator
arms. W3's accuracy comparison still includes the objective-local arm. Every
credit declares its kind, or it cannot enter the claim table.
**Metric discipline.** Every number carries: peak memory (bytes), walltime,
forward-equivalents, params, optimizer state, accuracy, σ, and the **matched**
budget. `[regime-mismatch]` marks a cell whose activation share is below the
binding gate — it is not evidence either way.
---
## 3. P1 — The credibility gate (published-parity audit, scoped)
**Decision.** Do our implementations of the credits we intend to publish reproduce
their published numbers at their published architecture and schedule?
**Why first.** A reference implementation weaker than the literature is a defect
that masquerades as a research finding. It is the cheapest session in the plan
and it protects every later claim. It is also where the complexity audit lands.
**Scope — three publishables plus the arm P2–P4 actually uses.** `pepita`,
`local_goodness`, `random_projections`, and the hybrid trunk's local rule. Do not
audit all eight; an unreferenced row is cost without a decision.
**Method, per credit:**
1. locate the published architecture, dataset, epochs, and reported accuracy;
2. reproduce at that coordinate with this repo's implementation;
3. record our number, published number, delta, σ, and the exact command;
4. **tolerance:** within ±1 pp or the published run-to-run σ, else defect.
5. **complexity audit:** measured peak activation bytes vs declared
   `memory_complexity` on a seeded 4/8/16/32 depth ladder. A class mismatch is a
   defect ticket, not a footnote.
**Deliverable.** `docs/BENCHMARKS.md` (does not exist yet): one row per
(credit, dataset, architecture, backend path) with published / ours / delta / σ /
command / date. Rows for a `pass`-stub backend are marked `unavailable`, never
measured.
**Caveat.** Published local-rule numbers are often single-seed or best-of.
Reproduce the protocol, compare means, record σ, and say when ours is a mean over
more seeds than theirs.
**Defect policy.** A gap beyond tolerance opens a defect ticket before any new
measurement. Fix the implementation, do not tune the benchmark. A second failure
after the fix pass is a refusal with a written reason, never a quiet exclusion.
**Cost.** 1–2 sessions (scoped down from 2–4). Most cells are minutes.
---
## 4. P2 — MPU1: the memory frontier
**Instrument first — mostly built.** `SystemTrainer` already reports
`peak_memory_mb` per epoch (`core/system_trainer/_resources.py`), surfaced as
`memory_usage` by `_trainer_utils.py:194-207`. Extend `EpochResource` with the
**decomposition** (`params`, `optimizer`, `activations = peak − params −
optimizer − auxiliary`, `auxiliary`, `cpu_rss`) and forward-equivalents from the
existing FLOP counter. Acceptance ladder, on a synthetic depth task used **only**
for instrument acceptance:
- backprop peak is monotone in depth;
- a true layer-sequential rule is flat in depth;
- checkpointing bends the backprop curve down at depth;
- `preserve_rng_state=True` gives gradient parity with plain backprop under
  dropout;
- **calibration:** measured activation bytes match the analytic `c·L·B·W·4`
  within 10%, with **c measured on the declared claim geometry** (c≈1 for
  Linear+ReLU; c≈2 when LayerNorm saves input *and* output). Lock the measured c,
  never a hardcoded 1. A non-binding cell is rejected by the guard;
- forward-equivalents are a **measurement**: measured FLOPs ÷ one-forward FLOPs
  (the counter exists). The ≈3/≈4 values in §1 are predictions to compare, not a
  lock target.
**Binding gate — on the *unrecovered* arm.** The gate asks "is this regime
memory-bound?", so it is computed on **plain `backprop`**, not
`backprop+ckpt`: checkpointing's job is to shrink activations below the gate, so
gating on it self-defeats. At the pilot (B=8192, W=1024, L=64, c=1) plain-backprop
activation share is 89% (SGD) / 73% (Adam). Report the ckpt arm's decomposition
separately; do not gate on it. If the plain-backprop share is <50%, the cell is
`[regime-mismatch]` and enters no claim table. Enforce it as a test over the
claim table. **Name the optimizer per table** — params+Adam state changes the
share, and the Appendix must never mix SGD-primary with an Adam share. **CUDA is
required for the claim:** CPU runs measure RSS only and are instrument-validity
cells, never claim rows.
**Claim task.** CIFAR-10 with headroom. **Primary geometry: Linear+ReLU, no norm**
(c≈1). LayerNorm is the fallback only if the plain stack fails the floor; it sets
c≈2 and requires the Appendix recompute in the same commit. BatchNorm is
excluded (non-local, breaks batch-1 streaming). The data is cached
(`data/cifar-10-batches-py`), but the registry marks it `CostClass.EXPENSIVE`:
use a **fixed 10k-image train subset and the full test split** for the ladder, and
name that bound in every row. The absolute vision criterion (>0.95) does not apply
to a flat-MLP memory ladder: W1/W2 are **relative** claims, and a 45–60% MLP is
not a failure verdict.
**Binding operating point.** Depth/width/batch are **hyperparameters and run
settings, not registry axes** (`num_layers` is an integer hyperparameter,
`batch_size` a run setting). Ladder: depth 4/8/16/32/64, width 1024/2048,
**batch 1k/8k/16k**, dtype fp32 for both arms (local rules often need it; a bf16
backprop vs fp32 local comparison is confounded). **SGD is the primary table;
Adam is a second table and its shares are computed separately.** Never print an
Adam share next to an SGD-primary label.
**Pilot appendix (one binding point, not the grid): B=8192, W=1024, L=64, c=1.**
| Arm (optimizer) | Activations | Params | Optimizer | Peak | Act. share |
|---|---|---|---|---|---|
| `backprop` (SGD) | 2.0 GiB | 256 MiB | — | 2.25 GiB | **89%** |
| `backprop` (Adam) | 2.0 GiB | 256 MiB | 512 MiB | 2.75 GiB | **73%** |
| `backprop+ckpt` √L=8 (SGD) | ~0.53 GiB | 256 MiB | — | ~0.78 GiB | 68% (report only) |
| `backprop+ckpt` √L=8 (Adam) | ~0.53 GiB | 256 MiB | 512 MiB | ~1.28 GiB | 41% (report only) |
The gate reads the **plain `backprop`** row. The ckpt rows are reported, never
gated: at Adam they fall below 50% *by design*, which is why gating on the
recovered arm self-defeats. At B=1024, W=512 the same arithmetic gives
activations ≈134 MB against ≈200 MB params+Adam — the v2 failure mode. Write this
appendix into the pre-registration so the binding check is arithmetic, not
assertion.
### 4.1 Measured binding arithmetic (T4a, 2026-11-15) — **supersedes the c≈1 rows above**
The appendix assumed `c≈1` (stored matmul inputs only). The claim path was
measured: `EpochResources` decomposes the CUDA peak and a two-point depth delta
gives **c = 4.1** (±1 %, W=256, B=2048, L=4/8/16, fp32, Linear+ReLU). The peak
carries four per-layer tensors — stored input, layer output, and the two
backward gradient buffers — and the coefficient is now *measured*, not assumed.
`docs/CORRECTIONS.md` correction 8 records the supersession.

Re-priced at the pilot point (L=64, B=8192, W=1024, fp32, c=4.1):

| Arm (optimizer) | Activations | Params | Optimizer | Peak | Fits 8 GB? |
|---|---|---|---|---|---|
| `backprop` (SGD+momentum) | 8.2 GiB | 256 MiB | 256 MiB | **≈8.7 GiB** | **no** |
| `backprop` (Adam) | 8.2 GiB | 256 MiB | 512 MiB | ≈8.9 GiB | **no** |
| `backprop+ckpt` √L=8 (SGD) | ≈1.0 GiB | 256 MiB | 256 MiB | ≈1.5 GiB | yes |

**Consequence.** The pilot's operating point moves: the claim ladder must be
posed where the arm fits, not where the old arithmetic said it would. Affordable
points at W=1024 with an 8 GB card and 20 % headroom (≈6.4 GiB budget):

| B | L | Activations (c=4.1) | Peak (SGD+momentum) |
|---|---|---|---|
| 8192 | 32 | 4.1 GiB | ≈4.6 GiB |
| 16384 | 16 | 4.1 GiB | ≈4.6 GiB |
| 8192 | 64 | 8.2 GiB | 8.7 GiB — **skip** |

So the **claim ladder is B=8192 at L≤32, or B=16k at L≤16**, and the depth rung
that wins W2 is bounded by the card, not by the model. The gate still binds
(measured share 0.95 at B=2048/L=8, and the share rises with depth), so the
verdict is unchanged; only the coordinates move. **The checkpointed arm's ≈1.0
GiB activation set is what makes the depth claim possible at all** — that is the
measured reason T4b gated T6, and the landed arm measures 3894 MB of epoch peak
at L=64/W=1024/B=8192 (forward retained set 480 MB, §9.4).
**Minimal claim ladder (register this, not the grid).** B=16k for L=16/32;
B=8192 for L=64 when c>1; W=1024; both arms; 5 paired seeds → **~30 cells**. The
5×2×3 grid is the artifact/screen, not the claim. Admission-check each cell's
measured cost against the 8 GB card with 20% headroom; skip the unaffordable.
**Arms.**
1. `hybrid` — lockstep-local trunk (O(B·W) working set) + 2–4 layer backprop
   head; PEPITA-trunk first (one global error from the head, no auxiliary params
   beyond the feedback matrix); InfoPro-style auxiliary heads second, with their
   params and optimizer state inside the memory ruler.
2. `local` — pure local control (the rule P1 validated).
3. `backprop` — plain.
4. `backprop+checkpointing` — √L segments.
5. optional `backprop+ckpt+optimizer-offload` — a **priced** arm; offload trades
   PCIe bandwidth, and optimizer offload is arm-neutral, so the differential is
   activations only. Say so; do not present it as extra arm surface.
**Hybrid integration (T3b ✅, landed 2026-11-16).** `System.credit` is a single
config (`ontology/system.py:426`); there is no per-layer credit. `HybridCredit`
is a C wrapper that owns a `PepitaTrunk` contrast and a `GradientCredit` head and
dispatches by layer index; it delegates the head to
`GradientCredit.gradient_of` rather than reimplementing autograd. No schema
change; one registry row and one declared `estimator_kind`.
**Reuse the runner, do not build a second ladder.** `validation/backprop_parity.py`
already implements a depth loop with per-depth baseline, seeds, bootstrap CIs,
peak memory, FLOPs, and parameter counts (`run_parity`, :729). Extend it with a
`batch_size` parameter and the `pepita`/`local_goodness` families (its portfolio
today is backprop/FA/PC/eqprop) and use it as the cell runner. Add only the Pareto
aggregation on top.
**Budgets.** Report params as a column, **not** a matched budget: matching params
across hybrid/local/backprop needs a width search and buys nothing the claim
needs. Report accuracy at (a) matched peak memory and (b) iso-walltime/
forward-equivalents. Two tables, one Pareto figure
(`computronium/experiment/analysis/pareto_analysis.py:compute_pareto_frontier`),
plus a stacked memory decomposition (params / optimizer / activations /
auxiliary) per arm.
**Claim shape (if W1/W2 hold).** "At 8 GB and matched walltime, the hybrid
dominates √L-checkpointed backprop on (accuracy, peak GB) — ≥δ hypervolume or
baseline accuracy at ≤0.5× **activation bytes** — and the local trunk reaches 2×
depth at
the accuracy floor." Pre-register the floor, the budgets, δ, the LR box, and the
binding arithmetic before seed 1.
**Stop rule.** Hybrid loses to `backprop+ckpt` at matched memory and matched
walltime → close MPU1 entirely, one verdict, no rescue tuning. Pure local losing
while the hybrid wins is the expected result and is not a stop.
---
## 5. P3 — MPU2: an architecture backprop cannot differentiate
**Why this is the novelty engine.** The only genuinely new capability available is
an architecture whose forward pass has operations with no useful derivative: hard
top-k routing, discrete selection, learned sparse connectivity, spiking
thresholds, in-network memory writes. Local credit needs no surrogate; backprop
must invent one, and the surrogate is biased.
**Run the cheap screen now, in parallel with P1.** STE-gap versus stacked
discrete-op count (1/2/4/8) against a soft-relaxation upper bound. If the gap
grows with depth, the matched pair is worth running. If it is flat, drop the
track after one session — that is the stop rule, not a failure.
**Candidate (pick one, not four).** Hard top-k routing where only k of n experts
receive a gradient-bearing path. `algorithms/routing/` already holds the routing
implementation; start there, do not build a new router.
**Baseline (strongest, not most convenient).** STE **plus load-balancing/z-loss**.
Expert-choice routing and dense-backprop-for-sparse-MoE are positioning controls
and literature anchors, not extra arms. "Local beats vanilla STE" is not a
publishable claim; vanilla STE is not the strongest baseline.
**Mechanism metric, defined.** Gradient bias of the estimator arm relative to a
**declared reference**: the temperature-smoothed routing gradient, and/or a
finite-difference estimate on a small net. "Bias magnitude" without a reference is
undefined — the true gradient of hard top-k is zero almost everywhere. The
forward-mode reference is scoped to a pure `nn.Sequential` first; if the composed
system is not functional (in-place ops, stateful settle), it is
**reference-only**, never an arm.
**Design.** Router accuracy and end-task accuracy at matched walltime; the bias
measurement is the mechanism claim.
**Stop rule.** STE+aux wins by ≥1 pp → publish the negative with the measured
bias; do not tune the local arm to rescue it.
---
## 6. P4 — MPU3: streaming without replay
**Why.** Batch-1, non-stationary data, no replay buffer: the regime where the
memory advantage is structural rather than a trade against checkpointing. But
locality does not address forgetting — that is weight interference — so the
mechanism under test is local credit **composed with consolidation**.
**Plasticity first (cheapest falsifier).** Final-task accuracy at batch 1. If the
local arm cannot learn the stream at all, retention is moot; stop there.
**Protocol.** A fixed sequence of 5 tasks, 1 epoch each, fixed order
(`SplitMNIST` first), presented once. Metrics: final-task accuracy (plasticity),
`CLMetrics.backward_transfer`, `avg_forgetting`, and `peak_memory_mb`, at
matched per-step cost. Name the order and the epoch budget in the registration;
a drifting distribution needs a declared generator, not a description.
**Arms.** The continual runner and its arms already exist
(`core/continual/runner.py`, `create_ewc_arm`, `create_si_arm`,
`create_replay_arm`, `SplitMNIST`). P4 is a **protocol and measurement** ticket,
not an implementation ticket:
- `local × EWC/SI` — `ElasticConsolidationUpdate` (`core/continual/arms.py:90`);
  `SynapticIntelligence` already exists at `core/continual/losses.py:84` and is
  lifted to a U row by T8, not rewritten;
- `backprop × EWC/SI` (the strong baseline);
- `backprop × EWC/SI ± small replay` — replay is priced at matched memory, and in
  the GB regime it is cheap, so a matched-memory replay comparison is a **foregone
  negative** and must not be the claim;
- optional compositional: `local × EWC` vs `backprop × EWC` at matched memory and
  iso-cost.
**Runner.** Use the existing `run_continual_learning`
(`core/continual/runner.py`); do not build a stream harness.
**Matched budget.** A pre-registered **analytic byte cap** (replay buffer +
consolidation state ≤ cap), enforced in the GPU runner, plus matched per-step
cost. "MCU-class" is a byte budget, not a device claim — the run is CUDA. If the
contest is GB-scale memory, replay wins by design and the result is
uninformative. **Consolidation state counts:** EWC's Fisher/importance vectors and
SI's +1× parameter state enter the cap, or the local arm gets a free budget.
**Stop rule.** Replay saturates retention at the tiny budget → close MPU3 and
record the saturation point. A replay-wins negative is a coordinate result, not a
verdict on local credit.
---
## 7. T0/D1 — deferred, manual tag now
The affinity instrument serves the composition-wide **search**, which §12 defers.
The three MPUs are targeted experiments and need no proposal bias. So:
- now: one manual `regime` tag on cells (a `StrEnum`, no proposal bias, no A/B);
- schema (`AxisSpec.regime_affinity` beside `target_kind` at
  `experiment/schema/axis.py:116`), coverage, and locks stay written for when the
  search re-enters;
- **D1 after P2**, and power it first: promotion is rare by design, so 300
  cells/arm yields single-digit events and "CI excludes 0" is likely undecidable.
  Use a continuous surrogate (screen-score uplift, native share) or pre-register
  a larger n.
**Invariants (unchanged):** affinity biases a proposal, never refuses a cell;
`--no-affinity` exists; an empty affinity set needs a written reason; the lock
fails if the field's removal leaves proposals unchanged on a seeded fixture; a
below-bar foreign cell is `[regime-mismatch]`, not a defect.
---
## 8. Ticket DAG (critical path)
| # | Ticket | Cost | Acceptance / output |
|---|---|---|---|
| T1 ✅ | **Truth pass** (defect tickets, stub fixes, measured complexity table, `estimator_kind`/`bias_reference` declarations, locks, `BENCHMARKS.md` skeleton, `CORRECTIONS.md` rows) | 1 session (watchdog 2×; if it overruns, split code-fixes from schema/locks) | A §14 "progress" row; each lock fails on current code and passes after its fix; no silent `activations_mb: 0.0` |
| T3 ✅ | Lockstep two-pass FF/PEPITA; exact-update lock vs the store-all schedule | 1 session | O(B·W) measured peak, flat in depth; max\|ΔW\| ≡ 0 per layer |
| T4a ✅ | Memory **decomposition** (`EpochResource`: params/optimizer/activations/aux/RSS) + binding guard + calibration lock | hours | `L·B·W·4` within 10%; guard rejects a non-binding cell |
| T4b ✅ | `backprop+ckpt` (√L segments, `preserve_rng_state`, `use_reentrant=False`, geometry forward) | 1 session | §4 acceptance ladder; gradient parity under dropout |
| T4c ✅ | Extend `validation/backprop_parity.run_parity` with `batch_size` and `pepita`/`local_goodness` families | hours | one runner for the ladder; no second depth loop |
| T5 | P1 scoped: 3 publishables + arms actually used | 1–2 sessions | rows with backend path, dtype, optimizer, σ |
| T3b ✅ | **Hybrid arm**: `HybridCredit` wrapper (trunk local + head backprop) + identity | 1–2 sessions | composes; trunk peak flat in depth; head gets true gradients; **landed 2026-11-16** |
| T6 | P2 pilot at **one binding operating point**, positive control included | 1 session | binding arithmetic appendix; positive control passes; then register |
| T6a | Pre-registration: `ThresholdRegistration` for the accuracy delta/floor + a budgets appendix the binding test reads | hours | floor, budgets, `n_max=5`, binding arithmetic, stop rule; extra keys are ignored by the loader, so the test reads the raw JSON |
| T7 | P0 estimator credits: `SurrogateCredit` (required baseline) + `ForwardTangentCredit` (bias reference); `ScoreFunctionCredit`/`ZerothOrderCredit` as controls | 1 session | W3's baseline and reference exist as first-class C rows with identity + compatibility predicates (§19) |
| T8 | P4 baselines: lift `SynapticIntelligence` to U; `CascadeSynapsePlasticity` | 1–2 sessions | local×SI and local×cascade runnable at the tiny-budget point (§19) |
| T9 | Temporal taxonomy: `EligibilityPropCredit`, `UnbiasedOnlineRTRL`, `RTRLReference` | trigger-gated | fires when MPU1 closes (T6) or a sequence-length axis enters (§19) |
| ∥ | P3 screen: STE-gap vs stacked discrete-op count against soft-relaxation bound | hours | gap grows with depth → matched pair worth running; flat → drop per stop rule |
Order: **T1 → T4a → T4c → T4b → T3 → T3b → T6 → T6a** (T1/T4a/T4c/T4b landed
2026-11-15; T3/T3b landed 2026-11-16; **T6 is the next block**), with T5 parallel
and the P3 screen starting alongside T1 (it needs no new primitive and is the
cheapest track-killer). T4b **gates T6** — the pilot compares against
checkpointing — and landed before T3/T6. T7 lands only if the P3 screen promotes,
in parallel with T3. T8 can start once T6 fixes the P4 protocol, in parallel with
T5; it does not wait for P2 to close. T9 is trigger-gated. P4 runs after P2
because both need the binding guard.
**Two falsifiers, two numbers.** T3b's composition lock was the last
**implementation** falsifier (~6 sessions: T1, T4a, T4c, T4b, T3, T3b — all
landed). The first **research** falsifier is T6 (~6–7 sessions), because it
needs T4b, T3, and T3b. Claim-grade row: **~10–11 sessions**.
### 8.1 Remaining work, ordered (start here next session)

| Order | Ticket | Blocks on | First command / file | Done when |
|---|---|---|---|---|
| 1 ✅ | **T4b** — `backprop+ckpt` | landed 2026-11-15 | `core/gradient_checkpointing.py`; `tests/property/test_checkpoint_parity.py` | checkpointed grads ≡ plain under dropout (bit-exact); RNG negative control fails without `preserve_rng_state`; segments=√L (Linears, not modules); **epoch peak 3894 MB < 6554 MB at L=64/W=1024/B=8192** |
| 2 ✅ | **T3** — lockstep two-pass FF/PEPITA | landed 2026-11-16 | `acceleration/ff_kernels.py` `lockstep_contrasts`; `tests/property/test_lockstep_parity.py` | deltas ≡ store-all at `atol=0`; **peak flat 66.3 MB (FF) / 58.5 MB (PEPITA) at L=4→32** at W=512, B=4096; retained-stream negative control bends to 576/568 MB |
| 3 ✅ | **T3b** — hybrid trunk + head | landed 2026-11-16 | `ontology/credit/_hybrid.py`; `primitives/credit_assignment/hybrid/`; `tests/property/test_hybrid_parity.py` | parity with the store-all hybrid **max\|Δ\| = 0.0**; head ≡ backprop; **trunk peak flat 81.0 MB above gradients at L=4→32** |
| 4 | **T6 + T6a** — pilot then pre-registration | T4b ✅, T3 ✅, T3b ✅ | §4.1's re-posed ladder (B=8192, L≤32) | binding arithmetic appendix, both positive controls, `n_max=5`, δ, floor |
| ∥ | **T5** — published parity | nothing (`BENCHMARKS.md` exists) | §3 method, 3 credits + hybrid trunk rule | one row per (credit, dataset, arch, backend path) with Δ and σ |
| ∥ | **P3 screen** | nothing | `benchmarks/joint/z3_fixed_weights.py` (STE already lifted) | STE-gap grows with stacked discrete ops → promote T7; flat → drop MPU2 |
| gate | **T7** / **T8** / **T9** | P3 screen / T6 / trigger | §19 rows | not work until the trigger fires |

**What the next session must not re-derive:** the decomposition API
(`EpochResource.{params,optimizer,activations,auxiliary,cpu_rss}_mb`,
`binding_verdict`), the measured coefficient (`c=4.1`, so the peak is 4× the v6
appendix), the ladder runner (`run_parity(batch_size=...)` with the `pepita`
family), the checkpointed arm (`create_backprop_mlp(checkpoint_segments=...)`,
`enable_gradient_checkpointing`, segments split at Linear starts), the lockstep
rung (`lockstep_contrasts(chain_a, chain_b, final_activation=...)` — one stream
for both families; `apply_contrast` updates in place; the store-all `forward_*`/
`backward` methods are the reference rung the lock holds at `atol=0`), the
hybrid (`HybridCredit` in `ontology/credit/_hybrid.py`: `PepitaTrunk` contrast,
`GradientCredit.gradient_of` for the head, `split_layer` on a Linear, and
`FeedforwardGeometry.step_layer` for one-layer lockstep with the residual input
threaded; the store-all reference is written from the equations in
`test_hybrid_parity.py`), and the refusal list (FF/SNN contrastive are
unavailable with triggers; hybrid refuses non-feedforward geometry).
---
## 9. Locks (the plan's culture, applied to itself)
1. **Memory-truth lock** — measured peak per backend matches its declared
   complexity class on a seeded depth ladder (constant vs monotone).
   **FF/PEPITA (`ff_kernels.py`) pass it (flat 66.3 / 58.5 MB); every other
   backend still declares `False`.**
2. **Stub detector** — for every contrastive backend: if the target error is
   non-zero, `nudged_phase` must differ from `free_phase` by more than tol. Kills
   the `pass` stubs at `contrastive_kernels.py:507` and `:747` permanently.
3. **Lockstep exactness** — `max|ΔW_lockstep − ΔW_reference| < tol` per layer on
   a seeded fixture. **Landed: `tol = 0` for FF/PEPITA; the hybrid trunk holds
   the same equality against the store-all hybrid at measured max|Δ| = 0.0
   (locked at `atol=1e-7`).**
4. **Checkpoint parity** — checkpointed gradients ≡ plain backprop under dropout
   with RNG preservation.
5. **Binding gate** — the **plain `backprop`** arm's activation share of peak
   ≥50%, else `[regime-mismatch]`, not evidence. The recovered
   `backprop+ckpt` share is reported, never gated. Enforced by a test over the
   claim table.
6. **Memory calibration** — measured activation bytes match `c·L·B·W·4` within
   10%, with **c measured on the declared geometry** (not hardcoded 1) and locked
   with tolerance. The guard rejects a deliberately non-binding cell. A lock
   whose fixture cannot fail is a comment.
7. **Positive controls** — instrument (calibration) **and** learning (plain
   backprop at L=8 reaches the pilot floor). A failed control invalidates the
   run, not the arm.
8. **W2 accuracy floor** — a depth counts only if val accuracy ≥ the pre-registered
   floor; "trainable" must mean "learns".
9. **Identity completeness** — backend path, dtype, optimizer, GPU model, torch
   version, forward-equivalents, seed, command, replay hash; missing field = row
   invalid.
Every lock must fail when its mechanism is removed (TODO46 D26).

**Landed 2026-11-15:** locks 1–2 partially (the declaration, the stub detector,
and the anti-fabrication scan: `tests/property/test_kernel_truth_lock.py`), lock
5–6 (`tests/property/test_memory_binding.py`: decomposition sums to peak,
measured `c`, gate rejects a non-binding cell), lock 4
(`tests/property/test_checkpoint_parity.py`: checkpointed grads ≡ plain under
dropout, with an RNG-off negative control and the pilot-point memory budget),
and the estimator-declaration lock for §2's taxonomy
(`tests/property/test_estimator_lock.py`).

**Landed 2026-11-16 (T3):** lock 3 (`tests/property/test_lockstep_parity.py`:
per-layer deltas ≡ the store-all schedule at `atol=0` for both families and both
surfaces, plus the applied-weight check) and lock 1 for the two two-pass families
(same file: peak flat at L=4/8/16/32, with the **retained-stream negative
control** bending to 8.7×).

**Landed 2026-11-16 (T3b):** lock 3 for the hybrid
(`tests/property/test_hybrid_parity.py`: the lockstep trunk ≡ the store-all
hybrid, max|Δ| = 0.0, head ≡ plain backprop, and a no-grad probe whose first
recorded pass is the negative control), lock 1 for the hybrid trunk (peak above
the weight-gradient set flat at 81.0 MB at L=4/8/16/32, with the **store-all
control** bending 122→1018 MB), and the composed-path learning control (rung 1:
`train_step` decreases loss and every weight moves). Locks 7 (the pilot's
learning control) and 8 (W2 floor) stay open with T6, and lock 1 stays open for
the eight backends that have not been
laddered.
---
## 10. Baseline ladder, stated once
```
backprop
  └─ + checkpointing (√L segments)                    ← required baseline
       └─ + optimizer offload (priced; arm-neutral)   ← optional, differential = activations only
```
Routing: `STE + load-balancing/z-loss` is the required baseline; expert-choice and
dense-backprop-MoE are positioning controls. Streaming: `backprop + SI/online-EWC`
± small replay; the cheapest falsifier is plasticity before retention. **No arm
is compared against a weaker implementation of itself.**
---
## 11. Artifact-first: the deliverable that survives any verdict
The durable, citable artifact is not a single win; it is:
- `docs/BENCHMARKS.md` — published / ours / delta / σ / command;
- the **measured complexity table** — claimed vs actual per backend, with the
  `pass`-stub rows marked unavailable;
- corrections rows in `docs/CORRECTIONS.md`;
- one **Pareto figure per task** (accuracy vs peak GB at iso-walltime) via
  `computronium/experiment/analysis/pareto_analysis.py:compute_pareto_frontier`;
- a **stacked memory decomposition** (params / optimizer / activations /
  auxiliary) per arm — cheap, and the mechanism behind every verdict.
**Venue, decided now (two artifacts, one program).** **NeurIPS Datasets &
Benchmarks** for the reusable comparator suite — identity cards, measured
complexity table, stacked decomposition, Pareto harness. **TMLR** for the
frontier/negative mechanism analysis. Naming both forces the artifact spec; "decide
later" is how the suite drifts into a demo. The contribution is **rigor and the
frontier**, not terra incognita.
---
## 12. Deferred track (v1, kept with triggers)
Nothing here is discarded; each item re-enters when its trigger fires.
| Item | Why it stays | Trigger to re-enter |
|---|---|---|
| **Phase-conjugate credit** (optical) | a credit mechanism physics provides and digital cannot; `U†` realised by phase conjugation, no stored backward weights | a digital claim lands and needs a substrate contrast, or a photonics collaborator appears |
| **Memristive drift as consolidation** | turns a hardware defect into free EWC-like anchoring | P4 closes with **either** verdict — a replay-wins negative is precisely the evidence that motivates substrate anchoring — and a device model with retention exists |
| **Per-layer substrate placement** | the only way to express digital front-end + analog back-end | a substrate signal exists |
| **CSP settling (`energy_structured`)** | settling *is* the algorithm on such tasks | a digital memory/streaming result lands, or a practical CSP use case appears |
| **Composition-wide sweep** | the 6-axis generator remains the long-run idea | three pieces of evidence that composition × regime changes outcomes |
**Why deferred, plainly:** substrate and toy-regime results do not help a user
today. If a digital result needs a substrate control, the trigger fires.
---
## 13. Portfolio discipline (no artificial caps)
1. **Every ticket names a decision, a falsifier, a cost, and a stop rule.** That
   is the only admission rule; there is no ticket-count quota.
2. **Cost is priced from a measured pilot**; the watchdog is 2× that price. A
   ticket that exceeds its watchdog is re-priced or killed, never extended.
3. **Re-rank every session** by expected value to the user ÷ expected cost;
   record the ranking in §14.
4. **Screening is wide; promotion is rare.** Hundreds of L0 cells allowed; five
   seeds and a pre-registration only after a screen promotes.
5. **A low number is a defect probe first** (P1 tolerance rule).
6. **Steering rules — the plan changes itself when results say so.**
| Observation | Steering |
|---|---|
| W1/W2 hold | MPU1 becomes the lead claim; MPU2/3 run as follow-ups |
| hybrid loses at matched memory and walltime | close MPU1; lead with MPU2/MPU3; the artifact is the frontier |
| pure local loses but hybrid wins | expected; report hybrid as the composition result, not a local-rule win |
| binding gate red at the pilot | re-pose the operating point (batch/width/dtype); **never** report the cell |
| STE+aux beats local on routing | publish the negative with the measured bias; drop the non-differentiable track |
| P3 screen flat in depth | drop MPU2 after one session |
| plasticity fails at batch 1 | stop P4 before retention; retention is undefined |
| replay saturates streaming | close MPU3; report the saturation point |
| P1 gaps beyond tolerance | defect tickets only; no measurement claims until closed |
| nothing wins | the honest negative: the structural advantage does not convert at matched budgets, with the measured decomposition showing why. Then §12's triggers lead |
---
## 14. Scoreboard (update in place; rulers mandatory)
| Date | Track | Measurement | n | Ruler | Regime | Verdict | Ticket |
|---|---|---|---|---|---|---|---|
| 2026-11-15 | P1 | complexity audit: 14 fabricated `activations_mb: 0.0` → `None`; 1 stub kernel fixed, 2 marked unavailable; 10 credit rows declare `estimator_kind` | 15 backends, 10 rows | declaration vs measured (none verified yet) | — | **defect found and fixed by failing locks** | T1 ✅ |
| 2026-11-15 | P2 | activation coefficient `c` on the claim geometry | 2 depth deltas × 1 seed | measured `c·L·B·W·4`, spread <1 % | Linear+ReLU fp32, W=256, B=2048, L=4/8/16 (CUDA) | **c = 4.1** (assumed 1 → peak 4× the appendix; pilot point re-posed, §4.1) | T4a ✅ |
| 2026-11-15 | P2 | ladder runner reachability | 2 cells | baseline + family cell returned, `results.json` written | iris, 1 epoch, 1 seed, CPU, 4.9 s | **defect found and fixed** (`batch_size` NameError blocked every campaign) | T4c ✅ |
| 2026-11-16 | P2 | lockstep two-pass rung: exactness and depth-flat peak | 2 families × 4 depths × 1 step | per-layer ΔW vs store-all (`atol=0`); CUDA peak above params | Linear+ReLU fp32, W=512, B=4096, L=4/8/16/32, RTX 3080 10 GiB | **ΔW ≡ 0; peak flat 66.3 MB (FF) / 58.5 MB (PEPITA) vs 576/568 MB retained; three live defects fixed** | T3 ✅ |
| 2026-11-16 | P2 | hybrid credit (lockstep-local trunk + exact head): parity and depth-flat peak | 2 fixtures + 4 depths × 1 step | per-layer ΔW vs store-all hybrid; head vs plain backprop; CUDA peak above gradients | Linear+ReLU fp32, W=512, B=4096, L=4/8/16/32, RTX 3080 10 GiB | **trunk Δ ≡ 0; head ≡ backprop; trunk peak flat 81.0 MB vs store-all 122→1018 MB; composed step learns** | T3b ✅ |
| 2026-11-15 | P2 | `backprop+ckpt` retained set and pilot admission | 2 depths × 1 forward + 1 epoch | forward peak and epoch peak vs the 6554 MB budget | W=1024, B=8192, L=16/64, fp32, RTX 3080 10 GiB | **ckpt fwd 480 MB at L=64 vs plain 2080 MB; epoch peak 3894 MB < budget; grads bit-exact under dropout** | T4b ✅ |
| — | P1 | published-parity (3 publishables + hybrid trunk rule) | — | published ±1 pp / σ | — | — | T5 |
| — | P2 | memory frontier (2 budgets, dominance/hypervolume) | — | acc @ matched memory / iso-walltime; binding share; forward-eq; δ | — | — | T3, T3b, T6 |
| — | P3 | routing: local vs STE+aux; bias | — | acc @ matched walltime; bias vs declared reference | — | — | P3 screen |
| — | P3 | estimator taxonomy (after screen) | — | bias vs declared reference; variance; forward-eq | — | — | T7 |
| — | P4 | plasticity + retention (SI/cascade baselines) | — | final-task acc; BWT; avg_forgetting; buffer size; k×params | — | — | T8 |
**Progress is one of:** a published-parity reference (P1); a measured frontier
(P2–P4); a promoted claim; a defect found and fixed by a failing test; a refusal
with a trigger. **Not progress:** more cells, more prose, more primitives, a knob
swept to pass.
---
## 15. Rules and guardrails
- **A claim names its budget.** Memory, walltime, forward-equivalents, or params
  — never an unstated swap.
- **The baseline is the strongest one**, not the most convenient.
- **Every number carries its ruler, its command, and its σ.**
- **Every run carries a positive control.** A failed control invalidates the run,
  not the arm. Never skip it (SEC: the control is the cheapest falsifier).
- **Rows, not prose.** ≤1 new module per ticket; no ontology change beyond the
  per-layer credit field and the §19 admissions, each bound to a ticket.
- **A new kernel path is a new identity, never a silent replacement.** Old rows
  stay valid under their old identity card.
- **Lift, do not duplicate.** A mechanism that already lives inside another
  module (STE in `core/utils/surrogate.py`, REINFORCE in `training/rl.py:196`,
  Lion at `primitives/parameter_update/lion`) becomes a first-class primitive by
  wrapping it, never by a second implementation.
- **No tuning to pass.** A knob turned to rescue a cell is a defect ticket.
- **Pre-register claims only**; screens run freely and stop cheaply. Reuse
  `configs/preregistrations/` (`r92_memory_budget_registered.json` is the shape).
- **Watchdog = 2× pilot price.** Kill or re-price; never extend.
- **If a ticket does not name a decision and a falsifier, it does not land.**
- **Rewrite §0/§14 in the same commit as the result.**
- **The plan's job is to shrink work.** The repo is ~3,000 files and 50 TODOs
  deep; a ticket that adds surface without removing a question is rejected.
---
## 16. Handoff contract
- TODO92 stays closed: gate, rulers, registrations, and ledger unchanged.
- Start order: **T1 → T4a → T4c → T4b → T3 → T3b → T6 → T6a** (T1/T4a/T4c/T4b/T3/T3b
  landed; **T6 next**), with T5 parallel and the P3 screen alongside T1; T7
  conditional on the screen promoting, T8 after T6, T9 trigger-gated.
- Every ticket lands with its measurement recorded where the mechanism lives, not
  only in the log.
- **Live from 2026-11-16:** T3 and T3b are landed; the next block is T6/T6a
  (pilot then pre-registration). The hybrid's trunk runs the same lockstep
  contrast the T3 kernel measured, its head is `BackpropCredit` on a
  `detach`ed boundary, and the store-all hybrid is the parity reference
  (§18 T3b). The frontier's matched comparison is the only missing piece.
- If a steering rule fires, rewrite §0 and §14 in the same commit that records the
  result.
---
## 17. Review answers (resolved)
| Q | Answer |
|---|---|
| 1. Order | T1 → T4a → T4c → T4b → T3 → T3b → T6 → T6a, T5 parallel, P3 screen alongside T1; T7 only if the screen promotes; T8 after T6. T4b landed and gates T6 (the pilot compares against checkpointing). |
| 2. Task | CIFAR-10, **fixed 10k-image train subset + full test** (`CostClass.EXPENSIVE`; data cached at `data/cifar-10-batches-py`). Depth/width/batch are hyperparameters and run settings, not registry axes. Synthetic depth task only for instrument acceptance. Normalization fixed across arms: LayerNorm or none — BatchNorm is non-local and breaks batch-1 streaming. W1/W2 are relative claims; the absolute vision bar does not apply. |
| 3. Checkpointing | **Landed (T4b).** `core/gradient_checkpointing.py` + `FeedforwardGeometry.set_gradient_checkpointing`, √L segments split at Linear starts, `use_reentrant=False`, `preserve_rng_state=True`, geometry forward only; grads bit-exact under dropout and the arm fits L=64 at W=1024/B=8192. |
| 4. P1 scope | Three publishables + the arm P2–P4 uses. Not eight. Add the complexity-audit column; reproduce the published protocol and record σ. |
| 5. D1 timing | Schema + lock written now, D1 after P2, powered for a continuous surrogate or a pre-registered larger n. |
| 6. Triggers | Event triggers, no fixed dates. Memristive-consolidation fires when P4 closes with either verdict. |
| 7. Headline | **Frontier, not depth:** "accuracy per GB at iso-walltime", ε-dominance with a pre-registered δ (or baseline accuracy at ≤0.5× **activation bytes**), with a stacked memory decomposition. "2× depth" is reported only with the accuracy floor. |
---
## 18. Code-change appendix (what each ticket touches)
**T1 — complexity truth.**
- `acceleration/kernel_backend.py:143` — `memory_complexity` gains a
  `complexity_verified: bool` (or `None`) so an unmeasured claim is distinguishable.
- Every `get_memory_stats()` returning `activations_mb: 0.0` — return `None`
  until measured, or compute from captured tensors. Files: `backprop_kernels.py`
  (:181), `ff_kernels.py` (:240, :576), `pc_kernels.py` (:294), `tp_kernels.py`
  (:505), `fa_kernels.py` (:328), `mep_kernels.py` (:308), `dfa_kernels.py`
  (:299), `hebbian_kernels.py` (:237), `contrastive_kernels.py` (:235),
  `snn_kernels.py` (:351), `tile_kernels.py` (:478, :1028),
  `eqprop_kernel_backend.py` (:342, :350).
- `acceleration/export.py:191` — identity card carries `complexity_verified`,
  backend path, dtype, optimizer, GPU model, torch version, forward-equivalents.
**T2 — stub fixes.**
- `acceleration/contrastive_kernels.py:498–510` `PEPITAContrastiveKernel.nudged_phase`
  — replace `pass` with error modulation via `_feedback_matrix` (the faithful
  `ff_kernels.PEPITAKernelBackend` is the reference); until fixed, mark the kernel
  `available=False` with `unavailable_reason`.
- `:747` `SNNContrastiveKernel._simulate` — same, or mark unavailable.
- `:410` `FFContrastiveKernel` — verify label-change semantics; `nudged` returning
  free otherwise yields a zero update.
**T3 — lockstep recompute (✅ landed 2026-11-16).**
- `acceleration/ff_kernels.py` — a two-pass path: pass 1 computes the error and
  discards intermediates; pass 2 recomputes standard and perturbed activations
  layer-by-layer in lockstep and updates W_ℓ immediately. Exact because each
  W_ℓ is used once per pass before its update.
- **What the code does.** `lockstep_contrasts` is one generator for both
  families — FF contrasts its positive and negative chains, PEPITA its standard
  and error-modulated ones, and both reduce to
  `postᵀpre/B` on each chain (`contrast_delta`, the Triton twin's tested
  equation). `apply_contrast` writes the layer before the next one is produced.
  `train_step` and `kernel_train_step` both run it under `no_grad`; the
  activation lists are gone from the step paths.
- **Where the lock came from.** The plan said "lock against the `algorithms/`
  path". That path's rule is **not** this rule: `PepitaCredit` takes the exact
  autograd gradient of the modulated loss, the kernel rung is the closed-form
  per-layer contrast (`estimator_kind` differs by design, §2). Numeric parity
  there would have been a tolerance chosen to pass. The lock is therefore
  **lockstep ≡ store-all of the same equations**, per layer, at `atol=0`, with
  the store-all rung retained as production reference code and the expected
  delta recomputed from the definition inside the test. The `algorithms/` parity
  question belongs to T5/P1 and is unchanged.
- **Three live defects it killed.** (1) `FFKernelBackend.train_step` called
  `self.backward_contrastive(...)`, which does not exist — every FF system-path
  step raised `AttributeError`. (2) `PEPITAKernelBackend.train_step` called
  `self.backward(std_acts, err_acts)` against a signature that required a third
  `error` argument — same outcome. (3) The bespoke PEPITA step multiplied the
  standard pre-activation into both chains while the Triton twin (its tested
  specification) uses each chain's own — the step and its own kernel disagreed.
  Also removed: `feedback_matrix_scale` was applied a second time to the update
  (it already scales the modulation) and the now-dead `compute_goodness`.
**T4a — decomposition and guard (hours, not sessions).**
- `core/system_trainer/_resources.py:62` `EpochResource` — add
  `params_mb`, `optimizer_mb`, `activations_mb`, `auxiliary_mb`, `cpu_rss_mb`;
  `EpochResources.stop` already reads CUDA peak, so subtract the known terms and
  record the remainder as auxiliary (never assert 0.0).
- `experiment/kernel/_trainer_utils.py:194-207` — emit the decomposition and
  `activation_share` beside `memory_usage`.
- new lock/test `tests/property/test_memory_binding.py` — calibration within 10%
  of `c·L·B·W·4` with **c measured on the declared geometry** (Linear+ReLU c≈1;
  LayerNorm c≈2), the gate computed on **plain `backprop`**, and a deliberately
  non-binding cell rejected.
- CPU RSS: `psutil` is already a declared dependency (`pyproject.toml:100`);
  read `Process().memory_info().rss`. No new dependency.
**T4b — activation checkpointing (✅ landed).**
- `core/gradient_checkpointing.py` — `segments_for_depth` (√L over Linears),
  `GradientCheckpointing.to_identity()` (`grad_checkpointing_segments`,
  `compiled=False`), and `enable_gradient_checkpointing(system, segments=None)`,
  which refuses a geometry with no measured path instead of silently running
  plain. `FeedforwardGeometry.set_gradient_checkpointing` splits the stack at
  **Linear starts** (a mid-block split would resume with the wrong residual skip
  tensor) and wraps each chunk with `checkpoint(..., use_reentrant=False,
  preserve_rng_state=True)`. The wrapped unit is the geometry forward, never
  `system.train_step` (which contains the update). Under checkpointing,
  `forward_with_intermediates` returns segment boundaries, so the retained set
  is O(√L·B·W), not O(L·B·W). `torch.compile` is not on this path; the identity
  card records `compiled=False`, and a compiled ckpt cell would need both
  variants measured and named.
**T4c — reuse the existing ladder runner.**
- `validation/backprop_parity.py:729` `run_parity` — add `batch_size`, and add
  `pepita`/`local_goodness` to `_COMPUTE_MATCHED_PORTFOLIO`; the depth loop,
  per-depth baseline, seeds, bootstrap CI, peak memory and FLOPs already exist.
**T3b — hybrid (declare the step semantics; no hand-waving). ✅ Landed
2026-11-16.**
- `HybridCredit` in `ontology/credit/_hybrid.py`, wrapped by
  `primitives/credit_assignment/hybrid/`; owns `trunk_credit` (`PepitaTrunk`
  contrast) + `head_credit` (`GradientCredit`) + `split_layer`; dispatches by
  layer index. One registry row in `_CREDIT_PRIMS`, one `estimator_kind="hybrid"`,
  a feedforward-geometry refusal (constraint row + `SystemConfig` validator), and
  a bottom-level `GradientCredit.gradient_of` shared with the head.
- **Semantics, fixed before the code:**
  1. **standard pass**: trunk forward under `torch.no_grad()`; at the boundary
     `h = h.detach().requires_grad_(True)`; head forward records the graph →
     logits → CE;
  2. head backward on the standard pass → boundary error
     `δ = ∂L/∂h_trunk_out` (the head's input gradient);
  3. **trunk error-modulated pass** under `torch.no_grad()` with `e_out = δ`,
     propagated by the trunk's feedback matrices; this is the PEPITA trunk's
     second pass;
  4. compute trunk and head gradients from the **same pre-update weights**; apply
     trunk then head. No second head forward, no head update before the boundary
     error is formed.
  The `no_grad` trunk and the `detach` boundary are what make the memory claim
  true; without them the trunk graph is retained and the hybrid is just backprop.
- **Reference fixture (correctness, not speed):** a *store-all* hybrid — two-pass
  PEPITA trunk + backprop head, no lockstep — is the reference. Lock the lockstep
  trunk against it (`max|ΔW| < tol` per layer), exactly as T3 does. "Composes" is
  not acceptance; parity is.
- **Acceptance:** hybrid loss decreases, trunk gets non-zero updates, head gets
  true gradients, parity with the store-all reference on a seeded synthetic task,
  and the measured trunk activation set is **flat in depth**. Budget the upper
  2 sessions; on watchdog, fall back to pure-local and record the composition
  refusal.
- the head's autograd graph is the only stored activation set; the trunk's
  working set is O(B·W) per layer. Record both in the decomposition, or the
  hybrid's advantage is unmeasured.
- no `System` schema change: `credit` stays a single protocol object.
- **What the code actually did.** `FeedforwardGeometry.step_layer` is the
  one-layer advance that threads the last Linear's *input* across the following
  activation (the residual skip reads it); `_apply_layers` now loops over it, so
  the lockstep and the store-all reference cannot disagree about a skip.
  `split_layer` is a stack index and must land on a Linear (a split between a
  Linear and its activation would lose the skip input); `-1` puts the head on
  the last two Linears. The trunk's first pass and second pass both run under
  `torch.no_grad()`; the head graph is the only retained set. The measured peak
  above the weight-gradient set is flat at **81.0 MB** (L=4→32, W=512, B=4096)
  against the store-all control's **122→1018 MB**; the per-layer trunk delta is
  bit-exact (max|Δ| = 0.0) and the head's gradient equals plain backprop's at
  the same boundary. `tests/property/test_hybrid_parity.py` (8 tests, 16 s,
  2 s CUDA) is the lock; the composed path's 40-step loss decreases and every
  weight moves. A measured defect was found and fixed by the depth lock: the
  second pass originally ran outside `no_grad`, so each stored contrast's
  `grad_fn` pinned the whole activation chain and the "flat" peak grew
  101→577 MB — the lock's first measurement caught it.
**T6a — pre-registration.**
- `configs/preregistrations/t93_memory_frontier.json` — a `ThresholdRegistration`
  for the accuracy delta/floor (`metric`, `threshold`, `min_seeds=5`) plus the
  budgets, binding arithmetic, and stop rule as extra keys.
  `ThresholdRegistration.from_dict` ignores extra keys, so a claim-table test
  reads the raw JSON; do not assume the loader enforces the binding gate.
- register the **LR viability ladder** (3 points per arm at L=8, best frozen,
  **seeds disjoint from the claim**), the fixed epochs/`batches_per_epoch`, the
  claim seed list and data-order seed, the **minimal ladder** (§4: ~30 cells, not
  the grid), and the **hypervolume reference point** `(floor−5 pp, max_peak×1.1)`
  with δ — or the ≤0.5× **activation** rule.
- register **both positive controls**: instrument (calibration cell reads
  `c·L·B·W·4` within tol) and learning (plain backprop at L=8 reaches the pilot
  floor). A failed control invalidates the run.
- the ε-dominance claim is computed from the registered budgets after the run;
  the budgets, δ, and the reference point are fixed before it, so this is not
  post-hoc.
**T8 — lift, do not rewrite.**
- `core/continual/losses.py:84` `SynapticIntelligence` already implements the
  mechanism; lift it to `ontology/update/` as a U row and reuse
  `create_si_arm` (`core/continual/arms.py:238`). `create_replay_arm` and
  `create_ewc_arm` already exist for P4's baselines.
**T6 — frontier figure.**
- reuse `experiment/analysis/pareto_analysis.py:compute_pareto_frontier`
  (objectives `["accuracy", "peak_bytes"]`, `maximize=[True, False]`).
**T1 (cont.) — estimator coordinate.**
- `experiment/schema/axis.py:116` — add
  `estimator_kind: Literal["exact","surrogate","gradient_approx","objective_local","local_supervised","score_function","forward_mode","zeroth_order","temporal_local","hybrid"]`
  and `bias_reference: Literal["none","exact_tractable","smoothed_objective"]`
  beside `target_kind`.
- `experiment/schema/seed_registries.py:186` `_CREDIT_PRIMS` — each row declares
  its kind; add the declaration lock. The lock applies to **CREDIT rows only**
  (`AxisSpec` is shared across all six axes; other axes default `unspecified`).
  Initial mapping: `gradient=exact`; `random_projections`, `target_inversion`,
  `thermodynamic_contrast`, `pc_alm` = **`gradient_approx`**;
  `pepita`, `local_goodness`, `local_contrastive`, `homeostatic` =
  **`objective_local`**; `temporal_trace` = `temporal_local`.
  `bias_reference="none"` for `objective_local`/`local_supervised`/
  `temporal_local`; `"exact_tractable"` for the gradient-estimator rows. Confirm
  per implementation before locking; do not label a local objective as a biased
  gradient.
**T7 — estimator credits (only after the P3 screen promotes).**
- new `primitives/credit_assignment/surrogate/` — lift the STE/Gumbel machinery
  already in `core/utils/surrogate.py` and `benchmarks/joint/z3_fixed_weights.py`;
  do not reimplement.
- new `primitives/credit_assignment/forward_tangent/` — `torch.func.jvp`,
  random and antithetic tangents; declare `forward_mode`.
- new `primitives/credit_assignment/score_function/` — lift REINFORCE from
  `training/rl.py:196`; add a moving-average or value baseline; declare
  `score_function`.
- new `primitives/credit_assignment/zeroth_order/` — SPSA (2 evals), antithetic
  ES, blockwise perturbations; declare `zeroth_order`.
- `experiment/kernel/search_space.py:288` — compatibility predicates:
  `score_function` requires stochastic selection in geometry; `forward_mode`
  requires jvp-capable ops; `temporal_local` requires recurrent dynamics.
**T8 — P4 baselines.**
- `SynapticIntelligence` already exists at `core/continual/losses.py:84` and
  `create_si_arm` at `core/continual/arms.py:238`; **lift** it into
  `ontology/update/` as a U row. Do not write a second implementation.
- new `primitives/plasticity/cascade/` — Benna–Fusi k hidden states; price
  `k×params` in the memory ruler before the first cell.
- `primitives/parameter_update/lion/` already exists — reuse it; do not add a
  sign-momentum primitive.
**T9 — temporal (trigger-gated).**
- new `primitives/credit_assignment/eligibility_prop/`,
  `.../unbiased_rtrl/`; the exact RTRL reference is a fixture under
  `tests/`, never a registered arm.
**Deferred T0.**
- `experiment/schema/axis.py:116` — `regime: frozenset[Regime]` beside
  `target_kind`, only when §12's search trigger fires; until then the manual tag
  lives on the cell record.
---
### Landed 2026-11-16 (T3 — what the code actually did)
- **One stream, two families.** `lockstep_contrasts(layers, chain_a, chain_b,
  activation, final_activation=...)` yields `LayerContrast(layer, post_a,
  post_b, weight, bias)`; both rules reduce to `postᵀpre/B` on each chain, so
  Forward-Forward and PEPITA share the kernel instead of owning two copies.
  `apply_contrast(contrast, lr)` writes `W_l` before layer `l+1` is produced.
- **The step paths are the rung; the reference is production code.** `train_step`
  and `kernel_train_step` run the stream under `no_grad`;
  `forward_positive`/`forward_negative`/`forward_standard`/
  `forward_error_modulated`/`backward`/`update_weights` are retained as the
  store-all rung the lock compares against — a live reference, not a test copy.
- **Every step superscript is now measured.** `complexity_verified=True` on both
  backends with the ladder in `docs/BENCHMARKS.md` §2.2; `activations_mb` stays
  `None` per instance because a kernel does not self-measure.
- **`feedback_matrix_scale` is applied once, to the modulation.** It had also
  been multiplying the update in the store-all `backward`, so a non-unit scale
  scaled the rule twice.

### Landed 2026-11-16 (T3b — what the code actually did)
- **One layer advance, two readers.** `FeedforwardGeometry.step_layer` advances
  one layer and returns the threaded `h_in` (the last Linear's input, which the
  following activation's residual skip reads); `_apply_layers` now loops over it.
  A hybrid that advanced the stack itself would add the wrong skip tensor on a
  residual geometry — the parity lock covers the residual fixture.
- **The boundary is a stack index, not a width.** `split_layer` indexes
  `geometry._layers` and must land on a Linear; the head's first layer reads the
  detached boundary, so a split between a Linear and its activation would lose
  the skip input. `-1` selects the last two Linears (the readout and the last
  hidden layer), clamped so the trunk keeps at least one Linear.
- **The head delegates, it does not reimplement.** `GradientCredit.gradient_of`
  is the single exact-autograd choke point (fail-loud on a missing gradient);
  `GradientCredit.compute_pseudo_gradient` and `HybridCredit`'s head both call
  it, so the head's gradient is backprop by construction.
- **The first measured defect was the lock itself.** The second pass initially
  ran outside `no_grad`; each stored contrast's `grad_fn` pinned the trunk's
  activation chain, and the "flat" peak grew 101→577 MB with depth. The depth
  lock caught it on its first run; with `no_grad` the peak is flat at 81.0 MB
  above the weight-gradient set (the O(L·W²) parameter-sized tensor set every
  pseudo-gradient credit returns), and the store-all control is 122→1018 MB.
- **Composition and refusal are both declared.** One `_CREDIT_PRIMS` row, one
  `estimator_kind="hybrid"` card, a `system.py` validator plus a constraint row
  refusing non-feedforward geometry; `tests/property/test_hybrid_parity.py`
  (8 tests, 16 s, 2 s CUDA) is the lock.

### Landed 2026-11-15 (T1/T4a/T4c/T4b — what the code actually did)
- **Estimator coordinate lives on the identity card, not on `axis.py` alone.**
  `AlgorithmIdentityCard` gained `estimator_kind`/`bias_reference`; each of the
  10 credit classes declares them, `spec.estimator_coordinate()` reads the card,
  and `_seed_axis_primitives` stamps `AxisSpec` (which gained the two fields,
  defaulting `unspecified` for the other five axes). One declaration, three
  readers — the same shape as `error_blind_credit`.
- **Complexity truth is a protocol-level declaration.** `KernelBackend` gained
  `complexity_verified`, `available`, `unavailable_reason`; `get_memory_stats()`
  returns `dict[str, float | None]` and `activations_mb` is `None` at all 14
  former zero sites; `KernelRegistry.get` refuses an unavailable backend;
  `export._build_manifest` carries `complexity_verified`, `available`,
  `unavailable_reason`, `backend_path`, `gpu_model`, `torch_version`.
- **The PEPITA contrastive nudge is a real second pass.** `free_phase` caches the
  logits; `nudged_phase` backprojects `one_hot(target) − logits` through the
  fixed feedback matrix and replays the stack. FF and SNN contrastive are
  `available=False` with reversal triggers (no label channel; the nudge branch
  ignores its target).
- **T4a is a decomposition, not a counter.** `EpochResources._decomposition`
  reads geometry params, the update rule's `state_tensors()` (a new non-cloning
  accessor on `StateSnapshotMixin`/`AdamStateMixin`/`LionStateMixin`/
  `BaseParameterUpdate`) and the CUDA peak; `activations = peak − params −
  optimizer − auxiliary`, `None` when the optimizer cannot be enumerated.
  `auxiliary_mb` stays `None` until a mechanism declares state outside both.
- **T4c's real defect:** `backprop_baseline` referenced a `batch_size` it never
  received, so `run_parity` raised `NameError` before training a cell. Fixed and
  locked; `batch_size` is now a campaign parameter (the binding gate is `B·W·L`).
- **T4b is a recovered-arm instrument, not a flag.** Segments count Linears
  (127 modules at L=64, so √L=8 is only correct because the count is depth);
  chunks start at Linears so a residual block never splits; non-reentrant
  checkpoint with `preserve_rng_state=True` gives bit-exact gradients under
  dropout, and the negative control re-runs the fixture with the flag off to
  prove the lock can fail. Measured at W=1024, B=8192: forward peak 480 MB at
  L=64 (plain 2080 MB) and epoch peak 3894 MB against the 6554 MB 8 GB-card
  budget (§4.1). The epoch peak keeps a param-sized gradient floor (~2.1 GB at
  L=64) that checkpointing cannot remove — that is the activation term's bend,
  not the whole peak's.

## 19. Primitive admission queue (cost-priced, ticket-bound)
**Framing.** `more primitives` is not progress (§14). Each row below names the
ticket that cannot run without it; a row whose trigger has not fired is not work.
**Verified inventory (2026-11-15, second pass).** Confirmed absent:
`SurrogateCredit`, `ForwardTangentCredit`, `ScoreFunctionCredit`,
`ZerothOrderCredit`, `LocalSupervisionCredit`, `CascadeSynapsePlasticity`,
`BayesianOnlineUpdate`, `EligibilityPropCredit`, `UnbiasedOnlineRTRL`,
`estimator_kind`/`bias_reference`. Confirmed present and **not admitted as new**:
`lion`, `adam`, `local_adam`, `ortho_adam`, `mean_norm`, `role_split`
(`primitives/parameter_update/`); STE utilities (`core/utils/surrogate.py`,
`benchmarks/joint/z3_fixed_weights.py`); REINFORCE (`training/rl.py:196`); EWC
(`core/continual/arms.py:90`); **SynapticIntelligence**
(`core/continual/losses.py:84`, `create_si_arm`); **replay**
(`create_replay_arm`); eight EP variants plus PC/pcalm (`algorithms/`). SI and
replay are arms today, not first-class U rows: lift SI, reuse replay.
### P0 — estimator credits (unblocks T7; lands only after the screen promotes)
The screen itself needs no new primitive: `benchmarks/joint/z3_fixed_weights.py`
already implements straight-through Gumbel selection. The claim arm needs a
first-class row because the claim table names its estimator kind and identity.
| Primitive (axis) | Mechanism / variants | Decision it enables | Lift from | Cost | Stop |
|---|---|---|---|---|---|
| `SurrogateCredit` (C) | STE, Gumbel-ST, perturbed top-k | the **required** W3 baseline; biased-pathwise arm | `core/utils/surrogate.py`, `z3_fixed_weights.py` | low | screen flat → do not admit |
| `ForwardTangentCredit` (C) | `jvp` random/antithetic tangents, O(1) activation memory | unbiased-pathwise reference; small-width MPU1 dark horse | none | low–med | variance >100× local → reference only |
| `ScoreFunctionCredit` (C) | REINFORCE ± baseline, Gumbel selection | unbiased-for-expected-loss control | `training/rl.py:196` | low | no gain over forward-mode → control only |
| `ZerothOrderCredit` (C) | SPSA (2 evals), antithetic ES, layerwise blocks | gradient-free control; bridges deferred `energy_structured` | none | low | variance too high → control only |
### P1 — the hybrid enabler (blocking for T3b, not trigger-gated)
| Primitive (axis) | Mechanism | Decision | Cost |
|---|---|---|---|
| `HybridCredit` (C) ✅ | wrapper: `PepitaTrunk` local contrast + `GradientCredit.gradient_of` head, dispatch by `split_layer`; `FeedforwardGeometry.step_layer` supplies the one-layer advance | the lead arm cannot compose without it (`System.credit` is one object) | **landed 2026-11-16** |
### P2 — binding arithmetic; trigger-gated, not blocking
| Primitive (axis) | Mechanism | Decision | Trigger | Cost |
|---|---|---|---|---|
| `LocalSupervisionCredit` (C) | greedy layerwise, DGL, InfoPro, periodic global guidance | alternative trunk credit; aux-head params enter the ruler | T6 hybrid trunk below floor or Pareto-dominated | med |
| `FactoredSecondMomentUpdate` (U) | Adafactor | optimizer-memory recovery; moves the binding point | optimizer state ≥40% of peak at the binding point | low |
| `QuantizedStateUpdate` (U) | 8-bit Adam | same; dtype enters identity | same | low |
| `ScheduleFreeUpdate` (U) | schedule-free SGD/Adam | removes schedule asymmetry between arms | a P1 parity gap is traced to schedule choice | low |
**Why not blocking:** the plain-backprop pilot already binds on activations
(89% SGD / 73% Adam at B=8192), so optimizer-state primitives move a boundary
that is already crossed.
### P3 — P4 baselines (lands with T8)
| Primitive (axis) | Mechanism | Decision | Stop |
|---|---|---|---|
| `SynapticIntelligenceUpdate` (U) | **lift** `core/continual/losses.py:84` into a U row; online path integral, +1× params | strictly stronger streaming baseline than EWC, cheaper than replay at tiny budgets | SI ≈ EWC → keep EWC, one arm fewer |
| `CascadeSynapsePlasticity` (P) | Benna–Fusi k-state, power-law forgetting | local consolidation; digital control for memristive drift; first multi-state-synapse family on P | price `k×params` first; stop if it exceeds the affordable replay buffer |
| `BayesianOnlineUpdate` (U) | VON natural-gradient variational online | optional if SI is insufficient | admit only if SI fails its stop rule |
**Cascade caveat.** Benna–Fusi's power-law forgetting is a long-stream phenomenon;
at 5 tasks × 1 epoch it will not separate from SI, and `k×params` may exceed the
tiny cap by construction. Keep it **trigger-gated until a long-stream protocol
exists** (≥20 tasks or a declared drift horizon); at 5 tasks the arm is a
coordinate result, not evidence.
### P4 — temporal, trigger-gated (MPU1 closes or a sequence-length axis enters)
| Primitive (axis) | Mechanism | Role |
|---|---|---|
| `EligibilityPropCredit` (C) | e-prop: eligibility trace × top-down signal, O(params) | supervised temporal-local; fills the gap between STDP and BPTT |
| `UnbiasedOnlineRTRLCredit` (C) | UORO rank-1, provably unbiased | unbiased temporal control; extends the taxonomy into time |
| `RTRLReference` (C, fixture) | exact O(n⁴) temporal gradient on tiny nets | ground-truth lock for temporal bias; never a scalable arm |
**Variant completions, not new primitives:** reward-modulated STDP on
`TemporalTraceCredit`; learned/adaptive feedback on `RandomProjectionsCredit`
(`scripts/probes/w7_pepita_learned_b.py`); differentiable plasticity on
`fast_weights` (trigger: `task_switch`).
### Do not admit
- More EP/PC variants — eight EP variants plus PC/pcalm already ship; no ticket
  needs another.
- Substrate primitives — deferred §12.
- Optimizer-of-the-month (SOAP et al.) — arm-neutral; no ticket prices it.
- Unsupervised rules with no regime win (BCM, sparse coding) — `sparse_topology`
  is commented; defer.
- Lookahead/EMA/SWA — arm-neutral stabilizers; admit as U variants only if
  pre-registered for **both** arms. Applying them to local only is tuning-to-pass.
- Anything requiring new geometry before a ticket needs it.
---
## 20. Executability audit (2026-11-15, verified against the claim path)
| Assumption in v4 | Verified in the repo | Consequence |
|---|---|---|
| Peak memory is not measured in the claim path | `core/system_trainer/_resources.py:73,133,155` captures it; `_trainer_utils.py:194-207` emits `memory_usage` per cell | T4a is hours; only the decomposition, RSS, and guard are new |
| Backprop checkpointing is entirely absent | **Landed (T4b):** `core/gradient_checkpointing.py` wraps the geometry forward in √L segments; `torch.utils.checkpoint(use_reentrant=False)` was already used for settle steps (`core/local_learning/settling.py:403,446,760`) | proven API, and the parity lock makes the wrapped unit (forward, not step) checkable |
| The claim path is `domains/trainer.py` | The claim path is `experiment/kernel/evaluate.py` → `SystemTrainer.train_epoch` | Instrument `_resources`, never `_TaskTrainer` |
| CIFAR-10 needs a download | Cached at `data/cifar-10-batches-py`; registry marks it `EXPENSIVE` | Fixed 10k train subset + full test; price the cell |
| The hybrid is one schema field | `System.credit` is a single config (`ontology/system.py:426`); `BackpropCredit` exists (`joint.py:122`) | T3b is a wrapper primitive, not a schema change |
| A frontier runner must be built | `validation/backprop_parity.run_parity` (:729) already loops depth, baseline, seeds, CIs, memory, FLOPs | T4c extends it; no second runner |
| Synaptic Intelligence is missing | `SynapticIntelligence` at `core/continual/losses.py:84`; `create_si_arm` at `arms.py:238` | Lift to U; do not implement |
| P4 needs a stream and arms | `run_continual_learning`, `create_ewc_arm`, `create_replay_arm`, `SplitMNIST` exist | P4 is a protocol/measurement ticket |
| A router must be built | `algorithms/routing/` exists | Reuse; do not rebuild |
| Depth/width/batch are registry axes | They are hyperparameters/run settings (`num_layers` integer, `batch_size` run config) | Fix the ladder vocabulary; no axis work |
| Lion/sign-momentum is missing | `primitives/parameter_update/lion/` exists | No admission; reuse |
| A "gate" can be a sentence | Locks and claim-table assertions are runnable predicates | Binding guard is a test, not a CLI |
**v6 arithmetic corrections (B1–B6, applied).**
| Bug | Correction | Where |
|---|---|---|
| B1: gate on `backprop+ckpt` self-defeats (Adam share 41%) | gate on **plain backprop** (89% SGD / 73% Adam); ckpt reported only; optimizer named per table | §4, §9.5 |
| B2: ≤0.5× *peak* is unreachable (params+optimizer floor) | ≤0.5× **activation bytes**, or ε-dominance with a pre-registered HV anchor | §2 W1 |
| B3: calibration hardcodes c=1; LN gives c≈2 | measure and lock **c** on the declared geometry | §4, §9.6 |
| B4: hybrid step semantics undefined | explicit four-step order + **store-all hybrid reference** lock | §18 T3b, §9.3 |
| B5: W4 "matched memory" contradicts §6 | pre-registered **analytic byte cap** in the GPU runner | §2 W4, §6 |
| B6: local objectives labelled "biased gradients" | `gradient_approx` vs `objective_local`; alignment, not bias, for local objectives | §2, §18 T1 |
**Cost-critical refs, confirmed 2026-11-15.** `_resources.py:73,133,155` +
`_trainer_utils.py:194-207` (peak → `memory_usage`); `backprop_parity.py:729`
(`run_parity`; portfolio :121; `batch_size` hardcoded 64 at :778, so T4c must add
the parameter); `core/continual/losses.py:84` (SI), `arms.py:90,238` (EWC, SI
arm), `runner.py:412` (`run_continual_learning`); `core/utils/surrogate.py:8` +
`z3_fixed_weights.py`; `ontology/system.py:426` (single credit) +
`core/system_trainer/joint.py:122` (`BackpropCredit`); `settling.py:403,446,760`
(checkpoint precedent); `primitives/parameter_update/lion/`; `psutil` at
`pyproject.toml:100`. **Costs hold.**
**Remaining execution risks, priced.**
1. **Hybrid integration — closed.** It did share one `train_step`: the credit
   re-runs the stack from the free state (like PEPITA), so `System.train_step`
   needed no change. The measured split is a stack index on a Linear, and the
   composed-path learning control passes. Residual geometry required one
   geometry helper (`step_layer`) so the lockstep's per-layer advance threads the
   same skip input the full pass does; the parity lock covers it.
2. **`torch.func.jvp` on a composed system.** Many primitives mutate state.
   Scope the forward-mode reference to a pure `nn.Sequential`; if the composed
   system fails, it is a reference, not an arm.
3. **A 64-layer fp32 MLP may not train.** LayerNorm and residual connections are
   the fallback; if the floor is unreachable at L=32, cap the ladder and report
   the measured ceiling rather than forcing depth.
4. **CIFAR-10 flat-MLP accuracy is low.** W1/W2 are relative; say so in the
   pre-registration so a 45–60% row is not read as a capability failure.
5. **`psutil` availability.** Confirmed: declared at `pyproject.toml:100`; read
   `Process().memory_info().rss`. No new dependency. **Landed in T4a:**
   `EpochResource.cpu_rss_mb`, `None` only if the import fails.
6. **The pilot point does not fit the card at the measured coefficient.**
   c=4.1 puts L=64/B=8192/W=1024 at ≈8.7 GiB (SGD+momentum). Re-posed to B=8192
   at L≤32 or B=16k at L≤16 (§4.1). This is arithmetic, not a risk: the ladder
   is bounded by the card, and the checkpointed arm (≈1.0 GiB) is what buys
   depth. Price the claim cells from these coordinates, not the v6 appendix.
7. **A verified memory class is claimed for two backends, not twelve.**
   T3 measured FF and PEPITA (`complexity_verified=True`, flat at L=4→32, §2.2 of
   `BENCHMARKS.md`); the other eight rungs still declare `False`, so their rows
   are honest gaps rather than claims. Filling them is T5 work, not a defect.
**Net effect.** The truth pass and the decomposition are one day, not three. The
**implementation** falsifier (the lockstep and the hybrid both work) cost ~6
sessions and is closed; the first **research** falsifier (hybrid vs ckpt at a
binding point) costs ~6–7; a claim-grade row ~10–11. T6/T6a is the critical path
to a positive result: the hybrid now has a landed wrapper, measured parity, a
store-all reference fixture, and a depth-flat peak.
