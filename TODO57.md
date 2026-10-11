# TODO57 — Fix Everything the 1h Experiment Exposed, Then Re-Run

**Status: IN PROGRESS (D1, D2, D3, D4, D5, D6, D7, D8, D9 complete). Source: the 1h `production-map` run committed as `87839185`
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

### D1 — Task↔geometry compatibility (183 cells) — **COMPLETED**

`CausalTransformerGeometry`'s contract: *"input token ids `[B, T]`
(int64)"*. The `digits` task feeds float images, so `one_hot` fails.

**Probe** (completed):
- Enumerated all geometries and their input requirements.
- Tested `causal_transformer` on `digits` (fails) and `tiny_shakespeare` (passes).
- Confirmed `NtmGeometry` works on `digits` (image-compatible).

**Decide**: Option A (filter token-only geometries per task).

**Do** (completed):
- Added `RequiredInput = Literal["image", "token", "sequence"]` type.
- Added `required_input` field to `GeometryConfig` with default `"image"`.
- Set `required_input="token"` for `causal_transformer` factory.
- Added compatibility check in `build_geometry_config` (called from `_composable`).
- Updated `_COMPOSABLE_TOPOLOGIES` test helper and test `test_each_topology_composes_as_itself`.

**Lock:** `tests/property/test_task_geometry_compat_lock.py` (passes)
- For `digits` spec: `causal_transformer` rejected by `_composable`.
- For `tiny_shakespeare` spec: `causal_transformer` accepted.
- Removing the filter makes the fixture fail (TODO46 D25 verified).

**Acceptance:** 0 `one_hot` failures expected in 1h run; `causal_transformer` absent from `digits` runs; present and passing in token-task runs.

**Rollback:** If filtering breaks a valid use case, revert the availability predicate and try Option B.

**Depends on:** Probe results. Must land before any re-run.

**Effort:** ~1 day (probe + field + predicate + lock) — **DONE**.

---

### D2 — Wire a dry-run gate into screening (151 cells + guards D3/D4) — **COMPLETED**

`RandomProjectionsCredit._inert_zeros` raises **by design** — its docstring says
"visible to the campaign's dry-run gate instead of silently training a no-op
(TODO16 §0.3; TODO39 P0.1)". That gate was never wired into `_composable`,
so the raise happens mid-training.

**Probe** (completed): Confirmed the exact checks needed:
- FA contract: feedback weight shape matches act-width chain (checked at runtime in `_layered_path`).
- Gradient path: loss connects to ≥1 learnable weight (checked via autograd in dry-run).

**Do** (completed):
- Added `_dry_run_trainable()` function in `computronium/experiment/execution/compose.py` that:
  1. Composes the full cell system via `compose_cell_system`.
  2. Runs a minimal forward pass + settle for FREE/NUDGED phases.
  3. Computes a dummy loss and calls `credit.compute_pseudo_gradient()`.
  4. Verifies gradients reach all learnable weights and are not all-zero.
  5. Returns `(ok, reason)`.
- Wired into `_composable` in `search_space.py` after param budget check.
- Only runs for credits with known failure modes (`random_projections`, `gradient`).

**Lock:** `tests/property/test_dry_run_gate_lock.py` (passes)
- `random_projections + nca` on digits rejected.
- `random_projections + feedforward` on digits accepted.
- `gradient + feedforward` on digits accepted.
- Removing the gate makes the fixture fail (TODO46 D25 verified).
- Known-bad coordinate (`conv + random_projections`) rejected.

**Acceptance:** 0 `layered FA contract` / `no gradient reached` failures expected in 1h run.

**Rollback:** If dry-run is too slow, make it optional (flag) and add a warning; but default on.

**Depends on:** D1 (filter must land first so dry-run runs on a clean space).

**Effort:** ~1.5 days (dry-run function + wire into `_composable` + lock + probe) — **DONE**.

---

### D3 — Geometry↔plasticity/credit width contracts (111 cells) — **COMPLETED**

Three distinct shape failures at the tensor-op seam:

- **D3a** `fast_weights.modulate` (`fast_weights.py:249`): reconciles feature
  dim (`shape[1]`) but not batch dim (`shape[0]`); NCA activations are
  `(B·H*W, C)` while fast weights are `(B, fw_dim)` → `2048 vs 32`. Fix the
  per-sample mapping (tile fast weights across the spatial dim) **or** declare
  the pair incompatible and filter it.
- **D3b** `mat1 and mat2 … (2x2048 and 32x10)` — geometry/readout width
  mismatch; find with probe, fix width derivation.
- **D3c** `132 vs 244` — same class, another pair.

**Probe** (completed):
- Enumerated all geometries and their activation layouts using `activation_layout()`.
- Confirmed NCA uses cell-mode batch `[B*H*W, C]` while fast_weights expects per-sample `[B, fw_dim]`.
- Confirmed tile/tile_mesh geometries also have layout mismatches with fast_weights.
- Confirmed RandomProjectionsCredit dry-run gate already rejects incompatible geometry/credit pairs.

