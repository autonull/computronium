# TODO49.md — The Whole Path

**Supersedes:** nothing — this file *extends* TODO48. Its Phase A–C **are**
TODO48's queue (Q1–Q8, unchanged, gates unchanged); this file does not repeat
them. Phase D–F is the path TODO48 did not cover: what stands between
"the pipeline works" and "a researcher uses this weekly and trusts what it
prints".

**Binding:** `AGENTS.md`. **Binding:** this file.

---

## 0. The terminal state — the definition of done

> A researcher who has never read this repo runs one command, waits minutes
> not hours, and reads a report in which every number is derivable from the
> store, every claim carries its uncertainty and its limitations, and every
> architectural seam that could silently falsify it is locked. If the answer
> is "no effect", the report says so with the power it had.

That is the whole path. Everything below is a phase of it.

---

## Phase A — The loop produces meaning (TODO48 Q1, Q1b, Q2)

The campaign under a working lr: does any credit rule separate; the
multiplier table measured; the promotion stage so maturity above L0 exists.
**Exit criterion:** the campaign report states, per credit rule, an accuracy
with an uncertainty that is not `{}`, and `promotion_history` is non-empty on
a run that earned it.

## Phase B — The seams are singular or loud (TODO48 Q3, Q4, Q5, Q7)

Per-axis hyperparameters; one prior registry; a legal compose emits zero
warnings; every lock demonstrably fails when its mechanism is removed.
**Exit criterion:** removing any single named mechanism from any queue-owned
file turns at least one lock red, and a fresh checkout composes every legal
campaign cell silently.

## Phase C — Shrink to purpose (TODO48 Q6, Q8)

Lab census + retirements; conformance honesty; per-cell replay hash retired;
effective lr visible in records.
**Exit criterion:** `git grep -c ""` over the lab shrinks by the census's
retired list, and no module survives without a caller or a recorded reason.

## Phase D — Scale to real use

TODO48 says nothing about *cost at scale*. A campaign is a research
instrument only if its walltime is bounded and its device is chosen.

### D1 — Device as a first-class schedule field
- **Does:** `Schedule` gains `device` ("cpu" | "cuda" | "auto", default
  "auto"); the evaluator threads it to `SystemTrainer` and the task; the YAML
  spec declares it; `comp run` reports it. Today `evaluate.py` defaults to
  "auto" in the signature but `_task` pins "cpu" (evaluate.py:79, 89) —
  the campaign is CPU-bound by construction.
- **Gate:** the campaign lock runs one cheap cell on "cuda" when available
  (skip-marked otherwise) and asserts `provenance` records the device used;
  falsifiable by hardcoding "cpu" in the evaluator.

### D2 — Campaign economics: the record price, published
- **Does:** `comp status --run-id` prints measured cost per record and
  projected completion (records done / records declared × s/record); the
  report prints the same. A run that will take 4 hours must say so at 60 s,
  not at 3 hours.
- **Gate:** a lock running the 10-cell narrowed store spec asserts the status
  output contains `records/s` and a projection; falsifiable by removing the
  projection.

### D3 — Long-campaign survival: checkpoint + resume at scale
- **Does:** TODO47 T1's resume works per-run; campaigns must checkpoint on
  budget exhaustion (TODO47 §5 already warns per-cell resumes waste rounds)
  and `comp run --resume <run_id>` must be the documented recovery path for
  an interrupted campaign. Verify the policy `resume()` paths for all three
  policies, not just the two the lock covers.
- **Gate:** the resume lock extended: interrupt a 3-round campaign twice, the
  third launch completes the declared space with no duplicate key and no gap
  (the §3.7 gate-5 statement at campaign scale).

## Phase E — Scientific rigor in the report

The report is honest but thin. Rudimentary was acceptable; this phase makes
the numbers *arguable*.

### E1 — Uncertainty is a measurement, not `{}` 
- **Does:** `Record.create` writes `uncertainty={}` forever
  (`cell_record`); claims derive nothing from it. Per-cell records carry the
  seed plan's spread: for a cell measured over n_seeds, uncertainty is the
  across-seed std of each claimed metric; single-seed cells carry the
  floor (1/√n bootstrap is a lie — record "single_seed" as the reason).
  `derive_claims` consumes it: a claim states "0.49 ± 0.03 (3 seeds)".
- **Gate:** a lock asserting claims on a multi-seed measured run carry
  non-empty uncertainty sourced from the store's own records, and that
  `ReportGenerator` renders it; falsifiable by zeroing the spread.

### E2 — Significance: difference claims need a test
- **Does:** the campaign compares credit rules; the report must state
  *whether the difference survives its seeds* — a paired permutation test
  over shared cells (no new dependency: torch/itertools implement it), with
  the test named in the report and the p-value next to the claim. No test
  where n<2 cells per rule: the report says "insufficient coverage",
  which is a finding, not a failure.
