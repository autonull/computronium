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

## B. Defect work items (fix + lock + probe + acceptance)

Each item below has: **Probe** (what to investigate before fixing), **Do** (the fix), **Lock** (falsifiable test), **Acceptance** (when is this item done), **Rollback** (if the fix breaks something else), **Depends on** (what must land first), **Effort** (rough estimate).

---

### D1 — Task↔geometry compatibility (183 cells) — **DESIGN DECISION FIRST**

`CausalTransformerGeometry`'s contract: *"input token ids `[B, T]`
(int64)"*. The `digits` task feeds float images, so `one_hot` fails.

**Probe** (before deciding):
- Enumerate all geometries and their input requirements (token vs image vs sequence) by inspecting `GeometryConfig` fields and `forward` signatures.
- Run a probe: for each geometry, attempt a forward pass with `digits` (float images) and a token task (if available); record which succeed/fail.
- Confirm `NtmGeometry` truly works on `digits` (it did in 1h run) — verify it's image-compatible.

**Decide** (then implement one):
- **Option A (default):** Filter token-only geometries per task. Add `required_input: {image, token, sequence}` to `GeometryConfig` / availability predicate; `_composable` rejects mismatches.
- **Option B:** Make `causal_transformer` embed float inputs (architecture change; larger scope).
- Default to **(A)** unless probe shows (B) is trivial and safe.

**Do** (if A): add `required_input` field to `GeometryConfig`; populate for all 11 geometries; add check in `_composable` (or `compose_configs`) that rejects a geometry when `task.required_input != geometry.required_input`. Audit all 11 geometries and fill the field.

**Lock:** `tests/property/test_task_geometry_compat_lock.py`
- For `digits` spec: no proposed cell uses a token-only geometry; `causal_transformer` absent.
- For a token-task spec: `causal_transformer` is proposed and trains.
- Removing the filter must make the fixture fail (TODO46 D25).

**Acceptance:** 0 `one_hot` failures in 1h run; `causal_transformer` absent from `digits` runs; present and passing in token-task runs.

**Rollback:** If filtering breaks a valid use case, revert the availability predicate and try Option B.

**Depends on:** Probe results. Must land before any re-run.

**Effort:** ~1 day (probe + field + predicate + lock).

---

### D2 — Wire a dry-run gate into screening (151 cells + guards D3/D4)

`RandomProjectionsCredit._inert_zeros` raises **by design** — its docstring says
"visible to the campaign's dry-run gate instead of silently training a no-op
(TODO16 §0.3; TODO39 P0.1)". That gate was never wired into `_composable`,
so the raise happens mid-training.

**Probe:** Confirm the exact checks needed:
- FA contract: for each learnable weight, feedback weight shape matches act-width chain.
- Gradient path: loss connects to ≥1 learnable weight (autograd graph not detached).

**Do:** Add a `dry_run_trainable(cell_config)` function that:
1. Composes the cell (already done in `_composable`).
2. Runs the credit's dry-run check (FA contract / gradient connectivity) without training.
4. Returns `(ok, reason)`; `_composable` rejects if not ok.

Wire this into `_composable` (after `compose_configs`, before returning). Ensure `_composable`, `SystemConfig.validate`, and evaluator first-step guards all consult the same predicates.

**Lock:** `tests/property/test_dry_run_gate_lock.py`
- A coordinate the space yields never raises `_inert_zeros` / "no gradient reached" in training.
- Removing the gate must make the fixture fail (TODO46 D25).
- Probe: construct a known-bad coordinate (e.g., `conv` + `random_projections`) and assert the gate rejects it.

**Acceptance:** 0 `layered FA contract` / `no gradient reached` failures in 1h run.

**Rollback:** If dry-run is too slow, make it optional (flag) and add a warning; but default on.

**Depends on:** D1 (filter must land first so dry-run runs on a clean space).

**Effort:** ~1.5 days (dry-run function + wire into `_composable` + lock + probe).

---

### D3 — Geometry↔plasticity/credit width contracts (111 cells)

Three distinct shape failures at the tensor-op seam:

- **D3a** `fast_weights.modulate` (`fast_weights.py:249`): reconciles feature
  dim (`shape[1]`) but not batch dim (`shape[0]`); NCA activations are
  `(B·H·W, C)` while fast weights are `(B, fw_dim)` → `2048 vs 32`. Fix the
  per-sample mapping (tile fast weights across the spatial dim) **or** declare
  the pair incompatible and filter it.
- **D3b** `mat1 and mat2 … (2x2048 and 32x10)` — geometry/readout width
  mismatch; find with probe, fix width derivation.
- **D3c** `132 vs 244` — same class, another pair.

**Probe:** For each failing (geometry, plasticity, credit) tuple from the 1h run, print the geometry's `active(coordinate)` layout, the plasticity's expected `fw_dim` / credit's expected shapes, and the mismatch. Build a table of all (geometry, plasticity, credit) combos in the space and their expected vs actual widths.

