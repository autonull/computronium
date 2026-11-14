# TODO92 — Refusal, liveness, interaction and evidence (successor to TODO91)

**Status:** 2026-11-14 · §3.0a, §3.0, §3.3, §3.3b, §3.4 and §3.9 closed. The
measurement layer is honest: 3,437 measurements, 93/99 pairs, 0 holes, ~468
claim-shaped L2/n≥5 keys. The first audit found the complex/adam PEPITA pair is
on a **declared-refused pair** (`complex_substrate_real_compute`), not a live
substrate interaction. §3.9 now classifies all 57 declared axis values: **48
live, 1 refused, 2 unavailable, 6 canonical references; 0 undeclared inert.**
§3.7's digital probe is a **cost-adjusted parity, not a win** (details
in §3.7): no non-standard composition yet has a cost-adjusted capability win;
the plan searches for one. Next: **§3.7, then §3.10.**
**TODO91 is closed (2026-11-14)** — its §10 stop condition holds, so this file
is the plan of record. The two gaps it handed over are closed: the
claim-blocking locks group (TODO91 S8) and the regression lane (TODO91 S9). The
open gap list is §3, ordered by what unblocks a number.

**Mission:** grow the *measured* capability of the library, not its paper
surface. TODO91 closed the selection surface (every declared coordinate
resolves and trains somewhere); this plan asks the next question: is every
declared axis value refused with a reason or live, and which live compositions
produce a number that clears their domain's bar?

**Research thesis (2026-11-14, broad).** The library's claim is that
capability is a property of the **composition** of mechanisms, not of backprop
alone. The program has four levels:

1. **Refusal and liveness.** Every declared axis value is either **refused**
   with a measured reason **and a reversal trigger**, or **live** — it changes
   the computation it claims to own at a fixed coordinate and seed. A refusal
   is a hypothesis about the current implementation, not a law. An axis value
   that is neither refused nor live is an inert defect, not a breadth row.
2. **Interaction.** Only live, non-refused pairs enter an interaction — credit ×
   substrate, dynamics × geometry, plasticity × task, update × geometry. The
   interesting claims are interactions; a main-effect tie on one cell is a
   probe, not the thesis.
3. **Capability.** At least one non-standard composition matches or beats the
   standard stack (digital / feedforward / instantaneous / null / gradient /
   adam) at claim grade, on a task that matters, **at matched cost** — the
   primary metric plus walltime, parameter count, and the substrate's energy
   estimate. A win on accuracy at 10× cost is a different claim.
4. **Generality.** A winning composition replicates on at least one second task
   or names its boundary; a single-cell win is a probe, not a library result.
   The thesis is falsified if, after refusal/liveness and interaction mapping,
   every non-standard composition is dominated by the standard stack at matched
   cost.

The first audit result is a **refusal**, not a hidden defect: `complex` is
declared real-arithmetic, and every complex cell is refused by
`complex_substrate_real_compute` (`seed_registries.py`). The PEPITA
digital/complex values are bit-identical because the complex operator on real
weights is the digital matmul — the intended behavior of that row. The plan's
earlier "substrate interaction" was computed on a refused pair; the error was
in the analysis, not the factory. Read the refusal matrix before an
interaction. Only live, non-refused pairs can carry a claim — until a refusal is
reversed.

The complex refusal is **provisional**: it reverses when the complex operator
gains a real-valued phase/noise term and the factory dispatches to it, as the
lock's own comment says. `local_contrastive` is the precedent: declared
unavailable, then N7 wired the label channel and the row returned
(`test_incompatible_cell_refusal_lock.py`). The plan **parks** the complex pair
with that trigger; it does not delete the question, and a reversal is progress.

The first live credit probe is a **cost-adjusted parity, not a win**: PEPITA is
**−0.04 pp** vs gradient on the same update at 1.15× walltime, and −0.38 pp vs the
best backprop at 1.41× walltime (both 55,050 params). The MNIST cell does not
satisfy level 3. The interaction matrix (§3.10) is the search for a cell that
does; if none is found, the thesis is falsified at matched cost.

Every session follows the SEC cycle in `AGENTS.md` (RUN → ANALYZE → FIX →
VERIFY → COMMIT). This file replaces the per-phase TODO cadence: one rolling
plan, tickets ordered by what unblocks a measured number.

---

## 1. The progress rule

A session progresses only if it increases one of:

1. a **live axis** — a forward/step differs from the reference at the same
   seed — or a **refusal with a measured reason and a reversal trigger**,
   including a refused pair removed from breadth; or a **refusal reversed** by
   a measured liveness/interaction result, including the row re-admitted;
2. a domain's best measured metric, with its ruler; a **claim** requires L2,
   n≥5, and a pre-registration — n=3/L1 is screening;
3. the count of **claim-grade matched comparisons or interactions** (L2, n≥5,
   same cell except one axis; pre-registered when the effect is within 1σ of
   its threshold);
4. the count of claim-eligible cells (the code's predicate: L2, gate PASS,
   n≥5, replay hash — `claims.py`);
5. the count of runnable (task × geometry × **error-aware** credit) cells;
6. the count of declared-unavailable rows that became runnable, or a refusal
   with a measured rule.

**Not progress:** files changed, tests restructured, inventory rows added, plan
text written, another coverage cell, another L0 record, another marginal arm
without a stop rule, **a measurement on an inert axis or a refused pair — unless
the refusal is reversed by its trigger**. TODO91's S1d thread is
the worked example: four commits, two attempts, one revert, zero capability.

---

## 2. Measured baseline (2026-11-14)

Corpus (re-measured 2026-11-14 after §3.4): **7,450 PASS records / 443
stores** — **3,437 distinct measurements** (the two numbers differ; see the
ruler note); **28/28 tasks** measured; **93/99** substrate × geometry pairs hold
a measurement (25 refused by a named rule, 19 hold 257 measurements that cannot
count as substrate breadth, **0 unmeasured**). The last hole,
`neuromorphic × graph`, now holds three cells recorded in
`experiments/t92_neuromorphic_graph.duckdb` (§3.4).

