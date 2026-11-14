# TODO92 — Breadth and evidence (successor to TODO91)

**Status:** 2026-11-14 · **charter and scoreboard; no tickets yet.**
**This file opens when TODO91 is closed.** If TODO91 §8 still lists work, do it
there first — a second queue built on an unfinished one is how the same ticket
gets attempted twice. The stop condition is written in TODO91 §10.

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

Corpus: **7,433 PASS cells / 440 stores**; **28/28 tasks** measured;
**92/98** substrate × geometry pairs hold a cell (25 refused by a named rule,
19 hold cells that cannot count as substrate breadth, 1 unmeasured:
`neuromorphic × graph`).

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

### 3.0 First ticket (pre-registered with this plan): re-verify the baseline

The §2 numbers are quoted from the TODO85–90 records. A baseline nobody has
re-executed is a claim about a record, not about the system — and this project's
own history (G8, G11, G20) is a list of measurements that were wrong for harness
reasons. So the first ticket is reproduction, not new breadth.

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

1. **Regression lane** (TODO91 §8, next-ticket subsection). Measured: 9/18
   cells fail on `diabetes`/`lorenz_state`; 7 class-readout one-hot failures,
   2 label-channel failures. Blocks 2 tasks across ~5 credits/plasticities.
2. **RL.** −1184 against > −200. This is a capability gap, not a tuning gap:
   check episode budget, reward scaling, and whether the control task's
   geometry/credit pairing is legal before treating it as an algorithm result.
3. **`neuromorphic × graph`** — no cell, no rule. Either a graph-operator path
   for the substrate or a declared refusal with a measured reason.
4. **Claim-blockers** (TODO91 §8, claim-blocking group): settle telemetry, RNG
   seeding, objective validation, settle-driver loop. Needed before any new
   claim is credible.

---

## 4. Scoreboard (update in place; never rewrite history)

| Date | Domain | Best | n | Ruler | Status | Ticket |
|---|---|---|---|---|---|---|
| 2026-11-14 | regression | — | 1 | MSE, target-variance units | not claim-eligible | §3.1 |

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
- **Claims need n≥3 and a preregistration** when the result sits within 1σ of
  its threshold (`configs/preregistrations/`).
- **A surface defect found here is fixed here only if it blocks the number**;
  otherwise it files into TODO91 §8 while that file is open.

---

## 6. Handoff contract

- TODO91 §10 defines when that plan is closed. Until then, its §8 work takes
  precedence: this file must not open tickets that TODO91 already owns.
- When TODO91 closes, this file becomes the plan of record; the first ticket is
  §3.1 (regression lane) if still open.
- If this file is read while TODO91 §8 is non-empty, stop: work belongs there.