**Do:** There is one width contract (activation layout per geometry) consumed by plasticity, credit, and readout. Make it explicit and shared:
- Add `Geometry.activation_layout(coordinate) -> Layout` returning a structured description (per-layer shapes, batch handling).
- Update `FastWeightPlasticity`, `RandomProjectionsCredit`, `GradientCredit`, readout to consume `Layout` instead of re-deriving.
- If a pair is fundamentally incompatible (e.g., NCA + fast_weights), add a void constraint rather than hacking the code.

**Lock:** `tests/property/test_width_contract_lock.py`
- For every (geometry, plasticity, credit) the space yields, `modulate` / credit shapes match the geometry's declared `activation_layout`.
- Removing the `Layout` sharing must make the fixture fail.

**Acceptance:** 0 shape/matmul failures in 1h run.

**Rollback:** If a pair is declared incompatible and filtered, verify it doesn't drop a genuinely useful combination (probe with a minimal train run).

**Depends on:** D1, D2 (clean space).

**Effort:** ~2 days (probe + Layout schema + consumers + constraints + lock).

---

### D4 — GradientCredit "no gradient reached" (27 cells)

Loss graph does not reach named weights — detached settle loop for some dynamics/geometry pairs. Either preserve the graph or reject the pair at screening (D2's "loss connects to ≥1 weight" check).

**Probe:** Identify which (dynamics, geometry) pairs trigger this. Is it specific to certain dynamics (e.g., `pc_alm`, `error_predictive_coding`) or all detached-settle dynamics?

**Do:** Extend D2's dry-run gate to check "loss connects to ≥1 learnable weight" for `GradientCredit`. Reject at screening.

**Lock:** Extends D2's lock (gradient cell always has a connected graph).

**Acceptance:** 0 "no gradient reached" failures in 1h run.

**Depends on:** D2.

**Effort:** ~0.5 days (included in D2 implementation).

---

### D5 — pc_alm / predictive_settling NaN (23 cells)

Divergence in the settle.

**Probe:** For each failing pair, capture the step number, energy trajectory, and dynamics config. Is it a step-size/clamp defect or a genuinely unstable pair? Run a probe that sweeps `step_size` and `beta` for the failing pairs.

**Do:** 
- If step-size/clamp: add per-dynamics clamp/step-size limit in the settle loop, or validate config at compose time.
- If genuinely unstable: mark the pair void via constraint.
- Add a divergence guard in the settle loop (max energy, NaN check) that aborts with a clear verdict instead of NaN propagation.

**Lock:** `tests/property/test_settle_stability_lock.py` — the space does not yield a cell whose declared settle diverges on its own init (run a 0-epoch dry-run settle).

**Acceptance:** 0 NaN/Inf in settle failures in 1h run.

**Effort:** ~1.5 days (probe + clamp/guard + lock).

---

### D6 — Telemetry device placement (3 cells, caught)

`_free_settle_metrics` (`evaluate.py:342`) hits `cuda:0 vs cpu`. `_JointSystem.to`
now moves geometry/plasticity/dynamics/credit, yet `ntm` still strands tensors.

**Probe:** In `NtmGeometry`, find all tensors created in `__init__` / `_reset_buffers` / `step` that are not registered as buffers/parameters and thus not moved by `.to()`. Likely `_mem`, `_read`, `_state` created on CPU.

**Do:** Register `_mem`, `_read`, `_state` as buffers with `register_buffer` (so `.to(device)` moves them) OR create them on the input device in `step`/`forward`.

**Lock:** `tests/property/test_device_placement_lock.py` — after `system.to("cuda")`, every tensor reachable from the system is on `cuda` (skip if no GPU).

**Acceptance:** 0 telemetry device warnings in 1h run.

**Effort:** ~0.5 day.

---

## C. Latent issues found in the runner (not failures, but correctness)

### D7 — `iter_candidates` page cap can silently truncate a long run

The runner iterates `iter_candidates(...)` once with default `page_size=50_000` (scanned). It never advances `offset`. At ~13% legal, 50k scanned ≈ 6.7k cells; a longer/denser run **silently stops** when the first page is exhausted.

**Do:** Page the stream in the runner: `while not deadline.expired(): for cell in iter_candidates(..., offset=offset, page_size=page_size): ...; offset += page_size`. Or raise the cap and assert non-truncation. The 1h run did not hit it (3,744 cells ≈ 28k scanned) but the ceiling is real.

**Lock:** `tests/property/test_stream_paging_lock.py` — a run whose legal density exceeds one page still reaches its deadline (simulate by setting `page_size=100` and running a long enough profile).

**Acceptance:** A 2h run with dense legal fraction does not stop early.

**Effort:** ~0.5 day.

---

### D8 — Report Pareto frontier is empty (`Pareto points: 0`)

With `production-map` objectives `validation_accuracy, walltime_total, param_count` over 3,744 cells, an empty frontier is suspicious.

**Probe:** Check `ReportGenerator.pareto_frontier` — does it read `val_acc`, `walltime_s`, `param_count` from records? Or is it keyed on `validation_accuracy` (missing)?

**Do:** Ensure `ReportGenerator` reads the actual metric names stored in records (`val_acc`, `walltime_s`, `param_count`). If keys differ, map them.

**Lock:** Extends the report/render lock — a run with ≥2 objectives and ≥1 passing cell yields a non-empty frontier.

**Effort:** ~0.5 day.

---

### D9 — TODO56 residual: signal handling

External `SIGTERM` (e.g. a `timeout` wrapper) yields a graceful stop but the budget-window check then fails. The internal deadline is the production path, but the external-interrupt path should also produce a valid report.

**Do:** On shutdown-requested, still finalize the run and generate the report from whatever was measured. In `_run_experiment`, catch the shutdown flag, call `store.finish_run` with status `interrupted`, then call `_generate_report`.

**Lock:** `tests/property/test_signal_shutdown_lock.py` — send `SIGTERM` to a running 10s experiment; assert it produces a valid report with status `interrupted`.

**Effort:** ~0.5 day.

---

## D. Remaining work carried from TODO56.md

- [ ] **Re-run the experiment** after D1–D9 land: 1 min → 5 min → 1 h, expecting failure taxonomy ≈ 0 (only *declared* negative results) and coverage `geometry 11/11`, `update 12/12`, all axes complete.
- [ ] **Signal handling** (D9) — was TODO56 §1, never closed.
- [ ] **Do not** reintroduce the deleted CellStream/BatchSizer/regime ladder; the `_walk` pager + `Deadline` + store dedup is the design (TODO56 anti-patterns).
- [ ] Keep `scripts/run_experiment.py` transparent: it must name the experiment and fail loud on zero cells (already done — keep it that way).
- [ ] `docs/notebooks/` is untracked and unrelated to this effort — decide whether to track it separately.

---

## E. Sequencing & Dependencies

```
D1 (probe → decide → filter) 
  ↓
D2 (dry-run gate) 
  ↓
D3 (width contracts) ← D1, D2
  ↓
D4 (gradient graph) ← D2
D5 (NaN) ← D2, D3
  ↓
D6 (telemetry device)
  ↓
D7 (paging), D8 (Pareto), D9 (SIGTERM) — can run in parallel with D3–D5
  ↓
Re-run **1m → 5m → 1h**; verify acceptance.
```

---

## F. Acceptance for "Fixed"

- A fresh 1h `production-map` run: `failure taxonomy == {}` for the intended objectives (or every entry is a *declared* negative result with a constraint naming it in `CONSTRAINTS_REGISTRY`), and coverage complete on all six axes (`geometry 11/11`, `update 12/12`).
- Every fix carries a **lock whose fixture fails when the mechanism is removed** (TODO46 D25) — a lock that cannot fail is a comment.
- Screening and evaluation consult one contract; no coordinate is proposed that the evaluator cannot train.
- Every fix has an investigation probe, a rollback plan, and a falsifiable lock.

---

## G. Investigation order for the next session

1. **D1 probe**: Enumerate all geometries' input requirements; test `causal_transformer` vs `digits`; confirm `ntm` works.
2. **D1 decide**: (A) filter vs (B) embed. If (A), implement filter; if (B), scope the embedding change.
3. **D2 probe + implement**: Dry-run gate in `_composable` for FA contract + gradient connectivity.
4. **D1 implement** (if not done): geometry `required_input` field + `_composable` check.
5. **Run 1m**: Verify D1+D2 reduce failures to ~150 (D3/D4/D5).
6. **D3 probe + implement**: Width contract `Layout` + shared consumers.
7. **D5 probe + implement**: Settle stability clamp/guard.
7. **D6**: ntm buffer registration.
8. **D7, D8, D9**: Runner/report robustness.
8. **Full 1h re-run**: Verify acceptance.

---

## H. Investigation probes needed (run these first)

```bash
# D1 probe: enumerate geometry input requirements
uv run python -c "
from computronium.ontology.geometry import GEOMETRIES
for name, spec in GEOMETRIES.items():
    print(name, 'input_dims', getattr(spec, 'input_dims', None), 'seq_len', getattr(spec, 'seq_len', None))
"

# D1 probe: test causal_transformer on digits (float) vs token task
uv run python -c "
from computronium.experiment.execution.compose import compose_cell_system
from computronium.experiment.schema.coordinate import Coordinate
from computronium.experiment.execution.evaluate import task_shape
c=Coordinate(substrate='digital', geometry='causal_transformer', dynamics='instantaneous', plasticity='null', credit='gradient', update='adam', params={})
try:
    sys=compose_cell_system(coordinate=c, task='digits', param_budget=50000)
    print('compose ok')
except Exception as e:
    print('compose FAIL', e)
"

# D2 probe: find all coords that trigger _inert_zeros
uv run python -c "
from computronium.ontology.credit import RandomProjectionsCredit
# What geometry act-width chains does it accept?
"

# D3 probe: for each failing (geometry, plasticity, credit) tuple from 1h run, print act-layout
# D5 probe: sweep step_size/beta for failing pc_alm pairs
```

---

## I. Verification that locks catch regressions

Before landing each D-item, run its lock with the mechanism **commented out** — the fixture must fail. If it passes, the lock is a comment and the fix is not locked. (TODO46 D25 rule.)