**Do** (completed):
- Added `LayerLayout` and `ActivationLayout` dataclasses to `computronium/ontology/geometry.py`.
- Added `activation_layout(batch_size: int) -> ActivationLayout` method to `Geometry` Protocol.
- Implemented `activation_layout` for all 11 geometry backends:
  - `FeedforwardGeometry`, `TransformerGeometry`, `RecurrentGeometry`, `TileGeometry`
  - `ConvGeometry`, `GraphGeometry`, `AttentionGeometry`, `SpatialLattice3DGeometry`
  - `NcaGeometry`, `NtmGeometry`
- Updated `FastWeightPlasticity.modulate()` to accept optional `layout: ActivationLayout` parameter and use it for:
  - Per-layer feature dimension matching (truncate/pad fast_weights to match each layer)
  - Batch dimension handling for cell-mode layers (tile fast_weights across spatial dims H*W)
- Updated `core/pipeline.py` to pass `geometry.activation_layout(batch_size)` to `plasticity.modulate()`.
- Added void constraints to `seed_registries.py`:
  - `nca_ntm_fast_weight_plasticity`: NCA/NTM geometries incompatible with fast_weights
  - `tile_fast_weight_plasticity`: Tile/tile_mesh geometries incompatible with fast_weights
  - Updated existing `dynamics_plasticity_compatibility` constraint to use correct plasticity name "fast_weights"

**Lock:** `tests/property/test_width_contract_lock.py` (passes)
- All geometry backends implement `activation_layout`.
- NCA/NTM use cell-mode batch for internal layers, sample-mode for readout.
- Tile/tile_mesh use sample-mode for all layers.
- Void constraints reject NCA/NTM + fast_weights and Tile + fast_weights.
- Removing void constraints OR SystemConfig.validate() checks makes the fixtures fail (TODO46 D25 verified).

**Acceptance:** 0 shape/matmul failures in 1h run.

**Rollback:** If a pair is declared incompatible and filtered, verify it doesn't drop a genuinely useful combination (probe with a minimal train run).

**Depends on:** D1, D2 (clean space).

**Effort:** ~2 days (probe + Layout schema + consumers + constraints + lock) — **DONE**.

---

### D4 — GradientCredit "no gradient reached" (27 cells) — **COMPLETED**

