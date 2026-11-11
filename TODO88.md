# TODO88 — Experiment/Fix Cycle Continuation (Post-TODO87)

**Mission:** Continue the experiment/fix cycle: run experiments (≤15 min each), discover bugs, scrutinize poor-performing algorithms as potential implementation defects, and question excluded possibilities.

**Status:** TODO87 PHASE 1-7 COMPLETE. Recent fixes: task-aware positive control, graph task payload_key='val_acc', TransformerGeometry handles flattened input. Core system working across vision, RL, graph, tabular. Property locks pass (lint=583, FA determinism tests passing).

---

## 🎯 PRIMARY MISSION: Experiment/Fix Cycle

**Loop:**
1. **RUN** (≤15 min) — `survey_cli` with focused axes
2. **ANALYZE** (30s) — `comp report`, `comp coverage`, check for anomalies
3. **FIX** (≤15 min) — Infrastructure only; suspect low performance = implementation defect
4. **VERIFY** (0.02h) — Quick re-run
5. **COMMIT + LOG** — Update TODO88.md

**Key Principle:** Be skeptical of low-performing experiments; this could indicate an implementation defect to fix. Be suspicious of any excluded possibilities that may actually be possible.

---

## 🔬 EXPERIMENTS TO RUN (Priority Order)

### 1. Causal Transformer Vision — Credit Sweep (L0, MNIST)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_causal_transformer_credits.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["causal_transformer"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections","homeostatic","pc_alm"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Watch for:** `random_projections` cosine similarity vs true gradient; `homeostatic`/`pc_alm` should work per TODO87 PHASE 6.

### 2. Causal Transformer Vision — Geometry Parity (L0, MNIST)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_vision_geometry_parity.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["conv","feedforward","causal_transformer"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Watch for:** Transformer vision should be competitive with conv/feedforward (~0.95+). If not, investigate patch embedding, pooling, or credit assignment.

### 3. Graph Classification — Geometry Sweep (L0, MUTAG)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks graph_classification --fidelity L0 \
  --store experiments/t88_graph_geometry_sweep.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph","spatial_lattice"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["euclidean","adam"]}' \
  --epochs 5 --n-seeds 2
```
**Watch for:** `spatial_lattice` should work for graph tasks. `random_projections` credit on graph geometry.

### 4. Graph Node Classification — Full Sweep (L0, Cora/Citeseer/Pubmed)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks cora,citeseer,pubmed --fidelity L0 \
  --store experiments/t88_node_classification.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["graph"],"dynamics":["instantaneous","energy_minimization"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam","euclidean"]}' \
  --epochs 5 --n-seeds 2
```
**Watch for:** `energy_minimization` dynamics on graph (EqProp). Should train, not just instantaneous.

### 5. Energy Minimization — Dynamics Sweep (L0, MNIST)
```bash
uv run python -m computronium.experiment.survey_cli 0.15 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_energy_min_dynamics.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward"],"dynamics":["instantaneous","energy_minimization","predictive_settling"],"plasticity":["null"],"credit":["gradient","random_projections"],"update":["adam"]}' \
  --epochs 5 --n-seeds 2
```
**Watch for:** `energy_minimization` should match/exceed instantaneous (as in C2 validation). `predictive_settling` should work.

