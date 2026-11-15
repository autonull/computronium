# TODO92 — Refusal, liveness, interaction and evidence (successor to TODO91)

**Status:** 2026-11-15 · §3.0a, §3.0, §3.2, §3.3, §3.3b, §3.4, §3.7, §3.9,
§3.3c and §3.10's four interactions are closed; §3.11's credit viability
map and its `local_goodness` vs `gradient` follow-up are closed. The gate now means **defect-free
and above the task's chance/majority ruler**: a cell that measures at or below
the trivial predictor is FAIL with a named `below bar` defect. The recorded
−1536.6 RL positive control is now FAIL (§3.3c), so PASS counts no longer
overstate learning. The measurement layer is honest:
3,512 measurements, 93/99 pairs, 0 holes, 543 L2/planned-n≥5 measurement keys
(2026-11-15 re-count; achieved seeds are lower). The first audit found the
complex/adam PEPITA pair is on a **declared-refused pair**
(`complex_substrate_real_compute`), not a live substrate interaction. §3.9 now
classifies all 57 declared axis values: **48 live, 1 refused, 2 unavailable, 6
canonical references; 0 undeclared inert.** §3.7's digital probe is now a
pre-registered **cost-adjusted parity**: PEPITA **0.9752 ± 0.0019** vs gradient
**0.9744 ± 0.0027** over 10 fresh seeds, paired **+0.0008**, 95% CI
[−0.0012, +0.0029], **EQUIVALENT** within ±0.01 at 1.17× walltime (details in
§3.7). No non-standard composition yet has a cost-adjusted capability win; the
plan searches for one.
The first two interactions are **negative**, and they name the mechanism:
`energy_minimization` costs the `random_projections` credit **−2.4 pp**
against `gradient`, and `muon`'s benefit is **−6.2 pp smaller on graph than on
feedforward** (both claim-grade, n=5, L2/100; §3.10). The graph/muon cell is
the node row's best measured (**0.7680 ± 0.0133**, 1.35σ above 0.75). The
graph row's last lever is now **excluded**: sum pooling measures 0.6466 ±
0.0248 vs mean 0.6951 ± 0.0237, paired **−0.0484**, 95% CI [−0.0601, −0.0368]
(n=5, L1/100, seeds 42–46), so §3.2 closes the row **at-bar/marginal**.
The third interaction — credit × substrate — is **measured and closed**
(2026-11-15): `local_goodness` loses **0.91 pp** and `gradient` **0.11 pp** on
the analog substrate against their digital cells, so the interaction is
**−0.85 pp**, 95% CI [−1.08, −0.60], p=0.008 (n=5, L2/20, seeds 57–61, 68 min
CPU). The CI straddles the pre-registered ±1 pp margin: **no interaction at the
declared margin**, direction unfavorable — a boundary coordinate, not a
negative claim (`experiments/t92_credit_substrate_lg.duckdb`, run `33621198`).
The fourth interaction — plasticity × task — is **measured and closed** too
(2026-11-15): with every other axis fixed, `fast_weights` forgetting is
**0.0425 ± 0.0053** vs `null` **0.0417 ± 0.0051**, paired null−fast
**−0.0008**, 95% CI [−0.0021, +0.0006], p=0.37 (n=5, seeds 62–66, 5
epochs/task), at **8.9× walltime** (256 s vs 29 s per run). The CI is inside
the pre-registered ±0.01 margin: **no plasticity × task interaction** at this
coordinate. **The interaction matrix is complete: two negative interactions,
two no-interaction-at-margin results, zero capability wins.** The thesis's
strong form — a non-standard composition wins at matched cost — is falsified at
these coordinates; its weak form survives as two cost-adjusted parities
(PEPITA 1.17×, `local_goodness` 0.81× walltime on MNIST).
**§3.11 is measured and its follow-up is closed (2026-11-15):**
all **8/8 error-aware credits clear chance** at their ladder's best point on the
MNIST anchor, so no credit is an unwired row; `local_goodness` with its declared
target channel is the map's best cell (**0.9619 / 0.9623** vs `gradient`
0.9562 / 0.9456). The matched claim-grade pair is now measured: `local_goodness`
**0.9753 ± 0.0011** vs `gradient` **0.9759 ± 0.0017**, paired **−0.0006**, 95%
CI [−0.0021, +0.0011], **EQUIVALENT** within ±0.01 at **0.81× walltime**
(n=5, L2/20, seeds 57–61). It is the first **non-PEPITA** credit at claim grade
and a cost-adjusted parity, not a win. The map
demoted the credit × substrate 2×2: a fourth PEPITA cell on a substrate that is
the digital matmul plus additive noise answers less than seven credits whose
implementation was unvalidated. With the map closed, that interaction re-enters
on `local_goodness`, the credit the map leaves standing. The plan is
**breadth-first**: no cross-credit ranking and no HPO until every declared value
is validated (AGENTS.md SEC Loop; §5).
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

Every session follows the SEC decision loop in `AGENTS.md` (DECIDE →
FALSIFY CHEAPLY → TRIAGE → FIX → VERIFY → RECORD), with the rung ladder and
2× measured-cost watchdog. This file replaces the per-phase TODO cadence: one
rolling plan, tickets ordered by what unblocks a measured number.

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
the refusal is reversed by its trigger**, or **a cross-credit ranking or a
tuning sweep before each credit's implementation is validated** — a low cell is
a defect probe first (AGENTS.md SEC Loop; §5). TODO91's S1d thread is
the worked example: four commits, two attempts, one revert, zero capability.

---

## 2. Measured baseline (2026-11-14)