**Ruler note (measured 2026-11-14; re-measured by §3.0a).** `scan_corpus` counts
PASS records, and `measurement_key` is unique *within* a store, not across
stores: 441 stores held 7,442 PASS records for **3,431 distinct configurations**
before §3.4 (1,300 keys repeat; max 114); the §3.4 store adds 4 records and 3
measurements. Every earlier "PASS cells" number in TODO85–91 is therefore a
record count, inflated ~2.2× by re-runs. Breadth is quoted as distinct
measurements from here on; "28/28 tasks" survives because it unions task ids.
The report now prints both numbers: `7,450 PASS records = 3,437 distinct
measurements` over 443 readable stores. Pair breadth: **93/99** hold a
measurement, 25 are refused by a named rule (19 of those hold 257 measurements
that cannot count as substrate breadth until the refusal reverses; §3.9),
**0 holes**.

| Domain | Best measured (re-executed 2026-11-14) | Ruler | Target | Verdict |
|---|---|---|---|---|
| Vision | MNIST **0.9789 ± 0.0003** (SD) gradient (digital/euclidean) | n=5, L2/20, val_acc, 10k held out; chance 0.10 | > 0.95 | met, **claim-grade** |
| Vision (local credit) | MNIST **0.9751 ± 0.0020** (SD) PEPITA (digital/adam) | n=5, L2/20, same split; matched gradient **0.9755 ± 0.0023** | > 0.95 | met, **claim-grade**; paired diff −0.0004 at 1.15× walltime — parity, not a win |
| Graph classification | PROTEINS **0.7013 ± 0.0164** (SD) | n=5, L1/100, 223 held out; majority 0.596 | > 0.70 | **screening; marginal** (0.08σ) |
| Node classification | Cora **0.7660 ± 0.0151** (SD) | n=3, L1/100, 500-node public split; majority 0.316 | > 0.75 | **screening; met** (1.06σ) |
| Tabular | wine **1.0000** (record 0.9722) | n=3, L0, 36 held out (resolution 0.0278); majority 0.389 | > 0.90 | **screening; saturated** |
| RL | pendulum **−135.1 ± 9.0** (SD) | n=3, L0/40 epochs, 400 episodes, mean return; chance ≈ −1200 | > −200 | **screening; lane result, credit-inert** |

**Claim grade (measured 2026-11-14).** The corpus holds 3,437 distinct
measurements, but only ~468 distinct keys are L2 with planned n≥5 — the code's
`claim_eligible` floor (`computronium/experiment/evidence/claims.py`). The
vision n=5 L2 cells are claim-grade. The first differentiated matched
comparison is the **digital/adam MNIST pair** (same coordinate and schedule,
seeds 42–46, only the credit differs): gradient **0.9755 ± 0.0023**, PEPITA
**0.9751 ± 0.0020**, paired PEPITA − gradient **−0.0004**, 95% CI [−0.0051,
+0.0044], p=0.84, dz=−0.09. **Cost:** both arms 55,050 params; PEPITA
412 s/seed vs gradient 359 s/seed on CPU (~1.15×). The best backprop
(digital/euclidean) is **0.9789** at 293 s/seed; PEPITA is −0.38 pp at 1.41×.
The digital pair is a **cost-adjusted parity, not a capability win**.
**Retraction (2026-11-14):** the complex/adam pair is **refused** by
`complex_substrate_real_compute`; its cells are bit-identical to digital
because the operator is the digital matmul on real weights. Its records are
among the 257 refused-pair measurements that cannot count; §3.9 audited the
rest (48 live, 1 refused, 2 unavailable). The graph, node, tabular and RL rows
are screening; their "met" is a
domain-bar verdict, not a formal claim.

Provenance for the pre-re-run rows was TODO85–90's session log. Every row now
carries a re-execution: `scripts/probes/t92_baseline_replay.py` rebuilds each
located record's coordinate and schedule and trains it again through the same
evaluator; the recomputed `measurement_key` matches the record's (Cora on all
three seeds), so a number that moves is the system moving, not a different cell.
The re-run holds each verdict: node reproduces seed-for-seed (0.782/0.752/0.764)
and vision within 1e-4, while graph's point estimate moves (record mean 0.6969 →
0.7013) and stays 0.08σ above its bar. Wine's record does not reproduce
(0.9722 → 1.0000 at the same key and seed), so its row is the re-run. RL's old
−1219 row had no replayable record; its new row is the 3-seed 400-episode run
recorded 2026-11-14. **That number is the lane's, not a credit's:** the
trainer optimises geometry parameters with DDPG and never calls the composed
credit, so the cell that produced −135.1 is geometry × substrate. The space now
refuses error-aware credits on RL tasks and keeps only the two `error_blind`
rows (§3.3b). The only open **domain bar** is the graph-classification
marginal; RL's −135.1 is a screening lane result (n=3, L0), and the other met
rows are screening until converted to L2/n≥5 (§3.8). The regression lane is
closed (§3.1).

---

### 3.0a ~~First ticket: the corpus ruler~~ — **closed 2026-11-14**

**Delivered.** `CorpusCoverage` reports `records` and `measurements` side by
side; per-geometry, per-pair and per-task counts dedupe by `measurement_key`;
the report's first line says what the store count counts (readable of found),
and a second line names the ruler. The lock fixture now holds a cell re-run in a
second store: `records=6`, `measurements=5`, and deleting the dedupe moves the
distinct count to 6 — the lock contains the case it exists for.

**Re-measured corpus.** 441 readable stores (441 found, none unreadable), **7,442
PASS records = 3,431 distinct measurements**, 28 tasks, 92/98 pairs measured,
25 refused (19 holding 257 measurements that cannot count), 1 hole:
`neuromorphic × graph`. §2's numbers reproduce.

### 3.0 ~~Second ticket: re-verify the baseline~~ — **closed 2026-11-14**

**Delivered.** `scripts/probes/t92_baseline_replay.py` rebuilds each located
record's coordinate and schedule from the record and trains it again through
`kernel.evaluate_cell`. The anchor seed recomputes the record's
`measurement_key` (Cora matches on all three seeds), so a replay that moves is
the system moving, not a different cell. Twelve cells, 18 min walltime (MNIST
3 × 278 s on its recorded cpu device; the GPU cells are ≤ 40 s).

