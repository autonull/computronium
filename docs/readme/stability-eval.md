---

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

---

## 🌐 Evaluation Domains

The framework defines **7 evaluation domains**, unified through a common task interface (`DomainTask` protocol), each with dedicated data loaders and metrics. **~25 tasks/datasets are currently implemented**; additional tasks are planned extensions (marked below). Planned entries do not count toward implemented totals.

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

### 🖼️ Vision Domain

**Tasks**: `mnist`, `fashion_mnist`, `kmnist`, `usps`, `cifar10`, `cifar100`, `svhn`, `digits`, `xor`, `spiral`, `circles`  
(image classification + synthetic boolean tasks)

**Quick Commands**
```bash
# Quick verification run
comp run quick-verify --dry-run

# Run with store
comp run quick-verify --store experiment.duckdb
```

### 📝 Language Modeling Domain

**Tasks**: `tiny_shakespeare` (char), `char_ngram`; `wikitext2`, `penn_treebank` (planned)

**Key Experiments**
```bash
# Quick verification run
comp run quick-verify --dry-run
```

### 🎮 Reinforcement Learning Domain

**Tasks**: `cartpole`, `pendulum`, `acrobot` (implemented); `mountain_car`, `lunar_lander` (planned) — Gymnasium classic control + Box2D

**Key Experiments**
```bash
# Quick verification run
comp run quick-verify --dry-run
```

### 🕸️ Graph Domain

**Tasks**: `cora`, `citeseer`, `pubmed` (Planetoid citation networks, node classification)

### 📋 Tabular Domain

**Tasks**: `breast_cancer`, `iris`, `wine` (classification, sklearn); `diabetes`, `california_housing` (regression, planned)

**Models**: All MLP-based families (backprop, eqprop, fa, pepita, hebbian, tile) support tabular tasks.

### 📈 Time Series Domain

**Tasks**: `synthetic_forecast` (sine-wave forecasting); `ett_h1` (planned)

**Models**: RNN/LSTM/Transformer families across all credit assignments.

### 🔬 Scientific Domain

**Tasks**: `pendulum`, `lorenz` (ODE simulation); PDE suites (Heat/Wave/Burgers, Navier-Stokes) planned

**Models**: Physics-informed variants (PINO, DeepONet, FNO) adapted to computronium credit assignments.