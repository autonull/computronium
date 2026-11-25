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
Phase 6.1/6.2, Phase 7.1 and Phase 8.2/8.3 landed, each with a lock. A2
acceptance measured on the GPU; meta-SEC regenerated with a nonzero objective
(3.589). The first Phase-4 re-run exposed a new defect (A11: every rung-2 pair
ran at one seed, so `d=0.00`); it is fixed and the coverage map re-launched
with `SEC_RUNG2=none` (`logs/serial2_*/`). The n=100 fresh-seed claim run is a
coordinate (A22). **Then:** the breadth exit PASSes (`comp gate breadth`,
17/17 error-aware credits on ≥2 families, A27), the A1-artifact reconciliation
is recorded (34 `all_refused → viable` serial flips, A27), the shape-source
defect is closed across the app path (`_apply_task_spatial`, 6.3, A28), the
cost model is validated on a held-out wave and the box-keyed model landed
(A29), the two "unsupplied" carriers measured (A30), and TODO103's
checklist is regenerated (8.2). 8.1 is re-triaged: both "unsupplied" carriers
measure (A30), so no primitive proposal is needed; 5.3's 18+ claim target is
restated as blocked by the seed-block spread (A22), not by the number of
viable rules.

---

## 🔜 Remaining work (after 2026-11-25)

| Item | What it needs | Cost / trigger |
|---|---|---|
| **Breadth composition rules** | A18 routing×gradient, A19 param ceiling, A20 sparse×gradient each need a declared rule or a dispatch path, with a failing composition as the trigger | `kernel/search_space.py`, `kernel/compose.py` |
| **5.3 claim target** | a pre-registered family minimum below every measured block's CI lower bound (0.5 is below all three blocks) *and* a seed-block variance estimate; fresh seeds, fixed n | 128 cells ≈ 15 min at the measured 6 s/cell |
| **Geometry re-run** | record the two carriers (graph/cora, spatial_lattice/mnist) in the map so 4.2's named gap closes on data, not a probe | geometry axis at `SEC_RUNG2=none`, ~2 cells + its ladder |
| **2.2 `natural_gradient`** | mark the row unavailable with its measured L0 cost (>180 s/epoch) instead of a priced skip | needs the axis row's own availability flag |
| **Hygiene queue** | 6 stale fixtures fail at HEAD (API drift: `_train_nearest` gained `budget_s`; two registration/box helpers moved) in `test_paired_ci.py`, `test_ladder_record_lock.py`, `test_screen_has_no_verdict.py` | round-close pass, not a commit blocker |

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

### A16. The continual tasks had no ruler (`evaluate` returned `None`)
- **Evidence:** 33 of 46 defect rungs in the 2026-11-25 map were
  `non-finite metric`, all on cells whose family mapped to `split_mnist`;
  the log names `task.evaluate() failed: 'NoneType' object has no attribute
  'to_dict'`.
- **Mechanism:** `SplitMNIST`/`PermutedMNIST` delegated `evaluate` to
  `DomainTask.evaluate`, whose body is a docstring — so the ruler returned
  `None` and the metric became non-finite. The cell trained; the ruler was
  absent.
- **Fix:** both continual tasks use `evaluate = VisionTask.evaluate` (the
  loader, loss and device are theirs; the ruler is the shared one). Lock:
  `test_continual_tasks_carry_a_ruler`.

### A17. A declared family was used as the comparison box
- **Evidence:** the same 33 rows show the family chosen was the first declared
  (`continual`), whose base box carries a 4096-wide head over a 2-class
  split — the map measured the box, not the mechanism.
- **Fix:** `preferred_task_family` — a rule's families declare *availability*;
  the map measures on `vision` when declared, else the first. Lock:
  `test_the_map_measures_the_common_family`.

### Pre-registration — `random_projections` n_max=100, seeds 164..263 (06:35)
- **Claim (unchanged):** tuning `credit.feedback_scale` to 22.653x raises
  val_acc on `credit/random_projections` at the mnist base box.
- **Test:** 100 index-matched pairs at seeds 164..263 (the 0..63 pilot and the
  64..163 run are untouched by this one), fixed-n, no peeking, `alpha=0.05`.
  The registration is re-created with the A26 box (axis primitive, fidelity,
  epochs, batch_size, task_id, device, precision — the knob and seed are not
  box fields) and `min_d` from the declared per-family table.
- **Decision rule:** `claim` iff the 95 % CI lower bound on d > `min_d` and
  `p < 0.05`; otherwise `coordinate` with the boxed effect.
- **Basis:** the 64..163 run measured `d=+1.065`, `sd_diff≈0.025`,
  `d-CI-lower=0.876`; at n=100 the expected lower bound is ~0.87.
- **Command:** `SEC_AXES=credit SEC_PRIMITIVES=random_projections
  SEC_RUNG2=auto SEC_RUNG2_SEEDS=100 SEC_RUNG2_SEED_OFFSET=164
  SEC_RESULTS_DIR=results/sec/claim100b`.