| Domain | Re-run | n | Ruler | Verdict |
|---|---|---|---|---|
| Vision | 0.9787 ± 0.0009 | 3 | val_acc, 10k held out | reproduced (record 0.9792 at seed 46); met |
| Graph | 0.7013 ± 0.0164 | 5 | 223 held out; majority 0.596 | reproduced as **marginal** (0.08σ) |
| Node | 0.7660 ± 0.0151 | 3 | 500 public-split nodes; majority 0.316 | reproduced, keys match; met (1.06σ) |
| Tabular | 1.0000 ± 0.0000 | 3 | 36 held out (resolution 0.0278); majority 0.389 | **not reproduced** (record 0.9722 at the same key/seed) — row is the re-run; met |
| RL | −1219 (record) | 1 | L0 3 ep, mean reward; credit `homeostatic` (`error_blind`) | **not replayable**; row leaves §2 → §3.3 |

What the re-run corrected: §2's graph row quoted the best seed (0.7040) and a
spread no statistic yields (±0.0071); the confirm run's own 5 seeds mean 0.6969,
and the re-run means 0.7013 — the marginal verdict survives, the point estimate
did not. Wine's record is stale: the same cell now measures 1.0000, so the row
is the re-run, not a reproduced record. Node's 0.766 is the thinnest
screening row (1.06σ above 0.75; not claim-grade: n=3, L1 — §3.8).

`--only` replays a subset; the probe prints per-seed `measurement_key` and
walltime, and never records a run into a store.

### 3.9 ~~Axis refusal/liveness audit~~ — **closed 2026-11-14**

**Delivered.** `scripts/probes/t92_axis_liveness.py` enumerates all 57 declared
axis values and classifies each as reference, refused, live, or unavailable.
Ruler: one seeded `train_step` at the digits task shape (Cora for `graph`),
fingerprinting the **post-step geometry parameters**. The reference is the same
completion with the axis set to the canonical value, composed from the variant's
pre-step weights. Parameters, not `train_loss`: the trainer reports the loss
before the update, and Lion vs Adam are bit-identical in one-step loss but differ
by 6.3e-06 in parameters. A plasticity variant is compared against a **joint**
null, because the 5-D and 6-D system families take different pipeline paths
(measured: `rule_state` looks live vs a 5-D null and is bit-identical vs a joint
null).

| Axis | Declared | Live | Refused | Unavailable | Reference |
|---|---|---|---|---|---|
| Substrate | 9 | 8 | `complex` | — | `digital` |
| Geometry | 11 | 11 | — | — | `feedforward` |
| Dynamics | 8 | 8 | — | — | `instantaneous` |
| Plasticity | 7 | 5 | — | `rule_state`, `substrate_coupled` | `null` |
| Credit | 10 | 10 | — | — | `gradient` |
| Update | 12 | 12 | — | — | `adam` |

**Findings.**

- `complex` stays refused by `complex_substrate_real_compute` (ledger row
  already present).
- `rule_state` is inert: it computes ψ but has no `modulate`, so the standard
  step never applies the selected operator. `substrate_coupled` is a documented
  no-op at the plasticity protocol level (ψ ≡ σ; the substrate owns state
  evolution). Both are now `available=False` in `seed_registries._UNAVAILABLE`
  with a reason and a reversal trigger; the row stays constructible for the
  benchmarks that use it outside the standard step.
- `conflict_adaptive` is live, but only under a credit that writes the
  replacement readout (`local_goodness`, `target_inversion`,
  `random_projections`, `thermodynamic_contrast`). Its closest legal completion
  (`homeostatic`, error-blind) is inert: a readout-replacing law cannot be
  exercised by a credit that never reads the label.
- `lion` is live by parameters although its one-step `train_loss` equals
  Adam's. A loss-based audit would have called an update rule inert.
- `graph` is live on Cora against a flat feedforward reference; the digits shape
  rule never proposes it.

**Locks.** `tests/property/test_axis_liveness_lock.py`: the two unavailable rows
stay declared with reasons/triggers, are bit-identical to a joint null after one
step, `fast_weights` (the live control) is not, `lion` differs from Adam, and
`complex` stays refused. Removing either `_UNAVAILABLE` row or adding `modulate`
to `rule_state` fails the lock.

**Not claimed.** Liveness is one step, not a capability result. Every live row
still needs a matched interaction or claim (§3.7, §3.10).

## 3. Gap list (ordered by what unblocks a number)

**Priority order (2026-11-14, after the first refusal finding):**

1. ~~**§3.9 — axis refusal/liveness audit.**~~ — **closed 2026-11-14.** 57
   declared values = 6 canonical references + 48 live + 1 refused (`complex`) +
   2 unavailable (`rule_state`, `substrate_coupled`); 0 undeclared inert. The
   ledger and locks are in §3.9; the next blocker is §3.7.
2. **§3.7 — PEPITA digital/adam equivalence.** The first credit-axis probe;
   both arms are live digital cells. ~2.1 h CPU for the n=10 confirmation.
3. **§3.10 — interaction matrix.** Dynamics × credit first (the axis with no
   claim-grade evidence), then plasticity × task, update × geometry, credit ×
   substrate on a live non-refused substrate. This is where the broad thesis is
   tested.
4. **§3.3c — gate metric bar.** Makes PASS mean above-bar; every later claim
   depends on it.
5. **§3.2 — one graph readout arm with a stop rule.** The only graph lever left.
6. **§3.8 — claim-conversion backlog.** Convert only the screening rows a claim
   needs; label the rest screening.
7. **§3.6 — batched graph-settle path.** Defer; no domain bar depends on it.
8. **§3.1 — regression claims.** n=1 records; no current claim.

1. ~~**Regression lane**~~ — **closed 2026-11-14 (TODO91 S9).** 3 laws
   generalized (`pepita`, `target_inversion`, the shared output-target
   convention), 3 mechanism rows declared class-only and refused on a
   continuous target; the re-run measured 9/9 PASS. Remaining work is a claim,
   not a lane: `diabetes` 10 and `lorenz_state` 8 PASS records, all n=1 (record
   counts, not yet re-counted as measurements). **Priority 8; no current
   claim.**
