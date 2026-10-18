# Computronium: Formal Proof Research Specification

Research plan · Rocq proof assistant · Computational theory · Architecture and plasticity

## 1. Research objective

The objective is to identify and carry out the formal proof research that can establish whether Computronium's architectural ideas have genuine mathematical substance, particularly its plasticity axis, its Z3-inspired separation between persistent machinery and changing computational state, and the possibility of using those ideas to construct more capable learning and computing systems.

The goal is not merely to demonstrate that a system can execute a computation. It is to establish precisely what its architecture permits, what constraints it imposes, what capabilities follow mathematically, and which properties might distinguish it from existing approaches.

The research should produce machine-checked theorems in Rocq wherever practical, with explicit assumptions and executable counterexamples where a proposed claim is false.

There are several distinct research questions:

- Computational power: Can a system with fixed persistent parameters and evolving plastic state simulate a universal computing machine?
- Architectural significance: Does the plasticity mechanism add capabilities, or merely provide another representation of computation already possible in the underlying system?
- Plasticity theory: Can we characterize the tradeoffs between adaptation, stability, memory, and control?
- Learning theory: Can plasticity provide formal guarantees about online adaptation, retention, or generalization under suitable assumptions?
- Computational efficiency: Can the architecture perform particular computations with fewer resources, fewer updates, or simpler mechanisms?
- Framework validity: Can the Computronium ontology and its axes be given rigorous semantics, with provable relationships among architectural choices?

A central distinction must govern the entire project:

Proving that an architecture is Turing complete establishes what it can compute in principle. It does not establish that it learns algorithms efficiently, generalizes well, or outperforms other architectures.

Those are separate research programs, and the specification below treats them separately.

## 2. What the repository already establishes—and what remains open

The current README makes the research opportunity more concrete than a generic investigation of recurrent networks.

Computronium explicitly models six axes:

\\[ \mathcal{A}=S\times G\times D\times P\times C\times U \\]

where \\(S\\) is substrate, \\(G\\) geometry, \\(D\\) state dynamics, \\(P\\) plasticity, \\(C\\) credit assignment, and \\(U\\) parameter updates. Plasticity is intended to elevate the computational rule itself to a dynamical variable, represented by a changing state \\(\psi\\) on persistent machinery \\(\theta\\). The README also identifies a frozen-\\(\theta\\) contract, experimental probes of plasticity expressiveness, and existing stability analyses.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

autonull/computronium · GitHub

+1



That gives us a much more useful starting point than trying to prove one broad claim about “plasticity.”

| Repository component                       | Formal research opportunity                                                                                |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| Six-axis ontology                          | Prove that the composition has well-defined semantics and that axis changes preserve specified invariants. |
| RuleStatePlasticity                        | Formalize rule selection and prove which computations the mechanism can represent.                         |
| Frozen-\\(\theta\\), evolving-\\(\psi\\)   | Prove exact parameter invariance and characterize the computation enabled by the changing state.           |
| External memory and writable program state | Establish memory bounds, universality conditions, and impossibility results under bounded state.           |
| Temporal plasticity                        | Prove conditions for adaptation, forgetting, and task-state reset.                                         |
| Coupled dynamics                           | Prove convergence, stability, robustness, or bounded-error properties under explicit assumptions.          |
| Learning and credit assignment             | Prove that particular update rules optimize their stated objectives or provide local learning guarantees.  |
| Substrate constraints                      | Prove correctness and error bounds for quantized, noisy, sparse, or otherwise constrained computation.     |

The repository describes the plasticity expressiveness probes as preliminary, and explicitly treats superiority over conventional memory as an open empirical question. Its stability and frozen-parameter checks also have different verification strengths: sampled tests are not machine-checked mathematical proofs.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://github.com\&sz=32)

autonull/computronium · GitHub



One important historical qualification shapes the first project. Raúl Rojas's Z3 result is a simulation argument involving arithmetic operations, a fixed program loop, and techniques for eliminating conditional branching. It establishes universality under a specified abstract model, not a claim that every finite physical implementation can compute indefinitely with unlimited memory.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://www.researchgate.net\&sz=32)

ResearchGate

+1



For Computronium, therefore, we should prove a theorem about a precisely specified abstract machine, then separately prove that the implemented architecture refines that machine.

## 3. Complete research program

The following specification is designed to be usable as a standalone research document and implementation plan. It separates proof projects that can be attempted immediately from deeper projects whose success depends on what the formal model reveals.

# Computronium Formal Proof Research Program

