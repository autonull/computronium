# TODO87 — System Fixes & Remaining Coverage (Post-TODO86)

**Status:** PHASE 1 & 2 COMPLETE. Graph classification and CausalTransformer vision support working. Remaining: baselines, tabular fixes, infrastructure hardening, scale validation.

---

## 🎯 PHASE 1: Fix Graph Classification Support — ✅ COMPLETE

**Problem:** `GraphGeometry.forward(x, substrate)` only supports node classification (single graph, edge_index stored in geometry). Graph classification needs `forward(x, edge_index, batch)` for batched graphs from DataLoader.

**Root cause:** `GraphGeometry` (ontology/geometry.py:2169) has fixed signature. `GraphSystemTrainer` now detects both modes but geometry doesn't.

**Fix implemented:** Made `GraphGeometry.forward` polymorphic with optional `edge_index, batch` params. Added `settle_blocks` for dynamics integration. Updated pipeline to pass extra args through `dynamics.settle`. Added `global_mean_pool` for graph-level readout.

**Validation:** `digital/graph/instant/random_projections/euclid` on `graph_classification` (MUTAG) — forward pass and training verified working. Node classification (Cora) backward compatibility confirmed.

---

## 🎯 PHASE 2: Fix CausalTransformer for Vision (Patch Embedding) — ✅ COMPLETE

**Problem:** `causal_transformer` geometry expects 1D token sequence. Vision tasks (MNIST, CIFAR) need patch embedding to convert 2D→1D.

**Fix implemented:** Added patch embedding config to `GeometryConfig` (`patch_size`, `patch_embed_dim`, `image_hw`, `in_channels`). Updated `TransformerGeometry` to handle both LM mode (token IDs `[B, T]`) and vision mode (images `[B, C, H, W]` → patches → transformer → pooling → classification). Updated compose pipeline, input compatibility checks, and trainer to preserve 4D input for vision mode.

**Validation:** `digital/causal_transformer/instant/grad/euclid` on MNIST — composes successfully, forward pass produces `[B, 10]` logits, loss computation works. LM mode backward compatibility confirmed.

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
| Multi-worker parallelism | Add `--max-workers N` flag; process-pool evaluation with per-worker CUDA contexts | High |
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

1. ~~**GraphGeometry polymorphic forward** — unblocks graph_classification~~ ✅ DONE
2. ~~**CausalTransformer patch embedding** — unblocks B3c, vision transformers~~ ✅ DONE
3. **B1b pendulum + B1c-alt acrobot** — complete RL baselines
4. **B4a wine/iris fix** — complete tabular baselines
5. **C2/C4 scale** — GPU validation at scale
6. **Credit assignment for transformer vision** — `random_projections` fails due to pooling batch dim mismatch; need transformer-compatible credit

---

## ⚠️ OPEN TECHNICAL ISSUES

- ~~**GraphGeometry.forward signature**: Must handle both `(x, substrate)` and `(x, edge_index, batch)` without breaking existing node classification.~~ ✅ FIXED
- ~~**CausalTransformer input handling**: Currently expects 1D; needs automatic patchify for 2D/3D inputs.~~ ✅ FIXED
- **Credit assignment for transformer vision**: `RandomProjectionsCredit` fails because pooling changes batch dimension (B*T → B). Need transformer-aware credit or [CLS] token approach.
- **wine task**: All seeds 0.0 — likely StandardScaler + class mapping issue in TabularTask.
- **iris task**: High variance — may need more epochs (50+) or more seeds (10+) for stable estimate.
- **Energy minimization + recurrent**: ~120s/cell at L0 due to settle loop per env step — document as known limitation.
- **run_experiment.py val_acc=0.0000 bug**: All cells PASS but report zero accuracy (gate checks finite metrics, not learnability). Same root cause as wine/iris — metric extraction broken in async path.
- **Two experiment engines**: `survey_cli.py` (canonical, fixed) vs `run_experiment.py` (legacy, unfixed). Need deprecation plan.

---

## 🎯 PHASE 6: Consolidate Experiment Entry Points — ✅ COMPLETE

**Done:** Deleted legacy engines, `survey_cli.py` is now the single canonical entry point.

| Entry Point | Path | Status |
|-------------|------|--------|
| `survey_cli.py` | `python -m computronium.experiment.survey_cli` | ✅ **Canonical** — sequential, wave-based, planners, all fixes |
| `run_experiment.py` | `python scripts/run_experiment.py` | ❌ **DELETED** |
| `experiment.sh` | `./experiment.sh` | ❌ **DELETED** |
| `experiment_shallow.sh` | `./experiment_shallow.sh` | ❌ **DELETED** (commit f26b8ee3) |

**Feature parity verified:** `survey_cli.py` covers all use cases via explicit flags (`--fidelity`, `--tasks`, `--axes`, `--epochs`, `--n-seeds`, `--policy`, `--mode learn|static`, `--ladder`, `--promote-from`, `--resume`, `--dry-run`, `--doctor`) instead of profile presets.

**Verified working:** CUDA, all task domains (vision, RL, graph, sequence, tabular), L0/L1/L2 fidelities, learning/static modes, dry-run, doctor check.

---

## 🚫 NO (Same as TODO86)

- Paper figures
- Publishing artifacts
- Hypothesis backlogs
- Preventive fixes
- Meetings/retrospectives
- Cycles > 30 min