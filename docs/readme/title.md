# 🌌 Computronium: A Composable Laboratory for Learning Mechanisms

![Computronium Dashboard](docs/screenshots/assets/dashboard-hero.png)

*Computronium is a composable laboratory for learning mechanisms. Watch algorithms battle it out under a neutral, pre-registered evaluation protocol.*

> **Computronium** is a composable ML library and experimental laboratory for studying how learning mechanisms interact with dynamics, writable state, communication, precision, and resource constraints. Its six-axis interface supports controlled comparisons; its research program investigates when particular combinations offer measurable benefits.

**Computronium** (from [Wikipedia](https://en.wikipedia.org/wiki/Computronium)): the theoretical limit of physical computation. The name reflects the framework's aim to bridge abstract algorithms and the physical constraints of optical, memristive, neuromorphic, biological, quantum, and other substrate models.

<details>
<summary><strong>Motivation (the motivating hypothesis, not an established result)</strong> ⋯</summary>

Modern deep learning has achieved remarkable results in mathematical abstraction. But abstraction hides physical cost. Natural intelligence operates without global clocks, infinite memory for backward passes, or perfect precision—emerging from local interactions, energy minimization, and physical constraints.

The **search for computronium** is the motivating hypothesis: investigate learning systems native to physical constraints — asynchronous operation, local interactions, adaptation, noise tolerance, and energy/resource efficiency — and determine empirically which combinations of dynamics, learning rules, and substrates offer useful performance under those constraints. This is the *research agenda*; the library is usable independently of it, and no claim below is a conclusion of the search.
</details>

> **Status:** `v1.0.0`. The library, ontology, experiment kernel, demo and verification locks are complete. What is proven, designed, planned and unbuilt is stated in [Status and scope](#status-and-scope), so nothing below has to be taken on trust.

The library is usable independently of the research hypotheses; the research program consists of ongoing empirical questions, not completed conclusions.

| Audience | Entry Point |
|----------|-------------|
| 🧠 **Natural Scientists & Physicists** | Energy-based local learning demo: Hebbian/contrastive rules with Lyapunov stability analysis, passivity checks, energy tracking |
| 📊 **Data Scientists & ML Researchers** | Composable learning rules, local credit assignment, depth/compute scaling, systematic comparison across algorithms |
| 🔬 **Algorithm / Hardware Researchers** | Substrate models, hardware-aware constraints, stability analysis, algorithm–substrate co-design |
| 💻 **Systems Engineers & Developers** | Correctness by construction: type-safe (PEP 695 generics), property-locked (Hypothesis), Triton-accelerated, experiment kernel automation |

The library provides the composable primitives; the experiment kernel provides the campaign infrastructure for systematic exploration; the scientific program articulates the hypotheses that guide exploration priorities. [What is Computronium](#what-is-computronium) states what each layer gives you.

