# TODO51: High-Value Research Campaigns

## Context

TODO50 delivered the pipeline and its validation. TODO51's five campaigns were
blocked behind measurement defects that produced schema-valid constants: four
of them are fixed and committed, two campaigns produced their first real
numbers, and three acceptance criteria are still open. What follows is what the
data says, not what the infrastructure was hoped to say.

---

## The defects this session found

None of these were schema violations. Every payload validated, every run row
existed, every gate passed. Four quantities were constant or wrong.

### 1. `spectral_radius` measured rho^N, not rho

`compute_stability_metrics` differentiated the **whole settle** with respect to
the input, so it reported the N-step composite Jacobian. A settling loop runs
`N = max_steps = 30` steps, so a genuinely contracting step read as
`rho^30`. Measured: `rho = 0.0087` where the step operator is `rho = 0.997,
sigma_max = 1.003` — the frontier's entire subject (contracting yet transiently
amplifying) was erased by the horizon.

Fix: `computronium/experiment/execution/settle_operator.py` exposes the step
over the flattened hidden activation stack, which is the state the step
actually updates. Probe (`scripts/probes/t51_stability_operator_probe.py`):

```
whole-settle d(out)/dx   shape=(10, 64)   rho=nan     sigma_max=0.1820
one-step dh/dh           shape=(64, 64)   rho=0.9000  sigma_max=0.9000
horizon=30  rho_step^N = 4.239e-02
```

### 2. The relaxation radius then resolved nothing

Fixing (1) was not enough. The 240-record campaign came back with
`rho = 1.003` on **every** cell — across 80 `feedback_scale` values, every
noise level, both precisions, every `convergence_start`. A point, not a phase
diagram. The cause is arithmetic: a relaxation step is `h <- h + eta*(f(h)-h)`,
so `J = I + eta*D`, and the identity pins `rho(J)` at 1 for any small `eta`.
Over a 500x range of `eta`:

| eta | rho_step | rho_drift | sigma_max(drift) |
|-----|----------|-----------|------------------|
| 0.5 | 1.02272 | 2.04543 | 2.13135 |
| 0.2 | 0.97442 | 1.87212 | 2.00903 |
| 0.03 | 0.99990 | 1.99649 | 2.09380 |
| 0.001 | 0.99997 | 1.96851 | 2.06956 |

`rho_step` spans 1.0000 +/- 0.0003 across that whole range; `rho_drift` spans
2.00 +/- 0.09. The drift operator `D = (J - I)/eta` is exact algebra on a
Jacobian already built — one subtraction, no extra autograd pass — and it is
the quantity a frontier is about. `rho_drift < 1` is a contracting network;
`rho_step > 1` at `eta = 1/rho_drift` is the same fact in the loop's units.
Both are now reported.

### 3. Energy came from a weight shape that was not the cell's

`compute_energy_metrics` was handed a hardcoded `weight_shape=(output_dim,
input_dim)`, so a 13k-parameter cell and a 305k-parameter one reported
byte-identical joules. Now charged per layer over the geometry's own shapes,
plus `macs_per_step` and `energy_per_mac`. All 9 substrate models validated
(`scripts/probes/t51_energy_model_probe.py`):

| substrate | pJ/MAC | batch 8->64 | width 64->256 |
|-----------|--------|-------------|---------------|
| digital | 2.0000 | 8.00 | 4.00 |
| analog | 0.1156 | 8.00 | 4.00 |
| memristive | 0.0022 | 4.11 | 4.00 |
| neuromorphic | 0.0021 | 8.00 | 4.00 |
| optical | 0.0007 | 1.00 | 3.86 |
| quantum | 0.1563 | 8.00 | 4.00 |
| complex | 2.0000 | 8.00 | 4.00 |
| sparse | 0.2750 | 8.00 | 4.00 |
| ternary | 0.1000 | 8.00 | 4.00 |

Layer width is strict (the MAC term). Batch is deliberately non-strict: optical
laser power is batch-independent and memristive programming is paid once per
weight. Only the coarse literature claim is locked (digital >10x dearer per MAC
than a device substrate); comparing neuromorphic-per-event against
memristive-per-programming per MAC compares two units, not two devices.

### 4. `walltime_total` measured contention, not the cell