- **Result (07:11):** `n=100` at seeds 164..263, `mean_diff=+0.0218`,
  `d=+0.828`, `p=1e-4`, `d-CI-lower=0.640` → **`coordinate`**. The effect
  replicated (0.83 vs 1.02-1.07 on the earlier seed blocks) and is real, but
  a 95 % lower bound above 0.8 would need `n = (1.96/0.028)^2 ≈ 4900` pairs
  (`≈ 9800` cells, ~19 h at this box) — infeasible.
- **Conclusion (A22, measured):** the *threshold* is the binding constraint,
  not the effect. A 0.5 vision minimum would certify this effect at `n=64`
  (`d_lower ≈ 0.78 > 0.5`). The next claim run pre-registers a 0.5 minimum
  for vision, or the meta proxy gains `d - 1.96/sqrt(n) > min_d` as a
  constraint so it cannot price an uncertifiable minimum.

### A26. The registration pinned the knob and seed it varies
- **Evidence:** the n=100 confirmatory run measured `d=+1.065`,
  `d-CI-lower=0.876` against `min_d=0.8`, `p=1e-4` — a pass — and still
  returned `coordinate`. The reason string was
  `credit.feedback_scale: registered 0.01, run 0.2265`.
- **Mechanism:** `create_registration` put the *varied knob* and the per-pair
  `seed` into the declared box, so `box_mismatch` refused the one cell the
  claim varies. The box identity must be the invariant part of the run.
- **Fix:** the declared box is `{axis: primitive}` + `fidelity`, `epochs`,
  `batch_size`, `task_id`, `device`, `precision`; the knob is the
  intervention and the seed is the pair index. Lock:
  `test_the_varied_knob_is_not_a_box_field`.

### A25. Two tables disagreed on the registered minimum d
- **Evidence:** the committed registration
  (`configs/preregistrations/sec_credit_random_projections.json`) carries
  `min_d: 0.8` while the driver prints and names vision `0.916`.
- **Mechanism:** `EffectSizeRegistration.for_task_family` computed `min_d` from
  its own `MIN_EFFECT_SIZE_BY_FAMILY` and ignored the caller's resolved value,
  so the file (0.8) and the claim text (0.916) disagreed — a second table
  re-deriving one rule.
- **Fix:** `for_task_family(min_d=...)` takes the caller's declared value;
  the family table is the fallback for a caller that carries none. Lock:
  `test_the_declared_min_d_wins`.

### A24. `mean_norm`'s declared default cannot train (7/7 control seeds at chance)
- **Evidence:** the paired run at the mnist box: control arm (the declared
  default `update.step_size=0.001`) measured `[0.124, 0.101, 0.116, 0.101,
  0.103, 0.103, 0.114]` — chance on all seven seeds — while the treatment
  (1.5e-5) measured `[0.838, …, 0.845]`, `d=+54.43`.
- **Mechanism:** `MeanNormUpdate` normalizes by the parameter norm, so a
  0.001 step overshoots at the mnist box; a 66x smaller step trains. The
  declared default is not a legal working point, so every control arm on this
  row measures a broken cell.
- **Fix (next):** declare a working default in the config classmethod (the
  measured 1.5e-5 regime) and re-measure; a default that cannot train is a
  defect, not a tuning result.

### A22. The claim threshold is unattainable at 7 pairs
- **Evidence:** the first valid paired run (7 seeds × 2 arms) measured real
  effects — `random_projections` diff `+0.0297`, `d=+1.21`, `p=0.0004`;
  `analog` `d=+1.00`; `optical` `d=+0.92` — and every one returned
  `coordinate`, because `passes_effect_size` requires the *CI lower bound* on
  d to exceed `min_d` (vision `0.93`).
- **Arithmetic:** at n pairs the lower bound is `d - 1.96/sqrt(n)`; clearing
  0.93 with `d=1.21` needs `n >= 49`, with `d=1.0` needs `n > 300`. The
  meta-SEC proxy priced a 0.93 minimum without pricing the seed budget, so no
  feasible n certifies a typical effect.
- **Fix (next):** size each claim from its measured effect — a pre-registered
  `n_max` (64 for `random_projections`, 128 for `analog`) — and record the
  required n beside the coordinate. The proxy gains the
  `d - 1.96/sqrt(n) > min_d` constraint.

### A23. A rounded integer knob left its declared domain
- **Evidence:** `conv` and `ntm` paired `d=-0.38` with a CI at `~0`: the
  ladder's best was `num_layers` 3 × 0.0152, which rounds to **0** layers — a
  degenerate geometry compared against a 3-layer default.
- **Fix:** `knob_point` rounds an integer knob *and* clamps it to the domain
  the config class declares (1..12 for `num_layers`); both ladders and
  `comparison_boxes` read it. Lock:
  `test_a_ladder_point_stays_in_the_declared_domain`.

