# TODO86 — Scale & Coverage (Post-TODO85)

**Status:** System fixed and experimentally sound. Now: validate at scale, cover remaining task types.

**Baseline (Run 48):** 72 cells, 72 PASS, L0→L1→L2 working, best L2 0.9775 on mnist.

---

## 🎯 PHASE 1: GPU Scale Validation (Track C)

**Goal:** Prove GPU speedup at scale (hidden=256, batch=256, epochs=50) on best combos.

| Experiment | Axes | Budget | Purpose |
|------------|------|--------|---------|
| C1 | digital/ff/instant/null/grad/euclid (best L2) | 2h | GPU vs CPU baseline at scale |
| C2 | digital/ff/energy_min/null/grad/adam (2nd best L2) | 2h | GPU with settling at scale |
| C3 | digital/ff/instant/null/pepita/adam (best non-grad credit) | 1h | Credit variety at scale |
| C4 | memristive/ff/energy_min/null/grad/adam | 1h | Non-digital substrate at scale |

**Prerequisites:**
- Benchmark single cell: `hidden=256, batch=256, epochs=1` CPU vs CUDA
- If GPU not faster, investigate: settle loop sync, compilation, kernel launch overhead

---

## 🎯 PHASE 2: RL/Control Tasks (Track B1)

**Goal:** Full training loop for cartpole, pendulum, acrobot.

**Status:** ✅ COMPLETED - RLSystemTrainer implemented and tested

**Experiments:**
| Experiment | Axes | Budget | Purpose | Status |
|------------|------|--------|---------|--------|
| B1a | digital/ff/instant/null/grad/euclid | 0.5h | Cartpole baseline | ✅ Done |
| B1b | digital/ff/instant/null/grad/euclid | 0.5h | Pendulum baseline | ✅ Done |
| B1c | digital/recurrent/energy_min/null/grad/adam | 1h | Recurrent + energy_min on control | Pending |

---

## 🎯 PHASE 3: Graph Tasks (Track B2)

**Goal:** Full training for cora/citeseer/pubmed (node classification) + graph_classification.

**Status:** ✅ COMPLETED - GraphSystemTrainer implemented and tested

**Experiments:**
| Experiment | Axes | Budget | Purpose | Status |
|------------|------|--------|---------|--------|
| B2a | digital/graph/instant/random_projections/euclid | 0.5h | Cora baseline | ✅ Done |
| B2b | digital/conv/instant/homeostatic/euclid | 0.5h | Conv geometry on graph | Pending |
| B2c | digital/graph/instant/grad/euclid | 1h | Native graph geometry | Pending (needs compatible credit) |

---

## 🎯 PHASE 4: Sequence Tasks (Track B3)

**Tasks:** copy_task, sequential_mnist, tiny_shakespeare

**Metric:** perplexity (LM) or accuracy (classification)

**Experiments:**
| Experiment | Axes | Budget | Purpose |
|------------|------|--------|---------|
| B3a | digital/ff/instant/null/grad/euclid | 0.5h | Copy task |
| B3b | digital/recurrent/instant/grad/euclid | 0.5h | Sequential MNIST |
| B3c | digital/causal_transformer/instant/grad/euclid | 1h | Tiny Shakespeare (needs patch embedding) |

---

## 🎯 PHASE 5: Tabular Baselines (Track B4)

**Tasks:** iris, wine, breast_cancer, digits (sklearn), covtype

**Experiments:**
| Experiment | Axes | Budget | Purpose |
|------------|------|--------|---------|
| B4a | digital/ff/instant/null/grad/euclid | 0.3h | Full tabular sweep |

---

## 🛠️ INFRASTRUCTURE IMPROVEMENTS (Parallel)

| Item | Description | Priority |
|------|-------------|----------|
| ✅ Compiled settle for energy_minimization | Move convergence check off hot path; batch horizon with `compiled=True` | High — enables GPU speedup |
| ~~RLSystemTrainer~~ | ~~Episode rollout + policy gradient~~ | ~~High — unblocks B1~~ ✓ |
| ~~GraphSystemTrainer~~ | ~~Masked node classification + graph readout~~ | ~~High — unblocks B2~~ ✓ |
| CausalTransformer patch embedding | ViT-style for vision; 1D token handling for sequence | Medium — unblocks B3 |
| Timing cache per (device, fidelity, workers, task) | Already works; verify at scale | Low |
| Claim eligibility | n>=3, replay_hash, normalized_metric, PASS — currently 0; investigate | Medium |

---

## 🔄 EXPERIMENT LOOP (Same as TODO85)

```bash
# 1. RUN (1-2h, TPE, GPU for C*, CPU for B*)
./experiment_shallow.sh 1.5 --policy tpe --device cuda --workers 4 \
  --tasks <task_list> \
  --axes '<axis_json>' \
  --ladder --skip-doctor

# 2. ANALYZE (30s)
uv run comp report --store experiments/<latest>.duckdb --format text
uv run comp coverage report --store experiments/<latest>.duckdb

# 3. FIX (≤15 min) — infrastructure only, not preventive
# 4. VERIFY (0.02h, no ladder)
# 5. COMMIT + LOG
```

---

## 📋 PRIORITY ORDER

1. **C1** — GPU scale on best combo (validates Track C)
2. ~~**B1a** — RLSystemTrainer + Cartpole (unblocks Track B1)~~ ✓
3. ~~**B2a** — GraphSystemTrainer + Cora (unblocks Track B2)~~ ✓
4. **C2-C4** — Remaining GPU scale combos
5. **B1b-B1c, B2b-B2c** — RL/Graph variety
6. **B3, B4** — Sequence + Tabular coverage

---

## 🚫 NO (Same as TODO85)

- Paper figures
- Publishing artifacts
- Hypothesis backlogs
- Preventive fixes
- Meetings/retrospectives
- Cycles > 30 min