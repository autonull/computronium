# TODO87 — System Fixes & Remaining Coverage (Post-TODO86)

**Status:** Core experiment loop working; geometry/trainer mismatches block graph classification and causal_transformer.

---

## 🎯 PHASE 1: Fix Graph Classification Support

**Problem:** `GraphGeometry.forward(x, substrate)` only supports node classification (single graph, edge_index stored in geometry). Graph classification needs `forward(x, edge_index, batch)` for batched graphs from DataLoader.

**Root cause:** `GraphGeometry` (ontology/geometry.py:2169) has fixed signature. `GraphSystemTrainer` now detects both modes but geometry doesn't.

**Fix options:**
1. Make `GraphGeometry.forward` polymorphic: detect args (if 3 args → graph classification mode)
2. Add `GraphClassificationGeometry` as separate primitive
3. Store edge_index/batch in geometry config at compose time (not viable for batched)

**Recommended:** Option 1 — add optional `edge_index, batch` params to `forward()`, use stored buffers when not provided.

**Validation:** `digital/graph/instant/random_projections/euclid` on `graph_classification` (MUTAG) should PASS at L0.

---

## 🎯 PHASE 2: Fix CausalTransformer for Vision (Patch Embedding)

**Problem:** `causal_transformer` geometry expects 1D token sequence. Vision tasks (MNIST, CIFAR) need patch embedding to convert 2D→1D.

**Status:** B3c blocked; also affects any vision task using causal_transformer.

**Fix:** Add `patch_embedding` config to `CausalTransformerGeometry`:
- `patch_size`: int (e.g., 4 for 28×28 → 7×7 patches)
- `embed_dim`: int (projection dim)
- In `forward()`: rearrange (B, C, H, W) → (B, N_patches, patch_dim) → project → transformer

**Dependencies:** Needs `einops` or manual rearrange.

**Validation:** `digital/causal_transformer/instant/grad/euclid` on MNIST should compose and train.

---

## 🎯 PHASE 3: Complete Remaining Baselines

### B1b — Pendulum Baseline
- `digital/ff/instant/null/grad/euclid` on `pendulum` @ L0/L1
- Continuous action space; verify RLSystemTrainer handles Box actions

### B1c-alt Extended — Acrobot
- `digital/recurrent/instant/random_projections/euclid` on `acrobot` @ L0
- Discrete action space (3 actions)

### B4a — Tabular Fixes
- **wine**: 0.0 acc all seeds — investigate normalization / class mapping
- **iris**: high seed variance (0.07–0.53) — rerun with more epochs/seeds

---

## 🎯 PHASE 4: Infrastructure Hardening

| Item | Description | Priority |
|------|-------------|----------|
| GraphGeometry polymorphic forward | Support both node + graph classification | High |
| CausalTransformer patch embedding | Unblocks vision + sequence | High |
| Wine/iris tabular debug | Fix baselines | Medium |
| Per-step logging CLI flag | `--log-steps N` exposes step-level progress | Low |
| SIGTERM run closure | Write manifest on graceful shutdown | Low |

---

## 🎯 PHASE 5: Scale Validation (Deferred from TODO86)

| Experiment | Axes | Budget | Status |
|------------|------|--------|--------|
| C2 | digital/ff/energy_min/null/grad/adam | 2h | Needs settling-sized budget |
| C4 | memristive/ff/energy_min/null/grad/adam | ~1h | CPU-bound; needs optimize or accept |

---

## 🔄 EXPERIMENT LOOP (Same)

```bash
# 1. RUN
uv run python -m computronium.experiment.survey_cli 0.25 \
  --policy tpe --device cuda \
  --tasks <task_list> \
  --axes '<axis_json>'

# 2. ANALYZE (30s)
uv run comp report --store experiments/<latest>.duckdb --format text
uv run comp coverage report --store experiments/<latest>.duckdb
cat experiments/<latest>.run.json

# 3. FIX (≤15 min) — infrastructure only
# 4. VERIFY (0.02h, no ladder)
# 5. COMMIT + LOG
```

---

## 📋 PRIORITY ORDER

1. **GraphGeometry polymorphic forward** — unblocks graph_classification
2. **CausalTransformer patch embedding** — unblocks B3c, vision transformers
3. **B1b pendulum + B1c-alt acrobot** — complete RL baselines
4. **B4a wine/iris fix** — complete tabular baselines
5. **C2/C4 scale** — GPU validation at scale

---

## ⚠️ OPEN TECHNICAL ISSUES

- **GraphGeometry.forward signature**: Must handle both `(x, substrate)` and `(x, edge_index, batch)` without breaking existing node classification.
- **CausalTransformer input handling**: Currently expects 1D; needs automatic patchify for 2D/3D inputs.
- **wine task**: All seeds 0.0 — likely StandardScaler + class mapping issue in TabularTask.
- **iris task**: High variance — may need more epochs (50+) or more seeds (10+) for stable estimate.
- **Energy minimization + recurrent**: ~120s/cell at L0 due to settle loop per env step — document as known limitation.
- **run_experiment.py val_acc=0.0000 bug**: All cells PASS but report zero accuracy (gate checks finite metrics, not learnability). Same root cause as wine/iris — metric extraction broken in async path.
- **Two experiment engines**: `survey_cli.py` (canonical, fixed) vs `run_experiment.py` (legacy, unfixed). Need deprecation plan.

---

## 🎯 PHASE 6: Consolidate Experiment Entry Points

**Problem:** Two separate experiment execution engines exist:

| Entry Point | Path | Architecture | Status |
|-------------|------|--------------|--------|
| `survey_cli.py` | `python -m computronium.experiment.survey_cli` | Sequential, wave-based, planners | **Canonical** (fixed, tested) |
| `run_experiment.py` | `python scripts/run_experiment.py` | Async, CellStream, LocalBackend | **Legacy** (unfixed bugs) |
| `experiment.sh` | `./experiment.sh` | Bash wrapper → run_experiment.py | **Legacy** |

**Issues in `run_experiment.py` path (found during quick-verify test):**
- **val_acc=0.0000 bug**: All cells PASS but report zero accuracy (same as wine/iris issue)
- **No dry-run composable filtering**: Invalid cells proposed and evaluated
- **No per-epoch heartbeat**: Silent long runs
- **No seed-plan expansion**: `--n-seeds 3` writes 1 record, not 3
- **No task-aware replication key**: Seeds across tasks fuse
- **Async + LocalBackend**: Different semantics (max_workers=1 but async overhead)
- **No honest wave sizing**: Uses policy directly, no cost model

**Recommendation:** Deprecate `scripts/run_experiment.py` and `experiment.sh`. All new work uses `survey_cli.py`. 

**Migration:**
1. Verify `survey_cli.py` covers all `run_experiment.py` use cases (profiles, policies, axes)
2. Add `--mode learn|static` flag parity for `run_experiment.py --policy`
3. Delete `scripts/run_experiment.py`, `experiment.sh`, `experiment_shallow.sh` (already deleted)
4. Update docs/TODOs to reference only `survey_cli.py`

---

## 🚫 NO (Same as TODO86)

- Paper figures
- Publishing artifacts
- Hypothesis backlogs
- Preventive fixes
- Meetings/retrospectives
- Cycles > 30 min