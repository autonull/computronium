# TODO57 — Fix Everything the 1h Experiment Exposed, Then Re-Run

**Status: PLAN. Source: the 1h `production-map` run committed as `87839185`
(3,744 cells, 100.0% budget, `results/exp_todo56_1h.html`). 504 cells (13%)
failed. Every failure is a *screening gap* or a *latent runtime defect* — the
runner and the diverse sampler now work. This plan closes all of them, then
repeats the experiment (1m → 5m → 1h) expecting a near-empty failure taxonomy
and complete axis coverage.**

Guiding rule (from TODO56): *a coordinate the space proposes is a coordinate the
evaluator can train.* Today the space proposes cells `SystemConfig.validate`
accepts but training cannot run. The fix is to make **screening and evaluation
read the same contracts** — one source of truth, not two.

---

## A. Failure taxonomy from the 1h run (504 cells)

| Count | Symptom | First location | Class |
|------:|---------|----------------|-------|
| 183 | `one_hot … index tensor LongTensor` | `ontology/geometry.py:1031` | task↔geometry compat |
| 151 | `RandomProjectionsCredit: layered FA contract would return all-zero pseudo-gradient … rejected at dry-run` | `ontology/credit.py:920` (`_inert_zeros`) | missing dry-run gate |
| 111 | shape/matmul: `2048 vs 32`, `132 vs 244`, `2x2048 · 32x10` | `core/plasticity/fast_weights.py:249`, geometry/credit width contracts | width-derivation |
| 27 | `GradientCredit: no gradient reached [ … ]` | `credit.py` gradient path | detached settle graph |
| 23 | `NaN/Inf in activations at step N (pc_alm / predictive_settling settle)` | `ontology/dynamics/_dynamics.py` | numerical divergence |
| 6 | `non-finite metrics …` | `experiment/execution/evaluate.py` | downstream of A5/A6 |
| 3 | `free settle telemetry failed: … cuda:0 vs cpu` (caught) | `evaluate.py:342` | device placement |

---

## B. Defect work items (fix + lock)

### D1 — Task↔geometry compatibility (183 cells) — **design decision first**
`CausalTransformerGeometry`'s contract is explicit: *"input token ids `[B, T]`
(int64)"*. The `digits` task feeds float images, so `one_hot` cannot run.
- **Decide:** either (a) the space must filter token-only geometries for
  non-token tasks, or (b) `causal_transformer` embeds float inputs (architecture
  change). Default to **(a)** — a geometry declares the input kind it requires;
  `_composable`/`compose_configs` rejects a mismatch, exactly as it already
  rejects shape mismatches.
- **Do:** add `required_input: {image, token}` (or equivalent) to
  `GeometryConfig`/availability; make the availability predicate (or a
  task-aware check in `_composable`) reject `causal_transformer` on an image
  task. Audit every geometry for the same declaration (`ntm`, `nca`,
  `spatial_lattice`, `graph`, `attention`, `conv`, `tile*`, `recurrent`,
  `feedforward`).
- **Special probe:** with the `digits`-flatten trick, `NtmGeometry` *does* run
  (it passed in the 1h run) — confirm `ntm` is image-compatible before
  filtering, so we drop only what is genuinely token-only.
- **Lock:** `tests/property/test_task_geometry_compat_lock.py` — for the
  `digits` spec, no proposed cell uses a token-only geometry; for a token task,
  `causal_transformer` is proposed and trains.

### D2 — Wire a dry-run gate into screening (151 + guards the rest)
`RandomProjectionsCredit._inert_zeros` raises **by design** — its docstring says
"visible to the campaign's dry-run gate instead of silently training a no-op
(TODO16 §0.3; TODO39 P0.1)". That gate was never wired into this runner's
`_composable`, so the raise happens mid-training.
- **Do:** give the search space a cheap **trainability dry-run**: compose the
  cell (already done) and assert the credit's no-op guard is not triggered — the
  FA contract only needs the geometry's act-width chain vs feedback shapes, and
  the gradient path only needs "loss connects to ≥1 learnable weight". Both are
  structural (no training), so they belong in `_composable`.
- **Do:** unify so `_composable`, `SystemConfig.validate`, and the evaluator's
  first-step guards consult the **same** predicates. The two-channel defect
  (screen one way, train another) is the root of A2/A3/A4.
- **Lock:** `tests/property/test_dry_run_gate_lock.py` — a coordinate the space
  yields never raises `_inert_zeros` / "no gradient reached" in training;
  removing the gate must make the fixture fail (the TODO46 D25 rule).

### D3 — Geometry↔plasticity/credit width contracts (111 cells)
Three distinct shape failures, all at the tensor-op seam:
- **D3a** `fast_weights.modulate` (`fast_weights.py:249`): reconciles feature
  dim (`shape[1]`) but not batch dim (`shape[0]`); NCA activations are
  `(B·H·W, C)` while fast weights are `(B, fw_dim)` → `2048 vs 32`. Fix the
  per-sample mapping (tile fast weights across the spatial dim) **or** declare
  the pair incompatible and filter it.
- **D3b** `mat1 and mat2 … (2x2048 and 32x10)` — a geometry/readout width
  mismatch for some pairs; find with a probe, fix the width derivation.
