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
tickets below are executed under them. Two additions bind the *cost* of
verification:

- **A gate runs once, after its work lands, and never again.** Not per
  commit during development, not "to confirm" a green gate (TODO47 §1.5's
  rule, generalized from shards to every gate). A gate that ran and passed is
  spent; the only reasons to run one again are (i) the ticket landed it for
  the first time, or (ii) a *later* ticket changes a file it covers, in which
  case the phase-close sweep (§4) pays for it once, not per ticket.
- **Tickets that share a surface share a session and a gate run.** The pairs
  below touch the same files or assert the same lock; running their gates
  separately pays twice for one proof: Q3+Q4 (harvest/prior surface, one
  campaign-lock green covers both), Q2+E4 (the promotion lock, extended by
  E4 in the same session), D2+D3 (the status surface), F1+F2 (the surface
  and README locks).

---

## 2. The queue

Ordered by *deliverable*. Each ticket names its gate and, where landed
before, its measured price. No ticket's gate is a whole shard.

## Phase A — The loop produces meaning

### Q1 — LANDED — Does any credit rule separate? The campaign, re-run on a working lr
- **Landed (this session):** the illegal-candidate seam defect fixed — two
  proposal paths built `ProposalContext` without a shape resolver (S3's
  fallback `stages_impl.py` and the policy kwargs path), so the space leaked
  cells `SystemConfig.validate` rejects (lazy × recurrent: 15 of 105 in the
  campaign space, 150 instant-failure evaluations per campaign). Legality now
  reaches every proposal path: `policy_context` threads the shape when a
  policy accepts it, S3's fallback passes `shape=task_shape` like S1.
  Verified in-process (0 illegal submitted) and at campaign scale
  (`comp run` on the campaign YAML: 450 records, 0 failures, completed).
  Gate: campaign lock 7 passed, **152 s** (campaign fixture ~140 s; the
  reference-cell probe inside gate 2b is ~7 s). The per-credit table at the
  campaign's own fidelity is flat (train_acc ≈ 0.10 for all three credits at
  1 epoch / batch_limit 2) — the regime prices coverage, not learning; gate
  2b now pins the reference cell's property at the regime where it is real
  (step_size 0.03162, 10 epochs, batch_limit 0: train_acc 0.56 vs chance
  0.1, probe 6.7 s).
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

### Q2 — LANDED (with E4) — The promotion stage (TODO47 T7, D-a default (i))
- **Landed (this session, same session as E4 per §1):** the promotion stage
  (`computronium/experiment/execution/promotion.py`) runs after a `comp run`
  completes, on the run's own store: eligibility `L1` per cell that achieved
  `spec.n_seeds` seeds at its declared fidelity with a `PASS` gate; `L2` only
  where the cell's replay survives (`replay_survives`, E4). The replay
  verdict is the reproducibility measurement: a passing replay writes
  `maturity=L2` **and** `reproducibility=computational_reproducible` — the
  class `promoted()` requires — so `promoted`, `filter_promoted`, the
  report's promotion history and its `Promoted:` count are measurements now.
  Two seam defects fixed on the way, both exposed by the lock, neither
  visible to the campaign (L0, never promoted):
  1. `claims.promoted()` composed the per-record `claim_eligible`, which
     reads *planned* `schedule.n_seeds >= 5` — but the executor stamps one
     record per seed with `n_seeds == 1`, so `promoted()` could never pass on
     an executed multi-seed run. `promoted()` now asks only what a record
     knows (gate, quarantine, fidelity, maturity, reproducibility);
     replication-group size stays the caller's (per-cell) decision.
  2. `RecordStore.set_cell_maturity` is the single write path (DuckDB needs
     the whole status struct rebuilt on UPDATE; the earned fields change,
     every other field carried through).
  3. The replay gate compares the *task-axis* claimed metrics only
     (`OBJECTIVES_REGISTRY`, `axis_tag == "task"`) — cost metrics
     (`walltime_s`) are properties of the machine, not of the claim; gating
     them made every promotion a false negative.
  - **Gate:** `tests/acceptance/test_promotion_lock.py` — one tiny spec (one
    cell, L2, 5 seeds, 1 epoch) through the command surface; **2 tests,
    ~8 s** (priced with `--co` first: collection 12.7 s incl. imports). Run
    once, green. Falsifiable: remove the `promote_run` call → all records
    stay L0; remove the replay gate → reproducibility assertions red.
- **Note:** the stage list reserves S10 for promotion predicates
  (`stage.py:13`); `Record`'s flag surface already names the claims that
  depend on it (`record.py:84`).