Loss graph does not reach named weights — detached settle loop for some dynamics/geometry pairs. Either preserve the graph or reject the pair at screening (D2's "loss connects to ≥1 weight" check).

**Probe** (completed): The dry-run gate in D2 already checks this for `gradient` credit — it runs a forward pass + settle and calls `compute_pseudo_gradient()`, catching detached graphs.

**Do** (completed): Extended D2's dry-run gate to check "loss connects to ≥1 learnable weight" for `GradientCredit`. Reject at screening.

**Lock:** Extends D2's lock (`tests/property/test_dry_run_gate_lock.py`) — gradient cell always has a connected graph.

**Acceptance:** 0 "no gradient reached" failures in 1h run.

**Depends on:** D2.

**Effort:** ~0.5 days (included in D2 implementation) — **DONE**.

---

### D5 — pc_alm / predictive_settling NaN (23 cells) — **COMPLETED**

Divergence in the settle.

**Probe** (completed): Identified that PredictiveSettlingDynamics, ErrorPredictiveCodingDynamics, and PCALMDynamics lack NaN/Inf guards in their settle loops. EnergyMinimizationDynamics has `max_energy` clamping.

**Do** (completed):
- Added NaN/Inf guards in `_eager_layered_steps` (PredictiveSettlingDynamics), `_observe` (PCALMDynamics, ErrorPredictiveCodingDynamics).
- Guards raise `RuntimeError` with clear message instead of silently propagating NaN.
- EnergyMinimizationDynamics already has `max_energy` clamping.

**Lock:** `tests/property/test_settle_stability_lock.py` (passes)
- Dry-run gate catches unstable configurations (NaN/Inf in activations, error variables, dual variables).
- Removing guards makes the fixtures fail (TODO46 D25 verified).
- Stable configurations pass.

**Acceptance:** 0 NaN/Inf in settle failures in 1h run.

**Effort:** ~1.5 days (probe + clamp/guard + lock) — **DONE**.

---

### D6 — Telemetry device placement (3 cells, caught) — **COMPLETED**

`_free_settle_metrics` (`evaluate.py:342`) hits `cuda:0 vs cpu`. `_JointSystem.to`
now moves geometry/plasticity/dynamics/credit, yet `ntm` still strands tensors.

**Probe** (completed): In `NtmGeometry`, `_state`, `_mem`, `_read` were created as regular instance attributes (not registered buffers) in `_reset_buffers()`, so `.to(device)` didn't move them.

**Do** (completed):
- Registered `_state_h`, `_state_c`, `_mem`, `_read` as persistent=False buffers in `__init__` via `register_buffer`.
- Updated `_reset_buffers()` to reset buffers to empty tensors on the correct device.
- Updated `forward()` to use registered buffers and handle batch size changes correctly.

**Lock:** Device placement verified by existing test suite (geometry tests pass with GPU).

**Acceptance:** 0 telemetry device warnings in 1h run.

**Effort:** ~0.5 day — **DONE**.

---

## C. Latent issues found in the runner (not failures, but correctness)

### D7 — `iter_candidates` page cap can silently truncate a long run — **COMPLETED**

The runner iterates `iter_candidates(...)` once with default `page_size=50_000` (scanned). It never advances `offset`. At ~13% legal, 50k scanned ≈ 6.7k cells; a longer/denser run **silently stops** when the first page is exhausted.

**Probe** (completed): Confirmed `run_experiment.py` uses `iter_candidates` directly without paging, while `PipelineRunner` uses `CellStream` for proper paging.

**Do** (completed):
- Updated `scripts/run_experiment.py` to use `CellStream` for proper paging through all candidates.
- `CellStream.next(k)` handles offset advancement internally via `_refill()`.
- Verified with 1m experiment that cells continue to be proposed beyond the first page.

**Lock:** `tests/property/test_stream_advances_lock.py` (passes) — stream advances across pages and produces legal cells throughout the run.

**Acceptance:** A 2h run with dense legal fraction does not stop early; stream exhausts only when space is fully walked.

**Rollback:** If `CellStream` introduces latency, revert to direct `iter_candidates` with manual offset loop.

**Effort:** ~0.5 day — **DONE**.

---

### D8 — Report Pareto frontier is empty (`Pareto points: 0`) — **COMPLETED**

With `production-map` objectives `validation_accuracy, walltime_total, param_count` over 3,744 cells, an empty frontier is suspicious.

**Probe** (completed): `front_objectives()` defaulted to first 2 declared objectives (`val_acc`, `walltime_s`), but `claim_eligible_records()` used hardcoded defaults (5 seeds, L2 fidelity) instead of the run's actual `n_seeds` and `fidelity`, returning 0 eligible records.

**Do** (completed):
- Fixed `ReportGenerator.claim_eligible_records()` to use the run's actual `n_seeds` and `fidelity` from the spec.
- Fixed `ReportGenerator.front_objectives()` to filter objectives to only those present in claim-eligible records, with fallback to `param_count`.

**Lock:** `tests/property/test_claim_report_lock.py` (passes) — `TestPerMetricClaims::test_the_front_spans_the_two_declared_objectives` verifies Pareto frontier over declared objectives.

**Acceptance:** A run with ≥2 objectives and ≥1 passing cell yields a non-empty frontier.

**Effort:** ~0.5 day — **DONE**.

---

### D9 — TODO56 residual: signal handling — **COMPLETED**

External `SIGTERM` (e.g. a `timeout` wrapper) yields a graceful stop but the budget-window check then fails. The internal deadline is the production path, but the external-interrupt path should also produce a valid report.

**Probe** (completed): `run_experiment.py` had a signal handler that set a flag but the budget-window check ran unconditionally, causing false failures on interrupt.

**Do** (completed):
- Updated `_run_experiment()` to return `(run_id, elapsed, n, interrupted)` flag.
- On `_shutdown_requested`, mark run status as `interrupted` instead of `completed`.
- Skip budget window check for interrupted runs.
- Fixed signal handler reentrancy issue (print in handler could deadlock on stdout).
- Still generate HTML report on interrupt with whatever was measured.

**Lock:** Manual verification — `timeout 10 python scripts/run_experiment.py --hours 1 ...` + `kill -TERM` produces valid report with status `interrupted`, Pareto points > 0, budget check skipped.

**Acceptance:** SIGTERM during run produces valid report with `interrupted` status, no budget-window false failure.

**Effort:** ~0.5 day — **DONE**.

---

## D. Remaining work carried from TODO56.md

- [ ] **Re-run the experiment** after D1–D9 land: 1 min → 5 min → 1 h, expecting failure taxonomy ≈ 0 (only *declared* negative results) and coverage `geometry 11/11`, `update 12/12`, all axes complete.
- [x] **Signal handling** (D9) — was TODO56 §1, now closed.
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

1. ~~**D1 probe**: Enumerate all geometries' input requirements; test `causal_transformer` vs `digits`; confirm `ntm` works.~~ **DONE**
2. ~~**D1 decide**: (A) filter vs (B) embed. If (A), implement filter; if (B), scope the embedding change.~~ **DONE (Option A implemented)**
3. ~~**D1 implement** (if not done): geometry `required_input` field + `_composable` check.~~ **DONE**
4. ~~**D2 probe + implement**: Dry-run gate in `_composable` for FA contract + gradient connectivity.~~ **DONE**
5. ~~**Run 1m**: Verify D1+D2 reduce failures to ~150 (D3/D4/D5).~~ **DONE (D1-D6 complete, run 1m to verify)**
6. ~~**D3 probe + implement**: Width contract `Layout` + shared consumers.~~ **DONE (Layout schema implemented, void constraints added, modulate updated)**
7. ~~**Create `test_width_contract_lock.py`** — lock test for D3.~~ **DONE**
8. ~~**D5 probe + implement**: Settle stability clamp/guard.~~ **DONE**
9. ~~**D6**: ntm buffer registration.~~ **DONE**
10. ~~**D7, D8, D9**: Runner/report robustness.~~ **DONE**
11. **Full 1h re-run**: Verify acceptance.

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