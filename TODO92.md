# TODO92 — Breadth and evidence (successor to TODO91)

**Status:** 2026-11-14 · **charter and scoreboard; no tickets yet.**
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
measured; **92/98** substrate × geometry pairs hold a cell (25 refused by a
named rule, 19 hold cells that cannot count as substrate breadth, 1 unmeasured:
`neuromorphic × graph`).

**Ruler note (measured 2026-11-14).** `scan_corpus` counts PASS records, and
`measurement_key` is unique *within* a store, not across stores: 441 stores hold
7,442 PASS records for **3,431 distinct configurations** (1,300 keys repeat;
max 114). Every earlier "PASS cells" number in TODO85–91 is therefore a record
count, inflated ~2.2× by re-runs. Breadth is quoted as distinct measurements
from here on; "28/28 tasks" survives because it unions task ids. The report fix
is §3.0a, and it runs before §3.0's baseline lookup.

| Domain | Best measured | Ruler | Target | Verdict |
|---|---|---|---|---|
| Vision | MNIST **0.97** | held-out accuracy (TODO90 C2) | > 0.95 | met |
| Graph classification | PROTEINS **0.7040 ± 0.0071** | n=5, 223 held out; majority 0.596 | > 0.70 | **marginal** (within 1σ) |
| Node classification | Cora **0.766** | n=3, public split | > 0.75 | met |
| Tabular | wine **0.94–0.97** | n=3, stratified split | > 0.90 | met |
| RL | pendulum **−1184** | 400 episodes, mean reward | > −200 | **not met** |

Provenance for every row is TODO85–90's session log; this plan does not
re-measure what is already claim-grade. The three weakest points are the
graph-classification marginal, RL, and the regression lane.

---

### 3.0a First ticket: the corpus ruler

**Why.** §2 measured 7,442 PASS records for 3,431 distinct configurations. A
report that cannot tell a re-run from new coverage makes every breadth number
ambiguous, and the baseline lookup in §3.0 reads the same corpus.

**Deliverable.** `scan_corpus` (and the report render) reports **records** and
**distinct `measurement_key`s** side by side; per-task and per-pair counts
dedupe by measurement identity; the store-count line says what it counts.

**Acceptance.** the two numbers are printed; a deliberately re-run cell does
not change the distinct count; run the report on the current corpus and record
the demoted totals in §2. Cost: ~30 min.

### 3.0 Second ticket (pre-registered with this plan): re-verify the baseline

Depends on §3.0a: locate each best cell by measurement identity, not by a
record count.

The §2 numbers are quoted from the TODO85–90 records. A baseline nobody has
re-executed is a claim about a record, not about the system — and this project's
own history (G8, G11, G20) is a list of measurements that were wrong for harness
reasons. So reproduction precedes new breadth — after the ruler fix, since a
record count cannot stand in for coverage.

1. Locate each domain's best recorded cell in the corpus by its `replay_hash`.
2. Re-execute one cell per domain at that recorded config (n=3 where the claim
   needs seeds; PROTEINS at n=5 because it is marginal).
3. Classify each row **reproduced / not reproduced / not replayable** and
   correct §2 in place.
4. Demote any row that does not reproduce: it leaves the baseline and becomes a
   ticket in §3, not a number.

Acceptance: five domains classified, §2 carries the verdict, and no row remains
that has only a record behind it. Cost: five cells, one session at most.

## 3. Gap list (ordered by what unblocks a number)

1. ~~**Regression lane**~~ — **closed 2026-11-14 (TODO91 S9).** 3 laws
   generalized (`pepita`, `target_inversion`, the shared output-target
   convention), 3 mechanism rows declared class-only and refused on a
   continuous target; the re-run measured 9/9 PASS. Remaining work is a claim,
   not a lane: `diabetes` 10 and `lorenz_state` 8 PASS cells, all n=1.
2. **RL.** −1184 against > −200. This is a capability gap, not a tuning gap:
   check episode budget, reward scaling, and whether the control task's
   geometry/credit pairing is legal before treating it as an algorithm result.
3. **`neuromorphic × graph`** — no cell, no rule. Either a graph-operator path
   for the substrate or a declared refusal with a measured reason.
4. ~~**Claim-blockers**~~ — **closed 2026-11-14 (TODO91 S8).** Settle telemetry,
   RNG seeding, objective validation and the settle-driver loop are green
   (269 passed in the final gate). No claim made here rests on a known-red
   lock.

---

## 4. Scoreboard (update in place; never rewrite history)

| Date | Domain | Best | n | Ruler | Status | Ticket |
|---|---|---|---|---|---|---|
| 2026-11-14 | regression | — | 1 | MSE, target-variance units | not claim-eligible | §3.1 |
| 2026-11-14 | regression | lane closed: 3 laws + 3 refusals | 1 | same | cells exist (10 + 8 PASS), claim needs n≥3 | §3.1 (closed) |

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
- The first ticket is §3.0a (the corpus ruler: records vs distinct
  measurements), then §3.0 (baseline re-verification) — the one claim the §2
  table still rests on a record rather than a run.
- A surface defect found here is fixed here only if it blocks the number;
  otherwise it files into this plan's §3 with a measured reason. TODO91 takes
  no new work.