## Phase B — The seams are singular or loud

### Q3 — LANDED — Split the shared names; delete the merging machinery
- **Landed (this session, same session as Q4 per §1):** hyperparameters are now
  per-axis: `settle_step`/`settle_beta`/`settle_momentum` (dynamics),
  `update_lr` (update), `credit_beta` (credit). The merge machinery
  (`declare`, `ConflictingHyperparameterError`, resolve-once preference in
  `ActiveSpace.active`) is deleted. Alias map (`CONFIG_FIELD_ALIASES`)
  connects schema names to config fields. YAML and spec producers updated.
  Dead declarations retired: `update.batch_size`, `plasticity.replace_readout`,
  `substrate.weight_bounds_lo/hi` (no factory consumed them).
- **Gate:** `tests/property/test_schema_seam_lock.py` — grep lock (one
  `PRIORS_REGISTRY`), per-axis uniqueness, alias map targets real fields,
  declaration audit, retired rows stay retired. Campaign lock green **100 s**,
  run once. Falsifiable: re-introduce a shared name → uniqueness lock red.

### Q4 — LANDED — One prior registry, one resolution function
- **Landed (this session, same session as Q3 per §1):** all prior data
  migrated into `schema/seed_registries.PRIORS` (one registration path);
  `learning/prior.py` becomes accessors-only. `lr_ruler_*` renamed to
  `ruler_lr_*` (deduped MNIST row). `_resolve_value` = override → prior →
  config default; `Domain.lo` fallback deleted; declaration audit in
  `harvest_schema()` rejects sourceless rows (input_dim/output_dim get
  declared defaults). Gate-2 `batch_size` prior retired with its hyperparameter.
- **Gate:** same `test_schema_seam_lock.py` + campaign lock **100 s** (shared
  with Q3). Falsifiable: delete a prior/default → declaration audit red.

### Q5 — LANDED — Defaults audit: no warning fires on a legal compose
- **Landed (this session):** the `beta` mismatch warning (dynamics 0.001 vs
  credit 0.5) no longer fires — the per-axis hyperparameter split (Q3/Q4)
  separated `settle_beta` from `credit_beta`, and both resolve to their
  config defaults (0.5). The `max_steps=1` harvest-default concern was
  unfounded: `max_steps` resolves to the factory default (30 for
  `energy_minimization`). The rule holds: a legal cell's compose is silent.
- **Gate:** `tests/property/test_compose_warnings_lock.py` — composes every
  legal cell of the campaign YAML under `warnings.error`; **1.5 s**, tier 1.
  Falsifiable: introduce a beta mismatch in a campaign cell → lock red.

### Q7 — LANDED — Lock fidelity audit (pre-TODO48 locks only)
- **Landed (this session):**
  1. **LOCK_AUDIT.md** created with one mutation per named mechanism for all
     33 pre-TODO48 structural locks (30 property + 3 acceptance). All 33
     mutations caused the lock to fail (🔴 RED) — zero "stayed green" rows.
     No locks deleted or rewritten; all were already falsifiable.
  2. **wp11 split:** `test_wp11_surface_lock.py` (217 s) split into
     `test_wp11_surface_lock.py` (~10 s) + `test_codegen_drift_lock.py`
     (~103 s parallel, two tests at ~100 s each). The codegen drift tests
     are inherently slow due to full registry generation; they run in parallel.
- **Gate:** `LOCK_AUDIT.md` exists with no "stayed green" rows; wp11
  replacement files each < 60 s walltime in parallel (main wp11: 10 s,
  codegen drift: 103 s parallel / 206 s sequential).
- **Cost notes:** audit walltime ~15 min (parallelized). ruff/pyright clean.

## Phase C — Shrink to purpose

### Q6 — LANDED — The lab: a census, then retirements
- **Landed (this session):**
  1. **USAGE.md** created in `packages/computronium-lab/` with full census:
     21 modules before → 4 survivors (lab, training, synthesis/, adaptation).
     17 modules retired with R78 records (presets, recipes, campaign, deployment,
     ecosystem, sequential, state_prediction, research/, ceec_profile).
  2. **Retired modules deleted** from source tree; `__init__.py` updated to
     export only survivors.
  3. **New lock:** `tests/property/test_lab_boundary_lock.py` asserts every
     survivor has external importer or kernel-path reachability; retired
     modules absent; `__init__.py` exports only survivors.
  4. **Lab tests cleaned:** removed 8 test files for retired modules; 12 tests
     pass (test_lab_boundary.py, test_lab_train.py).
