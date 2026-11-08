# TODO85 — Continuous Experiment/Improve Cycle (Post-TODO84)

**Status:** Supersedes TODO84.md. All blockers fixed, all tests pass (883/883), system ready for continuous evidence-gathering.
**Machine:** 16 cores, RTX 3080 10 GB, 31 GB RAM, Linux 7.3.1-1-cachyos
**Codebase:** computronium main (commit `3adf259e` → latest)
**Constraint:** Each experiment ≤30 min walltime. Stay general, versatile, hypothesis-agnostic.

---

## 🔄 EXPERIMENT CYCLE TEMPLATE (≤30 min each)

```bash
# 1. HYPOTHESIZE: Pick 1-3 axes to vary (credit, update, substrate, dynamics, plasticity, geometry, task)
# 2. RUN: 0.1-0.5h ladder experiment with TPE
# 3. ANALYZE: comp report + comp coverage + look for patterns
# 4. IMPROVE: Fix bugs, add metrics, refine search space, update docs
# 5. COMMIT: Log findings, update TODO85.md, push
```

### Standard Command (adapt axes/hyperparams as needed)
```bash
./experiment_shallow.sh 0.2 --ladder --policy tpe --device cpu --workers 4 \
  --tasks digits \
  --axes '{"axis1":["val1","val2"],"axis2":["valA","valB"],"axis3":["valX"]}' \
  --hyperparams '{"param1":[v1,v2],"param2":[v3]}' \
  --skip-doctor
```

### Analysis Commands
```bash
uv run comp report --store <latest>.duckdb --format text
uv run comp coverage report --store <latest>.duckdb
uv run comp dashboard --store <latest>.duckdb --console  # Ctrl+C to exit
```

---

## 🎯 GENERAL EXPERIMENT DIRECTIONS (Mix & Match)

| Direction | Axes to Vary | Hyperparams to Sweep | Questions |
|-----------|-------------|---------------------|-----------|
| **Credit × Update** | credit, update | step_size, lr | Which credit/update pairs generalize? |
| **Substrate Robustness** | substrate, credit | weight_bits, init_scale | Where does quantization hurt? |
| **Dynamics Compatibility** | dynamics, substrate, credit | step_size, energy_weight | Which dynamics work on which substrates? |
| **Plasticity Effects** | plasticity, credit, update | psi_scale, rule_lr | When does plasticity help/hurt? |
| **Geometry × Task** | geometry, task | hidden_dims, kernel_size | Architecture-task fit? |
| **Optimizer Comparison** | update, credit | lr, momentum, weight_decay | Lion vs Muon vs Euclidean vs NGD? |
| **Fidelity Scaling** | (use --ladder) | n_seeds, epochs | L0→L1→L2 promotion efficiency? |
| **Sampler Efficiency** | (use --policy tpe/nsga2/random) | n_startup_trials | TPE vs Random vs NSGA-II? |

---

## 🛠️ SYSTEM IMPROVEMENT BACKLOG (Pick 1 per cycle)

| Area | Quick Wins (≤30 min) | Deeper Work |
|------|---------------------|-------------|
| **Ternary Substrate** | Add LR auto-scaling by weight_bits | Straight-through estimator, noise metrics |
| **CUDA Multi-Worker** | Verify spawn + single GPU per worker | torch.distributed, context isolation |
| **Search Space** | Add incompatibility filter at harvest | Pruning, min_samples_per_combo ordering |
| **Metrics** | Add gradient norm, weight norm, energy | Jacobian spectrum, loss landscape |
| **Dashboard** | Fix console exit, add heatmap view | Real-time updates, export |
| **Reproducibility** | Auto-generate run.json with git SHA | Hyperparameter importance, seed tracking |

---

## 📋 CYCLE LOG (Append each iteration)

| Cycle | Experiment (axes/hyperparams) | Walltime | Key Finding | Improvement Made |
|-------|------------------------------|----------|-------------|------------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| ... | | | | |

---

## 🚀 QUICK START (Copy-Paste-Adapt)

```bash
# Pick axes (1-3), hyperparams (optional), run:
./experiment_shallow.sh 0.2 --ladder --policy tpe --device cpu --workers 4 \
  --tasks digits \
  --axes '{"credit":["gradient","homeostatic"],"update":["euclidean","lion"],"substrate":["digital","ternary"]}' \
  --skip-doctor

# Analyze:
uv run comp report --store experiments/experiment_$(ls -t experiments/*.duckdb | head -1).duckdb --format text
uv run comp coverage report --store experiments/experiment_$(ls -t experiments/*.duckdb | head -1).duckdb

# Log cycle in TODO85.md, commit, repeat.
```

---

## 📝 COMMIT HISTORY (Baseline from TODO84)

| Commit | Message |
|--------|---------|
| `3adf259e` | Fix planner _seen not cleared between startup trials and wave loop |
| `3744b6da` | Improve experiment_shallow.sh: add --skip-doctor flag and skip doctor by default |
| `eee8bc91` | Fix test expectation: priors registry has 5 entries (not 28) |
| `9f07a70d` | Fix all pre-existing test failures: NTM, RandomProjections, integration regexes |
| `60fe60cd` | Fix integration test: update error message regex for PC-ALM credit validation |
| `fc062fb6` | Update TODO84.md: add test_policy_generation_lock fix to commit history |
| `d91cdfe9` | Fix test_policy_generation_lock: add DiverseRandomPolicy to test fixtures |
| `3f51e370` | Fix TPE sampler: add min_samples_per_combo to prevent COMBO_INSUFFICIENT_SAMPLES |
| `131b528b` | Fix registry exports: add reference_forward, kernel_*, and cases module public functions |
| ... | (see TODO84.md for full history) |

---

> **Principle:** Run → Observe → Improve → Repeat. No fixed hypothesis. Let data guide.