# TODO48b.md — Finish TODO48 Faster: One Campaign, One Session, One Gate

**Binding:** `AGENTS.md` in full. **Binding:** `TODO48.md` in full.
**Relationship:** TODO48.md's §2 queue is **not** cancelled — it is the evidence
record of what each ticket claims and which lock proves it. This file changes
only **order, cost, and scope of execution** for the tickets TODO48 leaves open.
Every gate TODO48 names still asserts the same thing; what this file removes is
*duplicated measurement*, never an assertion.

**Supersedes:** the remaining-queue ordering in TODO48.md §4 step 3 onward.

---

## 0. Why this file exists: the cost is in the fixture, not the gate

Measured on this box (16 cores), 2026-10-03:

| thing | cost | share of a campaign run |
|---|---|---|
| DuckDB open / append / query | 29 ms / **2.9 ms per record** / 30 ms per 450 rows | **~1%** |
| one campaign cell (EqProp, L0/1ep/`batch_limit 2`) | **0.710 s** | ~100% |
| the same cell with `instantaneous` | **0.084 s** | — |
| pytest collection, one acceptance file | 3.9 s | per-invocation tax |
| the campaign lock | ~150 s (450 cells) | — |

Every remaining ticket's cost is dominated by **measuring cells**, and the
campaign lock alone is ~150 s that four separate tickets would each pay again.
The store is not the bottleneck and was never going to be (TODO48 opportunity 2),
so no time is spent tuning it.

Three measured facts drive the whole refactor:

1. **EqProp is 8.8× the cheapest primitive** for the same forward/backward, and
   ~80% of a cell is the settle loop, whose convergence early-exit **never
   fires** at campaign fidelity (`scripts/probes/dynamics_cost.py`). Every gate
   that measures cells is paying that 8.8× over and over.
2. **One campaign run can serve four consumers** (the owed D3 verification, E3,
   F2, CP-1) — but only if they share one fixture. Today the fixture is
   module-scoped *inside one file*, so any second file re-measures all 450 cells.
3. **A background gate dies with the shell that launched it.** This session lost
   a 150 s campaign run that way. It is a two-second fix (§4) and it is not
   optional: an unrun gate is not a green gate.

---

## 1. Six rules that buy the time back

1. **One fixture, many consumers.** A module-scoped fixture in
   `tests/acceptance/conftest.py` serves every campaign-dependent gate in the
   same session. A run is measured once and *read* many times.
2. **Cheap locks first, expensive fixture late.** Property-tier locks
   (constructed stores, no training) iterate in seconds; the campaign is run once
   at the end, when the assertions around it have stopped moving.
3. **No pytest invocation without a price.** `--co` before any selection whose
   runtime is unknown; `-n 4` is already in `addopts` and is not overridden for
   small selections.
4. **A gate runs once, after its work lands** (TODO48 §1). Unchanged — but a
   gate that a *later* ticket covers is re-paid once, at the phase sweep, never
   per ticket.
5. **Background means detached.** `setsid` + a log file. A `nohup … &` from a
   shell the tool may terminate is not background, it is a wish.
