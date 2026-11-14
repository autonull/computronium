# TODO92 — Breadth and evidence (successor to TODO91)

**Status:** 2026-11-14 · §3.0a, §3.0, §3.3, §3.3b and §3.4 closed. The
measurement layer is honest: 3,437 measurements, 93/99 pairs, 0 holes, and
~468 claim-shaped L2/n≥5 keys. The next phase is **claim conversion**. The
highest-value result already in the corpus is a matched MNIST pair — PEPITA
**0.9751 ± 0.0020** vs gradient **0.9755 ± 0.0023** (n=5, L2/20, paired diff
−0.0004, 95% CI [−0.0051, +0.0044]) — a local credit matches backprop within
0.5 accuracy points. §3.7 pre-registers the n=10 confirmation. Graph stays
marginal with one readout arm and a stop rule (§3.2); the gate metric bar
(§3.3c) makes PASS mean above-bar. Next: **§3.7, then §3.3c, then §3.2.**
**TODO91 is closed (2026-11-14)** — its §10 stop condition holds, so this file
is the plan of record. The two gaps it handed over are closed: the
claim-blocking locks group (TODO91 S8) and the regression lane (TODO91 S9). The
open gap list is §3, ordered by what unblocks a number.

**Mission:** grow the *measured* capability of the library, not its paper
surface. TODO91 closed the selection surface (every declared coordinate
resolves and trains somewhere); this plan asks the next question: which
combinations produce a number that clears its domain's bar, and what does it
take to get the rest there.

**Research thesis (2026-11-14).** The library's differentiated claim is not
that it can train MNIST; it is that a local, error-aware credit can match
backprop on a matched cell. The corpus's first claim-grade comparison points
that way: PEPITA **0.9751 ± 0.0020** vs gradient **0.9755 ± 0.0023** (n=5,
L2/20, paired diff −0.0004, 95% CI [−0.0051, +0.0044]). The next long run
should decide that claim, not chase a 0.08σ domain bar. A backprop-only result
is table stakes; a PEPITA parity claim is the library's reason to exist.

Every session follows the SEC cycle in `AGENTS.md` (RUN → ANALYZE → FIX →
VERIFY → COMMIT). This file replaces the per-phase TODO cadence: one rolling
plan, tickets ordered by what unblocks a measured number.

---

## 1. The progress rule

A session progresses only if it increases one of:

1. a domain's best measured metric, with its ruler; a **claim** requires L2,
   n≥5, and a pre-registration — n=3/L1 is screening;
2. the count of **claim-grade matched comparisons** (L2, n≥5, same cell except
   one axis; pre-registered when the effect is within 1σ of its threshold);
3. the count of claim-eligible cells (the code's predicate: L2, gate PASS,
   n≥5, replay hash — `claims.py`);
4. the count of runnable (task × geometry × **error-aware** credit) cells;
5. the count of declared-unavailable rows that became runnable, or a refusal
   with a measured rule.

**Not progress:** files changed, tests restructured, inventory rows added, plan
text written, another coverage cell, another L0 record, another marginal arm
without a stop rule. TODO91's S1d thread is the worked example: four commits,
two attempts, one revert, zero capability.

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
that cannot count as substrate breadth), **0 holes**.

| Domain | Best measured (re-executed 2026-11-14) | Ruler | Target | Verdict |
|---|---|---|---|---|
| Vision | MNIST **0.9789 ± 0.0003** (SD) gradient (digital/euclidean) | n=5, L2/20, val_acc, 10k held out; chance 0.10 | > 0.95 | met, **claim-grade** |
| Vision (local credit) | MNIST **0.9751 ± 0.0020** (SD) PEPITA (digital/adam) | n=5, L2/20, same split; matched gradient **0.9755 ± 0.0023** | > 0.95 | met, **claim-grade**; paired diff −0.0004 |
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
+0.0044], p=0.84, dz=−0.09. The complex/adam pair is secondary: **+0.0043**,
CI [−0.0003, +0.0089], p=0.06 — a substrate interaction, not general
superiority. §3.7 pre-registers the n=10 confirmation. The graph, node,
tabular and RL rows are screening; their "met" is a domain-bar verdict, not a
formal claim.

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

