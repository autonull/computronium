# TODO93 — Local learning that wins on the hardware people own
**Status:** 2026-11-15 · **draft v2 for review** — nothing implemented, no seed
spent. v1 (composition-wide search, substrate inversion) is condensed into §8 as a
**deferred track with triggers**; nothing from it is discarded.
**Successor to TODO92** (closed: 12 claim-grade rows, breadth gate 8/8, parity on
two families, 0 capability wins).
**The pivot.** TODO92 competed with backprop on backprop's home turf: accuracy at
matched parameters on tasks backprop was built for. That contest has a known
outcome and produced 12 uninformative rows. This plan competes on the axes where
local learning is **structurally** advantaged and users actually feel the cost:
activation memory, streaming, non-differentiable computation, depth at fixed
budget — **on digital hardware**, where the compute is.
**The claim we are trying to earn:** a practitioner with a consumer GPU can
train something local learning makes possible that backprop cannot, at matched
memory and matched compute, with a reproducible command.
---
## 0. Start here
**Three minimum publishable units (MPUs), in order of expected value per session.**
| MPU | Question | Why it is publishable | First evidence |
|---|---|---|---|
| **MPU1 — memory frontier** | At matched peak memory *and* matched compute, does a local rule match or beat backprop (with checkpointing) on accuracy, and reach greater depth/batch at fixed memory? | Every practitioner is memory-bound; nobody publishes memory-matched comparisons systematically | peak-memory instrument + depth ladder |
| **MPU2 — non-differentiable architecture** | Does local credit beat straight-through gradients on an architecture backprop can only approximate (hard routing / discrete selection)? | A capability backprop structurally lacks, and a new architecture class | one architecture, one matched pair |
| **MPU3 — streaming** | On batch-1, non-stationary data with no replay, does local credit retain more at matched memory than backprop + replay? | On-device training, edge, privacy-preserving adaptation | stream protocol + retention metric |
**The credibility gate comes first (P1).** A low number from a weak implementation
is a defect, not a verdict. Before any claim, each credit we intend to publish
must reproduce its *published* number at the published architecture within
tolerance. The README already names this programme ("fair-HPO recovery study");
this plan makes it the gate rather than a footnote.
**What changed from v1 and why**
| v1 | v2 | Reason |
|---|---|---|
| composition-wide search over the 6-axis space | digital-first, three named win conditions | uncapped search has no decision per session; users run digital hardware |
| substrate inversion (photonic, memristive, per-layer placement) as lead | deferred track with triggers (§8) | no user benefit until a digital result exists; keeps the ideas |
| regime affinity as the organizing idea | regime affinity as an **instrument** (§7) | metadata guides sampling; it is not the research question |
| quarterly caps on new primitives | no count caps; cost-priced portfolio (§9) | artificial limits; the binding constraint is time, priced per ticket |
| SEC at session granularity | SEC at **promotion** granularity | screening must be wide and cheap; claims must be expensive and rare |
---
## 1. The scarce-resource thesis
**Fact (structural).** Backprop stores per-layer activations for the backward
pass: O(depth × batch × width). Local rules compute an update from local signals:
O(1) per layer, no stored activation graph. `contrastive_kernels.py` already
implements the "no stored activations" family.
**Fact (honest).** Gradient checkpointing and reversible layers recover much of
that memory for backprop, at ~1.0–1.6× extra compute per step (an extra forward
per checkpoint segment). Any memory claim is therefore **straw** unless it is
also compute-matched. This plan states the baseline explicitly:
`backprop + checkpointing`, same walltime budget.
**Where local keeps an advantage even against checkpointing:**
1. no extra forward to recompute → compute is not traded for memory;
2. no batch required → batch-1 streaming has no checkpoint segment to trade;
3. non-differentiable ops need no surrogate → no bias to correct;
4. no global backward channel → shardable, asynchronous, heterogeneous.
**Where local is expected to lose, stated in advance:** accuracy per parameter on
small, saturated tasks; walltime on matmul-optimised GPUs where the backward pass
is cheap relative to the forward; anything where the global gradient is the only
signal that propagates credit across many layers.
---
## 2. The four win conditions (falsifiable)
| # | Prediction | Falsifier | If false |
|---|---|---|---|
| W1 | At matched peak memory and walltime, a local rule is within 1 pp of backprop+checkpointing on at least one depth ladder, and within 3 pp at 2× depth | matched pair, n=5, L2/20 | memory is not a differentiator on digital → drop MPU1 |
| W2 | At fixed memory, the maximum trainable depth for local ≥ 2× backprop+checkpointing | depth ladder until OOM, both arms | local's per-layer overhead eats the saving → report the measured ratio |
| W3 | On a hard-routing architecture, local credit beats straight-through by ≥2 pp at matched walltime | matched pair, n=5 | STE is sufficient → negative result with the mechanism named |
| W4 | On batch-1 non-stationary streams with no replay, local retention exceeds backprop+replay at matched memory | stream protocol, n=5 seeds | replay is cheap enough that streaming advantage is moot |
**Metric discipline.** Every number carries: peak memory (bytes), walltime,
params, and accuracy. "Matched" always names which budget is matched — memory,
walltime, or params — and never silently swaps one for another.
---
## 3. P1 — The credibility gate (published-parity audit)
**Decision.** Do our implementations of the credits we intend to publish reproduce
their published numbers at their published architecture and schedule?
**Why first.** The user's standard: a reference implementation that is weaker
than the literature is a defect that masquerades as a research finding. It is
also the cheapest session in the plan and it protects every later claim.
**Method, per credit** (start with the ones the gate already calls viable:
`pepita`, `local_goodness`, `random_projections`, `target_inversion`,
`thermodynamic_contrast`, `pc_alm`, `local_contrastive`, `homeostatic`):
1. locate the published architecture, dataset, epochs, and reported accuracy;
2. reproduce at that coordinate with this repo's implementation;
3. record our number, published number, delta, and the exact command;
4. **tolerance:** within ±1 pp or the published run-to-run σ, else defect.
**Deliverable.** `docs/BENCHMARKS.md`: one row per (credit, dataset, architecture)
with published / ours / delta / command / date. This is the "state-of-the-art
reference" artifact — the thing a developer can start from.
**Defect policy.** A gap beyond tolerance opens a defect ticket before any new
measurement. Fix the implementation, do not tune the benchmark. A second failure
after the fix pass is a refusal with a written reason (e.g. dataset difference),
never a quiet exclusion.
**Cost.** ~2–4 sessions; most cells are minutes. No new code expected beyond
runner glue.
---
## 4. P2 — MPU1: the memory frontier
**Instrument first.** The harness needs a **peak-memory** measurement per cell
(activation peak + optimizer state), recorded with the same identity discipline as
accuracy. Without it, no memory claim is possible. Acceptance: a known ladder
shows monotone peak memory vs depth and batch, and checkpointing changes the
backprop curve as expected.
**Design.** Depth × width ladder (e.g. 4/8/16/32/64 layers, width 256/512), one
task with headroom (not a saturated 0.978 task), three arms:
`backprop`, `backprop+checkpointing`, `local` (the best from P1).
**Budgets.** Report accuracy at: (a) matched params, (b) matched peak memory,
(c) matched walltime. Three tables, one figure.
**Claim shape (if W1/W2 hold).** "At 8 GB, local trains 2× the depth of
backprop+checkpointing at equal walltime and within 1 pp accuracy." Pre-register
the threshold and the two budgets before seed 1.
**Stop rule.** If local loses at matched memory *and* matched walltime, the
memory thesis is false; record the measured frontier, close MPU1, and move to
MPU2 (which does not depend on it).
---
## 5. P3 — MPU2: an architecture backprop cannot differentiate
**Why this is the novelty engine.** The only genuinely new capability available
is an architecture whose forward pass has operations with no useful derivative:
hard top-k routing, discrete selection, learned sparse connectivity, spiking
thresholds, in-network memory writes. Local credit does not need a surrogate;
backprop must invent one, and the surrogate is biased.
**Candidate (pick one, not four).** Hard top-k routing where only k of n experts
receive a gradient-bearing path. Baseline: straight-through estimator, same
architecture, same budget. Prediction W3.
**Cheapest falsifier.** Does the local arm learn *at all* (above chance, non-zero
update) on one epoch? Then the matched pair.
**Design.** Router accuracy and end-task accuracy at matched walltime; also report
gradient-bias magnitude of the STE arm (this is the mechanism claim).
**Stop rule.** STE wins by ≥1 pp → publish the negative with bias measurement;
do not tune the local arm to rescue it.
---
## 6. P4 — MPU3: streaming without replay
**Why.** Batch-1, non-stationary data, no replay buffer: the regime where the
memory advantage is structural rather than a trade against checkpointing.
**Protocol.** A sequence of tasks (or a drifting distribution) presented once;
metric = retention of earlier tasks + final-task accuracy, at matched memory.
Arms: local (batch 1) vs backprop+replay (same memory budget for the buffer).
**Cheapest falsifier.** Retention above the backprop+replay arm on one stream.
**Stop rule.** Replay wins on retention at matched memory → close MPU3 and record
the buffer size at which replay saturates.
---
## 7. T0/D1 — The instrument: `regime_affinity`
**Purpose.** Guide sampling toward the mechanism × problem-structure pairs that
are worth measuring, and label cells where a mechanism is out of its intended
regime. **Soft by construction.**
**Schema.** `Regime` `StrEnum`; `AxisSpec.regime_affinity: frozenset[Regime]` beside
`target_kind`; `TaskSpecEnriched.regimes`; `DataOrigin.foreign_regime`;
`comp coverage regimes` (mechanism × regime matrix: measured / empty).
**Primary vocabulary (9).**
| Regime | Structure | Digital-relevant examples |
|---|---|---|
| `memory_limited` | peak activation/optimizer memory binds | deep nets, large batch, consumer GPU |
| `streaming` | batch-1, non-stationary, no replay | edge, on-device, RL rollout |
| `non_differentiable_path` | forward has no useful derivative | hard routing, spiking, discrete selection |
| `temporal_credit` | error/reward delayed beyond 1 step | RL, sequence control |
| `task_switch` | distribution shifts, θ may be frozen | continual, personalisation |
| `local_only` | no global backward channel | edge, asynchronous, multi-device |
| `memory_horizon` | dependency beyond BPTT budget | long sequences, tape |
| `energy_limited` | energy/FLOP budget binds first | mobile, embedded |
| `energy_structured` | solution is a landscape minimum | CSP, Ising, scheduling |
**Commented, for future consideration** (do not add until a task needs one):
`precision_limited` (noisy/low-bit arithmetic binds), `sparse_topology` (fixed
sparse wiring), `scale_limited` (multi-tenant/cluster budget), `adversarial_stream`
(non-stationary with distribution shift *toward* adversarial inputs),
`privacy_limited` (no raw data egress; federated/on-device gradients).
**Invariants (locked).**
1. Affinity **biases a proposal; it never refuses a cell.** Legal compositions
   outside every affinity run and are labelled `foreign_regime`.
