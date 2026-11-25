
## 📐 Stability-Plasticity Trade-off Hypothesis

v1 relied on strict Lyapunov descent and global contraction. In the joint architecture, we recognize that global contraction is a *sufficient* condition for a unique fixed point, but not a *necessary* condition for useful computation. Systems can exhibit local contraction, multiple attractors, limit cycles, or metastable states.

### The Hypothesis

We formulate the research object as:

```
adaptive computation ↔ controlled departure from contraction
```

*Useful rule reconfiguration may require temporarily sacrificing some of the contraction/stability margin that a fixed computational attractor would maximize.*

### Monitoring the Frontier

The framework measures:

| Metric | Purpose |
|--------|---------|
| $\rho(J_F)$ | Spectral radius of joint Jacobian — stability margin |
| Local Lyapunov exponent | Sensitivity/divergence |
| Settling time | Dynamical latency |
| Basin stability | Robustness to perturbation |

**Cheap fast-mode proxies (for CI)**: step-norm ratio, finite-difference perturbation growth, settle iterations, activation variance, gate entropy.

**Deeper estimates (nightly/campaign)**: spectral radius via eigvals of the autograd Jacobian (`spectral_radius_from_jacobian`), transient amplification via SVD (`dominant_singular_value`), Lyapunov via QR, basin via sampling.

### Resource Vector

<details>
<summary><strong>Resource vector definition</strong> ⋯</summary>

The scientific claim is strictly about **resource scaling, locality, energy efficiency, and learnability** under constrained physical resources:

$$\mathcal{C} = (\text{compute}, \text{memory}, \text{energy}, \text{latency}, \text{plastic-state capacity})$$

The campaign asks whether adaptive-rule systems occupy a superior Pareto frontier in $\mathcal{C}$.
</details>

### 5-Level Benchmark Hierarchy

<details>
<summary><strong>Experimental questions, not established results</strong> ⋯</summary>

The five experimental questions — adaptation efficiency, compute efficiency, structural robustness, algorithm migration, Z3 fixed-weights — are specified once per experiment (question, toy task, comparison axes, file) in the *Experiment Suite* below, each with a runnable `comp benchmark run --suite …` command. They define experimental questions, not established results.
</details>


## 🌐 Evaluation Domains

The framework defines **7 evaluation domains**, unified through a common task interface (`DomainTask` protocol), each with dedicated data loaders and metrics. **~26 tasks/datasets are currently implemented**; additional tasks are planned extensions (marked below). Planned entries do not count toward implemented totals.

### 📊 Domain Overview

| Domain | Tasks | Example Datasets | Models | Key Metrics |
|--------|-------|------------------|--------|-------------|
| **Vision** | 11 | MNIST, CIFAR-10/100, SVHN, Digits, synthetic (XOR, spirals) | 25+ | Accuracy, Loss, Energy, FLOPs |
| **Language (LM)** | 4 | Tiny Shakespeare, char n-gram, WikiText-2, Penn Treebank | 12+ | Perplexity, BPC, Accuracy |
| **Reinforcement Learning (RL)** | 3 (+2 planned) | CartPole, Pendulum, Acrobot; MountainCar, LunarLander (planned) | 8+ | Episode Return, Success Rate |
| **Graph** | 3 | Cora, CiteSeer, PubMed | 6+ | Node Classification Acc, F1 |
| **Tabular** | 3 (+2 planned) | Breast Cancer, Iris, Wine; Diabetes, California Housing (planned) | 10+ | Accuracy, R², AUC |
| **Time Series** | 1 (+1 planned) | Synthetic Forecast; ETT (planned) | 6+ | MSE, MAE |
| **Scientific** | 2 (+PDE suite planned) | Pendulum/Lorenz ODE simulation; Heat/Wave/Burgers, Navier-Stokes (planned) | 5+ | Relative L2, Conservation |

**Quick Commands (all domains)**
```bash
# Quick verification run (dry-run)
comp run quick-verify --dry-run

# Run with store
comp run quick-verify --store experiment.duckdb
```

### 🖼️ Vision Domain

**Tasks**: `mnist`, `fashion_mnist`, `kmnist`, `usps`, `cifar10`, `cifar100`, `svhn`, `digits`, `xor`, `spiral`, `circles`  
(image classification + synthetic boolean tasks)

### 📝 Language Modeling Domain

