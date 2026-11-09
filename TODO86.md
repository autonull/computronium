# TODO86 — Strategic Plan: From Primitive Coverage to Scientific Discovery

**Status:** All primitives measured at least once (Run 42). System runs wide multi-task ladder experiments reliably.

**Philosophy:** The system works. Now make it *discover* — find what combinations actually work, why, and at what scale.

---

## 🎯 THREE STRATEGIC TRACKS

### Track A: Compatibility Depth (2-3 runs)
Find which primitive combinations *actually work well together* on vision tasks.

| Priority | Experiment | Why |
|----------|------------|-----|
| A1 | **Geometry × Credit matrix** on `mnist`/`fashion_mnist` | Graph/causal_transformer/nca/tile/tile_mesh need non-gradient credits (homeostatic, pc_alm, target_inversion, temporal_trace, random_projections, local_goodness, local_contrastive). Currently only tested with gradient on feedforward/recurrent. |
| A2 | **neuromorphic substrate** full sweep | 0/9 substrates measured in Run 42. Needs spike_integration + temporal_trace/target_inversion credit. |
| A3 | **pc_alm dynamics × pc_alm credit** debug | Failed in Run 42 (compatibility). Fix or filter. |
| A4 | **Missing updates**: muon, natural_gradient, role_split | Never measured. Add to next wide run. |

### Track B: Task Breadth (2-3 runs)
Expand beyond 3 vision tasks to the full 24-task registry.

| Priority | Experiment | Why |
|----------|------------|-----|
| B1 | **Control/RL tasks**: cartpole, pendulum, acrobot | Test recurrent/nca geometries + energy_minimization/lazy dynamics on continuous control |
| B2 | **Graph tasks**: cora, citeseer, pubmed, graph_classification | Test graph geometry + compatible credits |
| B3 | **Sequence tasks**: copy_task, sequential_mnist, tiny_shakespeare | Test ntm/recurrent + temporal_trace/target_inversion credit |
| B4 | **Tabular/other**: iris, wine, breast_cancer, xor, circles, spiral | Baseline coverage |

### Track C: Scale & Hardware (1-2 runs)
Validate that findings transfer to larger models and GPU.

| Priority | Experiment | Why |
|----------|------------|-----|
| C1 | **hidden=256, batch=256** on best L2 combos | GPU only wins at scale. Test: complex/recurrent/energy_min/rule_state/grad/adam, optical/ff/instant/temporal_psi/random_projections/local_adam |
| C2 | **Longer training**: 50-100 epochs on promoted cells | L1=8 epochs, L2=20 seeds is thin. Real training needs more epochs. |

---

## 📋 EXPERIMENT QUEUE (Ready to Run)

### Next Run (Track A1 + A2): Geometry × Credit + Neuromorphic
```bash
./experiment_shallow.sh 1.5 --policy tpe --device cpu --workers 8 \
  --tasks mnist,fashion_mnist --ladder \
  --axes '{
    "credit":["gradient","homeostatic","pc_alm","target_inversion","temporal_trace","random_projections","local_goodness","local_contrastive"],
    "update":["euclidean","adam","lion","local_adam"],
    "substrate":["digital","neuromorphic","analog","optical","sparse"],
    "plasticity":["null","rule_state","temporal_psi"],
    "dynamics":["instantaneous","energy_minimization","spike_integration","lazy"],
    "geometry":["feedforward","recurrent","conv","attention","graph","causal_transformer","nca","tile_mesh","ntm"]
  }' --skip-doctor
```

### Run After (Track A3 + A4): pc_alm Debug + Missing Updates
```bash
./experiment_shallow.sh 1.0 --policy tpe --device cpu --workers 8 \
  --tasks mnist --ladder \
  --axes '{
    "credit":["pc_alm","gradient"],
    "update":["euclidean","adam","muon","natural_gradient","role_split","lion"],
    "substrate":["digital"],
    "plasticity":["null","rule_state"],
    "dynamics":["pc_alm","instantaneous","energy_minimization"],
    "geometry":["feedforward","recurrent"]
  }' --skip-doctor
```