## 3. Gap list (ordered by what unblocks a number)

**Priority order (2026-11-14, after §3.4):**

1. **§3.7 — pre-register and run the matched PEPITA vs gradient claim.** It
   tests the differentiated axis; ~2.1 h CPU; highest information per hour.
2. **§3.3c — gate metric bar.** Makes PASS mean above-bar; every later claim
   depends on it.
3. **§3.2 — one graph readout arm with a stop rule.** The only graph lever left
   after capacity; do not run a third arm.
4. **§3.8 — claim-conversion backlog.** Convert only the screening rows a claim
   needs; label the rest screening.
5. **§3.6 — batched graph-settle path.** Defer; no domain bar depends on it.
6. **§3.1 — regression claims.** n=1 records; no current claim.

1. ~~**Regression lane**~~ — **closed 2026-11-14 (TODO91 S9).** 3 laws
   generalized (`pepita`, `target_inversion`, the shared output-target
   convention), 3 mechanism rows declared class-only and refused on a
   continuous target; the re-run measured 9/9 PASS. Remaining work is a claim,
   not a lane: `diabetes` 10 and `lorenz_state` 8 PASS records, all n=1 (record
   counts, not yet re-counted as measurements). **Priority 6; no current
   claim.**
2. **Graph classification is marginal (screening, L1).** Re-run 0.7013 ± 0.0164
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
3c. **Gate PASS is defect-free, not above-bar (priority 2).**
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
6. **Graph classification × settling dynamics (deferred, priority 5).**
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

7. **Claim: PEPITA matches backprop on a matched MNIST cell (priority 1).**
   This is the highest-value experiment in the plan: it tests the
   differentiated axis, not another domain bar. The discovery data is already
   in the corpus — `digital / feedforward / instantaneous / null / adam`, MNIST,
   L2/20, seeds 42–46, only the credit differs:

   | Arm | Mean ± SD | n | Ruler |
   |---|---|---|---|
   | gradient | **0.9755 ± 0.0023** | 5 | val_acc, 10k held out; L2/20 |
   | PEPITA | **0.9751 ± 0.0020** | 5 | same |
   | paired PEPITA − gradient | **−0.0004**, 95% CI [−0.0051, +0.0044] | 5 | paired by seed; p=0.84, dz=−0.09 |

   The complex/adam pair is a **secondary** observation: PEPITA **+0.0043**,
   CI [−0.0003, +0.0089], p=0.06 — a substrate interaction, not general
   superiority. Do not use it as the primary claim.

   **Best-backprop check (secondary):** PEPITA digital/adam **0.9751** vs
   gradient digital/euclidean **0.9789** (the best backprop cell), paired over
   the same seeds: **−0.0038**, 95% CI [−0.0064, −0.0012], p=0.015. The update
   differs, so this is a non-inferiority check, not a matched credit claim; the
   gap is 0.38 pp, inside the ±0.01 margin. It answers the "inferior optimizer"
   objection: PEPITA is within 1 point of the best backprop configuration, not
   only of gradient on its own update.

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
   `configs/preregistrations/t93_pepita_mnist.json` **before** the run.
   **Cost:** measured 360 s/seed (gradient) and 412 s/seed (PEPITA) on CPU at
   L2/20; 10 new seeds × 2 arms ≈ **2.1 h**, background. GPU was not faster on
   the recorded PEPITA seed (395 s). **Acceptance:** prereg committed before the
   run; records in `experiments/t93_pepita_mnist.duckdb`; a scoreboard row with
   n=10, the CI, and the ruler; if it passes, the vision row gains a claim no
   backprop-only library can make. **Stop rule:** if the CI leaves the ±0.01
   band, report the measured boundary and do not run a third credit on MNIST;
   move the local-credit question to a harder task. **If it passes:** scale the
   same matched design to a harder task (CIFAR-10 or a deeper geometry) before
   claiming general parity; MNIST parity is necessary, not sufficient.