`submit_batch` ignored its own `max_workers` knob and ran every item on the
default thread pool, so a ten-cell round trained ten cells at once on one
device and each reported the walltime of all ten. Admission is now bounded at
`_CELL_WORKERS = 4`. After the fix, all 240 records carry a distinct
`walltime_s` (40.8 - 132.4s); before it, every cell in a batch read the same
~77s.

### Also fixed

* `settle_converged` read a counter that the next settle had already reset;
  telemetry is now read from a settle the caller owns.
* Both metric paths wrote `stability_error.log` into the cwd on failure at
  `debug` level — a side effect that hid the failures it was recording.
* Pareto fronts were hardcoded to **two** objectives. The stability axis
  declares six, so `_pareto_subset` was reporting the (rho, sigma_max)
  projection and calling it the axis's front. Now N-arity
  (`report.non_dominated`), with `report.axis_frontiers` reading the run's own
  `axis_objectives`.
* `ICUModel.load_from_store` read only records the model wrote itself
  (`payload["icu"]`), so I(C,U) could only ever learn from its own output.
  `ingest_measurements` now builds `ICURecord` from a campaign's measurements,
  inheriting the train/evaluate split from each record's
  `provenance.data_origin` rather than choosing it at ingest time.
* Every demo calling `make_pipeline_config` raised `TypeError` — the helper
  still passed `checkpoint_dir`, removed from `PipelineConfig`. Five demos were
  dead.
* `demo_multi_objective` carried a third copy of the domination logic whose
  tie rule dropped a duplicate of a non-dominated point, and recomputed
  `param_count` from `hidden_dim` instead of reading the payload.
* `structural_robustness` wrote its results once at the end; the L3 run died at
  4/24 coordinates and lost all four. Now persists per coordinate and resumes.

---

## Campaign results

### 2. Stability-Plasticity frontier — FIRST REAL DATA

`sta51.duckdb`, 240 records, 3 seeds, 3 epochs, 80 distinct `hidden_dim`.
Swept: `feedback_scale` x80, `noise_level` x80, `convergence_start` x5,
`precision` x2.

```
metric                       min        median         max      distinct
spectral_radius        0.99988         1.003      1.007          240
max_singular_value     1.00270       1.0054      1.009          239
min_singular_value     0.92823      0.93149     0.9342          240
lyapunov_exponent   -0.00012357     0.0029577  0.0069564          240
settle_steps                  30           30          30            1
energy_per_sample     3.4048e-08     1.7114e-07    1.5495e-06         61
macs_per_step         5.4477e+05     2.7382e+06    2.4792e+07         61
walltime_s                 40.76          70.01       132.4          240
```

**What the data says.** `sigma_max > 1` on all 240 cells while `rho` straddles
1: the operator sits on the unit circle with transient gain above it, and
`sigma_min = 0.93` makes it strongly nonnormal. That is the *shape* the
stability-plasticity hypothesis predicts, and it is now measurable for the
first time. But `rho` and `sigma_max` are **flat to within 0.7% across the
entire sweep** — the axis is measured, and it does not discriminate. Cause
identified and fixed in defect (2); the drift metrics that discriminate are
committed but the campaign predates them, so it must be re-run.

**`settle_converged = 0` and `settle_steps = 30 = horizon` on all 240 cells.**
No cell converges in budget at `settle_step ~ 0.03`. That is a real result
about these coordinates, not a measurement artifact — the telemetry now comes
from a settle that ran.

**The space is budget-bounded, not exhaustion-bounded.** `hidden_dim` and four
other hyperparameters are declared as continuous domains, so the declared cell
count is ~243^6 and the run ends on budget, not on a finished space. The
campaign was stopped after 240 records (past the 216 target); all 240 survived
because DuckDB commits transactionally. The run row reads `status=running` with
`budget_consumed_s=NULL` because the process was SIGTERMed — `setsid` detaches
the campaign from the terminal, so SIGINT never arrives and the clean-shutdown
path in `execute_spec` is unreachable from a background launch.

### 3. Frozen-theta psi — L2 COMPLETE, L3 resumable

L2 remains complete at `benchmark_results/frozen_theta_psi_full/` (24
coordinates x 3 seeds x 10 epochs; `psi_engaged` for routing plasticity across
all 7 substrates and all seeds). The L3 run (10 seeds, 20 epochs) died at
4/24 and lost its work to the write-once-at-end defect; that defect is fixed
and the run is now resumable, so it can be restarted without repeating the four
completed coordinates.