**Version:** 1.0\
**Date:** October 17, 2026\
**Primary proof assistant:** Rocq\
**Repository:** [https://github.com/autonull/computronium](https://github.com/autonull/computronium)\
**Primary research areas:** computational universality, RuleStatePlasticity, dynamic computational rules, architectural compositionality, learning dynamics, stability, and resource-bounded computation.

## 1. Mission

Develop a machine-checked mathematical foundation for Computronium that establishes:

1. What its six-axis architecture means mathematically.
2. What computational capabilities arise from each axis and their interactions.
3. Whether RuleStatePlasticity supports universal computation under explicit assumptions.
4. What the separation between persistent parameters (\theta) and evolving plastic state (\psi) actually guarantees.
5. Which capabilities require plasticity, which can be implemented without it, and which require additional memory or computational resources.
6. Whether useful guarantees can be proved for adaptation, retention, stability, precision, and learning.
7. Which claims are false, underspecified, redundant, or dependent on unrealistic assumptions.

The objective is a reusable Rocq development, not merely a collection of isolated proofs.

## 2. Foundational principles

### 2.1 Formalize the actual architecture

The proof must describe the implemented mechanism rather than an idealized mechanism that happens to be easier to prove.

For each primitive, document its state, parameters, transition function, assumptions, and observable behavior.

If the implementation differs from the mathematical model, either establish a refinement theorem connecting them or explicitly label the result as applying only to the abstract model.

### 2.2 Distinguish four different claims

**Computability:** Can the architecture compute a specified function?

**Expressiveness:** What family of functions or state transitions can it represent?

**Efficiency:** How many operations, memory cells, bits, or state updates does it require?

**Learnability:** Can a specified learning process discover a useful configuration within a reasonable resource budget?

These are separate properties. Proving one does not establish the others.

### 2.3 Make all resource assumptions explicit

Every theorem about universality must specify:

- Whether persistent parameters are finite or may grow.
- Whether the plastic state has finite or unbounded capacity.
- Whether numeric values have exact or finite precision.
- Whether transition functions are arbitrary or drawn from a restricted class.
- Whether inputs and observations are available indefinitely.
- Whether the system has access to a clock or unbounded step counter.
- Whether configuration is supplied in advance or must be learned.
- Whether the proof concerns termination, partial computation, or an infinite stream.

A theorem that assumes an unbounded tape does not establish universality for a fixed-size state vector.

### 2.4 Prefer exact models before approximate models

Begin with finite symbolic machines and exact arithmetic. Introduce floating-point behavior, stochastic transitions, and hardware effects only after the relevant abstract theorems are established.

### 2.5 Treat negative results as successful outcomes

If a proposed capability follows entirely from an existing component, establish that fact. If universality is impossible under a finite-state restriction, prove the limitation. If an axis is only an organizational abstraction, characterize its mathematical scope without assuming it creates new computational power.

---

# Part I — Foundational semantics

## 3. F0: Formal inventory and proof-gap analysis

**Priority:** P0 — prerequisite\
**Difficulty:** Low to moderate\
**Expected result:** A verified inventory of existing formal claims and assumptions.

### Questions

- What has already been defined in Rocq?
- Which definitions correspond to actual repository components?
- Which theorems are proved, admitted, axiomatized, or merely stated?
- Do the current definitions model the six axes, frozen parameters, evolving plastic state, or a different abstraction?
- Which results can be reused without changing their assumptions?

### Tasks

1. Inventory all `.v` files, modules, definitions, lemmas, and theorems.
2. Record every use of `Admitted`, `admit`, custom axioms, or assumptions introduced through imported modules.
3. Identify dependencies on classical logic, functional extensionality, choice, or external libraries.
4. Trace each existing theorem to the repository claim it is intended to support.
5. Establish a clean, reproducible build of the existing proof development.
6. Create a dependency graph showing which unproved results block which research objectives.

### Deliverables

- `docs/formal/PROOF_INVENTORY.md`
- `docs/formal/PROOF_GAPS.md`
- A clean-build command and CI gate.
- A table mapping repository claims to formal definitions and proved results.

### Acceptance criteria

Every theorem reported as machine-checked must compile in the declared environment, and all nontrivial assumptions must be visible in its statement or dependency record.

Do not begin by replacing Rocq or rewriting working proofs. Determine the existing development's actual state first.

## 4. F1: Formal semantics of the six-axis ontology

**Priority:** P0\
**Difficulty:** Moderate\
**Expected result:** A compositional mathematical model of Computronium systems.

### Mathematical model

Define an architecture as a tuple

[\
A=(S,G,D,P,C,U)\
]

where each component has a type and an associated operational contract.

For an executable system, define:

- A state space (Z).
- An input space (I).
- An output space (O).
- A parameter space (\Theta).
- A plastic-state space (\Psi).
- A transition relation or transition function.
- An observation function.

A useful initial model is

[\
F_A:\Theta\times Z\times I\rightarrow Z\
]

with outputs determined by

[\
o_t=R_A(\theta,z_t,i_t).\
]

The state may be decomposed as

[\
z_t=(x_t,\psi_t,\sigma_t),\
]

where (x_t) is activity, (\psi_t) is plastic state, and (\sigma_t) is substrate state.

These definitions should be refined to match the repository's actual interfaces.

### Theorems to prove

**F1.1 — Totality or explicit partiality**

Every transition is defined for all states and inputs allowed by its contract, or the model explicitly represents failure and undefined transitions.

**F1.2 — Composition correctness**

When two compatible components are composed, the resulting transition agrees with the documented composition semantics.

**F1.3 — Interface compatibility**

An invalid axis combination cannot silently satisfy the well-formed-system predicate.

**F1.4 — Null-plasticity embedding**

A system using `NullPlasticity` behaves exactly as its corresponding five-axis system under a defined correspondence between their states.

**F1.5 — Axis replacement**

Replacing one component while holding the others fixed changes only the transition dependencies authorized by the composition interface.

**F1.6 — Observational equivalence**

Define when two architectures produce identical observable behavior for every allowed input sequence, even if their internal states differ.

### Research value

These results would establish whether the ontology is a mathematically meaningful compositional interface rather than merely a catalog of named mechanisms.

They would also create a foundation for all subsequent theorems.

## 5. F2: Formal semantics of persistent parameters and plastic state

**Priority:** P0\
**Difficulty:** Moderate\
**Expected result:** A precise, reusable model of frozen-(\theta), evolving-(\psi) computation.

Define an episode as a sequence of transitions

[\
(\theta,z_t,i_t)\mapsto(\theta,z\_{t+1}).\
]

The defining invariant is

[\
\theta\_{t+1}=\theta_t.\
]

Plastic state may evolve according to

[\
\psi\_{t+1}=Q\_\theta(z_t,i_t).\
]

The function (Q\_\theta) is fixed during the episode, but its outputs can change with the state and inputs.

### Theorems

**F2.1 — Parameter invariance**

For every finite execution trace, the persistent parameters at every step equal their initial values.

**F2.2 — Invariance under arbitrary trace length**

The preceding property holds for every finite prefix of an execution, without a fixed maximum episode length.

**F2.3 — State-update correctness**

Every plastic-state transition follows the declared update rule.

**F2.4 — Lifecycle separation**

Episode initialization, within-episode adaptation, reset, and optional between-episode consolidation are distinct transitions with explicit contracts.

**F2.5 — Reset isolation**

If reset is intended to clear (\psi) without changing (\theta), prove that it does so exactly.

**F2.6 — Parameter integrity**

No transition in the frozen-parameter machine can modify persistent parameters, including through indirect state aliases in the abstract semantics.

The last theorem is a property of the mathematical model. The Python implementation additionally needs an implementation-level refinement or audit argument.

### Required distinction

The symbol (\theta) must include every quantity claimed to remain fixed. If substrate variables, gates, optimizer state, or routing configuration can change, determine whether they belong to (\theta), (\psi), or another explicitly mutable state component.

A theorem about frozen neural-network weights alone is not a theorem about the entire persistent machinery.

---

# Part II — The Z3 connection and computational universality

## 6. F3: Reconstruct and formalize the Z3 simulation argument

**Priority:** P0\
**Difficulty:** Moderate to high\
**Expected result:** A machine-checked account of the exact universality result being used as inspiration.

### Research question

What precise abstract machine does the cited Z3 argument establish to be universal, and what assumptions are necessary for that result?

### Tasks

1. Identify the exact version of the Z3 simulation argument to formalize.
2. Specify its arithmetic instruction set.
3. Specify its memory and addressing model.
4. Specify the program-loop mechanism.
5. Define the source machine being simulated.
6. State the simulation relation between source and target configurations.
7. Prove that each source transition is simulated by a finite target execution.
8. Prove preservation of observable outputs and halting behavior.

### Important qualification

Rojas's result uses arithmetic operations and techniques for simulating branching and indirect addressing in a fixed-loop program. The historical paper describes universality for machines with a specified finite tape bound, with the tape-program size growing significantly as the bound increases.

Do not silently strengthen this into a claim that the literal physical Z3 has infinite memory, infinite precision, or unrestricted modern-machine behavior.

### Suggested formal interface

Define a source machine:

```
SourceConfig
SourceStep
SourceRun
SourceHalts
```

Define the arithmetic target machine:

```
TargetConfig
TargetInstruction
TargetStep
TargetRun
```

Define a relation

```
Simulates : SourceConfig -> TargetConfig -> Prop
```

Prove a forward-simulation theorem:

[\
\operatorname{Simulates}(c,d)\
\land c\rightarrow c'\
\implies\
\exists d'.\ d\rightarrow^{+}d'\
\land\operatorname{Simulates}(c',d').\
]

The exact transition counts and arithmetic assumptions must be specified by the chosen machine model.

### Acceptance criteria

The theorem must identify exactly which version of universality has been proved and must not depend on an undocumented ability to branch, address arbitrary memory, or represent unbounded integers.

## 7. F4: Formalize RuleStatePlasticity

**Priority:** P0 — central research objective\
**Difficulty:** Moderate to high, depending on the actual implementation\
**Expected result:** A precise computational model of the repository's Z3-inspired plasticity mechanism.

The README describes `RuleStatePlasticity` as a mechanism for rule selection, with the program represented as writable data on fixed machinery.

This description is a hypothesis to formalize, not yet a theorem.

### Define the machine

At minimum, specify:

- A fixed transition mechanism (F\_\theta).
- A plastic state (\psi).
- An input (i_t).
- A rule-selection function (r_t=\operatorname{select}(\psi_t,i_t)).
- A state-update function.
- An output function.
- A definition of which parts of the rule are mutable.
- A definition of what counts as executing an algorithm.

The resulting machine might have the form

[\
\begin{aligned}\
r_t &= \operatorname{select}(\psi_t,i_t),\\\
z\_{t+1} &= F\_\theta(z_t,i_t,r_t),\\\
\psi\_{t+1} &= Q\_\theta(\psi_t,z_t,i_t).\
\end{aligned}\
]

This is only a candidate specification. Replace it with the actual transition semantics used by Computronium.

### Required lemmas

**F4.1 — Rule-selection determinacy**

Under deterministic assumptions, a given state and input select a unique rule.

**F4.2 — Rule-state transition correctness**

Each selected rule induces the transition declared by the semantics.

**F4.3 — Frozen-machinery invariant**

Rule selection and plastic-state updates do not change the persistent mechanism.

**F4.4 — State representation**

Prove the correspondence between the encoded plastic state and the abstract rule, instruction, or machine configuration it represents.

**F4.5 — Multi-step simulation**

A sequence of plastic-state updates simulates a sequence of abstract machine transitions.

**F4.6 — Observable correctness**

The outputs of the plasticity machine agree with those of the simulated machine.

### Central research question

Does (\psi) encode merely a selection among a finite set of predefined behaviors, or can it encode and manipulate the data and control state needed to implement arbitrary computations?

Both are meaningful architectures. They imply different theorems.

A finite selector can be useful without being universal. A universal machine needs an appropriate state representation, transition mechanism, and memory model.

## 8. F5: Prove or refute universality of RuleStatePlasticity

**Priority:** P0\
**Difficulty:** High\
**Expected result:** Either a constructive universality theorem or a rigorous limitation result.

### Preferred theorem

Let (M) be a specified universal machine and (R\_\theta) the fixed Computronium machine.

Prove that there exists an encoding (E) from configurations of (M) into states of (R\_\theta) such that every source transition can be simulated by a finite target execution.

A useful statement is:

[\
E(c)=z\
\land c\rightarrow_M c'\
\implies\
\exists z'.\
z\rightarrow\_{R\_\theta}^{+}z'\
\land E(c')=z'.\
]

Also prove that the simulation preserves termination and outputs, under the stated encoding.

### Two possible routes

**Route A — Direct simulation**

Construct an encoding of a Turing machine's tape, head position, control state, and transition table within (\psi) and any permitted memory.

Prove that each simulated step preserves the encoding invariant.

**Route B — Transfer of universality**

Prove that RuleStatePlasticity can faithfully simulate the abstract arithmetic machine established in F3. Then transfer the universality result through composition of simulations.

Route B may be shorter if the plastic-state mechanism naturally supports the arithmetic target's operations. It is not automatically easier: the key difficulty is still establishing that the actual plasticity mechanism can implement every required target operation.

### Separate variants

Attempt these theorems independently:

1. **Fixed (\theta), unbounded (\psi):** Universality may be possible if the fixed transition mechanism can manipulate the required memory.
2. **Fixed (\theta), bounded (\psi), unbounded external memory:** Determine whether the external memory and its access rules suffice.
3. **Fixed (\theta), finite (\psi), finite input alphabet:** Establish the finite-state limitation when the complete machine has only finitely many configurations.
4. **Fixed finite-precision hardware:** Determine what can be proved for the actual finite-state implementation.
5. **Restricted rule library:** Characterize universality for the specific available rule set rather than assuming arbitrary transitions.

### What would count as success?

A successful theorem would establish that a specified RuleStatePlasticity machine simulates a universal machine while its persistent machinery remains fixed.

It would not establish that the learned rule configuration is easy to discover, that the machine is efficient, or that plasticity increases the set of computable functions relative to an already universal baseline.

Those require separate results.

## 9. F6: State-capacity and impossibility theorems

**Priority:** P1\
**Difficulty:** Moderate\
**Expected result:** A rigorous characterization of the limits imposed by bounded state.

### Questions

- Can a finite plastic state support unbounded computation?
- What changes when external memory is available?
- Is the state update invertible, lossy, or capable of retaining an unbounded history?
- Which results depend on arbitrary-precision arithmetic?

### Theorems

**F6.1 — Finite-state limitation**

For a deterministic machine with finitely many total configurations, prove that every infinite execution eventually repeats a configuration and therefore repeats its future trajectory.

**F6.2 — Periodicity**

Under the same assumptions, prove eventual periodicity of the execution.

**F6.3 — Memory lower bound**

For a task requiring (N) distinguishable internal situations, prove that at least (\lceil\log_2 N\rceil) bits of distinguishable state are required, under a model where these situations must be distinguished by future behavior.

**F6.4 — External-memory dependency**

Compare the machine with and without writable external memory and characterize the capabilities supplied by that memory.

**F6.5 — Precision dependency**

Establish whether a universality argument depends on exact integer or rational arithmetic, arbitrary-precision values, or idealized real numbers.

### Research value

These results prevent an important category error: treating a mathematical model with unlimited representational capacity as proof that a fixed-size neural or physical device has the same capabilities.

---

# Part III — Plasticity as an architectural dimension

## 10. F7: Characterize the expressive power of plasticity mechanisms

**Priority:** P1\
**Difficulty:** Moderate to high\
**Expected result:** A hierarchy of formal capabilities across the plasticity axis.

Study each existing primitive independently:

- `NullPlasticity`
- `RoutingPlasticity`
- `FastWeightPlasticity`
- `SubstrateCoupledPlasticity`
- `RuleStatePlasticity`
- `ClosedFormRidgePlasticity`
- `TemporalPsiPlasticity`

Do not assume these mechanisms form a simple linear hierarchy. Different mechanisms may be incomparable.

### Define an expressiveness relation

For two systems (A) and (B), define

[\
A\preceq B\
]

when every behavior implementable by (A), under a declared resource model, can be simulated by (B) with an explicitly specified resource overhead.

The definition must say whether it compares:

- Computable input-output functions.
- State-transition systems.
- Online adaptation behaviors.
- Resource-bounded computations.
- Learning procedures.

These are different comparisons.

### Theorems

**F7.1 — Zero-plasticity embedding**

The `NullPlasticity` model is embedded in the general six-axis semantics.

**F7.2 — Routing simulation**

Determine which state-dependent routing behaviors can be represented by a fixed architecture with explicit routing state.

**F7.3 — Fast-weight equivalence or separation**

Determine when episode-local fast weights are equivalent to explicit memory and when the parameterization restricts their behavior.

**F7.4 — Rule-state separation**

Determine whether RuleStatePlasticity represents behaviors that a particular restricted routing or memory mechanism cannot represent under the same resource constraints.

**F7.5 — Temporal-plasticity characterization**

Prove which state histories can be retained, forgotten, or distinguished by trace-decayed plasticity.

**F7.6 — Pairwise simulation matrix**

Construct a matrix of proved simulation relationships among the primitives. Leave incomparable pairs unresolved unless a separation theorem is available.

### Critical interpretation

If two architectures are both unrestricted universal machines, they may have the same computability power while differing dramatically in practical efficiency, learnability, locality, or hardware compatibility.

A computability-equivalence result therefore does not make the plasticity axis uninteresting. It identifies which other properties need to be studied.

## 11. F8: Prove properties of plastic-state lifecycle control

**Priority:** P1\
**Difficulty:** Moderate\
**Expected result:** A formal account of plastic-state initialization, adaptation, decay, reset, and consolidation.

### Theorems

**F8.1 — Episode isolation**

Plastic state from one episode cannot influence another when reset is specified to clear all relevant mutable state.

**F8.2 — Exact reset**

A reset maps every permitted plastic state to the declared initial state.

**F8.3 — Bounded retention**

Under a stated decay rule, prove a bound on the contribution of past updates to the current state.

**F8.4 — Forgetting bound**

For a specified linear or contractive update, prove a bound on how rapidly the effect of an earlier input diminishes.

**F8.5 — Persistence condition**

Determine the conditions under which a stored state survives an interval without updates.

**F8.6 — Consolidation separation**

Prove that episode-local updates preserve (\theta), while explicitly authorized consolidation changes it only at designated boundaries.

### Scope

Start with exact finite-dimensional linear or discrete models. General nonlinear plasticity rules should be handled separately and only after the necessary assumptions are identified.

## 12. F9: Stability–plasticity tradeoffs

**Priority:** P1\
**Difficulty:** Moderate to high\
**Expected result:** Conditional theorems about adaptation, forgetting, and stability.

The objective is not to prove that more plasticity is always beneficial. It is to establish conditions under which a specified mechanism is stable, adapts, or loses previous information.

### Candidate results

**F9.1 — Contractive dynamics**

If a transition operator is contractive under a specified metric, prove existence and uniqueness of a fixed point where the relevant completeness and continuity assumptions hold.

**F9.2 — Perturbation bound**

Bound the change in a trajectory due to a bounded change in input or initial state.

**F9.3 — Stability under plastic updates**

Find sufficient conditions under which state-dependent changes in the computational rule preserve a stability property of the original dynamics.

**F9.4 — Instability counterexample**

Construct a small system where unrestricted plastic-state updates destabilize an otherwise stable process.

**F9.5 — Retention–adaptation incompatibility**

Investigate formal conditions under which a single bounded-memory mechanism cannot perfectly retain arbitrary past information while also adapting to arbitrary new information.

State the task class and memory assumptions precisely. Do not claim a universal impossibility theorem without proving the relevant quantifiers.

**F9.6 — Stability–expressiveness frontier**

For a specified finite model family, characterize the relationship between permitted transition dynamics and the behaviors they can represent.

This final result may be a finite classification theorem rather than a general theorem about all learning systems.

---

# Part IV — Learning theory and credit assignment

## 13. F10: Formal correctness of plasticity update rules

**Priority:** P1\
**Difficulty:** Moderate\
**Expected result:** Proofs of exact update properties for selected mechanisms.

For each rule, define the mathematical update independently of its Python implementation.

### Initial targets

1. Closed-form ridge plasticity.
2. Temporal trace-decayed plasticity.
3. Fast-weight updates.
4. Routing or gating updates.
5. Substrate-coupled updates.

### Candidate theorems

**F10.1 — Closed-form ridge solution**

Under the specified matrix assumptions and regularization conditions, prove that the computed state minimizes the stated ridge-regression objective.

**F10.2 — Uniqueness**

Prove uniqueness when the objective is strictly convex, or characterize the conditions under which multiple minimizers exist.

**F10.3 — Temporal recurrence**

Prove that the implemented trace update equals its stated closed-form recurrence over a sequence of observations.

**F10.4 — Decay bound**

Derive an explicit bound on residual influence after (k) update-free steps for the chosen trace rule.

**F10.5 — Update invariants**

Prove constraints such as bounded norms, nonnegative quantities, or preserved sparsity when the update is designed to maintain them.

**F10.6 — Objective descent**

For a selected update rule, prove descent of the declared objective under explicit assumptions about step size, smoothness, and the update direction.

Do not assume that an arbitrary local learning rule decreases global training loss.

## 14. F11: Formal learning guarantees under changing environments

**Priority:** P2\
**Difficulty:** High\
**Expected result:** Conditional guarantees for online adaptation.

This research area is especially relevant to reinforcement learning, robotics, and continual learning, but it should start with simpler online prediction problems.

### Candidate projects

**F11.1 — Finite-horizon online adaptation**

Define a bounded task family and prove a regret or prediction-error bound for a particular plasticity mechanism.

**F11.2 — Distribution-shift response**

Under a declared change model, bound the adaptation time or prediction error after a shift.

**F11.3 — Task interference**

Characterize when updates for one task alter behavior on another task.

**F11.4 — Memory-assisted adaptation**

Prove a benefit from an explicit memory mechanism for a narrowly defined task class, or establish a lower bound showing the memory requirement.

**F11.5 — Plasticity versus no plasticity**

Compare two formally specified learners on the same task class and resource budget. Prove a separation only if one learner achieves a guarantee that the other cannot achieve under those assumptions.

### Important limitation

A theorem about an online predictor does not automatically transfer to a reinforcement-learning policy. The latter requires additional assumptions about environment dynamics, exploration, reward, and the relationship between policy changes and observed data.

---

# Part V — Dynamical systems and physical substrates

## 15. F12: Stability and convergence of coupled dynamics

**Priority:** P1\
**Difficulty:** Moderate to high\
**Expected result:** Analytical or machine-checked theorems for selected state-dynamics implementations.

The repository includes energy-minimization and predictive-settling dynamics, along with stability analysis. The formal objective is to turn specific claims into mathematical statements with explicit conditions.

### Theorems

**F12.1 — Lyapunov decrease**

For a specified transition or differential equation, prove that a candidate Lyapunov function decreases under the documented assumptions.

**F12.2 — Equilibrium convergence**

Derive convergence to an equilibrium from sufficient conditions such as boundedness, continuity, and appropriate decrease properties.

**F12.3 — Discrete-time stability**

Prove stability conditions for a specified discrete transition map.

**F12.4 — Jacobian bounds**

Prove that a stated Jacobian norm or spectral-radius condition implies the claimed local property.

**F12.5 — Coupling effects**

Establish when adding a plastic-state subsystem preserves stability and when coupling can invalidate it.

**F12.6 — Noise robustness**

For a bounded disturbance model, derive a bound on trajectory deviation or an invariant neighborhood.

### Required discipline

A decreasing energy function does not by itself guarantee convergence to a unique equilibrium. Distinguish local stability, asymptotic stability, global convergence, uniqueness, and finite-time termination.

## 16. F13: Precision, noise, and substrate refinement

**Priority:** P2\
**Difficulty:** Moderate to high\
**Expected result:** Correctness and error bounds connecting abstract computation to constrained implementations.

### Substrates

Start with digital finite-precision computation. Extend later to noisy, sparse, ternary, memristive, neuromorphic, or photonic models.

Treat quantum substrates as a distinct formalization problem rather than assuming that a generic stochastic or complex-valued model captures quantum computation.

### Candidate theorems

**F13.1 — Quantization error**

Bound the discrepancy between an ideal transition and its quantized implementation under stated regularity assumptions.

**F13.2 — Error accumulation**

For a specified computation, bound or characterize how local numerical errors propagate over repeated transitions.

**F13.3 — Robustness margin**

Prove that bounded perturbations cannot change a specified output or discrete decision when the system has a sufficient margin.

**F13.4 — Noisy-state probability bound**

Under a declared stochastic model, derive a probability bound on deviation from the ideal behavior.

**F13.5 — Resource-aware refinement**

Relate an abstract machine's transition count and memory use to the cost model of a concrete implementation.

### Limitation

These results do not follow from a universality proof. A universal ideal machine may be impractical or impossible to reproduce exactly under finite precision and physical noise.

---

# Part VI — Compositionality, equivalence, and architecture discovery

## 17. F14: Formal compositionality of the six axes

**Priority:** P1\
**Difficulty:** Moderate\
**Expected result:** Theorems describing how local component properties transfer to whole systems.

### Questions

- When does substituting one component preserve system correctness?
- Which component properties compose?
- Which assumptions must be shared between axes?
- Does the six-axis representation create a useful factorization of proof obligations?

### Candidate theorems

**F14.1 — Component refinement**

If a component implementation refines its abstract interface, prove that the composed system refines the composed abstract system under compatible assumptions.

**F14.2 — Substitution preservation**

Prove that replacing a component with a behaviorally equivalent component preserves system-level observations.

**F14.3 — Invariant composition**

Show how local invariants combine into a global invariant of the coupled system.

**F14.4 — Commutation conditions**

For selected pairs of transitions, characterize when their order can be exchanged without changing observable results.

**F14.5 — Independence conditions**

Identify when changing one axis leaves a declared property invariant and when coupling between axes prevents such a conclusion.

### Research value

These theorems could make the ontology useful as a formal engineering framework even if the ontology itself does not imply new computational capabilities.

## 18. F15: Distinguish architectural novelty from new computational power

**Priority:** P1\
**Difficulty:** Moderate\
**Expected result:** A formal classification of what plasticity contributes.

### Required comparisons

Compare RuleStatePlasticity with:

- An explicit external-memory machine.
- A conventional recurrent state machine.
- A finite-state controller.
- A fixed transition system with an instruction or rule selector.
- A machine with mutable program memory.

The comparison must use explicit state and resource models.

### Candidate theorems

**F15.1 — Encoding equivalence**

Show that one architecture can represent another through a semantics-preserving encoding.

**F15.2 — Resource overhead**

Bound the additional state, transitions, or memory required by the encoding.

**F15.3 — Expressiveness separation**

Where possible, prove that one restricted architecture cannot implement a behavior that another can implement under the same resource limits.

**F15.4 — Redundancy characterization**

Determine whether a specific plasticity primitive is redundant with another primitive for a particular formal task class.

**F15.5 — Architectural advantage conditions**

Characterize which constraints—such as local access, fixed persistent parameters, or restricted communication—make a particular plasticity mechanism useful.

### Interpretation

The strongest possible outcome is not necessarily a theorem that plasticity makes universal computation possible. It may instead be a theorem that a particular plasticity mechanism provides a more natural or resource-efficient implementation under a specific set of constraints.

---

# Part VII — Theorems about resource efficiency

## 19. F16: Complexity of simulation and execution

**Priority:** P2\
**Difficulty:** Moderate to high\
**Expected result:** Complexity bounds for the formal machines established in F3–F5.

### Questions

- What is the time overhead of simulating a source machine?
- How much plastic state and external memory are required?
- Does rule selection require enumerating all candidate rules?
- How does the encoded program size grow?
- Can the simulation operate online, or must it precompute a complete transition schedule?

### Candidate theorems

**F16.1 — Step simulation bound**

Prove an upper bound on target transitions required per simulated source transition.

**F16.2 — Space bound**

Prove a relationship between source-machine space and target-machine state or memory.

**F16.3 — Encoding overhead**

Bound the size of the representation of a source program or machine configuration.

**F16.4 — Restricted-access overhead**

Characterize the cost of implementing indirect addressing or conditional selection using the operations actually available.

**F16.5 — Lower bounds**

Where feasible, establish lower bounds under an explicitly defined machine model.

### Significance

This is where a Z3-inspired architecture could prove interesting even if its computability power is conventional: it might support a distinctive organization of control, state, or resource use. Such an advantage must be proved for a defined cost model, not inferred from universality.

---

# Part VIII — Meta-theory of the research framework

## 20. F17: Verify the ontology and experiment specifications

**Priority:** P2\
**Difficulty:** Moderate\
**Expected result:** A formal contract for the claims made by the research infrastructure.

### Candidate results

**F17.1 — Configuration validity**

Every accepted system configuration satisfies the formal compatibility constraints.

**F17.2 — Experiment-variable isolation**

For a specified one-axis comparison, prove that the experiment specifications differ only in the designated variable.

**F17.3 — Frozen-parameter audit soundness**

Prove, at the level of the chosen implementation model, that an accepted audit implies the declared invariance property. A snapshot check alone requires careful treatment of aliasing, mutable storage, and observation boundaries.

**F17.4 — Claim-status integrity**

Prove that claims marked machine-checked refer to successfully checked theorem artifacts rather than empirical tests.

**F17.5 — Traceability**

Every promoted mathematical claim is linked to a theorem statement, assumptions, proof artifact, and version of the model it concerns.

### Scope

These results do not establish that a learning system performs well. They establish that the research process accurately represents what has been demonstrated.

---

# Part IX — Unified Rocq implementation plan

## 21. Proposed project structure

Use the existing Rocq layout where practical. The following is a target logical structure, not a requirement to create duplicate modules if equivalents already exist.

```
rocq/
  Core/
    State.v
    Transition.v
    Observation.v
    Trace.v
    Invariant.v

  Ontology/
    Axis.v
    System.v
    Composition.v
    NullPlasticity.v
    Refinement.v

  Plasticity/
    RuleState.v
    Routing.v
    FastWeights.v
    TemporalPsi.v
    Lifecycle.v
    Expressiveness.v

  Machines/
    TuringMachine.v
    FiniteStateMachine.v
    ArithmeticMachine.v
    Z3AbstractModel.v

  Simulation/
    Encoding.v
    ForwardSimulation.v
    TraceCorrectness.v
    HaltingPreservation.v

  Universality/
    Z3Simulation.v
    RuleStateSimulation.v
    UniversalityTransfer.v
    BoundedState.v

  Dynamics/
    Lyapunov.v
    Contraction.v
    Perturbation.v
    NoiseBounds.v

  Learning/
    Ridge.v
    TraceDecay.v
    UpdateInvariants.v
    OnlineBounds.v

  Complexity/
    TimeBound.v
    SpaceBound.v
    EncodingCost.v

  Verification/
    Assumptions.v
    ClaimLedger.v
```

## 22. Formalization conventions

1. Every major definition must have a concise prose specification.
2. State whether transitions are deterministic, nondeterministic, or probabilistic.
3. Separate total transition functions from relations that may fail or diverge.
4. Make all memory and precision assumptions explicit.
5. Use natural numbers, finite types, lists, or other suitable constructive representations where possible.
6. Isolate classical assumptions and nonconstructive existence results.
7. Avoid encoding the desired theorem into an overly restrictive definition.
8. Do not use axioms that directly assert the result under investigation.
9. Prove small encoding and transition lemmas before attempting universality.
10. Keep the formal model and the executable Python implementation connected through explicit conformance or refinement claims.

## 23. Machine-checked proof requirements

A proof counts as machine-checked only if:

- Its theorem statement captures the intended claim.
- The theorem compiles in the declared Rocq environment.
- All dependencies and assumptions are recorded.
- No admitted proof is hidden behind an imported lemma.
- Any use of axioms is documented and justified.
- The theorem's scope is not stronger in prose than it is in formal semantics.

A theorem about a simplified model is valuable, but must be labeled as such.

## 24. Suggested foundational definitions

Use an abstract transition system as the shared starting point.

```
Machine:
  State
  Input
  Output
  Parameters
  PlasticState
  initialize
  transition
  observe
```

Define a trace as a sequence of states and inputs satisfying the transition relation.

Define an invariant (I) and prove preservation:

[\
I(z_0)\land\
\left(\forall t,\ I(z_t)\Rightarrow I(z\_{t+1})\right)\
\Rightarrow\
\forall t,\ I(z_t).\
]

Use this pattern for frozen parameters, legal rule states, lifecycle isolation, and other invariants.

For simulation, define an encoding (E) and prove that source transitions are represented by target transitions. Keep correctness of a single step separate from correctness of entire traces and preservation of termination.

These reusable structures should be developed before specializing the model to RuleStatePlasticity.

---

# Part X — Prioritization and execution

## 25. Research sequence

### Phase A — Establish the actual proof baseline

Complete F0–F2.

**Gate A:** The state model, persistent parameters, mutable state, transition rules, and existing proof assumptions are documented and machine-checked where feasible.

### Phase B — Prove the central computational claim

Complete F3–F6.

**Gate B:** Obtain either:

- A universality theorem under explicit assumptions;
- A conditional theorem whose missing assumptions are clear; or
- A rigorous counterexample or impossibility result for the intended model.

Do not proceed on the assumption that universality must hold.

### Phase C — Determine what plasticity contributes

Complete F7–F9 and F14–F15.

**Gate C:** Produce a formal comparison of the relevant mechanisms and identify proved equivalences, separations, and unresolved cases.

### Phase D — Develop learning and dynamical guarantees

Complete F10–F13.

**Gate D:** At least one concrete plasticity primitive has a machine-checked correctness, stability, or adaptation theorem under clearly stated assumptions.

### Phase E — Analyze resource costs and research infrastructure

Complete F16–F17.

**Gate E:** The project has a defensible account of resource overhead, theorem provenance, and the relationship between abstract results and implementations.

## 26. Prioritization matrix

| Project                              | Importance | Initial feasibility     | Dependency |
| ------------------------------------ | ---------- | ----------------------- | ---------- |
| F0: Proof inventory                  | Essential  | High                    | None       |
| F1: Ontology semantics               | High       | High                    | F0         |
| F2: Frozen-(\theta), evolving-(\psi) | Essential  | High                    | F0–F1      |
| F3: Z3 formalization                 | High       | Moderate                | F0         |
| F4: RuleStatePlasticity semantics    | Essential  | Moderate                | F1–F2      |
| F5: Universality theorem             | Very high  | Uncertain               | F3–F4      |
| F6: Bounded-state limitations        | High       | High                    | F1–F2      |
| F7: Expressiveness hierarchy         | Very high  | Moderate                | F4–F6      |
| F8: Lifecycle guarantees             | High       | High                    | F2         |
| F9: Stability–plasticity theory      | High       | Moderate                | F2, F8     |
| F10: Update-rule correctness         | High       | High for selected rules | F1–F2      |
| F11: Online learning guarantees      | High       | Moderate to low         | F10        |
| F12: Dynamical stability             | High       | Moderate                | F1         |
| F13: Substrate refinement            | High       | Moderate                | F1, F12    |
| F14: Compositionality                | High       | Moderate                | F1         |
| F15: Novelty and equivalence         | Very high  | Moderate                | F5–F7      |
| F16: Complexity                      | High       | Moderate                | F3–F5      |
| F17: Verification infrastructure     | High       | Moderate                | F0–F2      |

These are qualitative planning estimates, not measured project durations.

## 27. Feasibility and resource requirements

A typical desktop computer should be sufficient for the foundational formalization, finite-state models, simulation proofs, and many of the stability theorems.

The main cost is likely to be mathematical specification and proof engineering rather than raw computation.

Rocq is sufficient for this research program. Lean is not required. Changing proof assistants would be justified only by a concrete library or interoperability need that cannot be handled reasonably in the current development.

Language models can help formulate candidate lemmas, generate proof scripts, explore counterexamples, and reduce repetitive proof engineering. They should not be treated as evidence that a conjecture is true. Every resulting proof must be checked, and every model assumption must be reviewed independently.

---

# Part XI — Definition of success

## 28. Minimum successful outcome

The initial project is successful if it delivers:

1. A clean inventory of the existing Rocq proofs and assumptions.
2. A formal frozen-parameter machine with an evolving plastic state.
3. A formal specification of RuleStatePlasticity matching the intended implementation.
4. A machine-checked simulation theorem for at least one nontrivial class of computations.
5. A precise universality theorem, a conditional universality theorem, or a rigorous impossibility result for the specified architecture.
6. At least one theorem characterizing what changes when plasticity or external memory is removed.
7. A reproducible build and documented theorem dependencies.

## 29. Strong research outcome

A stronger result would establish a meaningful theorem distinguishing a Computronium plasticity mechanism from a conventional architecture under a specified resource constraint.

Examples include:

- A simulation result with a useful complexity bound.
- A formal separation between two restricted architecture families.
- A guarantee for adaptation or retention unavailable to a specified baseline.
- A compositionality theorem that substantially reduces the proof burden for new architectures.
- A stability theorem that enables a previously unverified design choice.

A theorem proving that two architectures are equivalent can also be significant if it clarifies their tradeoffs or rules out a misleading novelty claim.

## 30. What must not be claimed without additional evidence

The following conclusions do not follow from the proposed foundational proofs alone:

- That Computronium is a new universal computing paradigm.
- That plasticity increases the computability power of every architecture.
- That RuleStatePlasticity is computationally universal merely because the Z3-inspired source machine is universal.
- That frozen parameters imply efficient or successful learning.
- That a universal abstract model is realizable by finite-precision hardware without additional assumptions.
- That formal expressiveness implies superior benchmark performance.
- That a proof of convergence establishes useful adaptation.
- That a successful simulation of a Turing machine establishes a practical advantage over conventional memory or recurrent computation.

Each claim requires its own theorem or empirical evidence.

## 31. Final research principle

The program should be organized around the question:

**What can we prove about the computations, learning behaviors, and resource tradeoffs enabled by making the computational rule itself a controllable state variable?**

The Z3 connection provides a concrete route into the computational theory. The six-axis ontology provides the broader architectural setting. The formal treatment of plasticity, compositionality, stability, and resource constraints determines whether the framework yields useful principles beyond the existence of another way to represent computation.

The first major milestone is not to prove that the entire Computronium framework is powerful. It is to produce a precise model, establish exactly what that model can do, and identify which properties genuinely depend on its plasticity mechanism.

## 4. The three proofs I would start with

Although the specification contains 18 research packages, I would not pursue them in parallel. Three projects offer the clearest route from the existing repository to substantive mathematical results.

### 1. Prove the frozen-\\(\theta\\) contract in Rocq

Start with a minimal formal machine in which persistent parameters are immutable and plastic state evolves. Prove the invariant for every finite execution trace. This establishes the exact premise of the proposed architecture without making any assumptions about universality.

Packages F1–F2 · Best initial proof target

### 2. Prove a simulation theorem for RuleStatePlasticity

Define what a rule is, how \\(\psi\\) represents it, and how state transitions execute it. Then prove that a step of a small abstract machine is correctly simulated. This tests the actual mathematical bridge between mutable rule state and computation.

Packages F3–F4 · Central conceptual target

### 3. Prove a capability boundary

Establish what is impossible when \\(\psi\\) is bounded, then compare it with the model that has writable external memory. This gives a rigorous account of which resources are actually responsible for the capability.

Packages F6–F7 · Best route to distinguishing architecture from implementation

The third project is particularly important. If a formal model permits arbitrary computation only because it quietly assumes unbounded writable memory, that is a legitimate result—but the contribution lies in understanding the memory model, not necessarily in plasticity itself.

## 5. The most important unresolved question

The decisive question is not simply whether RuleStatePlasticity is Turing complete. A sufficiently general recurrent machine or a conventional computer with writable memory may already have that property.

The more revealing question is:

Under identical memory, precision, and resource constraints, does making the computational rule an explicit evolving state enable a useful property that the corresponding fixed-rule architecture cannot provide as naturally or efficiently?

There are several possible answers:

- It may offer no new computability, but improve compositionality or lifecycle control.
- It may enable a more efficient representation of certain computations.
- It may support useful online adaptation without modifying persistent parameters.
- It may turn out to be equivalent to a familiar architecture once the state is encoded properly.
- Its apparent power may depend on hidden assumptions about memory, precision, or rule selection.

Each outcome tells us something substantive.

The first practical step is to inspect the existing Rocq files and formalize the actual `RuleStatePlasticity` transition semantics—not to assume the desired theorem, and not to rewrite the proof development in another assistant. Once those definitions are pinned down, we can determine whether the universality proof is a short simulation argument, a substantial formalization project, or a claim that needs to be narrowed.