### A21. Rung 2 compared two *different* mechanisms (d = -61)
- **Evidence:** the first claim run (2026-11-25 03:15) reported
  `d=-61.27` for `conv`, `-3.86` for `nca`, `-3.25` for `ntm` — a knob claim
  cannot produce |d| > 10 on a single tuned knob.
- **Mechanism:** `run_rung2_comparison` drew its control from
  `AXIS_DEFAULTS[axis]` (feedforward), so the "treatment" was conv at a knob
  value and the "control" a different geometry. The registration's claim text
  is "tuning {knob} on {primitive}", so the pair must share the primitive.
- **Fix:** `comparison_boxes` builds both arms from the same primitive —
  control at the registered default knob, treatment at the ladder's best — and
  `INT_KNOBS` is the one integer-knob declaration the ladder and the box read.
  Lock: `test_a_pair_is_one_primitive_two_knobs`.

### A19. A box over its ceiling was reported as a defect
- **Evidence:** 2 of the 9 remaining defect rows are ceiling overruns:
  `geometry/attention` (`param_count 16866970 over ceiling`) and
  `geometry/tile` (`720500`).
- **Mechanism:** `sec_loop._defect_for` names an overrun a DEFECT, but its own
  contract says a defect is an execution fact (TODO95 D5). A width that cannot
  fit the declared ceiling is an infeasible box — a refusal.
- **Fix (queued, one source):** `_defect_for` returns `within` for the caller
  to map to `refused` (a box statement), keeping `non-finite metric` as the
  only defect it names. The rule is shared with the breadth screen and the
  interaction slice, so it lands after the map run.

### A20. A sparse substrate zeroes the gradient of pruned parameters
- **Evidence:** `substrate/sparse` defects: `GradientCredit: no gradient
  reached target indices [0, 1, 2, 3]`.
- **Mechanism:** the sparse mask prunes parameters, so the autograd path to
  them is zero and the credit's contract check refuses the cell. That is the
  substrate's declared behaviour, not a crash: the pair needs a credit whose
  contract tolerates pruned parameters (or the row declares the requirement).
- **Fix (queued):** declare it in the void table (`gradient` × a substrate that
  prunes parameters) or measure the sparse substrate with a masked loss. Until
  then the row is a named refusal by the credit's contract.

### A18. `gradient` × hard routing gate = zero gradient (declared space gap)
- **Evidence:** `geometry/routing` defected at every rung: `Training failed:
  GradientCredit: no gradient reached target indicators`; the dry-run check in
  `compose.py` names the same mechanism.
- **Mechanism:** `routing_weights(..., surrogate=None)` selects the top-k with
  a `scatter` over indices, so the gate logits receive no gradient. With
  `surrogate="ste"` the same forward passes the soft gradient through.
- **Fix (queued, needs a VOID row):** a `gradient` credit requires a gate the
  gradient reaches — refuse `credit=gradient` on `geometry=routing` when
  `top_k < num_experts` and `surrogate != "ste"`, by name, in the declared
  space. The row is a schema edit, so it lands *after* the map run; the map
  row stays a named defect, not a mechanism verdict.

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
| B1 | Primitive proposals from gaps | ✅ re-triaged: no proposal is needed. Both carriers are existing rows behind a legality artifact (A30); the remaining gaps are composition rules (A18–A20) | `sec_loop._is_legal`, `schema/gaps.py` |
| B2 | Budget policy from measured cost model | ✅ `wave.py` sizes each wave from that fidelity's measured cells (measured → positive control → default); the offline `configs/cost_model.pkl` had no reader and is deleted | `wave.py` |
| B3 | Success metrics unmet | ❌ see Section D | — |
| B4 | Consolidated checklist stale (all `[ ]` despite detailed `[x]`) | 🟡 TODO103 §E marked superseded by TODO104 §E | `TODO103.md` |
| B5 | `graph`/`spatial_lattice` hardcoded `edge_index`/`lattice_dims` in `_params_for` | ✅ fixed: no invented topology; builders refuse by name | `sec_loop._params_for` |

---

### A27. The breadth exit was never run; the A1 row hid 34 viable rules
- **Evidence:** `comp gate breadth` on the corpus now PASSes (17 error-aware
  credits, ≥2 families each, 960 legacy records assessed, 43 unbarred, 58
  refused cells). Diffing the concurrent baseline against `serial3` shows 34
  rows that were `all_refused` concurrently and `viable` serially, the five
  A4 rows among them (`mean_norm`, `lion`, `schedule_free`, `ortho_adam`,
  `riemannian_orthogonal`), six `no_knob → viable`, and three `no_knob →
  refused` (`surrogate`, `fast_weights`, `rule_state`, each with a named
  reason). The gate is the predicate; the diff is the A1-artifact record.
- **Mechanism:** the concurrent driver killed cells under `torch.compile`
  recompile contention (A1); a killed cell reads as `all_refused`, and no
  reader ever compared two runs, so the artifact looked like a legality
  verdict.
