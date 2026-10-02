# TODO47.md — Finish the Run

**Supersedes:** the remaining-work list of `TODO46.md`. **TODO46 is frozen and
remains the evidence record** — its §1 defects, §2 false-✅ table, §3 doctrine
and §8 session log are not edited, summarised or re-derived here. Where this
file says "TODO46 §3.7", read TODO46; it does not repeat it. **Binding:**
`AGENTS.md` in full. **Binding:** this file.

**Goal:** the seven runnable assertions of TODO46 §3.7, on a clean checkout, in
one session each. **Not the goal:** another round of registry, lock or
documentation work. That work is what §0 is about.

---

## 0. Why six sessions produced no runnable system

Each cause below has evidence in TODO46 or in session 11's log, and each has a
response that is a *mechanism* rather than a resolution.

| # | Cause (evidence) | Response |
|---|---|---|
| 1 | **Tests were launched to get information that a grep gives free.** Session 11 ran `tests/property` twice, ~12 min wall, both hard-killed, no verdict — to answer "did my change to `evidence/` break anything", which a symbol grep narrowed to 3 files answering in 13 s. | **Select by symbol, not by directory** (§1.1). A `testpaths` directory is a round-close artifact, never a feature gate. |
| 2 | **A killed run destroys its own evidence.** pytest writes the summary at session end; the kill ate it, which is what forced run 2 of run 1. | **`-rf --tb=line` on every launch that may be interrupted** (§1.2). Free, and the failure list survives the kill. |
| 3 | **The prices are stale, so launches are optimistic.** TODO46 quotes `property` at 166 s; measured reality is >5 min and hard-killed at 92%, twice. | **Price from one ≤60 s measurement, write it in the ticket** (§1.3). TODO46 §6.1 already said this and did not fire, because prose is not a mechanism. |
| 4 | **Some gates are fake and indistinguishable from real ones.** `test_required_capabilities_are_active`: green four sessions while 39 rows named tests that did not exist. D25's prefilter lock: green while the seed filter it tested was absent, because the fidelity filter excluded the record anyway. | **A lock's fixture must contain the case the lock exists for** (§1.4). A gate that cannot fail on the defect it names is a comment. |
| 5 | **The cheap work is seductive and it won.** Sessions 3–5, 8–11 landed registries, locks, README generation, an evidence judge, claims and limitations — all tier-0, all satisfying. §3.6–§3.8, the part an external researcher runs, are untouched. | **Order the queue by deliverable, not by interest** (§2): the runnable assertions first, defect archaeology last, never mid-queue. |
| 6 | **Every session re-pays for context** — 1,900 lines re-read, conclusions re-derived, trust re-decided, eleven times. That is why the plan grows with caveats instead of shrinking as work lands. | **This file is the queue, and it is short on purpose** (§2). Landed work leaves the queue; it does not enter it. |
| 7 | **Correction arrived as interruption rather than as a rule.** The electricity rule (TODO46 §6.1) existed as prose; the operator's impatience arrived after 12 minutes of a doomed run. | **The rules are in `AGENTS.md` now** (§1), where they apply without being re-read. |
| 8 | **Nothing reports which gate can actually run today**, so each session picks the most *interesting* defect rather than the one that unblocks the deliverable. | Every ticket in §2 names its **gate**, its **cost**, and its **dependencies**, so the next session starts at ticket 1 without re-deriving anything. |

**The summary, stated once:** the expensive failures were never the tests. They
were running a 5-minute shard to learn something a 1-second grep knew, twice,
because the first run's output was destroyed by the kill that ended it.

---

## 1. Permanent rules (in `AGENTS.md`, not only here)

Added to AGENTS.md's Testing section in the same commit as this file. Restated
here only so a reader of this file knows they exist:

1. **Select tests by symbol, not by directory.** `grep -rn <symbol> tests/
   --include=*.py`, run the 2–4 files it names. A whole `testpaths` directory
   is a round-close artifact; it costs ~5× and can be killed without a verdict.
2. **Any run that may be interrupted writes `-rf --tb=line` to a log.** The
   summary is written at session end, so a kill takes the run's only artifact.