- **Gate:** a lock with a constructed store where rule A beats B by 3σ of its
  spread asserts the report prints the p-value; and a flat store asserts the
  report prints the honest null.

### E3 — Contrast design lands or is retired
- **Does:** `experiment/execution/contrast_design.py` and the
  `DataOrigin.CONTROL/CONTRAST` enum exist and no queue ticket has ever
  invoked them (grep-verified across TODO46/47). Decide: wire the contrast
  split into the campaign spec (control group = gradient reference at fixed
  lr, contrast group = the swept space) or retire with a record (R78).
  *Session default:* wire it — Phase A's table gains a control column.
- **Gate:** the campaign report names the control and the report lock
  asserts its presence; falsifiable by removing the split.

### E4 — Promotion earns L2 by replay, not by assertion
- **Does:** TODO48 Q2's promotion writes L2; make L2's gate the *replay
  gate*: a promoted cell re-measured from the store's own replay path
  reproduces its claimed metrics within registered tolerance
  (`replay.py` + `PARAM_BUDGET_TOLERANCE` precedent). This is the maturity
  ladder's first rung that means "independently reproducible".
- **Gate:** the promotion lock extended: the L2 write triggers one replay and
  the store records its verdict; falsifiable by removing the replay call.

## Phase F — Productization

The system is a tool; tools get interfaces, docs, and CI.

### F1 — CLI completeness as a locked surface
- **Does:** `comp`'s commands are whatever the campaign lock happens to
  exercise; enumerate the intended surface (`run`, `status`, `report`,
  `promote`, `resume`, `audit`) in one place (`cli/__init__.py` or a table)
  and lock it: every listed command appears in `--help`, every command in
  `--help` is listed, and each has at least one test exercising it through
  the command surface (TODO46's own rule: a gate stated against a Python API
  proves the API, not the command).
- **Gate:** a surface lock (the `test_wp11_surface_lock.py` shape, after
  TODO48 Q7 splits it, priced < 60 s).

### F2 — Documentation regenerated from the thing itself
- **Does:** README's pipeline section generated from the CLI surface lock and
  the campaign YAML's own schema (the README generation machinery from
  TODO47 sessions 3–5 exists); examples/ gains a second, *tiny* spec
  (mnist transfer, the T5 yaml already declares it) documented end-to-end
  with its measured walltime. No number in README that no test produces.
- **Gate:** the gallery/README lock green; every README pipeline number
  appears in a test assertion or a store record.

### F3 — CI gates adopted (AGENTS.md's order, actually running)
- **Does:** `ruff format --check` → `ruff check` → `pyright` (strict on
  computronium/, basic on packages/) → targeted pytest → `pip-audit`. The
  per-commit checklist is followed manually today; encode it so it cannot
  drift.
- **Gate:** the CI config exists and runs the four gates; a deliberately
  broken commit (format violation) fails it in the setup commit, then is
  reverted.

### F4 — Versioning the measurements
- **Does:** `schema.versioning` exists; records carry
  `assessment_procedure_version="1.0"` hardcoded. Bump and record the
  procedure version *per change that changes what a record means* (the lr
  fix is exactly such a change: pre-fix records measure a dead lr). The
  store gains a query for records whose procedure version predates a given
  change, so old measurements are visible, not silently mixed.
- **Gate:** a lock that writes a record with an old procedure version and
  asserts the store can exclude it; the campaign spec carries the current
  version.

---

## 5. Session ordering (the whole path, linear)

A–C are TODO48's queue in its order. Then, in dependency order:

1. **D1** (device) — cheap, unblocks scale.
2. **E1** (uncertainty) — the report's credibility.
3. **D2, D3** (economics, survival) — usable at real campaign size.
4. **E2, E3** (significance, contrast) — the report becomes arguable.
5. **E4** (L2 by replay) — the ladder's first trusted rung.
6. **F1–F4** — interface, docs, CI, versions, in that order; F3 (CI) any time
   after F1.

**Definition of "the system works":** Phase A complete. **Definition of
"the system is trustworthy":** Phase B complete. **Definition of "the system
is a tool":** Phase D. **Definition of "the system does science":** Phase E.
**Definition of "the system is done":** Phase F — and "done" here means the
plan file stops growing, per TODO47 §0.6.

## 6. What this plan does not promise

- That credit rules separate. Phase A measures it; Q1b separates a prior row
  strangling a rule from a genuine null.
- That every retired surface's users are happy. Retirement records name the
  reason; reversal is one commit.
- Walltimes. Every gate prices itself first (`--co`); no number in this file
  is trusted without its own measurement.

## 7. Session log

- (empty — this file is the queue; landed phases leave it shorter)
