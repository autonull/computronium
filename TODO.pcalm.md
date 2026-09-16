Integrate https://github.com/SakanaAI/pc-alm into Computronium

Deliver a complete research and development plan that we can follow to fully achieve the objectives:
- how to completely absorb the algorithm, its principles/ideas, evaluation/testing methodology.  consider what components may already be implemented, or what implemented components can be extended/abstracted/generalized to support PC-ALM
- implementation efficiency (ex: what Computronium's stack offers instead of JAX)
- defects or limitations of PC-ALM and its tests, which we can address in the process of porting
- ways to improve or develop new algorithms inspired by PC-ALM
- other algorithms referenced by the research that we might also absorb into Computronium
- properly attribute the research for reference

----

### **Research & Development Plan: Integrating PC-ALM into Computronium**

**Objective:** Fully absorb the "Augmented Lagrangian Predictive Coding" (PC-ALM) algorithm, recently released by Sakana AI (September 2026), and integrate it into the Computronium stack. This plan outlines the technical strategy for algorithmic abstraction, performance optimization over the reference JAX implementation, and future research directions.

---

### **Phase 1: Algorithm Absorption & Component Integration**

**1.1. Core Principles & Mathematical Abstraction**
PC-ALM replaces global Backpropagation (BP) with **layer-local dynamical systems**. Instead of a forward pass followed by a backward pass, the network is modeled as a physical system relaxing to equilibrium.
*   **Primal-Dual Formulation:** Every layer $l$ maintains a primal state (activations $h_l$) and a dual state (Lagrange multipliers $\lambda_l$).
*   **PI Controller Dynamics:** The dual variables accumulate prediction errors over time, acting as a Proportional-Integral (PI) feedback controller. This mechanism generates "ballistic" (wave-like) credit assignment signals that propagate through the network, allowing training of depths up to 1000 layers without vanishing gradients.
*   **Local Hebbian Updates:** Weight updates are computed strictly from local states: $\Delta W_l \propto \lambda_l h_{l-1}^T$.

**1.2. Extension of Computronium Components**
To support PC-ALM, Computronium’s core abstractions must be generalized beyond standard differentiable modules:
*   **`LocalDynamicsModule` Base Class:** Extend the standard `Module` interface. Instead of just `forward()`, implement a `dynamical_step(t)` method that takes the states of neighboring layers ($h_{l-1}, h_{l+1}$) and updates the local primal/dual states.
*   **Relaxation Engine:** Create a `RelaxationEngine` that runs the inference loop. This engine manages the iterative settling process for a fixed "inference budget" ($T$ steps) before any weight updates occur.
*   **State Management:** Computronium’s memory manager must support explicit allocation for dual variables $\lambda_l$, which act as persistent memory across the relaxation phase but are not part of the global autograd graph.

---

### **Phase 2: Implementation Efficiency (Computronium vs. JAX)**

The reference implementation uses JAX. While JAX is powerful, its reliance on XLA compilation and functional paradigms introduces bottlenecks that Computronium’s custom stack can exploit.

| Feature | JAX Reference Implementation | Computronium Stack Strategy |
| :--- | :--- | :--- |
| **Relaxation Loop** | Uses `jax.lax.scan` or Python loops. XLA compiles this into a sequence of ops, often forcing reads/writes to High Bandwidth Memory (HBM) at every time step $t$. | **Kernel Fusion:** Implement the entire relaxation loop ($T$ steps) as a single fused GPU kernel (e.g., via Triton, CUDA, or Mojo). Keep $h$ and $\lambda$ in fast SRAM/registers throughout the loop, drastically reducing memory bandwidth usage. |
| **Dynamic Control Flow** | Static unrolling or `lax.while_loop`, which can be inefficient or struggle with complex termination conditions on accelerators. | **Dynamic Early Stopping:** Implement hardware-native termination. If the prediction error drops below $\epsilon$, the kernel terminates immediately, saving compute cycles without graph recompilation. |
| **Memory Layout** | JAX often uses Array of Structures (AoS) or default tensor layouts. | **SoA Vectorization:** Store Primal ($H$) and Dual ($\Lambda$) variables in Structure of Arrays (SoA) format to maximize SIMD vectorization and cache line efficiency. |

---

### **Phase 3: Defect Resolution & Porting Improvements**

During the porting process, we will address specific limitations identified in the Sakana AI research:

*   **Loss of "Prospective Configuration":**
    *   *Defect:* Standard Predictive Coding allows activations to settle into a "prospective" state that differs from the standard forward pass, often improving sample efficiency. PC-ALM’s strict alignment with BP loses this benefit.
    *   *Solution:* Implement a **Hybrid Dynamics** mode in Computronium. Introduce a leakage factor $\alpha \in [0, 1]$ for the dual variables. When $\alpha=0$, it behaves like PC-ALM; as $\alpha \to 1$, it recovers Prospective Configuration. This allows tuning the trade-off between credit propagation speed and representation learning.
*   **Fixed Inference Budgets ($T$):**
    *   *Defect:* The reference code uses a fixed budget (e.g., $T=2L$), which is wasteful for shallow networks or easy inputs.
    *   *Solution:* Implement **Adaptive Relaxation**. The Computronium engine should monitor the norm of the constraint violation $\|C(h)\|$ and stop the relaxation phase dynamically once convergence is reached.
*   **Static Hyperparameter Grids:**
    *   *Defect:* The reference relies on pre-calculated tables (`eta_best_by_cell.csv`) for learning rates.
    *   *Solution:* Integrate **Meta-Learning** or **Auto-Tuning**. Train a small hypernetwork to predict the optimal step sizes $\eta_h$ and penalty parameters $\gamma_0$ dynamically based on the layer's activation statistics.

---

### **Phase 4: New Algorithms Inspired by PC-ALM**

With PC-ALM integrated, Computronium can pioneer new variants:
1.  **Local Learning Transformers:** Derive the Augmented Lagrangian for the Self-Attention mechanism. Define dual variables for Queries ($Q$), Keys ($K$), and Values ($V$) to enforce local constraints, potentially enabling Transformers that train without backpropagation.
2.  **Asynchronous Distributed PC-ALM:** Since PC-ALM requires only neighbor-to-neighbor communication, Computronium can implement a **Neuromorphic Cluster** topology. Layers can reside on physically separate nodes (or even different hardware types) and train asynchronously without global gradient synchronization (All-Reduce), fundamentally changing distributed training scaling laws.
3.  **Spiking PC-ALM (SNNs):** Map the continuous PI controller dynamics to discrete Spiking Neural Networks. Use spike-timing-dependent plasticity (STDP) modulated by dual variables to train deep SNNs with the efficiency of PC-ALM.

---

### **Phase 5: Ecosystem & Reference Absorption**

To make Computronium a leader in alternative learning rules, we must also absorb the foundational algorithms referenced by PC-ALM:
*   **Equilibrium Propagation (EP):** (Scellier & Bengio) - Absorb the "two-phase" relaxation mechanism (free phase vs. nudged phase) which is a strong competitor to PC-ALM for energy-based models.
*   **Target Propagation (TP / DTP):** (LeCun, Bengio) - Implement invertible layers that propagate *targets* rather than gradients, offering another biologically plausible alternative.
*   **The Forward-Forward Algorithm:** (Hinton) - Implement the contrastive learning approach (Positive vs. Negative data phases) to compare against PC-ALM’s continuous dynamics.
*   **Residual MLP Parameterizations:** (Innocenti et al., 2026) - Port the specific weight initialization and scaling factors (e.g., $\gamma_0$) used to stabilize 1000-layer networks, as standard initializations fail at this depth.

---

### **6. Attribution & Compliance**

**License Compliance:**
The PC-ALM reference implementation is released under the **MIT License**. This is a permissive license that allows Computronium to:
*   Use, copy, modify, and merge the code.
*   Distribute and sublicense the code.
*   Use the code for commercial purposes.
*   **Requirement:** We must include the original copyright notice and permission notice in all copies or substantial portions of the software.

**Proper Attribution:**
All documentation, publications, and derivative code within Computronium must cite the original research.

**BibTeX Citation:**
```bibtex
@misc{seely2026pc-alm,
  title         = {Augmented Lagrangian Predictive Coding},
  author        = {Jeffrey Seely and Julian Gould},
  year          = {2026},
  eprint        = {2605.31022},
  archivePrefix = {arXiv},
  primaryClass  = {cs.LG},
  url           = {https://arxiv.org/abs/2605.31022},
}
```

**Code Header:**
```python
# Portions of this module are derived from PC-ALM.
# Copyright (c) 2026 Sakana AI
# Original Authors: Jeffrey Seely, Julian Gould
# License: MIT
# Paper: https://arxiv.org/abs/2605.31022
```