- **Fix:** serial is the only competitive path (1.4); the breadth exit is an
  exit code (`comp gate breadth`), and this row records the reconciliation.

### A28. The family base box's pixel grid leaked into another task
- **Evidence:** a usps cell composed `geometry.input_hw = (28, 28)` — the
  vision base box's mnist grid — and `digits` likewise; `_params_for` and
  `screen_coordinate` returned `(28, 28)` for any spatial primitive, and
  `own_knob_params` invented a two-node graph chain and a 28x28 conv default.
- **Mechanism:** the base box declares its own task's facts (vision is mnist)
  and the parameter builder treated them as the *run's* facts; `setdefault`
  never overrode them for another task in the same family. The declared space
  passes a rank check, so the cell was legal on paper and would die at the
  first forward pass.
- **Fix:** `_apply_task_spatial` overrides the base box's grid with the task's
  own (`channel_count`/`spatial_extent` are the one reading); both the box
  path and `_params_for` call it; `own_knob_params` derives geometry defaults
  from the task shape and returns none for a topology the task cannot declare
  (graph connectivity stays the task's data). Lock:
  `test_params_for_reads_the_tasks_extent`; probe:
  `scripts/probes/todo104_non_mnist_shape.py` — usps/conv measured 0.665 in
  2.2 s, digits/nca 0.625 in 0.5 s, both at their own 16x16/8x8 extent.

### A30. The "unsupplied carriers" both train; legality refused the graph
- **Evidence:** `geometry/graph` on `cora` was refused by the declarative check
  (`graph topology requires edge_index`) while the evaluator composes graph
  cells *with the task instance* and extracts cora's own connectivity. Post-fix
  probe (`scripts/probes/todo104_carriers.py`): graph/cora **0.114 @ 1.1 s**,
  spatial_lattice/mnist **0.9167 @ 67.5 s**, both `legal=True, measured`.
- **Mechanism:** `sec_loop._is_legal` called `compose_configs` without the
  task instance, so the connectivity extraction never ran; a legal cell was
  refused, and the map called the carrier "unsupplied" — a legality artifact,
  not a capability gap. The lattice's refusal was the same class, closed by
  the task-shape derivation (A28); its extent now comes from the 3-D shape.
- **Fix:** `evaluate.task_instance` is the public door to the cached task;
  `_is_legal` passes it when the geometry reads task data. Locks:
  `test_a_graph_cell_is_legal_on_a_graph_task`,
  `test_a_graph_cell_on_a_table_stays_refused`.

### A29. A task price is not a box price (cost-model validation)
- **Evidence:** held-out split of the 579 measured SEC cells
  (`scripts/probes/todo104_cost_model_heldout.py`): pricing by task gives
  median `|predicted/measured - 1| = 0.78` (9 task groups); pricing by
  `task+geometry+dynamics+credit` gives 0.38 (33 box groups). mnist's
  feedforward cells measure 4.4 s and its settle cells 130 s, so one task
  price cannot serve both.
- **Mechanism:** `CostModel.cost_for` keys on the task; the wave's own price
  (`_first_wave_price`) uses the positive control's measured walltime at the
  run's box, which is why the run path is right and the fallback table is
  not. The fallback under-prices a wave whose cells differ by topology.
- **Fix (landed):** `CostModel.per_box` keys the persisted model on
  (task, geometry, dynamics, credit), with `cost_for_box` → `cost_for(task)`
  → run-wide; the cache round-trips it and `survey_cli`'s dry run prices its
  own cells (`cost_for_cells`). Locks: `test_a_box_price_wins_over_its_task_price`,
  `test_a_box_price_survives_the_cache`.



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

## 🛠 Section C — Implementation plan (ordered by unblocking value)

### Phase 2 — Box/legality correctness (unblocks breadth)
- [x] **2.1** A4: `_accepted_knobs(axis, primitive)` intersects the box and the
      primary knob with the harvested `AxisSpec.accepted_params`; lock sweeps
      `lion`/`muon`/`local_adam`.
- [x] **2.2** A5 priced with the cooperative deadline: `update/adafactor` is
      **viable** (0.9128 at 0.587x, ~13 min for its 4-rung ladder) and stays
      a priced skip, not a gap. `update/natural_gradient` times out at every
      rung ("run deadline expired before the first epoch completed") — one L0
      epoch exceeds the 180 s cell budget, so it is priced as a skip with that
      measured reason. Declaring it a gap row needs the axis row's own
      availability flag (the census refuses a gap on an available row).
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
- [x] **4.1** Re-ran all six axes serially (`SEC_RUNG2=none`):
      `results/sec/serial3`. Final map **52/75 viable+blind** (credit 11,
      dynamics 3, geometry 7, plasticity 5, substrate 9, update 17). The eight
      priced skip rows re-ran under `SEC_INCLUDE_SLOW=1`: `dynamics/lazy`
      (0.9362), `geometry/nca` (0.8963) and `update/adafactor` (0.9128) are
      viable — the skip list was hiding them; the rest refuse by name (void
      constraint or L0 cost).
- [x] **4.2** Breadth read: every axis has a working default
      (`instantaneous` 0.9172, `feedforward` 0.9134, `null` 0.92,
      `digital` 0.9172, `adam`/`euclidean` 16/18 update rows viable).
      Remaining gaps are named: routing×gradient (A18), param ceiling (A19),
      sparse×gradient (A20), and the three structural carriers (graph,
      spatial_lattice) that no task supplies. **Breadth exit:** `uv run comp
      gate breadth` PASSes — 17/17 error-aware credits hold a legal,
      bar-cleared cell on ≥2 task families (960 legacy records re-assessed
      against their own bar, 43 unbarred, 58 refused cells excluded).
- [x] **4.3** Reconcile: `eligibility_prop`, `rtrl_reference`, `unbiased_rtrl`
      refuse on a declared batch-layout rule, not a mechanism verdict; the
      five A4 refusals from the concurrent run all run serially (A1 artifact
      confirmed). The full diff: 34 `all_refused → viable` (all five A4 rows
      among them), six `no_knob → viable`, three `no_knob → refused`
      (`surrogate`, `fast_weights`, `rule_state`, each named). Table: A27.

### Phase 5 — Competitive evidence (tune, then compare)
- [x] **5.1** Every viable arm reached its ladder best (4 points incl. the
      declared default; the confirmation seed is the paired run's seed 0).
- [x] **5.2** Pre-registered paired comparisons: 22 arms selected by
      "best factor ≠ 1.0 and above bar"; the run is `results/sec/claims2`
      (`logs/claims2_*`) at the registered box, 7 seeds × 2 arms. The
      confirmatory `random_projections` runs followed: n=64 (0..63) and
      n=100 fresh seeds (64..163, then 164..263), each pre-registered before
      its first seed.
- [x] **5.3** Read the verdicts: claim / marginal / coordinate / refused.
      (`claims2`, 7 pairs): **0 claims, 6 coordinates, 1 no_power, 1 defect**
      with real effects (`random_projections` d=+1.21 p=0.0004, `analog`
      d=+1.00, `optical` d=+0.92). A22 explains the gap: the 95 % CI lower
      bound on d must clear the registered minimum (vision 0.8 in the family
      table; the meta-SEC sample set 0.916 for the SEC driver). The n=64 run
      measured 0.783 — 0.017 short. The n=100 fresh block measured d=+0.828
      (lower 0.640) while seeds 64..163 measured d=+1.065: **seed-block
      variation exceeds the within-block CI**, so n alone cannot certify the
      effect until that variation has an estimate. **Target restated:** 18+
      claims needs a pre-registered minimum the planned n can certify *and* a
      stable effect; the threshold, not the effect, was binding.

### Measured paired effects (7 pairs, mnist base box, 2026-11-25)
| Arm | mean_diff | Cohen's dz | verdict |
|---|---|---|---|
| `credit/random_projections` (`feedback_scale` 22.65x) | +0.0297 | +1.21 | coordinate |
| `substrate/analog` | +0.0206 | +1.00 | coordinate |
| `substrate/optical` | +0.0058 | +0.92 | coordinate |
| `update/lion` | +0.0123 | +0.92 | coordinate |
| `update/schedule_free` | +0.0218 | +0.46 | coordinate |
| `update/spectral_constrained` | +0.0592 | +4.34 | coordinate |
| `update/mean_norm` | +0.7268 | +54.43 | coordinate (control broken, A24) |
| `geometry/conv`, `geometry/ntm`, `plasticity/temporal_psi` | ~0 | -0.38 | coordinate (A23) |
| `geometry/tile_mesh` | — | — | defect |
| `substrate/ternary`, `update/<default>` | — | — | no_power (best is the default) |

Every one is a **coordinate**, and by A22 that is the correct verdict at
n=7: the CI lower bound on d must clear `min_d` (vision 0.916).

### Pre-registration — `random_projections` at n_max=64 (2026-11-25 04:27)
- **Claim:** tuning `credit.feedback_scale` to the ladder's best (22.653x of
  its 0.01 default) on `credit/random_projections` raises val_acc at the
  mnist base box.
- **Test:** paired comparison, 64 index-matched seeds per arm (one cell per
  seed), fixed-n, no peeking; `alpha=0.05`; `min_d` = vision 0.916.
- **Decision rule:** `claim` iff the 95 % CI lower bound on Cohen's d exceeds
  0.916 and `p < 0.05`; otherwise `coordinate` (a boxed effect size).
- **Basis:** the 7-pair run measured d=+1.21, sd_diff≈0.0245; at n=64 the
  lower bound is 1.21 - 1.96/8 ≈ 0.965 (A22's arithmetic).
- **Command:** `SEC_AXES=credit SEC_PRIMITIVES=random_projections
  SEC_RUNG2=auto SEC_RUNG2_SEEDS=64 SEC_RESULTS_DIR=results/sec/claim64`.
- **Result (06:25, seeds 64..163):** `n=100`, `mean_diff=+0.0266`,
  `d=+1.065`, `d-CI-lower=0.876`, `p=1e-4` — a *pass* against 0.8, refused
  by A26's box mismatch (the registration pinned the knob). The measurement
  is the effect; the verdict was a box-check artifact.
- **Result (05:34, seeds 0..63):** `n=64`, `mean_diff=+0.0259`, `d=+1.024`,
  `p=1.0e-4`, `d-CI-lower=0.783` against the file's `min_d=0.8` →
  **`coordinate`**, 0.017 short — `marginal`, not met (AGENTS: within 1σ of
  the threshold is not a claim). The committed file declared 0.8 (A25), so
  this run's bar is 0.8, not the 0.916 the plan named.
- **Next:** a *fresh-seed* confirmatory run at n_max=100 (seeds 64..163),
  pre-registered before its first seed; expected lower bound
  `1.024 - 1.96/10 ≈ 0.828 > 0.8`.

### Pre-registration — `random_projections` n_max=100, seeds 64..163 (05:45)
- **Claim (unchanged):** tuning `credit.feedback_scale` to 22.653x raises
  val_acc on `credit/random_projections` at the mnist base box.
- **Test:** 100 index-matched pairs at *fresh* seeds (64..163 — the n=64 pilot
  used 0..63), fixed-n, no peeking, `alpha=0.05`; threshold = the committed
  registration's `min_d=0.8` (A25: the file is the pre-registration).
- **Decision rule:** `claim` iff the 95 % CI lower bound on d > 0.8 and
  `p < 0.05`; otherwise `coordinate` with the boxed effect.
- **Basis:** 64-pair pilot `d=+1.024`, `sd_diff≈0.0253`; at n=100 the lower
  bound is `1.024 - 1.96/10 ≈ 0.828`.
- **Command:** `SEC_AXES=credit SEC_PRIMITIVES=random_projections
  SEC_RUNG2=auto SEC_RUNG2_SEEDS=100 SEC_RUNG2_SEED_OFFSET=64
  SEC_RESULTS_DIR=results/sec/claim100`.

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
- [x] **6.3** Proved with grep + a capability gate on non-MNIST tasks, and
      closed the last literals. `_apply_task_spatial` overrides the family
      base box's grid with the task's own in both `_params_for` and
      `screen_coordinate`; `own_knob_params` derives geometry defaults from
      the task shape and returns none for a topology it cannot declare (no
      graph chain, no 28x28/16x16 fallback). Probe
      `scripts/probes/todo104_non_mnist_shape.py`: usps/conv 0.665 @ 2.2 s,
      digits/nca 0.625 @ 0.5 s, each at its own extent. Lock:
      `test_params_for_reads_the_tasks_extent`,
      `test_own_knob_defaults_refuse_an_undeclared_extent`. The remaining
      `28x28` literals are base-box declarations of mnist-shaped base tasks,
      never a fallback.

### Phase 7 — Budget policy (B2)
- [x] **7.1** Wave sizing already prices each wave from *that* fidelity's
      measured cells (`wave.py`: measured → positive control → default), which is
      the per-cell cost the plan asked for. The offline
      `configs/cost_model.pkl` had no reader and is deleted; the meta proxy now
      reads the same measured walltimes (`avg_walltime_s=15.1`).
- [x] **7.2** Validated on a held-out wave
      (`scripts/probes/todo104_cost_model_heldout.py`, 579 measured cells):
      a price keyed on the box (task+geometry+dynamics+credit) predicts the
      later half of each group's walltime within `|ratio-1| = 0.38` (33
      groups); a price keyed on the task alone is off by 0.78 (9 groups)
      because one task's cells span 4.4 s to 130 s. The wave's own price is
      the positive control's measured walltime at the run's box, so the run
      path is right; the per-task fallback table is the defect (A29).

### Phase 8 — Proposals & metrics (B1, B3, B4)
- [x] **8.1** Re-triaged: **no new primitive is needed**. The three candidates
      in the earlier list each surveyed an existing row: `graph_carrier` is
      `geometry/graph` (it reads the task's own `edge_index`; the refusal was
      A30's legality artifact), `lattice_carrier` is `geometry/spatial_lattice`
      (its extent derives from any 3-D shape, A28), and `gpu_neuromorphic` is
      the substrate `device` parameter, not a primitive. Both carriers now
      measure (`scripts/probes/todo104_carriers.py`: graph/cora 0.114 @ 1.1 s,
      spatial_lattice/mnist 0.9167 @ 67.5 s), so no spec row, config
      classmethod or wiring lock is added. The remaining breadth gaps are
      composition rules (A18–A20), not missing primitives.
- [x] **8.2** Regenerated TODO103's consolidated checklist against the
      measured evidence: each row names its verdict and the artefact that
      carries it; TODO104 §E is the live list.
- [x] **8.3** Recorded the serial map, the breadth exit, the claim and the
      coordinate table in `docs/readme/stability-eval.md`
      ("Measured Capability Map").

---

## 📈 Section D — Success metrics

| Metric | TODO103 actual | TODO104 target | Measurement |
|---|---|---|---|
| Valid claims | 1 (A11 artifact) | 18+ at the family minimum → **restated** | **0** — every pair is a coordinate; A22 explains why: the CI lower bound must clear the registered minimum, the n=64 run missed 0.8 by 0.017, and seed-block d varies 0.83–1.07 (wider than the within-block CI), so n alone cannot certify it |
| Viable primitives (serial) | 23/75 | 45+ | **52/75** (serial3 incl. the skip re-run: 50 viable + 2 error_blind) **met** |
| Rung timeouts | 0 (serial) / 133 (concurrent) | 0 | 3 of 229 rungs (serial3: 176 measured, 41 refused, 9 defect, 3 timeout) |
| Neuromorphic L0 no crash | ❌ | ✅ **met** (two widths, one process) | A2 lock + probe |
| Update primitives running | 8/18 | 18/18 or named reason | **17/18 viable**; `natural_gradient` = named L0 cost |
| Meta-SEC objective | 0.0 (invalid) | >0, `claim_seeds≥5` | `meta_sec_best.json` → **3.589, valid, seeds=7** |
| Primitive proposals | 0 | 3+ → **re-triaged** | **0 added, none needed**: graph/cora 0.114 and spatial_lattice/mnist 0.9167 both measure (A30); the three candidates were existing rows |
| Hardcoded MNIST defaults | 5+ | 0 | factory/builder/app path: **0** (A28: `_apply_task_spatial` + task-shaped `own_knob_params`); base-box rows declare their own mnist-shaped task |
| Lost result on crash | 2 axes | 0 | per-primitive parts under `<axis>/parts/` |
| Breadth exit | not run | `comp gate breadth` PASS | **PASS** (17/17 error-aware credits, ≥2 families) |
| Held-out cost prediction | unpriced | box price within tolerance | **0.38** median `|ratio-1|` by box key; 0.78 by task key (A29) |
| Refusal rate | — | <5% of non-skipped | **17.9%** (41 of 229 serial rungs), each with a named reason; **not met** — the remaining rows are L0 cost or a declared void rule (A5/A18–A20) |

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
- [x] 2.2 adafactor viable (0.913 at 0.59x); natural_gradient = named L0 cost (skipped, priced)
- [x] 2.3 claim runs at the registered box (+ lock)

### Phase 3 — Meta-SEC (done 2026-11-25)
- [x] 3.1 claim-seed space derives from the floor
- [x] 3.2 calibrate objective; assert best_value>0
- [x] 3.3 regenerate meta_sec_best.json (3.589, valid)

### Phase 4 — Coverage (done 2026-11-25)
- [x] 4.1 re-run skipped primitives (serial)
- [x] 4.2 breadth: `comp gate breadth` PASS (17/17 error-aware credits)
- [x] 4.3 record flipped refusals as A1 artifacts (34 rows, A27)

### Phase 5 — Competitive evidence
- [x] 5.1 best declared box per primitive (ladder + confirm seed)
- [x] 5.2 pre-registered paired comparisons to n_max (7, 64, 100 pairs)
- [ ] 5.3 claims: **restated** — 0 claims; the n=64 run missed 0.8 by 0.017 and seed-block d varies 0.83–1.07, so the target needs a pre-registered minimum every block clears *and* a block-variance estimate (A22)

### Phase 6 — Hardcoded removal
- [x] 6.1 geometry factories read no guessed extent (+ lock)
- [x] 6.2 sec_loop invents no edge_index/lattice_dims (+ lock)
- [x] 6.3 no MNIST literal in the app path; non-MNIST capability gate PASS

### Phase 7 — Budget
- [x] 7.1 wave sizing prices the fidelity's measured cells (offline pkl deleted)
- [x] 7.2 validated on a held-out wave (box price 0.38; task price 0.78 → box-keyed model landed, A29)

### Phase 8 — Proposals & docs
- [x] 8.1 re-triaged: both named carriers measure (A30); no new primitive
- [x] 8.2 regenerate TODO103 checklist
- [x] 8.3 record serial table + claim in stability-eval.md
```

---

## 🗒 Section G — Progress log

### Session 2026-11-25 (breadth exit, shape source, held-out price)
**Decision:** close the four remaining evidence/legitimacy items that do not
need a new mechanism — the breadth exit (4.2), the A1-artifact reconciliation
(4.3), the last MNIST-shape literals (6.3) and the cost-model validation
(7.2) — and restate 5.3 against A22 instead of chasing an unattainable 18+
claims at 0.916. Error cost of a wrong call: a map that says "refused" for a
mechanism that runs (A1) or a wave that dies on a guessed grid (A28).
**Experiment:** `comp gate breadth`; the serial3-vs-concurrent diff; the
geometry/pilot lock suites; `scripts/probes/todo104_non_mnist_shape.py`;
`scripts/probes/todo104_cost_model_heldout.py`.
**Box / rung / stop:** breadth exit is a repository predicate (rung 0 for the
gate); 6.3 is a rung-0 wiring check plus one L0 cell per topology (usps
1×16×16, digits 1×8×8); 7.2 is a held-out split of the 579 measured cells,
no new run.
**Result:** gate PASS (17/17 error-aware credits, ≥2 families; 960 legacy
records assessed). Reconciliation: 34 `all_refused → viable`, 6 `no_knob →
viable`, 3 `no_knob → refused`. Shape source: usps/conv 0.665 @ 2.2 s,
digits/nca 0.625 @ 0.5 s, both at their own extent. Held-out price: box key
0.38 median `|ratio-1|`, task key 0.78 → the task-keyed fallback under-prices.
**Triage:** 4.2/4.3 are gate + record (done); 6.3 fixes a defect with a lock
and a probe; 7.2 is a **capability gap** (box-keyed cost model) whose trigger
is `survey_cli`'s `cost_for_tasks`; 5.3's 18+ target is a **coordinate**
statement about the threshold (A22), not a mechanism verdict.
**Fixes Applied:** `sec_loop.py` (`_apply_task_spatial`, `screen_coordinate`),
`sec_pilot.py` (`_geometry_defaults`, task-shaped `own_knob_params`, stale
base-box extents removed), `_geometry_builders.py` (public
`channel_count`/`spatial_extent`), `test_geometry_shape_source_lock.py` (three
locks), `test_pilot_calibration.py` (the family-declaration lock now iterates
the box's own axes and skips variant rows), `sec_pilot.py`/`TODO103.md`/
`stability-eval.md` docs, two probes.
**Next Experiment:** the box-keyed cost model is landed (A29, cache + dry-run
price); next is a geometry-axis re-run that records the two carriers in the map
(graph/cora, spatial_lattice/mnist), then the `surrogate`/`fast_weights`/
`rule_state` named refusals and the A18–A20 composition rules.

### Session 2026-11-25 (continued: map + claims)
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
**Map (serial3 + the skip re-run):** 52/75 viable+blind; 176+ measured rungs
and 9 defects, each naming a mechanism (A18 routing×gradient, A19 ceiling
classification, A20 sparse gradient, A24 mean_norm default).
**Claims (claims2/claims3/claim64):** 7-pair effects are real
(`random_projections` d=+1.21, `analog` +1.00, `optical` +0.92,
`spectral_constrained` +4.34) and all are coordinates by A22; the n=64
confirmatory run measured d=+1.024 with a 0.783 lower bound against the
registered 0.8 — marginal. The n=100 fresh-seed run is pre-registered and in
flight (`logs/claim100_*`).

**Next experiment:** read the n=100 verdict; then fix A24 (mean_norm default),
A18/A19/A20 declarations, and re-run rung 2 at each arm's sized n. Read
each axis' parts under `results/sec/serial2/<axis>/parts/` even if a process
dies. Then: A5 cost profile (2.2), non-MNIST gate (6.3), docs (8.3).

**Sixth finding (A21):** the claim path compared two different mechanisms
(control from `AXIS_DEFAULTS`), so every knob claim reported |d| > 3. Both arms
now share the primitive. Claims re-run: `logs/claims2_*`.

**Fifth finding (A16/A17):** 33 defect rungs were `non-finite metric` because
the continual tasks' `evaluate` was the base class's empty body (no ruler), and
the map had chosen `continual` as the comparison family for axis-orthogonal
rules. Both are fixed: the continual tasks use the vision ruler, and the map
measures on `vision` when a rule declares it. A16/A17 are re-running for
geometry/dynamics/update/plasticity/substrate.

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
- Breadth exit (a predicate; exit 1 while any credit is below two families):
  `uv run comp gate breadth`
- Shape source: `uv run python scripts/probes/todo104_non_mnist_shape.py`
  (usps/conv, digits/nca at their own extent).
- Held-out price: `uv run python scripts/probes/todo104_cost_model_heldout.py`
  (task key vs box key over `results/sec/cells.jsonl`).

---

## ⛔ Never

- Call a concurrent-run timeout an algorithm verdict (A1).
- Emit a meta-SEC "best" with `best_value==0` or `claim_seeds<5` (A6, A7).
- Decide a claim at a box the ladder never measured (A8).
- Let a process death discard an axis of evidence (A9).
- Keep a hardcoded MNIST default behind a `[x]` checkbox (A10).
