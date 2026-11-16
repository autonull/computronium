# TODO93 — Local learning that wins on the hardware people own
**Status:** 2026-11-15 · **draft v5, executability-audited** — nothing
implemented, no seed spent. v1 (composition-wide search, substrate inversion) is
condensed into §12 as a **deferred track with triggers**; v2's premise was
corrected in v3; v4 added the estimator taxonomy and the ticket-bound primitive
queue (§19); v5 verifies the plan against the actual claim path and corrects its
two costliest assumptions (§20). Every blocking finding is a ticket or a lock,
not prose.
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
---
## 0. Start here
**Three minimum publishable units (MPUs), in order of expected value per session.**
| MPU | Question | Why it is publishable | First evidence |
|---|---|---|---|
| **MPU1 — memory frontier** | On the accuracy-per-GB frontier at iso-walltime, does a *composition* (lockstep-local trunk + small backprop head) dominate `backprop+checkpointing`, and does a pure-local arm reach greater depth at fixed memory? | Practitioners are memory-bound; the contribution is a measured, matched frontier and its decomposition, not virgin territory (InfoPro, TinyFoA, DGL, greedy layerwise already occupy parts) | peak-memory instrument + binding gate + depth/width/batch ladder |
| **MPU2 — non-differentiable architecture** | Does local credit beat the *best backprop-compatible estimator* (STE + load-balancing/z-loss) on hard top-k routing, with the estimator's bias measured against a defined reference? | A capability backprop can only approximate, positioned against the STE and MoE literature | one-epoch STE-gap screen, then one matched pair |
| **MPU3 — streaming** | On batch-1, non-stationary data, does local×consolidation retain more at matched memory than backprop×consolidation ± small replay? | On-device training, edge, privacy-preserving adaptation | plasticity probe, then stream protocol |
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
| W1 | On ≥1 task family, some arm (hybrid allowed) is Pareto-nondominated on (accuracy, peak GB) at iso-walltime | `backprop+ckpt(√L)`; accuracy floor per task; every contributing cell passes the binding gate | no arm dominates **and** no arm reaches the floor | memory frontier closed; the measured frontier is still the artifact |
| W2 | At fixed peak memory (8 GB), max depth at val-acc ≥ floor for local/hybrid ≥ 2× `backprop+ckpt` | floor locked before seed 1; "trainable" must mean "learns" | ratio <2, or floor not met at depth | report the measured ratio; do not claim depth |
| W3 | On hard top-k routing, local beats the **best backprop-compatible estimator** (STE + load-balancing/z-loss) by ≥2 pp at matched walltime, with bias measured against a defined reference | soft-relaxation gradient and/or finite-difference reference, declared before the pair; expert-choice and dense-backprop-MoE are positioning controls, not arms | STE+aux ≥ local−2 pp | negative with the measured bias mechanism named |
| W4 | On batch-1 non-stationary streams, local×consolidation retention exceeds `backprop+EWC/SI` ± small replay at matched memory | plasticity gate first (final-task acc at batch 1); then retention; matched budget named as per-step latency/energy or MCU-class total | replay saturates retention, or local fails plasticity | report the buffer size / budget at which replay saturates |
**Error control and floors.** Fix `n_max=5` paired seeds per depth before the
first run; do not peek. **Floor:** val accuracy at L=8 for the
`backprop+ckpt` arm minus 1 pp, measured on the same task, and then held fixed at
every deeper rung. The floor is set from the **pilot**, and the claim seeds are
**disjoint** from the pilot seeds; otherwise the floor is a peek. If the CI is
inconclusive at `n_max`, that is a coordinate result, not a claim. W1/W2 are
**relative** claims: the repo's absolute vision criterion (>0.95) does not govern
a flat-MLP memory ladder.
**Estimator taxonomy (the reason §19 exists).** W3 is not "local vs weak STE". It
is: *which bias/variance tradeoff wins at matched compute on hard routing* —
biased-pathwise (STE), biased-structural (local), unbiased-score-function
(REINFORCE), unbiased-pathwise (forward-mode), smoothed (SPSA). Every credit
declares **what it estimates and against what reference** (`estimator_kind`,
`bias_reference`), or it cannot enter the claim table.
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
- **calibration:** measured activation bytes match the analytic `L·B·W·4`
  within 10% on a known cell; a non-binding cell is rejected by the guard;