Corpus (re-measured 2026-11-15 after §3.10's credit × substrate 2×2): **7,530
PASS records / 448 stores** — **3,512 distinct measurements** (the two numbers differ; see the
ruler note); **28/28 tasks** measured; **93/99** substrate × geometry pairs hold
a measurement (25 refused by a named rule, 19 hold 257 measurements that cannot
count as substrate breadth, **0 unmeasured**). The last hole,
`neuromorphic × graph`, holds three cells recorded in
`experiments/t92_neuromorphic_graph.duckdb` (§3.4); §3.11's follow-up adds
`experiments/t92_local_goodness_mnist.duckdb` (10 records, 10 measurements).

**Ruler note (measured 2026-11-14; re-measured by §3.0a).** `scan_corpus` counts
PASS records, and `measurement_key` is unique *within* a store, not across
stores: 441 stores held 7,442 PASS records for **3,431 distinct configurations**
before §3.4 (1,300 keys repeat; max 114); the §3.4 store adds 4 records and 3
measurements. Every earlier "PASS cells" number in TODO85–91 is therefore a
record count, inflated ~2.2× by re-runs. Breadth is quoted as distinct
measurements from here on; "28/28 tasks" survives because it unions task ids.
The report now prints both numbers: `7,530 PASS records = 3,512 distinct
measurements` over 448 readable stores (2026-11-15). Pair breadth: **93/99**
hold a
measurement, 25 are refused by a named rule (19 of those hold 257 measurements
that cannot count as substrate breadth until the refusal reverses; §3.9),
**0 holes**.

| Domain | Best measured (re-executed 2026-11-14) | Ruler | Target | Verdict |
|---|---|---|---|---|
| Vision | MNIST **0.9789 ± 0.0003** (SD) gradient (digital/euclidean) | n=5, L2/20, val_acc, 10k held out; chance 0.10 | > 0.95 | met, **claim-grade** |
| Vision (local credit) | MNIST **0.9752 ± 0.0019** (SD) PEPITA (digital/adam) | n=10, L2/20, 10k held out; matched gradient **0.9744 ± 0.0027** | > 0.95 | met, **claim-grade**; **confirmed equivalent** +0.0008, 95% CI [−0.0012, +0.0029], at 1.17× walltime — parity, not a win |
| Vision (FF local credit) | MNIST **0.9753 ± 0.0011** (SD) `local_goodness` (`readout_error`) | n=5, L2/20, 10k held out; matched gradient **0.9759 ± 0.0017** | > 0.95 | met, **claim-grade**; **confirmed equivalent** −0.0006, 95% CI [−0.0021, +0.0011], at 0.81× walltime — parity, not a win |
| Graph classification | PROTEINS **0.7013 ± 0.0164** (SD) | n=5, L1/100, 223 held out; majority 0.596 | > 0.70 | **screening; marginal** (0.08σ) |
| Node classification | Cora **0.7660 ± 0.0151** (SD) | n=3, L1/100, 500-node public split; majority 0.316 | > 0.75 | **screening; met** (1.06σ) |
| Tabular | wine **1.0000** (record 0.9722) | n=3, L0, 36 held out (resolution 0.0278); majority 0.389 | > 0.90 | **screening; saturated** |
| RL | pendulum **−135.1 ± 9.0** (SD) | n=3, L0/40 epochs, 400 episodes, mean return; chance ≈ −1200 | > −200 | **screening; lane result, credit-inert** |

**Claim grade (measured 2026-11-15).** The corpus holds 3,512 distinct
measurements, but only 543 are L2 with planned n≥5 — the code's
`claim_eligible` floor (`computronium/experiment/evidence/claims.py`). The
vision n=5 L2 cells are claim-grade. The first differentiated matched
comparison is the **digital/adam MNIST pair** (same coordinate and schedule,
seeds 42–46, only the credit differs): gradient **0.9755 ± 0.0023**, PEPITA
**0.9751 ± 0.0020**, paired PEPITA − gradient **−0.0004**, 95% CI [−0.0051,
+0.0044], p=0.84, dz=−0.09. **Cost:** both arms 55,050 params; PEPITA
412 s/seed vs gradient 359 s/seed on CPU (~1.15×). The best backprop
(digital/euclidean) is **0.9789** at 293 s/seed; PEPITA is −0.38 pp at 1.41×.
The digital pair is a **cost-adjusted parity, not a capability win**.
**FF local credit (2026-11-15, §3.11 follow-up).** The second claim-grade
matched pair changes the credit to `local_goodness` with its declared
`readout_error` channel on the same anchor: over fresh seeds 57–61 at L2/20,
gradient **0.9759 ± 0.0017** vs `local_goodness` **0.9753 ± 0.0011**, paired
**−0.0006**, 95% CI [−0.0021, +0.0011], **EQUIVALENT** within ±0.01 at
**0.81× walltime** (349 vs 432 s/seed; 55,050 params each). It is the first
non-PEPITA credit at claim grade — a parity, not a win.
**Retraction (2026-11-14):** the complex/adam pair is **refused** by
`complex_substrate_real_compute`; its cells are bit-identical to digital
because the operator is the digital matmul on real weights. Its records are
among the 257 refused-pair measurements that cannot count; §3.9 audited the
rest (48 live, 1 refused, 2 unavailable). The graph, node, tabular and RL rows
are screening; their "met" is a
domain-bar verdict, not a formal claim.
**Gate semantics (2026-11-14, §3.3c).** A record written from this date
PASSes only when it is defect-free **and** above its task's chance/majority
ruler; the bar and the comparison are stored in the payload
(`pass_bar`, `pass_bar_cleared`). Records written earlier keep the verdict
they recorded and are **legacy PASS** (defect-free only). Every number in this
section is read from the payload metric against its ruler, never from a PASS
count.

**Node's n=5/L2 conversion (measured 2026-11-14, §3.10).** The Cora cell at
L2/100 over fresh seeds 47–51 measures **0.7568 ± 0.0145** with `adam`:
**0.47σ** above the 0.75 bar, inside the 1σ band, so that arm is **marginal**,
not met. The same 2×2's `muon` arm measures **0.7680 ± 0.0133**: **1.35σ**
above the bar, a claim-grade **cell** and the node row's best measured. The
`muon − adam` main effect on graph is +1.1 pp, CI [−0.3, +2.4], p=0.17 —
descriptive, not a pre-registered main-effect claim; the pre-registered
*interaction* with geometry is the negative result below. The 0.7660 n=3/L1
row is superseded as best measured but kept as history.

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
marginal, now **closed at-bar/marginal**: both remaining levers (capacity and
readout) are excluded by pre-registered paired comparisons (§3.2). RL's −135.1
is a screening lane result (n=3, L0), and the other met
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

**Priority order (2026-11-15: §3.2, §3.7, §3.11's map/follow-up and all four
§3.10 interactions are closed. No interaction remains open. Next capability
question is a harder-task credit comparison (CIFAR-10 or a deeper geometry, the
§3.7 stop rule); §3.8 conversions follow only if a formal claim is needed):**

1. ~~**§3.9 — axis refusal/liveness audit.**~~ — **closed 2026-11-14.** 57
   declared values = 6 canonical references + 48 live + 1 refused (`complex`) +
   2 unavailable (`rule_state`, `substrate_coupled`); 0 undeclared inert. The
   ledger and locks are in §3.9; the next blocker was §3.7 (now closed).
2. ~~**§3.7 — PEPITA digital/adam equivalence.**~~ — **closed 2026-11-14:
   confirmed.** 10 fresh seeds 47–56 on both arms (L2/20, 10k held out, CPU,
   55,050 params each): gradient **0.9744 ± 0.0027**, PEPITA
   **0.9752 ± 0.0019**; paired PEPITA−gradient **+0.0008**, 95% CI
   [−0.0012, +0.0029], p=0.46 — **EQUIVALENT** within the pre-registered ±0.01
   margin. Records: `experiments/t92_pepita_mnist.duckdb` (run `150bd310`,
   20 PASS, 100 min CPU). Cost: PEPITA 322.7 s/seed vs gradient 276.7 s/seed
   (~1.17×). This is a **cost-adjusted parity, not a capability win**; per the
   stop rule, the next local-credit question is a harder task (CIFAR-10 or a
   deeper geometry), not a third MNIST credit.
3. **§3.10 — interaction matrix.** **Status: four of four measured; closed.** The
   breadth gate (§3.11) is closed, so `credit × substrate` re-enters on
   `local_goodness`, the map's best and now claim-grade credit (its digital
   arms are measured in §3.11's follow-up). `plasticity × task`, the last row,
   needed a matched arm build; it is now measured below.
   First two interactions **measured
   2026-11-14**. Dynamics × credit on Cora. PEPITA is refused on graph
   (`local_contrastive_geometry` is feedforward-only), so the graph pair is
   `random_projections` (error-aware layered FA) vs `gradient`. 2×2, seeds
   47–51, L2/100 (record `f6a16dae`, `experiments/t92_dynamics_credit_cora.duckdb`):
   instantaneous/gradient **0.7568 ± 0.0145**, instantaneous/RP
   **0.7460 ± 0.0049**, energy/gradient **0.7496 ± 0.0107**, energy/RP
   **0.7152 ± 0.0256**. Interaction `(RP−grad)_energy − (RP−grad)_inst` =
   **−0.0236**, 95% CI [−0.0496, −0.0076], p=0.008 — **NEGATIVE**. At this
   coordinate, settling does not help the local credit; it costs it 2.4 pp, at
   5.5× the walltime (22 s vs 4 s per 5-seed energy cell). The 1-epoch 7.5 s
   cost was setup, not
   per-epoch settle: the whole 2×2 ran in ~41 s. Remaining then: credit ×
   substrate (rung 0 passed). One pre-registered 2×2 at a time. **Update × geometry cost measured** (1 epoch, seed 42, Cora anchor):
   graph+muon 0.47 s/epoch, feedforward+adam/muon 0.01–0.02 s/epoch, so the
   pre-registered `(muon−adam)_graph − (muon−adam)_feedforward` 2×2 at L2/100 ×
   5 seeds is ~4 min. **Measured 2026-11-14** (record `t92_update_geometry_cora`,
   seeds 47–51): graph/adam **0.7568 ± 0.0145**, graph/muon **0.7680 ± 0.0133**,
   feedforward/adam **0.4756 ± 0.0375**, feedforward/muon **0.5492 ± 0.0276**.
   Interaction **−0.0624**, 95% CI [−0.0960, −0.0288], p=0.008 — **NEGATIVE**.
   Muon helps the unstructured feedforward stack **+7.4 pp** (CI [+2.7, +12.0])
   and the graph stack only **+1.1 pp** (CI [−0.3, +2.4], p=0.17): at this
   coordinate, graph message passing may already supply what muon's
   orthogonalized update supplies on a flat stack — a hypothesis, not a
   mechanism claim. The graph/muon cell is the node row's best measured:
   **0.7680 ± 0.0133**, 1.35σ above 0.75 — a claim-grade **cell**, not a
   pre-registered main-effect claim.
   Credit × substrate was the candidate experiment for a non-standard **win**
   at matched cost; it needed a live, non-refused substrate (analog, ternary,
   sparse, memristive) on feedforward geometry.
   **Measured 2026-11-15:** rung 0 passes on all seven live substrates (one
   step, both credits, same initial weights), so the pair is legal everywhere;
   the pilot measures digital/analog gradient 0.9548/0.9525 and PEPITA
   0.9524/0.9512 at 1 epoch, seed 47, CPU (~20 s/epoch). `analog` is the
   candidate (largest declared noise, 0.1).
   **Reversal trigger fired (§3.11 closed): the 2×2 re-enters on
   `local_goodness` — the credit the map leaves standing and the first
   non-PEPITA credit at claim grade.** Design: credit {gradient,
   `local_goodness`(+`readout_error`)} × substrate {digital, analog}, L2/20,
   seeds 57–61, difference-in-differences
   `(LG−grad)_analog − (LG−grad)_digital`. The digital pair is already
   measured (§3.11 follow-up: gradient 0.9759, `local_goodness` 0.9753), so
   only the two analog arms (10 cells) are new; at ~20–25 s/epoch that is
   ~70 min. It required its pre-registration before the run, and the
   interaction is read as **noise robustness** (the substrates are the digital matmul plus
   additive state noise), not a distinct operator. PEPITA is the fallback arm
   if `local_goodness` cannot compose on analog.
   **Measured 2026-11-15 (closed): boundary — no interaction at ±1 pp.**
   Pre-registered in `configs/preregistrations/t92_credit_substrate_lg.json`
   before the run; `scripts/probes/t92_credit_substrate_lg.py` ran the two
   analog arms (10 cells, seeds 57–61, L2/20, CPU, 4095 s) into
   `experiments/t92_credit_substrate_lg.duckdb` (run `33621198`, 10 PASS) and
   paired them with the digital §3.11 cells. Analog: gradient **0.9748 ±
   0.0024**, `local_goodness` **0.9657 ± 0.0024**; digital: **0.9759 ± 0.0017**
   and **0.9753 ± 0.0011**. Difference-in-differences **−0.0085**, 95% CI
   [−0.0108, −0.0060], p=0.008, dz=−2.73. The CI straddles the pre-registered
   ±0.01 margin (upper −0.0060 is inside), so the verdict is **boundary**: no
   interaction at the declared margin, but the direction says
   `local_goodness` is **0.85 pp less noise-robust** than gradient. Stop rule
   applied: no lr tuning, no seed sweep, no third substrate. Rung-1 pilot
   (1 epoch, seed 57, analog: gradient 0.9554, `local_goodness` 0.9582) is in
   the probe docstring; the watchdog was 2× the measured ~82 min and the run
   finished in 68 min.
   **Plasticity × task measured 2026-11-15 (closed): no interaction at ±1 pp,
   at 8.9× walltime.** The build was the missing piece: a matched
   `create_plasticity_arm` holds the reference stack fixed
   (digital/feedforward/instantaneous/null-prior/gradient/euclidean) and varies
   only plasticity; the existing `create_fast_weight_arm` also changes
   dynamics, credit and update, so it was a four-axis contrast. The CL runner's
   own `avg_forgetting` is the reader. Pre-registered in
   `configs/preregistrations/t92_plasticity_task.json` before the full run
   (pilot: 1 seed, 5 epochs/task, null 0.0353 in 30.8 s vs fast 0.0370 in
   261.0 s). Full run (`scripts/probes/t92_plasticity_task.py`, seeds 62–66, 5
   epochs/task, SplitMNIST, CPU, ~24 min): `null` **0.0417 ± 0.0051**,
   `fast_weights` **0.0425 ± 0.0053**, final task-0 accuracy 0.9970 vs 0.9974,
   BWT −0.0519 vs −0.0527; paired null−fast **−0.0008**, 95% CI [−0.0021,
   +0.0006], p=0.37, dz=−0.42. The CI lies inside the pre-registered ±0.01
   margin: **EQUIVALENT — no plasticity × task interaction** at this
   coordinate. The regime's forgetting headroom is small (≈4 pp), so the null
   has little to lose; re-open the row only on a harder CL regime (more tasks
   or longer per-task training) where forgetting is ≥10 pp, and pre-register
   the new coordinate. Stop rule applied: no tuning of `fast_weight_dim`,
   decay or lr, no extra seeds, no third arm.
   **Two latent CL-runner defects were found and fixed** (no test covered the
   runner): the protocol call sites passed keyword-only fields positionally
   (`run_continual_learning` raised `TypeError` on every arm since
   2026-10-05), and `_finalize_metrics` read `fast_weights_dim` instead of
   `fast_weight_dim` (crashed every fast-weight run). Lock:
   `tests/unit/core/test_cl_runner_smoke.py`.
   **Breadth gate before the next comparison — now run and closed (§3.11).**
   Each credit got the AGENTS viability gate: 3 values of its primary knob
   (lr, γ, `readout_error`), 1 seed each plus one confirmation seed at the best
   point, one cheap task, label channel declared. The map is §3.11; it is the
   input to this section, not a claim.
   **All three interactions are fixed-coordinate results, not family
   rankings.** They say what these implementations do at one schedule; HPO may
   move them.
   Do not read them as "settling is bad" or "muon is for flat stacks" in
   general (§5; AGENTS.md SEC Loop).
4. ~~**§3.3c — gate metric bar.**~~ — **closed 2026-11-14.** Every task
   declares a chance/majority ruler in its registry spec (`pass_bar`, default
   `1/output_dim` for accuracy); `cell_record` compares the primary metric to
   it and writes `pass_bar` + `pass_bar_cleared` into the payload. A miss is
   FAIL with defect `below bar: …`, cause `divergence`. Acceptance met: the
   recorded RL positive control now measures FAIL
   (`mean_reward=-1536.6081` vs the −1200 random-policy floor), and a near-
   chance digits cell that PASSed before is FAIL. Details in §3.3c.
5. ~~**§3.2 — one graph readout arm with a stop rule.**~~ — **closed
   2026-11-14: readout excluded.** The pre-registered
   `configs/preregistrations/t92_graph_pooling.json` (sum vs mean,
   seeds 42–46, threshold +0.01, L1/100) measures control **0.6951 ± 0.0237**
   and treatment **0.6466 ± 0.0248**: paired **−0.0484**, 95% CI
   [−0.0601, −0.0368], p=0.008 — **FAIL**, and sum is worse by 4.8 pp. The
   graph row closes **at-bar/marginal** (0.7013 ± 0.0164, 0.08σ above 0.70);
   per the stop rule, no third capacity/readout arm and no seed sweep. A
   formal claim would need the same cell at n=5 L2/100 (§3.8), not another
   lever. Details in §3.2.
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
   **Readout arm measured (2026-11-14): FAIL — the row is closed.** Pre-registered
   in `configs/preregistrations/t92_graph_pooling.json` and run by
   `scripts/probes/t92_graph_pooling.py` (n=5, seeds 42–46, L1/100, 223 held
   out, majority 0.5964). Control `mean` **0.6951 ± 0.0237** (36.3 s/seed),
   treatment `sum` **0.6466 ± 0.0248** (36.4 s/seed): paired **−0.0484**, 95%
   CI [−0.0601, −0.0368], p=0.008, dz=−3.30. Sum pooling is not the lever; it
   loses 4.8 pp. The graph row closes **at-bar/marginal**: 0.7013 ± 0.0164
   (0.08σ above 0.70) remains the best measured, and three runs of the same
   control now read 0.7013 / 0.6960 / 0.6951, so run noise (~0.006) is wider
   than the bar margin. This is a screening paired comparison (L1), not a
   claim-grade cell. **No further graph lever is opened**; only the §3.8
   n=5 L2/100 conversion of the same cell remains, and only if a formal claim
   is needed.
3. ~~**RL**~~ — **closed 2026-11-14: met.** Three seeds × 400 episodes
   (40 × 10) recorded to `experiments/t92_rl_400ep.duckdb`:
   −144.94 / −133.04 / −127.21, mean **−135.1**, SD 9.0, bootstrap CI
   [−144.9, −127.2] against the > −200 bar. Pre-registered in
   `configs/preregistrations/t92_rl_400ep.json`. The pre-DDPG −1219 row was
   stale; the current lane clears the bar. Two findings it produced are filed:
   the credit axis is inert (§3.3b) and gate PASS had no metric bar
   (§3.3c, closed 2026-11-14).
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
3c. ~~**Gate PASS was defect-free, not above-bar**~~ — **closed 2026-11-14.**
    **Measured problem.** `assess_gate_verdict` read void/hard/soft defects and
    an optional seed floor; it had no metric threshold, so the positive
    control PASSed at −1536.6 and corpus PASS counts overstated learning on
    RL and near-chance tasks.
    **Fix.** The bar is declared where the task is declared:
    `TaskSpecEnriched.pass_bar` in
    `computronium/experiment/registry/task_registry.py`, resolved by
    `primary_pass_bar()` against the primary objective's metric key and
    direction. Accuracy tasks default to `1/output_dim`; RL returns
    (pendulum −1200, acrobot −500, cartpole 20), language perplexity (65/27 =
    uniform over the vocab) and regression MSE (standardized diabetes 1.0 =
    train-mean predictor; measured scientific/forecast mean-predictor MSE)
    declare theirs. Graph/tabular rows declare the measured **majority** rate
    (PROTEINS 0.5964, MUTAG 0.6579, Cora 0.316, CiteSeer 0.2107, PubMed
    0.3994, breast_cancer 0.6316, wine 0.3889), because a random 0.5 floor
    would pass a cell below the trivial classifier.
    `cell_record` compares the primary metric (`maximize`: strictly greater;
    `minimize`: strictly less; missing/non-finite never clears), writes
    `pass_bar = {metric, direction, value}` and `pass_bar_cleared` into the
    payload, and makes a miss FAIL with defect
    `below bar: <metric>=<value> misses <direction> <bar>` and cause
    `divergence`. PASS is now defect-free **and** above the ruler; claim
    eligibility still requires L2, n≥5 (§3.8).
    **Acceptance (met).** `tests/property/test_gate_metric_bar_lock.py`:
    every registered task resolves a ruler; direction decides the clearing
    side; a below-chance digits cell FAILs and names the bar; an above-bar
    cell PASSes. The recorded RL positive control
    (`mean_reward=-1536.6081`, 1 epoch, seed 42) now measures
    `gate=FAIL, cause=divergence, defect="below bar: mean_reward=-1536.6081
    misses maximize -1200.0000 (pendulum mean_reward)"`.
    `tests/property/test_cell_evaluation_lock.py`'s near-chance digits cell
    (measured val_acc 0.0625 < 0.10) now records FAIL, where it PASSed before;
    the lock asserts the verdict agrees with `pass_bar_cleared`.
    **Consequences.** Existing stores keep their recorded verdicts: the 3,437
    measurements are **legacy PASS** (defect-free only) unless re-assessed;
    the claim-grade rows in §2/§4 are above their bars, so their claims stand.
    Three locks that used 1-epoch/2-batch digits cells as *claim-eligible*
    (`test_claim_report_lock`, the CEEC export, and the campaign-free claim
    fixture) now train the campaign's proved regime (`params` + 5 epochs,
    unlimited batches), because a below-bar cell is correctly not
    claim-eligible however many seeds it has.
    **Reversal trigger.** A task that declares no derivable ruler returns
    `pass_bar=None` and PASS stays defect-free; that is a coverage gap, not a
    pass, and `test_gate_metric_bar_lock` refuses a new unbarred task.
    **Follow-up (documentation, round close).** AGENTS.md's success criterion
    "100% positive control PASS rate" now conflates compose+train with
    above-bar: a hard task's 1-epoch control can be FAIL-by-bar without the run
    being invalid (`wave.py` logs the verdict and continues). Reword it to
    "control completes and its bar verdict is reported".