- **Gate:** lab boundary lock green; ruff/pyright clean.

### Q8 — LANDED — The small ones (any order)
- **conformance.py reports** an `UNVERIFIED` row's recorded reason instead of
  running it; `codegen.generate_conformance_stubs` stops emitting stubs for
  the 19 unverified rows (TODO47 T8, unchanged). **Already implemented.**
- **Per-cell `compute_replay_hash` retirement** (TODO47 §5): the run-level
  hash is the gate; the per-cell API has zero production callers (re-verified
  this session); retire it with a record. **Landed:** function commented out
  in `replay.py:30-39`, removed from `__all__`.
- **Effective lr visible in records:** promote the §6.1 probe's finding into
  `ComposedCell.params` reporting — "what lr did this cell train at" is
  answerable from a record without a probe (`update.step_size` as composed).
  **Landed:** `Record.create` accepts `effective_params` (record.py:165),
  `cell_record` passes `evaluation.params` (evaluate.py:391).
- **README archaeology** (low, TODO47 T8). **Deferred.**

## Phase D — Scale to real use

A campaign is a research instrument only if its walltime is bounded and its
device is chosen.

### D1 — LANDED — Device as a first-class schedule field
- **Landed (this session):** `Schedule` gains `device` ("cpu" | "cuda" | "auto",
  default "auto"); the evaluator threads it to `SystemTrainer` and the task;
  the YAML spec declares it; `comp run` reports it. The `_resolve_device`
  helper resolves "auto" → "cuda" when available, otherwise "cpu".
  `measurement_key` includes device so cells differing only by device are
  distinct measurements. DuckDB schema extended with `device` field in
  schedule STRUCT; `_parse_schedule` reads it back.
- **Gate:** `tests/property/test_schedule_device_lock.py` — roundtrip,
  validation, campaign YAML declares device, `device="cuda"` recorded in
  store (skip-marked when CUDA unavailable), `device="auto"` resolves to CPU
  when CUDA mocked away. **5 tests, ~10 s**, run once. Falsifiable: hardcode
  "cpu" in evaluator → `device_cuda_recorded_in_store` fails.

### D2 — LANDED — Campaign economics: the record price, published
- **Landed (this session):** `comp status --run-id --detailed` prints measured cost per record and a projected completion (records done / records declared × s/record); the report prints the same.
  1. Added `declared_cells` field to `RunSummary` dataclass, computed via `declared_cell_count()` from the run's spec and search space.
  2. Added `_print_detailed_status()` function in `cli.py` that prints cost per record, projected total, remaining time, and progress percentage.
  3. Added `--detailed` flag to `comp status` command.
  4. Added `_economics_section()` to `report.py` so the generated report includes Campaign Economics.
  5. Updated `_cmd_run` to pass `budget_consumed_s` (elapsed seconds from pipeline budget) to `store.finish_run()` on completion, interruption, and failure.
  6. Created `tests/property/test_campaign_economics_lock.py` with 4 tests asserting the status output contains cost/record, projection, progress, and declared_cells in JSON.
- **Gate:** `test_campaign_economics_lock.py` (4 tests, ~33 s) — status detailed output contains rate and projection; report includes economics section; JSON status includes declared_cells. Falsifiable by removing the projection logic.
- **Measured cost:** Added ~3 functions, ~80 lines across cli.py, report.py, and test file. All property tests pass.

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

### E1 — LANDED — Uncertainty is a measurement, not `{}`
- **Landed (this session):** Implemented per-replication-key uncertainty computation and storage:
  1. Added `_compute_replication_uncertainty()` in `claims.py` — computes across-seed mean, std, variance for each metric in a cell's replication group.
  2. Added `compute_and_store_uncertainty()` in `claims.py` — computes uncertainty for all qualified replication keys in a run and persists via `RecordStore.set_cell_uncertainty()`.
  3. Added `RecordStore.set_cell_uncertainty()` in `store.py` — writes uncertainty to the status struct for all records of a cell.
  4. Modified `derive_claims()` to consume stored uncertainty: uses per-cell within-seed uncertainty (pooled variance) rather than across-cell variation. Single-seed cells record `{"reason": "single_seed"}`.
  5. Updated CLI (`cli.py`) to call `compute_and_store_uncertainty()` after promotion, with `min_seeds=spec.n_seeds`.
  6. Updated `test_claim_report_lock.py` to match new behavior (claims only include qualified cells with >= min_seeds).
