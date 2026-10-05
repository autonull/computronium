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

## Acceptance criteria

- [ ] **Axis-Aligned Pareto**: needs a spec whose objectives all resolve to
      measurements, then a run. `axis_frontiers` is ready for the analysis.
- [ ] **Stability-Plasticity**: 240/243 records collected; phase diagram
      measured but not yet discriminating. **Re-run required** — the campaign
      predates the drift metrics that give the axis resolution.
- [x] **Frozen-theta psi**: L2 complete, `theta_audit` passes for all, scope
      verified. (Carried forward unchanged.)
- [ ] **I(C,U)**: ingestion built and locked; blocked on a credit x update
      campaign, which no current command generates.
- [x] **Hardware-Aware energy**: 9/9 substrate models validated against their
      own arithmetic and the literature's ordering. Co-design still open.

---

## Next steps, in order

1. **Finish the stability-plasticity drift re-run.** Started, 30/108 records,
   then stopped to wrap up. It confirms the fix works:

   ```
   metric                    distinct   min        median     max
   spectral_radius               30   1.0011     1.0029    1.0042   (0.31% spread)
   drift_spectral_radius         30   2.0341     2.0929    2.1340   (4.78% spread)
   drift_max_singular_value      30   2.1615     2.2113    2.2554   (4.24% spread)
   contraction_rate              30   0.93252    0.93382   0.93568
   ```

   17x the relative spread of `rho_step`, and `sigma_max(drift) > rho_drift` on
   every cell, so the drift operator is nonnormal too. The remaining run is
   just budget: `uv run comp stability-plasticity --store sta51_drift.duckdb
   --run --seeds 3 --epochs 3 --budget-seconds 7200 --rho 0.5,0.9,1.05
   --feedback-scale 0.1,0.5,1.0 --precision float32 --noise-level 0.0,0.01
   --convergence-start 1,5`.

   **Caveat carried forward:** `contraction_rate = 1 - eta*rho_drift` is linear
   theory, not a measurement. It predicts 0.934 while the measured
   `spectral_radius` reads 1.003 — the two disagree because complex eigenpairs
   do not follow `rho(J) = 1 - eta*rho(D)`. It is reported as a prediction and
   labelled as one; it must not be quoted as the observed contraction.
2. **Launch background campaigns with a reachable shutdown.** `setsid` detaches
   the process from the terminal, so `execute_spec`'s KeyboardInterrupt path
   never fires and the run row stays `running`. Either keep a `hard_seconds`
   budget low enough to terminate on its own, or teach the CLI to close the run
   on SIGTERM. Until then, a terminated campaign leaves an unclosed run row.
3. **Give the campaign commands a substrate and a credit x update axis.**
   Criterion 5 needs substrate variation and criterion 4 needs credit x update
   variation; both commands currently pin those axes to single primitives. This
   is the shared blocker for §1, §4 and §5.
4. **Restart the L3 frozen-theta psi run** — now resumable, so it picks up at
   coordinate 5 rather than coordinate 1.
5. **Audit the remaining flat metrics.** `val_acc` spans 0.008-0.203 with 41
   distinct values over 240 records at 3 epochs — near-chance on a 10-class
   task. `settle_converged` is 0 everywhere. Both may be genuine at L1/3-epoch
   fidelity, but "be skeptical of low-performing experiments" applies: a
   learning signal that does not move over 240 cells is worth a probe before it
   is reported as a result.
6. **Widen the campaign off one dynamics primitive.** Every number in §2 —
   including the 17x drift-spread confirmation — comes from
   `dynamics=energy_minimization` + `credit=thermodynamic_contrast`, one cell
   out of 8 dynamics x 9 credit. The metrics themselves are not energy-gated: a
   coverage probe over the registered dynamics produced the full stability set
   for `energy_minimization`, `error_predictive_coding`, `pc_alm` and
   `predictive_settling`. The four that raised did so on the framework's own
   validity rules, not on metric failures — `diffusion` requires recurrent
   geometry, `spike_integration` requires `temporal_trace`/`target_inversion`
   credit, `instantaneous` rejects `thermodynamic_contrast`, `lazy` has its own
   pairing rule. So the evidence base is narrower than the metric, and widening
   the dynamics axis is what makes §2's conclusion about settling systems
   rather than about EqProp.

   Two things follow. `free_energy` cannot be treated as one quantity across
   the axis: the `StateDynamics` Protocol has `compute_energy` return a
   Lyapunov function for energy-based dynamics and "a proxy" otherwise, so it
   must not sit unqualified in a cross-dynamics objective set. And
   `test_stability_energy_metrics_lock.py` asserts nothing about dynamics
   coverage, so nothing would catch a regression that made these metrics
   energy-only again.

   `scripts/probes/t51_metric_coverage_probe.py` (uncommitted, one lint error,
   runs legal pairings only) is the starting point for both.
7. **Reconcile the `min_singular_value` anomaly.** It is 0.93 on every cell
   while `sigma_max` is 1.005, a condition number of only 1.08 — mild for an
   operator measured to sit on the unit circle. Worth confirming against an
   independently constructed nonnormal operator before the nonnormality ratio
   is treated as evidence.

## Files changed this session

* `computronium/experiment/execution/settle_operator.py` (new) — the settle
  step as a differentiable operator; real per-layer weight shapes
* `computronium/experiment/execution/evaluate.py` — per-step Jacobian, drift
  metrics, per-layer energy, settle telemetry from an owned settle
* `computronium/experiment/execution/backends.py` — bounded admission
* `computronium/experiment/schema/metrics.py`, `seed_registries.py` — 6 new
  measured metrics, 7 new objectives
* `computronium/experiment/surface/cli.py` — `execute_spec` extracted; campaign
  commands delegate to it (closed runs, `--run-id` resume)
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
* `tests/property/test_stability_energy_metrics_lock.py` (new, 23),
  `test_axis_frontier_lock.py` (new, 6),
  `test_icu_ingestion_lock.py` (new, 5)

## Loose ends from this session

* `docs/figures/run_records/*.json` are rewritten by every demo-gate run with a
  fresh `git_commit` provenance stamp, which changes each file's sha256 and so
  invalidates `docs/figures/manifest.json`. The measurements in those files are
  byte-identical; only the stamp moves. I reverted the churn rather than leave a
  re-pinning half-done, and `tests/integration/test_gallery_lock.py` did not
  collect under `uv run python -m pytest tests/integration/test_gallery_lock.py`
  (reports "no tests ran" with no error), so the re-pin needs that investigated
  first. Round-close item, not a per-commit one.
* The `stability_error.log` the old metric path wrote into the cwd is gone; the
  file that predated this session was removed rather than committed.

## Tests

* New locks: 34 passed
* `test_claim_report_lock.py` 26 passed (point shape updated for N-arity fronts)
* `test_experiment_registries_wiring_lock.py` 12 passed (count is a floor now)
* Demo gate: 25 passed
* Pre-existing failures unchanged, none introduced: 5 in
  `test_sampler_lock.py` (`step_size` key, `icu_guided` name, RunSpec
  validation), 7 pyright errors in `structural_robustness.py`