4. ~~**`neuromorphic × graph`**~~ — **closed 2026-11-14: measured, not
   refused.** The pair is runnable on node classification. Three L0/1-epoch
   cells on Cora (500-node public split, majority 0.316) recorded to
   `experiments/t92_neuromorphic_graph.duckdb` (run `707b3848`):
   `energy_minimization + gradient` 0.154 (19 s), `energy_minimization +
   temporal_trace` 0.146 (0.03 s), `spike_integration + temporal_trace` 0.130
   (0.07 s); the `digital/graph/instantaneous/gradient` positive control
   measured 0.132. All four PASS; this is **coverage, not a claim** — the
   numbers sit below the majority rate at one epoch and no seed replication
   exists. **§3.3c reclassifies them:** they are legacy PASS under the old
   defect-free gate, and would FAIL today against Cora's 0.316 majority bar. Corpus: 93/99 pairs, **0 holes**. The graph path is node-mode; the
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

7. ~~**Credit-axis probe: PEPITA vs gradient on a matched MNIST cell
   (priority 2).**~~ — **closed 2026-11-14: confirmed equivalent.**
   This is the first credit-axis probe, not the whole thesis: it asks whether a
   local, error-aware credit matches backprop on a live digital pair. The
   discovery answer was a **cost-adjusted parity, not a capability win**:
   **−0.04 pp** vs gradient at 1.15× walltime, and −0.38 pp vs the best
   backprop at 1.41×. The confirmation (below) measures **+0.08 pp** at 1.17×;
   the verdict is unchanged.
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

   **Confirmation (2026-11-14, closed).** The pre-registered run
   (`configs/preregistrations/t92_pepita_mnist.json`, committed in `d6757435`
   before any seed 47–56) measured:

   | Arm | Mean ± SD | n | Ruler |
   |---|---|---|---|
   | gradient | **0.9744 ± 0.0027** | 10 | val_acc, 10k held out; L2/20, seeds 47–56 |
   | PEPITA | **0.9752 ± 0.0019** | 10 | same |
   | paired PEPITA − gradient | **+0.0008**, 95% CI [−0.0012, +0.0029] | 10 | paired by seed; p=0.46, dz=0.23 |

   The CI lies inside the pre-registered ±0.01 margin: **EQUIVALENT**. Cost:
   PEPITA 322.7 s/seed vs gradient 276.7 s/seed (~1.17×), both 55,050 params.
   Records: `experiments/t92_pepita_mnist.duckdb` (run `150bd310`, 20 PASS,
   100 min CPU). The vision row gains a **cost-adjusted parity** claim, not a
   capability win. The equivalence predicate is
   `EquivalenceRegistration`/`PairedComparison.passes_equivalence` in
   `computronium/validation/preregistration.py`; the superiority p is
   secondary. **Stop rule applied:** the CI is inside the band, so do not run a
   third credit on MNIST; scale the matched design to a harder task (CIFAR-10
   or a deeper geometry) before claiming general parity.

   **Not a competitiveness claim.** This run licenses the rule's implementation
   on one cell. It does not rank credit families and does not say FF, FA or PC
   are worse: their cells are unconcluded, several are label-free by contract or
   under-optimized, and none has had the HPO that a competitive comparison
   requires. Breadth before HPO (§5; AGENTS.md SEC Loop).