- **D3c** `132 vs 244` — same class, another pair.
- **Do:** there is one width contract (activation layout per geometry) consumed
  by plasticity, credit, and readout. Make it explicit and shared, not
  re-derived in each consumer.
- **Lock:** `tests/property/test_width_contract_lock.py` — for every
  (geometry, plasticity, credit) the space yields, modulate/credit shapes match
  the geometry's declared act layout.

### D4 — GradientCredit "no gradient reached" (27 cells)
The loss graph does not reach named weights — a detached settle loop for some
dynamics/geometry pairs. Either preserve the graph or reject the pair at
screening (D2's "loss connects to ≥1 weight" check).
- **Lock:** extends D2's lock (gradient cell always has a connected graph).

### D5 — pc_alm / predictive_settling NaN (23 cells)
Divergence in the settle. Determine whether it is a step-size/clamp defect or a
genuinely unstable pair.
- **Do:** inspect the settle for the failing pairs; add divergence guard
  (clamp/abort-with-verdict) and/or mark the pair void.
- **Lock:** `tests/property/test_settle_stability_lock.py` — the space does not
  yield a cell whose declared settle diverges on its own init.

### D6 — Telemetry device placement (3 cells, caught)
`_free_settle_metrics` (`evaluate.py:342`) hits `cuda:0 vs cpu`. `_JointSystem.to`
now moves geometry/plasticity/dynamics/credit, yet `ntm` still strands tensors.
- **Do:** find the un-moved tensor in `NtmGeometry` (lazy `_mem`/`_read`/`_state`
  created off-device) and register it as a buffer or create it on the input
  device. Then the telemetry settles and reports.
- **Lock:** `tests/property/test_device_placement_lock.py` — after `system.to(
  "cuda")`, every tensor reachable from the system is on `cuda` (skip if no GPU).

---

## C. Latent issues found in the runner (not failures, but correctness)

### D7 — `iter_candidates` page cap can silently truncate a long run
The runner iterates `iter_candidates(...)` once with default
`page_size=50_000` (scanned candidates). It never advances `offset`. At ~13%
legal, 50k scanned ≈ 6.7k cells; a longer/denser run **silently stops** when the
first page is exhausted, before the deadline.
- **Do:** page the stream in the runner (`offset += page_size`, loop until the
  deadline), or raise the cap and assert non-truncation. The 1h run did not hit
  it (3,744 cells ≈ 28k scanned, ended on the deadline) but the ceiling is real.
- **Lock:** `tests/property/test_stream_paging_lock.py` — a run whose legal
  density exceeds one page still reaches its deadline.

### D8 — Report Pareto frontier is empty (`Pareto points: 0`)
With `production-map` objectives `validation_accuracy, walltime_total,
param_count` over 3,744 cells, an empty frontier is suspicious.
- **Do:** verify `ReportGenerator.pareto_frontier` reads the right objective
  keys from records (records carry `val_acc`, `walltime_s`, `param_count`);
  confirm it is not silently keyed on absent metric names.
- **Lock:** extends the report/render lock — a run with ≥2 objectives and ≥1
  passing cell yields a non-empty frontier.

### D9 — TODO56 residual: signal handling
External `SIGTERM` (e.g. a `timeout` wrapper) yields a graceful stop but the
budget-window check then fails. The internal deadline is the production path, but
make the external-interrupt path produce a valid report too.
- **Do:** on shutdown-requested, still finalize the run and generate the report
  from whatever was measured.
- **Lock:** `tests/property/test_signal_shutdown_lock.py`.

---

## D. Remaining work carried from TODO56.md

- [ ] **Re-run the experiment** after D1–D9 land: 1 min → 5 min → 1 h, expecting
      failure taxonomy ≈ 0 (only *declared* negative results) and coverage
      `geometry 11/11`, `update 12/12`, all axes complete.
- [ ] **Signal handling** (D9) — was TODO56 §1, never closed.
- [ ] **Do not** reintroduce the deleted CellStream/BatchSizer/regime ladder; the
      `_walk` pager + `Deadline` + store dedup is the design (TODO56 anti-patterns).
- [ ] Keep `scripts/run_experiment.py` transparent: it must name the experiment and
      fail loud on zero cells (already done — keep it that way).
- [ ] `docs/notebooks/` is untracked and unrelated to this effort — decide whether
      to track it separately.

---

## E. Sequencing

1. **D1, D2** first — they are 66% of failures and both are *screening*, so they
   shrink every later run and unblock clean data.
2. **D3, D4, D5** — runtime defects behind the screening gates.
3. **D6, D9** — device/interrupt robustness.
4. **D7, D8** — runner/report correctness.
5. Re-run **1m → 5m → 1h**; re-pin figures/manifest if any demo changes.

## F. Acceptance for "fixed"

- A fresh 1h `production-map` run: `failure taxonomy == {}` for the intended
  objectives (or every entry is a *declared* negative result with a constraint
  naming it), and coverage complete on all six axes.
- Every fix carries a **lock whose fixture fails when the mechanism is removed**
  (TODO46 D25) — a lock that cannot fail is a comment.
- Screening and evaluation consult one contract; no coordinate is proposed that
  the evaluator cannot train.