2. **Graph classification is marginal (screening, L1; priority 5).** Re-run 0.7013 ± 0.0164
   (SD), n=5, 223 held out: 0.08σ above the 0.70 bar, so the claim rule says
   marginal, not met. **Capacity arm excluded (2026-11-14).** Pre-registered in
   `configs/preregistrations/t92_graph_capacity.json` and run by
   `scripts/probes/t92_graph_capacity.py`: 256-wide 6-layer vs 128-wide 4-layer,
   paired over seeds 42–46, threshold +0.01. Treatment 0.6816 ± 0.0210 vs
   control 0.6960 ± 0.0260: mean diff −0.0143, CI [−0.0395, +0.0036], p=0.41 —
   **FAIL**, capacity is not the lever (train_acc 0.718 shows underfitting, so
   more parameters were the plausible fix; they did not help). The credit axis
   is excluded by record too: the only other
   error-aware graph credit, `random_projections`, holds 0.6233 on PROTEINS.
   Two runs of the same control cell measure 0.7013 and 0.6960, so run noise is
   ~0.005 and the marginal band is wider than the CI suggests. The remaining
   lever is the readout or a different task split — a design change, not a seed
   sweep. The graph builder already reads `pooling` (`mean` or `sum`, in
   `geometry_keys.py`) but no run declares it, so the arm is a declared
   `geometry.pooling` value, not a new primitive. Cost: one arm, ~8 min
   (control measured 39 s/seed). **Run one arm only.** Acceptance: a
   pre-registered paired comparison (sum vs mean, seeds 42–46, threshold +0.01)
   that either moves the row above 0.70 or excludes the readout the way
   capacity was excluded. **Stop rule:** if it fails, close the graph row as
   **at-bar/marginal** and stop; no third capacity/readout arm. If a formal
   claim is ever needed, run the same cell at n=5 L2/100 (§3.8), not another
   lever.
3. ~~**RL**~~ — **closed 2026-11-14: met.** Three seeds × 400 episodes
   (40 × 10) recorded to `experiments/t92_rl_400ep.duckdb`:
   −144.94 / −133.04 / −127.21, mean **−135.1**, SD 9.0, bootstrap CI
   [−144.9, −127.2] against the > −200 bar. Pre-registered in
   `configs/preregistrations/t92_rl_400ep.json`. The pre-DDPG −1219 row was
   stale; the current lane clears the bar. Two findings it produced are filed:
   the credit axis is inert (§3.3b) and gate PASS has no metric bar (§3.3c).
   **Grade:** screening (n=3, L0); the lane result is a trainer/geometry
   result, not a credit claim. Claim-grade conversion is in §3.8.
3b. ~~**RL's credit signal is unbuilt.**~~ — **closed 2026-11-14: refused with
    a measured rule.** DDPG optimises `system.geometry.params` and never calls
    the composed credit: `gradient`, `target_inversion`, `pc_alm`,
    `random_projections`, `local_goodness` and `homeostatic` measured
    bit-identically at 30 episodes (−126.4). The refusal is declared once, as
    the void constraint `rl_credit_must_be_error_blind` in
    `seed_registries.py`: on an RL task only the two rows that declare
    `error_blind=True` (`homeostatic`, `temporal_trace`) compose; an
    error-aware credit is refused with that reason instead of proposing a cell
    whose credit the trainer never applies. The trainer docstring carries the
    note. Lock: `tests/property/test_rl_credit_refusal_lock.py` proves the rule
    is task-scoped and that the pendulum space drops `gradient` while keeping
    the two error-blind rows; deleting the constraint fails it. Reproduced by
    `scripts/probes/t92_rl_credit_identity.py`: `gradient` and `homeostatic`
    both return **−1536.608102** (1 epoch, seed 42, 15 s/cell), bit-identical
    to the recorded positive control. The 400-episode −135.1 row predates the
    rule and remains the lane's geometry × substrate measurement; a
    credit-aware RL update is still unbuilt.