2. `--no-affinity` exists. Bias defaults on only if D1 passes.
3. A primitive with an empty affinity set is allowed only with a written reason;
   the lock fails on a silent empty.
4. The lock fails if removing the field leaves proposals unchanged on a seeded
   fixture (TODO46 D26: a fixture that cannot fail is a comment).
5. Affinity never enters a gate verdict: a below-bar foreign cell is
   `[regime-mismatch]`, not a defect.
**D1 — does the bias pay?** Two arms, same task set, same policy seed, 300 cells
each: affinity-guided vs uniform. Metric: promoted cells per 100 screened, and
native-cell share. Decision rule stated before the run: uplift CI excludes 0 and
≥1 extra promoted cell per 100, else **label only, bias off**. Cost ~2 h.
**Cost.** ~1 session for schema + backfill + lock + coverage; D1 ~2 h.
---
## 8. Deferred track (v1, kept with triggers)
Nothing here is discarded; each item re-enters when its trigger fires, and each
keeps its v1 rationale in this section.
| Item | Why it stays | Trigger to re-enter |
|---|---|---|
| **Phase-conjugate credit** (optical) | a credit mechanism physics provides and digital cannot; `U†` realised by phase conjugation, no stored backward weights | a digital claim lands and needs a substrate contrast, or a photonics collaborator appears |
| **Memristive drift as consolidation** | turns a hardware defect into free EWC-like anchoring | a continual-learning claim exists on digital and a device model with retention is available |
| **Per-layer substrate placement** | the only way to express digital front-end + analog back-end | a substrate signal exists; otherwise it is architecture for its own sake |
| **CSP settling (`energy_structured`)** | settling *is* the algorithm on such tasks | a digital memory/streaming result lands, or a practical CSP/scheduling use case appears |
| **Composition-wide sweep** | the 6-axis generator remains the long-run idea | three pieces of evidence exist that composition × regime changes outcomes |
**Why deferred, plainly:** substrate and toy-regime results do not help a user
today, and the digital results above are both faster to obtain and more broadly
useful. If a digital result needs a substrate control, the trigger fires.
---
## 9. Portfolio discipline (no artificial caps)
1. **Every ticket names a decision, a falsifier, a cost, and a stop rule.** That
   is the only admission rule; there is no ticket-count quota.