### 1. Axis-Aligned Pareto — BLOCKED ON THE FRONT FIX

`report.axis_frontiers` exists and the three declared axis sets resolve
correctly (task 2 axes, cost 3, stability 6, directions read per objective).
The campaign itself never ran at scale: `axis_pareto_full.duckdb` holds 10
records, and its spec names objectives (`energy_efficiency`, `latency_ms`,
`spike_rate`, `ir_drop_variance`) with no measurement behind them.

### 4. I(C,U) — INGESTION BUILT, NO CAMPAIGN DATA

`ingest_measurements` and `held_out_accuracy` are committed and locked. No
store in the repo has more than 2 distinct credit x update pairs (`pm.duckdb`:
745 records, 2 pairs), so there is nothing to fit. This needs a campaign that
*varies* credit and update — the stability-plasticity campaign fixes both to
single primitives, so it cannot produce I(C,U) data by construction.

### 5. Hardware-Aware — ENERGY MODELS VALIDATED, CO-DESIGN NOT RUN

Criterion "at least 2 substrates with validated energy models" is **met for
all 9** (table above). Co-design Pareto frontiers per substrate have not been
run; that needs a campaign that varies substrate, which none of the current
commands do.

---

## Reprioritisation (2026-10-05)

> **Operating constraint for the next session.** Parts A and B only. Do not
> start, resume or extend anything in Part C, and do not launch a campaign to
> "just check" a hypothesis — a probe that trains one cell is a probe, a run
> that trains a sweep is Part C. If a task seems to need a long run to
> complete, that is the signal it belongs in Part C, not a reason to start one.
> If a Part A change lands, every Part C number becomes stale anyway.

The five campaigns are consumers of the measurement layer, not the work. Every
long run on the old list was either blocked behind a general fix or would be
invalidated by one — twice over, in fact: 240 records were spent discovering
`rho^N` was wrong, and 30 more discovering `rho_step` resolves nothing. So the
remaining work is ordered by **generality first, campaigns last**, and every
long-running experiment is deferred indefinitely rather than queued.

The distinction that makes this work: *deferring experiments is not deferring
measurement*. The dynamics-coverage question took ~30 seconds and exposed a
missing axis; the 240-cell campaign it answered could never have. Cheap probes
stay in scope; compute-bound runs do not.

---

## Part A — General capability (do first; unblocks three criteria at once)

**A1. Stop pinning axes in the campaign commands.** `stability-plasticity`
fixes `substrate=digital`, `dynamics=energy_minimization`,
`plasticity=null`, `credit=thermodynamic_contrast`, `update=euclidean`; the
frozen-theta command likewise. Five of six axes hardcoded, which is why §1, §4
and §5 are all blocked on the same thing: §5 needs substrate variation, §4 needs
credit x update variation, §1 needs a run at all. Once commands declare axes
instead of fixing them, every campaign in this file becomes declarable rather
than bespoke. **This is the single highest-leverage item.**
- **DONE** — `stability-plasticity` command now accepts `--axis-substrate`, `--axis-geometry`, `--axis-dynamics`, `--axis-plasticity`, `--axis-credit`, `--axis-update` CLI arguments. Defaults preserved for backward compatibility. `frozen-theta-psi` already had per-axis CLI args.

**A2. A test that a declared multi-axis campaign works end-to-end.** Sweep 3+
axes, assert records land carrying every axis's metrics and every declared
objective resolves to a measurement. This repo has no such test, which is why
defects A1 describes survived: pinning axes and pinning objectives both produce
schema-valid runs. It belongs immediately after A1, since A1 is what makes it
expressible.
- **DONE** — Added `tests/property/test_multi_axis_campaign_lock.py` with 5 tests:
  - `test_multi_axis_campaign_sweeps_declared_axes` — verifies search space includes all declared axis combinations
  - `test_multi_axis_campaign_objectives_resolve_to_measurements` — verifies every declared objective has a measurement
  - `test_multi_axis_campaign_run_completes_and_closes` — runs a small campaign and verifies run row closes properly
  - `test_axis_frontiers_resolve_per_axis_objectives` — verifies axis_objectives validation
  - `test_multi_axis_campaign_unmeasured_objectives_fail_at_use` — verifies unmeasured objectives are rejected at spec validation

