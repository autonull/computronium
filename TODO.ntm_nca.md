Yes. Both are implementable in/around Plasticity, but they are **not equally valuable for the TODO14 agenda**.

### Recommendation

| Architecture                             |             Implement? |   Priority | Why                                                                                                                     |
| ---------------------------------------- | ---------------------: | ---------: | ----------------------------------------------------------------------------------------------------------------------- |
| **Neural Cellular Automata (NCA)**       |                **Yes** |   **High** | Excellent fit for local credit, locality, iterative dynamics, spatial/temporal credit, and O(1)-memory claims           |
| **Neural Turing Machine (NTM)**          | **Yes, but minimally** |     Medium | Strong test of local credit on differentiable external memory; potentially compelling if learned without BPTT/global CE |
| **Differentiable Neural Computer (DNC)** |              **Later** | Medium/Low | More complex NTM; useful only after the simpler memory experiment succeeds                                              |

The important point is that these should **not** become generic "let's implement famous architectures" projects. They should be used as **adversarial testbeds for the project's thesis**.

## 1. NCA is unusually well matched

An NCA is almost tailor-made for the question TODO14 is asking.

![Image](https://images.openai.com/static-rsc-4/mfd9QLRHaTvamsB5lvIcWmTrYM4oCkk2FGsdW-vMm2jnuuUbLjqz5-Zd1-vEebqHHxtF7vLHU0_8HTaAbulQ6I7qvPYt_OOKQHU2XDVUH3bFGJqPEPN4OnjcQ4MGJqfsMnT21yG6qTMYffRr9Ff3N_AeBgNfuPozHY8jVGzcLj2VkCFDP7n4Plkkvyv4JF1G?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/OJ2snhxjwYBi5RaJMK7W2Nx5P4mrp8vJiRIyeYk2aziHirws5pMruXVh8rKjBdTCVX4fR8evtMXYTibh5-h_qNMsKqG1NGXQVI_uN5z3Jcu-7ympCtPuQ4q4N1FLYNAypuL8wK4gCo2INqOc7l1kTzv-5b93xLsoGOe-FLAU7oYeD4xYgR-D5hy89-OTxOJw?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/bmX6ROk6ltYiBhuEBcXg9m8SiQMWLV3CEhIs3IgGthXss1FhAQ_RvGx_ii8UUZiJ1U-S6RQD7TVOKRJ9fa8q0LiToe--Slwli2AKjMyw_VTwlJox2babEMTkU4ItKsn5Fru66fDQ-a34wUAywVm0B-txDCFKqnpVJK9HIV6xK7aoPO4pOMd68d-WdDez64Nc?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/N1IWZPWuRQ1Fam3-DunTJDutV8xtrixrmCFlUI52oYPCvH2vQuVurskEmYXovNY3Ta1J0v7wlch7bBGcddoyevKv63VbZjUKv3XB3n7pTrtEfH6ddNf9_-p2yokPq5mpg8V5GHcwN5BHSlbXDLl62w6sZeS2MZ8bIxNpHIUOXy7pM8rxHM7DVp3C6rbU-Lvf?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/Dctv2Q-ADi8RJMol_fVk4H8l86n89SGe_h2hg4WHvmi-urxVgePWKchwfor2q61462jiWq5zOhmWj5KQNv-eWTbOEE4n-N_z6lcQ7z05XgqlwgC5nZ_fB6ODLfYrH8_UsJkiynQsiKgEh8y0oCIgC0lQwBvsrshWl7Uxxj4aewJ1gzgDG7N76Ekky2NdtFZX?purpose=fullsize)

Each cell receives a local neighborhood, applies a learned update, and repeatedly modifies its state. That gives you:

* **strict locality**
* weight sharing across space
* recurrent/iterative computation
* long-horizon credit assignment
* emergent global behavior from local updates
* potentially enormous numbers of local learning sites
* an especially clean comparison against BPTT

That makes NCA a much better experimental vehicle for the project's central claim than simply adding another feed-forward benchmark.

### The killer experiment

Train an NCA to perform something that requires **long-range/global coordination**, while restricting learning to local information.

For example:

1. **Pattern regeneration**

   * damage part of an organism/image
   * let the NCA reconstruct it

2. **Growth / morphogenesis**

   * seed → target morphology

3. **Persistent memory**

   * encode information in a spatial pattern
   * perturb it
   * recover it

4. **Maze / path propagation**

   * local cells must collectively discover a global solution

5. **Classification through emergent state**

   * local updates ultimately produce a global readout

Then compare:

* BP/BPTT
* local contrastive
* Hebbian
* μPC
* `ff_hybrid`
* degenerate pseudo-gradients
* Muon / OrthoAdam

The particularly interesting question is:

> **How much can a completely local learning rule accomplish when the computation itself is also local and recurrent?**

That is almost a laboratory instrument for the project's thesis.

---

# 2. NTM/DNC: also valuable, but for a different reason

![Image](https://images.openai.com/static-rsc-4/-mXoIimC7LI6DZIGJn4IGo9Xy8OxfCFqEdsBo0Gmz2MmkCqxa9GWWX_anKv4VgnWUeBkqWP_1Gs5RK_pTbk0-mO7hFZc7mfaYCqByS-sNEd0lA4su9O-m59rZ5LkQsQfYJDoXkyGuwyx-P_Hiyd5ysVGUSff25CukgvDX21QvktE1Tn4GtHsYz4R_agROzfW?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/F_zcGj0uuh20RD7NJ7jmdP02nVEznKcL57ujRhOYFpd67A6M2h5LousgkSnaUX5nhdquVooshl3k3oxKwi3BM5K5BD3GI4locyTX1zx50Vepo0qf9qbLzXXIfQ-TzQ9aB4TkXu8aLISb1TAY9ymMPuAqx1EZW3G_9HnwQ43pzWM7b2FLiluagwhtq2K22s4z?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/VnTViVLcxoumjzEIXf4LIRvh2DgIB7G4fLaPOVVSJSveeAR7SA8TeaYC2s0hSjZNuV_pNOsV8FdBuy4RK3nAeoK6Fs5WlXGMOFrDgLeQm-mqCvGPl_tIRrRQdsCjBAp9GmAIOZ_rZbbXHwu2Xl0_MTeu9OMGk50YzYzApjxJe7_jDJTPMFN0sg4yz57JDn6G?purpose=fullsize)

![Image](https://images.openai.com/static-rsc-4/IgptZYxbzX7LAdB7clD6JTp2fYMfFJJPEcnSgut5TCqevQUXPD6Q-vJzlNolkzCQmk29eJCXeuD_TWBE2mhqfKApgOuGnb4rKCmFzIM2HBMQ_BgRxxmib2CiWWgK6_b3d500iY3YYvfodcL-hA-FI2wHbJFK0rZIi9reZ3jMD1V_FIiCV6A0Wk5M4hwGF3pP?purpose=fullsize)

NTM/DNC introduces something NCA doesn't:

**explicit differentiable external memory.**

That gives you a very interesting stress test:

> Can local credit learn a controller that learns to **write, read, retrieve, and manipulate information in an external memory**, without conventional BPTT?

That's substantially harder than ordinary supervised prediction.

### Start with NTM, not DNC

Implement a deliberately small NTM:

```text
input
  ↓
controller
  ↓
┌───────────────┐
│ read head     │
│ write head    │
└───────┬───────┘
        ↓
 external memory
        ↓
     output
```

Use the classic algorithmic tasks:

* copy
* repeat-copy
* associative recall
* priority sort

These are ideal because they distinguish **actual algorithmic memory** from ordinary statistical prediction.

---

# 3. The really interesting version for Plasticity

I would **not** initially implement an NTM exactly as traditionally trained.

Instead, factor it into independently trainable local modules:

```text
                 ┌──────────────┐
input ──────────►│ controller   │
                 └──────┬───────┘
                        │
                 local targets
                        │
            ┌───────────┴───────────┐
            ▼                       ▼
       read controller        write controller
            │                       │
            └───────────┬───────────┘
                        ▼
                 external memory
                        │
                        ▼
                      output
```

Then ask whether Plasticity's learning rules can train:

* controller representation
* key generation
* addressing
* read/write gates
* memory contents
* output projection

**without sending the global loss backward through the entire computational history.**

That is much more aligned with TODO14.

---

# 4. There is an even better combined experiment

The most interesting project may actually be:

## **Local-credit Neural Cellular Computer**

Combine the two ideas.

Have an NCA-like controller interact with an external memory:

```text
        spatially local neural field
      ┌────────────────────────────┐
      │  ○─○─○─○─○─○─○─○─○─○     │
      │  ○─○─○─○─○─○─○─○─○─○     │
      │  ○─○─○─○─○─○─○─○─○─○     │
      └────────────┬───────────────┘
                   │
             local controller
                   │
             ┌─────┴─────┐
             │ read/write│
             │  memory   │
             └───────────┘
```

Now the project is testing something much more ambitious:

> **Can useful computation emerge from local learning rules in a system with both distributed state and persistent external memory?**

If yes, that's far more interesting than "we implemented an NTM."

---

# 5. Plasticity is particularly useful here

This is one place where Plasticity's architecture could become a real experimental advantage rather than merely an implementation convenience.

The desired abstraction is roughly:

```python
layer = LocalLayer(
    update_rule=...,
    optimizer=Muon(...),
    target_rule=...
)
```

while the architecture supplies:

```python
NCA(...)
NTM(...)
DNC(...)
```

Then the **architecture and credit mechanism can be independently crossed**.

That gives you a matrix like:

| Architecture | BP | μPC | local contrastive | Hebbian | random-ish |
| ------------ | -: | --: | ----------------: | ------: | ---------: |
| MLP          |  ✓ |   ✓ |                 ✓ |       ✓ |          ✓ |
| Transformer  |  ✓ |   ✓ |                 ✓ |       — |          — |
| NCA          |  ✓ |   ? |                 ? |       ? |          ? |
| NTM          |  ✓ |   ? |                 ? |       ? |          ? |
| DNC          |  ✓ |   ? |                 ? |       ? |          ? |

That is scientifically much stronger than adding isolated demos.

---

# 6. What I would add to TODO14

I'd add a new major workstream:

### **W5 — Local Credit on Stateful / Emergent Computers**

**W5.1 — Neural Cellular Automata**

* minimal NCA implementation
* BP/BPTT baseline
* local-credit training
* long-horizon regeneration
* morphogenesis
* damage/recovery
* measure credit degradation vs rollout length

**W5.2 — NCA optimizer interaction**

* SGD
* Adam
* OrthoAdam
* Muon
* deliberately degraded pseudo-gradients
* identify optimizer-dominance boundary

**W5.3 — Neural Turing Machine**

* minimal differentiable external memory
* copy
* repeat-copy
* associative recall
* local controller credit
* compare BPTT vs local rules

**W5.4 — Memory-credit scaling**

* sequence length
* memory size
* number of recurrent steps
* locality radius
* controller depth

**W5.5 — DNC**

* only after NTM succeeds
* dynamic memory allocation
* temporal links
* content addressing
* test whether local credit survives the additional machinery

**W5.6 — Unified local-learning computer**

* NCA controller + external memory
* test whether local learning can produce persistent, distributed computation

---

## Priority order I'd actually use

**1. NCA first.**
It is cheap, conceptually clean, and almost perfectly aligned with the project's locality thesis.

**2. NTM copy task.**
This is the first serious "can local credit learn an algorithm?" challenge.

**3. NCA long-horizon / damaged-regeneration experiments.**
This directly attacks the temporal-credit objection.

**4. NTM associative recall.**
Now memory addressing rather than simple copying matters.

**5. DNC.**
Only if NTM produces a meaningful result.

**6. NCA + external memory.**
This is the moonshot.

### One particularly important addition

For both NCA and NTM, **retain a BP/BPTT implementation as a gold-standard control**. The objective isn't to make local learning look good by choosing favorable tasks. It is to ask where the local method genuinely breaks.

That makes the eventual result much stronger:

> *Here is the maximum temporal/spatial complexity that local credit can learn, here is the optimizer dependence, here is where it fails, and here is the surprising regime where it beats or matches BPTT.*

That would fit TODO14 considerably better than treating NTM/DNC/NCA as ordinary architecture ports.
