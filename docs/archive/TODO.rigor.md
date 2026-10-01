Yes. Beyond the remediation plan, the review suggests several high-leverage extensions. I would treat these as “force multipliers”: they do not add more model families; they make every future experiment more trustworthy, comparable, and easier to debug.

Below are additional suggestions, organized by theme.

---

## 1. Make claims a first-class engineering object

The project would benefit from a **claim ledger**: a structured registry of every scientific or performance claim made in documentation, figures, or experiment reports.

Each claim could have:

```yaml
claim_id: CLM-0014
statement: >
  Routing plasticity reduces effective matmul operations on the mixture-of-experts
  task without reducing accuracy under a matched parameter budget.
status: hypothesized | implemented | measured | supported | refuted | superseded
evidence_level: 4  # sampled numerical test / empirical result
dependencies:
  - run: RUN-2026-09-08-routing-moe-001
  - metric: active_units
  - metric: task_loss
falsification_condition: >
  If accuracy drops by more than 1 percentage point under matched writable-bit budget,
  the claim should be rejected.
last_reviewed: 2026-09-10
```

### Why this helps

- It separates **claims** from **runs**.
- It prevents old results from silently supporting new, stronger language.
- It makes the README easier to audit: every sentence that implies a result can point to a claim ID.
- It creates a natural place to record negative results and superseded interpretations.

A simple version could be a YAML or SQLite file in `claims/`. The important part is the discipline, not the storage format.

---

## 2. Create a measurement protocol registry

Many of the issues in the review came from metrics being used more broadly than their definitions justified. A **measurement protocol registry** would prevent that.

For each metric, define:

```text
Metric: spectral_radius
Definition: maximum absolute eigenvalue of a Jacobian at a fixed point.
Estimator: power iteration on J, with fixed base state.
Assumptions:
  - differentiable map
  - fixed base state
  - sufficient iterations
  - no trajectory drift during estimation
Does not establish:
  - contraction
  - global stability
  - transient amplification
  - chaos
Calibration tests:
  - diagonal matrix with known eigenvalues
  - nonnormal matrix with rho=0.5 and sigma_max≈10
Failure modes:
  - base state changes between iterations
  - JVP-only used when singular values are intended
```

Do the same for:

- `lyapunov_local`
- `settling_time`
- `basin_stability`
- `free_energy`
- `gate_entropy`
- `directional_amplification`
- `gradient_alignment`
- `adaptation_time`
- `effective_flops`
- `writable_bits`
- `simulated_energy`

This turns metrics into documented instruments rather than ad hoc numbers.

---

## 3. Add a calibration suite for dynamical metrics

Before using stability or memory metrics on learned systems, test them on synthetic systems with known behavior.

Examples:

| Synthetic system | Known property | Metric should show |
|---|---|---|
| Diagonal stable linear map | $\rho < 1$, $\sigma_{\max} < 1$ | both stable |
| Nonnormal stable matrix | $\rho < 1$, $\sigma_{\max} > 1$ | stable but transiently amplifying |
| Orthogonal rotation | $\rho = 1$, $\sigma_{\max} = 1$ | neutral, not contracting |
| Expanding linear map | $\rho > 1$ | unstable |
| Contractive map with noise | memory decays predictably | delayed recall decreases |
| Gated memory with contractive activity | activity stable, memory retained | high delayed recall despite contraction |
| Chaotic map | sensitive dependence | positive finite-time divergence |

This suite would catch estimator bugs before they contaminate large campaigns.

A good default nonnormal regression case remains:

\[
J =
\begin{pmatrix}
0.5 & 10 \\
0 & 0.5
\end{pmatrix}
\]

It has \(\rho(J)=0.5\) but large transient amplification.

---

## 4. Build a small canonical task battery for mechanism diagnostics

Large benchmarks like MNIST or CIFAR are useful for parity, but they often hide mechanistic differences. For the P-axis, stability, and memory questions, I would add a small set of diagnostic tasks with known computational requirements.

Examples:

| Task | Mechanism probed |
|---|---|
| Copy task | short-term memory, write/read fidelity |
| Delayed match-to-sample | retention under distractors |
| Cumulative sum | integration, precision, drift |
| Last-symbol detection | selective retention, reset |
| Parity | sequential composition, nonlinear state |
| Task switching | rule selection, adaptation |
| Sequence reversal | composition depth, control |
| Noisy delayed recall | memory under precision constraints |
| Sparse route selection | gating and communication cost |
| Operator composition | frozen-\(\theta\) program execution |

