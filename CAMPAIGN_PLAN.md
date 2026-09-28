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
uv run comp continuous deep-tier --root artifacts/broad_map --maturation 10
```

### Multi-Task
```bash
uv run comp continuous --tasks mnist,cifar10,spiral \
  --budget 5m --target-cells 50 --root artifacts/broad_map
```

### Substrate-Aware
```bash
uv run comp continuous --substrate memristive \
  --budget 5m --target-cells 50 --root artifacts/broad_map
```

---

## 3. Analysis Commands (Auto + Manual)

### Auto-Analyze (Primary)
```bash
uv run python scripts/campaign_analyze.py --root artifacts/broad_map/mnist
# Emits: clamp rates, spectral outliers, param blowups, Pareto spread, top-3 worst combos
```

### KB Report (HTML + JSON)
```bash
uv run comp campaign kb-report --root artifacts/broad_map/mnist \
  --output-dir artifacts/broad_map/report
```

### Pareto Front
```bash
uv run comp frontier --study broad_mapping_sweep \
  --db artifacts/broad_map/mnist/kb.sqlite
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

### Spectral Radius Explosions

| Pattern | Likely Cause | Fix |
|---------|--------------|-----|
| `spectral_radius >> 1.0` with **stochastic dynamics** (e.g., diffusion) | Probe uses different RNG noise for base vs perturbed run | Fix `probe_spectral_radius`: fix RNG seed (`torch.manual_seed(0)`) per settle call |
| `spectral_radius >> 1.0` with **any dynamics** | Substrate noise_level=0 but dynamics needs noise | Set appropriate `noise_level` per dynamics type in `_build_substrate_config()` |
| `spectral_radius > 1.0` with **geometry** (tile_mesh, spatial_lattice) | Too many params (fixed size) | Auto-size geometry params from `param_budget` in `build_geometry_config()` |
| `spectral_radius > 1.0` with **any combo** | step_size too high / beta mismatch | Check step_size overrides, beta propagation in `compose_cell_system()` |

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
| Beta propagation | `autoscientist/compose.py` | `compose_cell_system()` |
| Energy clamp tracking | `ontology/dynamics/_dynamics.py` | `_SettleTelemetry`, `compute_energy()`, `settle()` |
| KB clamp reporting | `core/campaign/kb_report.py` | `_extract_clamp_stats()` |
| Void enumeration | `autoscientist/broad_map.py` | `enumerate_constraint_voids()` |
| Driver objective bias | `autoscientist/broad_map.py` | `StratifiedRandomDriver._score_proposal()` |
| Maturation pipeline | `autoscientist/broad_map.py` | `promote_candidates()`, `run_l1_maturation()`, `run_deep_tier()` |
| Spectral radius probe | `autoscientist/campaign.py` | `probe_spectral_radius()` |

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

---

*End of CAMPAIGN_PLAN.md — this file rarely changes. See CAMPAIGN_LOG.md for iteration history.*