3. **A killed run yields no verdict — collect, do not re-run.**
   `pytest <dir> --co -q > ids.txt` executes no test code (~40 s) and locates
   the failure from the progress line. **Never `--lf`/`--ff`** in this repo:
   `.pytest_cache/v/cache/lastfailed` holds 520 entries, most with node ids that
   no longer collect.
4. **A lock's fixture must contain the case the lock exists for.** If the
   fixture cannot fail when the mechanism is removed, the lock is a comment —
   the D25 and `test_required_capabilities_are_active` shape.
5. **One shard run per round close, never per commit**, and never a re-run of a
   shard already green "to confirm".

---

## 2. The queue

Eight tickets, ordered by *unblocking the deliverable*. Each ends in its own
commit and its own named gate; **no ticket's gate is a whole shard.**

### T1 — DONE (§3.7 gate 5: resume without duplicating or losing a measurement)
- **Does:** interrupt a run mid-flight, resume by `run_id`, and prove the store
  holds no duplicate `measurement_key` and no gap in coordinate coverage.
- **Gate:** a new lock asserting both properties from the store alone, on a
  `digits` run interrupted after the first N records (tier 1, ~1 min).
- **Blocked by:** nothing. **Unblocks:** T5.
- **Landed:** `PipelineRunner._resume_completed_measurements` seeds
  `completed_measurement_keys` from the store for its own `run_id`
  (`pipeline.py:185`), and `_fresh_batch_items` (`pipeline.py:556`) drops
  already-measured proposals instead of paying for a measurement the store
  refuses. `RecordStore.is_open` guards the seed; `PipelineRunner.rejections`
  exposes the classification list so a lock can read it.
- **Gate:** `tests/property/test_resume_coverage_lock.py` — **27 s**, both
  tests. 5-file selection (stage/sampler/kernel/resume locks + U3 acceptance)
  **83 s**. Falsified by removing the seeding: both tests go red on the
  `PERSISTENCE_ERROR` rejection list.

### T2 — DONE (§3.7 gate 6: replay hash)
- **Does:** wire `compute_replay_hash` (`replay.py`, exported, **zero callers**
  — TODO46 §2.0). It must be written on run completion, not computed on demand,
  or the hash cannot detect a run that diverged.
- **Gate:** the same spec run twice yields the same `replay_hash`; a spec with
  one changed field yields a different one (tier 1).
- **Blocked by:** nothing. **Unblocks:** T5's reproducibility claim.
- **Landed:** `compute_run_replay_hash(run_spec, measurement_keys)`
  (`replay.py:63`) hashes the canonical spec plus the *sorted set of measured
  `measurement_key`\ s*, and `PipelineRunner._record_replay_hash`
  (`pipeline.py:222`) writes it to `runs.replay_hash` when `run()` returns, not
  on demand. `RecordStore.set_replay_hash` is the writer; `finish_run` now
  preserves a hash it was not given (`COALESCE`), which it previously erased.
- **Gate:** the same lock file, 5 tests / **49 s**. Falsified twice: removing
  the `_record_replay_hash()` call turns both replay tests red.
- **Why not a spec hash:** measured *values* are excluded (walltime and float
  kernels are not reproducible) but measured *identity* is included, which is
  what detects a diverged run. `test_a_diverged_run_hashes_differently_though_its_spec_did_not`
  pins that distinction — same spec, one extra round, different hash.

### T3 — DONE (§3.7 gate 7: two policies over one store)
- **Does:** `--policy stratified_random` then `--policy model_based` against
  the same store, schema and task; records comparable (R16/R17), and per TODO46
  §8 session 7's honesty note the model-based trial sequence must *differ* from
  the random one for the same seed.
- **Gate:** a lock comparing the two runs' record sets (tier 1–2).
- **Blocked by:** nothing. **Unblocks:** T5.
- **Landed:** `test_two_policies_over_one_store_measure_different_trials` and
  `test_measurement_identity_is_the_coordinate_alone` in the renamed
  `tests/property/test_run_ledger_lock.py` (was `test_resume_coverage_lock.py`;
  it now holds gates 5-7 and one spec/config builder).
- **Gate:** 7 tests / **53 s**. Falsified by pointing the "model_based" run at
  `StratifiedRandomPolicy`: the sequence assertion goes red, which is the point
  — identical sequences are the failure this gate exists to catch.