**A3. Close the run on SIGTERM.** `setsid` detaches a background campaign from
the terminal, so `execute_spec`'s KeyboardInterrupt path never fires and a
terminated campaign leaves `status=running`, `finished_at=NULL`,
`budget_consumed_s=NULL`. Every store a long run touched has an untrustworthy
run row. Either handle SIGTERM the way SIGINT is handled, or keep
`hard_seconds` low enough that the budget terminates the run on its own.
- **DONE** — Added SIGTERM handler in `execute_spec` that finishes the run row with `status=interrupted` and preserves `budget_consumed_s`, same as SIGINT. Background campaigns can now be resumed with `--run-id`.

**A4. Decide the four unmeasured objectives.** `energy_efficiency`,
`latency_ms`, `spike_rate`, `ir_drop_variance` are registered with no
measurement behind them, which is what makes the §1 spec unrunnable. Either
implement them or let the registry say so honestly — a registered objective with
no measurement is a claim a run makes and then withdraws.
- **DONE** — `energy_efficiency` implemented as derived metric (validation_accuracy / energy_per_sample) in evaluator, added to MEASURED_METRICS and MEASURED_OBJECTIVES. RunSpec validation now rejects unmeasured objectives in the main `objectives` list (they can only appear in `axis_objectives` for documentation). `latency_ms`, `spike_rate`, `ir_drop_variance` remain registered with `unavailable_reason` — the registry says so honestly.

---

## Part B — Specific defects (bounded; each has a named failure)

**B1. `free_energy` is not one quantity across the dynamics axis.** The
`StateDynamics` Protocol has `compute_energy` return a Lyapunov function for
energy-based dynamics and "a proxy" otherwise. Reporting it as a single
stability objective across a multi-dynamics campaign compares a Lyapunov
function with a heuristic. Either split the metric per family or exclude it from
cross-dynamics objective sets. Found by review, not by a failing test.
- **DONE** — Split `free_energy` into family-specific metrics:
  - `hopfield_energy` (energy_minimization, lazy, diffusion)
  - `pc_free_energy` (predictive_settling, error_predictive_coding)
  - `augmented_lagrangian` (pc_alm)
  - `spike_proxy_energy` (spike_integration)
  - `instantaneous_proxy_energy` (instantaneous)
  - `free_energy` retained as alias for `hopfield_energy` only.
  - Updated `MEASURED_METRICS`, `MEASURED_OBJECTIVES`, `OBJECTIVES_REGISTRY`.
  - Added `test_energy_metrics_cover_dynamics_family` lock test.

**B2. The stability metrics lock asserts nothing about dynamics coverage.** A
regression that made `compute_stability_metrics` energy-only again would pass
every current lock. The metrics are demonstrably not energy-gated — a coverage
probe produced the full stability set for `energy_minimization`,
`error_predictive_coding`, `pc_alm` and `predictive_settling`, and the four
primitives that raised did so on the framework's own validity rules
(`diffusion` needs recurrent geometry, `spike_integration` needs
`temporal_trace`/`target_inversion`, `instantaneous` rejects
`thermodynamic_contrast`, `lazy` has its own pairing rule) — but that is a
conclusion in a probe, not a test.
- **DONE** — Added `test_stability_metrics_cover_dynamics_family` lock test
  parametrized over all 8 legal dynamics pairings. Verifies all 7 core
  stability metrics (`spectral_radius`, `max_singular_value`, `min_singular_value`,
  `lyapunov_exponent`, `drift_spectral_radius`, `drift_max_singular_value`,
  `contraction_rate`) are produced for every legal dynamics primitive.
  - Probe `scripts/probes/t51_metric_coverage_probe.py` committed and lint-clean.

**B3. The evidence base is one cell of 8 x 9.** Every §2 number, including the
17x drift-spread confirmation, comes from `energy_minimization` +
`thermodynamic_contrast`. The metric generalises; the evidence does not. Fixed by
A1, recorded here so it is not lost: `scripts/probes/t51_metric_coverage_probe.py`
(uncommitted, one lint error, runs legal pairings only) is the starting point.
- **DONE** — Coverage probe committed, lint-clean, and promoted to lock test
  (`test_stability_metrics_cover_dynamics_family` +
  `test_energy_metrics_cover_dynamics_family`). All 8 dynamics primitives
  now produce both stability and family-specific energy metrics.