### Run After (Track B1): Control Tasks
```bash
./experiment_shallow.sh 1.0 --policy tpe --device cpu --workers 8 \
  --tasks cartpole,pendulum,acrobot --ladder \
  --axes '{
    "credit":["gradient","target_inversion","temporal_trace"],
    "update":["euclidean","adam","lion"],
    "substrate":["digital","analog"],
    "plasticity":["null","fast_weights","temporal_psi"],
    "dynamics":["instantaneous","energy_minimization","lazy","predictive_settling"],
    "geometry":["recurrent","nca","feedforward"]
  }' --skip-doctor
```

---

## 🔬 SCIENTIFIC QUESTIONS TO ANSWER

| Question | How to Answer |
|----------|---------------|
| **Which credit × geometry pairs work?** | Run A1, analyze val_acc heatmap per (credit, geometry) |
| **Does neuromorphic + spike_integration beat digital?** | Compare neuromorphic/spike_integration/temporal_trace vs digital/instantaneous/gradient on same geometry |
| **Does energy_minimization help at scale?** | Run C1: compare energy_minimization vs instantaneous at hidden=256, epochs=50 |
| **Do advanced updates (muon, natural_gradient) help?** | Run A4: compare adam vs muon vs natural_gradient on same cells |
| **Which plasticity helps recurrent geometries?** | Track A1: rule_state vs temporal_psi vs fast_weights on recurrent/nca |
| **Do findings transfer across tasks?** | Track B: run best vision combos on control/graph/sequence tasks |

---

## 📊 SUCCESS METRICS (Per Track)

### Track A: Compatibility Depth
- [ ] ≥80% of (credit × geometry) pairs measured with ≥3 seeds
- [ ] neuromorphic substrate has ≥5 measured cells with val_acc > 0.5
- [ ] pc_alm dynamics either works or cleanly filtered
- [ ] muon/natural_gradient/role_split each have ≥3 measured cells

### Track B: Task Breadth
- [ ] ≥12/24 tasks have ≥1 measured cell
- [ ] ≥3 non-vision tasks have val_acc > random baseline
- [ ] Graph tasks work with graph geometry + compatible credit

### Track C: Scale & Hardware
- [ ] hidden=256, batch=256, epochs=50 runs without OOM
- [ ] GPU speedup > 1.5× vs CPU at that scale
- [ ] Best L2 combo maintains val_acc > 0.95 at scale

---

## 🛠️ INFRASTRUCTURE IMPROVEMENTS (Parallel)

| Improvement | File | Effort |
|-------------|------|--------|
| L0 share auto-tuning | `wave.py` | 1-2 hrs |
| energy_minimization convergence doc/fix | `ontology/dynamics/_dynamics.py` | 30 min |
| GPU convergence check off hot path | `kernel/evaluate.py` + Triton kernels | 2-4 hrs |
| Task-aware scheduling (not round-robin) | `wave.py` | 1-2 hrs |
| Coverage heatmap report | `comp coverage report` | 1 hr |

---

## 📈 TRACKING

| Run | Track | Axes | Result | Key Finding |
|-----|-------|------|--------|-------------|
| 42 | A | All primitives | 63 cells, 1 fail | **All primitives measured**; quantum/spike_integration/pc_alm/conflict_adaptive/routing/substrate_coupled/local_adam/etc. now have data |
| — | — | — | — | — |

---

## 🚫 STILL NOT DOING

- Paper figures
- Publishing artifacts
- Hypothesis backlogs
- Preventive fixes
- Meetings/retrospectives
- Cycles > 30 min per fix iteration

---

**Start:** Run Track A1 (Geometry × Credit + Neuromorphic) on mnist/fashion_mnist. Fix what breaks. Repeat.