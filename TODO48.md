# TODO48.md — Trust the Seams, Then Build the Tool

**Supersedes:** the remaining queue of `TODO47.md` (T7, T8, round-close items).
**TODO47 is frozen and remains the evidence record** — its §0 doctrine, §6.1
root-cause analysis and ticket history are not repeated here.
**Binding:** `AGENTS.md` in full. **Binding:** this file.

**Goal:** from "the pipeline works" to "a researcher uses this weekly and
trusts what it prints", in one queue. The kernel crosses the real threshold
(TODO47 §6.1 resolved: cells learn; the campaign loop runs and is locked);
what remains is meaning (Phase A), seam trust (B), shrinkage (C), scale (D),
rigor (E), and productization (F).

**The terminal state — the definition of done:**

> A researcher who has never read this repo runs one command, waits minutes
> not hours, and reads a report in which every number is derivable from the
> store, every claim carries its uncertainty and its limitations, and every
> seam that could silently falsify it is locked. If the answer is "no
> effect", the report says so with the power it had.

---

## 1. The doctrine, in one paragraph

TODO47's record is unambiguous about where defects lived: not in the ontology,
the store, or the claims — in the *seams*: places where two registries, two
specs, or two defaults meet. Six of the eleven measured defects (the lr at
1e-5, the `beta` warning, the seed shift, the diagonal walk, the off-by-one
rounds, the unreproducible record key) were seam defects. Every seam in this
plan is either **singular** (one implementation) or **loud** (a gate that
fails). And every gate is tier-1 or a priced demo — no ticket's gate is a
whole shard, and no lock's fixture may lack the case the lock exists for.