### 6. Credit Assignment — Cross-Geometry (L0, Multi-Task)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist,cifar10,sequential_mnist,copy_task,cora,graph_classification,pendulum,acrobot,wine,iris --fidelity L0 \
  --store experiments/t88_credit_cross_geometry.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["feedforward","recurrent","causal_transformer","graph"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient","random_projections","homeostatic","local_contrastive"],"update":["adam","euclidean"]}' \
  --epochs 3 --n-seeds 1
```
**Watch for:** Credit rules that fail on specific geometries. `local_contrastive` on transformer, `random_projections` on graph/RNN.

### 7. Substrate Comparison — Digital vs Memristive (L0, MNIST)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks mnist --fidelity L0 \
  --store experiments/t88_substrate_comparison.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital","memristive"],"geometry":["feedforward"],"dynamics":["instantaneous"],"plasticity":["null"],"credit":["gradient"],"update":["adam"]}' \
  --epochs 3 --n-seeds 1
```
**Watch for:** Memristive should work (known CPU-bound for energy_min, but instantaneous should be fine).

### 8. Plasticity Sweep — Fast Weights / Routing (L0, Sequential MNIST)
```bash
uv run python -m computronium.experiment.survey_cli 0.1 \
  --mode learn --policy tpe --device cuda \
  --tasks sequential_mnist,copy_task --fidelity L0 \
  --store experiments/t88_plasticity_sweep.duckdb \
  --max-workers 4 \
  --axes '{"substrate":["digital"],"geometry":["recurrent"],"dynamics":["instantaneous"],"plasticity":["null","fast_weight","routing"],"credit":["random_projections"],"update":["euclidean"]}' \
  --epochs 5 --n-seeds 2
```
**Watch for:** Plasticity should improve over null on sequential tasks.

---

## 🐛 DEFECT PATTERNS TO INVESTIGATE

| Symptom | Likely Defect | Investigation |
|---------|---------------|---------------|
| val_acc ≈ chance | Forward pass broken, wrong geometry, credit produces zeros | Check activation shapes, credit pseudo-gradients, loss flow |
| val_acc drops over epochs | Optimizer misconfigured, gradient explosion, weight decay wrong | Check update step, learning rate, gradient clipping |
| "free settle telemetry failed" | Geometry not layered, device mismatch, wrong act count | Check `forward_with_intermediates` returns list matching params |
| Positive control FAIL | Wrong geometry for task, compatibility check broken | Check `geometry_hint` in task registry, `_check_coord_compatibility` |
| NaN/Inf loss | Numerical instability, unclamped energy, bad init | Check `max_energy` clamp, weight init, substrate noise |
| All credits fail on geometry | Credit dispatch missing, geometry not in compatibility matrix | Check `credit_assignment` compatibility, `_transformer_path` etc. |
| Graph CUDA OOM/index error | PyG batch to CUDA, upstream version mismatch | Try CPU, check PyG/CUDA versions, document limitation |
| Slow training (>60s/epoch L0) | CPU-bound settle loop, no GPU kernel, unnecessary copies | Profile, check `device` placement, check for `.to(cpu)` calls |

---

## 🚫 EXCLUDED POSSIBILITIES TO QUESTION

| Assumption | Why It Might Be Wrong | Test |
|------------|----------------------|------|
| "GraphClassification CUDA is unfixable upstream" | May be version pin or DataLoader config | Try `num_workers=0`, `pin_memory=False`, PyG 2.6.x |
| "Energy minimization + recurrent is CPU-bound" | May lack GPU kernel; check if `_settle_compiled` works | Profile `energy_minimization` on recurrent geometry |
| "Transformer vision needs patch embedding" | Could use positional encoding on flattened patches | Try `patch_size=0` with `seq_len=H*W` for comparison |
| "Memristive substrate doesn't support energy_min" | May just need GPU settle kernel | Check `SubstrateSettleKernel` for memristive |
| "RandomProjectionsCredit fails on graph" | May need `_graph_path` like `_transformer_path` | Check credit dispatch for `graph` geometry |
| "Spatial lattice only for 3D" | May work for 2D grid graphs | Try `spatial_lattice` on graph tasks |
| "Null plasticity is only baseline" | `rule_state` plasticity may be zero-cost | Test `rule_state` on feedforward/recurrent |

---

## 📋 REMAINING WORK FROM TODO87 (Carried Forward)

### Immediate (Next Session)
- [ ] **C4 scale validation** — Memristive energy_min CPU-bound (~560s/epoch). Document; skip full L2. Use GPU-accelerated dynamics for future scale validation.

### Register C Hygiene Pass (Deferred)
- [ ] **Lint reduction** — 583 → 0. Each requires manual review (math notation, Triton DSL).
- [ ] **Type checking** — Full repo-wide pyright strict (currently strict on new modules only).
- [ ] **Full pytest run** — All shards + acceptance (~10 min).
- [ ] **pip-audit** — Dependency vulnerability scan.

### Upstream Dependencies (Question, Don't Assume Unfixable)
- [ ] **GraphClassification CUDA** — Test PyG version pins, DataLoader config.
- [ ] **torch_geometric fvcore/jit warning** — Check if newer PyG fixes this.

### Known Limitations (Document, But Revisit)
- [ ] **Energy minimization + recurrent** — ~58s/epoch at L0 on CPU. Check for GPU kernel.

---

## 🔄 CONTINUOUS INTEGRATION CHECKS (Per Commit)

```bash
# Dev-env smoke
uv run python -c "import optuna, scipy, torchvision, pytest"

# Format + lint changed files
uv run ruff format && uv run ruff check --fix

# Pyright on changed files (strict for new modules)
uv run pyright <changed_files>

# Targeted tests
uv run python -m pytest tests/property/test_task_geometry_compat_lock.py tests/property/test_dynamics_wiring_lock.py -v
```

---

## 📊 SUCCESS CRITERIA

| Metric | Target |
|--------|--------|
| Positive control PASS rate | 100% across all task domains |
| Vision (MNIST/CIFAR) best val_acc | > 0.95 (digital/ff/grad/adam) |
| Graph classification best val_acc | > 0.70 (digital/graph/grad/adam) |
| Node classification (Cora) best val_acc | > 0.75 (digital/graph/grad/adam) |
| RL (Pendulum) mean_reward | > -200 (digital/ff/grad/euclid) |
| Tabular (Iris) best val_acc | > 0.90 (digital/ff/grad/euclid) |
| Credit sweep: ≥3 credits work per geometry | gradient + random_projections + 1 other |
| No "free settle telemetry failed" warnings | 0 occurrences |
| Experiment cycle time | ≤30 min (run + analyze + fix + verify) |

---

## 🚫 NO (Same as TODO86/87)

- Paper figures
- Publishing artifacts  
- Hypothesis backlogs
- Preventive fixes
- Meetings/retrospectives
- Cycles > 30 min

---

## 📝 SESSION LOG TEMPLATE

After each experiment/fix cycle, append to this file:

```
## Session YYYY-MM-DD
**Experiment:** <command>
**Result:** <PASS/FAIL, key metrics>
**Defects Found:** <list>
**Fixes Applied:** <files changed>
**Next Experiment:** <planned command>
```