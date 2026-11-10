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

---

## 🚫 NO (Same as TODO86)

- Paper figures
- Publishing artifacts
- Hypothesis backlogs
- Preventive fixes
- Meetings/retrospectives
- Cycles > 30 min