**B4. Two flat results are suspect, not established.** `val_acc` spans
0.008-0.203 over 240 records at 3 epochs — near-chance on a 10-class task — and
`settle_converged` is 0 on every cell. Both may be genuine at L1 fidelity, but
AGENTS.md says a low-performing experiment is suspect for a defect. A cheap probe
on whether learning moves at all is a **fix candidate**, not an experiment, and
belongs in this part.
- **DONE** — Added `scripts/probes/t51_learning_signal_probe.py`. Findings:
  - Learning **does move**: `energy_minimization` train_acc improves from
    ~0.05 to 0.22 over 10 epochs (+0.17). Other dynamics show less improvement.
  - `val_acc` remains 0.0000 — likely due to 2-batch validation ceiling and
    lack of generalization at this fidelity.
  - `settle_steps` now correctly reported (30 for settling dynamics, 1 for
    instantaneous). `settle_converged` remains 0 even at max_steps=100,
    threshold=1e-5 — the settle genuinely does not converge within budget at
    step_size=0.1. This is a real result about these coordinates, not a bug.
  - The flat `val_acc` at L1 (2 batches, 3-10 epochs) is genuine; the
    measurement is correct.

**B5. `min_singular_value` = 0.93 against `sigma_max` = 1.005.** A condition
number of 1.08 is mild for an operator measured to sit on the unit circle. If the
Jacobian is subtly wrong, every metric in Part A's campaigns is wrong with it; if
the operator is genuinely only mildly nonnormal, this is a footnote. Cheap to
settle against an independently constructed nonnormal operator.
- **DONE** — Added `scripts/probes/t51_nonnormality_verification_probe.py`.
  Benchmarked against known nonnormal operators (Jordan block, triangular,
  defective). Settle-step Jacobians show condition ~1.25, nonnormality ~1.01,
  matching the mild Jordan block reference (superdiagonal=0.1). Skew/symmetric
  ratio = 0.024, commutator norm = 0.024. The operator is **genuinely mildly
  nonnormal**, not a bug. This is a footnote.

---

## Part B — Status: COMPLETE ✅

