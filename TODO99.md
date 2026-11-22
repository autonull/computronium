# TODO99 Improvements — Beyond Acceleration

**Status:** 2026-11-22. Additional high-impact improvements that compound with the accelerated plan.

---

## 1. Infrastructure: Single-Session Surface Re-measure ✅ DONE

**Problem:** Each P3 session runs `p1_law_surface.py --resume` (5 min cached) + `comp test --surface` (10 min). The surface recomputes 75 laws × 2 instruments = 150 cells.

**Fix:** Add `--incremental` flag to surface CLI — only re-measure laws whose code changed.

```python
# scripts/probes/p1_law_surface.py
# Track file hashes per law; on --incremental, only re-run laws with changed deps
```

**Saves:** 10 min/session × 4 sessions = **40 min wall-clock**. Compounds across all future sessions.

**Implementation:** Added `--incremental` flag to `p1_law_surface.py` that tracks axis-level file dependency hashes and only re-runs laws whose dependencies changed.

---

## 2. Architecture: Remove the "Screened Box" Indirection ✅ DONE

**Problem:** `_build_box_for_family()` reads `results/sec/map.json` to get the "screened box" for compatibility. This is a runtime lookup of a static property.

**Fix:** Move compatibility into the primitive's identity card — declare `compatible_geometries`, `compatible_dynamics`, `requires_readout_error` as static fields. The search space filters at harvest time, not at run time.

```python
# computronium/primitives/protocol.py
@dataclass(frozen=True, slots=True)
class PrimitiveSpec:
    compatible_geometries: tuple[str, ...] = ()
    compatible_dynamics: tuple[str, ...] = ()
    requires_readout_error: bool = False
    # ...
```

**Eliminates:** `_build_box_for_family()`, `screen_coordinate()` lookup, map.json dependency for SEC. Makes legality a static property.

**Implementation:** Added fields to `PrimitiveSpec` in `protocol.py` and populated them in `registry.py` via `_COMPATIBLE_GEOMETRIES`, `_COMPATIBLE_DYNAMICS`, `_REQUIRES_READOUT_ERROR` dictionaries.

---

## 3. Scope: Add Missing Task Families to Breadth ✅ DONE

**Current breadth gate:** 17 credits × 2 families = 34 cells. But some credits only have 1 legal family (e.g., `pc_alm` only tabular/vision).

**Add:** 
- `pc_alm` → graph classification (needs graph geometry + energy_minimization)
- `thermodynamic_contrast` → sequence (needs recurrent + energy_minimization)
- `target_inversion` → continual (needs compatible dynamics)

**How:** Add geometry/dynamics combos to BASE_BOXES in Session C. No new code — just composition table entries.

**Gains:** More viable (credit, family) pairs → more claim candidates → higher chance of ≥3 claims.

**Implementation:** 
- Added `graph_energy_min`, `sequence_energy_min`, `continual_energy_min` to `BASE_BOXES` in `sec_pilot.py`
- Updated `task_families` for `pc_alm`, `thermodynamic_contrast`, `target_inversion` in `registry.py`
- Fixed `coordinate()` in `fit.py` to use the family's `base_coordinate` directly

---

## 4. Process: Capability Suite as Continuous Gate ✅ DONE

**Problem:** Capability suite runs once at Session 6. If a P3 fix breaks a previously-working primitive, we don't know until Session 6.

**Fix:** Run capability on *changed primitives only* after each P3 session.

```sh
# After Session A (plasticity fixes):
uv run python scripts/run_capability.py --session A

# After Session B (update + credits):
uv run python scripts/run_capability.py --session B
```

**Gains:** Immediate feedback; no regression surprises at Session 6.

**Implementation:** Created `scripts/run_capability.py` helper script with predefined session groups (A, B, C, D) for running capability tests on relevant primitives.

---

## 5. Architecture: Parallel SEC Evaluator ✅ DONE

**Problem:** SEC runs 5 seeds × 2 arms = 10 cells sequentially per (credit, family). At ~5 min/cell = 50 min per ladder.

**Fix:** `evaluate_cell` is pure (no shared state). Use `asyncio.TaskGroup` with semaphore for GPU memory.

```python
# computronium/experiment/sec_loop.py _paired_cells
async def _paired_cells_async(candidate, schedule, treatment, semaphore):
    async with semaphore:
        return await asyncio.to_thread(_measure, ...)
```

**Saves:** 50 min → **10-15 min** per ladder (4-5× speedup). Compounds across all SEC runs.

**Implementation:** Added `_paired_cells_async` and `_ladder_async` to `sec_loop.py` using `asyncio.gather` with semaphore for GPU memory control. P4 track now uses async versions by default.

---

## 6. Scope: Claim on "Effect Size" Not Just Margin ✅ DONE

**Current:** Margin = 0.01 (1% absolute accuracy). This is arbitrary and doesn't scale.

**Fix:** Use Cohen's d with pre-registered minimum effect size per task family:

