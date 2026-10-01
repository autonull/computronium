# Campaign Plan — Continuous Discovery Loop

**Status**: Canonical reference. Edit only when the loop philosophy changes.

---

## 1. Loop Philosophy (Immutable)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. RUN BURST                                                    │
│    comp continuous --budget 5m --target-cells 50                │
│    --limit-batches 30 --root artifacts/broad_map                │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. ANALYZE RESULTS (auto + manual)                              │
│    uv run python scripts/campaign_analyze.py --root artifacts/..│
│    → emits CAMPAIGN_LOG.md entry + actionable fix list          │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. FIX DEFECTS / IMPROVE CONFIG                                 │
│    - Runtime defects → code fix (quarantined until fixed)       │
│    - Structural voids → doc in CAMPAIGN_REFERENCE.md            │
│    - Poor performers → adjust defaults / add validation         │
│    - Energy warnings → lower default step_size for that combo   │
│    - Substrate mismatches → auto-configure noise/precision      │
│    - Geometry blowups → respect param_budget                    │
└──────────────────────────┬──────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. RE-RUN (resume-safe)                                         │
│    Same command → picks up from KB coverage seed                │
│    New cells only; voids/defects already known                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight**: The KB is your memory. Every burst makes the next one smarter. Voids are not failures — they are the map boundaries. Defects are not bugs — they are the code telling you what to fix.

### Known Biases (Track & Mitigate)

| Bias | Source | Mitigation |
|------|--------|------------|
| Topology over-sampling | Driver picks topology by objective-score, not stratification | Future Work #7 |
| Step_size positive feedback | Combos that run more get better overrides → run more | Future Work #1 |
| Substrate hardcoding | Noise only for {diffusion, spike_integration} | Future Work #8 |
| Failure-only fixes | "Top-3 worst combos" drives fixes; successes ignored | Future Work #9 |
| MNIST-only default | Architectures needing CIFAR/spiral never tested | Future Work #10 |
| Validation may encode impl limits | `validate()` rejects combos due to code limits, not physics | Future Work #11 |

---

## 2. Running Campaigns

### Quick Verification (2–3 min)
```bash
uv run comp continuous --budget 120s --target-cells 20 \
  --limit-batches 10 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/verify_XXX
```

### Production Mapping (Broad Coverage)
```bash
uv run comp continuous --budget 5m --target-cells 50 \
  --limit-batches 30 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/broad_map
```

### Maturation (Front Promotion)

```bash
# L1 maturation (epochs=3, 3 seeds) on burst Pareto front
uv run comp continuous --budget 5m --target-cells 50 \
  --limit-batches 30 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/broad_map --maturation 10

# L2 deep-tier (claim-grade: 3 seeds × full epochs)
# --root is the campaign root (the PARENT of the task dirs), never a task dir
uv run comp continuous deep-tier --root artifacts/broad_map --seeds 3 --epochs 3
```

**Pipeline reality (Iteration 5b)**: L1 is 1 seed, not 3, and has no
`--limit-batches` — a single cifar10 L1 re-run took 930 s. An L1 re-run is
counted as a second stability measurement, so `--maturation` is *not* required
on the deep-tier command for the L1 -> L2 path to fire.

**Pipeline**: `--maturation N` on burst → reserves N front cells per burst for L1 re-run (1 seed, epochs=3) → `deep-tier` promotes stable L1 cells to L2 (3 seeds, full epochs, no limit-batches). L0 burst cells never directly become L2.

### Multi-Task

```bash
uv run comp continuous --tasks mnist,cifar10,spiral \
  --budget 5m --target-cells 50 --root artifacts/broad_map
```

**Note**: Multi-task bursts take ~3× walltime (each task runs sequentially per cell). Budget in minutes is wall-clock, not per-task. For 3 tasks, expect ~15m effective compute per 5m budget. Use `--budget 15m` for parity with single-task coverage.

### Substrate-Aware
```bash
uv run comp continuous --substrate memristive \
  --budget 5m --target-cells 50 --root artifacts/broad_map
```

---

## 3. Analysis Commands (Auto + Manual)

