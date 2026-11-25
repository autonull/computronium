# TODO104 — Defect Closure & Competitive Rigor

**Status:** 2026-11-24. Carried forward from the TODO103 serial competitive run.
That run was the first full 6-axis pass (23/75 viable, 1 claim, 21 coordinates)
and it surfaced a set of concrete defects that now block *trustworthy* breadth.
TODO104 closes those defects, then re-runs the cells they hid.

**Principle:** A low cell is a defect probe first. Every item here names a
mechanism, a failing check, and the file it lives in. A fix that moves neither
the cell nor a test is hygiene, not a fix. The map is the artifact; the loop is
the engine.

**Progress 2026-11-25:** Phase 1 (1.1–1.4), Phase 2.1–2.3, Phase 3 (3.1–3.3),
Phase 6.1/6.2 and Phase 7.1 landed, each with a lock. A2 acceptance measured on
the GPU; meta-SEC regenerated with a nonzero objective (3.589). The first
Phase-4 re-run exposed a new defect (A11: every rung-2 pair ran at one seed, so
`d=0.00`); it is fixed and the coverage map re-launched with `SEC_RUNG2=none`
(`logs/serial2_*/`). Open: 2.2 (A5 cost profile), 4.x breadth read, 5.x claims,
6.3 non-MNIST gate, 7.2, 8.x — see §Progress log.

---

## 📊 What the TODO103 run established

Authoritative serial run: `results/sec/serial/` (gitignored), one process per
axis, `SEC_SEMAPHORE=1`, `SEC_RUNG_TIMEOUT=180`. Logs: `logs/serial_20261124_*`.

| Axis | Viable | Coordinates | Claims |
|---|---|---|---|
| credit | 5/19 | 4 | 0 |
| dynamics | 1/8 | 0 | **1** |
| geometry | 5/12 | 5 | 0 |
| update | 8/18 | 8 | 0 |
| plasticity | 1/8 | 1 | 0 |
| substrate | 3/10 | 3 | 0 |
| **TOTAL** | **23/75** | **21** | **1** |

- **Claim:** `dynamics/energy_minimization` on MNIST — `mean_diff=0.0153`,
  CI `[0.0151, 0.0158]`, `p=0.0076`, `d=31.1` (vision `min_d=1.09`).
- **Baseline concurrent run** (one process, semaphore≥2): 6/75 viable,
  4 coords, 0 claims, **133 rung timeouts**. Kept only as the artifact
  demonstrating the defect in A1; the serial run supersedes it.

---

## 🐞 Section A — Discoveries (each is a defect with a fix)

### A1. Concurrency thrashes `torch.compile` on one GPU (infrastructure)
- **Evidence:** baseline run, 133 `status=timeout` rungs; serial run, 0 in
  credit. Same code, same boxes.
- **Mechanism:** four rungs per primitive run concurrently (`asyncio.gather`,
  `asyncio.Semaphore(2)`), each calling `_measure` in a thread; `_eqprop_settle_*`
  is `torch.compile(..., dynamic=False)`, so every new shape/state recompiles
  and hits `config.recompile_limit` under contention.
- **Fix:** the serial driver already avoids it (`scripts/run_sec_axes_serial.sh`,
  one process per axis, semaphore=1). **Close A1** by making serial the *only*
  competitive path and deleting the concurrent default; add a guard that refuses
  `SEC_SEMAPHORE>1` on a single CUDA device for the `_measure` path.

### A2. Settle-kernel recompile crash on non-vision tasks (blocking)
- **Evidence:** update and substrate processes died at `spiking_mnist` with
  `torch._dynamo hit config.recompile_limit (8)` on
  `_eqprop_settle_chunk_simple_noise`, then `leaked semaphore objects ... at
  shutdown`.
- **Location:** `computronium/ontology/_settle_kernel.py:388`
  `_compiled_eqprop_settle_chunk = torch.compile(_eqprop_settle_chunk, dynamic=False)`
  (and the `_analog` / `_simple_noise` twins at ~460/515).
- **Fix:** compile with `dynamic=True` (or `torch._dynamo.mark_dynamic` on the
  shape-carrying args) so settle does not recompile per geometry; or gate the
  compiled path behind a shape-stable check and fall back to eager. **Acceptance:**
  a neuromorphic `spiking_mnist` cell runs L0 without recompile-limit warnings
  and without a leaked semaphore; the lock fails when `dynamic=False` is restored.