8. **Claim-conversion backlog (priority 6).** The code's `claim_eligible` is
   L2 + n≥5; these rows are screening. Convert only what a claim needs:

   | Row | Current | To claim | Cost | Priority |
   |---|---|---|---|---|
   | Node Cora | **measured 2026-11-14**: 0.7680 ± 0.0133 at n=5 L2/100 (`muon`); adam arm 0.7568 ± 0.0145 | claim-grade **cell** (1.35σ above 0.75); a main-effect claim needs a pre-registered paired muon−adam (descriptive +1.1 pp, p=0.17) | done | closed |
   | Graph PROTEINS | 0.701 n=5 L1/100; row closed at-bar/marginal (§3.2) | n=5 L2/100 | ~10 min | only if a formal claim is needed |
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
      **Blocker (2026-11-15):** the `core/continual` runner's arms are
      confounded — `create_backprop_arm` is instantaneous + gradient +
      euclidean, while `create_fast_weight_arm` is energy_minimization +
      thermodynamic_contrast + adam, so its `backprop` vs `fast_weights`
      comparison differs on four axes. Do **not** use
      `run_continual_learning("backprop")` vs `("fast_weights")` as the
      plasticity comparison. The matched build composes one
      `compose_joint_system` twice (digital / feedforward /
      `energy_minimization` / gradient / adam) with `NullPlasticity` vs
      `FastWeightPlasticity` (instantaneous + fast_weights is a declared
      refusal), runs the SplitMNIST task-incremental protocol, and reads
      `compute_cl_metrics` (final accuracies, forgetting). Cost is unmeasured;
      the first step is a one-arm pilot.
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

    **Credit × substrate rung 0 measured (2026-11-15).** Both credits were
    checked per substrate with the §3.9 one-step ruler at the digits shape,
    from the same pre-step weights
    (`scripts/probes/t92_credit_substrate_rung0.py`). All seven non-digital
    available substrates compose, produce a finite non-zero update, and make
    `pepita` differ from `gradient`: `analog`, `memristive`, `optical`,
    `quantum`, `sparse`, `ternary`, and `neuromorphic` (against a
    `digital + energy_minimization` baseline, since it refuses instantaneous
    dynamics). `complex` stays refused. **Mechanism finding:** in this
    implementation the non-digital substrates are the digital matmul plus
    additive state noise (and their energy model), so a substrate arm here
    measures the credit's **noise robustness**, not a distinct operator. The
    interaction must be read that way, and the substrate's declared
    `noise_level` is the knob that matters.

   **Ladder measured (2026-11-15, MNIST, 1 epoch, seed 57, cpu and cuda).**
   PEPITA/analog over `update.step_size` 3e-4 / 1e-3 / 3e-3 measures 0.9344 /
   0.9545 / **0.9574**, best point confirmed at seed 157: PEPITA **0.9539** vs
   gradient **0.9523**. The analog cell is viable on both credits; the
   substrate's cost is ~20-25 s/1-epoch cell on CPU and CUDA alike, so a full
   four-cell L2/20 n=5 2×2 is ~2.4 h. **Not run at that design:** §3.11 closed
   first, and the 2×2 re-entered on `local_goodness` with the digital arms
   already measured (above), so only the analog arms (~70 min) are new.
   **Rung-1 pilot (2026-11-15, MNIST, §3.7 anchor, 1 epoch, seed 47, CPU).**
    gradient digital **0.9548** (15.2 s) / analog **0.9525** (20.1 s);
    PEPITA digital **0.9524** (21.5 s) / analog **0.9512** (23.2 s). All four
    are far above chance (0.10), so the analog cell trains. `analog` is the
    candidate (largest declared noise, 0.1). Measured cost: **~20 s/epoch** on
    CPU, so the pre-registered L2/20 2×2 at n=5 (4 cells × 5 seeds) is
    **~2.4 h**. The ladder is implemented in
    `scripts/probes/t92_credit_substrate_pilot.py --mode ladder` (3 lr points +
    one confirmation seed, ~2 min at 1 epoch). The 2×2 is not run yet: the
    re-entered `local_goodness` design (above) needs its pre-registration. This
    PEPITA/analog ladder remains the fallback arm's viability evidence.