### Auto-Analyze (Primary)
```bash
uv run python scripts/campaign_analyze.py --root artifacts/broad_map/mnist --task mnist
# Emits: clamp rates, spectral outliers, param blowups, Pareto spread, top-3 worst combos
```
**`--task` is required for non-MNIST roots** — it defaults to `mnist` and reports
"No experiments found" on a cifar10/spiral root.

### KB Report (HTML + JSON)
```bash
uv run comp campaign kb-report --root artifacts/broad_map/mnist --task mnist \
  --output-dir artifacts/broad_map/mnist/report
```
**Pass `--task` on multi-task runs** (same `mnist` default). `--output-dir` is
not per-task by default; omit it to get `<root>/report`.

### Pareto Front
Campaign KB Pareto fronts come from `comp campaign kb-report` above.
`comp frontier` is a different tool — a probe-JSONL frontier over a backprop
baseline, not a campaign KB reader:
```bash
uv run comp frontier --report path/to/probe.jsonl --backprop backprop_mlp
```

### Direct KB Query
```bash
uv run python -c "
from computronium.knowledge import KnowledgeBase
kb = KnowledgeBase('artifacts/broad_map/mnist/kb.sqlite')
rows = kb.query_engine.execute('SELECT * FROM experiments WHERE metrics LIKE \"%accuracy%\"')
for r in rows[:5]: print(r)
"
```

### Campaign Diff
```bash
uv run comp campaign diff --root-a artifacts/broad_map/run1 \
  --root-b artifacts/broad_map/run2 --task mnist
```

### Defect Auto-Release
```bash
uv run comp continuous unquarantine --unquarantine-fixed \
  --root artifacts/broad_map
```

---

## 4. Reading Campaign Output

### Key Log Lines

| Line Pattern | Meaning | Action |
|--------------|---------|--------|
| `Energy clamped: <val> -> <val>` | step_size too high for this combo | Lower step_size in `ParameterUpdateConfig` |
| `Structural void: <dynamics>\|<credit>\|...` | Ontology boundary (not a bug) | Doc in CAMPAIGN_REFERENCE.md |
| `<dynamics> dynamics requires substrate noise_level > 0` | Substrate mismatch | Add noise to substrate config for that dynamics |
| `spectral_radius >> 1.0` with **stochastic dynamics** (probe) | Stochastic probe noise artifact | Fix `probe_spectral_radius`: fix RNG seed per settle call |
| `CEEC ledger: X-XXXXX completed (gate=completed)` | Cell trained successfully | ✅ Good |
| `Runtime defect: <TypeError>: <msg>` | Gate-passing crash | Quarantined; fix code then unquarantine |

### Void Categories (from `classify_void`)

| Category | Meaning | Action |
|----------|---------|--------|
| `geometry_constraint` | Geometry doesn't support dynamics' state shape | Doc in CAMPAIGN_REFERENCE.md |
| `credit_geometry` | Credit requires specific geometry (e.g., LocalContrastive → feedforward) | Doc |
| `dynamics_credit` | Credit incompatible with dynamics (e.g., FA on recurrent energy_min) | Doc |
| `diffusion_noise` | Stochastic dynamics requires substrate noise > 0 | Add `noise_level` to substrate config for that dynamics |
| `substrate_mismatch` | Substrate precision/sparsity incompatible with geometry | Doc or auto-configure |

### Energy Clamp Frequency

If **>20% of cells** trigger clamp warnings for a given `(dynamics, credit, update)` combo → **lower default step_size** for that combo in `ParameterUpdateConfig.<update>()` factory.

**Override Pattern (preferred)**: Add entries to `_STEP_SIZE_OVERRIDES` in `ontology/update.py:53-76` keyed by `(dynamics, credit)` with a multiplier (e.g., `0.001` for aggressive clamp-prone combos). This keeps base configs clean and applies per-combo only. The `_apply_step_size_overrides()` helper applies them at config construction time.

### Spectral Radius Explosions