- forward-equivalents match the declared arithmetic.
**Binding gate (blocks the claim, not the run).** If the baseline arm's
activation share of peak is <50%, the cell is `[regime-mismatch]` and enters no
claim table. Enforce it as a test over the claim table, not a sentence. This is
the invariant that makes W2 non-vacuous. **CUDA is required for the claim:** CPU
runs measure RSS only and are instrument-validity cells, never claim rows.
**Claim task.** CIFAR-10 with headroom, normalization fixed across arms
(LayerNorm or none — BatchNorm is non-local and breaks batch-1 streaming). The
data is cached (`data/cifar-10-batches-py`), but the registry marks it
`CostClass.EXPENSIVE`: use a **fixed 10k-image train subset and the full test
split** for the ladder, and name that bound in every row. The absolute vision
criterion (>0.95) does not apply to a flat-MLP memory ladder: W1/W2 are
**relative** claims, and a 45–60% MLP is not a failure verdict.
**Binding operating point.** Depth/width/batch are **hyperparameters and run
settings, not registry axes** (`num_layers` is an integer hyperparameter,
`batch_size` a run setting). Ladder: depth 4/8/16/32/64, width 1024/2048,
**batch 1k/8k/16k**, dtype fp32 for both arms (local rules often need it; a bf16
backprop vs fp32 local comparison is confounded), SGD for both in the primary
table, Adam in a second table with optimizer state counted explicitly.
The pilot uses **one binding point**, not the ladder: B=8192, W=1024, L=64:

| Term | Bytes | Share |
|---|---|---|
| activations 64·8192·1024·4 | 2.0 GiB | 73% |
| params 64·1024²·4 | 256 MiB | 9% |
| Adam state 2× params | 512 MiB | 19% |