### A3. Timeout leaves a live thread holding the GPU (infrastructure)
- **Evidence:** after the concurrent run printed its summary, the process held
  ~10% of RAM and 95% CPU until killed; `asyncio.wait_for(asyncio.to_thread(...))`
  cannot cancel a running thread.
- **Location:** `scripts/run_full_sec_competitive.py` (`run_rung1_ladder_fixed`,
  `run_primitive_full_fixed`), `sec_all_axes._measure_async`.
- **Fix:** cooperative deadline — pass a `deadline_check` into `_measure` /
  `train_epoch` (the harness already supports it, per AGENTS) instead of killing
  a thread. Then a timeout returns a *cell* and frees the device.

### A4. Update knobs refused as "inactive hyperparameters" (partly A1)
- **Evidence:** concurrent baseline refused `mean_norm`, `role_split`, `lion`,
  `schedule_free`, `ortho_adam`, `riemannian_orthogonal` with
  `Hyperparameters update.grad_clip, update.momentum, update.step_size are
  inactive for coordinate ...`. **Serial re-run flipped five of these to
  viable** (`mean_norm`, `lion`, `schedule_free`, `ortho_adam`,
  `riemannian_orthogonal`), so part of this is the A1 artifact, not a stable
  legality verdict. Verify before touching the builder.
- **Mechanism:** `_build_axis_box` sets fields the primitive's `accepted_params`
  may not include; `screen_coordinate` correctly fails loud.
- **Location:** `sec_all_axes._build_axis_box` (~498–519) and
  `_get_primary_knob` (~242–260).
- **Fix:** first re-run the refused set serially and diff; then intersect the
  box's `{axis}.{field}` keys with the primitive's accepted params, so the
  ladder only varies an accepted knob. **Acceptance:** every update primitive
  either runs or returns a *named* reason that is stable across serial re-runs.

### A5. `adafactor` / `natural_gradient` hang past the watchdog (blocking)
- **Evidence:** `update/adafactor` on MNIST exceeded 17 min (killed);
  `natural_gradient` returned `all_refused` only after the watchdog.
- **Fix:** profile once; if it is the settle/SVD path, A2/A3 fixes apply. If it
  is a per-step cost, price it and either run at reduced steps or declare it
  `available=False` with `unavailable_reason="cost"`. **Acceptance:** each
  finishes under its measured `2×` watchdog or is explicitly unavailable.

### A6. Meta-SEC samples a claim seed budget below the floor (methodology)
- **Evidence:** `configs/meta_sec_best.json` → `claim_seeds=3`;
  `DEFAULT_MIN_SEEDS=5` (`experiment/evidence/claims.py:37`); `paired_comparison`
  raises `seed budget 3 below pre-registration floor 5`.
- **Location:** `experiment/meta_sec.py:171`
  `trial.suggest_categorical("claim_seeds", [3, 5, 7, 10])`.
- **Fix:** drop `3` from the search space (or make the floor a hard constraint in
  the objective). A meta-SEC "optimum" that cannot carry a paired comparison is
  not a legal point.

### A7. Meta-SEC objective is degenerate (`best_value=0.0`)
- **Evidence:** `best_value=0.0` in `configs/meta_sec_best.json`; the reported
  params were not selected by a live gradient.
- **Location:** `experiment/meta_sec.py:206` `_simulate_sec_run` returns 0 when
  `"error" in baseline` or `gpu_hours==0`.
- **Fix:** calibrate the proxy on the measured `results/sec/cells.jsonl`
  (per-cell walltime × viable_rate) and assert `best_value>0`; if the proxy
  cannot beat 0, mark the study **invalid** and fall back to declared defaults
  rather than emitting a zero-value "best".

### A15. `conv` died on the reproducibility box (deterministic backward)
- **Evidence:** every `geometry/conv` rung — the vision geometry's own row —
  defected: `adaptive_avg_pool2d_backward_cuda does not have a deterministic
  implementation` (the schedule runs `deterministic=True`).
- **Mechanism:** `nn.functional.adaptive_avg_pool2d` has no deterministic CUDA
  backward; the conv stack pooled through it.