- **A real defect fell out of it: the store could not reproduce a record's own
  key.** `measurement_key` hashes `schedule.param_budget`, but the `schedule`
  STRUCT (`store.py:202`) had no such column and neither insert site wrote one,
  so every stored schedule read back with `param_budget=0` and *no stored
  record's key recomputed from its own record*. `_parse_schedule`'s
  `.get("param_budget", 0)` had been hiding this behind a comment about older
  rows. Fixed by persisting the column at both append paths; a store written
  before it is now refused at open with a clear message instead of failing deep
  in DuckDB on append (`RecordStore._assert_identity_recomputable`).

### T4 — DONE (the operator's own criterion: which axis mattered)
- **Does:** `derive_claims` becomes per-*metric* rather than per-first-objective
  (session 11's note), and the report prints a Pareto front over ≥2 declared
  objectives instead of one metric against `param_count`.
- **Gate:** on a real measured run, the report prints claims for **two**
  metrics and a front with ≥2 non-dominated points (tier 1).
- **Blocked by:** nothing. **Unblocks:** T5's headline.
- **Landed:** `derive_claims(records, metrics=(...))` is per metric
  (`claims.py:192`); `ReportGenerator.claim_metrics` resolves every measured
  declared objective, `claims()` claims all of them and takes `min_seeds` from
  the run's own spec (was a hardcoded 5), and `front_objectives` is the first
  *two* measured objectives rather than (first objective, `param_count`).
  Directions come from each objective's declared `direction` via
  `metrics.optimizes` / `metrics.objective_name` — the old fixed
  `maximize=(True, False)` maximized walltime on the second axis. The two copies
  of the Pareto filter collapsed into `_pareto_subset`.
- **Gate:** `TestPerMetricClaims` in `test_claim_report_lock.py` — **14 s** for
  the whole file, 26 tests. Falsified twice: capping `claim_metrics` at one
  metric and disabling the two-objective front each turn it red.
- **Measured fact, recorded not hidden: the L0 regime has no trade-off.**
  `val_acc` takes two values at `batch_limit=2`, so the fastest high-accuracy
  cell dominates all others and the measured front is legitimately **one**
  point; raising `batch_limit` to 8 does not change that (probed). The
  "≥2 non-dominated points" half of the gate therefore runs on a fabricated
  three-point set with a real trade-off, and the measured front is asserted to
  be over both declared objectives and non-empty. A front with one point is a
  finding about the regime; a filter that cannot hold two is broken — only a
  real trade-off separates the two, and T5 is where the space gets wide enough
  to have one.

### T5 — §3.6 the campaign (the one expensive ticket)
- **Does:** `examples/*.yaml` as a **fixture**: `digits` primary, `mnist` as the
  transfer task, varying algorithms (dynamics × credit × update) and topology
  with hyperparameters — not every primitive on every axis.
- **Gate:** demo-marked test asserting the seven properties of TODO46 §3.7 plus
  T1–T4's, so the campaign is assertable rather than narrated.
- **Blocked by:** T1, T2, T3, T4 — it is their integration, and running it
  before they pass means paying the most expensive tier against gates that do
  not yet exist.
- **Cost discipline — DONE, priced.** One cell is one `(coordinate, schedule)`
  evaluated through the executor the backend calls (`cell_record`), measured in
  `scripts/probes/_t5_cell_price.py` over three credits:

  | task | batch_limit | s/cell |
  |---|---|---|
  | digits | 2 | 0.44 (first cell 1.06 — warmup) |
  | digits | 8 | 0.23 |
  | mnist | 2 | 0.16 |
  | mnist | 8 | 0.33 |

  **Budget 0.5 s/cell and the campaign is a normal test, not a demo.** The
  shape below is 6 algorithms × 2 geometries × 2 tasks × 5 seeds = **120
  measurements ≈ 60 s**, plus pipeline and store overhead; TODO46 §3.6's "a few
  hundred real cells is a few minutes" holds, so the whole campaign fits one
  round close and stays **in** `testpaths`. If a future axis multiplies that by
  more than ~5, re-price and move it to the demo tier rather than growing it.
- **Planned shape** (not every primitive on every axis, per §3.6): substrate
  `digital`, plasticity `fast_weights`, update `euclidean` fixed; algorithms
  = dynamics {energy_minimization, diffusion} × credit {thermodynamic_contrast,
  local_contrastive, gradient}; geometry {feedforward, recurrent}; digits
  primary, mnist transfer; L0, 1 epoch, measured param budget, 5 seeds.
- **Gates 1-4 are CLI-shaped and still unimplemented**, which is the honest
  status of this ticket: `comp run --spec examples/<file>.yaml` must write
  records, a real `train_acc` must *move when the axis moves*, `comp report
  --run-id <id>` must give claim+evidence+limitations from the store alone, and
  `comp report status` must list the run. `examples/` **does not exist yet** —
  the closest fixtures are `experiments/campaign_gate_tier0_digits.yaml` (a
  different, older schema) and `campaigns/checkpoints/*.yaml`.

### T6 — §3.8 fold the lab in, last
- **Does:** the kernel owns evaluation; the lab becomes a facade over it; the
  lab's *predicted* metrics stay labelled predicted everywhere and never enter a
  claim; anything that does not survive gets a retirement record (R78).
- **Gate:** no second evaluation implementation exists, and the lab's own tests
  pass against the kernel's evaluator (tier 1–2).
- **Blocked by:** T5. Folding earlier produces the second evaluator §3.8
  forbids — the whole reason it is last.

### T7 — D24: promotion has no stage
- **Does:** decide what promotes a cell (decision **D-a** below), then add the
  stage that writes `status.maturity` above `L0`. Today `promoted`,
  `filter_promoted` and the report's promotion-history section are permanently
  empty — a constant, not a measurement.
- **Gate:** a lock asserting a promoted cell reaches `L2` and appears in
  `promotion_history`; plus the report's `Promoted:` count becomes non-zero on
  a run that earned it (tier 1).
- **Blocked by:** decision D-a.

### T8 — The small ones (any order, any session)
- `conformance.py` should **report** an `UNVERIFIED` row's recorded reason
  rather than run its node id and print a pytest failure for a capability it
  already knows is unverified; `codegen.generate_conformance_stubs` should stop
  emitting stubs for the 19 unverified rows (TODO46 §8 session 9).
- **`nca`** stays retired (TODO46 D17) — restoring it is a geometry feature with
  credit/settle consequences, i.e. its own plan, not a queue item here.
- **README content archaeology** (low): diff `README.md` back past each rewrite
  and recover substance worth keeping into `docs/readme/*.md`.

### Deliberately not in the queue
- **New defect archaeology.** TODO46 §1 is where a defect found by reading code
  belongs, with `file:line` evidence — but the *queue* does not grow for it.
  Defects that block a ticket above are pulled forward explicitly; the rest
  wait for the deliverable.
- **`pytest tests/`** — never, and now also never `pytest tests/property` for a
  feature change (§1.1).

---

## 3. Decisions needed from the operator

Four forks, each one line to settle and one line to reverse. Three of them sit
*inside* a later ticket as a blocker, which is why they are asked now and not
then.

- **D-a — what promotes a cell?** (blocks T7.) Options: (i) achieved seeds
  ≥ `spec.n_seeds` at the declared fidelity with a `PASS` gate; (ii) an explicit
  L2 gate the gate stage writes; (iii) an operator action recorded in the store.
  *Session default if unanswered:* (i), written by a new promotion stage, with
  maturity `L1` on eligibility and `L2` on promotion.
- **D-b — is a `batch_limit`-bounded `val_acc` an admissible claim objective?**
  (TODO46 §7.1-2; affects T4.) *Default if unanswered:* record `val_batches`
  beside `val_acc` and let every consumer decide — already the session-7
  default, kept.
- **D-c — are the 32 unmeasured objectives research targets or noise?**
  (TODO46 §7.1-3; affects what T4 may claim.) *Default if unanswered:* keep
  them registered with their reasons, so `OBJECTIVES` does not silently shrink.
- **D-d — the campaign is a demo-marked test, not a script.** (TODO46 §7.1-5;
  T5.) *Default if unanswered:* demo-marked test, because the plan requires the
  campaign to be assertable.

---

## 4. How a session runs a ticket

1. Read this file and `AGENTS.md`. Not TODO46, unless the ticket names a
   section of it.
2. **Grep for the touched symbols** in `tests/` and run the 2–4 files that name
   them. Nothing else.
3. Implement. `ruff format` + `ruff check` on changed files, `pyright` on
   changed modules.
4. Run the ticket's gate. If it goes red, fix the cause — do not launch a shard
   to investigate.
5. Update this file's ticket to DONE with the measured seconds, commit, stop.
   Shard runs happen at round close, once, backgrounded, with a kill time.
6. Landed tickets leave the queue. The queue should get **shorter**, and the
   file should not grow a session log — TODO46 §8 is where evidence lives, and
   a one-line entry here is enough.

---

## 5. Session log

- **T1 landed.** The store was already correct — `UNIQUE(run_id,
  measurement_key)` at `store.py:207` — which is why the first version of the
  lock *passed with the mechanism removed*: the constraint swallows duplicates
  and the pipeline classifies them as `PERSISTENCE_ERROR` rejections, so both
  store-level properties held anyway (§1.4, second instance of the D25 shape).
  The falsifiable property is the rejection list, not the record count.
- **`max_rounds` is off by one and it hides it.** `RoundController.should_continue`
  increments before it compares (`decision.py:64`), so `max_rounds=1` executes
  **zero** rounds. `test_u3_pause_resume_via_run_id` used `max_rounds=1` for its
  "first run" and asserted `round2_count >= round1_count` — `0 >= 0`, green for
  four sessions (TODO46 §2, third false-✅). Fixed: first run uses 2, and the
  assertion is now `round1_count > 0` and `round2_count > round1_count`. Worth
  grepping the repo for other `max_rounds=1` configs before the campaign (T5)
  sizes its cells.
- **Objectives must actually trade off before any front means anything.** With
  two credits at L0 the front is one point, so a campaign whose cells differ
  only by seed cannot produce a Pareto story — T5 must vary the *structural*
  axes (dynamics/geometry/credit), not just the seed, or its headline front will
  be a single cell that dominates.
- **`min_seeds` was hardcoded to 5 in `ReportGenerator.claims`** while
  `limitations` read the run's own `spec.n_seeds`. A run declaring 2 seeds
  could make no claim no matter how well it replicated. Now read from the spec;
  the 5 remains only as the spec-less default.
- **`test_wp11_surface_lock.py` is slow and flaky.** Alone it is **217 s** and
  two runs of the same file failed *differently* — once on
  `test_listings_deterministic`, once on a pytest-timeout (>120 s on a single
  test). Unrelated to the store change (codegen does not read it), but it means
  the property shard's price is not just long, it is not reproducible: raise the
  per-test timeout for that file, or split it, before it is quoted as a gate.
- **`compute_replay_hash` (per-cell) and `compute_run_replay_hash` (per-run)
  coexist and neither calls the other.** The per-cell one is still the one
  `test_replay_hash_deterministic` covers and nothing in production calls it.
  If the run-level hash is the gate, the per-cell one is a candidate for
  retirement (T8's `nca`-style retirement record) rather than a second API.
- **Resume is now per-run, not per-round, but the runner is still stateless
  across launches.** The policy object restarts from its seed, so a resumed run
  re-proposes round 1's cells, skips them all, and only starts adding coverage
  from its second round. Harmless for coverage, but it means a resumed run burns
  one round per launch. T5's campaign should resume rarely (checkpoint on
  budget exhaustion, not on every cell) or this becomes N wasted rounds.

## 6. Improvement opportunities found while landing T1

1. **`RoundController` semantics.** `max_rounds` executing `max_rounds - 1`
   rounds is a trap for every caller. Either rename to `total_rounds_inclusive`
   or fix the comparison and update the callers — but pick one and lock it, or
   the next `max_rounds=1` writes another vacuous gate.
2. **`_merge_classification` appends untyped dicts** to the same list
   `_classify_rejection` appends to, so a consumer of `PipelineRunner.rejections`
   must use `.get("cause")`. A `Rejection` frozen dataclass (stage, cell_key,
   coordinate, schedule, cause, message, timestamp) would let T3's record-set
   comparison and the report read causes without defensive `.get`.
3. **The store's dedup is the last line of defence and nothing measures it.**
   A lock that a forced-duplicate append is refused *and* that a resume never
   reaches that path is the §3.7 gate-5 statement in full; today the resume lock
   covers the second half only.