Each task should have controllable parameters:

- sequence length;
- input dimension;
- noise level;
- precision;
- delay;
- distractor probability;
- task-switch interval;
- memory capacity required.

This gives the AutoScientist a set of cheap, interpretable environments before scaling to more expensive domains.

---

## 5. Introduce budget-normalized comparisons

Many apparent advantages disappear once systems are matched on a fair budget. The framework could make budget matching a standard experimental condition.

Possible budgets:

| Budget type | What it controls |
|---|---|
| Writable bits | total mutable state capacity |
| FLOPs per step | arithmetic cost |
| Communication volume | bytes crossing modules or devices |
| Sequential depth | number of dependent steps |
| Training samples | adaptation data budget |
| Wall-clock latency | real-time cost |
- energy proxy | modeled energy cost |
| Precision | numerical bits available |
| Optimizer state | extra hidden capacity in update rules |

For example, comparing a fast-weight plasticity mechanism against a baseline should ideally match:

\[
\text{persistent parameters} + \text{fast weights} + \text{optimizer state}
\]

against an equivalent total writable capacity in the baseline.

This would prevent accidentally comparing “mechanism A” against “mechanism B plus hidden extra memory.”

---

## 6. Define an intervention API for plasticity and state

The P-axis would become much clearer if the framework exposed explicit interventions.

Possible operations:

```python
system.freeze_theta()
system.freeze_psi()
system.reset_psi()
system.shuffle_psi()
system.clamp_psi(value)
system.disable_plasticity()
system.replace_plasticity_with_recurrent_state(capacity_bits=...)
system.inject_noise(target="psi", scale=...)
system.measure_delayed_recall(delay_steps=...)
```

This would make many of the recommended controls easy to run:

- reset \(\psi\) at evaluation;
- freeze \(\psi\) after adaptation;
- shuffle \(\psi\) across tasks;
- replace plasticity with equal-capacity recurrent state;
- test whether adaptation is actually stored in \(\psi\).

The API would also help distinguish architectural value from scientific superiority. Even if a baseline matches performance, the ability to cleanly intervene on \(\psi\) may still justify the axis.

---

## 7. Make locality a measurable resource

The project talks about locality, but locality should not remain a qualitative virtue. It can be measured.

Possible locality metrics:

| Metric | Meaning |
|---|---|
| Communication cut size | number of edges crossing a partition |
| Bytes per example crossing partition | communication cost |
| Global reductions per step | number of all-reduce-like operations |
| Feedback path length | distance from error source to updated parameter |
| Temporal dependency horizon | how far back credit/state must reach |
| Synchronization rounds | number of barriers or global phases |
| Receptive field growth | spatial or depthwise spread of influence |
| Weight-transport violation count | number of nonlocal parameter dependencies |

Then experiments can plot:

\[
\text{accuracy} \quad \text{vs.} \quad \text{communication budget}
\]

or:

\[
\text{adaptation speed} \quad \text{vs.} \quad \text{credit horizon}
\]

This would make the physical-computation narrative much more concrete.

---

## 8. Separate logical sparsity from execution cost

The framework should avoid treating sparsity as automatically beneficial. Logical sparsity can reduce arithmetic but still perform poorly on real hardware because of indexing overhead, synchronization, or poor memory access patterns.

A useful distinction:

| Level | Question |
|---|---|
| Logical sparsity | How many operations are mathematically nonzero? |
| Scheduled sparsity | How many operations does the executor actually perform? |
| Memory sparsity | How much memory is touched? |
| Communication sparsity | How many messages or transfers occur? |
| Energy sparsity | How much energy is modeled or measured? |
| Latency sparsity | Does wall-clock time improve? |

For each sparse or routed system, report at least two levels: logical and executed. If a routing mechanism reduces FLOPs but not latency, that is a valuable negative result.

---

## 9. Add a “capacity-matched baseline” requirement

For any plasticity or adaptation claim, include a set of baselines that test whether the effect comes from the mechanism or merely from extra state.

Suggested baselines:

1. **Null plasticity**  
   No \(\psi\), same \(\theta\).

2. **Recurrent state baseline**  
   Add ordinary hidden state with the same capacity as \(\psi\).