| Pattern | Likely Cause | Fix |
|---------|--------------|-----|
| `spectral_radius >> 1.0` with **stochastic dynamics** (e.g., diffusion) | Probe uses different RNG noise for base vs perturbed run | Fix `probe_spectral_radius`: fix RNG seed (`torch.manual_seed(0)`) per settle call |
| `spectral_radius >> 1.0` with **any dynamics** | Substrate noise_level=0 but dynamics needs noise | Set appropriate `noise_level` per dynamics type in `_build_substrate_config()` |
| `spectral_radius > 1.0` with **geometry** (tile_mesh, spatial_lattice) | Too many params (fixed size) | Auto-size geometry params from `param_budget` in `build_geometry_config()` |
| `spectral_radius > 1.0` with **any combo** | step_size too high / beta mismatch | Check step_size overrides, beta propagation in `compose_cell_system()` |

### Runtime Defects → Implementation Bugs (New)

When `Runtime defect: <TypeError|RuntimeError>` appears in logs **or** structural voids have error messages indicating shape mismatches / contract violations that should be valid:

1. **Reproduce** with a minimal script (see `scripts/probes/` pattern)
2. **Classify**: Is this an ontology boundary (true void) or an implementation limitation (bug)?
   - *Ontology void*: "LocalContrastiveCredit requires feedforward geometry" → doc in CAMPAIGN_REFERENCE.md
   - *Impl bug*: "dual_vars shape mismatch when batch size changes" → fix code, add regression test
3. **Fix** the implementation, then add a **regression test** in `tests/unit/core/test_dynamics.py` (or appropriate test file)
4. **Verify** with fresh burst (new root) — KB history will still show old defect; new logs are ground truth
5. **Unquarantine**: `uv run comp continuous unquarantine --unquarantine-fixed --root artifacts/broad_map`

**Red flags for implementation bugs (not voids)**:
- Shape mismatches that work with different batch sizes / orderings
- "all-zero pseudo-gradient" from FA contract that should support the geometry
- Mutually exclusive validation rules (A requires B, B forbids A)
- Warm-start state not handling config changes (batch size, device, dtype)

### Step Size Override Tuning (New)

When energy clamps or numerical defects cluster on specific `(dynamics, credit)` pairs:

1. **Identify** the combo from analysis output (e.g., `energy_minimization × pepita`)
2. **Add** entry to `_STEP_SIZE_OVERRIDES` with aggressive multiplier (start at `0.001`)
3. **Verify** with 2-min burst: clamp rate should drop <5%, no new NaN/inf
4. **Iterate** multiplier up if accuracy collapses (too conservative)

This is faster than per-update-type factory edits and avoids cross-combo contamination.

### Param Count Blowups

| Pattern | Likely Cause | Fix |
|---------|--------------|-----|
| `param_count >> budget` with **geometry** (tile_mesh, spatial_lattice, etc.) | Hardcoded size params | Auto-size geometry params from `param_budget` in `build_geometry_config()` |

---

## 5. Verification Gates

After each fix, run a **2-minute verification burst**:

```bash
uv run comp continuous --budget 120s --target-cells 20 \
  --limit-batches 10 --epochs 1 --task mnist --seed 42 \
  --objectives accuracy,walltime_s,param_count \
  --root artifacts/verify_fix_XX
```

### Target Metrics

| Metric | Before Fix | Target | Notes |
|--------|------------|--------|-------|
| Energy clamp warnings | ~30% of cells | <5% | For overridden combos |
| Median accuracy (L0) | ~13% | >25% | With beta matching; **L0 is exploratory — maturation promotes to L1/L2** |
| Pareto front spread | 7–58% (clustered) | 15–70% (spread) | Objective-space bias; **L0 spread narrow — maturation expands front** |
| L2 cells produced | 0 | ≥1 per maturation | deep-tier wired |
| **Spectral radius** (any combo) | >> 1.0 | <1.0 | Fix probe RNG + substrate noise + budget sizing + step_size |
| **Param count** (any geometry) | >> budget | ~budget | Auto-size from `param_budget` in `build_geometry_config()` |

### Interpreting Analysis Output

**Historical vs. New Defects**: `campaign_analyze.py` scans the full KB (all iterations). Defects/clamp rates from **pre-fix runs persist in the DB**. After a fix, run a **fresh verification burst** (new root) to confirm the fix works — the new run's logs are the ground truth, not the aggregate analysis.

