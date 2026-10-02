# 🌌 Computronium: A Composable Laboratory for Learning Mechanisms

> **Computronium** is a composable ML library and experimental laboratory for studying how learning mechanisms interact with dynamics, writable state, communication, precision, and resource constraints. Its six-axis interface supports controlled comparisons; its research program investigates when particular combinations offer measurable benefits.

**Computronium** (from [Wikipedia](https://en.wikipedia.org/wiki/Computronium)): the theoretical limit of physical computation. The name reflects the framework's aim to bridge abstract algorithms and the physical constraints of optical, memristive, neuromorphic, biological, quantum, and other substrate models.

<details>
<summary><strong>Motivation (the motivating hypothesis, not an established result)</strong> ⋯</summary>

Modern deep learning has achieved remarkable results in mathematical abstraction. But abstraction hides physical cost. Natural intelligence operates without global clocks, infinite memory for backward passes, or perfect precision—emerging from local interactions, energy minimization, and physical constraints.

The **search for computronium** is the motivating hypothesis: investigate learning systems native to physical constraints — asynchronous operation, local interactions, adaptation, noise tolerance, and energy/resource efficiency — and determine empirically which combinations of dynamics, learning rules, and substrates offer useful performance under those constraints. This is the *research agenda*; the library is usable independently of it, and no claim below is a conclusion of the search.
</details>

> **Status:** Active development. The core library, ontology, verification infrastructure, and experiment tooling are implemented; large-scale empirical studies and physical-hardware validation are ongoing.

The library is usable independently of the research hypotheses; the research program consists of ongoing empirical questions, not completed conclusions.

| Aspect | What It Is | What You Get |
|------|------------|--------------|
| **📦 ML Library** | Composable learning systems behind one training API | Train and compare every implemented rule — Backprop, EqProp, FA, FF, PEPITA, Target Prop, Predictive Coding, Hebbian/STDP, SNN, TileNet, 6-D joint — under a single interface |
| **🔬 Research Framework** | 6-D parameterized algorithm space (Substrate × Geometry × StateDynamics × Plasticity × CreditAssignment × ParameterUpdate), experiment kernel, property-verified hypercube, stability-plasticity monitoring, **multi-objective Pareto frontier analysis** (configurable objectives per axis) | Systematic ablations across axes; controlled benchmark campaigns for adaptation efficiency, compute efficiency, structural robustness, algorithm migration, Z3 fixed-weight adaptation; **axis-aligned objective optimization** (accuracy, walltime, params, FLOPs, energy, latency, stability, plasticity, credit alignment, ruler-relative) |
| **🧪 Scientific Program** | Hypotheses on locality, plasticity, stability, and physical constraints as first-class dimensions; stability-plasticity trade-off as controlled departure from contraction; resource-vector Pareto analysis (compute, memory, energy, latency, plastic-state capacity) | Ongoing empirical investigation—not validated claims. Large-scale campaigns and physical-hardware validation remain future work. |

| Audience | Entry Point |
|----------|-------------|
| 🧠 **Natural Scientists & Physicists** | Energy-based local learning demo: Hebbian/contrastive rules with Lyapunov stability analysis, passivity checks, energy tracking |
| 📊 **Data Scientists & ML Researchers** | Composable learning rules, local credit assignment, depth/compute scaling, systematic comparison across algorithms |
| 🔬 **Algorithm / Hardware Researchers** | Substrate models, hardware-aware constraints, stability analysis, algorithm–substrate co-design |
| 💻 **Systems Engineers & Developers** | Correctness by construction: type-safe (PEP 695 generics), property-locked (Hypothesis), Triton-accelerated, experiment kernel automation |

The ML library provides the composable primitives; the research framework provides the campaign infrastructure for systematic exploration; the scientific program articulates the hypotheses that guide exploration priorities.

---