3. **Fast-weight baseline**  
   Add episode-local weights without the full plasticity abstraction.

4. **Adapter baseline**  
   Add low-rank task-specific parameters.

5. **Oracle selector**  
   Provide the correct operator or rule directly.

6. **Random selector**  
   Choose rules randomly to establish a lower bound.

7. **Nonplastic learned selector**  
   Learn to route without treating the rule as plastic state.

8. **Label-driven routing**  
   If task identity is available, test whether adaptation collapses into simple task lookup.

If a P-axis mechanism beats only the null baseline but loses to an equal-capacity recurrent state baseline, that is still informative. It means the benefit may be architectural convenience rather than computational power.

---

## 10. Turn negative results into structured artifacts

The project already has a healthy attitude toward negative results. That can be formalized.

A negative result record could include:

```yaml
negative_result_id: NR-0021
title: >
  Short-horizon local credit fails to stabilize long-horizon operator composition
mechanism: >
  per-step operator error accumulates until rollout becomes unreliable
conditions:
  precision: float32
  training_horizon: 8
  rollout_horizon: 64
  local_credit: true
what_was_tried:
  - stronger contraction
  - normalized operators
  - gated memory
  - longer local horizon
partial_successes:
  - composition works for short sequences under contractive operators
  - error is predictable from one-step operator precision
future_directions:
  - precision-horizon phase diagram
  - exact-transition baselines
  - protected memory channel
```

This makes failures reusable. Future researchers can query: “What already failed when increasing rollout horizon?”

---

## 11. Add a glossary and anti-glossary

Because the project uses terms from ML, dynamical systems, physics, and hardware, ambiguity is a real risk.

A glossary could define:

- energy;
- free energy;
- contraction;
- stability;
- plasticity;
- credit assignment;
- substrate;
- writable state;
- adaptation;
- locality;
- simulated energy;
- measured energy;
- formal proof;
- sampled test;
- empirical result.

An **anti-glossary** may be even more useful:

| Term | What it does not mean here |
|---|---|
| Energy | Not necessarily joules; often a Lyapunov function |
| Quantum | Not automatically quantum advantage; may mean complex-valued simulation |
| Verified | Not necessarily mathematically proven |
| Locality | Not necessarily physical locality |
| Plasticity | Not necessarily biological plasticity |
| Frozen weights | Not necessarily absence of all mutable state |
| Sparsity | Not necessarily faster execution |
| Equivalence | Not necessarily exact mathematical identity |
| Stability | Not necessarily contraction |
| Adaptation | Not necessarily learning a new algorithm |

This would significantly reduce overreading by users and reviewers.

---

## 12. Add “assumption manifests” to models and theorems

Every model or stability claim could carry an assumption manifest.

Example:

```yaml
model: eqprop_mlp
assumptions:
  - symmetric recurrent connectivity
  - scalar energy function exists
  - bounded activations
  - small nudge parameter beta
  - discretized settling approximates continuous dynamics
  - no substrate drift during settling
violated_if:
  - connectivity is directed without symmetric counterpart
  - beta is large enough to change the energy landscape
  - discretization causes energy increase
```

For theorems or analytical claims:

```yaml
theorem: eqprop_fixed_point_descent
assumptions:
  - differentiable energy
  - compact state space
  - symmetric interactions
  - appropriate step size
  - no numerical overflow
status: analytical_result
proof_artifact: docs/theory/eqprop_descent.md
```

This makes the boundary between theory and implementation explicit.

---

## 13. Use “algorithm renaming” as a hygiene rule

If composition changes an algorithm enough that it no longer matches the literature, rename it.

For example:

| Literature name | If modified substantially, use |
|---|---|
| Equilibrium Propagation | `EqProp-variant`, `finite-nudge EP`, `directed EP` |
| Feedback Alignment | `random-projection credit`, `FA-like update` |
| PEPITA | `PEPITA-inspired input modulation` if changed |
| Forward-Forward | `local-goodness classifier` if not the original objective |
| Muon | `orthogonalized update` if rectangular/rank assumptions differ |
| STDP | `temporal trace credit` if not the full biological rule |

This avoids the common framework failure mode where a name survives after the algorithm has changed.

A good rule:

> If the identity card cannot cite the original equations without listing significant deviations, the public name should include “variant” or use a framework-native name.

---

## 14. Add a compatibility report CLI

The six-axis space is not a free product. A useful tool would be:

```bash
comp explain-coordinate \
  --substrate Memristive \
  --geometry TileMesh \
  --dynamics EnergyMinimization \
  --plasticity RoutingPlasticity \
  --credit ThermodynamicContrast \
  --update SpectralConstrainedUpdate
```

Output:

```text
Coordinate status: valid with constraints

Compatibility:
  Memristive substrate supports bounded conductance and write-noise model.
  ThermodynamicContrast requires a scalar energy function.
  EnergyMinimization provides such a function under symmetric routing.
  RoutingPlasticity may break symmetry if gates are directed.

Required checks:
  - verify effective recurrent matrix remains symmetric or energy-compatible
  - verify conductance bounds after update
  - verify spectral constraint does not conflict with memristive write model

Known limitations:
  - energy estimate is simulated, not hardware-measured
```

This would be far more useful than a generic constructor error.

---

## 15. Make reproducibility artifacts mandatory

Every reported experiment should produce a self-contained reproduction bundle.

Suggested structure:

```text
artifacts/
  2026-09-10_eqprop_mnist_slice/
    config.yaml
    seeds.yaml
    env.lock
    dataset_manifest.json
    run_manifest.json
    metrics.json
    claim_record.yaml
    figures/
    logs/
    reproduce.sh
```

The `run_manifest.json` could include:

- git commit;
- Python version;
- package versions;
- hardware;
- deterministic settings;
- dataset hashes;
- RNG seeds;
- command line;
- metric definitions;
- estimator versions.

Then the README can cite artifacts rather than vague internal TODOs.

---

## 16. Add a “run report” generator

Every experiment run could automatically generate a human-readable report:

```text
Run ID: RUN-2026-09-10-eqprop-slice-001
Coordinate: Digital × Recurrent × EnergyMinimization × Null × ThermodynamicContrast × Euclidean
Task: mnist
Seed: 0
Duration: 42s
Final train accuracy: 0.912
Final val accuracy: 0.901
Energy descent: monotonic within tolerance 1e-4
Gradient sign consistency: 0.97
Frozen theta: not applicable
Resource usage:
  peak memory: 312 MB
  estimated flops: 1.8e9
  simulated energy: 4.2e-3 arbitrary units
Warnings:
  none
```

This would make campaigns easier to audit and less dependent on manual interpretation.

---

## 17. Add deterministic-mode contracts

Determinism claims should be explicit about scope.

For example:

```text
Determinism contract:
  - device: cpu
  - torch.use_deterministic_algorithms(True)
  - fixed seed
  - fixed dataset order
  - no asynchronous I/O
  - no nondeterministic Triton kernels
  - same package versions
  - same hardware class

Not guaranteed:
  - bitwise equality across GPU architectures
  - equality across different CUDA versions
  - equality when using asynchronous neuromorphic simulation
```

This prevents “bitwise reproducible” from being interpreted too broadly.

---

## 18. Add a physical-cost model hierarchy

Since the project is inspired by physical computation, it should clearly separate cost levels.

| Level | Description | Example |
|---|---|---|
| L0 | Logical operation count | FLOPs, matmuls, spikes |
| L1 | Simulated device cost | memristive write energy model |
| L2 | Calibrated proxy cost | model tuned against published hardware numbers |
| L3 | Hardware-measured cost | actual device or FPGA measurement |
| L4 | End-to-end system cost | including control, conversion, communication |

The README should always state which level is being reported.

For example:

> Energy values in this experiment are L1 simulated device costs, not measured joules.

This is a small wording change but prevents a large class of overclaiming.

---

## 19. Add a hardware-in-the-loop interface, even if empty

Physical substrate validation is future work, but the interface can be designed now.

A simple protocol:

```python
class HardwareBackend(Protocol):
    def execute_forward(self, state: State) -> State: ...
    def execute_update(self, update: Update) -> None: ...
    def measure_energy(self) -> EnergyReading: ...
    def measure_latency(self) -> LatencyReading: ...
    def report_nonidealities(self) -> NonidealityReport: ...
```

Even if all current backends are simulated, this prepares the project for later physical validation without redesign.

---

## 20. Add a “minimal publishable experiment” template

For contributors, a good template would be:

```text
1. Question
2. Coordinate(s)
3. Baselines
4. Budgets matched
5. Tasks
6. Metrics
7. Seeds and uncertainty
8. Falsification condition
9. Result
10. Claim status
11. Reproduction command
```

