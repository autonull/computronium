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

### R1 — A mechanism tier: plumbing locks without training (NEW)
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

### R2 — A price oracle: ask the fixture's questions without running it (NEW)
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

### R5 — E2: significance, on a constructed store (no training at all)
- **Does:** a paired permutation test over shared cells; the report names the
  test and prints the p-value beside the claim; fewer than 2 cells per rule
  yields "insufficient coverage", a finding rather than a failure.
- **Gate:** a constructed store where rule A beats B by 3σ of its spread asserts
  the p-value is printed; a flat store asserts the honest null. No pipeline, no
  cells, no campaign — which is the whole point of building the store by hand.
- **Cost:** <5 s *(estimate, tier 1)*.

### R6 — F1 + F4 in one selection: the surface is locked, and versioned
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
- **D-m — is the mechanism tier (R1) allowed to assert on a fake backend?**
  Without the sync lock it would be a fast tier that can drift; with it, it is
  two locks instead of one slow one. *Recommendation:* yes, and never ship R1
  without the sync lock in the same commit.

---

## 6. Session ordering and the exit

**Session A (minutes, no cells):** R1 (fake backend + sync lock) → R2 (price
oracle) → R5 (E2) → R6 (F1+F4).
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