- **Fix:** `geometry._pool_to` uses `avg_pool2d` when the feature extent divides
  evenly by `pool_hw` (the same pooling up to float summation order, and its
  backward is deterministic — verified on the GPU) and keeps the adaptive
  operator for a non-divisible extent. Lock:
  `test_conv_pool_is_deterministic` + `test_conv_reads_the_deterministic_pool`.
- **Note:** the geometry source lock was fake — `__import__("pkg.mod")` returns
  the top package, so it read `computronium/__init__.py`. Fixed to
  `importlib.import_module`.

### A13. Error-blind credits were judged by the accuracy bar
- **Evidence:** `credit/temporal_trace` at 0.1028 (chance 0.10) was reported
  `viable`, and `credit/homeostatic` at 0.0646 `below_bar` — both read no
  label, so chance is their contract (they must be triaged on a non-zero
  update, never on val_acc).
- **Fix:** `sec_all_axes.ladder_verdict` returns `error_blind` for a credit
  whose rule declares `error_blind=True` (`core/system_trainer/spec.py` is the
  single source); the row is counted apart so the error-aware breadth count
  is not moved by a credit that never reads a target. Lock:
  `test_error_blind_credit_is_not_a_bar_verdict`.
- **Remaining:** the cell does not yet record a parameter-update norm, so the
  error-blind *viability* criterion (non-zero update) is still unmeasured.

### A14. The dynamics axis default cannot be created (`split_mnist`)
- **Evidence:** `dynamics/instantaneous` — the axis default — defects at every
  rung: `ValueError: SplitMNIST requires a task_id to be set`.
- **Mechanism:** `FAMILY_TO_TASK["continual"] = "split_mnist"` and the domain
  factory constructs `SplitMNIST(task_id=None)`, which raises on first use. A
  registry task must be creatable from its id alone.
