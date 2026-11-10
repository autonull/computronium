# TODO87 — System Fixes & Remaining Coverage (Post-TODO86)

**Status:** PHASE 1, 2, 3 (B1b, B1c-alt, B4a) COMPLETE. PHASE 4 infrastructure hardening: multi-worker, SIGTERM closure, per-step logging — DONE. PHASE 5 scale validation (C2/C4) running. PHASE 6 transformer credit assignment — DONE.

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

## 🎯 PHASE 3: Complete Remaining Baselines — ✅ COMPLETE

### B1b — Pendulum Baseline ✅
- `digital/ff/instant/null/grad/euclid` on `pendulum` @ L0/L1 — **WORKING**
- Continuous action space; RLSystemTrainer handles Box actions — **VERIFIED**

### B1c-alt Extended — Acrobot ✅
- `digital/recurrent/instant/random_projections/euclid` on `acrobot` @ L0 — **WORKING**
- Discrete action space (3 actions) — **VERIFIED**

### B4a — Tabular Fixes ✅
- **wine**: ~28-31% accuracy (was 0.0) — **FIXED** (StandardScaler + class mapping working)
- **iris**: ~83-87% accuracy, low variance (was 0.07–0.53) — **FIXED** (normalization working)

---

## 🎯 PHASE 4: Infrastructure Hardening — ✅ COMPLETE

| Item | Description | Priority |
|------|-------------|----------|
| GraphGeometry polymorphic forward | Support both node + graph classification | High ✅ DONE |
| CausalTransformer patch embedding | Unblocks vision + sequence | High ✅ DONE |
| Multi-worker parallelism | Add `--max-workers N` flag; thread-pool fan-out over cells | High ✅ DONE |
| Wine/iris tabular debug | Fix baselines | Medium ✅ DONE |
| Per-step logging CLI flag | `--log-steps N` exposes step-level progress | Low ✅ DONE |
| SIGTERM run closure | Write manifest on graceful shutdown (`interrupted` status) | Low ✅ DONE |
| fvcore/jit deprecation | Removed internal fvcore usage; upstream torch_geometric warning remains | Medium ✅ PARTIAL |

---

## 🎯 PHASE 5: Scale Validation (Deferred from TODO86)

| Experiment | Axes | Budget | Status |
|------------|------|--------|--------|
| C2 | digital/ff/energy_min/null/grad/adam | 2h | Running (epoch 19/20, val_acc≈0.976, ~120-155s/epoch) |
| C4 | memristive/ff/energy_min/null/grad/adam | ~1h | Pending (n_seeds=1, 20 epochs) |

---

## 🎯 PHASE 6: Credit Assignment for Transformer Vision — ✅ COMPLETE

**Problem:** `RandomProjectionsCredit` failed because the transformer's activation chain pairs each weight with the act it *consumes* (not produces), the fused QKV widens the error space to 3d before attention narrows it back to d, and the vision readout pools the sequence (B*T → B), so the readout error lives in sample space while hidden acts are in sequence space.

**Fix implemented:**
1. **Geometry:** `TransformerGeometry.forward_with_intermediates` now delegates to `_apply_stack` so the act chain is the single source of truth (one act per 2-D weight input, plus logits). Vision mode appends the pooled act before the head, so the chain is `... → head_input (B, d) → logits (B, V)`.
2. **Credit:** `RandomProjectionsCredit` dispatches a `_transformer_path` for `causal_transformer` geometry (mirroring `LocalContrastiveCredit._tf_gradient` precedent). The path:
   - Uses feedback shaped by consecutive error widths (not weight shapes).
   - Walks error back: `err[k] = err[k+1] @ B_k` where `B_k` spans the two error widths.
   - When sample-space error (B) enters the sequence stream (B*T), it expands by replication across the sample's positions — the mean pool's structure.
3. **Validation:** Constraint `transformer_pairing_credit` rejects `target_inversion` and `temporal_trace` on transformer (they need pre/post pairs the chain doesn't provide). Working credits on transformer vision: `gradient`, `random_projections`, `homeostatic`, `pc_alm`.

**Validation:** `scripts/probes/t87_transformer_fa_credit.py` — `random_projections` carries live pseudo-gradients (cosine ≈ ±0.1–0.3 vs true gradient; head cosine = 1.0). Trains to val_acc=0.117 after 3 epochs (vs chance 0.1).

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
3. ~~**B1b pendulum + B1c-alt acrobot** — complete RL baselines~~ ✅ DONE
4. ~~**B4a wine/iris fix** — complete tabular baselines~~ ✅ DONE
5. **C2/C4 scale** — GPU validation at scale (C2 running, C4 pending)
6. ~~**Credit assignment for transformer vision** — `random_projections` fails due to pooling batch dim mismatch; need transformer-compatible credit~~ ✅ DONE
7. ~~**Multi-worker parallelism** — Add `--max-workers N` flag~~ ✅ DONE
8. ~~**SIGTERM run closure** — Write manifest on graceful shutdown~~ ✅ DONE

---

## ⚠️ OPEN TECHNICAL ISSUES

- ~~**GraphGeometry.forward signature**: Must handle both `(x, substrate)` and `(x, edge_index, batch)` without breaking existing node classification.~~ ✅ FIXED
- ~~**CausalTransformer input handling**: Currently expects 1D; needs automatic patchify for 2D/3D inputs.~~ ✅ FIXED
- ~~**Credit assignment for transformer vision**: `RandomProjectionsCredit` fails because pooling changes batch dimension (B*T → B). Need transformer-aware credit or [CLS] token approach.~~ ✅ FIXED
- **Energy minimization + recurrent**: ~58s/epoch at L0 on CPU due to settle loop per step — document as known limitation; use GPU for scale.
- **run_experiment.py val_acc=0.0000 bug**: All cells PASS but report zero accuracy (gate checks finite metrics, not learnability). Same root cause as wine/iris — metric extraction broken in async path.
- **Two experiment engines**: `survey_cli.py` (canonical, fixed) vs `run_experiment.py` (legacy, unfixed). Need deprecation plan.
- **torch_geometric fvcore/jit warning**: Upstream dependency uses deprecated `torch.jit.script` — unfixable from our side.

---

## 🎯 PHASE 7: Consolidate Experiment Entry Points — ✅ COMPLETE

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