**Tasks**: `tiny_shakespeare` (char), `char_ngram`; `wikitext2`, `penn_treebank` (planned)

### 🎮 Reinforcement Learning Domain

**Tasks**: `cartpole`, `pendulum`, `acrobot` (implemented); `mountain_car`, `lunar_lander` (planned) — Gymnasium classic control + Box2D

### 🕸️ Graph Domain

**Tasks**: `cora`, `citeseer`, `pubmed` (Planetoid citation networks, node classification)

### 📋 Tabular Domain

**Tasks**: `breast_cancer`, `iris`, `wine` (classification, sklearn); `diabetes` (regression, continuous target, MSE read in train-variance units); `california_housing` (regression, planned: the sklearn loader downloads)

**Models**: All MLP-based families (backprop, eqprop, fa, pepita, hebbian, tile) support tabular tasks.

### 📈 Time Series Domain

**Tasks**: `synthetic_forecast` (sine-wave forecasting); `ett_h1` (planned)

**Models**: `recurrent`, `attention`, and `causal_transformer` geometries across all credit assignments. A standalone LSTM family is declared unavailable: the only LSTM in the tree is NTM's controller.

### 🔬 Scientific Domain

**Tasks**: `pendulum_state`, `lorenz_state` (offline ODE integration, one-step state prediction); the PDE suites Heat/Wave/Burgers/Navier-Stokes are planned

**Models**: `feedforward` and `recurrent` geometries over integrated state vectors. The operator-learning families PINO, DeepONet, and FNO are declared unavailable: no geometry implements them, and each carries a declared reason and trigger in the surface inventory.

## 🗺️ Measured Capability Map (serial, 2026-11-25)

One process per axis (`SEC_SEMAPHORE=1`), one rung-2 pair per seed, at each
rule's own declared box: `results/sec/serial3`. A row is *viable* when its
ladder reached an above-chance cell; *error-blind* rows (`homeostatic`,
`temporal_trace`) measure chance by contract and are counted separately.

| Axis | Viable + error-blind | Priced skips (named reason) |
|---|---|---|
| credit | 11/19 | `eligibility_prop`, `rtrl_reference`, `unbiased_rtrl` (declared batch layout) |
| dynamics | 3/8 | `natural_gradient` equivalent L0 cost (>180 s/epoch) |
| geometry | 7/12 | `graph`, `spatial_lattice` (no task declares the carrier) |
| plasticity | 5/8 | `eligibility_prop`-family layout refusals |
| substrate | 9/10 | one L0 cost row |
| update | 17/18 | `natural_gradient` L0 cost |
| **total** | **52/75** | 229 rungs: 176 measured, 41 refused, 9 defect, 3 timeout |

Two rows the earlier map named *unsupplied* now measure: `geometry/graph` on
`cora` **0.162 @ 0.8 s** (node classification, one epoch, above chance for
7-class, below bar) and `geometry/spatial_lattice` on `mnist`
**0.908 @ 5 s**. The graph refusal was a legality artifact: the declared-space
check composed without the task's `edge_index`, which the evaluator supplies
(`scripts/probes/todo104_carriers.py`).

The breadth exit is a predicate the repository evaluates:

```bash
uv run comp gate breadth
# gate: PASS (17 error-aware credits, ≥2 task families each)
```

**Claim** — `dynamics/energy_minimization` on MNIST at the base box:
`mean_diff = 0.0153`, 95 % CI `[0.0151, 0.0158]`, `p = 0.0076`, Cohen's
`d = 31.1` against the vision family minimum `0.8`.

**Coordinates** — the 22 paired arms measured at 7 index-matched seeds return
`coordinate`, not a claim: the effect is real (`random_projections` d=+1.21,
`analog` +1.00, `optical` +0.92, `spectral_constrained` +4.34) but a claim
needs the 95 % lower bound on `d` above the registered minimum. The n=64
`random_projections` run measured d=+1.024 with lower bound 0.783 — 0.017
short of 0.8. A fresh n=100 block measured d=+0.828 (lower 0.640) while
seeds 64..163 measured +1.065: seed-block variation exceeds the within-block
CI, so a larger n alone does not certify the effect. A pre-registered
comparison declares the minimum it must clear *and* the seed-block variance it
must cover; the meta-SEC proxy prices only minima its planned n can certify.