At B=1024, W=512 the same arithmetic gives activations ≈134 MB against ≈200 MB
params+Adam — the v2 failure mode. Write this appendix into the pre-registration
so the binding check is arithmetic, not assertion.
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
**Hybrid integration (T3b, the lead arm's missing ticket).** `System.credit` is a
single config (`ontology/system.py:426`); there is no per-layer credit. Build
`HybridCredit`, a C wrapper that owns a trunk credit and a head credit and
dispatches by layer index. `BackpropCredit` already exists
(`core/system_trainer/joint.py:122`, `create_backprop_system`), so the wrapper
delegates rather than reimplements. No schema change; one registry row and one
declared `estimator_kind`.
**Reuse the runner, do not build a second ladder.** `validation/backprop_parity.py`
already implements a depth loop with per-depth baseline, seeds, bootstrap CIs,
peak memory, FLOPs, and parameter counts (`run_parity`, :729). Extend it with a
`batch_size` parameter and the `pepita`/`local_goodness` families (its portfolio
today is backprop/FA/PC/eqprop) and use it as the cell runner. Add only the Pareto
aggregation on top.
**Budgets.** Report accuracy at (a) matched params, (b) matched peak memory,
(c) iso-walltime/forward-equivalents. Three tables, one Pareto figure
(`computronium/experiment/analysis/pareto_analysis.py:compute_pareto_frontier`),
plus a stacked memory decomposition (params / optimizer / activations /
auxiliary) per arm.
**Claim shape (if W1/W2 hold).** "At 8 GB and matched walltime, the hybrid is
Pareto-nondominated against √L-checkpointed backprop, and the local trunk reaches
2× depth at the accuracy floor." Pre-register the floor, the budgets, and the
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
**Protocol.** A sequence of tasks (or a drifting distribution) presented once;
metrics = final-task accuracy (plasticity) and retention of earlier tasks, at
matched memory and matched per-step cost.
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
**Protocol source.** Use the existing `run_continual_learning` runner and a fixed
task order (e.g. 5-way split, `SplitMNIST` first). Name the order in the
pre-registration; a drifting distribution needs a declared generator, not a
description.
**Matched budget.** Per-step latency/energy, or a genuinely tiny total budget
(MCU-class), not GB-scale memory. If the contest is GB-scale memory, replay wins
by design and the result is uninformative. **Consolidation state counts:** EWC's
Fisher/importance vectors and SI's +1× parameter state enter the memory ruler, or
the local arm gets a free budget.
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
| T1 | **Truth pass** (defect tickets, stub fixes, measured complexity table, `estimator_kind`/`bias_reference` declarations, locks) | 1 session | A §14 "progress" row; each lock fails on current code and passes after its fix; no silent `activations_mb: 0.0` |
| T2 | Locks in §9 wired into CI (subsumed by T1; kept as the lock list's home) | — | each lock fails on current code, passes after its fix |
| T2b | `estimator_kind` + `bias_reference` on `AxisSpec`; declare every existing C row; lock fails on `unspecified` | hours | field + declaration table + lock; no new credit admitted until declared (§19) |
| T3 | Lockstep two-pass FF/PEPITA; exact-update lock vs faithful reference | 1 session | O(B·W) measured peak, flat in depth; max\|ΔW\| < tol per layer |
| T4a | Memory **decomposition** (`EpochResource`: params/optimizer/activations/aux/RSS) + binding guard + calibration lock | hours | `L·B·W·4` within 10%; guard rejects a non-binding cell |
| T4b | `backprop+ckpt` (√L segments, `preserve_rng_state`, `use_reentrant=False`, geometry forward) | 1 session | §4 acceptance ladder; gradient parity under dropout |
| T4c | Extend `validation/backprop_parity.run_parity` with `batch_size` and `pepita`/`local_goodness` families | hours | one runner for the ladder; no second depth loop |
| T5 | P1 scoped: 3 publishables + arms actually used | 1–2 sessions | rows with backend path, dtype, optimizer, σ |
| T3b | **Hybrid arm**: `HybridCredit` wrapper (trunk local + head backprop) + identity | 1–2 sessions | composes; trunk peak flat in depth; head gets true gradients |
| T6 | P2 pilot at **one binding operating point** | 1 session | binding arithmetic appendix |
| T6a | Pre-registration: `ThresholdRegistration` for the accuracy delta/floor + a budgets appendix the binding test reads | hours | floor, budgets, `n_max=5`, binding arithmetic, stop rule; extra keys are ignored by the loader, so the test reads the raw JSON |
| T7 | P0 estimator credits: `SurrogateCredit` (required baseline) + `ForwardTangentCredit` (bias reference); `ScoreFunctionCredit`/`ZerothOrderCredit` as controls | 1 session | W3's baseline and reference exist as first-class C rows with identity + compatibility predicates (§19) |
| T8 | P4 baselines: lift `SynapticIntelligence` to U; `CascadeSynapsePlasticity` | 1–2 sessions | local×SI and local×cascade runnable at the tiny-budget point (§19) |
| T9 | Temporal taxonomy: `EligibilityPropCredit`, `UnbiasedOnlineRTRL`, `RTRLReference` | trigger-gated | fires when MPU1 closes (T6) or a sequence-length axis enters (§19) |
| ∥ | P3 screen: STE-gap vs stacked discrete-op count against soft-relaxation bound | hours | gap grows with depth → matched pair worth running; flat → drop per stop rule |
Order: **T1 (absorbs T2/T2b) → T4a → T3 → T3b → T6 → T6a**, with T4c and T5 in
parallel. T4b (checkpointing) lands in parallel with T5 and does not gate T3 —
T3 needs the decomposition (T4a), not checkpointing. T7 lands **only if the P3
screen promotes**, in parallel with T3/T4b. T8 can start once T6 fixes the P4
protocol, in parallel with T5; it does not wait for P2 to close. T9 is
trigger-gated. P4 runs after P2 because both need the binding guard.
**Total to a claim-grade row: ~9–10 sessions** (T1, T4a, T3, T3b, T4b, T5, T6,
T6a, T7/T8 as they fire); to the first falsifier: **~3 sessions** (T1, T4a, T3).
---
## 9. Locks (the plan's culture, applied to itself)
1. **Memory-truth lock** — measured peak per backend matches its declared
   complexity class on a seeded depth ladder (constant vs monotone). Fails today.
2. **Stub detector** — for every contrastive backend: if the target error is
   non-zero, `nudged_phase` must differ from `free_phase` by more than tol. Kills
   the `pass` stubs at `contrastive_kernels.py:507` and `:747` permanently.
3. **Lockstep exactness** — `max|ΔW_lockstep − ΔW_reference| < tol` per layer on
   a seeded fixture.
4. **Checkpoint parity** — checkpointed gradients ≡ plain backprop under dropout
   with RNG preservation.
5. **Binding gate** — baseline-arm activation share of peak ≥50%, else
   `[regime-mismatch]`, not evidence. Enforced by a test over the claim table.
6. **Memory calibration** — measured activation bytes match `L·B·W·4` within 10%
   on a known-depth backprop cell; the guard rejects a deliberately non-binding
   cell. A lock whose fixture cannot fail is a comment.
7. **W2 accuracy floor** — a depth counts only if val accuracy ≥ the pre-registered
   floor; "trainable" must mean "learns".
8. **Identity completeness** — backend path, dtype, optimizer, GPU model, torch
   version, forward-equivalents; missing field = row invalid.
Every lock must fail when its mechanism is removed (TODO46 D26).
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
Venue fit for an all-negative capability outcome: TMLR, or NeurIPS Datasets &
Benchmarks (which wants a reusable suite — aligned with identity cards). Decide
early. The contribution is **rigor and the frontier**, not terra incognita.
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
| — | P1 | published-parity + complexity audit | — | published ±1 pp / σ; declared vs measured class | — | — | T1, T5 |
| — | P2 | memory frontier (3 budgets, Pareto) | — | acc @ matched memory / walltime / params; binding share; forward-eq | — | — | T4a–T4c, T6 |
| — | P3 | routing: local vs STE+aux; bias | — | acc @ matched walltime; bias vs declared reference | — | — | P3 screen |
| — | P3 | estimator taxonomy (after screen) | — | bias vs declared reference; variance; forward-eq | — | — | T7 |
| — | P4 | plasticity + retention (SI/cascade baselines) | — | final-task acc; retention; buffer size; k×params | — | — | T8 |
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
- Start order: **T1 → T4a → T3 → T3b → T6 → T6a**, with T4c/T5 in parallel,
  T4b parallel with T5, T7 conditional on the P3 screen promoting, T8 after T6,
  and T9 trigger-gated.
- Every ticket lands with its measurement recorded where the mechanism lives, not
  only in the log.
- If a steering rule fires, rewrite §0 and §14 in the same commit that records the
  result.
---
## 17. Review answers (resolved)
| Q | Answer |
|---|---|
| 1. Order | T1 (folds T2/T2b) → T4a → T3 → T3b → T6 → T6a, T4c/T5 in parallel; T4b parallel with T5; T7 only if the screen promotes; T8 after T6. |
| 2. Task | CIFAR-10, **fixed 10k-image train subset + full test** (`CostClass.EXPENSIVE`; data cached at `data/cifar-10-batches-py`). Depth/width/batch are hyperparameters and run settings, not registry axes. Synthetic depth task only for instrument acceptance. Normalization fixed across arms: LayerNorm or none — BatchNorm is non-local and breaks batch-1 streaming. W1/W2 are relative claims; the absolute vision bar does not apply. |
| 3. Checkpointing | Backprop-activation checkpointing is not implemented, but the API is already used for settle steps (`core/local_learning/settling.py:403`, `ontology/dynamics/_settle_driver.py:167`). T4b, 1 session; it does not gate T3. |
| 4. P1 scope | Three publishables + the arm P2–P4 uses. Not eight. Add the complexity-audit column; reproduce the published protocol and record σ. |
| 5. D1 timing | Schema + lock written now, D1 after P2, powered for a continuous surrogate or a pre-registered larger n. |
| 6. Triggers | Event triggers, no fixed dates. Memristive-consolidation fires when P4 closes with either verdict. |
| 7. Headline | **Frontier, not depth:** "accuracy per GB at iso-walltime", Pareto dominance, with a stacked memory decomposition. "2× depth" is reported only with the accuracy floor. |
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
**T3 — lockstep recompute.**
- `acceleration/ff_kernels.py` — a two-pass path: pass 1 computes the error and
  discards intermediates; pass 2 recomputes standard and perturbed activations
  layer-by-layer in lockstep and updates W_ℓ immediately. Exact because each
  W_ℓ is used once per pass before its update. Lock against the faithful
  reference (`algorithms/` path) on a seeded fixture.
**T4a — decomposition and guard (hours, not sessions).**
- `core/system_trainer/_resources.py:62` `EpochResource` — add
  `params_mb`, `optimizer_mb`, `activations_mb`, `auxiliary_mb`, `cpu_rss_mb`;
  `EpochResources.stop` already reads CUDA peak, so subtract the known terms and
  record the remainder as auxiliary (never assert 0.0).
- `experiment/kernel/_trainer_utils.py:194-207` — emit the decomposition and
  `activation_share` beside `memory_usage`.
- new lock/test `tests/property/test_memory_binding.py` — calibration within 10%
  of `L·B·W·4`; a deliberately non-binding cell must be rejected.
- CPU RSS: `psutil` is already a declared dependency (`pyproject.toml:100`);
  read `Process().memory_info().rss`. No new dependency.
**T4b — activation checkpointing.**
- new `core/gradient_checkpointing.py` — wrap the **geometry forward**, not
  `system.train_step` (which contains updates); `segments=√L`,
  `preserve_rng_state=True`, `use_reentrant=False` (repo precedent:
  `core/local_learning/settling.py:403`). Parity lock §9.4. `torch.compile`
  interacts with checkpointing: disable compile for ckpt cells or test both, and
  record which was used in the identity card.
**T4c — reuse the existing ladder runner.**
- `validation/backprop_parity.py:729` `run_parity` — add `batch_size`, and add
  `pepita`/`local_goodness` to `_COMPUTE_MATCHED_PORTFOLIO`; the depth loop,
  per-depth baseline, seeds, bootstrap CI, peak memory and FLOPs already exist.
**T3b — hybrid.**
- new `primitives/credit_assignment/hybrid/` — `HybridCredit` owns
  `trunk_credit` + `head_credit` + `split_layer`; dispatches by layer index;
  delegates to `BackpropCredit` (`core/system_trainer/joint.py:122`) for the
  head. One registry row in `_CREDIT_PRIMS`, one `estimator_kind="hybrid"`.
- the head's autograd graph is the only stored activation set; the trunk's
  working set is O(B·W) per layer. Record both in the decomposition, or the
  hybrid's advantage is unmeasured.
- no `System` schema change: `credit` stays a single protocol object.
**T6a — pre-registration.**
- `configs/preregistrations/t93_memory_frontier.json` — a `ThresholdRegistration`
  for the accuracy delta/floor (`metric`, `threshold`, `min_seeds=5`) plus the
  budgets, binding arithmetic, and stop rule as extra keys.
  `ThresholdRegistration.from_dict` ignores extra keys, so a claim-table test
  reads the raw JSON; do not assume the loader enforces the binding gate.
- the Pareto claim is computed from the registered budgets after the run; the
  budgets are fixed before it, so this is not post-hoc.
**T8 — lift, do not rewrite.**
- `core/continual/losses.py:84` `SynapticIntelligence` already implements the
  mechanism; lift it to `ontology/update/` as a U row and reuse
  `create_si_arm` (`core/continual/arms.py:238`). `create_replay_arm` and
  `create_ewc_arm` already exist for P4's baselines.
**T6 — frontier figure.**
- reuse `experiment/analysis/pareto_analysis.py:compute_pareto_frontier`
  (objectives `["accuracy", "peak_bytes"]`, `maximize=[True, False]`).
**T2b — estimator coordinate.**
- `experiment/schema/axis.py:116` — add
  `estimator_kind: Literal["exact","surrogate","local","score_function","forward_mode","zeroth_order","temporal_local","local_supervised","hybrid"]`
  and `bias_reference: Literal["none","exact_tractable","smoothed_objective"]`
  beside `target_kind`.
- `experiment/schema/seed_registries.py:186` `_CREDIT_PRIMS` — each row declares
  its kind; add the declaration lock. The lock applies to **CREDIT rows only**
  (`AxisSpec` is shared across all six axes; other axes default `unspecified`).
  Existing initial mapping: `gradient=exact`;
  `temporal_trace=temporal_local`; the other eight `local` (confirm per
  implementation before locking).
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
| `HybridCredit` (C) | wrapper: local trunk credit + backprop head, dispatch by `split_layer`; `BackpropCredit` already exists | the lead arm cannot compose without it (`System.credit` is one object) | 1–2 sessions |
### P2 — binding arithmetic; trigger-gated, not blocking
| Primitive (axis) | Mechanism | Decision | Trigger | Cost |
|---|---|---|---|---|
| `LocalSupervisionCredit` (C) | greedy layerwise, DGL, InfoPro, periodic global guidance | alternative trunk credit; aux-head params enter the ruler | T6 hybrid trunk below floor or Pareto-dominated | med |
| `FactoredSecondMomentUpdate` (U) | Adafactor | optimizer-memory recovery; moves the binding point | optimizer state ≥40% of peak at the binding point | low |
| `QuantizedStateUpdate` (U) | 8-bit Adam | same; dtype enters identity | same | low |
| `ScheduleFreeUpdate` (U) | schedule-free SGD/Adam | removes schedule asymmetry between arms | a P1 parity gap is traced to schedule choice | low |
**Why not blocking:** the T6 pilot already binds on activations (73% at B=8192,
SGD), so optimizer-state primitives move a boundary that is already crossed.
### P3 — P4 baselines (lands with T8)
| Primitive (axis) | Mechanism | Decision | Stop |
|---|---|---|---|
| `SynapticIntelligenceUpdate` (U) | **lift** `core/continual/losses.py:84` into a U row; online path integral, +1× params | strictly stronger streaming baseline than EWC, cheaper than replay at tiny budgets | SI ≈ EWC → keep EWC, one arm fewer |
| `CascadeSynapsePlasticity` (P) | Benna–Fusi k-state, power-law forgetting | local consolidation; digital control for memristive drift; first multi-state-synapse family on P | price `k×params` first; stop if it exceeds the affordable replay buffer |
| `BayesianOnlineUpdate` (U) | VON natural-gradient variational online | optional if SI is insufficient | admit only if SI fails its stop rule |
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
| Backprop checkpointing is entirely absent | `torch.utils.checkpoint(use_reentrant=False)` is used for settle steps (`core/local_learning/settling.py:403,446,760`) | T4b is a new use of a proven API, not a new dependency |
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
**Remaining execution risks, priced.**
1. **Hybrid integration is the highest-risk ticket.** If the head backward and the
   trunk local update cannot share one `train_step`, T3b needs a custom step that
   bypasses `System.train_step`. Budget the upper 2 sessions; if it exceeds the
   watchdog, fall back to the pure-local arm and record the composition refusal.
2. **`torch.func.jvp` on a composed system.** Many primitives mutate state.
   Scope the forward-mode reference to a pure `nn.Sequential`; if the composed
   system fails, it is a reference, not an arm.
3. **A 64-layer fp32 MLP may not train.** LayerNorm and residual connections are
   the fallback; if the floor is unreachable at L=32, cap the ladder and report
   the measured ceiling rather than forcing depth.
4. **CIFAR-10 flat-MLP accuracy is low.** W1/W2 are relative; say so in the
   pre-registration so a 45–60% row is not read as a capability failure.
5. **`psutil` availability.** Confirmed: declared at `pyproject.toml:100`; read
   `Process().memory_info().rss`. No new dependency.
**Net effect.** The truth pass and the decomposition are one day, not three; the
first falsifier costs ~3 sessions; the hybrid is the critical path to a positive
result, and it now has a ticket, a design, and a fallback.
