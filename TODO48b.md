# TODO48b.md — Finish TODO48 Faster: One Campaign, One Session, One Gate

**Binding:** `AGENTS.md` in full. **Binding:** `TODO48.md` in full.
**Relationship:** TODO48.md's §2 queue is **not** cancelled — it is the evidence
record of what each ticket claims and which lock proves it. This file changes
only **order, cost, and scope of execution** for the tickets TODO48 leaves open.
Every gate TODO48 names still asserts the same thing; what this file removes is
*duplicated measurement*, never an assertion.

**Supersedes:** the remaining-queue ordering in TODO48.md §4 step 3 onward.

---

## 0. Why this file exists: the cost is in the cell, not the gate

Measured on this box (16 cores, **CUDA available**), 2026-10-03:

| thing | cost | share of a campaign run |
|---|---|---|
| DuckDB open / append / query | 29 ms / **2.9 ms per record** / 30 ms per 450 rows | **~1%** |
| one campaign cell (EqProp, L0/1ep/`batch_limit 2`) | **0.710 s** | ~100% |
| the same cell with `instantaneous` | **0.084 s** | — |
| `uv run` overhead | 0.07 s | ~0% |
| `import computronium` | 0.11 s | — |
| `import torch` | **1.78 s** | per worker, once |
| pytest collection, one acceptance file | 3.9 s | per invocation |
| the campaign lock | ~150 s (450 cells) | — |

Four measured facts drive the whole refactor:

1. **EqProp is 8.8× the cheapest primitive** for the same forward/backward, and
   ~80% of a cell is the settle loop, whose convergence early-exit **never
   fires** at campaign fidelity (`scripts/probes/dynamics_cost.py`). Every gate
   that measures cells is paying that 8.8× over and over.
2. **One campaign run can serve four consumers** (the owed D3 verification, E3,
   F2, CP-1) — but only if they share one fixture. Today the fixture is
   module-scoped *inside one file*, so any second file re-measures all 450 cells.
3. **Most claims do not need a trained cell at all.** `PipelineConfig.backend`
   is injectable and everything D3 touched — the dedup, the store writes, the
   budget charge, the S10 decision read, the resume filter — is
   backend-agnostic. They are currently verified by *training cells to check
   plumbing*.
4. **A background gate dies with the shell that launched it.** This session lost
   a 150 s campaign run that way. It is a two-second fix (§4) and it is not
   optional: an unrun gate is not a green gate.

### 0.1 Bloat audit: mostly a **negative** result, recorded so it is not re-investigated

The hypothesis "the process is slow because of infrastructure bloat" was tested
and **does not hold**, with two small exceptions:

| suspected bloat | measured | verdict |
|---|---|---|
| git / repo size | `.git` **28 MB**; `build/`, `logs/`, `.venv/` all gitignored and untracked | **not bloat** |
| Python import cost | `computronium` **0.11 s** (the root package is already lazy), `pytest` 0.2 s, `optuna` 0.28 s; `torch` **1.78 s** dominates | ~2.1 s per worker, once — **not the bottleneck** |
| `uv run` tax | **0.07 s** | **not bloat** |
| `.venv` size (6.7 GB) | **3.2 GB is `nvidia`/CUDA — and CUDA *is* available here** | **not dead weight** (checked, not assumed) |
| test-suite size | 524 files / 2681 tests (`tests/property` alone: 149 files / 992) | large, but the tiered plan already avoids running them; the real cost is *collection* (~40 s for the property dir), which is what `--co` pricing exists for |
| **`build/`** | **714 stale `.py` files duplicating `computronium/` (720)** | **real**: it already produced a false-positive grep hit this session. Delete; keep ignored. |
| **`logs/`** | **446 MB, 11,237 files**, one `g4_full_pytest.log` at **370 MB** | **real**: AGENTS.md tells every session to write a log here, and nothing prunes. Needs a retention rule. |

The two real items are disk hygiene, not latency — but the stale `build/` tree is
a genuine *correctness* hazard (a grep for a symbol matches two files, one of
them dead), and 446 MB of logs will eventually slow any directory walk.

---

## 1. Seven rules that buy the time back

1. **Mechanism locks do not train cells.** Anything about plumbing (dedup,
   budget, decisions, resume, identity) is verified against an injected fake
   backend — milliseconds. Training is for claims about *learning*.
2. **One fixture, many consumers.** A module-scoped fixture in
   `tests/acceptance/conftest.py` serves every campaign-dependent gate in the
   same session. A run is measured once and *read* many times.
3. **Cheap locks first, expensive fixture late.** Property-tier locks iterate in
   seconds; the campaign is run once at the end, when the assertions around it
   have stopped moving.
4. **No pytest invocation without a price.** `--co` before any selection whose
   runtime is unknown; `-n 4` is already in `addopts` and is not overridden for
   small selections.
5. **A gate runs once, after its work lands** (TODO48 §1). Unchanged — but a
   gate a *later* ticket covers is re-paid once, at the phase sweep, never per
   ticket.
6. **Background means detached.** `setsid` + a log file. A `nohup … &` from a
   shell the tool may terminate is not background, it is a wish.
