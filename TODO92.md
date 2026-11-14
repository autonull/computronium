# TODO92 — Breadth and evidence (successor to TODO91)

**Status:** 2026-11-14 · §3.0a, §3.0 and §3.3 closed. RL is met at −135.1
(n=3, 400 episodes); its credit axis is inert (§3.3b). Graph stays marginal with
capacity excluded (§3.2). Next: §3.3b (credit-aware RL) or the graph readout
lever.
**TODO91 is closed (2026-11-14)** — its §10 stop condition holds, so this file
is the plan of record. The two gaps it handed over are closed: the
claim-blocking locks group (TODO91 S8) and the regression lane (TODO91 S9). The
open gap list is §3, ordered by what unblocks a number.

**Mission:** grow the *measured* capability of the library, not its paper
surface. TODO91 closed the selection surface (every declared coordinate
resolves and trains somewhere); this plan asks the next question: which
combinations produce a number that clears its domain's bar, and what does it
take to get the rest there.

Every session follows the SEC cycle in `AGENTS.md` (RUN → ANALYZE → FIX →
VERIFY → COMMIT). This file replaces the per-phase TODO cadence: one rolling
plan, tickets ordered by what unblocks a measured number.

---

## 1. The progress rule

A session progresses only if it increases one of:

1. a domain's best measured metric, with its ruler (and ≥3 seeds before it is
   called a claim);
2. the count of **claim-eligible** cells (n≥3, gate PASS, replay hash);
3. the count of runnable (task × geometry × **error-aware** credit) cells;
4. the count of declared-unavailable rows that became runnable, or a refusal
   with a measured rule.

**Not progress:** files changed, tests restructured, inventory rows added, plan
text written. TODO91's S1d thread is the worked example: four commits, two
attempts, one revert, zero capability.

---

## 2. Measured baseline (2026-11-14)

Corpus: **7,442 PASS records / 441 stores** — **3,431 distinct
measurements** (the two numbers differ; see the ruler note); **28/28 tasks**
measured; **92/98** substrate × geometry pairs hold a measurement (25 refused by
a named rule, 19 hold 257 measurements that cannot count as substrate breadth, 1
unmeasured: `neuromorphic × graph`).

**Ruler note (measured 2026-11-14; re-measured by §3.0a).** `scan_corpus` counts
PASS records, and `measurement_key` is unique *within* a store, not across
stores: 441 stores hold 7,442 PASS records for **3,431 distinct configurations**
(1,300 keys repeat; max 114). Every earlier "PASS cells" number in TODO85–91 is
therefore a record count, inflated ~2.2× by re-runs. Breadth is quoted as
distinct measurements from here on; "28/28 tasks" survives because it unions
task ids. The report now prints both numbers: `7,442 PASS records = 3,431
distinct measurements` over 441 readable stores. Pair breadth: **92/98** hold a
measurement, 25 are refused by a named rule (19 of those hold 257 measurements
that cannot count as substrate breadth), 1 hole: `neuromorphic × graph`.

| Domain | Best measured (re-executed 2026-11-14) | Ruler | Target | Verdict |
|---|---|---|---|---|
| Vision | MNIST **0.9787 ± 0.0009** (SD) | val_acc, 10k held out; chance 0.10 | > 0.95 | met |
| Graph classification | PROTEINS **0.7013 ± 0.0164** (SD) | n=5, 223 held out; majority 0.596 | > 0.70 | **marginal** (0.08σ) |
| Node classification | Cora **0.7660 ± 0.0151** (SD) | n=3, 500-node public split; majority 0.316 | > 0.75 | met (1.06σ) |
| Tabular | wine **1.0000** (record 0.9722) | n=3, 36 held out (resolution 0.0278); majority 0.389 | > 0.90 | met |
| RL | pendulum **−135.1 ± 9.0** (SD) | n=3, 400 episodes (40×10), mean return; chance ≈ −1200 | > −200 | met → §3.3 |

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
credit, so the cell that produced −135.1 is geometry × substrate (§3.3b). The
only open weak point is the graph-classification marginal; RL is met. The
regression lane is closed (§3.1).

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
is the re-run, not a reproduced record. Node's 0.766 is the thinnest met row
(1.06σ above 0.75).