- **Fix (next):** either declare which split a bare `split_mnist` means in the
  domain row (one source: the task's default), or refuse the family by name
  and prefer a constructible family for an axis-orthogonal rule. Note the axis
  default failing is a control-arm defect: every dynamics comparison needs it.

### A12. The ladder swept a field the rule ignores (dead knob)
- **Evidence:** 2026-11-25 coverage run — `credit/gradient` returned val_acc
  0.9172 at every rung (0.015x..22.65x of `credit.feedback_scale`), and
  `homeostatic`/`temporal_trace` returned one value at every rung.
- **Mechanism:** the ladder's primary knob came from the table's first positive
  candidate, not from the field the rule declares it reads. Four credit rules
  already declare `reads(...)` (`thermodynamic_contrast`, `local_goodness`,
  `target_inversion`, `zeroth_order`) but nothing consumed it.
- **Fix:** `sec_all_axes._declared_reads` resolves the rule class and its
  config, and `_get_primary_knob` keeps only declared fields: `zeroth_order`
  now sweeps `credit.fd_step` (the S9e conclusion), `thermodynamic_contrast`
  sweeps `credit.beta`, `GradientCredit.reads` is `frozenset()` (exact
  backprop reads no credit field). A rule with an empty set gets one measured
  default cell (`measure_declared_default`) instead of a dead sweep.
- **Remaining:** the 15 rules without a `reads` declaration still fall back to
  the table order (`homeostatic`, `temporal_trace`, ...), so their ladders may
  still sweep an inert field. Declaring `reads` per rule is the queued work.

### A11. Rung 2 pairs all ran at one seed (`d=0.00` everywhere)
- **Evidence:** the 2026-11-25 re-run logged `Rung 2: coordinate (d=0.00)` on
  every viable primitive; the paired difference was exactly 0.
- **Mechanism:** `sec_all_axes.run_rung2_comparison.run_cell` recorded `seed`
  in the cell but ran `_measure_async(coord, schedule)` with the base
  schedule's seed for every pair, so both arms were one cell run twice. A
  10-cell claim was 1 cell × 10 records.
- **Fix:** `pair_schedule(schedule, seed)` — one seed per cell, `n_seeds=1`;
  lock `test_each_pair_runs_its_own_seed`. `sec_claims._paired_cells` already
  did this, so the defect was the all-axes driver only.
- **Consequence:** the 2026-11-24 rung-2 verdicts (21 coordinates, 1 claim)
  are A11 artifacts, not power statements. The re-run must not read them.

### A8. Registration box fidelity ≠ run fidelity
- **State:** fixed 2026-11-25 (`claim_schedule`); lock in
  `tests/property/test_claim_box_identity_lock.py`.
- **Evidence:** `create_registration` writes `epochs` from the family base box
  (iris=20, cora=200) while the ladder runs `epochs=1`. `box_mismatch` then
  decides a run at a box the ladder never measured.
- **Location:** `sec_all_axes.create_registration` (~856–884) vs
  `run_rung1_ladder_fixed` (`epochs=1`).
- **Fix:** the registration's box must be the box that is measured; either run
  Rung 2 at the registered base box (current) and label the ladder separately,
  or register the L0 box the ladder used. Never mix.

### A9. Results are lost when a process dies (durability)
- **Evidence:** serial `update`/`substrate` printed outcomes but wrote no JSON
  because the process died mid-axis (A2); a full axis of evidence was lost.
- **Fix:** write each primitive's result to disk immediately after it completes
  (`<axis>/<primitive>.json`), and wrap the per-axis loop in `try/finally` so a
  partial axis still flushes. The combined file is a reduce over the parts.

### A10. MNIST geometry defaults still present (carried TODO103 Phase 1)
- **Evidence:** `computronium/ontology/geometry.py` still defaults
  `input_hw=(28,28)` (287), `image_hw=(28,28)` (263, 298), `grid_hw=(16,16)`
  (303), and `:1554` reads `image_hw, (28, 28)`. TODO103 Phase 1 is marked `[x]`
  but the defaults remain.
- **Fix:** make the factory `image_hw`/`input_hw`/`grid_hw` required (no
  default) and derive from `TaskShape` in the builder; update the success-metric
  grep to prove zero remain.

---

## 🧭 Section B — Remaining work carried from TODO103

| ID | Item | State | Where |
|---|---|---|---|
| B1 | Primitive proposals from gaps | 🟡 three candidates named in 8.1; each needs a spec row + wiring lock (the gap table is census-locked) | `schema/gaps.py`, `schema/seed_registries.py` |
| B2 | Budget policy from measured cost model | ✅ `wave.py` sizes each wave from that fidelity's measured cells (measured → positive control → default); the offline `configs/cost_model.pkl` had no reader and is deleted | `wave.py` |
| B3 | Success metrics unmet | ❌ see Section D | — |
| B4 | Consolidated checklist stale (all `[ ]` despite detailed `[x]`) | 🟡 TODO103 §E marked superseded by TODO104 §E | `TODO103.md` |
| B5 | `graph`/`spatial_lattice` hardcoded `edge_index`/`lattice_dims` in `_params_for` | ✅ fixed: no invented topology; builders refuse by name | `sec_loop._params_for` |

---

## 🛠 Section C — Implementation plan (ordered by unblocking value)

### Phase 1 — Infrastructure correctness (unblocks every re-run) ✅
- [x] **1.1** A2: `compile_settle` traces shape-dynamically (`dynamic=True`,
      `_settle_kernel.compile_settle`); lock
      `tests/property/test_settle_dynamic_compile_lock.py`; GPU acceptance
      `scripts/probes/todo104_a2_settle_recompile.py` → two widths of
      `substrate/neuromorphic` on `spiking_mnist` in one process, both
      `measured` (0.7648 @ 51.5s, 0.7555 @ 74.9s), no recompile-limit error.
- [x] **1.2** A3: cooperative deadline — `sec_loop.deadline_params(budget_s)`
      feeds `evaluate_cell`; `_measure(coord, run, budget_s)` reports a
      `timeout` cell; the driver no longer holds a cancelled thread
      (`asyncio.wait_for` gone). Lock: `test_sec_run_infrastructure_lock.py`.
- [x] **1.3** A9: `computronium/experiment/sec_parts.py` writes one part per
      primitive and reduces the axis; `main` flushes in `finally`, so a dead
      process keeps every completed primitive. Lock: same file.
- [x] **1.4** A1: `sec_all_axes.resolve_semaphore` refuses `>1` cell on one
      CUDA device; the driver prints the refusal. `SLOW_PRIMITIVES` pruned back
      to priced rows (the axis defaults and the whole substrate set are no
      longer skipped).

### Phase 2 — Box/legality correctness (unblocks breadth)
- [x] **2.1** A4: `_accepted_knobs(axis, primitive)` intersects the box and the
      primary knob with the harvested `AxisSpec.accepted_params`; lock sweeps
      `lion`/`muon`/`local_adam`.
- [ ] **2.2** A5: profile `adafactor`/`natural_gradient`; fix or mark
      `available=False` with a named reason. (Priced as skips for the re-run;
      the deadline now returns a timeout cell instead of a kill.)
- [x] **2.3** A8: `sec_claims.claim_schedule(registration, fallback)` runs the
      claim at the registered box (fidelity/epochs/seeds), so a ladder cannot
      decide a box it never measured; lock `test_claim_box_identity_lock.py`.

### Phase 3 — Meta-SEC validity ✅
- [x] **3.1** A6: `CLAIM_SEED_CHOICES` derives from `DEFAULT_MIN_SEEDS`
      (3 is dropped); the driver clamps `CLAIM_SEEDS` to the floor.
- [x] **3.2** A7: the proxy reads `record.payload.{walltime_s,val_acc}`
      (was 0 through the top level); `_resolve_best` marks a zero-objective
      study invalid and returns the declared defaults.
- [x] **3.3** Re-ran meta-SEC on `results/sec/cells.jsonl`:
      `best_value=3.589` (was 0.0), `valid=true`, `claim_seeds=7`,
      `avg_walltime_s=15.1` (was 0.0). Ladder factors now always include the
      declared default (factor 1.0).

### Phase 4 — Recover coverage hidden by A1–A5
- [ ] **4.1** Re-run the skipped/refused primitives per axis (serial, fresh
      process) now that Phase 1–2 fixes land. **Launched:**
      `bash scripts/run_sec_axes_serial.sh` → `logs/serial_todo104_driver.log`.
- [ ] **4.2** Target: every error-aware credit has ≥1 legal above-chance cell on
      its target family; every legal composition family trains or has a named reason.
- [ ] **4.3** Reconcile: an "all_refused" that flips to "viable" under serial is
      an A1 artifact, not a mechanism verdict — record it as such.

### Phase 5 — Competitive evidence (tune, then compare)
- [ ] **5.1** For each viable primitive, reach its best declared box (3-point
      ladder + 1 confirmation seed) before any paired comparison.
- [ ] **5.2** Pre-register paired comparisons (fixed `n_max≥5`, no peeking) and
      run to `n_max`; report `equivalent/superior/inferior/inconclusive`.
- [ ] **5.3** Push claim count toward the 18+ target with valid boxes; a claim
      within 1σ of `min_d` is `marginal`, not met.

### Phase 6 — Hardcoded removal (A10 + B5)
- [x] **6.1** Factory `getattr(config, "image_hw", (28, 28))` fallback deleted;
      `GeometryConfig.spatial_lattice` requires `lattice_dims`;
      `build_spatial_lattice_config` refuses a cell that declares none
      (`_as_int_tuple(..., None)`), so a guessed extent cannot train.
      Remaining: the dataclass field defaults (`input_hw`/`image_hw`/`grid_hw`)
      still exist for direct constructions — the app path never reads them now.
- [x] **6.2** `sec_loop._params_for` no longer invents `graph.edge_index`
      (a literal two-node chain) or `spatial_lattice.lattice_dims=(8,8)`; the
      lattice extent derives from the task's `input_shape` and the builders
      refuse the rest by name. Lock:
      `tests/property/test_geometry_shape_source_lock.py`.
- [ ] **6.3** Prove with grep + capability gate on a non-MNIST task
      (`digits`/`iris`), and delete the remaining `sec_pilot.py` literals.

### Phase 7 — Budget policy (B2)
- [x] **7.1** Wave sizing already prices each wave from *that* fidelity's
      measured cells (`wave.py`: measured → positive control → default), which is
      the per-cell cost the plan asked for. The offline
      `configs/cost_model.pkl` had no reader and is deleted; the meta proxy now
      reads the same measured walltimes (`avg_walltime_s=15.1`).
- [ ] **7.2** Validate on one held-out wave: predicted vs measured walltime.

### Phase 8 — Proposals & metrics (B1, B3, B4)
- [ ] **8.1** Emit ≥3 primitive proposals. The gap table is locked to the
      census (`test_inventory_single_source`), so a proposal needs a spec row +
      config classmethod + the wiring lockstep lock — not a bare gap row.
      Candidates from tonight's evidence, each with its trigger:
      1. `primitive.geometry.graph_carrier` — reads the task's own connectivity;
         trigger: a task declares `edge_index` in its shape (B5 refusal today).
      2. `primitive.geometry.lattice_carrier` — derives the lattice extent from
         a 3-D task shape; trigger: a spatial task declares a 3-D extent (A10).
      3. `primitive.substrate.gpu_neuromorphic` — neuromorphic settle on the
         GPU (every cell's box declares `substrate.device=cpu`, so the cell is
         CPU-bound: `spiking_mnist` L0 measured 51–81 s/cell).
- [ ] **8.2** Regenerate the TODO103 consolidated checklist to match reality.
- [ ] **8.3** Record the serial competitive table and the claim in
      `docs/readme/stability-eval.md` (implemented row + box).

---

## 📈 Section D — Success metrics

| Metric | TODO103 actual | TODO104 target | Measurement |
|---|---|---|---|
| Valid claims | 1 | 18+ | `results/sec/serial` rung2 verdicts |
| Viable primitives (serial) | 23/75 | 45+ | serial summary |
| Rung timeouts | 0 (serial) / 133 (concurrent) | 0 | rung `status` counts |
| Neuromorphic L0 no crash | ❌ | ✅ **met** (two widths, one process) | A2 lock + probe |
| Update primitives running | 8/18 | 18/18 or named reason | axis log |
| Meta-SEC objective | 0.0 (invalid) | >0, `claim_seeds≥5` | `meta_sec_best.json` → **3.589, valid, seeds=7** |
| Primitive proposals | 0 | 3+ | `registry.py` `"proposed"` |
| Hardcoded MNIST defaults | 5+ | 0 | factory/builder path: **0**; dataclass field defaults remain (never read by the app path) |
| Lost result on crash | 2 axes | 0 | per-primitive parts under `<axis>/parts/` |
| Refusal rate | — | <5% of non-skipped | `cells.jsonl` status |

---

## 📋 Section E — Consolidated checklist

```markdown
### Phase 1 — Infrastructure (done 2026-11-25)
- [x] 1.1 settle compile dynamic=True (+ lock + GPU probe PASS)
- [x] 1.2 cooperative deadline; no thread-kill timeouts
- [x] 1.3 per-primitive durable write + try/finally per axis
- [x] 1.4 serial-only competitive path; block semaphore>1 on one GPU

### Phase 2 — Box/legality
- [x] 2.1 intersect box keys with accepted params
- [ ] 2.2 adafactor/natural_gradient: profile, then fix or mark unavailable
- [x] 2.3 claim runs at the registered box (+ lock)

### Phase 3 — Meta-SEC (done 2026-11-25)
- [x] 3.1 claim-seed space derives from the floor
- [x] 3.2 calibrate objective; assert best_value>0
- [x] 3.3 regenerate meta_sec_best.json (3.589, valid)

### Phase 4 — Coverage (run in flight)
- [ ] 4.1 re-run skipped primitives (serial)
- [ ] 4.2 breadth: ≥1 above-chance cell per error-aware credit / family
- [ ] 4.3 record flipped refusals as A1 artifacts

### Phase 5 — Competitive evidence
- [ ] 5.1 best declared box per primitive (ladder + confirm seed)
- [ ] 5.2 pre-registered paired comparisons to n_max≥5
- [ ] 5.3 push claims to 18+ (marginal ≠ met)

### Phase 6 — Hardcoded removal
- [x] 6.1 geometry factories read no guessed extent (+ lock)
- [x] 6.2 sec_loop invents no edge_index/lattice_dims (+ lock)
- [ ] 6.3 grep + non-MNIST capability gate (sec_pilot literals remain)

### Phase 7 — Budget
- [x] 7.1 wave sizing prices the fidelity's measured cells (offline pkl deleted)
- [ ] 7.2 validate on held-out wave

### Phase 8 — Proposals & docs
- [ ] 8.1 ≥3 primitive proposals from gaps
- [ ] 8.2 regenerate TODO103 checklist
- [ ] 8.3 record serial table + claim in stability-eval.md
```

---

## 🗒 Section G — Progress log

### Session 2026-11-25
**Decision:** close the infrastructure and meta-SEC defects that made the
2026-11-24 map untrustworthy (A1, A2, A3, A4, A6, A7, A9, A10/B5), then re-run
the coverage the defects hid. Error cost of a wrong call: a rerun priced in hours
and a map that cannot carry claims.
**Experiment (fix evidence):** lock suites
(`test_settle_dynamic_compile_lock.py`, `test_sec_run_infrastructure_lock.py`,
`test_geometry_shape_source_lock.py`) and
`scripts/probes/todo104_a2_settle_recompile.py`.
**Box / rung / stop:** A2 proved at rung 0 (one process, two widths, both
measured) — a wired mechanism needs no ladder. Meta-SEC regenerated on
`results/sec/cells.jsonl` (60 trials, pure proxy).
**Result:** A2 two widths measured (0.7648 @ 51.5s; 0.7555 @ 74.9s), no
recompile-limit error; meta objective 0.0 → 3.589, `valid=true`,
`claim_seeds=7`, `avg_walltime_s=15.1` (was 0.0).
**Triage:** A1/A2/A3/A4/A6/A7/A9/A10 are *fixed defects* with locks; A5 remains
a cost question, A8 a box-identity question. A4's refused set is confirmed as an
A1 artifact (five of five flipped viable serially).
**Fixes applied:** `_settle_kernel.py`, `dynamics/_dynamics.py`,
`geometry.py`, `_geometry_builders.py`, `sec_loop.py`, `sec_all_axes.py`,
`meta_sec.py`, new `sec_parts.py`, `scripts/run_full_sec_competitive.py`,
three lock tests + one probe, `configs/meta_sec_best.json`.
**Next experiment:** the final coverage re-run (`SEC_RUNG2=none`,
`results/sec/serial3/<axis>`, `logs/serial3_*`) with every fix in it, then a
pre-registered rung 2 on the arms whose coverage cells clear their bar. Read
each axis' parts under `results/sec/serial2/<axis>/parts/` even if a process
dies. Then: A5 cost profile (2.2), non-MNIST gate (6.3), docs (8.3).

**Fourth finding (A15):** `geometry/conv` could not run at the reproducibility
box — `adaptive_avg_pool2d` has no deterministic CUDA backward. `_pool_to`
switches to `avg_pool2d` on a divisible extent (same pooling, deterministic
backward, verified on the GPU).

**Third finding (A12):** the ladder swept a field its rule ignores (four
identical rungs). `reads(...)` already declared the fields each rule uses but
nothing read it; `_declared_reads` now steers the knob, and a rule that
declares none is measured once at its default. 15 rules still lack a `reads`
declaration (queued work).

**Second finding (A11):** the first re-run logged `d=0.00` on every rung 2 —
`run_cell` recorded the seed but measured the base schedule, so both arms were
one cell twice. `pair_schedule` now sets one seed per cell. Every 2026-11-24
rung-2 verdict is an A11 artifact: 21 coordinates and 1 claim carry no power
statement. Coverage (rung 1) was unaffected, so the map re-ran as coverage first
(`SEC_RUNG2=none`), and claims follow at the registered box only.

## 📎 Section F — Evidence & commands

- Serial results: `results/sec/serial/{axis}/{axis}_results.json` (gitignored),
  combined: `results/sec/serial/full_competitive_results.json`.
- Concurrent baseline (A1 evidence): `results/sec/full_competitive/`.
- Drivers: `scripts/run_full_sec_competitive.py` (env: `SEC_AXES`,
  `SEC_SEMAPHORE`, `SEC_RUNG_TIMEOUT`, `SEC_RESULTS_DIR`),
  `scripts/run_sec_axes_serial.sh`.
- Reproduce serial run:
  ```
  bash scripts/run_sec_axes_serial.sh credit dynamics geometry update plasticity substrate
  ```
- Count rung statuses in a results file:
  ```
  uv run python -c "import json,sys,collections; d=json.load(open(sys.argv[1])); \
  c=collections.Counter(x['status'] for r in d['results'] for x in (r.get('rung1_ladder') or [])); print(c)" \
  results/sec/serial/update/update_results.json
  ```

---

## ⛔ Never

- Call a concurrent-run timeout an algorithm verdict (A1).
- Emit a meta-SEC "best" with `best_value==0` or `claim_seeds<5` (A6, A7).
- Decide a claim at a box the ladder never measured (A8).
- Let a process death discard an axis of evidence (A9).
- Keep a hardcoded MNIST default behind a `[x]` checkbox (A10).