This lowers the barrier to producing rigorous experiments and discourages contributors from submitting unsupported claims.

---

## 21. Add a public “what this project does not claim” section

This can be surprisingly effective for credibility.

Example:

```markdown
## What Computronium does not claim

- It does not claim that physical substrates are automatically more efficient.
- It does not claim that local learning rules outperform backpropagation in general.
- It does not claim that the six-axis decomposition is a complete theory of learning systems.
- It does not claim that current substrate models are validated on physical hardware.
- It does not claim that passing property tests constitute mathematical proofs.
- It does not claim that frozen-theta adaptation demonstrates new computational power without matched baselines.
```

This preempts misunderstandings and signals scientific seriousness.

---

## 22. Add a “research questions” board

Instead of only tracking features or bugs, track open scientific questions.

Examples:

| Question | Status | Required evidence |
|---|---|---|
| Does routing reduce executed operations under matched accuracy? | open | budget-matched MoE experiment |
| Does contractive activity plus gated memory outperform globally expansive dynamics on delayed recall? | open | stability-memory campaign |
| Does ψ provide benefits beyond equal-capacity recurrent state? | open | capacity-matched baselines |
| At what precision does long-horizon composition fail? | open | precision-horizon phase diagram |
| Does thermodynamic contrast approximate backprop under instantaneous dynamics only in shallow networks? | open | analytic derivation + scaling test |

This makes the project feel like a laboratory rather than a product roadmap.

---

## 23. Add a “mechanism dashboard”

For interactive use, a dashboard could show not just loss curves but mechanism diagnostics.

Possible panels:

- energy trajectory;
- spectral radius vs. singular value estimate;
- gate entropy;
- active units;
- memory probe accuracy over delay;
- gradient alignment with sign consistency;
- resource usage over time;
- ψ mutation count;
- θ invariance audit status;
- communication volume;
- settling time distribution.

This would make the framework’s unique value visible immediately.

---

## 24. Add a “baseline zoo” as a first-class module

Rather than scattering baselines across experiments, create a dedicated module:

```text
computronium/baselines/
  null_plasticity.py
  recurrent_capacity.py
  fast_weight_capacity.py
  adapter_capacity.py
  oracle_selector.py
  random_selector.py
  label_router.py
  global_backprop.py
  full_trajectory_credit.py
```

Each baseline should expose:

- capacity budget;
- resource budget;
- intervention hooks;
- known limitations;
- identity card.

This makes fair comparison much easier.

---

## 25. Add a “metric bias” review

Some metrics may systematically favor certain architectures.

For example:

- FLOPs may favor dense GPU execution over sparse event-driven execution.
- Wall-clock time may favor optimized libraries over conceptually simpler algorithms.
- Energy proxies may favor digital simulation because analog overhead is not modeled.
- Accuracy may hide adaptation cost.
- Settling time may depend on tolerance choices.

A useful practice is to document known biases for each metric and report at least one alternative metric that has different biases.

---

## 26. Add “pre-registered” experiments for high-stakes claims

For claims that are central to the scientific program, pre-register the protocol before running large campaigns.

A lightweight pre-registration:

```yaml
experiment: psi_adaptation_beyond_capacity
hypothesis: >
  RoutingPlasticity improves task-switching latency compared to capacity-matched
  recurrent state under fixed writable-bit budget.
primary_metric: adaptation_time_to_threshold
secondary_metrics:
  - task_loss
  - gate_entropy
  - active_units
budgets:
  writable_bits: matched
  flops_per_step: matched
  samples: matched
analysis_plan:
  - report mean and interval over seeds
  - report per-task traces
  - report failure cases
falsification:
  - if capacity-matched recurrent state is within equivalence margin,
    do not claim mechanism superiority
```

This prevents post hoc interpretation from turning ambiguous results into strong claims.

---

## 27. Add a “proof-to-test” traceability matrix

For mathematical claims, connect theory to tests.

| Theory claim | Test type | Evidence level | Status |
|---|---|---|---|
| EqProp energy non-increasing under assumptions | sampled numerical test | Level 4 | implemented |
| Predictive settling free-energy descent | sampled numerical test | Level 4 | implemented |
| Null plasticity zero-extension | numerical equivalence test | Level 4 | implemented |
| Muon orthogonalizes update | sampled numerical test | Level 4 | implemented |
| Passivity of neuromorphic substrate | sampled numerical test, not physical passivity | Level 4 | needs clarification |