6. **CI absorbs breadth.** Once F3 exists, wide selections (CP-3's shards) run
   in CI, not on the critical path of the next ticket. Local time is spent only
   on tier-1 gates and on the one shared campaign fixture.

---

## 2. The revised queue

Ordered by **cost**, not by theme. Prices marked *(measured)* are from this
session; *(estimate)* is derived from measured components and must be re-priced
with `--co` before it is trusted (TODO48 §5: no number is trusted without its
own measurement).

### R0 — The settle loop stops early (kernel; makes every later gate cheaper)
- **Does:** the convergence exit in `_dynamics.py:3066(_sweep)` / `:1370(_observe)`
  never fires at campaign fidelity, so all 30 steps run every sweep. Either the
  test becomes relative (`delta / delta_prev`) or the sweep batches across cells
  that differ only in a swept hyperparameter. TODO48 opportunity 1.
- **Why first:** it is the only item on this list that makes *other* items
  cheaper. At `instantaneous`-class cost the campaign lock drops from ~150 s to
  ~40 s *(estimate)* and every cell-measuring gate with it.
- **Gate — mechanism, not walltime:** a property test that a settle whose delta
  falls below threshold **stops before `max_steps`**, plus the probe's own table
  (`scripts/probes/dynamics_cost.py`) as the recorded measurement. A walltime
  assertion would be flaky on a loaded machine and would be a bad lock; the
  early-exit is the mechanism and is falsifiable by restoring the fixed loop.
- **Cost:** probe ~60 s *(measured)* + one tier-1 lock <10 s *(estimate)*.

### R1 — Q1b: the multiplier table is a prior, not a verdict
- **Does:** TODO48's Q1b. For each `(dynamics, credit)` row, one 10-epoch probe
  at prior-center lr; the known-suspect row
  `("energy_minimization", "thermodynamic_contrast"): 0.00005` (effective lr
  1.6e-6 — a cell that cannot learn by construction, in the table the campaign
  compares rules through) is re-registered with its measurement or retired.
- **Scope cut:** this is a **probe and a registry edit, not a pytest gate.** Its
  claim is about a table's provenance, which a probe demonstrates and a lock
  would only re-state. One script, one output, one commit.
- **Cost:** ~120 s of probing *(estimate)*, run once.

### R2 — E2: significance, on a constructed store (no training at all)
- **Does:** a paired permutation test over shared cells; the report names the
  test and prints the p-value beside the claim; fewer than 2 cells per rule
  yields "insufficient coverage", a finding rather than a failure.
- **Gate:** a constructed store where rule A beats B by 3σ of its spread asserts
  the p-value is printed; a flat store asserts the honest null. **No pipeline,
  no cells, no campaign** — this is the whole point of building the store by
  hand.
- **Cost:** <5 s *(estimate, tier 1)*.

### R3 — F1: the CLI surface is a locked surface — **plus catalog construction**
- **Does:** TODO48's F1, extended per TODO48 opportunity 4: the lock also
  asserts every `POLICY_CATALOG` entry is constructible from a spec alone via
  `create_policy(name, **policy_context(spec, name))`. Two of eight entries were
  not, and a `--help`-text lock would never have found it. Free: same lock.
- **Rides along (one line, same seam class):** `RecordSource` — "the slice of
  the record store a policy needs" — declares `query_records(run_id, limit)`
  positionally, while `RecordStore.query_records` is `(run_id, *, …, limit, …)`.
  Every caller passes a `RecordStore` into `ProposalContext.evidence`, so the
  protocol is a signature no real store satisfies: a stated seam that is not
  one. D3 made that dependency central (the resume filter reads through it), so
  the protocol should say what the store actually offers. Pre-existing, not a
  D3 regression.
- **Cost:** <60 s *(estimate, per TODO48's own gate)*.

### R4 — F4: version the measurements
- **Does:** TODO48's F4 — records carry `assessment_procedure_version`; a store
  query excludes records predating a given change. This matters more after D3:
  a pre-D3 record means something a post-D3 record does not, and nothing in the
  store says so.
- **Gate:** a lock writes a record with an old version and asserts the store can
  exclude it; the campaign spec carries the current version.
- **Cost:** <10 s *(estimate)*. **Pairs with R3** — both tier-1, one selection.

### R5 — F3: CI gates adopted (move wide work off the critical path)
- **Does:** TODO48's F3 — `ruff format --check` → `ruff check` → `pyright` →
  pytest → `pip-audit`. Encodes AGENTS.md's per-commit checklist so it cannot
  drift.
- **Why here and not last:** once it exists, R7's CP-3 shard selection and any
  future wide sweep run in CI instead of locally. Everything after this point
  gets cheaper; everything before it could not.
- **Gate:** the CI config exists and runs the gates; a deliberately broken
  format commit fails it in the setup commit, then is reverted.

### R6 — ONE campaign run, four consumers (the owed D3 verification rides here)
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
- **The saving, stated plainly:** four consumers × ~150 s *(measured)* = ~600 s
  of duplicated measurement becomes one ~150 s run (or ~40 s after R0). **This is
  the single largest saving in the refactor.**
- **Falsifiable:** break the budget charge or the round loop and CP-1/gate-1 go
  red, exactly as they would have.
- **Cost:** ~150 s *(measured, pre-R0)* / ~40 s *(estimate, post-R0)* + the
  report assertions, which are seconds.

### R7 — §7 Completion Proof, with CP-3's breadth handed to CI
- **CP-1** rides R6 — free.
- **CP-2** rides R6's store plus the promotion lock (~8 s *(measured)*).
- **CP-3**'s structural locks are cheap and run as one selection; **its shard
  run (~10 min *(measured)*) moves to CI** under rule 6.
- **CP-4** (the defect-class ledger) and **CP-5** (fresh eyes through README) are
  **document work and a manual walk**: no gates, no runs.

---

## 3. Scope explicitly cut, and why the proof is intact

| cut | why it is not a weakened claim |
|---|---|
| Q1b becomes a probe, not a gate | its claim is a table's *provenance*; a probe demonstrates it and a lock would only restate the registry |
| CP-4, CP-5 run no tests | one is a table, one is a person reading a README |
| CP-3's shards run in CI, not locally | the same assertions, executed where breadth is free; the local critical path keeps only tier-1 |
| No campaign run per ticket | four consumers read one store; the *assertions* are unchanged, only the measurement is deduplicated |
| Perf is gated on mechanism, not walltime | a walltime assertion is flaky under `-n 4`; "the exit fires" is falsifiable and stable |

**Not cut:** every falsifiability claim in TODO48 stands. If removing a
mechanism must turn a lock red, it still does.

---

## 4. Process fixes (runnable, and each one has already cost time)

- **Detached background gates.** `nohup … &` from a shell the tool may kill is
  not background:
  ```
  setsid nohup uv run python -m pytest <selection> -q -rf --tb=line \
      > logs/<name>.log 2>&1 < /dev/null &
  ```
  Poll at ≤2 min with a pre-registered kill time. A killed run yields no verdict:
  `--co` to locate, never `--lf` (TODO47 §1 / AGENTS.md).
- **Dry-run every new fixture before writing its gate.**
  `comp run --spec … --dry-run` prints the plan and refuses the illegal. The Q2/E4
  session lost five red runs to spec-authoring errors; this is the whole fix.
- **Size fixtures to the claim, not to the kernel.** A lock about resume does not
  need EqProp: `instantaneous` cells are 8.8× cheaper and the lock asserts
  nothing about learning. Reserve `energy_minimization` for the locks whose
  property *is* EqProp's (gate 2b, the campaign).
- **Read the store, don't re-measure it.** When a lock needs evidence, prefer
  `RecordStore.query_records` over a pipeline run. TODO48's own gates do this
  (the run-ledger lock reads the store alone).
- **Respect the 120 s per-test timeout** (`pyproject.toml`) unless the mark
  raises it, as `test_campaign_lock.py` does with `pytest.mark.timeout(900)` —
  consolidation must not build a fixture that dies mid-file.

---

## 5. Decisions needed from the operator

- **D-j — the 5 pre-existing `test_sampler_lock.py` failures.** They fail
  **identically at HEAD** (verified by stash this session) and they block CP-3's
  "all structural locks green". Options: (i) fix them (unknown cost, not
  estimated); (ii) **waive with a record** — a lock that pins the waiver, so a
  *new* failure of any kind goes red while the five known ones are enumerated.
  *Recommendation:* (ii). They are not in D3's blast radius, they are not
  regressions, and a waiver lock that fails on anything new is honest and cheap.
- **D-k — do R0 (the settle-loop fix) now, or after the queue?** It is the
  largest single saving in this file and it makes R6 ~4× cheaper, but it is a
  kernel change in Phase D rather than a Phase E/F claim.
  *Recommendation:* **now**, before R2–R4, because those locks are cheap either
  way and R0's saving is only realized on everything after it.
- **D-l — is CI trusted for breadth?** R5's whole value is moving CP-3's shards
  off the local path. If CI is not yet wired to run on pushes here, R5 buys
  documentation rather than time and should be dropped from the critical path.

---

## 6. Session ordering and the exit

**Session A (cheap, high-yield):** R0 → R3 + R4 (one selection).
**Session B (cheap, no cells):** R2, then R1's probe.
**Session C (the one campaign):** R6 — one run, four consumers — then R5.
**Session D (paper):** CP-4 ledger, CP-5 walk, then close the plan.

Local gate time, estimated from the measured components:

| path | local gate time |
|---|---|
| TODO48's order as written | ~35–45 min *(estimate)* |
| this file, R0 included | **~15 min** *(estimate)* |
| this file, R0 + CI absorbing breadth | **~6 min** *(estimate)* |

The exit is unchanged: CP-1..CP-3 green (breadth in CI), CP-4's table complete,
CP-5 walked. Then TODO48.md closes and the plan files stop growing.

---

## 7. What did not change

The goal, the terminal state, and every gate's *claim*. TODO48's definition of
done — one command, minutes not hours, every number derivable from the store,
every claim carrying its uncertainty, every seam locked — is not renegotiated
here. Only the order of arrival and the number of times the same 450 cells get
measured.