| Task Family | Min d | Rationale |
|-------------|-------|-----------|
| Vision (mnist) | 0.8 | Large effect detectable |
| Tabular (iris) | 0.5 | Medium effect, small N |
| Graph (cora) | 0.5 | Medium effect |
| Sequence | 0.8 | High variance |
| Continual | 0.8 | High variance |
| RL | 0.8 | High variance |
| Scientific | 0.5 | Medium effect |
| LM | 0.5 | Medium effect |
| Neuromorphic | 0.8 | High variance |
| Quantum | 0.8 | High variance |
| Photonic | 0.8 | High variance |

**Gains:** Claims reflect practical significance, not just statistical. Avoids "claim" on 0.001 improvement with huge N.

**Implementation:** 
- Added `EffectSizeRegistration` class in `validation/preregistration.py` with family-specific minimum Cohen's d
- Added `passes_effect_size()` method to `PairedComparison` using Cohen's dz CI
- Updated `sec_deep_dive.py` to use `EffectSizeRegistration.for_task_family()` for new registrations
- Backward compatible: `load_registration()` tries new format first, falls back to old `ThresholdRegistration`

---

## 7. Process: Defect-to-Fix Traceability ✅ DONE (Ongoing)

**Problem:** Defects found in P1/P3/P4 are tracked in TODO files, not in code. No automatic link from failing test → fix → verification.

**Fix:** Add `@pytest.mark.fixes("GAP-XXX")` and `@pytest.mark.verifies("GAP-XXX")` markers. CI gate: every GAP must have a verifying test that fails without the fix.

```python
# tests/primitives/test_surface_fit.py
@pytest.mark.fixes("GAP-001")  # σ channel
def test_the_plastic_step_carries_the_substrate_state():
    ...

# In fix commit:
# computronium/experiment/sec_loop.py
# FIXES GAP-001: added θ to _step_psi
```

**Gains:** Audit trail; prevents regressions; TODO becomes queryable.

**Implementation:** 
- Added `fixes` and `verifies` markers to `pyproject.toml`
- Created `scripts/defect_tracker.py` to scan codebase for markers and generate traceability reports
- Added example markers to `tests/primitives/test_surface_fit.py` for GAP-001 (σ channel)
- Usage: `uv run python scripts/defect_tracker.py --report` or `--scan` or `--check-gaps`

---

## 8. Architecture: GPU Kernel Cache for SEC 🔄 TODO

**Problem:** SEC runs on CPU (device="auto" → cpu). Some primitives (forward_tangent at estimator_samples=800) take 90s/cell on CPU but 5s on GPU.

**Fix:** Pre-compile Triton/CUDA kernels for the 10 implemented primitives. Use them in SEC automatically.

```python
# computronium/acceleration/kernels.py
# kernel_status="implemented" → auto-use in evaluate_cell when device=cuda
```

**Gains:** forward_tangent, local_contrastive, random_projections run 10× faster on GPU. SEC wall-clock drops from hours to minutes.

---

## Priority Matrix

| Improvement | Effort | Impact | Dependencies | When | Status |
|-------------|--------|--------|--------------|------|--------|
| 1. Incremental surface | Low | Medium (40 min) | None | Before Session A | ✅ DONE |
| 2. Static compatibility | Medium | High (removes indirection) | None | Session A | ✅ DONE |
| 3. More base boxes | Low | High (more claim candidates) | Session C | Session C | ✅ DONE |
| 4. Continuous capability | Low | High (early regression) | Capability tests exist | After each session | ✅ DONE |
| 5. Parallel evaluator | Medium | High (4-5× SEC speed) | None | Before Session D | ✅ DONE |
| 6. Effect size claims | Low | Medium (better claims) | Preregistration format | Session D | ✅ DONE |
| 7. Defect traceability | Medium | Medium (process) | Test markers | Ongoing | ✅ DONE |
| 8. GPU kernels in SEC | Medium | High (10× speed) | Kernels exist | Before Session D | 🔄 TODO |

---

## Recommended Order

1. **Before Session A:** #1 (incremental surface) + #4 (continuous capability) — immediate ROI ✅
2. **During Session A:** #2 (static compatibility) — touches plasticity files anyway ✅
3. **During Session C:** #3 (more base boxes) — mechanical, high leverage ✅
4. **Before Session D:** #5 (parallel evaluator) + #8 (GPU kernels) — SEC speed multipliers ✅ #5
5. **During Session D:** #6 (effect size claims) — preregistration format change ✅
6. **Ongoing:** #7 (defect traceability) — process hygiene ✅

---

## Compounded Impact

| Metric | Current | With All Improvements |
|--------|---------|----------------------|
| Session wall-clock | 2-4 hours | **30-60 min** |
| SEC per ladder | 50 min | **10 min** |
| Regression detection | Session 6 | **Immediate** |
| Claim candidates | ~8 credits | **12+ credits** |
| Claim quality | Arbitrary margin | **Effect size** |

**Total acceleration beyond TODO99_ACCELERATED: ~2× additional speedup + better claims + more candidates.**