This prevents tests from being described as proofs and proofs from being assumed where only tests exist.

---

## 28. Add a “state inventory” for every experiment

Frozen-\(\theta\) and adaptation experiments should list all mutable state.

Example:

```text
Mutable state inventory:
  theta: persistent parameters
  psi: fast plastic routing state
  sigma: substrate conductance state
  optimizer_moments: excluded / included
  normalization_running_stats: frozen
  rng_state: seeded, not considered learned state
  ntm_memory: task-visible writable state
  caches: cleared between episodes
  dataloader_order: seeded
```

This avoids accidentally claiming “only ψ changed” while optimizer moments or buffers carry information.

---

## 29. Add a “communication topology” view

Many physical and local learning claims depend on topology. The framework could expose a graph view of each coordinate.

For each system, report:

- nodes: layers, tiles, neurons, memory units;
- edges: forward, recurrent, credit, plasticity, substrate coupling;
- edge types: local, nonlocal, symmetric, random, learned;
- communication cost per step;
- partitionability;
- minimum cut size;
- global synchronization points.

This would make locality discussions concrete and visual.

---

## 30. Add a “capability vs. capacity” distinction

This is especially relevant for the P-axis.

A mechanism may improve performance because of:

1. **Capability:** it can represent or execute something the baseline cannot.
2. **Capacity:** it simply has more writable state.
3. **Inductive bias:** it guides search toward useful solutions.
4. **Optimization effect:** it changes update dynamics beneficially.
5. **Measurement artifact:** the metric accidentally rewards hidden state.

Experiments should try to distinguish these. For example:

- If a baseline with equal capacity matches the mechanism, the effect may be capacity.
- If the mechanism matches only with an oracle, the effect may be operator quality.
- If random selection performs similarly, the routing may not matter.
- If performance disappears when \(\psi\) is reset, adaptation is stored there.
- If performance disappears when \(\psi\) is frozen, ongoing plasticity matters.

---

## 31. Add a “minimal viable scientific paper” path

Once the remediation is complete, a strong first paper or technical report could be narrow:

> **A budget-matched comparison of local credit rules and update rules on synthetic sequence tasks**

or:

> **Measuring the stability-memory trade-off in contractive recurrent systems with gated memory**

or:

> **An auditable measurement pipeline for comparing learning mechanisms under resource constraints**

The paper should not try to prove “computronium.” It should demonstrate that the laboratory can produce one clean, reproducible, falsifiable result.

---

## 32. Suggestions I would avoid

Some ideas may be tempting but are probably premature:

1. **Adding more axes**  
   Do not add new ontology axes until the current six are rigorously documented and stress-tested.

2. **Adding more substrate models**  
   More simulated substrates will not help until the measurement and cost-model hierarchy is solid.

3. **Chasing SOTA benchmarks**  
   The project’s value is mechanistic comparison, not leaderboard performance.

4. **Using broad physical metaphors in user-facing claims**  
   Terms like “physical computation,” “energy,” and “thermodynamic” should be tightly scoped.

5. **Building large autonomous research agents before the measurement pipeline is trustworthy**  
   Automation amplifies measurement errors.

6. **Treating architectural elegance as scientific evidence**  
   A clean abstraction can be valuable, but it does not prove a hypothesis about learning or physics.

---

## Highest-priority additions

If I had to choose only a few additional suggestions beyond the existing plan, I would pick these:

1. **Claim ledger**  
   Every public claim gets an ID, evidence level, dependencies, and falsification condition.

2. **Measurement protocol registry**  
   Every metric gets a definition, assumptions, failure modes, and calibration tests.

3. **Canonical diagnostic task battery**  
   Small tasks with known memory, composition, and adaptation requirements.

4. **Capacity-matched baselines**  
   Especially for P-axis and frozen-\(\theta\) experiments.

5. **Budget-normalized reporting**  
   Writable bits, communication, precision, latency, and energy level should be standard.

6. **Intervention API**  
   Freeze, reset, shuffle, clamp, and replace state channels systematically.

7. **“What we do not claim” section**  
   This is cheap, high-value, and improves trust immediately.

These additions would strengthen the project without expanding its surface area too quickly. They turn the remediation into a durable research operating system.