7. **CI absorbs breadth.** Once F3 exists, wide selections (CP-3's shards) run in
   CI, not on the critical path. Local time is spent on tier-1 gates, the
   mechanism tier, and the one shared campaign fixture.

---

## 2. The revised queue

Ordered by **cost**, not by theme. Prices marked *(measured)* are from this
session; *(estimate)* is derived from measured components and must be re-priced
with `--co` before it is trusted (TODO48 §5: no number is trusted without its own
measurement).

### R1 — LANDED — A mechanism tier: plumbing locks without training (NEW)
- **Landed (this session):** `tests/property/_fake_backend.py` (`FakeBackend`,
  `synthetic_record`) and `tests/property/test_round_loop_mechanism_lock.py`
  (6 fast tests + the sync test). Six mechanisms are asserted: relaunch adds no
  key and loses none; an all-fresh-less batch measures nothing *and raises the
  exhaustion signal*; the budget is charged for exactly what was stored; S10's
  COMPLETE reaches the loop (not the round limit); a rejected cell is classified
  and its siblings survive; and the fake/real key sets are identical.
  **11 tests, 31 s, one selection** — the six fast ones ~1 s total, the sync
  test ~3.2 s (the shared spec's projected price).
- **Cost, re-priced:** the fast tier is **~1 s per assertion**, not the
  17–26 s the campaign cells cost. The sync lock costs the oracle's projection.
- **Does:** a ~20-line fake `ExecutionBackend` in `tests/` that returns
  `Success(records=[Record.create(…)])` or `Failure(…)`. Everything the round
  loop decides is downstream of that: `_fresh_batch_items` (dedup/resume),
  `_persist_results` (store writes, rejection classification), `_charge_budget`,
  the S10 decision read, and the round-termination heuristics. Those become
  sub-second tests instead of 17–26 s ones.
- **Why first:** four of the five defects this session found in D3's own blast
  radius (the uncharged budget, the unread decision, two unconstructible
  policies, the re-proposing policies) were found by *training cells to check
  plumbing*. This tier is how that stops happening.
- **The honesty requirement — a synchronization lock.** A fake tier can drift
  from reality, so one lock runs the *same* tiny spec through the fake **and** a
  real `LocalBackend` and asserts the two runs store an **identical set of
  `measurement_key`s**. If they ever diverge, the fast tier is lying and the
  lock says which side moved. Falsifiable by making the fake skip the dedup.
- **Cost:** the fake ~0 s to run; the sync lock costs one real cell batch
  (~5–10 s *(estimate)*).

### R2 — LANDED — A price oracle: ask the fixture's questions without running it (NEW)
- **Landed (this session):** `computronium/experiment/execution/pricing.py`
  (`price_plan`, `PricePlan`) + the measured price table in
  `schema/registries.py` (`MEASURED_CELL_SECONDS`, `cell_price_seconds`), read by
  `_dry_run_report`. The oracle prints declared vs **legal** cells, the
  per-dynamics totals, the projected seconds, the cell a declared budget stops
  on, and **the primitives the axes name that no legal cell reaches**.
  Gate: `tests/property/test_price_oracle_lock.py` (4 tests) — declared cells ==
  stored keys on a real backend, the per-cell timed cost inside the published
  band (0.2x-4x), the stop index consistent with the ledger, and the
  unreachable line present.
- **It paid for itself on the first draft.** The shared fixture's first
  declaration paired `thermodynamic_contrast` with `instantaneous` dynamics and
  had **one legal cell out of two declared axes**, silently — TODO48 opportunity
  3, now a report line. The oracle also prices the shipped campaign:
  **declared 120 / legal 90 / 54.5 s** (`comp run --spec
  examples/learning-rules-and-geometry-digits.yaml --dry-run`).
- **Cost, measured:** the walk is bounded at **24 scanned candidates**
  (`iter_candidates` gained `max_scan`) because *composing a candidate costs
  ~60 ms* — see §0.2. Past the bound the totals are the sample mean
  extrapolated over the declared count and are printed as such. On the small
  specs the locks use, the bound is never reached.
- **Does:** `_dry_run_report` (`cli.py:315`) already builds the space through the
  runner's own builders and prints the first cells. Extend it to print **declared
  cell count, per-cell cost, projected total walltime, and where a declared
  budget would stop**. Every guess this session made by trial — "will
  `target_cells=6` stop after 7 records?", "how many cells does this space
  declare?", "is this fixture big enough to need three launches?" — becomes a
  print instead of a 10–15 s probe.
- **Gate:** the oracle's numbers are the ones the run then produces: declared
  cells == stored keys, and the projected total is within the published
  tolerance (D2 already computes s/record). Falsifiable: overstate the count and
  the oracle's own assertion goes red.
- **Cost:** <10 s *(estimate, tier 1)*. **Highest leverage per line in this
  file**: it converts fixture design from trial-and-error into measurement.

### R3 — LANDED — the settle early exit was honest; the campaign's step band was not
- **Landed:** `scripts/probes/settle_convergence.py` (the measurement),
  `tests/property/test_settle_convergence_lock.py` (6 tests, **~10 s**, no
  training), and one line in
  `examples/learning-rules-and-geometry-digits.yaml`.
- **The premise was wrong, and that is the finding.** The ticket assumed the exit
  never fires because the test is *absolute* (`delta < 1e-4`) rather than
  relative. Measured at the campaign's own regime (hidden 64, batch 2, horizon
  30, sweeps executed):

  | settle_step | 0.01 | 0.03162 | 0.1 | 0.3 | 0.5 | 1.0 |
  |---|---|---|---|---|---|---|
  | energy_minimization | 30 | 30 | 30 | 29 | 18 | 8 |
  | lazy | 30 | 30 | 30 | 29 | 18 | 8 |

  At every step size the shipped campaign could declare, EqProp contracts
  **0.919 per sweep**, so `1e-4` is unreachable inside 30 sweeps. A *relative*
  test is further away still (the ratio is 0.919, not < 1e-4), and the
  scale-free test the local-learning path already uses
  (`delta/‖out‖ ≈ 1.5e-3` at the horizon) says the same thing: **the settle has
  not converged, so the loop is right not to stop.** The test was never the
  defect; the *declared band* was — and it was a science defect, not a walltime
  one: every EqProp cell in the campaign was measuring an unconverged settle.
- **Does now:** the shipped spec's `settle_step` band is `[0.001, 1.0]` — the
  harvested ceiling — instead of the hand-narrowed `[0.001, 0.1]`. Two of the
  five sweep points are now steps at which EqProp converges, the exit fires, and
  the cells get cheaper *and* meaningful. The early exit is unchanged code.
- **Gate — mechanism plus declaration, both falsifiable:** claim 1, a converging
  settle stops before `max_steps` and the telemetry agrees with the flag in both
  directions; claim 2, **a shipped spec's declared band contains a step size at
  which each EqProp dynamics it declares converges.** Claim 1 was already
  covered by `TestSettleHorizonTelemetry`; claim 2 is the new one, and it is the
  claim a campaign fixture can violate invisibly — a non-converging settle
  returns a plausible state and a plausible number, and a run cannot say so.
  *Verified falsifiable:* narrowing the band back to `hi: 0.1` turns both
  parametrizations red with the message naming the sweeps.
- **A falsifiability check caught a bug in the lock, not in the code:** the
  first `_log_grid` interpolated as if `lo`/`hi` were already log values, so the
  grid sampled step ≈ 1.0 and the lock passed vacuously. Rejecting the narrowed
  band exposed it. Grid points are `3` and the epochs are real ones — a lock
  that cannot fail is worse than no lock.
- **Cost, measured:** probe ~40 s; lock 6 tests / ~10 s. **No kernel change and
  no `_dynamics.py` edit at all** — the saving R3 was promised (~150 s on R8)
  arrives as *correct cells* first and cheaper cells second.

### R4 — LANDED — Q1b: the multiplier table was 29 handicaps, and the rules were fine
- **Landed:** `scripts/probes/step_size_multipliers.py` (`--audit` composes every
  row, milliseconds, no training; `--ladder <pair>` is the control), the
  retirement of all 29 `step_size_override_*` rows in
  `schema/seed_registries.py`, and
  `tests/property/test_multiplier_floor_lock.py` (3 tests, **~1 s** of compose,
  no cells).
- **What the multiplier actually scales — the first wrong assumption here too.**
  `ontology/update.py::_apply_step_size_overrides` is the only reader, so the
  table multiplies the **parameter update lr** (swept as `update_lr`), not the
  settle step. TODO48's "effective lr 1.6e-6" was right; the first draft of this
  session's probe mislabelled the column and inherited the plan's framing.
- **The control settles it: the algorithms were never broken.** `energy_minimization
  x thermodynamic_contrast` — the campaign's own rule — trained on `digits` at
  gate 2b's reference regime, 10 epochs, ladder over the *composed* update lr:

  | composed update lr | 5e-7 (as registered) | 1e-4 | 1e-3 | 5e-3 | 1.6e-2 |
  |---|---|---|---|---|---|
  | `train_acc` | 0.105 | 0.080 | 0.411 | **0.878** | 0.767 |

  The rule reaches **0.878** train accuracy — four decades above the lr its own
  row hands it. Every "the algorithm does not learn" reading of the campaign's
  flat `train_acc ≈ 0.10` was the table.
- **Does:** all 29 rows re-registered at `mean: 1.0` with `confidence: 0.2` and
  a description recording the retired value and the ladder that retired it. The
  column could only ever attenuate (every registered value was `< 1.0`), none
  carried a measurement, and the swept `update_lr` now means what it says.
- **Gate (a lock after all, contra the ticket's own scope cut):** the ticket said
  a probe demonstrates provenance and a lock would only restate the registry.
  That is true of a *description* and false of a *floor*: **no registered row may
  compose an update lr below `LEARNING_FLOOR = 1e-3`**, the measured value from
  the ladder. The lock asserts the **composed** config, not the table, so a row
  whose *base* also moved cannot hide behind a nominal 1.0. A second claim holds
  the retirement honest: an attenuating row (`mult < 1.0`) must say `Retired` in
  its description. *Verified falsifiable:* re-registering the suspect row at
  `1e-4` turns the floor lock red, naming the pair and the composed lr.
- **Cost, measured:** audit ~3 s (28 composable rows, ~60 ms each); ladder 5 cells
  × ~45 s = **228 s**; lock 3 tests / ~11 s. Four `diffusion` rows are illegal on
  feedforward and one row (`diffusion_spectral_constrained`) names an *update*
  primitive, not a credit — the probe prints both instead of dropping them,
  because a silently narrowed audit reads as "audited".

### R5 — LANDED — E2: significance, on a constructed store (no training at all)
- **Landed (this session):** `computronium/experiment/evidence/significance.py`
  (`Significance`, `Resampling`, `paired_significance`, `MIN_SHARED_CELLS = 2`)
  over the existing statistics primitives — bootstrap CI, sign-flip
  permutation p, Cohen's dz. The report prints one line naming the test
  (`ReportGenerator.significance`, `_claims_section`). Gate:
  `tests/property/test_significance_lock.py` (7 tests, **11.6 s**, no cells).
- **The pairing is the mechanism.** `claims.pairing_key(record, axis)` is the
  cell's identity *minus the axis under test*, so two arms can only be paired
  on cells that differ in nothing else — including swept hyperparameters,
  because a cell trained at a different lr is not the same cell measured twice.
  `claims.cell_metrics_by_axis_value` groups qualified cells by that key;
  `claims._qualified_cells` is now the single definition of "a cell that may
  back a claim", shared by the claim table, the pairing and the report.
- **Three states, all expressible, none a failure:** a real difference prints
  `p=… — significant`; a flat one prints `p≈1.0 — not significant`; fewer than
  two shared cells prints `insufficient coverage (n shared cell(s), 2 required)
  — no test run` with `p_value is None`. The floor is enforced in
  `Significance.__post_init__`, so no caller can attach a p-value to coverage
  that cannot support one.
- **Silent nulls are a defect, so the null is printed.** `strongest_axis`
  returns `None` at zero spread, which would have left a tied run with *no*
  line at all — indistinguishable from a test never run. `_pair_under_test`
  falls back to the first axis carrying two values, so a tie is tested and
  reported as a tie.
- **Cost, measured:** the seven fast tests are **11.6 s**, of which ~10 s is
  three module-scoped store fixtures (5 seeds × 5 pairs × 2 arms each) and the
  10,000-draw resampling. The arithmetic itself is milliseconds.

### R6 — LANDED — F1 + F4 in one selection: the surface is locked, and versioned
- **Landed (this session):** `tests/property/test_cli_surface_lock.py` (18 tests,
  **4.6 s**, no cells). F1: every `_SUBCOMMANDS` entry appears in `comp --help`
  and vice versa (the two dicts are asserted equal), every command answers
  `--help` **through the dispatcher**, an unknown command exits 2 with no
  traceback, and every `POLICY_CATALOG` entry is constructible from a spec alone
  (opportunity 4). F4: `ASSESSMENT_PROCEDURE_VERSION` is now one registered
  constant instead of the literal `"1.0"` at six call sites,
  `RecordStore.query_records(min_assessment_procedure_version=…)` exists, and
  `procedure_version_key` orders versions numerically (`1.10 > 1.9`).
- **Two seams closed on the way:**
  1. **`RecordSource` was a protocol no real store satisfies** — it declared
     `query_records(run_id, limit)` positionally while the store's `limit` is
     keyword-only. Fixed, and locked *structurally* (parameter-kind
     compatibility), because `runtime_checkable` only checks the name exists.
  2. **Four of ten commands had no test reaching them** (`parity`, `repro`,
     `validate`, `joint-validate`): F1's "each has a test through the command
     surface" was stated but unexecuted. The parameterized dispatch test is that
     coverage.
- **F1:** every listed command appears in `--help`, every command in `--help` is
  listed, each has a test through the command surface — **plus** every
  `POLICY_CATALOG` entry is constructible from a spec alone via
  `create_policy(name, **policy_context(spec, name))`. Two of eight were not, and
  a help-text lock would never have found it (TODO48 opportunity 4).
  - **Rides along (one line, same seam class):** `RecordSource` — "the slice of
    the record store a policy needs" — declares `query_records(run_id, limit)`
    positionally while `RecordStore.query_records` is `(run_id, *, …)`. Every
    caller passes a `RecordStore`, so the protocol is a signature no real store
    satisfies. D3 made that dependency central (the resume filter reads through
    it). Pre-existing, not a D3 regression.
- **F4:** records carry `assessment_procedure_version`; a store query excludes
  records predating a change. More pressing after D3: a pre-D3 record means
  something a post-D3 record does not, and nothing in the store says so. Gate: a
  lock writes a record with an old version and asserts the store excludes it.
- **Cost:** <60 s *(estimate)*. **Paired** — both tier-1, one selection, no cells.

### R7 — F3: CI gates adopted (move wide work off the critical path)
- **Does:** TODO48's F3 — `ruff format --check` → `ruff check` → `pyright` →
  pytest → `pip-audit`. Encodes AGENTS.md's per-commit checklist so it cannot
  drift.
- **Why here and not last:** once it exists, R9's CP-3 shard selection and every
  future wide sweep run in CI instead of locally. Everything after this point
  gets cheaper; everything before it could not.
- **Gate:** the CI config exists and runs the gates; a deliberately broken format
  commit fails it in the setup commit, then is reverted.
- **Fold in (disk hygiene, §0.1):** delete `build/`, keep it ignored; add a
  `logs/` retention rule so a 370 MB log cannot recur. Two lines, and one of them
  removes a real grep hazard.

### R8 — LANDED (unverified gate) — ONE campaign run, four consumers

**Landed this session.** `tests/acceptance/conftest.py` (session-scoped,
cross-worker) + `tests/acceptance/_campaign.py` + `tests/acceptance/
test_campaign_evidence_lock.py` (11 tests). Four gates read one store: the owed
D3 verification, E3, F2, CP-1.

- **The cross-worker part is load-bearing, not decoration.** `addopts` carries
  `-n 4`, so a *module*-scoped fixture runs once per **worker** — the first
  draft paid the campaign twice for two modules and timed out at 300 s each
  (measured: 7 passed, 11 setup timeouts, 698 s). The store now lives at a path
  keyed by the declaration's content and a `FileLock`, so exactly one process
  builds it. **Measured: 18 tests across both modules in ~357 s.**
- **The cache key was wrong twice, and the second wrongness was mine.** Keyed
  on git HEAD + a dirty flag — which does *not* change when an already-dirty
  file is edited, so a store built before the E3 fix survived it and three
  gates read a store from the code they were meant to be testing. Keyed on the
  package's newest source mtime instead, which cannot lie. This cost ~20 min of
  gate runs; recorded because a gate's cache key must change on every edit.

**Three defects found, all real:**

1. **The contrast design had never once produced a record.** Two causes, both
   fixed: the per-origin `max(1, …)` counts summed past the round size and
   `data_origins[:total]` truncated away the two 5%-quota groups; and the
   registered stage spec allocated **nothing** for them. A 450-record campaign
   carried 250 exploration / 120 calibration / 80 test and **zero** control or
   contrast. Now 40/40. The allocator is largest-remainder, exact at every
   round size, and gives exploration away before it gives up a protocol group.
2. **Design metadata died in the scheduler.** `_fresh_batch_items` passed `{}`
   as every item's params, so S1's `data_origin` never reached a record.
3. **`lr=0` trains silently** — see §2.5.

**§8.1 item 1 is CLOSED.** The oracle's gap was two factors of *opposite sign*,
both large, neither visible from the other: it priced **cells** while a run
measures **records** (× `n_seeds`), and the price table is **serial** while a
run executes **4-way concurrent** (÷ 3.86). `scripts/probes/campaign_throughput.py`
measured the second (8 records, 1→4 workers: 0.867 → 0.488 s/record, 3.86×);
`MEASURED_PARALLEL_SPEEDUP` is now registered beside the price table, and
`FIXED_RUN_COST_SECONDS` moved out of a test literal into the registry.

**NOT VERIFIED: the acceptance gate never went green.** The session ended with
the campaign run in flight. `test_campaign_evidence_lock.py` and the rewritten
`test_campaign_lock.py` have never run together against a fresh store. Their
assertions are written and their fixtures work; their *verdicts* are unknown.
Cheap lock that *is* green: `tests/property/test_design_and_rate_lock.py`, 9
tests / 14 s, verified falsifiable both ways.

### R9 — NOT STARTED — §7 Completion Proof, with CP-3's breadth handed to CI

Unchanged from its original text; **R7's CI claim is already satisfied** —
`.github/workflows/ci.yml` runs ruff format → ruff check → pyright → pytest →
pip-audit, which is F3 exactly. Only the disk hygiene remains (§0.1: a
`logs/` retention rule; `build/` no longer exists on this tree). CP-1/CP-2 ride
R8's store once its gate is verified; CP-3 is one selection plus CI; **CP-4 and
CP-5 are documents and neither is worth more than TODO49** — see §6.

## 2.1 What R1/R2/R6 changed about the plan's own premises

Three measured facts the next session should not re-derive:

1. **The legality preview, not the cell, is the expensive thing.** Composing one
   candidate costs **~60 ms** (`geometry_param_count` builds real modules, 13
   calls per compose). A price oracle over a factorial is therefore a
   *bounded-sample* tool, and so is any lock that wants the whole space. Measured:
   the quick-verify profile's dry run spends **~88 s finding its first five legal
   cells** — pre-existing, not caused by R2, and the reason R2 adds a scan bound.
2. **A wall clock is not a projection.** The first version of R2's gate compared
   the run's *elapsed* time with the per-cell projection and failed at 4.12x: a
   run pays ~10 s of fixed cost (stage dispatch, legality preview, torch's first
   touch) that no per-cell price can include. The gate now compares the cells'
   own timed cost and asserts elapsed < projection + a published fixed-cost
   constant.
3. **An exhausted space can end two different ways, and only one is a signal.**
   A policy whose stream is *empty* proposes nothing, so the all-seen batch never
   forms and `last_batch_was_all_seen` stays false; the run is ended by
   `_MAX_FRUITLESS_ROUNDS` instead. Both terminate, but only one names its
   reason in the log. Locked as two separate claims rather than one.

## 2.2 New improvement opportunities (raised by R1/R2/R6)

1. **The pre-existing 88 s dry run is the next tier-1 cost.** `comp run
   quick-verify --dry-run` spends its time in `_composable`, i.e. building
   geometries to answer "would this cell compose". Legality is asked of
   `SystemConfig.validate` on purpose (no second source of truth), but a
   *counting* question ("how many cells are legal") does not need the geometry's
   parameter count — the compose itself would do. A cheap legality predicate for
   counting, with the full compose kept for the cells that survive, would make
   every oracle and every pool query orders of magnitude cheaper.
2. **Two declarations, two declared counts.** For the shipped campaign the
   oracle reports *declared 120, legal 90*: `declared_cell_count` multiplies by
   the longest sweep ladder while `iter_candidates` de-duplicates identical
   measurement keys, so the status line's "Declared Cells" overstates the work by
   a third. Both numbers are correct about different things; a reader comparing
   them has no way to know which to believe. One name each, or one line that
   prints both, would settle it.
3. **The `RecordSource` mismatch was a symptom.** `runtime_checkable` passed a
   protocol no store satisfies for as long as the two existed. A structural
   protocol lock (this file's) belongs next to every `Protocol` in the execution
   seam, not just this one.
4. **CLOSED by R5 — E2 is written against the fake tier.** `synthetic_record`
   gained one keyword, `metric=`, which overrides its key-derived spread: a
   lock that needs a *known* delta declares the number instead of hoping the
   hash produces one. The fixture that §2.2 described is now
   `tests/property/test_significance_lock.py`.

## 2.4 New improvement opportunities (raised by R3/R4)

1. **Every number the campaign reports was computed at a step size nothing in
   the campaign could declare.** The shipped `settle_step` band is now the
   harvested one, so the price regime (`MEASURED_CELL_SECONDS`, `dynamics_cost.py`)
   is measured at `settle_step=0.03162` — inside the old band but at its very
   top, and *outside* nothing. It should be re-measured at a step the campaign
   now sweeps across, and the table should carry a *step-size axis*, not one
   representative cell. This is the same defect §2.3 item 4 named for the credit
   axis, one axis further out.
2. **`LEARNING_FLOOR` is measured on one rule and applied to 29 rows.** The
   floor (`1e-3` composed update lr) comes from `energy_minimization x
   thermodynamic_contrast`; the lock holds every row to it. That is the right
   direction to be wrong in — a rule that cannot reach a floor another rule
   clears is suspect — but the honest form is a floor *per rule*, measured by
   `--ladder`, stored beside the row. Twenty-eight ladders at ~45 s each is one
   detached run, and it would replace a generalized constant with 29
   measurements.
3. **The multiplier column was not the only unmeasured prior.** `ruler_lr_*`
   (three rows) and the 28 `step_size_*_override_*` priors (the *dynamics*
   step size, a different table) carry the same "registered, never verified"
   character, and `confidence=0.8` on all of them is a number nothing measures.
   `confidence` is the field that should be falsifiable, and today it is
   decoration: a lock that a prior's confidence agrees with its provenance would
   have caught both tables.
4. **A shipped hyperparameter band is a scientific claim with no gate of its
   own.** R3's fix was a spec edit found by measurement; R3's lock is the first
   thing that will stop the next one. Two bands are now unchecked and were
   narrowed by hand for the same reason: `update_lr: [0.001, 0.1]` (the ladder
   says the interesting range starts at 1e-3, i.e. *at* the band floor, so
   three of five declared points are below anything measured) and
   `hidden_dim: [32, 256]` (no claim behind it at all).
5. **Four of the 29 multiplier rows are illegal on the campaign's geometry**
   (`diffusion` requires recurrent), and one names an *update* primitive in a
   credit column. So the table has rows the campaign cannot reach and a row that
   is not a pair — the same "a declared axis must offer what the campaign claims
   to compare" seam as TODO48 opportunity 3, in a *registry* rather than a spec.
6. **Pre-existing, found by the R3/R4 regression run (Register C, not this
   session's work):** `tests/property/test_run_spec_lock.py` has two failures
   that are identical at HEAD — the lock declares `step_size` as a run-swept
   hyperparameter and the harvested schema only publishes `settle_step`
   (`schema/harvest.py:72` maps one to the other). One name, two vocabularies.

## 2.3 New improvement opportunities (raised by R5)

1. **A tie is now a first-class report state; a *thin* run is not.** A run with
   <2 shared cells prints "insufficient coverage", but nothing counts
   *unpaired* cells: an arm measured 5 times against an arm measured once
   reports a coverage number (1) without saying the other 4 cells went
   unmatched. `Significance` could carry `unpaired` and the report could name
   it — the difference between "we tested little" and "we had data and could
   not pair it".
2. **One axis is tested per report.** `_pair_under_test` picks the widest (or
   first two-valued) axis and stops. A factorial declares several, and each
   one's verdict is a separate question a reader will ask; the machinery is
   per-axis already, so the report section is what limits it to one.
3. **`preregistration.paired_comparison` and `significance.paired_significance`
   are the same test with two floors.** The former raises below 5 *seeds*; the
   latter refuses below 2 *cells*. One function taking the floor as a parameter
   would remove the duplication — with the caveat that they pair on different
   identities (index-matched seeds vs. matched cells), which is the reason they
   have not already converged.
4. **R2's oracle prices one representative cell; a campaign is a *mix*.** §8.1
   measures the consequence: the published regime said the budget could not
   bind and it bound at 91% of the space. `price_plan` should aggregate a
   per-cell cost over the dynamics × credit the plan actually declares (it
   already prints per-dynamics totals — the credit axis is what's missing), so
   "budget: never binds" stops being a claim about a single cell.
5. **Pre-existing, found by pyright while R5 ran:** `RecordSource` is still
   unsatisfied by `RecordStore` at `execution/stages_impl.py:60,157` — the same
   protocol-vs-store mismatch R6's structural lock was meant to close, in a
   *different* file. The lock asserted one seam; the seam class is wider.

---

## 3. Scope explicitly cut, and why the proof is intact

| cut | why it is not a weakened claim |
|---|---|
| plumbing locks train **no cells** | the mechanism tier (R1) asserts the same behaviour against an injected backend, and the sync lock ties the fast tier to a real run |
| Q1b becomes a probe, not a gate | its claim is a table's *provenance*; a probe demonstrates it and a lock would only restate the registry |
| CP-4, CP-5 run no tests | one is a table, one is a person reading a README |
| CP-3's shards run in CI, not locally | the same assertions, executed where breadth is free; the local path keeps only tier-1 and the mechanism tier |
| no campaign run per ticket | four consumers read one store; the *assertions* are unchanged, only the measurement is deduplicated |
| perf is gated on mechanism, not walltime | a walltime assertion is flaky under `-n 4`; "the exit fires" is falsifiable and stable |

**Not cut:** every falsifiability claim in TODO48 stands. If removing a
mechanism must turn a lock red, it still does — including the mechanism tier,
which is exactly why R1 carries a synchronization lock.

---

## 4. Process fixes (runnable; each one has already cost time)

- **Detached background gates.** `nohup … &` from a shell the tool may kill is
  not background:
  ```
  setsid nohup uv run python -m pytest <selection> -q -rf --tb=line \
      > logs/<name>.log 2>&1 < /dev/null &
  ```
  Poll at ≤2 min with a pre-registered kill time. A killed run yields no verdict:
  `--co` to locate, never `--lf` (TODO47 §1 / AGENTS.md — `lastfailed` already
  holds 520 stale entries).
- **Dry-run every fixture, then price it.** `comp run --spec … --dry-run` (and
  R2's extension) prints the plan, the cell count and the stop point, and refuses
  the illegal. The Q2/E4 session lost five red runs to spec-authoring errors; R2
  removes the guesswork that produced them.
- **One parameterized probe, not four throwaways.** This session wrote
  `probe_budget`, `probe_d3`, `probe_d3b`, `probe_d3c` to answer four related
  questions; one script with a table would have answered all four in one run.
- **Size fixtures to the claim, not to the kernel.** A lock about resume does not
  need EqProp: `instantaneous` cells are 8.8× cheaper and the lock asserts
  nothing about learning. Reserve `energy_minimization` for the locks whose
  property *is* EqProp's (gate 2b, the campaign).
- **Read the store, don't re-measure it.** Prefer
  `RecordStore.query_records` over a pipeline run when a lock needs evidence —
  TODO48's own run-ledger lock does exactly this.
- **Respect the 120 s per-test timeout** (`pyproject.toml`) unless the mark
  raises it, as `test_campaign_lock.py` does with `pytest.mark.timeout(900)` —
  consolidation must not build a fixture that dies mid-file.
- **Delete `build/` and prune `logs/`** (§0.1): a 714-file stale copy of the
  package is a grep hazard, and 446 MB of logs is unbounded growth.

---

## 5. Decisions needed from the operator

- **D-j — the 5 pre-existing `test_sampler_lock.py` failures.** They fail
  **identically at HEAD** (verified by stash this session) and they block CP-3's
  "all structural locks green". Options: (i) fix them (cost not estimated);
  (ii) **waive with a record** — a lock pinning the waiver, so a *new* failure of
  any kind goes red while the five known ones are enumerated.
  *Recommendation:* (ii). Not in D3's blast radius, not regressions, and a waiver
  lock that fails on anything new is honest and cheap.
- **D-k — RESOLVED (Session B): do R3 before or after the cheap tickets?** It is
  the largest single *total-time* saving, but R1+R2 make everything else cheap
  enough that R3's value is mostly on R8's 150 s.
  *Recommendation:* **after R1/R2/R5/R6** — those are minutes, and R3 is a kernel
  change in Phase D rather than a Phase E/F claim. Revisit once R8 has a price.
  **Outcome: the premise was wrong and the decision was moot.** R3 was not a
  kernel change; it was a one-line spec edit, and its payoff is *correct cells*
  (converging settles) before it is cheaper ones. Session B did it after the
  cheap tickets, as recommended, at a cost of ~4 min.
- **D-l — is CI trusted for breadth?** R7's whole value is moving CP-3's shards
  off the local path. If CI is not wired to run on pushes here, R7 buys
  documentation rather than time and should leave the critical path.
- **D-n — gate 1's coverage assertion races its own budget.** The campaign
  spec caps walltime (`budget_seconds: 300`), so "every legal cell was
  measured" is only true on a fast enough box (§8.1: 70 of 74 measured, 354 s
  consumed). *Recommendation:* assert coverage of the cells the budget allowed
  and read the shortfall as a priced fact (D2 already computes s/record), or
  drop the cap from the gate's spec. Until then gate 1 is a coin flip on load —
  which is worse than a lock, because it looks like one.
- **D-m — is the mechanism tier (R1) allowed to assert on a fake backend?**
  Without the sync lock it would be a fast tier that can drift; with it, it is
  two locks instead of one slow one. *Recommendation:* yes, and never ship R1
  without the sync lock in the same commit.

---

## 5.5 What this session cost, and where the plan itself is wrong

**Three of this session's six changes touch nothing a user can reach.** The
fixture reorganization, the metadata threading, and the cache key are all
test-infrastructure. The price oracle and the `lr=0` fix reach a user; the
contrast design reached nothing because it had never run. That ratio is the
honest one, and it is a fact about *this plan's* subject matter, not about the
session: TODO46–48b is a plan about measurement honesty, and measurement honesty
is not usability.

**The plan's own ordering is the defect.** It schedules CP-5 — *a person who has
never read this repo follows the README* — last, as "document work, no gates, no
runs". CP-5 is the **only** usability signal in the entire file, and it is the
one item that would have caught `lr=0` by inspection rather than by a probe.
Everything before it verifies systems that already exist.

**Recommendation, recorded so the next session does not re-derive it:** TODO49
is the better use of the next hours, and it supersedes R9's remaining scope
except where R9 asserts something TODO49 does not. CP-4 (the defect-class ledger)
is an argument in a document and should be dropped or deferred indefinitely; it
produces no capability and gates nothing.

### 5.6 Two things a future session must not re-derive

1. **A gate's cache key must change on every code edit.** Keyed on git HEAD plus
   a dirty flag, it does not — the flag is already set. This cost ~20 minutes of
   gate runs reading a store built before the fix. Key on a content digest of the
   declaration *and* the package's newest source mtime.
2. **`-n 4` means a module-scoped fixture runs once per worker.** "One fixture,
   many consumers" is false across processes unless the store path is derived
   from the input and guarded by a file lock. Measured: 698 s and eleven setup
   timeouts for the naive version, ~357 s for the fixed one.

## 6. Session ordering and the exit

**Session A (minutes, no cells):** R1 (fake backend + sync lock) → R2 (price
oracle) → R6 (F1+F4) → R5 (E2). **LANDED.**
**Session B: R3 (the settle early exit) → R4 (Q1b). LANDED** — and both landed
as *declaration* fixes rather than code fixes: one spec line and 29 registry
rows. No kernel change, no `_dynamics.py` edit, ~4 min of local gate time.
**Session C (the one campaign):** R8 — one run, four consumers — then R7 (CI).
R8's price must be re-taken first: the cells it measures are now different
cells (converging settles, un-attenuated update lrs), so §8.1's 5.06 s/cell and
the oracle's 81.7 s projection are both stale.
**Session D (paper):** CP-4 ledger, CP-5 walk, then close the plan.

Local gate time, from the measured components:

| path | local gate time |
|---|---|
| TODO48's order as written | ~35–45 min *(estimate)* |
| this file, R1+R2 included | ~12 min *(estimate)* |
| this file, R1+R2+R3+R4 | **~6 min** *(measured: 25 s + 26 s selections)* |

The exit is unchanged: CP-1..CP-3 green (breadth in CI), CP-4's table complete,
CP-5 walked. Then TODO48.md closes and the plan files stop growing.

---

## 7. What did not change

The goal, the terminal state, and every gate's *claim*. TODO48's definition of
done — one command, minutes not hours, every number derivable from the store,
every claim carrying its uncertainty, every seam locked — is not renegotiated
here. Only the order of arrival, and the number of times the same 450 cells get
measured.

---

## 8. Session log

- **Session B landed R3 + R4 (fifth session of the plan), and the operator's
  challenge is what made R4 correct.** The mid-session report showed
  `train_acc ≈ 0.07` for most EqProp credit rules and the read was "these
  algorithms do not learn". That read was wrong, and the check that killed it
  was a *ladder* rather than another point: the same
  `energy_minimization x thermodynamic_contrast` cell reaches **0.878** train
  accuracy at composed lr 5e-3 and 0.105 at the 5e-7 its registry row hands it.
  Nothing was broken; a 29-row multiplier column was multiplying every update lr
  by an unmeasured factor below 1.
  - **Both tickets were premise corrections, not implementations.** R3 promised a
    kernel change to the convergence test and needed a one-line spec edit; R4
    promised "one 10-epoch probe per row" and needed *one* control plus 29
    registry rows. AGENTS.md's "be skeptical of low-performing experiments; this
    could indicate an implementation defect" applies to the *plan* here as much
    as to the code: three of this session's four assumptions (relative-vs-
    absolute convergence, the multiplier scaling the settle step, the row's
    effective lr being 1.6e-6 rather than 5e-7) were wrong before measurement.
  - **Cost, measured:** settle probe ~40 s; R3 lock 6 tests / ~10 s; multiplier
    audit ~3 s; ladder 5 cells / **228 s**; multiplier lock 3 tests / ~11 s.
    Regressions (schema seam, wp10 learning integration, active space, search
    space, run spec, schedule device, harvest schema gate 2, ontology locks and
    parity, role-split update, eqprop locality, gradient equivalence, price
    oracle, cell evaluation, round loop, significance, cli surface, claim report,
    campaign economics, state dynamics protocol) **239 passed / 26 s** plus a
    97-test first pass. ruff and pyright clean on every changed file.
  - **Do not repeat:** the probe harness is `cell_record(Coordinate, Schedule,
    Provenance)` — a direct cell, no store, no run. It is the cheapest way to
    measure one coordinate and the R4 ladder used nothing else.
  - **Do not repeat:** `test_run_spec_lock.py` has two failures that are
    identical at HEAD (verified by `git stash`); they are Register C, recorded
    in §2.4 item 6, and not this session's to fix.

- **R5 landed; Session A is done (fourth session of the plan).** The
  mechanism tier did exactly what §2.2 item 4 predicted: E2 needed a *store*,
  not a cell, and the whole ticket — model, report line, three-state verdict,
  seven tests — cost ~150 lines and no training. The pairing key was the part
  worth naming: an axis comparison over a factorial is only honest if the two
  arms are matched on everything *else*, and that had to be an identity, not an
  assumption.
  - **Falsifiability held:** removing the axis from `pairing_key` makes every
    arm unmatchable and the lock reads "insufficient coverage"; pairing on the
    whole `cell_key` does the same. `Significance.__post_init__` refuses a
    p-value under the coverage floor, so a future caller cannot skip the check.
  - **Cost notes:** ruff + pyright clean on all four changed files; the
    significance lock is 7 tests / 11.6 s, `test_claim_report_lock.py` +
    `test_campaign_economics_lock.py` 30 passed / 59 s, the R1 and R6 locks 25
    passed / 29 s. One behavioural change rode along and was deliberate: a run
    whose arms *tie* now prints a tested null instead of nothing (§2.3 item 2's
    sibling claim, on `strongest_axis`'s zero-spread `None`).
  - **Do not repeat:** `synthetic_record(metric=…)` is the override; do not
    rebuild the spread by hand-writing payloads, which would bypass the record
    schema the store enforces.
### 8.1 A defect class found by R5's regression run (CP-4 material, not R5's)

`tests/acceptance/test_campaign_lock.py` gate 1 failed in R5's regression
selection: **"4 legal cell(s) went unmeasured"** (1 failed, 6 passed, 368 s).
It is not an R5 regression — nothing in R5's diff touches the runner, the
space, or the store — and the cause is quantitative, not a mystery:

| fact | measured | source |
|---|---|---|
| the spec declares a **walltime** cap | `budget_seconds: 300` | `examples/learning-rules-and-geometry-digits.yaml` |
| the run consumed | **354.4 s**, 350 outcomes, **70 cells**, 7 rounds | the run log |
| the space yields | **74** legal cells | gate 1's own `iter_candidates` |
| R2's oracle projects | **81.7 s** (≈3.4 s/cell), "budget: never binds" | `comp run --dry-run` |
| measured per cell | **≈5.06 s** | 354.4 s / 70 |

So gate 1 asserts *space coverage* against a run that is **budget-capped**:
whether `measured == legal` holds is a race between the budget and the space,
decided by how fast this box was that day. That is a lock whose fixture does
not contain the case it exists for, in AGENTS.md's terms — and it is a
**flaky gate**, not a stable one, so it must not be read as either a
regression or a green.

Two things follow, and both are open:

1. **R2's price regime understates this mix by ~1.5×.** The published regime is
   `gradient` credit on `feedforward`; the campaign's cells are dominated by
   `energy_minimization`, whose settle loop never early-exits (R3). The oracle
   says the budget cannot bind; the budget binds at cell 70 of 74. Either the
   price regime needs a per-cell-cost *mix* rather than one representative
   cell, or the budget charge is not the oracle's cost — **unresolved**, and
   cheap to settle with the oracle's own inputs (no run needed).
2. **Gate 1 needs a decision from the operator (see §5, D-n).** Either the
   gate's spec drops `budget_seconds` so coverage is a property of the space,
   or the gate asserts coverage *of what the budget allowed* and the budget
   becomes part of the fixture. Both are honest; the current one is neither.
- **R1 + R2 landed (third session of the plan; the one before described both and
  built neither).** The queue's own costing was right: the four Session-A
  tickets are minutes, and the two that needed new machinery are ~90 lines and
  two lock files. Details are on each ticket; the three facts a future session
  should not re-derive are in §2.1 and the four new opportunities in §2.2.
  - **Ordering note:** R6 (F1+F4) went before R5 (E2) because F1's own premise
    turned out to be false — four commands had no test reaching them — and a
    surface lock is cheap while a significance feature is not. R5 remains
    Session A's last item and is now the cheapest ticket left in the plan.
  - **Cost notes:** ruff and pyright clean on every changed file. Pre-existing
    findings left alone (Register C): one `noqa`-wording row in
    `stages_impl.py`, one `try`-clause finding in `store.py`, four files in
    `tests/property/` that a whole-directory `ruff --fix` would have touched.
    A regression selection (claims, stage model, scientific-validity protocol,
    schema seam, registry completeness, run ledger) is **103 passed, 55 s**.
  - **Do not repeat:** `ruff check --fix tests/property/` rewrites the whole
    directory's legacy findings. Lint the files you changed, by name.