3c. **Gate PASS is defect-free, not above-bar (priority 4).**
    `assess_gate_verdict` reads void/hard/soft defects and an optional seed
    floor; it has no metric threshold, so the positive control PASSed at
    −1536.6. Corpus PASS counts overstate learning on RL and near-chance tasks.
    The documented rule is in §5 ("A PASS record means defect-free, never
    above-bar"), but a rule is weaker than a gate. **Design:** add a per-task
    bar (metric key, direction, value) to the task registry or a
    `configs/pass_bars.json` table; `assess_gate_verdict` reads the record's
    primary metric and returns FAIL (or a named `below_bar` defect) when it
    misses the bar. PASS becomes defect-free **and** above-bar; claim
    eligibility still requires L2/n≥5. **Acceptance:** a lock with a
    near-chance cell that PASSed before and FAILs after; the −1536.6 positive
    control is FAIL; existing claim-grade records are re-assessed or marked
    legacy. **Cost:** one small code change plus its lock; no long run.
    Until it exists, every number in this plan is read from the payload metric
    against its task bar, never from PASS.
4. ~~**`neuromorphic × graph`**~~ — **closed 2026-11-14: measured, not
   refused.** The pair is runnable on node classification. Three L0/1-epoch
   cells on Cora (500-node public split, majority 0.316) recorded to
   `experiments/t92_neuromorphic_graph.duckdb` (run `707b3848`):
   `energy_minimization + gradient` 0.154 (19 s), `energy_minimization +
   temporal_trace` 0.146 (0.03 s), `spike_integration + temporal_trace` 0.130
   (0.07 s); the `digital/graph/instantaneous/gradient` positive control
   measured 0.132. All four PASS; this is **coverage, not a claim** — the
   numbers sit below the majority rate at one epoch and no seed replication
   exists. Corpus: 93/99 pairs, **0 holes**. The graph path is node-mode; the
   batched graph-classification path still fails under settling dynamics, filed
   as §3.6.
5. ~~**Claim-blockers**~~ — **closed 2026-11-14 (TODO91 S8).** Settle telemetry,
   RNG seeding, objective validation and the settle-driver loop are green
   (269 passed in the final gate). No claim made here rests on a known-red
   lock.
6. **Graph classification × settling dynamics (deferred, priority 7).**
    PROTEINS with `energy_minimization` dies on the batched readout (`Expected
    input batch_size (1134) to match target batch_size (32)`; Dynamo reports the
    same 1134-vs-32 mismatch for the fake-tensor call). `spike_integration`
    fails the same way; `diffusion` is refused earlier by
    `diffusion_dynamics_geometry` (requires recurrent). Node-mode Cora works
    (§3.4), so the defect is the pooled batched path, not the pair. **Defer:**
    no domain bar depends on it. Reopen only if a claim needs
    graph-classification × settling. Acceptance when reopened: a graph-batched
    settle path that trains, or a declared refusal naming the shape mismatch.
    Measured cost: <1 s to the failure; a fix is an operator-path change, not a
    tuning run.

7. **Credit-axis probe: PEPITA vs gradient on a matched MNIST cell (priority 2).**
   This is the first credit-axis probe, not the whole thesis: it asks whether a
   local, error-aware credit matches backprop on a live digital pair. The
   existing answer is a **cost-adjusted parity, not a capability win**: **−0.04 pp**
   vs gradient at 1.15× walltime, and −0.38 pp vs the best backprop at 1.41×.
   The discovery data is already in the corpus — `digital / feedforward /
   instantaneous / null / adam`, MNIST, L2/20, seeds 42–46, only the credit
   differs:

   | Arm | Mean ± SD | n | Ruler |
   |---|---|---|---|
   | gradient | **0.9755 ± 0.0023** | 5 | val_acc, 10k held out; L2/20 |
   | PEPITA | **0.9751 ± 0.0020** | 5 | same |
   | paired PEPITA − gradient | **−0.0004**, 95% CI [−0.0051, +0.0044] | 5 | paired by seed; p=0.84, dz=−0.09 |

   **Retraction (2026-11-14):** the complex/adam pair is **not** a substrate
   interaction. `complex` is declared real-arithmetic and every complex cell is
   refused by `complex_substrate_real_compute`; the complex and digital PEPITA
   cells are bit-identical because the operator is the digital matmul on real
   weights. The pair is refused, not evidence; §3.9 confirms the refusal. Do
   not use it as a claim.

   **Best-backprop check (secondary):** PEPITA digital/adam **0.9751** vs
   gradient digital/euclidean **0.9789** (the best backprop cell), paired over
   the same seeds: **−0.0038**, 95% CI [−0.0064, −0.0012], p=0.015. The update
   differs, so this is a non-inferiority check, not a matched credit claim; the
   gap is 0.38 pp, inside the ±0.01 margin (±1 pp). It answers the "inferior
   optimizer" objection: PEPITA is within 1 point of the best backprop
   configuration, at 1.41× walltime — a cost-adjusted loss, not parity.

   **Liveness prerequisite (closed 2026-11-14):** §3.9 classifies every
   substrate value; 8/9 are live and `complex` is refused. The digital pair is
   live — PEPITA and gradient differ at the same seed — so the credit probe is
   not blocked by the complex refusal.

   **Confirmation:** pre-register a two-sided equivalence claim with margin
   **±0.01**, α=0.05, `min_seeds=10`; run **new seeds 47–56** on both arms (the
   existing 42–46 are discovery, not confirmation). Primary decision: the 95%
   bootstrap CI of the paired difference lies inside ±0.01; report the
   superiority p vs 0 as secondary. Secondary endpoint: PEPITA digital/adam vs
   gradient digital/euclidean, non-inferiority margin 0.01, descriptive (the
   update differs). **Prerequisite:** add
   `PairedComparison.passes_equivalence(margin)` (or an
   `EquivalenceRegistration` beside `ThresholdRegistration`) to
   `computronium/validation/preregistration.py`; the existing `passes` is a
   one-sided superiority test and is the wrong predicate for a tie. Commit
   `configs/preregistrations/t92_pepita_mnist.json` **before** the run.
   **Cost:** measured 360 s/seed (gradient) and 412 s/seed (PEPITA) on CPU at
   L2/20; 10 new seeds × 2 arms ≈ **2.1 h**, background. GPU was not faster on
   the recorded PEPITA seed (395 s). **Acceptance:** prereg committed before the
   run; records in `experiments/t92_pepita_mnist.duckdb`; a scoreboard row with
   n=10, the CI, and the ruler; if it passes, the vision row gains a
   **cost-adjusted parity** claim (same update, 1.15× walltime), not a
   capability win; §3.10 then searches for a cell where a non-standard axis
   wins at matched cost. **Stop rule:** if the CI leaves the ±0.01
   band, report the measured boundary and do not run a third credit on MNIST;
   move the local-credit question to a harder task. **If it passes:** scale the
   same matched design to a harder task (CIFAR-10 or a deeper geometry) before
   claiming general parity; MNIST parity is necessary, not sufficient.

8. **Claim-conversion backlog (priority 6).** The code's `claim_eligible` is
   L2 + n≥5; these rows are screening. Convert only what a claim needs:

   | Row | Current | To claim | Cost | Priority |
   |---|---|---|---|---|
   | Node Cora | 0.766 n=3 L1/100 | n=5 L2/100 | measure first; ~5–10 min | after §3.7 |
   | Graph PROTEINS | 0.701 n=5 L1/100 | n=5 L2/100 | ~10 min | after §3.2 |
   | RL pendulum | −135.1 n=3 L0/40 | n=5 same schedule | ~60 min | only if the lane claim matters |
   | Tabular wine | 1.0 n=3 L0 | replace the task | new loader | low; wine is saturated |

   The tabular row is the weakest claim carrier: 36 held out, resolution
   0.0278, saturated at 1.0, and the record did not reproduce. A harder tabular
   task (`breast_cancer`/`diabetes`) with ≥100 held out is the right carrier; do
   not call wine a capability result.

9. **Axis refusal/liveness audit (priority 1).** Read the refusal matrix before
   composing a comparison. `complex` is the worked example: it is declared
   real-arithmetic (`SubstrateConfig.complex` with `substrate_type=DIGITAL`),
   and `complex_substrate_real_compute` refuses every complex cell. The complex
   PEPITA records are legacy refused-pair measurements — 93 complex ×
   feedforward measurements cannot count as substrate breadth. The factory behavior
   is intentional; the error was computing an interaction from refused records.
   **Audit design:** for each axis value, classify it:
   - **refused** — a void constraint names the reason **and the reversal
     trigger**; its records cannot count as breadth or enter a claim until the
     trigger fires;
   - **live** — the value changes the first forward/loss/step from the reference
     at the same seed;
   - **inert** — neither; a defect. Fix it, park it with a named reversal test,
     or declare it unavailable with a trigger.
   Cover all six axes with a cell the value can act on: substrate (8 variants),
   geometry (10), dynamics (7), plasticity (6), credit (9), update (11).
   Deterministic mode where noise would mask the comparison. Error-blind credits
   are live if their update differs from the reference; their null error signal
   is a declared contract. Probe: `scripts/probes/t92_axis_liveness.py`.
   **Acceptance:** a refusal/live/inert matrix; every refused row names its
   rule **and reversal trigger**; every inert row is fixed, parked with a test,
   or unavailable with a trigger; a liveness lock fails when a live variant
   becomes identity; the corpus breadth count excludes refused rows until
   reversed. **Refusal review:** at each round close, re-check every trigger; a
   reversal re-admits the row and is progress (the `local_contrastive`
   precedent). **Registry:** add `revisit: str | None` beside
   `unavailable_reason`/`description`; the audit fills it; the refusal review
   reads it. The trigger lives on the row, not in a second plan table.
   **Cost:** minutes, not hours — one forward/step per pair.

10. **Axis-interaction matrix (priority 3).** After refusal/liveness, the claims
    are interactions, not main effects. The axis evidence shows dynamics,
    plasticity and update have **no** claim-grade evidence, so start there:
    - **dynamics × credit:** `energy_minimization` vs `instantaneous` ×
      gradient/PEPITA, on a task where settling is constitutive; report val_acc
      **and** walltime per cell. First cell: Cora node classification
      (`energy_minimization` is legal and settling is iterative); if the effect
      is null, try a scientific state-prediction task.
    - **plasticity × task:** `fast_weights`/`routing` vs `null` on a
      memory/continual task; report retention and task accuracy.
    - **update × geometry:** `muon`/`lion` vs `adam` on feedforward/graph;
      report val_acc and param budget.
    - **credit × substrate:** PEPITA vs gradient on digital and a **live,
      non-refused** substrate (candidates: analog, ternary, sparse, memristive,
      neuromorphic with compatible dynamics; `complex` is refused today — its
      reversal trigger is a real-valued phase/noise term, and if it fires the
      pair re-enters). 2×2, seeds 47–56, difference-in-differences
      `(PEPITA−gradient)_substrate − (PEPITA−gradient)_digital`, L2/20. A null
      interaction is a named verdict (the local credit is substrate-invariant).
    Each is a pre-registered L2/n≥5 2×2 at matched cost; one interaction at a
    time, not a sweep. Every cell reports the primary metric, walltime,
    parameter count, and the substrate's energy estimate; the interaction is
    judged on the metric at matched cost. Choose a task where the axis is
    constitutive: dynamics → energy-based inference, plasticity →
    memory/continual, credit → vision, update → optimization-sensitive geometry.
    Acceptance: a claim-grade interaction table; a null interaction is a
    verdict, not a failure.

---

## 4. Scoreboard (update in place; never rewrite history)

| Date | Domain | Best | n | Ruler | Status | Ticket |
|---|---|---|---|---|---|---|
| 2026-11-14 | regression | — | 1 | MSE, target-variance units | not claim-eligible | §3.1 |
| 2026-11-14 | regression | lane closed: 3 laws + 3 refusals | 1 | same | cells exist (10 + 8 PASS), claim needs n≥3 | §3.1 (closed) |
| 2026-11-14 | corpus breadth | 3,431 measurements (7,442 records) | 441 stores | distinct `measurement_key`; 92/98 pairs, 1 hole | instrument prints both; §2 reproduces | §3.0a (closed) |
| 2026-11-14 | vision | MNIST 0.9787 ± 0.0009 (SD) | 3 | val_acc, 10k held out; chance 0.10 | reproduced; met | §3.0 (closed) |
| 2026-11-14 | graph classification | PROTEINS 0.7013 ± 0.0164 (SD) | 5 | 223 held out; majority 0.596 | reproduced; **marginal** (0.08σ) | §3.2 |
| 2026-11-14 | graph classification | 256×6 capacity arm 0.6816 ± 0.0210 | 5 | paired vs 128×4 control 0.6960; same seeds | pre-registered diff −0.0143, CI [−0.0395, +0.0036], p=0.41 — **arm rejected** | §3.2 |
| 2026-11-14 | node classification | Cora 0.7660 ± 0.0151 (SD) | 3 | 500 public-split nodes; majority 0.316 | reproduced; met (1.06σ) | §3.0 (closed) |
| 2026-11-14 | tabular | wine 1.0000 (record 0.9722 did not reproduce) | 3 | 36 held out (resolution 0.0278); majority 0.389 | re-run is the measurement; met | §3.0 (closed) |
| 2026-11-14 | RL (credit axis) | six credits identical: mean_reward −126.4 | 1 | 30 episodes, L0 | credit inert — one value for all six | §3.3b |
| 2026-11-14 | RL (credit axis) | `gradient` = `homeostatic` = −1536.608102 | 2 credits | 1 epoch, seed 42; 15 s/cell | error-aware credits **refused** on RL; only `error_blind` rows compose | §3.3b (closed) |
| 2026-11-14 | RL | pendulum −135.1 ± 9.0 (SD) | 3 | 400 episodes (40×10), mean return; chance ≈ −1200 | CI [−144.9, −127.2] vs −200; **met** | §3.3 (closed) |
| 2026-11-14 | corpus breadth | 3,437 measurements (7,450 records) | 443 stores | distinct `measurement_key`; 93/99 pairs, **0 holes** | §3.4 closes the last hole | §3.4 (closed) |
| 2026-11-14 | neuromorphic × graph (Cora) | 0.1540 / 0.1460 / 0.1300 | 1 seed each | 500-node public split; majority 0.316; L0/1 epoch | **coverage, not a claim** (below majority; no replication) | §3.4 (closed) |
| 2026-11-14 | axis liveness | 57 declared = 6 reference + 48 live + 1 refused + 2 unavailable | 57 values | one seeded `train_step`, post-step geometry fingerprint (digits 8×8; Cora for `graph`) | **0 undeclared inert**; `complex` refused, `rule_state`/`substrate_coupled` unavailable | §3.9 (closed) |
| 2026-11-14 | graph classification × settling | failure: 1134 vs 32 | 1 | PROTEINS batch, node-major readout | batched path dies under energy_minimization/spike; node-mode works | §3.6 |
| 2026-11-14 | vision (claim-grade) | matched digital/adam: gradient 0.9755 ± 0.0023 vs PEPITA 0.9751 ± 0.0020 (best gradient 0.9789, digital/euclidean) | 5 | L2/20, 10k held out; chance 0.10 | paired PEPITA−gradient −0.0004, CI [−0.0051, +0.0044], p=0.84 | §3.7 (discovery) |
| 2026-11-14 | vision (secondary) | complex/adam PEPITA vs gradient | 5 | L2/20, same split | **retracted**: `complex_substrate_real_compute` refuses every complex cell; PEPITA cells bit-identical | §3.9 (refused) |

One row per domain per measurement; a row is superseded, never edited.
Earlier "met" rows are **screening verdicts**; the formal claim bar is L2/n≥5
(`computronium/experiment/evidence/claims.py`). Rows written before the
refusal/liveness phase say "claim needs n≥3"; the current bar is L2/n≥5 (§5).
The vision n=5 L2 rows are the first claim-grade cells; §3.7 is the first
pre-registered matched claim.

### Claim-grade ledger (L2, n≥5, same cell except one axis)

| Date | Comparison | n | Ruler | Cost | Result | Status |
|---|---|---|---|---|---|---|
| 2026-11-14 | MNIST digital/adam: PEPITA vs gradient | 5 | val_acc, 10k held out; L2/20 | 55,050 params; PEPITA 412 s vs gradient 359 s (~1.15×) | −0.0004, 95% CI [−0.0051, +0.0044], p=0.84, dz=−0.09 | discovery; §3.7 confirms n=10 |
| 2026-11-14 | MNIST complex/adam: PEPITA vs gradient | 5 | same | — | **retracted**: `complex_substrate_real_compute` refuses every complex cell; PEPITA cells bit-identical | **refused**, not an interaction; §3.9 |
| 2026-11-14 | MNIST best-backprop check: PEPITA digital/adam vs gradient digital/euclidean | 5 | val_acc, 10k held out; L2/20 | 55,050 params; PEPITA 412 s vs gradient 293 s (~1.41×) | −0.0038, 95% CI [−0.0064, −0.0012], p=0.015 | secondary; cost-adjusted loss |

### Refusal/liveness ledger (axis value vs reference, same seed)

| Date | Axis | Variant | Reference | Observation | Verdict | Reversal trigger |
|---|---|---|---|---|---|---|
| 2026-11-14 | substrate | `complex` | `digital` | PEPITA val_acc/train_acc bit-identical per seed (42–46); `complex_substrate_real_compute` refuses every complex cell | **refused**, not live; records cannot count until reversed; §3.9 | complex operator gains a real-valued phase/noise term and `substrate_from_config` dispatches to it |
| 2026-11-14 | plasticity | `rule_state` | `null` (joint) | post-step geometry bit-identical across 12 declared completions; no `modulate` applies ψ | **inert** → unavailable; `_UNAVAILABLE` reason | a trainer applies `apply_operator` (the Z3 frozen-θ loop) |
| 2026-11-14 | plasticity | `substrate_coupled` | `null` (joint) | post-step geometry bit-identical across 12 declared completions; primitive is a documented no-op | **inert** → unavailable; `_UNAVAILABLE` reason | a substrate carries a separate state σ through the joint transition and the standard step reads it |
| 2026-11-14 | all axes | 51 non-reference values | canonical stack | 48 live, 1 refused, 2 unavailable, 0 undeclared inert | audit closed; one step is a liveness ruler, not a claim | re-run `scripts/probes/t92_axis_liveness.py` after a declaration change; a fired trigger is `stale-unavailable` |

**Claim-shaped keys.** 3,437 distinct measurements, but only ~468 distinct keys
are L2 with planned n≥5; the achieved-seed count is lower. Breadth is a floor,
not a claim count. The ledger is the claim count.

**Liveness caveat.** The 93/99 pair count counts declared substrate values, not
live substrates. §3.9 now classifies every declared axis value; pair breadth is
still a **coverage floor**, not evidence that a pair composes. The live count is
48/51 non-reference values (1 refused, 2 unavailable). A pair enters an
interaction only when both its axes are live and the cell is not refused.

**Axis evidence (2026-11-14).** The six-axis program, by what is actually
claim-grade:

| Axis | Liveness (2026-11-14) | Claim-grade evidence | Gap |
|---|---|---|---|
| Substrate | 8/9 live; `complex` refused | digital only | no live non-digital matched comparison |
| Geometry | 11/11 live | vision/graph/node screening | graph marginal; node n=3 |
| Dynamics | 8/8 live | none | best cells are instantaneous; no matched settling claim |
| Plasticity | 5/7 live; `rule_state`, `substrate_coupled` unavailable | none | no matched plasticity × task claim |
| Credit | 10/10 live | PEPITA digital/adam discovery | graph 2 error-aware; RL refused; most credits L0/1 |
| Update | 12/12 live | none | no matched update × geometry claim |

"Liveness" is the §3.9 one-step parameter fingerprint, not a PASS record or a
claim-grade cell; the claim-grade column is the evidence count. The gaps are the
program.

---

## 5. Rules for this plan

- **One plan, rolling.** No TODO93 per phase. Tickets enter §3 from a measured
  failure or a missing row, and leave when the number moves.
- **A ticket closes on a number or a named verdict**, never on a defect count.
- **No test restructuring.** Tests are a means; a test change is not progress.
  Duplication that costs walltime may be removed only when the replacement is
  mutation-checked.
- **Session logs live in commit messages.** The plan holds the scoreboard
  and the ticket list; it does not accumulate narrative. TODO91's length is
  the counter-example, not the template.
- **Every number carries its ruler** and the chance/majority rate it beats.
  Corpus breadth is **distinct measurements**, never PASS records (§3.0a).
- **A PASS record means defect-free, never above-bar** (measured 2026-11-14: a
  −1536.6 RL cell PASSed; §3.3c). A claim reads the metric and its ruler.
- **An axis the lane never applies is refused, not swept.** The RL credit axis
  names its refusal in one constraint (`rl_credit_must_be_error_blind`) and
  keeps only the rows whose contract matches the lane; a second table of
  "inert" credits is a defect (§3.3b).
- **Refusals are provisional.** A refusal is a measured hypothesis, not a law.
  Every refusal names a **reversal trigger**; when it fires, re-run the
  liveness test and re-admit the row. `local_contrastive` is the precedent
  (unavailable until N7 wired the label channel). A refusal without a trigger
  is a corner. Until reversal, a measurement on a refused pair cannot count as
  breadth or enter a claim (the complex PEPITA pair;
  `complex_substrate_real_compute`).
- **A non-refused axis value that returns bit-identical output is inert.** Fix
  it, park it with a test, or declare it unavailable with a trigger (§3.9). A
  composition claim names the live, non-refused axes it depends on; if one is
  refused or inert, retract the claim until it reverses (§3.7's complex pair).
- **A coverage cell is not a claim.** A measured pair with n=1, or one below
  its majority rate, closes a hole and enters the scoreboard with that ruler; it
  never enters §2's "best measured" row (§3.4).
- **Claims need L2, n≥5, and a preregistration.** n=3/L1 is screening; the
  code's `claim_eligible` (L2, PASS, n≥5, replay hash) is the authority
  (`configs/preregistrations/`). A domain row called "met" at n=3 or L1 is a
  screening verdict, not a claim.
- **A tie needs an equivalence predicate.** `PairedComparison.passes` is a
  one-sided superiority test; it is the wrong predicate for "matches." An
  equivalence claim reads the two-sided CI against a pre-registered margin
  (`passes_equivalence`; §3.7). Report the superiority p as secondary.
- **A marginal arm gets a stop rule before it runs.** One pre-registered arm
  per lever; if it misses its threshold, record the verdict, close the lever,
  and move on. No third capacity/readout sweep (§3.2).
- **A live interaction claim outranks a domain bar.** A 0.08σ domain gap is
  lower value than a matched comparison that tests a live interaction; spend
  the next long run on the latter (§3.7, §3.10).
- **A capability claim is metric at matched cost.** An accuracy tie at 1.4×
  walltime or 10× energy is not a win; report metric, walltime, parameter count,
  and energy beside every interaction. The standard stack is the cost reference
  (§3.10).
- **A surface defect found here is fixed here only if it blocks the number**;
  otherwise it files into §3 with a measured reason (TODO91 is closed and takes
  no new rows).

---

## 6. Handoff contract

- TODO91 is closed (2026-11-14): its stop condition holds, its §8
  claim-blocking group is green and its regression lane is closed. This file is
  the plan of record.
- §3.0a and §3.0 are closed (2026-11-14): the instrument prints records and
  distinct measurements, and every §2 row carries a re-execution whose
  `measurement_key` matches its located record. §3.2's capacity arm is rejected
  by pre-registered paired comparison; the graph row stays marginal and its next
  lever is the readout, not capacity or credit. §3.3 is closed with a number:
  RL −135.1 (n=3, 400 episodes) clears −200, and that number is geometry ×
  substrate because the credit axis is inert on the lane.
- §3.3b is closed (2026-11-14) as a refusal with a measured rule: the space
  refuses error-aware credits on RL tasks (`rl_credit_must_be_error_blind`) and
  keeps the two `error_blind` rows; the probe reproduces the identity
  (`gradient` = `homeostatic` = −1536.608102 at 1 epoch). A credit-aware RL
  update remains unbuilt and is the only way to reopen the axis.
- §3.4 is closed (2026-11-14) with measurements: `neuromorphic × graph` runs on
  Cora (node mode) at L0/1 epoch in three cells, so the corpus holds **93/99**
  pairs and **0 holes**. The numbers are coverage, not a claim. The batched
  graph-classification path under settling dynamics still fails (1134-vs-32
  shape mismatch), filed as §3.6.
- The **refusal/liveness phase** ran (2026-11-14). The first audit finding is a
  refusal, not a factory defect: `complex` is declared real-arithmetic and
  every complex cell is refused by `complex_substrate_real_compute`. The PEPITA
  complex/digital cells are bit-identical because the operator is the digital
  matmul; that pair is one of the 257 refused-pair measurements that cannot
  count as substrate breadth until the refusal reverses. §3.9 classified every
  axis value as refused, live, or unavailable before §3.10 composes an
  interaction. Every refusal carries a **reversal trigger**, and a refusal
  review at round close re-admits rows whose trigger fired;
  `local_contrastive` is the precedent.
- The **credit-axis probe** remains valid on the live digital pair: PEPITA
  0.9751 ± 0.0020 vs gradient 0.9755 ± 0.0023 (n=5, L2/20, seeds 42–46; paired
  −0.0004, 95% CI [−0.0051, +0.0044], p=0.84). Cost: 55,050 params; PEPITA
  412 s/seed vs gradient 359 s (~1.15×), and vs the best backprop 293 s
  (~1.41×) at −0.38 pp. It is a **cost-adjusted parity, not a capability win**;
  §3.7 adds the equivalence predicate and runs seeds 47–56 (~2.1 h CPU), and
  §3.10 searches for a cell where a non-standard axis wins at matched cost.
- §3.9 is closed (2026-11-14): all 57 declared axis values are classified (48
  live, 1 refused, 2 unavailable, 6 references); the two inert plasticity rows
  are declared unavailable with reversal triggers, and the lock proves the
  measurement. The audit is one step, not a capability claim.
- Open work, in priority order: §3.7 PEPITA digital equivalence; §3.10
  interaction matrix; §3.3c gate metric bar; §3.2 one graph readout arm with a
  stop rule; §3.8 claim-conversion backlog; §3.6 batched graph-settle
  (deferred); §3.1 regression claims (n=1).
- A surface defect found here is fixed here only if it blocks the number;
  otherwise it files into this plan's §3 with a measured reason. TODO91 takes
  no new work.