`--only` replays a subset; the probe prints per-seed `measurement_key` and
walltime, and never records a run into a store.

## 3. Gap list (ordered by what unblocks a number)

1. ~~**Regression lane**~~ — **closed 2026-11-14 (TODO91 S9).** 3 laws
   generalized (`pepita`, `target_inversion`, the shared output-target
   convention), 3 mechanism rows declared class-only and refused on a
   continuous target; the re-run measured 9/9 PASS. Remaining work is a claim,
   not a lane: `diabetes` 10 and `lorenz_state` 8 PASS records, all n=1 (record
   counts, not yet re-counted as measurements).
2. **Graph classification is marginal.** Re-run 0.7013 ± 0.0164 (SD), n=5,
   223 held out: 0.08σ above the 0.70 bar, so the claim rule says marginal, not
   met. **Capacity arm excluded (2026-11-14).** Pre-registered in
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
   lever is the readout (mean pooling; `pooling` is not a declared knob) or a
   different task split — a design change, not a seed sweep. Cost: one arm, 8
   min.
3. ~~**RL**~~ — **closed 2026-11-14: met.** Three seeds × 400 episodes
   (40 × 10) recorded to `experiments/t92_rl_400ep.duckdb`:
   −144.94 / −133.04 / −127.21, mean **−135.1**, SD 9.0, bootstrap CI
   [−144.9, −127.2] against the > −200 bar. Pre-registered in
   `configs/preregistrations/t92_rl_400ep.json`. The pre-DDPG −1219 row was
   stale; the current lane clears the bar. Two findings it produced are filed:
   the credit axis is inert (§3.3b) and gate PASS has no metric bar (§3.3c).
3b. **RL's credit signal is unbuilt.** DDPG optimises `system.geometry.params`
    and never calls the composed credit: `gradient`, `target_inversion`,
    `pc_alm`, `random_projections`, `local_goodness` and `homeostatic` measure
    bit-identically at 30 episodes (−126.4). Every RL row is therefore a
    measurement of geometry × substrate, and "RL × error-aware credit" is a
    declared-unavailable cell until the trainer threads the credit's
    pseudo-gradient into its update, or the lane declares itself credit-blind
    with that reason. Acceptance: one RL cell whose reward differs between two
    credits, or the refusal row plus the trainer note (criterion 4).
3c. **Gate PASS is defect-free, not above-bar.** `assess_gate_verdict` reads
    void/hard/soft defects and an optional seed floor; it has no metric
    threshold, so the positive control PASSed at −1536.6. Corpus PASS counts
    overstate learning on RL and near-chance tasks; claim eligibility must read
    the metric and its ruler. Fix is a per-task bar in the gate, or a documented
    rule that PASS never implies above-bar.
4. **`neuromorphic × graph`** — no cell, no rule. Either a graph-operator path
   for the substrate or a declared refusal with a measured reason.
5. ~~**Claim-blockers**~~ — **closed 2026-11-14 (TODO91 S8).** Settle telemetry,
   RNG seeding, objective validation and the settle-driver loop are green
   (269 passed in the final gate). No claim made here rests on a known-red
   lock.

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
| 2026-11-14 | RL | pendulum −135.1 ± 9.0 (SD) | 3 | 400 episodes (40×10), mean return; chance ≈ −1200 | CI [−144.9, −127.2] vs −200; **met** | §3.3 (closed) |

One row per domain per measurement; a row is superseded, never edited.

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
- **Claims need n≥3 and a preregistration** when the result sits within 1σ of
  its threshold (`configs/preregistrations/`).
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
  substrate because the credit axis is inert on the lane (§3.3b).
- A surface defect found here is fixed here only if it blocks the number;
  otherwise it files into this plan's §3 with a measured reason. TODO91 takes
  no new work.