2. **Cost is priced from a measured pilot**; the watchdog is 2× that price. A
   ticket that exceeds its watchdog is re-priced or killed, not extended.
3. **The portfolio is re-ranked every session** by expected value to the user
   (accuracy, time, energy, memory) ÷ expected cost. Ranking is recorded in §10.
4. **Screening is wide; promotion is rare.** Hundreds of L0 cells allowed; five
   seeds and a pre-registration only after a screen promotes.
5. **A low number is a defect probe first.** Below the published reference in a
   native regime → defect ticket before any verdict (P1's tolerance rule).
6. **Steering rules — the plan changes itself when results say so.**
| Observation | Steering |
|---|---|
| W1/W2 hold | MPU1 becomes the lead claim; MPU2/3 run as follow-ups |
| local loses memory-matched vs checkpointing | close MPU1; the memory thesis is falsified; lead with MPU2/MPU3 |
| STE beats local on routing (W3 false) | publish the negative with bias measurement; drop the non-differentiable track |
| replay saturates streaming (W4 false) | close MPU3; report the saturation buffer size |
| P1 gaps beyond tolerance | defect tickets only; no measurement claims until closed |
| nothing wins | the honest negative: local learning's structural advantage does not convert on digital at matched budgets. Then §8's triggers become the lead |
---
## 10. Scoreboard (update in place; rulers mandatory)
| Date | Track | Measurement | n | Ruler | Verdict | Ticket |
|---|---|---|---|---|---|---|
| — | P1 | published-parity audit | — | published ±1 pp / σ | — | P1 |
| — | P2 | memory frontier (3 budgets) | — | acc @ matched memory, walltime, params | — | P2 |
| — | P3 | hard routing, local vs STE | — | acc @ matched walltime; bias magnitude | — | P3 |
| — | P4 | streaming retention | — | retention @ matched memory | — | P4 |
| — | T0/D1 | affinity A/B | — | promoted cells / 100 screened | — | T0, D1 |
**Progress is one of:** a published-parity reference (P1); a new measured frontier
(P2–P4); a promoted claim; a defect found and fixed by a failing test; a refusal
with a trigger; an affinity that passed or failed its own A/B. **Not progress:**
more cells, more prose, more primitives, a knob swept to pass.
---
## 11. Rules
- **A claim names its budget.** Memory, walltime, or params — never an unstated
  swap.
- **The baseline is the strongest one**, not the most convenient: backprop with
  checkpointing, matched walltime.
- **Every number carries its ruler and its command.**
- **Skeptical default:** below the published reference is a defect first.
- **Pre-register claims only**; screens run freely and stop cheaply.
- **No tuning to pass.** A knob turned to rescue a cell is a defect ticket.
- **The plan stays small.** Rows, not narrative. To add work, add a row with a
  decision and a falsifier.
---
## 12. Handoff contract
- TODO92 stays closed: gate, rulers, registrations, and ledger unchanged.
- Start order: **T0 schema + lock → D1 → P1**; P2 follows P1, and P3/P4 run in
  parallel only if they do not contend for the same measurement instrument.
- Every ticket lands with its measurement recorded where the mechanism lives, not
  only in the log.
- If the steering rules fire, rewrite §0 and §10 in the same commit that records
  the result.

## 13. Review questions
1. **MPU order:** P1 → P2 → P3 → P4, or run P3 (hard routing) earlier because it
   is the clearest novelty and does not depend on memory instrumentation?
2. **Task choice for P2:** which task has real headroom and a memory ladder that
   will not saturate (CIFAR-10 subset? a synthetic depth task? — `breast_cancer`
   at 0.978 is excluded by design)?
3. **Checkpointing baseline:** is `backprop+checkpointing` implemented in this
   repo today, or is that instrumentation work inside P2?
4. **P1 scope:** all eight viable credits, or the three we would actually publish
   (`pepita`, `local_goodness`, `random_projections`)?
5. **D1 timing:** before P1 (instrument first) or after P2 (when there is a
   measured space for affinity to guide)?
6. **Deferred triggers:** are the §8 triggers the right ones to fire, or should
   the substrate track re-enter on a fixed date?
7. **Publishable target:** is MPU1's claim ("2× depth at equal walltime") the
   sharpest one, or is peak-memory-per-accuracy a better headline?
