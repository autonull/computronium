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

### R3 — The settle loop stops early (kernel; discounts everything after it)
- **Does:** the convergence exit in `_dynamics.py:3066(_sweep)` / `:1370(_observe)`
  never fires at campaign fidelity, so all 30 steps run every sweep. Either the
  test becomes relative (`delta / delta_prev`) or the sweep batches across cells
  differing only in a swept hyperparameter. TODO48 opportunity 1.
- **Gate — mechanism, not walltime:** a property test that a settle whose delta
  falls below threshold **stops before `max_steps`**, plus the probe's own table
  (`scripts/probes/dynamics_cost.py`) as the recorded measurement. A walltime
  assertion would be flaky on a loaded machine and under `-n 4`; the early exit
  is the mechanism, and restoring the fixed loop falsifies it.
- **Cost:** probe ~60 s *(measured)* + one tier-1 lock <10 s *(estimate)*.
- **Caveat, measured not assumed:** CUDA *is* available on this box, so the
  0.710 s/cell already includes GPU dispatch. Re-price after the fix; if the
  gain is smaller than the 8.8× CPU gap implied, R3's payoff is the mechanism
  (a correct early exit) rather than the walltime.

### R4 — Q1b: the multiplier table is a prior, not a verdict
- **Does:** TODO48's Q1b. For each `(dynamics, credit)` row, one 10-epoch probe
  at prior-center lr; the known-suspect row
  `("energy_minimization", "thermodynamic_contrast"): 0.00005` (effective lr
  1.6e-6 — a cell that cannot learn by construction, in the table the campaign
  compares rules through) is re-registered with its measurement or retired.
- **Scope cut:** a **probe and a registry edit, not a pytest gate.** Its claim is
  a table's provenance, which a probe demonstrates and a lock would only
  restate. One parameterized script (this session's four throwaway probes are the
  argument for writing one).
- **Cost:** ~120 s of probing *(estimate)*, once.

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

### R8 — ONE campaign run, four consumers (the owed D3 verification rides here)
- **Does:** a module-scoped `campaign` fixture in `tests/acceptance/conftest.py`,
  executed **once through the command surface** (`comp run` → `status` →
  `report`), serving:
  1. **the owed D3 verification** (round loop, budget, record schema, policies),
  2. **E3** — the report names the control; the lock asserts its presence,
  3. **F2** — every README pipeline number traces to a store record or a test
     assertion, plus the second tiny example with its measured walltime,
  4. **CP-1** — declared records == stored records, walltime within D2's
     projection, claims carry uncertainty and significance, non-empty promotion
     history.
- **The saving, stated plainly:** four consumers × ~150 s *(measured)* ≈ 600 s of
  duplicated measurement becomes one ~150 s run (less after R3). **The single
  largest saving in the refactor.**
- **Falsifiable:** break the budget charge or the round loop and CP-1/gate-1 go
  red exactly as they would have.
- **Cost:** ~150 s *(measured, pre-R3)* + seconds of report assertions.

### R9 — §7 Completion Proof, with CP-3's breadth handed to CI
- **CP-1** rides R8 — free. **CP-2** rides R8's store plus the promotion lock
  (~8 s *(measured)*). **CP-3**'s structural locks are cheap and run as one
  selection; **its shard run (~10 min *(measured)*) moves to CI** under rule 7.
- **CP-4** (the defect-class ledger) and **CP-5** (fresh eyes through README) are
  **document work and a manual walk**: no gates, no runs.

---

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
- **D-k — do R3 (the settle-loop fix) before or after the cheap tickets?** It is
  the largest single *total-time* saving, but R1+R2 make everything else cheap
  enough that R3's value is mostly on R8's 150 s.
  *Recommendation:* **after R1/R2/R5/R6** — those are minutes, and R3 is a kernel
  change in Phase D rather than a Phase E/F claim. Revisit once R8 has a price.
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

## 6. Session ordering and the exit

**Session A (minutes, no cells):** R1 (fake backend + sync lock) → R2 (price
oracle) → R6 (F1+F4) → R5 (E2).
**Status: R1, R2, R5 and R6 all landed — Session A is complete.** No cells
were trained to land any of them. **Session B (R3 settle early exit → R4 Q1b
probe) is next**, and its price is now the largest single item left.
**Session B (one kernel change, re-priced):** R3 (settle early exit) → R4 (Q1b
probe).
**Session C (the one campaign):** R8 — one run, four consumers — then R7 (CI).
**Session D (paper):** CP-4 ledger, CP-5 walk, then close the plan.

Local gate time, estimated from the measured components:

| path | local gate time |
|---|---|
| TODO48's order as written | ~35–45 min *(estimate)* |
| this file, R1+R2 included | ~12 min *(estimate)* |
| this file, R1+R2+R3, with CI absorbing breadth | **~5 min** *(estimate)* |

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