8. **Claim-conversion backlog (priority 4).** The code's `claim_eligible` is
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
| 2026-11-14 | graph classification × settling | failure: 1134 vs 32 | 1 | PROTEINS batch, node-major readout | batched path dies under energy_minimization/spike; node-mode works | §3.6 |
| 2026-11-14 | vision (claim-grade) | matched digital/adam: gradient 0.9755 ± 0.0023 vs PEPITA 0.9751 ± 0.0020 (best gradient 0.9789, digital/euclidean) | 5 | L2/20, 10k held out; chance 0.10 | paired PEPITA−gradient −0.0004, CI [−0.0051, +0.0044], p=0.84 | §3.7 (discovery) |
| 2026-11-14 | vision (secondary) | complex/adam PEPITA vs gradient | 5 | L2/20, same split | +0.0043, CI [−0.0003, +0.0089], p=0.06 | §3.7 (secondary) |

One row per domain per measurement; a row is superseded, never edited.
Earlier "met" rows are **screening verdicts**; the formal claim bar is L2/n≥5
(`computronium/experiment/evidence/claims.py`). Rows written before the
claim-conversion phase say "claim needs n≥3"; the current bar is L2/n≥5 (§5).
The vision n=5 L2 rows are the first claim-grade cells; §3.7 is the first
pre-registered matched claim.

### Claim-grade ledger (L2, n≥5, same cell except one axis)

| Date | Comparison | n | Ruler | Result | Status |
|---|---|---|---|---|---|
| 2026-11-14 | MNIST digital/adam: PEPITA vs gradient | 5 | val_acc, 10k held out; L2/20 | −0.0004, 95% CI [−0.0051, +0.0044], p=0.84, dz=−0.09 | discovery; §3.7 confirms n=10 |
| 2026-11-14 | MNIST complex/adam: PEPITA vs gradient | 5 | same | +0.0043, CI [−0.0003, +0.0089], p=0.06 | secondary; substrate interaction |
| 2026-11-14 | MNIST best-backprop check: PEPITA digital/adam vs gradient digital/euclidean | 5 | val_acc, 10k held out; L2/20 | −0.0038, 95% CI [−0.0064, −0.0012], p=0.015 | secondary; different update, non-inferiority only |

**Claim-shaped keys.** 3,437 distinct measurements, but only ~468 distinct keys
are L2 with planned n≥5; the achieved-seed count is lower. Breadth is a floor,
not a claim count. The ledger is the claim count.

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
- **A local-credit claim outranks a domain bar.** A 0.08σ domain gap is lower
  value than a matched comparison that tests the differentiated axis; spend the
  next long run on the latter (§3.7).
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
- The **claim-conversion phase** starts here (2026-11-14). The corpus's
  highest-value result is the matched MNIST pair: PEPITA 0.9751 ± 0.0020 vs
  gradient 0.9755 ± 0.0023 (n=5, L2/20, seeds 42–46; paired −0.0004, 95% CI
  [−0.0051, +0.0044], p=0.84). It is discovery, not a claim. §3.7 adds the
  equivalence predicate, commits `t93_pepita_mnist.json`, and runs new seeds
  47–56 (~2.1 h CPU) to decide whether a local credit matches backprop.
- Open work, in priority order: §3.7 PEPITA equivalence claim; §3.3c gate
  metric bar; §3.2 one graph readout arm with a stop rule; §3.8 claim-conversion
  backlog (node/graph/RL/tabular); §3.6 batched graph-settle (deferred); §3.1
  regression claims (n=1, no current claim).
- A surface defect found here is fixed here only if it blocks the number;
  otherwise it files into this plan's §3 with a measured reason. TODO91 takes
  no new work.