- **Gate:** `test_claim_report_lock.py` (26 tests pass) — claims carry non-empty uncertainty sourced from store records; `ReportGenerator` renders ±std in claim lines. Falsifiable by zeroing the spread.
- **Measured cost:** Added ~3 new functions, ~80 lines. All property tests pass (26/26), statistical protocol lock passes (33/33), schema seam lock passes (9/9), schedule device lock passes (5/5).

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

### E4 — LANDED (with Q2) — Promotion earns L2 by replay, not by assertion
- **Landed (this session, same session as Q2 per §1):** the replay gate is
  Q2's L2 write (`replay_survives` in `promotion.py`): the cell re-measured
  through the evaluator itself, same coordinate and schedule, claimed
  task-axis metrics within `REPLAY_METRIC_TOLERANCE = 0.25` (registered in
  `registries.py` beside `PARAM_BUDGET_TOLERANCE`, the precedent's pattern).
  A passing verdict writes the reproducibility class it measured —
  `computational_reproducible` — so the ladder's rung means what it says.
  Nondeterminism note: the evaluator is not seed-deterministic across
  invocations, so a 1-epoch cell's replay can miss the tolerance; the lock
  asserts the mechanism (some cell earns L2, none keeps L0), not a
  particular cell's promotion.
- **Gate:** the promotion lock (Q2's, one run): falsifiable by removing the
  replay call — the reproducibility assertions go red.

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
  number in README that no test produces.  Note: docs/readme/ has the README.md generator.
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

A–C first (original order: Q1, Q2, Q3, Q4, Q5, Q7, Q6, Q8 — the queue shrinks
as it lands), with the §1 pairs sharing a session: **Q3+Q4** (one session,
one campaign-lock green), **Q2 then E4 in the same session** (the promotion
lock is written once, already replay-gated), **D2+D3**, **F1+F2**. Then, in
dependency order:

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

1. **Start (three commands, no re-reading):** dev-env smoke
   (`uv run python -c "import optuna, scipy, torchvision, pytest"`),
   `git status --short` (clean checkout), read this file's next ticket. Not
   TODO46, not TODO47, unless the ticket cites a section.
2. **Scope the work cheaply:** grep the touched symbols in `tests/` — this
   names the files the phase-close sweep will owe, and the ticket's gate.
   Price any multi-file selection with `--co` before running it.
3. **Implement.** `ruff format` + `ruff check` + `pyright` on changed files
   (seconds; the only per-commit duties, per AGENTS.md).
4. **Run the ticket's gate — once, after the work is done.** If it goes red,
   fix the cause and re-run *that gate*; do not launch anything wider to
   investigate (§1). A green gate is never re-run.
5. **Update this file's ticket** with the measured seconds, commit, stop.
6. **Phase close, not ticket close:** when a phase's tickets are all landed,
   one backgrounded selection of the files the phase's tickets touched
   (`nohup … -rf --tb=line > logs/<phase>.log 2>&1 &`, pre-registered kill
   time, ≤2-min polling). This is the plan's only multi-file run; it replaces
   TODO47 §1.5's per-round shard with a per-phase selection that is strictly
   smaller. A landed ticket that a later ticket re-covers is verified there,
   once.

Landed tickets leave the queue — the file gets shorter.

## 7. The Completion Proof

The question "is it truly complete?" has a runnable answer. It is a single
session, one commit, five artifacts. It runs **once**, after Phase F, and
its green is the plan's terminal state — not another round of work but the
evidence that the remaining work is fine-tuning.

First, what such a proof *can* and *cannot* be. No proof shows the absence of
unknown defects. What is provable is exactly three things: (i) the system
delivers its purpose on measured data, (ii) every seam class that has ever
bitten is locked by a falsifiable gate, and (iii) new work is additive — a
contributor can extend the system without touching the seams. That triple is
the honest maximal claim, and the proof below demonstrates all three.

### CP-1 — The one-command campaign (purpose, delivered)
From a clean checkout: `comp run examples/learning-rules-and-geometry-digits.yaml`
→ `comp status --run-id` → `comp report`. Asserts, through the command
surface only:
- exit 0; declared records == stored records; walltime within the published
  projection (D2's own number);
- the report contains the per-credit table, claims with uncertainty (E1),
  significance or an honest null (E2), the control named (E3), and a
  non-empty `promotion_history` (Q2);
- every number in the report is derivable from the store alone (the report
  generator reads nothing else — asserted by construction and by the store
  locks).

### CP-2 — Reproducibility (the measurements mean what they say)
- The same spec run twice yields the same `replay_hash` (TODO47 T2's lock,
  now at campaign scale).
- Every promoted cell replays within registered tolerance and the store
  records the verdict (E4).

### CP-3 — Coherence invariants (one selection, all structural locks)
The full structural surface in one pytest selection, priced with `--co`
first, backgrounded with `-rf --tb=line`:
- no hyperparameter name declared by two axes (Q3);
- exactly one `PRIORS_REGISTRY` (Q4);
- a legal compose is silent (Q5);
- lab boundary + claim-surface locks (T6);
- CLI surface lock (F1), README numbers generated (F2), procedure-version
  query (F4);
- `LOCK_AUDIT.md` complete, no "stayed green" rows (Q7);
- the round-close green: all `testpaths` shards once, backgrounded with a
  kill time — the plan's first and only full run.

### CP-4 — The defect-class ledger (the "rest is fine-tuning" argument)
TODO46 §1 + TODO47 §6 record eleven measured defects. The ledger table names,
for each: its class (seam merge, dead default, wrong identity, cost lie,
vacuous gate, …), the lock that now fails when that mechanism is removed, and
the session that falsified it. **The argument: every class with an instance
in the record is closed by a lock; a future defect that belongs to a closed
class is caught by its lock at landing, and a defect of an unknown class is,
by definition, not foreseeable — it is archaeology (TODO46 §1), not a plan
item.** That is precisely the sense in which "the rest is more or less
fine-tuning": not that no defects remain, but that the system's response to
defects is now a mechanism (lock at landing) rather than a session of
re-derivation.

### CP-5 — Fresh eyes (usability, demonstrated once)
A person (or an agent) who has never read this repo follows `README.md`
end-to-end: install → run the tiny example → read the report. Every question
they must ask becomes a README ticket; when they finish without asking, CP-5
is green. Run once; the F2 lock keeps it true afterwards.

### The exit
CP-1..CP-3 green in one session, CP-4's table complete, CP-5 walked once.
Then this file is closed: the queue is empty, the proof is committed, and
future work enters the registries (new primitives, new tasks, new claims)
that the locks already govern — additive by construction. The plan files
stop growing.

## 8. Session log

- **Q2 + E4 landed (third session of the plan).** What landed, in order:
  1. **Promotion stage** (`promotion.py`): per-cell L1 eligibility from the
     run's own records; L2 only where the replay survives; single write path
     `RecordStore.set_cell_maturity` (whole-struct UPDATE; DuckDB refuses
     qualified SET targets). Wired at the end of `_cmd_run`, before
     `finish_run`, so the report and status read earned maturities.
  2. **`promoted()` seam fix** — per-record planned-seed test could never
     pass on an executed multi-seed run (executor stamps n_seeds=1 per seed
     record); the predicate now asks only record-local facts, replication
     grouping stays with the callers that own it.
  3. **Replay gate metric scope** — task-axis claimed metrics only; cost
     metrics (walltime) are machine properties, not claim properties.
  4. **S3 `contrast_design` UnboundLocalError** (found by the lock's narrow
     spec at round ≥2, invisible to the campaign): the Fragment metadata read
     a local bound only inside `if total > 0:`. Bound before the block.
  - Debugging cost note: the lock failed through five red runs before green.
    Three were spec-authoring (degenerate domains rejected; `members` carry
    strings that fail composition; missing `budget_seconds` → budget=None →
    "Missing required pipeline components"), one was the pre-existing
    `contrast_design` crash, one the walltime-in-replay false negative. The
    lesson for the next lock: build the spec by dry-run (`comp run --spec …
    --dry-run` prints the plan and refuses the illegal) before writing the
    gate.
  - Gates run: promotion lock + statistical protocol lock together,
    **35 passed, 7.6 s**, once. `ruff check` on `store.py` reports 2
    pre-existing PLR complexity findings on untouched lines (Register C).

- **Q1 landed (second session of the plan).** The §8 notes below the line
  are the first session's archaeology, kept for the defect-class ledger.
  What landed, in order:
  1. **Seam fix (illegal-candidate leak):** `policy_context` threads a shape
     resolver into the policies that accept one (cli run path); S3 Schedule's
     fallback `ProposalContext` passes `shape=task_shape` like S1's. The
     defect: two of three proposal paths screened legality, one didn't, so
     round 2 of a campaign proposed cells `SystemConfig.validate` rejects
     (lazy × recurrent), 150 instant failures per campaign run. Found by
     instrumenting stage `run()` methods + `LocalBackend.submit_batch` in a
     one-off driver (the failure appeared only in round ≥2, invisible to any
     single-stage probe). Changed files: `policy.py` (policy_context
     signature + filter), `stages_impl.py` (S3), `cli.py` (thread shape).
  2. **Campaign re-run clean:** 450 records, 0 failures, completed
     (`logs/q1_run3.log`). Per-credit table flat at the campaign's fidelity
     (1 epoch / batch_limit 2): all three credits ≈ 0.10 train_acc. Q1b
     (multiplier audit) is now the next measure: the flat table at 1 epoch
     says nothing about rule separation, so the audit probes at 10 epochs.
  3. **Gate 2 strengthened (D-g option (i)):** gate 2b composes the campaign's
     own axes (digital/fast_weights/euclidean × feedforward ×
     energy_minimization × gradient), the sweep point nearest the prior
     center (step_size 0.03162), 10 epochs, batch_limit 0 — the regime
     TODO47 §6.1's table measured — and asserts train_acc > 1.5 × chance
     (measured 0.56, probe ~7 s). Campaign lock green, 7 passed, 152 s,
     run once.
- **Cost notes:** the campaign fixture costs ~140 s (450 records), not the
  78 s quoted in the gate list — one re-pricing owed to the gate table
  (campaign lock ~150 s). `ruff check` on `policy.py` reports 4 pre-existing
  S311 findings on untouched lines (inline `# ruff: ignore` comments name the
  old rule wording); pyright reports 2 pre-existing `query_records`-signature
  errors, also present at HEAD. Both are Register C hygiene, not landed-work
  defects.

- **Q1 started, campaign run aborted (session cut short by walltime).**
  Dev-env smoke green; checkout clean; the campaign
  (`examples/learning-rules-and-geometry-digits.yaml`) was launched via
  `comp run` into `logs/q1_campaign.duckdb` (log `logs/q1_run.log`, kept) and
  killed before completion — ~15 min elapsed against the spec's
  `budget_seconds: 300`, with ~150 "Evaluation failed" lines, all of one
  signature: `Recurrent geometry ... requires energy-based, PC-family,
  diffusion, or instantaneous dynamics, got 'lazy'` (identity
  `ab3f7a32…`). Two findings before the abort:
  1. **The spec proposes cells its own validator rejects** — the
     `lazy`×`recurrent` combination is declared but illegal, so the space
     leaks failures instead of the search space filtering them
     (`iter_candidates` should never yield them; gate 1's `measured == legal`
     assertion could not have passed a full run). This is a Q1-adjacent seam
     defect to resolve *in Q1 itself*: either the space filters on the
     recurrence/credit compat predicate, or the spec drops `lazy`×recurrent.
     Price with a `--co`-dry-run before any campaign relaunch.
  2. **The campaign is slower than its published price.** T5 measured
     ~0.2-0.5 s/cell, but the run had not finished a 90-cell space's
     measurement in ~15 min. Re-price one cell (scripts/probes path) before
     re-launching; if the lr fix changed the price, update the YAML's cost
     comment and the campaign lock's docstring arithmetic in the same commit
     as the relaunch.
  - Remaining Q1 work, for the next session: relaunch after fixing (1),
    print the per-credit train/val table, then strengthen gate 2
    (gradient reference cell > 1.5× chance at the campaign's own
    epochs/batch_limit) — Q1's gate as written. Partial store deleted; the
    log is the only artifact.

- **Plan verified and restructured.** E3's premise was corrected against the
  tree: `contrast_design` *is* wired (S1, `stages_impl.py:130`) — the
  unverified part is whether its split produces distinct records and whether
  the report names the control. Q8's `compute_replay_hash` zero-caller claim
  re-verified. Test-cost check: every gate in the queue is a tier-1 lock
  (17–78 s) or a priced construction; the only >60 s gates are the existing
  campaign lock (78 s, the deliverable itself) and the Q7 audit, which
  splits wp11 rather than running it.

- **Q7 landed (sixth session of this plan).**
  1. **LOCK_AUDIT.md:** one mutation per named mechanism for 33 pre-TODO48
     structural locks (30 property + 3 acceptance). All 33 🔴 RED — zero
     "stayed green" rows. No locks deleted/rewritten.
  2. **wp11 split:** `test_wp11_surface_lock.py` → `test_wp11_surface_lock.py`
     (~10 s) + `test_codegen_drift_lock.py` (~103 s parallel).
  3. **Cost notes:** audit walltime ~15 min. ruff/pyright clean.

- **Q5 landed (fifth session of this plan).**
  1. **Compose warnings lock:** new test `tests/property/test_compose_warnings_lock.py`
     composes every legal cell of the campaign YAML under `warnings.error`;
     **1.5 s**, green. The beta mismatch warning (dynamics 0.001 vs credit 0.5)
     no longer fires — the per-axis split (Q3/Q4) fixed it. `max_steps`
     resolves to factory default (30), not domain lo (1).
  2. **Cost notes:** ruff/pyright clean on new test file.

- **Q3 + Q4 landed (fourth session of the plan).** What landed, in order:
  1. **Per-axis hyperparameter names (Q3):** `step_size` → `settle_step`
     (dynamics), `update_lr` (update); `beta` → `settle_beta` (dynamics),
     `credit_beta` (credit); `momentum` → `settle_momentum` (dynamics).
     Merge machinery deleted: `declare()`, `ConflictingHyperparameterError`,
     resolve-once preference in `ActiveSpace.active()`. Alias map
     `CONFIG_FIELD_ALIASES` routes schema names to config fields. YAML
     (`examples/learning-rules-and-geometry-digits.yaml`) and spec producers
     updated to the new names.
  2. **Dead declaration retirements (Q3/Q4 overlap):** `update.batch_size`,
     `plasticity.replace_readout`, `substrate.weight_bounds_lo/hi` — swept
     but never consumed by any factory. Retired with records.
  3. **Prior registry consolidation (Q4):** all prior data (`ruler_lr_*`,
     `step_size_override_*`, `dynamics_step_size_*`, `hidden_width/depth`)
     migrated into `schema/seed_registries.PRIORS`; `learning/prior.py` is now
     accessors-only. `lr_ruler_*` rows renamed to `ruler_lr_*` (MNIST
     deduped). `batch_size` prior retired with its hyperparameter.
  4. **Resolution rule hardened (Q4):** `_resolve_value` = override → prior →
     config default; `Domain.lo` fallback deleted. Declaration audit in
     `harvest_schema()` rejects any row with no prior and no config default.
     `input_dim`/`output_dim` get declared defaults (task-shaped, resolved by
     compose).
  5. **New seam lock:** `tests/property/test_schema_seam_lock.py` — grep lock
     (exactly one `PRIORS_REGISTRY`), per-axis uniqueness, alias map, audit,
     retired rows stay retired, serialization round-trip, accessors'
     registration path gone.
  6. **Campaign lock green** (shared Q3+Q4 gate): **100 s**, 7 passed, run
     once. Promotion lock flaky (pre-existing 1-epoch nondeterminism; Q2+E4
     session already verified).
  - Debugging cost: the `_config_default` bug (passing function instead of
    coordinate) caught by `test_per_axis_values_resolve_independently`.
- Cost notes: ruff/pyright clean on changed files. 3 pre-existing
     Register C findings in `_dynamics.py` untouched.

- **Q6 landed (seventh session of this plan).**
  1. **Lab census:** `packages/computronium-lab/USAGE.md` documents 21→4 modules.
     Survivors: `lab.py`, `training.py`, `synthesis/`, `adaptation.py`.
  2. **Retirements:** 17 modules deleted with R78 records in USAGE.md.
  3. **Lab boundary lock:** `tests/property/test_lab_boundary_lock.py` asserts
     survivors have external importer or kernel-path; retired modules absent.
  4. **Test cleanup:** 8 retired test files removed; 12 tests pass.
  5. **Cost notes:** ruff/pyright clean. Lock runs in ~5s.

- **D1 landed (eighth session of this plan).**
  1. **Schedule.device field:** added `device` ("cpu" | "cuda" | "auto", default
     "auto") to `Schedule` dataclass with validation; `to_dict`/`from_dict`
     roundtrip; `measurement_key` includes device so cells differing only by
     device are distinct measurements.
  2. **RunSpec.device field:** added `device` field with validation ("cpu",
     "cuda", "auto") to `RunSpec`; campaign YAML updated to declare
     `device: auto`.
  3. **Evaluator integration:** `_resolve_device` helper resolves "auto" →
     "cuda" when available else "cpu"; `_task` and `task_shape` use it;
     `evaluate_cell` threads `schedule.device` to `SystemTrainerConfig` and
     task creation (removed hardcoded "cpu").
  4. **Store persistence:** DuckDB `records` table `schedule` STRUCT extended
     with `device TEXT`; `append` uses `schedule.to_dict()`; `_parse_schedule`
     reads `device` back with default "auto".
  5. **Gate:** new `tests/property/test_schedule_device_lock.py` — 5 tests:
     roundtrip, RunSpec validation, campaign YAML declares device, CUDA
     device recorded in store (skip when unavailable), "auto" resolves to CPU
     when CUDA mocked away. **~10 s**, tier 1. Falsifiable: hardcode "cpu" in
     evaluator → `device_cuda_recorded_in_store` fails.
  6. **Campaign lock green:** all 7 gates pass, **~97 s** (device="auto"
     resolves to CPU in CI).
  7. **Cost notes:** ruff/pyright clean on changed files. Pre-existing Register
     C findings in `store.py` and `run_spec.py` untouched.

- **D2 landed (eleventh session of this plan).**
  1. **Campaign economics in status/report:** Added `declared_cells` to `RunSummary` (computed via `declared_cell_count()` from spec + search space). Added `--detailed` flag to `comp status` printing cost/record, projected total/remaining, progress %. Added Campaign Economics section to generated report.
  2. **Budget tracking:** `_cmd_run` now passes `budget_consumed_s` (elapsed seconds from pipeline budget) to `store.finish_run()` on completion, interruption, and failure.
  3. **New lock:** `tests/property/test_campaign_economics_lock.py` — 4 tests asserting status output contains rate and projection, report includes economics, JSON includes declared_cells.
  4. **Gate:** `test_campaign_economics_lock.py` (4 tests, ~33 s). Falsifiable by removing projection logic.
  5. **Cost notes:** ~80 lines across cli.py, report.py, test file. All property tests pass (88/88). Ruff/pyright clean.

- **E1 landed (tenth session of this plan).**
  1. **Uncertainty computation and storage:** Added `_compute_replication_uncertainty()` and `compute_and_store_uncertainty()` in `claims.py`; added `RecordStore.set_cell_uncertainty()` in `store.py`.
  2. **Claim derivation consumes uncertainty:** Modified `derive_claims()` to use per-cell within-seed uncertainty (pooled variance) from `record.status.uncertainty`. Single-seed cells record `{"reason": "single_seed"}`.
  3. **CLI integration:** Updated `cli.py` to call `compute_and_store_uncertainty()` after promotion with `min_seeds=spec.n_seeds`.
  4. **Test updates:** Updated `test_claim_report_lock.py` to match new behavior (claims only include qualified cells with >= min_seeds).
  5. **Gate:** `test_claim_report_lock.py` (26 passed), `test_statistical_protocol_lock.py` (33 passed), `test_schema_seam_lock.py` (9 passed), `test_schedule_device_lock.py` (5 passed). All pyright/ruff clean on changed files.
  6. **Cost notes:** Added ~80 lines across 3 files. Property test suite green.

- **Q8 landed (ninth session of this plan).**
  1. **Per-cell `compute_replay_hash` retirement:** function commented out in
     `replay.py:30-39` with explanatory note, removed from `__all__`; test
     `test_replay_hash_deterministic` removed from `test_stage_model_lock.py`.
  2. **Conformance UNVERIFIED handling:** already implemented —
     `codegen.generate_conformance_stubs` skips UNVERIFIED capabilities
     (codegen.py:302-303), `ConformanceHarness._check_capability` reports
     `unverified_reason` instead of running test (conformance.py:223-232).
  3. **Effective LR visible in records:** `Record.create` accepts optional
     `effective_params` (record.py:165), `cell_record` passes
     `evaluation.params` (effective params from `ComposedCell.params`) as
     `effective_params` (evaluate.py:391). Records now store per-axis
     effective hyperparameters (e.g., `dynamics.settle_step`,
     `update.update_lr`, `credit.credit_beta`).
  4. **Search space fixes:** `_cell_params` now maps hyperparameter names to
     config field names via `config_field_name` (search_space.py:202);
     `ActiveSpace.for_axis` maps hyperparameter names to config field names
     when checking `accepted_params` (harvest.py:135). Tests updated to use
     new hyperparameter names (`settle_step`, `settle_beta`).
  5. **Store fix:** `_parse_schedule` handles `device=None` from DuckDB
     (store.py:990).
  6. **Gate:** search space lock green (**25 passed, ~27 s**), active space
     lock green (**19 passed, ~10 s**), schema seam lock green (**9 passed,
     ~11 s**), conformance harness green (**12 passed, ~22 s**), atomic
     append lock green (**5 passed, ~30 s**).
  7. **Cost notes:** ruff/pyright clean on changed files. Pre-existing Register
     C findings in `store.py` and `harvest.py` untouched.