11. **§3.11 — credit viability map (the breadth gate).** *Status: **closed
    2026-11-15**; 8/8 error-aware credits viable, and the map's best credit
    (`local_goodness`) is confirmed equivalent to gradient at claim grade.*
    **Decision.** Before `credit × substrate` or any cross-credit comparison,
    every error-aware credit needs the AGENTS minimum fair chance: one legal
    cheap cell, 3 values of its primary knob, 1 seed each, 1 confirmation seed
    at the best point, label channel declared. A credit that cannot clear
    chance at any point is a defect or a refusal, not a coordinate to compare.
    This is what §5 and AGENTS.md's breadth exit require, and it is why the
    fourth PEPITA cell (§3.10) was not the next run.

    **Instrument.** `scripts/probes/t92_credit_viability.py`. Anchor: the §3.7
    MNIST cell (feedforward / instantaneous / adam, L2/20, 10k held out);
    seeds 57 (ladder) and 157 (confirmation), 1 epoch, cuda; chance 0.10.
    Primary knob: `credit.feedback_scale` (γ) for the feedback-matrix credits
    (PEPITA, `random_projections`), `update.step_size` (lr) otherwise; lr
    points 3e-4 / 1e-3 / 3e-3, γ points 0.01 / 0.05 / 0.25 (γ = 0.05 is
    PEPITA's documented parity point);
    `local_goodness` sets `credit.readout_error=True` — its declared target
    channel; `thermodynamic_contrast` and `pc_alm` run on their required
    dynamics. `homeostatic` and `temporal_trace` declare `error_blind=True`:
    chance is their contract, so accuracy is not their ruler, and §3.9's
    non-zero-update fingerprint already rules both live. 32 cells, 1915 s.

    | Credit | Knob | Ladder (seed 57) | Best | Confirm (157) | Verdict |
    |---|---|---|---|---|---|
    | `gradient` (ruler) | lr | 0.9370 / 0.9545 / 0.9562 | 0.9562 | 0.9456 | viable |
    | `pepita` | γ | 0.9533 / 0.9533 / 0.9533 | 0.9533 | 0.9562 | viable |
    | `local_goodness` (`readout_error`) | lr | 0.9481 / 0.9619 / 0.9610 | **0.9619** | **0.9623** | viable; map's best |
    | `random_projections` | γ | 0.9256 / 0.9254 / 0.9253 | 0.9256 | 0.9268 | viable |
    | `thermodynamic_contrast` (energy) | lr | 0.9426 / 0.9495 / 0.9480 | 0.9495 | 0.9534 | viable |
    | `local_contrastive` | lr | 0.5074 / 0.5037 / 0.6295 | 0.6295 | 0.5959 | viable (> chance), far below ruler |
    | `target_inversion` | lr | 0.4895 / 0.4040 / 0.2689 | 0.4895 | 0.5101 | viable, clipped at the low lr end |
    | `pc_alm` (pc_alm dynamics) | lr | 0.2064 / 0.3451 / 0.1034 | 0.3451 | 0.1769 | viable, peaks at 1e-3 |

    **Findings.**
    - **8/8 error-aware credits clear chance.** No credit is an unwired row;
      the breadth gate's viability floor holds across the whole credit axis.
    - **The tiers are coordinates, not a ranking.** Four credits sit at the
      gradient ruler, three sit far below it at 1 epoch — but each far one
      still has ladder direction (`target_inversion` improves as lr falls, so
      its ladder is clipped; `pc_alm` peaks at 1e-3 and collapses at 3e-3).
      Their next fair step is a 20-epoch cell, not a knob sweep at 1 epoch.
    - **`local_goodness` with its target channel is the map's best cell:**
      0.9619 / 0.9623 vs `gradient` 0.9562 / 0.9456 at the same coordinate and
      knob. One seed: screening at the time — its claim-grade pair is now
      measured **EQUIVALENT** (below): the first non-PEPITA credit to clear the
      ruler and the first to convert.
    - **γ does not resolve at 1 epoch.** PEPITA measures 0.9533 at γ = 0.01,
      0.05 and 0.25; `random_projections` 0.9253–0.9256 over the same range.
      The ladder prices the credit's severity, not its tuned value; γ's effect
      is the §3.7 20-epoch measurement.
    - **Cost model.** Every credit is ≤ 41 s per 1-epoch cell except `pc_alm`
      at **~315 s** (15×) — its claim-grade L2/20 cell is ~1.8 h/seed, so it
      converts last, and any interaction including it needs an hours budget.

    **Follow-up measured and closed (2026-11-15).** The pre-registered pair
    (`configs/preregistrations/t92_local_goodness_gradient.json`, committed in
    `3b9308d2` before any seed 57–61 at L2/20) measured:

    | Arm | Mean ± SD | n | Ruler |
    |---|---|---|---|
    | gradient | **0.9759 ± 0.0017** | 5 | val_acc, 10k held out; L2/20, seeds 57–61 |
    | `local_goodness` (`readout_error`) | **0.9753 ± 0.0011** | 5 | same |
    | paired treatment − control | **−0.0006**, 95% CI [−0.0021, +0.0011] | 5 | paired by seed; p=0.64, dz=−0.28 |

    The CI lies inside the pre-registered ±0.01 margin: **EQUIVALENT**. Cost:
    both arms 55,050 params; `local_goodness` **349 s/seed** vs gradient
    **432 s/seed** (**0.81×**) on CPU. Records:
    `experiments/t92_local_goodness_mnist.duckdb` (run `dbb3d765`, 10 PASS,
    65 min). This is the first **non-PEPITA** credit at claim grade and a
    **cost-adjusted parity**, not a capability win. Stop rule applied: the CI
    is inside the band, so no lr tuning and no extra seeds; the next
    local-credit question is a harder task, not another MNIST cell.

    **Not claimed.** One task, one schedule. The map says every implementation
    trains; it does not rank the credits. The parity licenses
    `local_goodness` as the credit the credit × substrate interaction re-enters
    on (§3.10), not a cross-credit ranking.

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
| 2026-11-14 | graph classification | sum-pooled readout 0.6466 ± 0.0248 vs mean 0.6951 ± 0.0237 | 5 | L1/100, 223 held out; seeds 42–46 | pre-registered diff **−0.0484**, CI [−0.0601, −0.0368], p=0.008 — **readout rejected**; row closes at-bar/marginal | §3.2 (closed) |
| 2026-11-14 | node classification | Cora 0.7660 ± 0.0151 (SD) | 3 | 500 public-split nodes; majority 0.316 | reproduced; met (1.06σ) | §3.0 (closed) |
| 2026-11-14 | tabular | wine 1.0000 (record 0.9722 did not reproduce) | 3 | 36 held out (resolution 0.0278); majority 0.389 | re-run is the measurement; met | §3.0 (closed) |
| 2026-11-14 | RL (credit axis) | six credits identical: mean_reward −126.4 | 1 | 30 episodes, L0 | credit inert — one value for all six | §3.3b |
| 2026-11-14 | RL (credit axis) | `gradient` = `homeostatic` = −1536.608102 | 2 credits | 1 epoch, seed 42; 15 s/cell | error-aware credits **refused** on RL; only `error_blind` rows compose | §3.3b (closed) |
| 2026-11-14 | RL | pendulum −135.1 ± 9.0 (SD) | 3 | 400 episodes (40×10), mean return; chance ≈ −1200 | CI [−144.9, −127.2] vs −200; **met** | §3.3 (closed) |
| 2026-11-14 | corpus breadth | 3,437 measurements (7,450 records) | 443 stores | distinct `measurement_key`; 93/99 pairs, **0 holes** | §3.4 closes the last hole | §3.4 (closed) |
| 2026-11-15 | corpus breadth | 3,512 measurements (7,530 records) | 448 stores | distinct `measurement_key`; 93/99 pairs, 0 holes; 543 L2/planned-n≥5 keys | re-measured after §3.10's 2×2 | §2 |
| 2026-11-14 | neuromorphic × graph (Cora) | 0.1540 / 0.1460 / 0.1300 | 1 seed each | 500-node public split; majority 0.316; L0/1 epoch | **coverage, not a claim** (below majority; no replication) | §3.4 (closed) |
| 2026-11-14 | axis liveness | 57 declared = 6 reference + 48 live + 1 refused + 2 unavailable | 57 values | one seeded `train_step`, post-step geometry fingerprint (digits 8×8; Cora for `graph`) | **0 undeclared inert**; `complex` refused, `rule_state`/`substrate_coupled` unavailable | §3.9 (closed) |
| 2026-11-15 | credit × substrate (rung 0) | 7/7 non-digital available substrates compose; PEPITA live on each | 1 step each | post-step parameter fingerprint vs digital; digits shape | **interaction unblocked**; substrates are digital matmul + additive noise, so the arm is a noise-robustness test | §3.10 |
| 2026-11-15 | credit × substrate (rung-1 pilot) | digital grad 0.9548 / PEPITA 0.9524; analog grad 0.9525 / PEPITA 0.9512 | 1 | val_acc, 10k held out, 1 epoch, seed 47, CPU; chance 0.10 | above chance; **~20 s/epoch**, so the L2/20 n=5 2×2 is ~2.4 h | §3.10 |
| 2026-11-14 | graph classification × settling | failure: 1134 vs 32 | 1 | PROTEINS batch, node-major readout | batched path dies under energy_minimization/spike; node-mode works | §3.6 |
| 2026-11-14 | vision (claim-grade) | matched digital/adam: gradient 0.9755 ± 0.0023 vs PEPITA 0.9751 ± 0.0020 (best gradient 0.9789, digital/euclidean) | 5 | L2/20, 10k held out; chance 0.10 | paired PEPITA−gradient −0.0004, CI [−0.0051, +0.0044], p=0.84 | §3.7 (discovery) |
| 2026-11-14 | vision (confirmation) | gradient **0.9744 ± 0.0027** vs PEPITA **0.9752 ± 0.0019** | 10 | L2/20, 10k held out; seeds 47–56; chance 0.10 | paired **+0.0008**, 95% CI [−0.0012, +0.0029], p=0.46 — **EQUIVALENT** within ±0.01; 1.17× walltime | §3.7 (closed) |
| 2026-11-14 | vision (secondary) | complex/adam PEPITA vs gradient | 5 | L2/20, same split | **retracted**: `complex_substrate_real_compute` refuses every complex cell; PEPITA cells bit-identical | §3.9 (refused) |
| 2026-11-14 | node classification (claim-grade cell) | Cora 0.7568 ± 0.0145 (SD) | 5 | L2/100, 500-node public split; majority 0.316; seeds 47–51 | 0.47σ above 0.75 — **marginal**, not met | §3.10 control (§3.8 conversion) |
| 2026-11-14 | node × dynamics × credit (Cora) | inst/grad 0.7568, inst/RP 0.7460, energy/grad 0.7496, energy/RP 0.7152 | 5 per cell | L2/100, same split; seeds 47–51 | interaction **−0.0236**, 95% CI [−0.0496, −0.0076], p=0.008 — **NEGATIVE**, claim-grade; 5.5× walltime | §3.10 (first interaction) |
| 2026-11-14 | node classification (best) | Cora **0.7680 ± 0.0133** (SD), `muon` | 5 | L2/100, 500-node public split; majority 0.316; seeds 47–51 | 1.35σ above 0.75 — **met**; claim-grade cell, main effect descriptive (CI [−0.3, +2.4] pp) | §3.10 (second interaction) |
| 2026-11-14 | node × update × geometry (Cora) | graph/adam 0.7568, graph/muon 0.7680, ff/adam 0.4756, ff/muon 0.5492 | 5 per cell | L2/100, same split; seeds 47–51 | interaction **−0.0624**, 95% CI [−0.0960, −0.0288], p=0.008 — **NEGATIVE**, claim-grade; muon helps ff +7.4 pp, graph +1.1 pp | §3.10 (second interaction) |
| 2026-11-15 | credit viability (breadth gate) | **8/8** error-aware credits above chance; best cell `local_goodness` **0.9619** (confirm 0.9623) vs `gradient` 0.9562 (0.9456) | 1 seed/point + 1 confirmation | val_acc, 1 epoch, MNIST 10k held out; chance 0.10; seeds 57/157 | **viability met** on the credit axis; screening, not a ranking | §3.11 |
| 2026-11-15 | vision (local credit, claim-grade) | MNIST `local_goodness` (`readout_error`) **0.9753 ± 0.0011** vs `gradient` **0.9759 ± 0.0017** | 5 | val_acc, L2/20, 10k held out; seeds 57–61; chance 0.10 | paired **−0.0006**, 95% CI [−0.0021, +0.0011], p=0.64 — **EQUIVALENT** within ±0.01; **0.81× walltime**; first non-PEPITA credit at claim grade | §3.11 follow-up (closed) |
| 2026-11-15 | vision (local credit cost) | `local_goodness` 349 s/seed vs `gradient` 432 s/seed | 5 each | same schedule; 55,050 params each | parity is cheaper here; no accuracy loss | §3.11 follow-up (closed) |
| 2026-11-15 | credit cost model | `pc_alm` **~315 s** per 1-epoch cell; every other credit ≤ 41 s | 1 | walltime, MNIST L2/20 shape | a claim-grade `pc_alm` cell is ~1.8 h/seed; it converts last | §3.11 |
| 2026-11-15 | credit × substrate (deferred) | PEPITA/analog ladder best 0.9574 at lr 3e-3; confirm 0.9539 vs gradient 0.9523 | 1 | val_acc, 1 epoch, MNIST; seed 57/157 | viable cell, **2×2 deferred** behind §3.11 | §3.10 |
| 2026-11-15 | credit × substrate (analog arms) | gradient **0.9748 ± 0.0024**; `local_goodness` **0.9657 ± 0.0024** | 5 each | val_acc, L2/20, 10k held out; seeds 57–61; chance 0.10; analog noise 0.1 | above bar; 4,095 s for the 10 cells; digital arms 0.9759 / 0.9753 | §3.10 (closed) |
| 2026-11-15 | credit × substrate (interaction) | `(LG−grad)_analog − (LG−grad)_digital` = **−0.0085** | 5 | same; pairs the analog arms with the §3.11 digital cells | 95% CI [−0.0108, −0.0060], p=0.008, dz=−2.73 — **boundary**: no interaction at the pre-registered ±0.01 margin; direction unfavorable (LG 0.85 pp less noise-robust) | §3.10 (closed) |
| 2026-11-15 | plasticity × task (SplitMNIST) | `null` forgetting **0.0417 ± 0.0051** vs `fast_weights` **0.0425 ± 0.0053** | 5 | 5 epochs/task, seeds 62–66; avg_forgetting; final task-0 acc 0.9970 / 0.9974 | paired null−fast **−0.0008**, 95% CI [−0.0021, +0.0006], p=0.37, dz=−0.42 — **no interaction at the ±0.01 margin**; fast weights cost **8.9×** (256 s vs 29 s per run). Pre-registered probe, not an L2 survey record | §3.10 (closed) |

One row per domain per measurement; a row is superseded, never edited.
Earlier "met" rows are **screening verdicts**; the formal claim bar is L2/n≥5
(`computronium/experiment/evidence/claims.py`). Rows written before the
refusal/liveness phase say "claim needs n≥3"; the current bar is L2/n≥5 (§5).
The vision n=5 L2 rows are the first claim-grade cells; §3.7 is the first
pre-registered matched claim.
**Gate semantics (2026-11-14, §3.3c).** PASS now means defect-free **and**
above the task's chance/majority ruler; each record carries
`pass_bar`/`pass_bar_cleared`. The recorded −1536.6 RL positive control is
FAIL (ticket row: `below bar: mean_reward=-1536.6081 misses maximize
-1200.0000`). Rows above predate the gate bar and are **legacy PASS** where
their cell measured below it; the claim-grade rows are above their bars.

### Claim-grade ledger (L2, n≥5, same cell except one axis)

| Date | Comparison | n | Ruler | Cost | Result | Status |
|---|---|---|---|---|---|---|
| 2026-11-14 | MNIST digital/adam: PEPITA vs gradient | 5 | val_acc, 10k held out; L2/20 | 55,050 params; PEPITA 412 s vs gradient 359 s (~1.15×) | −0.0004, 95% CI [−0.0051, +0.0044], p=0.84, dz=−0.09 | discovery; superseded by confirmation |
| 2026-11-14 | MNIST digital/adam: PEPITA vs gradient (confirmation) | 10 | val_acc, 10k held out; L2/20; seeds 47–56 | 55,050 params; PEPITA 322.7 s vs gradient 276.7 s (~1.17×) | +0.0008, 95% CI [−0.0012, +0.0029], p=0.46, dz=0.23 | **equivalence claim met** (±0.01); cost-adjusted parity |
| 2026-11-15 | MNIST digital/adam: `local_goodness` (+`readout_error`) vs gradient | 5 | val_acc, 10k held out; L2/20; seeds 57–61 | 55,050 params; 349 s vs 432 s per seed (0.81×) | −0.0006, 95% CI [−0.0021, +0.0011], p=0.64, dz=−0.28 | **equivalence claim met** (±0.01); cost-adjusted parity; first non-PEPITA credit at claim grade |
| 2026-11-14 | MNIST complex/adam: PEPITA vs gradient | 5 | same | — | **retracted**: `complex_substrate_real_compute` refuses every complex cell; PEPITA cells bit-identical | **refused**, not an interaction; §3.9 |
| 2026-11-14 | MNIST best-backprop check: PEPITA digital/adam vs gradient digital/euclidean | 5 | val_acc, 10k held out; L2/20 | 55,050 params; PEPITA 412 s vs gradient 293 s (~1.41×) | −0.0038, 95% CI [−0.0064, −0.0012], p=0.015 | secondary; cost-adjusted loss |
| 2026-11-14 | Cora dynamics × credit: `(RP−grad)_energy − (RP−grad)_inst` | 5 | val_acc, 500-node public split; majority 0.316; L2/100 | 96,391 params; 41 s for the 2×2 (energy 5.5× instant) | −0.0236, 95% CI [−0.0496, −0.0076], p=0.008 | claim-grade **negative interaction**; §3.10 |
| 2026-11-14 | Cora graph: muon vs adam (main effect) | 5 | val_acc, same split; L2/100 | 96,391 params; 5.1 s vs 3.8 s per 5-seed cell | +0.0112, 95% CI [−0.0028, +0.0244], p=0.17 | descriptive null; not pre-registered |
| 2026-11-14 | Cora update × geometry: `(muon−adam)_graph − (muon−adam)_ff` | 5 | val_acc, same split; L2/100 | 96,391 (graph) vs ff params; 15 s for the 2×2 | −0.0624, 95% CI [−0.0960, −0.0288], p=0.008 | claim-grade **negative interaction**; §3.10 |
| 2026-11-15 | MNIST credit × substrate: `(LG−grad)_analog − (LG−grad)_digital` | 5 | val_acc, 10k held out; L2/20; seeds 57–61; analog noise 0.1 | 55,050 params; 4,095 s for the 10 analog cells | −0.0085, 95% CI [−0.0108, −0.0060], p=0.008, dz=−2.73 | **boundary**: CI does not lie inside ±0.01, but no interaction at the declared margin; direction unfavorable |

### Refusal/liveness ledger (axis value vs reference, same seed)

| Date | Axis | Variant | Reference | Observation | Verdict | Reversal trigger |
|---|---|---|---|---|---|---|
| 2026-11-14 | substrate | `complex` | `digital` | PEPITA val_acc/train_acc bit-identical per seed (42–46); `complex_substrate_real_compute` refuses every complex cell | **refused**, not live; records cannot count until reversed; §3.9 | complex operator gains a real-valued phase/noise term and `substrate_from_config` dispatches to it |
| 2026-11-14 | plasticity | `rule_state` | `null` (joint) | post-step geometry bit-identical across 12 declared completions; no `modulate` applies ψ | **inert** → unavailable; `_UNAVAILABLE` reason | a trainer applies `apply_operator` (the Z3 frozen-θ loop) |
| 2026-11-14 | plasticity | `substrate_coupled` | `null` (joint) | post-step geometry bit-identical across 12 declared completions; primitive is a documented no-op | **inert** → unavailable; `_UNAVAILABLE` reason | a substrate carries a separate state σ through the joint transition and the standard step reads it |
| 2026-11-14 | all axes | 51 non-reference values | canonical stack | 48 live, 1 refused, 2 unavailable, 0 undeclared inert | audit closed; one step is a liveness ruler, not a claim | re-run `scripts/probes/t92_axis_liveness.py` after a declaration change; a fired trigger is `stale-unavailable` |

**Claim-shaped keys.** 3,512 distinct measurements, but only 543 measurement
keys are L2 with planned n≥5; the achieved-seed count is lower. Breadth is a
floor, not a claim count. The ledger is the claim count.

**Liveness caveat.** The 93/99 pair count counts declared substrate values, not
live substrates. §3.9 now classifies every declared axis value; pair breadth is
still a **coverage floor**, not evidence that a pair composes. The live count is
48/51 non-reference values (1 refused, 2 unavailable). A pair enters an
interaction only when both its axes are live and the cell is not refused.

**Axis evidence (2026-11-14).** The six-axis program, by what is actually
claim-grade:

| Axis | Liveness (2026-11-14) | Claim-grade evidence | Gap |
|---|---|---|---|
| Substrate | 8/9 live; `complex` refused | digital + analog | one live non-digital matched comparison (`analog` × credit, boundary at ±1 pp); no non-digital substrate clears a domain bar |
| Geometry | 11/11 live | vision/graph/node screening | graph marginal; node n=3 |
| Dynamics | 8/8 live | none | best cells are instantaneous; no matched settling claim |
| Plasticity | 5/7 live; `rule_state`, `substrate_coupled` unavailable | one pre-registered paired probe (n=5, no interaction at ±1 pp, 8.9× cost) | no matched plasticity × task **gain**; re-open only on a ≥10 pp-forgetting regime |
| Credit | 10/10 live | PEPITA and `local_goodness` each **confirmed equivalent at one MNIST coordinate**; **8/8 error-aware credits viable at rung 2** (§3.11); one claim-grade interaction (§3.10, boundary) | no claim-grade **win** and no harder-task parity for any credit; `local_goodness` is now claim-grade |
| Update | 12/12 live | none | no matched update × geometry claim |

"Liveness" is the §3.9 one-step parameter fingerprint, not a PASS record or a
claim-grade cell; the claim-grade column is the evidence count. The gaps are the
program.

**The credit column is not a league table.** A low cell can be an unwired label
channel (FF without `readout_error`), a schedule mismatch, a settle defect, or
an un-tuned implementation. Breadth first (AGENTS.md SEC Loop): validate that
each credit composes, updates, and declares its channel, then compare. No
cross-credit conclusion and no HPO before that point (§5).

---

## 5. Rules for this plan

- **Breadth before HPO.** A low cell is a **defect probe, not an algorithm
  verdict** (AGENTS.md SEC Loop). Do not tune a credit or axis value, and do not
  rank credit families, until every declared value has a validated
  implementation: it composes on its legal cells, produces a non-zero update,
  and declares its label channel and capability flags. PEPITA's equivalence is
  a fixed-coordinate implementation result, not a competitiveness claim; the
  other credits' cells are **unconcluded**. HPO starts only after viability
  breadth is established — that is also when compute and development assistance
  are worth seeking. A cross-credit comparison before that point is not
  evidence. AGENTS.md's SEC revision (2026-11-14) defines the decision loop,
  the rung ladder, the 3-point viability gate, the defect-triage verdicts, the
  breadth exit, and the 2× measured-cost watchdog (no wall-clock budget); this
  rule is the plan-specific corollary.
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
- **A PASS record means defect-free *and* above the task's chance/majority
  ruler** (measured 2026-11-14: the −1536.6 RL positive control is now FAIL;
  §3.3c). Records written before the gate bar are **legacy PASS** and carry no
  such guarantee. A claim reads the metric, its ruler, and its rung.
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
  (`EquivalenceRegistration` + `PairedComparison.passes_equivalence`, added
  2026-11-14; §3.7). Report the superiority p as secondary.
- **A credit's own ladder precedes any interaction that uses it.** The 3-point
  viability ladder (3 knob values, 1 seed each, 1 confirmation seed) is the
  cheapest test that separates "unwired" from "under-tuned", and it is what
  makes an interaction's arms comparable implementations rather than two
  guesses. A credit below chance at every ladder point is a defect or a
  refusal, never a coordinate (§3.11).
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
  by pre-registered paired comparison and its readout arm is rejected too
  (sum 0.6466 ± 0.0248 vs mean 0.6951 ± 0.0237, paired −0.0484, p=0.008), so the
  graph row is closed **at-bar/marginal** and no third lever is opened. §3.3 is
  closed with a number: RL −135.1 (n=3, 400 episodes) clears −200, and that
  number is geometry × substrate because the credit axis is inert on the lane.
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
- §3.7 is closed (2026-11-14): the pre-registered equivalence run over 10 fresh
  seeds 47–56 measures gradient **0.9744 ± 0.0027** vs PEPITA
  **0.9752 ± 0.0019**, paired **+0.0008**, 95% CI [−0.0012, +0.0029], p=0.46 —
  **EQUIVALENT** within ±0.01. Cost: 55,050 params; PEPITA 322.7 s/seed vs
  gradient 276.7 s (~1.17×). Records: `experiments/t92_pepita_mnist.duckdb`
  (run `150bd310`, 20 PASS). It is a **cost-adjusted parity, not a capability
  win**; the equivalence predicate and registration are in
  `computronium/validation/preregistration.py` and
  `configs/preregistrations/t92_pepita_mnist.json`. The stop rule applies: no
  third MNIST credit; a harder task is the next local-credit question. §3.10
  searches for a cell where a non-standard axis wins at matched cost.
- §3.9 is closed (2026-11-14): all 57 declared axis values are classified (48
  live, 1 refused, 2 unavailable, 6 references); the two inert plasticity rows
  are declared unavailable with reversal triggers, and the lock proves the
  measurement. The audit is one step, not a capability claim.
- §3.10's first two interactions are closed (2026-11-14) with **claim-grade
  negative numbers**. Dynamics × credit on Cora (2×2, seeds 47–51, L2/100):
  interaction **−0.0236 val_acc**, 95% CI [−0.0496, −0.0076], p=0.008;
  `energy_minimization` costs the `random_projections` credit 2.4 pp against
  `gradient` at 5.5× walltime. PEPITA is refused on graph
  (`local_contrastive_geometry`), so the graph pair is RP vs gradient. The 2×2
  ran in 41 s; the earlier 7.5 s/epoch estimate was setup cost. Update ×
  geometry (same anchor, seeds 47–51): interaction **−0.0624**, 95% CI
  [−0.0960, −0.0288], p=0.008; muon helps the feedforward stack +7.4 pp but
  graph only +1.1 pp (CI [−0.3, +2.4], p=0.17). The graph/muon cell is the node
  row's best measured: **0.7680 ± 0.0133**, 1.35σ above 0.75 — a claim-grade
  cell, not a pre-registered main-effect claim. The adam control is 0.7568 ±
  0.0145 (0.47σ, marginal), so the node row's best number moved; more seeds at
  the old cell would not have cleared the bar.
- §3.3c is closed (2026-11-14): the gate now reads a per-task chance/majority
  ruler (`TaskSpecEnriched.pass_bar`, resolved by `primary_pass_bar`), writes
  it into the payload, and FAILs a cell at or below it with a named `below
  bar` defect and cause `divergence`. Acceptance verified twice: the recorded
  RL positive control is FAIL
  (`mean_reward=-1536.6081` vs the −1200 random floor), and the near-chance
  digits cell that PASSed before is FAIL. Lock:
  `tests/property/test_gate_metric_bar_lock.py`. Existing stores are **legacy
  PASS**; the claim-grade rows are above their bars. Three claim fixtures were
  moved to the campaign's proved regime (params + 5 epochs, unlimited batches)
  because a below-bar cell is not claim-eligible.
- §3.11 is **closed** (2026-11-15): the credit viability map runs all eight
  error-aware credits through the AGENTS 3-point ladder on the MNIST anchor
  (32 cells, 1915 s). **8/8 clear chance**; no credit is unwired.
  `local_goodness` (`readout_error=True`) measures 0.9619 / 0.9623 against
  `gradient` 0.9562 / 0.9456, the map's best cell; `local_contrastive` (0.63),
  `target_inversion` (0.51) and `pc_alm` (0.35) are viable but far below the
  ruler at 1 epoch, with ladder direction still open. `pc_alm` costs ~315 s per
  1-epoch cell (15×), so it converts last. The map ranks nothing.
- §3.11's follow-up is **closed** (2026-11-15): the pre-registered matched pair
  (`t92_local_goodness_gradient.json`, committed in `3b9308d2` before the run)
  measures `local_goodness` **0.9753 ± 0.0011** vs `gradient`
  **0.9759 ± 0.0017** over seeds 57–61 at L2/20, paired **−0.0006**, 95% CI
  [−0.0021, +0.0011], p=0.64 — **EQUIVALENT** within ±0.01 at **0.81×
  walltime** (349 vs 432 s/seed, 55,050 params each). Records:
  `experiments/t92_local_goodness_mnist.duckdb` (run `dbb3d765`, 10 PASS). It
  is a cost-adjusted parity and the first non-PEPITA credit at claim grade, not
  a win and not a ranking. Stop rule applied: no further lr tuning or seeds at
  this coordinate; a harder task is the next local-credit question.
- §3.10's credit × substrate 2×2 is **closed** (2026-11-15) as a **boundary**:
  pre-registered in `t92_credit_substrate_lg.json` before the run, the analog
  arms (10 cells, seeds 57–61, L2/20, 4,095 s) pair with the §3.11 digital
  cells to give interaction `(LG−grad)_analog − (LG−grad)_digital` =
  **−0.0085**, 95% CI [−0.0108, −0.0060], p=0.008, dz=−2.73. The CI straddles
  the ±0.01 margin, so there is **no interaction at the declared margin**; the
  direction is unfavorable (`local_goodness` loses 0.91 pp on analog vs
  gradient's 0.11 pp). Records:
  `experiments/t92_credit_substrate_lg.duckdb` (run `33621198`, 10 PASS). Stop
  rule applied: no lr tuning, no seed sweep, no third substrate.
- §3.10's **fourth interaction (plasticity × task) is closed** (2026-11-15)
  with a no-interaction verdict: a matched `create_plasticity_arm` (only
  plasticity varies) and the CL runner's `avg_forgetting` reader, seeds 62–66
  at 5 epochs/task, measure `null` **0.0417 ± 0.0051** vs `fast_weights`
  **0.0425 ± 0.0053**, paired null−fast **−0.0008**, 95% CI [−0.0021,
  +0.0006], p=0.37, at **8.9× walltime**. Pre-registered in
  `t92_plasticity_task.json`. The probe found and fixed two latent CL-runner
  defects (positional keyword-only call sites; `fast_weights_dim` typo); lock:
  `tests/unit/core/test_cl_runner_smoke.py`. **The interaction matrix is
  complete:** two negative interactions, two no-interaction-at-margin results,
  zero capability wins.
- Open work, in priority order: **no interaction remains open**. The next
  capability question is the §3.7 stop rule's harder-task credit comparison
  (CIFAR-10 or a deeper geometry), not another MNIST arm; then §3.8 graph/RL/
  tabular conversions (only if a formal claim is needed); §3.6 batched
  graph-settle (deferred); §3.1 regression claims (n=1); §3.3c's documentation
  follow-up is **done** (AGENTS.md's positive-control criterion now reads
  "completes and reports its bar verdict", 2026-11-15). §3.2 is **closed**:
  capacity and readout are both excluded and the graph row is at-bar/marginal.
- **Breadth before HPO** (§5; AGENTS.md SEC Loop): the measured interactions are
  fixed-coordinate implementation results. No credit is ranked against another,
  and no credit is tuned, until every declared value composes, updates, and
  declares its label channel. Only then does HPO begin, with the compute and
  development case that breadth earns.
- A surface defect found here is fixed here only if it blocks the number;
  otherwise it files into this plan's §3 with a measured reason. TODO91 takes
  no new work.