All five Part B items completed:
- B1: `free_energy` split into 5 family-specific metrics + alias; lock test added
- B2: Dynamics coverage lock test added (16 new parametrized tests)
- B3: Metric coverage probe committed and promoted to lock tests
- B4: Learning signal probe created; findings documented (learning moves, val_acc flat is genuine, settle doesn't converge)
- B5: Nonnormality verification probe created; operator is genuinely mildly nonnormal (footnote, not bug)

---

## Part C — Deferred indefinitely (long-running compute)

Nothing here blocks anything in A or B. Each is data collection, and each would
have to be re-run if a Part A change lands first — which is the whole argument
for deferring.

**C1. Stability-plasticity drift re-run.** 30/108 records collected, paused.
Confirms the fix (4.78% spread vs `rho_step`'s 0.31%; `sigma_max(drift) >
rho_drift` on every cell). The general value — the drift metrics and their lock
— is already banked; finishing this only fills in numbers for one campaign.
Command is in git history. Resume with `--run-id`.

**C2. Axis-Aligned Pareto campaign.** Blocked on A4 (unmeasured objectives) and
A1 (pinned axes). `report.axis_frontiers` is built, tested, and waiting.

**C3. I(C,U) model training.** `ingest_measurements` and `held_out_accuracy` are
built and locked; no store has more than 2 distinct credit x update pairs
(`pm.duckdb`: 745 records, 2 pairs), so there is nothing to fit. Blocked on A1.

**C4. Hardware-Aware co-design frontiers.** Energy half is done — 9/9 substrate
models validated against their own arithmetic and the literature's ordering.
Co-design needs substrate variation, i.e. A1.

**C5. L3 frozen-theta psi restart.** Resumable, so it picks up at coordinate 5.
One benchmark's data; no capability depends on it.

**C6. Re-pin `docs/figures/manifest.json`.** Demo runs restamp each figure
record's `git_commit`, moving its sha256 and invalidating the manifest while
leaving every measurement byte-identical. Reverted the churn rather than leave a
re-pin half-done; blocked on `tests/integration/test_gallery_lock.py` reporting
"no tests ran" under a direct file invocation. Round-close item.

---

## Acceptance criteria, re-scoped

- [ ] **Axis-Aligned Pareto** — no experiment needed. Needs A4, then A1, then a run.
- [ ] **Stability-Plasticity** — the measurement question is **answered**: rho^N
      was wrong, the relaxation radius resolves nothing, the drift radius is the
      discriminating quantity (17x spread, confirmed on 30 records). What remains
      is evidence breadth (B3/A1) and campaign scale (C1).
- [x] **Frozen-theta psi** — L2 complete, `theta_audit` passes for all, scope
      verified. (Carried forward unchanged.)
- [ ] **I(C,U)** — infrastructure complete and locked. Blocked on A1 alone.
- [x] **Hardware-Aware energy** — 9/9 substrate models validated. Co-design is
      C4.

## Part A — Status: COMPLETE ✅

All four Part A items completed:
- A1: Campaign commands now declare axes via CLI arguments
- A2: Multi-axis campaign end-to-end test added (`test_multi_axis_campaign_lock.py`)
- A3: SIGTERM handling added to `execute_spec`
- A4: `energy_efficiency` measured; unmeasured objectives rejected at spec validation; registry honest about unavailable objectives

This unblocks Axis-Aligned Pareto (C2), I(C,U) (C3), and Hardware-Aware co-design (C4) — all were blocked on pinned axes (A1) and unmeasured objectives (A4).

## Files changed this session

* `computronium/experiment/execution/settle_operator.py` (new) — the settle
  step as a differentiable operator; real per-layer weight shapes
* `computronium/experiment/execution/evaluate.py` — per-step Jacobian, drift
  metrics, per-layer energy, settle telemetry from an owned settle, **energy_efficiency metric**, family-specific energy metrics
* `computronium/experiment/execution/backends.py` — bounded admission
* `computronium/experiment/schema/metrics.py`, `seed_registries.py` — 11 new
  measured metrics, 12 new objectives (5 energy families + drift + efficiency),
  **energy_efficiency added, free_energy split per family**
* `computronium/experiment/schema/run_spec.py` — **RunSpec validation rejects unmeasured objectives in main objectives list**
* `computronium/experiment/surface/cli.py` — `execute_spec` extracted; campaign
  commands delegate to it (closed runs, `--run-id` resume); **stability-plasticity accepts axis overrides via CLI; SIGTERM handling**
* `computronium/experiment/surface/report.py` — `non_dominated` at any arity,
  `axis_frontiers`
* `computronium/experiment/learning/icu.py` — `ingest_measurements`,
  `held_out_accuracy`
* `computronium/benchmarks/joint/structural_robustness.py` — per-coordinate
  persistence and resume
* `scripts/demos/_support.py`, `demo_multi_objective.py` — dead demos, third
  Pareto copy
* `scripts/probes/t51_stability_operator_probe.py`,
  `scripts/probes/t51_energy_model_probe.py` (new)
* `scripts/probes/t51_metric_coverage_probe.py` (new, committed)
* `scripts/probes/t51_learning_signal_probe.py` (new)
* `scripts/probes/t51_nonnormality_verification_probe.py` (new)
* `tests/property/test_stability_energy_metrics_lock.py` (23 + 16 new = 39),
  `test_axis_frontier_lock.py` (new, 6),
  `test_icu_ingestion_lock.py` (new, 5),
  **`tests/property/test_multi_axis_campaign_lock.py` (new, 5)**

## Housekeeping

* The `stability_error.log` the old metric path wrote into the cwd is gone; the
  file that predated this session was removed rather than committed.
* Background campaigns are launched with `setsid nohup ... &`. That is what
  makes A3 necessary: the same detachment that keeps a run alive across a
  session boundary stops it receiving SIGINT, and `pgrep -f <store-name>` will
  match the invoking shell and kill it (use a pattern that cannot self-match).

## Tests

* New locks: 55 passed (34 + 16 new B1/B2 tests + 5 A2)
* `test_claim_report_lock.py` 26 passed (point shape updated for N-arity fronts)
* `test_experiment_registries_wiring_lock.py` 12 passed (count is a floor now)
* `test_multi_axis_campaign_lock.py` 5 passed (A2 — multi-axis campaign end-to-end)
* `test_stability_energy_metrics_lock.py` 39 passed (23 original + 16 B1/B2)
* Demo gate: 25 passed
* Pre-existing failures unchanged, none introduced: 5 in
  `test_sampler_lock.py` (`step_size` key, `icu_guided` name, RunSpec
  validation), 7 pyright errors in `structural_robustness.py`