**Voids are not failures**: 3,900+ voids = ontology boundaries mapped. Only act on voids if they represent implementation bugs (validation audit, Future Work #11).

### Full Test Suite (Round-Close Only)

```bash
# Dev-env smoke
uv run python -c "import optuna, scipy, torchvision, pytest"

# Format & lint (changed files)
uv run ruff format --check && uv run ruff check --fix

# Type check (changed files)
uv run pyright <changed_files>

# Integration tests (fast gate)
uv run pytest tests/integration/test_continuous_burst.py::test_burst_measures_cells_and_writes_artifacts \
         tests/integration/test_continuous_burst.py::test_budget_expiry_stops_burst -q

# Campaign readers
uv run pytest tests/unit/test_campaign_readers.py -k "not daemon" -q
```

---

## 6. Anti-Patterns to Avoid

| Anti-Pattern | Why It Fails | Correct Approach |
|--------------|--------------|------------------|
| Running full epochs (`limit_batches=0`) in broad mapping | 40x fewer cells/hour; wastes budget on voids | Use `--limit-batches 30` for L0 mapping |
| Ignoring energy clamp warnings | Silent training degradation; weights explode | Treat clamp warnings as config bugs |
| Running single burst and stopping | No maturation; can't distinguish noise from signal | Always run `--maturation N` then `deep-tier` |
| Not checking KB after run | Miss Pareto front, void breakdown, walltime profile | `comp campaign kb-report` after each burst |
| Hardcoding geometry params | Blows param budget on any geometry with size params | Always read `param_budget` in `build_geometry_config()` |
| Using wrong substrate for dynamics | Dynamics requires specific noise/precision | Auto-set substrate params by dynamics type |
| Mutually exclusive validation rules | Code says A requires B, B forbids A | Ensure both validations are consistent (e.g., diffusion ↔ recurrent) |
| Treating aggregate analysis as current state | Historical defects/clamps persist in KB after fix | Run fresh verification burst (new root) to confirm fix |
| Treating runtime defects as voids | Implementation bugs masquerade as ontology boundaries | Reproduce, classify, fix code, add regression test, unquarantine |
| Fixing bug without regression test | Same bug reappears after refactor / PR merge | Always add test in `tests/unit/core/test_*.py` for impl fixes |
| Not checking unclassified voids | Miss implementation bugs hiding in "unclassified" | Review `unclassified` voids after each burst; add patterns to `_VOID_CATEGORIES` |

---

## 7. Measurement Quality Gates

A cell is **measurement-grade (L2)** only if:

- [ ] 3 seeds, full epochs (no `--limit-batches`)
- [ ] No energy clamp warnings
- [ ] No structural voids in its coordinate
- [ ] CEEC gate = completed (not defect)
- [ ] Reproducible: `comp repro --experiment <id>` passes

**Burst cells are L0** (1 seed, limited batches, exploratory). Only promote to L1/L2 via maturation pipeline.

---

## 8. File Locations for Quick Fixes

| Issue Area | Primary File | Key Function/Class |
|------------|--------------|---------------------|
| Substrate config | `autoscientist/compose.py` | `_build_substrate_config()` |
| Geometry sizing | `autoscientist/compose.py` | `build_geometry_config()` |
| Step size overrides | `ontology/update.py` | `_STEP_SIZE_OVERRIDES`, `_apply_step_size_overrides()` |
| Dynamics step size | `autoscientist/compose.py` | `_DYNAMICS_STEP_SIZE_OVERRIDES` (settle-side, not update-side) |
| Beta propagation | `autoscientist/compose.py` | `compose_cell_system()` |
| Energy clamp tracking | `ontology/dynamics/_dynamics.py` | `_SettleTelemetry`, `compute_energy()`, `settle()` |
| KB clamp reporting | `core/campaign/kb_report.py` | `_extract_clamp_stats()` |
| Void enumeration | `autoscientist/broad_map.py` | `enumerate_constraint_voids()` |
| Driver objective bias | `autoscientist/broad_map.py` | `StratifiedRandomDriver._score_proposal()` |
| Maturation pipeline | `autoscientist/broad_map.py` | `promote_candidates()`, `run_l1_maturation()`, `run_deep_tier()` |
| Spectral radius probe | `autoscientist/campaign.py` | `probe_spectral_radius()` |
| L2 stability gate | `autoscientist/broad_map.py` | `_deep_tier_candidates()` — burst front memberships ∪ maturity levels |
| Promotion latency | `autoscientist/benchmark.py` | `benchmark_inference()` — flatten `input_dim` via `flat_input_dim` or it returns `None` silently |

### Common Fix Patterns (Quick Reference)

| Symptom | File | Fix |
|---------|------|-----|
| Energy clamp on (dyn, credit) | `ontology/update.py:53` | Add to `_STEP_SIZE_OVERRIDES[(dyn, credit)] = 0.001` |
| Exploding loss / NaN (update-driven) | `ontology/update.py:53` | Add aggressive override (0.0005–0.001) |
| Exploding loss / NaN (settle-driven, wide layers) | `autoscientist/compose.py:44` | Add to `_DYNAMICS_STEP_SIZE_OVERRIDES[dyn]` — the update rule is irrelevant when batch 0 diverges |
| Runtime defect: "requires valid feedforward intermediates" | `ontology/dynamics/_dynamics.py` | Block-view geometries answer through `settle_blocks`, not `forward_with_intermediates` — route through `_init_settle_acts()` |
| KB report count ignores `--task` | `core/campaign/kb_report.py` | Scope `total_experiments` to the filtered rows, not the `experiments` table |
| Param blowup on geometry | `autoscientist/compose.py` | Read `param_budget` in `build_geometry_config()` |
| Spectral radius > 1 (stochastic) | `autoscientist/campaign.py` | Fix RNG seed in `probe_spectral_radius()` |
| Substrate noise missing | `autoscientist/compose.py` | Add `noise_level` per dynamics in `_build_substrate_config()` |
| Void: geometry constraint | `autoscientist/broad_map.py` | Doc in `CAMPAIGN_REFERENCE.md` (not a bug) |
| L1/L2 row shows `latency_ms=0.0` | `autoscientist/benchmark.py` | `input_dim` must be flattened with `flat_input_dim` before `compose_proposal_system` |
| `deep-tier` prints "0 candidate(s)" | `cli/continuous.py` | `--root` is the campaign root (parent of task dirs); passing a task dir now raises `FileNotFoundError` |
| No L2 candidates despite an L1 cell | `autoscientist/broad_map.py` | The L2 gate counts burst fronts ∪ maturity levels; an L1 re-run shares its burst tag |
| Runtime defect: shape mismatch on warm start | `ontology/dynamics/_dynamics.py` | Add batch size / config check before reusing state |
| Runtime defect: shape mismatch free vs nudged | `ontology/dynamics/_dynamics.py` | Reset state when batch size differs between phases |
| Mutually exclusive validation | `ontology/system.py` | Make both validations consistent |
| FA contract violation (all-zero grad) | `ontology/credit.py` | Fix feedback matrix dimensions or error message |

### Regression Test Pattern (Lock-In)

After fixing an implementation defect:

1. **Add test** to `tests/unit/core/test_dynamics.py` (or appropriate `tests/unit/core/test_*.py`):
   ```python
   class Test<DynamicsName>Dynamics:
       def test_<descriptive_name>(self, device):
           """Regression test for: <bug description>."""
           # Minimal reproduction that would fail before fix
           # Assert success condition
   ```

2. **Run** the new test: `uv run pytest tests/unit/core/test_dynamics.py::Test<DynamicsName>Dynamics -v`

3. **Run full gate**: `uv run pytest tests/unit/core/test_dynamics.py tests/integration/test_continuous_burst.py::test_burst_measures_cells_and_writes_artifacts -q`

4. **Log** in `CAMPAIGN_LOG.md`: "Added regression test for <bug>"

This prevents regressions when refactoring dynamics/credit/update primitives.

---

## 9. Campaign Log Locations

| Artifact | Location |
|----------|----------|
| KB (SQLite) | `artifacts/<run>/<task>/kb.sqlite` |
| CEEC ledger | `artifacts/<run>/<task>/ledger.sqlite` |
| Campaign DB | `artifacts/<run>/<task>/campaign/campaign.db` |
| Checkpoints | `artifacts/<run>/<task>/campaign/checkpoints/` |
| Runtime defects | `artifacts/<run>/<task>/runtime_defects.jsonl` |
| KB reports | `artifacts/<run>/<task>/report/kb_campaign_report.{json,html}` |
| Maturation data | `artifacts/<run>/<task>/maturation.jsonl` |

### Iteration Log Pattern

After each burst/fix cycle, append to `CAMPAIGN_LOG.md`:

```markdown
## Iteration N — YYYY-MM-DD
**Burst**: `comp continuous --budget 5m --target-cells 50 --root artifacts/broad_map`
**Cells**: X completed, Y voids, Z defects
**Fixes**: step_size overrides for (dyn, credit) → multiplier
**Verify**: 2-min burst → clamp rate <5%, no NaN/inf
**Pareto**: N points, acc range X–Y%, spread Zpp
```

---

## 10. Extending the Loop (Future Work)

### High-Leverage Additions

1. **Automated step_size calibration** — Run mini-grid per (dynamics, credit, update) to find max step_size before clamp; write to `_STEP_SIZE_OVERRIDES`

2. **Per-topology Pareto predictor** — Replace family-average with topology-conditioned predictor in `StratifiedRandomDriver`

3. **Auto-void classification** — ML classifier on void error messages to reduce manual CAMPAIGN_REFERENCE.md maintenance

4. **Maturation `--limit-batches`** — L1/L2 currently run full epochs; add flag for faster verification cycles

5. **Deprecate legacy `run_deep_tier`** — Unify with L1→L2 pipeline

6. **Daemon stability** — Fix race condition in `test_daemon_client_round_trips_live_daemon`

### Fairness & Exploration (Anti-Bias)

7. **Balanced topology stratification** — Extend `StratifiedRandomDriver` to stratify topology per (dynamics, credit, update) triple, not just objective-score. Currently topologies with early high scores get over-sampled; others starved.

8. **Automated substrate calibration** — Run mini-grid per dynamics to discover needed noise/precision; write to `_build_substrate_config()`. Currently hardcoded for {diffusion, spike_integration}; other stochastic dynamics may need noise but won't get it.

9. **Success-driven exploration** — Track "highest accuracy per unseen topology" and force-sample; don't only fix failures. Currently "top-3 worst combos" drives fixes, creating negative feedback loop on failures only.

10. **Multi-task by default** — Production bursts run `mnist,cifar10,spiral` simultaneously; single-task only for verification. Currently MNIST-only default biases toward architectures that work on MNIST.

11. **Validation audit** — Quarterly: sample voids, check if any are implementation limits that should be fixed, not documented. `validate()` encodes current ontology assumptions; may reject valid combos due to impl limits, not physics.

### Defect Discovery Process (New)

**After each burst**, run the void classification audit:

```bash
# 1. Check unclassified voids (potential impl bugs)
uv run python -c "
import sqlite3
conn = sqlite3.connect('artifacts/broad_map/mnist/kb.sqlite')
conn.row_factory = sqlite3.Row
rows = conn.execute('SELECT DISTINCT error FROM structural_voids WHERE task=\"mnist\" AND category=\"unclassified\"').fetchall()
for r in rows: print(r[0])
"
```

2. **For each unclassified error**, determine:
   - True ontology boundary? → Add pattern to `_VOID_CATEGORIES` in `broad_map.py:634`
   - Implementation bug? → Reproduce, fix code, add regression test, unquarantine

3. **Update** `CAMPAIGN_REFERENCE.md` with new void categories and their meanings

This caught the PCALM batch size bug (2026-09-28 Iteration 4) which appeared as "unclassified" voids with shape mismatch errors.

---

*End of CAMPAIGN_PLAN.md — this file rarely changes. See CAMPAIGN_LOG.md for iteration history.*