`AGENTS.md`'s Testing section binds all of TODO47 §1's rules (select by
symbol, `-rf --tb=line` to a log, killed runs yield no verdict, one shard per
round close, a lock's fixture must contain its case). Nothing restated; the
tickets below are executed under them.

---

## 2. The queue

Ordered by *deliverable*. Each ticket names its gate and, where landed
before, its measured price. No ticket's gate is a whole shard.

## Phase A — The loop produces meaning

### Q1 — Does any credit rule separate? The campaign, re-run on a working lr
- **Does:** run the T5 campaign (`examples/learning-rules-and-geometry-digits.yaml`)
  with the lr fix landed and read what it says about credit rules. This is the
  system's purpose and it has never been measured under a working learning
  rate. Report the per-credit accuracy table, not a verdict.
- **Blocks on nothing. Unblocks:** whether the multiplier audit (Q1b) is
  measured or speculative, and whether gate 2 can be strengthened (D-g).
- **Gate:** strengthen `test_campaign_lock.py` gate 2 (**78 s**, existing):
  the `gradient` reference cell beats 1.5× chance at the campaign's own
  epochs/batch_limit (measured: 0.49 vs chance 0.1 at prior-center lr, 10
  epochs — the lock may use a cheaper cell but the property must be the
  reference cell's, not a fabricated one). Falsifiable: revert the lr fix,
  gate goes red.
- **Q1b (same session if the table is flat):** audit the multiplier table
  (`prior.py:88-121`): for each (dynamics, credit) row, one 10-epoch probe at
  prior-center lr; any row whose effective lr cannot move the loss gets its
  multiplier re-registered with the measurement in the description or
  retired. A row is a prior, not a verdict. Known-suspect row:
  `("energy_minimization", "thermodynamic_contrast"): 0.00005` — an
  effective lr of 1.6e-6 at prior center, a cell that cannot learn by
  construction, in the table the campaign compares rules through.

### Q2 — The promotion stage (TODO47 T7, D-a default (i))
- **Does:** a promotion stage writing `status.maturity`: eligibility `L1`
  when a cell achieves `spec.n_seeds` seeds at its declared fidelity with a
  `PASS` gate; promotion `L2` when the eligible cell's claim survives E4's
  replay gate. `promoted`, `filter_promoted` and the report's
  promotion-history section become measurements.
- **Gate:** a lock asserting a promoted cell reaches `L2` and appears in
  `promotion_history`, on a *measured* store (the lr fix makes real runs
  eligible); the report's `Promoted:` count non-zero on the same run (tier 1).
- **Note:** the stage list reserves S10 for promotion predicates
  (`stage.py:13`); `Record`'s flag surface already names the claims that
  depend on it (`record.py:84`).

## Phase B — The seams are singular or loud

### Q3 — Split the shared names; delete the merging machinery
- **Does:** per-axis hyperparameters at the schema level: `update_lr` (update
  axis, Euclid-semantic: per-element displacement), `settle_step` (dynamics
  axis, per-iteration), per-axis `beta`/`momentum` where the meanings differ
  (`beta` couples only where an interaction is real — EqProp's β-matching
  check stays as a compose-time validation, not a warning). Three names are
  declared by two axes today (`harvest.by_axis_specs`: `step_size`, `beta`,
  `momentum`), each pair a different physical quantity; TODO47 §6.1's
  resolve-once preference rule is a patch on this and is deleted with it.
- **Backwards compatibility: none** (AGENTS.md). Update the T5 campaign YAML,
  the harvest locks, and every spec producer in the same commit.
- **Gate:** (i) no hyperparameter name is declared by two axes — a lock that
  walks `by_axis_specs`; (ii) the reference cell composes with **zero
  warnings** (shared with Q5's gate); (iii) the campaign lock stays green;
  (iv) falsifiable: re-introduce a shared name, lock (i) goes red.

### Q4 — One prior registry, one resolution function
- **Does:** consolidate `schema/seed_registries.py`'s schema priors and
  `learning/prior.py`'s runtime registry into one `PRIORS_REGISTRY` with one
  accessor (`prior_value`) and one registration path. `_resolve_value`
  shrinks to override → prior → config default, and `Domain.lo` as a
  fallback is deleted (a value with no prior and no config default is a
  schema error at declaration time, not a silent lower bound).
- **Gate:** exactly one `PRIORS_REGISTRY` definition in the repo (grep lock);
  `_config_default` cannot return a `Domain.lo` value for a continuous
  hyperparameter; the campaign lock stays green.

### Q5 — Defaults audit: no warning fires on a legal compose
- **Does:** for every warning emitted during `compose_configs` + `fit` on the
  reference cell (known: the `beta` mismatch at `system.py:405`, dynamics
  0.001 vs credit 0.5, firing on every compose today; suspect: `max_steps=1`
  as the harvest default for settling dynamics — a settling dynamic that
  settles once), either fix the default that caused it or convert the warning
  into a validation error so an illegal combination fails at compose time.
  The rule: **a legal cell's compose is silent**.
- **Gate:** a lock that composes every legal cell of the campaign YAML under
  `warnings.error` and asserts none raised (tier 1; price with `--co` first).

### Q7 — Lock fidelity audit
- **Does:** for every test file under `tests/property/` and
  `tests/acceptance/`, one mutation per lock's named mechanism (remove the
  call, flip the flag, break the invariant) and record green/red in a
  `LOCK_AUDIT.md`. A lock that stays green with its mechanism removed is
  deleted or rewritten in the same commit (TODO47 §1.4).
- **Also:** split `test_wp11_surface_lock.py` (217 s, two runs of the same
  file failed differently — TODO47 §5) so no file exceeds ~60 s.
- **Gate:** the audit table exists with no "stayed green" rows; wp11's
  replacement files each < 60 s.
- **Note:** deliberately *not* mutation testing of everything — one mutation
  per named mechanism, guided by the lock's own docstring.

## Phase C — Shrink to purpose

### Q6 — The lab: a census, then retirements
- **Does:** a usage census over `packages/computronium-lab/src` (importers,
  test callers, kernel-path reachability), recorded in
  `packages/computronium-lab/USAGE.md`; every module with no caller and no
  kernel-path reachability gets a retirement record (R78) and deletion.
  Survivors: the facade (`lab.py`), training certificates, synthesis
  (labelled predicted), the ψ-adaptation evaluator (scoped measurement,
  locked by T6).
- **Gate:** a lock asserting every surviving lab module has an importer
  outside itself; the retirement records live in the census file, one line
  each with the reason. **Decision D-f below sets the census criteria.**

### Q8 — The small ones (any order)
- **conformance.py reports** an `UNVERIFIED` row's recorded reason instead of
  running it; `codegen.generate_conformance_stubs` stops emitting stubs for
  the 19 unverified rows (TODO47 T8, unchanged).
- **Per-cell `compute_replay_hash` retirement** (TODO47 §5): the run-level
  hash is the gate; the per-cell API has zero production callers (re-verified
  this session); retire it with a record.
- **Effective lr visible in records:** promote the §6.1 probe's finding into
  `ComposedCell.params` reporting — "what lr did this cell train at" is
  answerable from a record without a probe (`update.step_size` as composed).
- **README archaeology** (low, TODO47 T8).

## Phase D — Scale to real use

A campaign is a research instrument only if its walltime is bounded and its
device is chosen.

### D1 — Device as a first-class schedule field
- **Does:** `Schedule` gains `device` ("cpu" | "cuda" | "auto", default
  "auto"); the evaluator threads it to `SystemTrainer` and the task; the YAML
  spec declares it; `comp run` reports it. Today `evaluate.py`'s `evaluate_cell`
  signature says "auto" but pins `_task(schedule.task_id, "cpu")` — the
  campaign is CPU-bound by construction.
- **Gate:** the campaign lock runs one cheap cell on "cuda" when available
  (skip-marked otherwise) and asserts provenance records the device used;
  falsifiable by hardcoding "cpu" in the evaluator.

### D2 — Campaign economics: the record price, published
- **Does:** `comp status --run-id` prints measured cost per record and a
  projected completion (records done / records declared × s/record); the
  report prints the same. A run that will take 4 hours must say so at 60 s,
  not at 3 hours.
- **Gate:** a lock running the 10-cell narrowed store spec asserts the status
  output contains a rate and a projection; falsifiable by removing the
  projection.

### D3 — Long-campaign survival: checkpoint + resume at scale
- **Does:** TODO47 T1's resume works per-run; campaigns must checkpoint on
  budget exhaustion (TODO47 §5 warns per-cell resumes waste rounds) and
  `comp run --resume <run_id>` must be the documented recovery path for an
  interrupted campaign. Verify the `Policy.resume()` paths for all policies,
  not just the two the lock covers.
- **Gate:** the resume lock extended: interrupt a 3-round campaign twice, the
  third launch completes the declared space with no duplicate key and no gap
  (the §3.7 gate-5 statement at campaign scale).

## Phase E — Scientific rigor in the report

Rudimentary was acceptable; this phase makes the numbers *arguable*.

### E1 — Uncertainty is a measurement, not `{}`
- **Does:** `cell_record` writes `uncertainty={}` forever; claims derive
  nothing from it. A cell measured over n_seeds carries the across-seed std
  of each claimed metric; single-seed cells record "single_seed" as the
  reason (a 1/√n bootstrap would be a lie). `derive_claims` consumes it: a
  claim states "0.49 ± 0.03 (3 seeds)".
- **Gate:** a lock asserting claims on a multi-seed measured run carry
  non-empty uncertainty sourced from the store's own records, and that
  `ReportGenerator` renders it; falsifiable by zeroing the spread.

### E2 — Significance: difference claims need a test
- **Does:** the campaign compares credit rules; the report states *whether
  the difference survives its seeds* — a paired permutation test over shared
  cells (no new dependency: torch implements it), the test named in the
  report, the p-value next to the claim. Fewer than 2 cells per rule: the
  report says "insufficient coverage" — a finding, not a failure.
- **Gate:** a lock with a constructed store where rule A beats B by 3σ of its
  spread asserts the report prints the p-value; and a flat store asserts the
  report prints the honest null.

### E3 — The contrast design is exercised and reported
- **Does:** `contrast_design.py` is *already wired* — S1 creates a design
  (`stages_impl.py:130`, default `ContrastDesignKind.OFAT`). What no ticket
  has ever verified is that the campaign's design actually splits
  control/contrast records and that the report names the control. Verify on
  a measured run; if OFAT's split produces no records distinct from the
  swept space, either fix the split or retire the enum values with a record
  (R78).
- **Gate:** the campaign report names the control and the report lock asserts
  its presence; falsifiable by removing the split.

### E4 — Promotion earns L2 by replay, not by assertion
- **Does:** make Q2's L2 gate the *replay gate*: a promoted cell re-measured
  through the store's replay path reproduces its claimed metrics within
  registered tolerance (`PARAM_BUDGET_TOLERANCE` precedent). The maturity
  ladder's first rung that means "independently reproducible".
- **Gate:** the promotion lock extended: the L2 write triggers one replay and
  the store records its verdict; falsifiable by removing the replay call.

## Phase F — Productization

### F1 — CLI completeness as a locked surface
- **Does:** enumerate the intended `comp` surface (`run`, `status`, `report`,
  `promote`, `resume`, `audit`) in one place and lock it: every listed
  command appears in `--help`, every command in `--help` is listed, and each
  has at least one test exercising it through the command surface (a gate
  stated against a Python API proves the API, not the command).
- **Gate:** a surface lock (the `test_wp11_surface_lock.py` shape, after Q7
  splits it, priced < 60 s).

### F2 — Documentation regenerated from the thing itself
- **Does:** README's pipeline section generated from the CLI surface lock and
  the campaign YAML's own schema (the README generation machinery exists);
  `examples/` gains a second, *tiny* spec (mnist transfer, the T5 yaml
  already declares it) documented end-to-end with its measured walltime. No
  number in README that no test produces.
- **Gate:** the gallery/README lock green; every README pipeline number
  appears in a test assertion or a store record.

### F3 — CI gates adopted (AGENTS.md's order, actually running)
- **Does:** `ruff format --check` → `ruff check` → `pyright` (strict on
  `computronium/`, basic on `packages/`) → targeted pytest → `pip-audit`.
  The per-commit checklist is followed manually today; encode it so it
  cannot drift.
- **Gate:** the CI config exists and runs the gates; a deliberately broken
  commit (format violation) fails it in the setup commit, then is reverted.

### F4 — Versioning the measurements
- **Does:** records carry `assessment_procedure_version="1.0"` hardcoded. Bump
  and record the procedure version *per change that changes what a record
  means* (the lr fix is exactly such a change: pre-fix records measure a
  dead lr). The store gains a query for records whose procedure version
  predates a given change, so old measurements are visible, not silently
  mixed.
- **Gate:** a lock that writes a record with an old procedure version and
  asserts the store can exclude it; the campaign spec carries the current
  version.

---

## 3. Decisions needed from the operator

Five forks; defaults keep the queue unblocked:

- **D-e — split the shared names?** (Q3.) Options: (i) per-axis names as
  proposed; (ii) one name per axis with per-axis config defaults only.
  *Session default:* (i) — it deletes the merging machinery and makes the
  campaign YAML name what it means.
- **D-f — the lab census criteria.** (Q6.) Options: (i) retirement = no
  importer outside the lab and no test exercising it; (ii) retirement = no
  kernel-path reachability *or* demo/recipe use. *Session default:* (i),
  stricter, with (ii) applied to `synthesis/` and `adaptation.py`, which the
  T6 locks already scope.
- **D-g — gate 2's strength.** (Q1.) Options: (i) reference cell beats 1.5×
  chance; (ii) measured variation only, retained. *Session default:* (i) —
  the lr fix made it measurable; if the campaign's real cells are too slow,
  the lock prices a cheaper reference cell rather than weakening the
  property.
- **D-h — what claims may name.** (E1/E2.) Options: (i) claims carry
  uncertainty and significance when the seeds exist, otherwise the report
  states the insufficiency; (ii) claims stay point estimates. *Session
  default:* (i) — TODO46 §7.1-3's default (unmeasured objectives stay
  registered with their reasons) is unchanged by it.
- **D-i — L0 records from before the lr fix.** (F4.) Options: (i) procedure
  versioning flags them, the report marks them "pre-fix"; (ii) the store is
  cleared. *Session default:* (i) — a record is evidence; versioning makes
  its meaning explicit without destroying it.

## 4. Session ordering and the definitions on the way

A–C first (TODO48's original order: Q1, Q2, Q3, Q4, Q5, Q7, Q6, Q8 — the
queue shrinks as it lands). Then, in dependency order:

1. **D1** (device) — cheap, unblocks scale.
2. **E1** (uncertainty) — the report's credibility.
3. **D2, D3** (economics, survival) — usable at real campaign size.
4. **E2, E3** (significance, contrast) — the report becomes arguable.
5. **E4** (L2 by replay) — the ladder's first trusted rung.
6. **F1–F4** — interface, docs, CI, versions, in that order; F3 (CI) any
   time after F1.

**"The system works"** = Phase A. **"The system is trustworthy"** = B.
**"The system is a tool"** = D. **"The system does science"** = E.
**"The system is done"** = F — and "done" means this file stops growing
(TODO47 §0.6: landed work leaves the queue).

## 5. What this plan does not promise

- That credit rules separate. Phase A measures it; Q1b separates a prior row
  strangling a rule from a genuine null.
- That every retired surface's users are happy. Retirement records name the
  reason; reversal is one commit.
- Walltimes. Every gate prices itself first (`--co`); no number in this file
  is trusted without its own measurement.

## 6. How a session runs a ticket

Unchanged from TODO47 §4: read this file and `AGENTS.md`; grep for the
touched symbols in `tests/` and run the 2–4 files that name them; implement;
`ruff format` + `ruff check` + `pyright` on changed files; run the ticket's
gate; update this file's ticket with the measured seconds; commit; stop.
Landed tickets leave the queue — the file gets shorter.

## 7. Session log

- **Plan verified and restructured.** E3's premise was corrected against the
  tree: `contrast_design` *is* wired (S1, `stages_impl.py:130`) — the
  unverified part is whether its split produces distinct records and whether
  the report names the control. Q8's `compute_replay_hash` zero-caller claim
  re-verified. Test-cost check: every gate in the queue is a tier-1 lock
  (17–78 s) or a priced construction; the only >60 s gates are the existing
  campaign lock (78 s, the deliverable itself) and the Q7 audit, which
  splits wp11 rather than running it.
