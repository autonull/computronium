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
| **🔬 Research Framework** | 6-D parameterized algorithm space (Substrate × Geometry × StateDynamics × Plasticity × CreditAssignment × ParameterUpdate), AutoScientist campaigns, property-verified hypercube, stability-plasticity monitoring, Pareto frontier analysis | Systematic ablations across axes; controlled benchmark campaigns for adaptation efficiency, compute efficiency, structural robustness, algorithm migration, Z3 fixed-weight adaptation |
| **🧪 Scientific Program** | Hypotheses on locality, plasticity, stability, and physical constraints as first-class dimensions; stability-plasticity trade-off as controlled departure from contraction; resource-vector Pareto analysis (compute, memory, energy, latency, plastic-state capacity) | Ongoing empirical investigation—not validated claims. Large-scale campaigns and physical-hardware validation remain future work. |

| Audience | Entry Point |
|----------|-------------|
| 🧠 **Natural Scientists & Physicists** | Energy-based local learning demo: Hebbian/contrastive rules with Lyapunov stability analysis, passivity checks, energy tracking |
| 📊 **Data Scientists & ML Researchers** | Composable learning rules, local credit assignment, depth/compute scaling, systematic comparison across algorithms |
| 🔬 **Algorithm / Hardware Researchers** | Substrate models, hardware-aware constraints, stability analysis, algorithm–substrate co-design |
| 💻 **Systems Engineers & Developers** | Correctness by construction: type-safe (PEP 695 generics), property-locked (Hypothesis), Triton-accelerated, AutoScientist automation |

The ML library provides the composable primitives; the research framework provides the campaign infrastructure for systematic exploration; the scientific program articulates the hypotheses that guide exploration priorities.

---

## 🔮 Six-Dimensional Decomposition

**Computronium models learning systems using 6 composable axes:**

```
System = Substrate × Geometry × StateDynamics × Plasticity × CreditAssignment × ParameterUpdate
```

A **System is a 6-axis coordinate; 5-D systems are the `P = NullPlasticity` subspace.** This decomposition is the framework's organizing abstraction for comparing learning systems. The space is a **compatibility-constrained subset** of the full Cartesian product — `SystemConfig.validate()` whitelists compatible combinations of primitives; the compatible region is the search space explored by the **AutoScientist**. The ontology is a design abstraction, not an established law of computation.

| Axis | Symbol | Role | Primitives |
|------|:------:|------|------------|
| **🔩 Substrate** | $S$ | Physical state space: precision, noise, sparsity constraints | `Digital`, `Memristive` (conductance, IR-drop), `Neuromorphic` (async spikes), `Photonic` (phase/amplitude), `Quantum` (unitary gates), `Noisy`, `Complex`, `Sparse`, `Ternary` |
| **🔷 Geometry** | $G$ | Topology & routing of computational units | `FeedforwardDAG` (MLP/CNN), `RecurrentAttractor` (Hopfield/EqProp), `TileMesh` (TileNet), `FabricPC` (arbitrary node-edge), `SpatialLattice3D` (neural_cube), `NTM` (external-memory tape: controller + content-addressed read/write heads), `NCA` (neural cellular automaton: emergent spatial fabric) |
| **🌀 StateDynamics** | $D$ | Forward evolution & settling (the "forward pass") | `EnergyMinimization` (EqProp), `PredictiveSettling` (Predictive Coding), `SpikeIntegration` (LIF/Izhikevich), `InstantaneousPass` (FF/Backprop), `LazyStateDynamics` (on-demand activation), `Diffusion` |
| **🧬 Plasticity (MetaDynamics)** | $P$ | Mechanism elevating the computational rule to a dynamical variable. With external memory (NTM) and emergent substrates (NCA), the program becomes data that can be written, composed, and sequenced on fixed hardware (θ): reconfigurable program (ψ), unbounded tape (NTM memory). P-axis provides *architectural* benefits (lifecycle control, intervention, explicit routing); whether it outperforms standard recurrent memory on benchmarks is an open empirical question | `NullPlasticity` (Zero-Extension), `RoutingPlasticity` (gating/rerouting), `FastWeightPlasticity` (episode-local memory), `SubstrateCoupledPlasticity` (physical plasticity), `RuleStatePlasticity` (Z3: rule selection), `ClosedFormRidgePlasticity` (supervised ψ computed, not trained), `TemporalPsiPlasticity` (trace-decayed supervised ψ — forgetting enables task migration on frozen θ) |
| **💡 CreditAssignment** | $C$ | Error routing & pseudo-gradient computation | `ThermodynamicContrast` (EqProp free/nudged), `RandomProjectionsCredit` (FA/DFA), `LocalGoodnessCredit` (Forward-Forward/PEPITA), `TemporalTraceCredit` (STDP), `TargetInversionCredit` (Target Prop), `HomeostaticCredit` (autonomous Lipschitz scaling) |
| **🔧 ParameterUpdate** | $U$ | Slow, persistent parameter consolidation Δθ | `EuclideanUpdate` (SGD/Adam), `RiemannianOrthogonalUpdate` (Muon), `SpectralConstrainedUpdate`, `NaturalGradientUpdate` (Fisher), `ElasticConsolidationUpdate` (EWC) |

### Substrate Specifications

<details>
<summary><strong>SubstrateSpec: substrates as structured specifications, not string tags</strong> ⋯</summary>

A substrate is defined by an execution model, a device model, a numeric representation, noise, constraints, and cost — captured by the frozen `SubstrateSpec` dataclass (`computronium/ontology/substrate/spec.py`) with `make_substrate(spec)` as its factory. Specs compose: "noisy, sparse, complex-valued" is one spec with three facets. `SubstrateSpec.from_config`/`to_config` round-trip all legacy `SubstrateConfig` presets losslessly (including the ternary/complex/sparse digital family, which legacy configs cannot distinguish from fields alone — new code should construct specs directly).
</details>

### Geometry Primitives

<details>
<summary><strong>NTM Geometry (`NtmGeometry`, `GeometryConfig.ntm`)</strong> ⋯</summary>

External-memory tape: LSTM controller + content-addressed heads; local credit learns copy via memory (0.958 @8000 steps, 3 seeds) — TODO.ntm_nca §11.14
</details>

<details>
<summary><strong>NCA Geometry (`NcaGeometry`, `GeometryConfig.nca`)</strong> ⋯</summary>

Neural cellular automaton fabric; local credit solves growing NCA (fg 1.000, 3 seeds) — TODO.ntm_nca §11.8
</details>

### CreditAssignment Primitives

<details>
<summary><strong>PEPITA / LEMMA Credit (`PepitaCredit`, `local_objective="lemma"`)</strong> ⋯</summary>

Published PEPITA input-modulation credit (BP parity 0.884) and the naming distinction from per-layer closed-form LEMMA — TODO15 §11.1/§11.2
</details>

### Algorithm Identity Cards

Every Credit, Update, and Plasticity primitive carries an
`AlgorithmIdentityCard` class attribute: reference equation, deviations
from the literature, the pseudo-gradient definition, validated limits,
and its verification level. Rendered cards live in
[`docs/IDENTITY_CARDS.md`](docs/IDENTITY_CARDS.md); the generator
(`scripts/generate_identity_cards.py --strict`) is wired into
pre-commit (C.1) and fails when a concrete primitive ships without
one.

---

### ML Library Capabilities

| Capability | Description |
|------------|-------------|
| **Composable systems** | Construct any 6-axis system coordinate via the `System` generic or factory functions (5-D systems are the `M = NullPlasticity` slice) — demonstrated live ([figure](docs/figures/d1_compose_6axis.png)) |
| **Common training API** | `SystemTrainer` — single interface for all learning rules, including joint systems via duck-typed `train_step`/`forward` |
| **Multiple learning rules** | Backprop, EqProp, FA, DFA, Forward-Forward, PEPITA, Target Prop, Predictive Coding, Hebbian/STDP, SNN, TileNet, 6-D joint (Routing, FastWeight) — credit swap demonstrated live ([figure](docs/figures/d2_swap_credit.png)) |
| **Substrate models** | Digital, Memristive (IR-drop), Neuromorphic (spikes), Photonic (phase), Quantum (unitary) |
| **Benchmarks & ablations** | 5-level hierarchy: adaptation, compute efficiency, structural robustness, algorithm migration, Z3 fixed-weights |
| **Stability / energy analysis** | Spectral radius, Lyapunov exponents, settling time, basin stability, free-energy tracking; frozen-θ lifecycle guarantee ([figure](docs/figures/d5_z3_frozen_theta.png)) |
| **EMA harvest** (`SystemTrainerConfig.harvest_mode`) | Probe-free streaming-weight harvest instrument; resurrected depth-50 (0.784→0.917) — TODO15 §13.3 / TODO16 §0.1 ([figure](docs/figures/d19_depth_harvest.png)) |
| **Recipe cards** (`recipe_cards.py`) | Family→optimizer/geometry/config canonical-constructor registry — TODO16 §0.3 |
| **I(C,U) predictive model** (`fit_icu_model.py`, `icu_report.py`) | Learnability-interaction law with 0.944 held-out lattice accuracy — TODO16 §4 |
| **Frozen-θ ψ benchmarks** (L1/L2/L3/L3.5, `psi_engaged`) | Frozen-θ ψ-only adaptation, recovery, and migration with θ bitwise-invariance audits — TODO16 §5 |
| **P-axis expressiveness probes** (`scripts/probes/w17_e*.py`) | Fixed-θ ψ mechanisms verified at probe scale: Kolmogorov compression (short ψ unfolds 32×32 patterns, 2.66× ratio), NCA rule reconfiguration (K distinct patterns from one seed, θ SHA-invariant, 3 seeds), sequential composition over NTM tape (max/sum/median at O(1) depth); σ_max(J_F) stability-expressiveness frontier measured. E1 (deep chaotic unfolding) falsified with a mechanism boundary — composition-error compounding — TODO17 |
| **I(C,U) ψ-orthogonality** (`harvest_icu_table.py`, `fit_icu_model.py`) | 3-seed measurement of ψ modulation on the credit×update surface: across tested configurations, observed ψ modulation averaged 2.0 percentage points (max 9.1 points, fa×muon routing). These measurements do not establish equivalence or negligibility; campaign-7.1 rows in `data/icu_measurements.csv`, `logs/w17_icu_fit.log` — TODO17 §5.1 |
| **Experiment sweeps / campaigns** | `comp campaign`, `comp benchmark`, `comp scientist` — structured hypercube exploration |
| **Distributed execution / deployment** | P2P (gRPC/Kademlia), multi-GPU (DDP/FSDP/DeepSpeed), ONNX/TorchScript/INT8/ternary export, FastAPI inference server |

---

### Architecture Diagram

```mermaid
flowchart LR
    S[Substrate] --> G[Geometry]
    G --> D[StateDynamics]
    D --> M[Plasticity]
    M --> C[CreditAssignment]
    C --> U[ParameterUpdate]
    U --> S
```

**Schematic Coupling Diagram** — arrows denote *data flow through the
ontology*, not execution order. The cyclic `U → S` edge represents
physical state updates (parameter consolidation altering substrate
state, e.g. memristive conductance), not a strict sequential pipeline.

<details>
<summary><strong>Why U → S cyclic dependency?</strong> ⋯</summary>

The cyclic dependency (U → S) reflects that parameter updates can alter substrate state (e.g., memristive conductance drift, weight quantization), which in turn affects subsequent forward passes. This is modeled explicitly in the joint transition operator.
</details>

---

### Algebraic Composition (API)

Construct systems by composing primitives across the six axes. The `System` generic and the `compose_*` factories catch invalid combinations at type-check time.

**One trainer, every credit rule** — the same coordinate trained through byte-identical wiring with a single swapped constructor argument. The block is locked verbatim against its source demo test ([`tests/integration/test_demo_swap_credit.py`](tests/integration/test_demo_swap_credit.py)); all three arms learn:

<!-- lock: swap_credit -->
```python
import torch

from computronium import (
    BackpropCredit,
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    EuclideanUpdate,
    GeometryConfig,
    NullPlasticity,
    ParameterUpdateConfig,
    RandomProjectionsCredit,
    RecurrentGeometry,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
    ThermodynamicContrast,
    compose_joint_system,
    create_task,
)

CREDIT_ARMS = (
    ("gradient", BackpropCredit()),
    ("thermodynamic_contrast", ThermodynamicContrast()),
    ("random_projections", RandomProjectionsCredit()),
)


def _flatten(loader):
    for x, y in loader:
        yield x.view(x.size(0), -1), y


task = create_task("mnist", device="cpu", quick_mode=True)
task.setup()
train_loader = task.get_dataloader("train")
config = SystemTrainerConfig(max_epochs=1, device="cpu", seed=42)
for name, credit in CREDIT_ARMS:
    torch.manual_seed(0)
    system = compose_joint_system(
        substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
        geometry=RecurrentGeometry(
            GeometryConfig.recurrent(
                input_dim=784, output_dim=10, hidden_dims=(32,)
            )
        ),
        dynamics=EnergyMinimizationDynamics(
            StateDynamicsConfig.energy_minimization(max_steps=3, beta=0.5)
        ),
        plasticity=NullPlasticity(),
        credit=credit,  # the one swapped argument
        update=EuclideanUpdate(ParameterUpdateConfig.euclidean(step_size=0.1)),
    )
    metrics = SystemTrainer(
        system=system, config=config, train_data=_flatten(train_loader)
    ).fit()[-1]
    print(f"{name}: {metrics['train_acc']:.1%}")
```
<details>
<summary><strong>Credit-swap demo explained</strong> ⋯</summary>

The credit-swap demo demonstrates that Backprop (global gradient), ThermodynamicContrast (energy-based local contrast), and RandomProjections (fixed random feedback) can all train the same recurrent geometry with only the credit constructor argument changed. This is the compositional abstraction in action: the geometry, dynamics, substrate, plasticity, and update remain identical.
</details>

<details>
<summary><strong>P-axis swaps work the same way</strong> ⋯</summary>

Pass `RoutingPlasticity(...)` / `FastWeightPlasticity(...)` / `SubstrateCoupledPlasticity(...)` (see [Plasticity](#-plasticity-metadynamics) in the axis table) as the `plasticity` argument of `compose_joint_system` — the null swap that retains what `NullPlasticity` forgets is demonstrated in `test_demo_swap_plasticity.py`.
</details>

<details>
<summary><strong>Formerly hardcoded model families → coordinates</strong> ⋯</summary>

Formerly hardcoded model families (`optical_looped_mlp`, `quantized_looped_mlp`, `crossbar_looped_mlp`, `eqprop_transformer`, `neural_cube`, `sparse_equilibrium`, `momentum_equilibrium`, TileNet variants) are now **expressed as coordinates/compositions** in this 6-axis space. These 5-D systems are recovered as the `M = NullPlasticity` slice.
</details>

---

### Research Direction Models (Experimental Variants)

These are native implementations of research directions and experimental variants expressed as first-class ontology coordinates. Several may overlap prior literature:

| Model | Coordinate | Description |
|-------|------------|-------------|
| `holomorphic_ep` | `QuantumSubstrate × RecurrentGeometry × EnergyMinimization × ThermodynamicContrast × EuclideanUpdate` | Complex-valued Equilibrium Propagation using holomorphic (analytic) activation functions and conjugate-transpose feedback pathways — complex-valued, not quantum: the quantum label applies only when running on the specific simulated unitary-gate substrate. Enables complex-domain credit assignment with potential for phase-based computation. |
| `directed_ep` | `DigitalSubstrate × RecurrentGeometry × EnergyMinimization × RandomProjections × EuclideanUpdate` | Directed/Asymmetric Equilibrium Propagation implementing Feedback Alignment within energy-based framework. Fixed random feedback matrices (no transport shortcut; FA is legitimate here — feedback is a fixed random matrix, not a transpose) with thermodynamic settling dynamics. |
| `finite_nudge_ep` | `DigitalSubstrate × RecurrentGeometry × EnergyMinimization × ThermodynamicContrast(beta≥1) × EuclideanUpdate` | Finite-Nudge Equilibrium Propagation using large β (finite nudge) instead of infinitesimal limit. Stronger supervision signals while maintaining equilibrium dynamics. |
| `ternary_eqprop` | `TernarySubstrate × RecurrentGeometry × EnergyMinimization × ThermodynamicContrast × EuclideanUpdate` | Ternary-weight Equilibrium Propagation with STE-based quantization. Weights constrained to {-α, 0, +α}. |
| `momentum_eqprop` | `DigitalSubstrate × RecurrentGeometry × EnergyMinimization(momentum) × ThermodynamicContrast × EuclideanUpdate` | Heavy-ball settling dynamics for faster equilibrium convergence. |
| `sparse_eqprop` | `SparseSubstrate × RecurrentGeometry × EnergyMinimization × ThermodynamicContrast × EuclideanUpdate` | Dynamic sparsity masks with efficient sparse matmul. |
| `diffusion_eqprop` | `DigitalSubstrate × RecurrentGeometry × DiffusionDynamics × ThermodynamicContrast × EuclideanUpdate` | Continuous-time diffusion settling dynamics. |

These models are available via the native API in `computronium.models.native`:

```python
from computronium.models.native import (
    create_native_holomorphic_ep,
    create_native_directed_ep,
    create_native_finite_nudge_ep,
    create_native_ternary_eqprop,
    create_native_momentum_eqprop,
    create_native_sparse_eqprop,
    create_native_diffusion_eqprop,
)
```

<details>
<summary><strong>Not claimed as novel algorithms</strong> ⋯</summary>

These models are not claimed as novel algorithms; they are *framework-native expressions* of research directions that can be systematically compared, ablated, and extended within the 6-axis ontology. The framework contribution is their common compositional representation and systematic comparison infrastructure.
</details>

---

## 🧬 Coupled Dynamical Systems

Historically, ML frameworks treat models as static computational graphs. Computronium treats them as **coupled dynamical systems**.

Computronium provides the ontology, infrastructure, and automation tooling used to investigate **limits imposed by stability, locality, and resource constraints**.

<details>
<summary><strong>Joint transition operator</strong> ⋯</summary>

By elevating the computational rule to a dynamical variable, we introduce a **joint transition operator** $z_{t+1} = F_{\theta_e}(z_t, u_t, \xi_t, \Delta t_t; G, S, D, P)$ unifying fast neural activity, inputs $u_t$, stochastic contributions $\xi_t$, elapsed time $\Delta t_t$, slow synaptic consolidation, and substrate physics. Existing 5-D learning systems are represented as the `M = NullPlasticity` slice of this joint 6-D formulation. The representation is substrate-aware; that does not by itself make any particular algorithm a physical process.
</details>

<details>
<summary><strong>Frozen-θ contract (Boundary Invariance, Stage-Boundary Invariance)</strong> ⋯</summary>

Within an episode, persistent θ is invariant: `FrozenThetaAudit`
(`computronium.core.frozen_theta`) snapshots geometry parameters,
substrate state tensors, and optimizer parameter groups at entry and
detects at exit — via clones, `Tensor._version` counters, and
`data_ptr()` — **in-place mutations**, *mutate-then-restore* (version
bumps survive a `copy_` rollback), **alias mutations**, and **storage
rebinding** (including added/removed tensors). Violations raise
`FrozenThetaError(AssertionError)`. This is enforced empirically
(`tests/property/joint/test_frozen_theta_audit.py`, adversarial suite)
— a sampled-numerical guard (Level 4), not a Level 1–3 derivation.
</details>

<details>
<summary><strong>P-axis: architectural capabilities (not a validated expressiveness capability)</strong> ⋯</summary>

The P-axis (ψ) provides **architectural** benefits independent of
benchmark performance: lifecycle control (ψ as a first-class dynamical
variable), intervention (frozen-θ ψ-only adaptation with bitwise θ
audits), and explicit routing (state-dependent gating over the NTM
tape or NCA fabric — the program becomes writable data on fixed
hardware θ). Whether ψ-mediated mechanisms outperform standard
recurrent memory on benchmarks remains an open empirical question;
the E1–E4 probes below report what was measured at probe scale.
</details>

<details>
<summary><strong>E-probe results (probe-scale evidence, not validated headline claims)</strong> ⋯</summary>

Compression (E2), fabric reconfiguration (E3), and program sequencing
over a tape (E4) are demonstrated at probe scale with frozen θ. Deep
*chaotic* unfolding (E1) is **falsified** with a recorded mechanism
boundary: under this architecture and precision, short-horizon local
learning failed to achieve the one-step accuracy needed for reliable
long-horizon rollout due to composition-error compounding (local
credit of fixed horizon T cannot control N-step composition error
unless T scales with N). A σ_max(J_F) stability–expressiveness
frontier on the NCA fabric is measured: most patterns cost nothing;
thin symmetric structure requires non-contractive rules.
</details>

<details>
<summary><strong>Campaign first records (probe-scale evidence, not validated headline claims)</strong> ⋯</summary>

**Credit × Update mechanistic study** (12 cells × 3 seeds, one-step
reset-state + 30-step trajectory arms, norm-matched): Muon gave the
best immediate transformation quality (eqprop×muon +0.324 vs euclidean
+0.221); the BP reference has the highest descent quality (+0.589) at
the smallest displacement; lemma cells measured near-inert at matched
norms. Records: `results/mechanistic_study/claim_record.json`.

**Stability × Memory campaign** (648 cells × 3 seeds × 8 trials,
store–delay–recall with contraction {0.5, 0.9, 1.05} × gate
{selective, ungated} × coupling {open, coupled} × precision {f32, f16,
bf16} × noise {0, 0.1} × readout {full, low-rank, 4-bit} × delay
{1, 8, 32}): selective (cue-gated) memory retains ≈ 1.0 at every
measured contraction rate and every delay, while ungated memory
collapses with distractor count (≈ 0.08 at delay 32). Feedback
coupling (memory into the state block) lowers the measured perturbation
decay but leaves retention unchanged — retention reads the memory
block only; the state-arm noise effect is reported separately as
`state_noise_divergence`. Records: `results/memory_stability/
claim_record.json`; scatter extraction via
`retention_contraction_scatter`. Both campaigns are Level 4 (sampled
numerical) / Level 5 (empirical).
</details>

---

## ⚡ Energy, Stability, and Dynamical Invariants

Energy binds Geometry and StateDynamics. The framework elevates the energy function `E(x)` to a first-class object, enabling mathematical stability analysis *before* implementation:

<details>
<summary><strong>Stability claims, stated at their actual strength</strong> ⋯</summary>

**Symmetric topology + EnergyMinimization**: under documented regularity and discretization assumptions, the specified dynamics admit a Lyapunov argument; convergence to an equilibrium depends on additional conditions stated per implementation (property-locked, Level 4). **Directed topology** → requires a Control-Lyapunov formulation (certified numerically for PredictiveSettlingDynamics). **Free energy tracking** → per-iteration Lyapunov certificates (`track_free_energy_per_iter`) for predictive coding and directed FA — Level 4 sampled numerical, consistent-with-descent, never proof.

**Stability metrics are explicitly separated** (TODO18 §2.1): the Asymptotic Stability Margin is the spectral radius $\rho(J_F)$ (via `spectral_radius_from_jacobian`); the Transient Amplification Bound is $\|J_F\|_2$ (via `dominant_singular_value`). These are different quantities on nonnormal Jacobians; `estimate_directional_amplification` measures finite-difference growth along probed directions and certifies neither $\rho$ nor $\sigma_{\max}$. Older materials quoting the estimator as "ρ(J)" are flagged `requires_rerun` in `docs/CORRECTIONS.md`.
</details>

### Verification Taxonomy

All claims in this repository are labeled by the 5-level taxonomy
(`computronium.verification`), enforced by `tests/property/test_verification_labels.py`:

| Level | Name | Meaning |
|:-----:|------|---------|
| 1 | Analytical | Pen-and-paper derivation |
| 2 | Machine-checked | Proof assistant / solver certificate |
| 3 | Certified numerical | Rigorous bound (interval arithmetic etc.) |
| 4 | Sampled numerical | Property tests, finite-difference checks, seeds |
| 5 | Empirical | Observed behavior, no bound |

The CI gate relies primarily on **Level 4** (sampled numerical) and **Level 5** (empirical). No CI test confers Level 1–3 status; wording that says otherwise is a defect.

<details>
<summary><strong>Joint dynamics extension</strong> ⋯</summary>

The joint extension of these dynamics — composite state $z_t = (x_t, \psi_t, \sigma_t)$, lifecycle registry, episode-boundary consolidation — is specified once in *Core Architecture* below. Campaign tooling treats the **stability-plasticity trade-off** and resource constraints as explicit search constraints rather than afterthoughts; the **AutoScientist** searches the declared ontology space and records experiment results.
</details>

---

## 🖥️ CLI: Use Cases

All entry points installed with `uv sync --dev`. The CLI is consolidated under the `comp` dispatcher:

```bash
comp <command> [args]
```

### CLI Reference

> **Note:** `comp scientist` and `comp frontier` are **automation tools**
> for exploring the 6-axis space and ranking measured results — not
> guarantees of finding superior algorithms. All AutoScientist output is
> hypothesis-generating evidence at probe scale.

All subcommands of the `comp` dispatcher:

| Command | Purpose | Example |
|---------|---------|---------|
| `comp run` | Campaign runner (validate/plan/run) | `comp run from-config --config configs/presets/backprop_mnist.yaml` |
| `comp report` | Render experiment reports | — |
| `comp parity` | Backprop parity benchmark | — |
| `comp repro` | Reproducibility verification | — |
| `comp hpo` | Hyperparameter optimization | — |
| `comp audit` | Registry metadata audit | — |
| `comp validate` | Run verification suite; optional knowledge-base recording | — |
| `comp scientist` | AutoScientist: autonomous exploration of the 6-D space | `comp scientist --campaign <campaign.yaml>` |
| `comp frontier` | Pareto frontier analysis | `comp frontier --study study_name` |
| `comp rank` | Family ranking from HPO studies | — |
| `comp lab` | Interactive experiments, training, benchmarks | `comp lab benchmark --domain vision --quick` |
| `comp joint-validate` | Validate arbitrary 6-axis joint coordinates | `comp joint-validate --coordinate S=Memristive,G=TileMesh,...` |
| `comp campaign` | Run/compare/resume joint campaigns; render the static discovery report (HTML/JSON) | `comp campaign run --config <campaign.yaml>` |
| `comp stability` | Stability-plasticity frontier reports | `comp stability --model eqprop_mlp --task mnist` |
| `comp benchmark` | Joint benchmark suites (adaptation, Z3, etc.) | `comp benchmark run --suite adaptation_efficiency` |
| `comp gallery` | Render the demo suite's figures + manifest from live run records | `comp gallery --run` |

Module entry points (not installed as scripts):

```bash
uv run python -m computronium.p2p.grpc_worker --node-id worker_0 --device cpu   # P2P worker
uv run python -m computronium.cli.export_kernel --algorithm eqprop --target fpga  # kernel export
```

---

## 📦 Installation

Prerequisites: **Python 3.14+** (3.13 minimum for the free-threaded build),
**PyTorch 2.x** (pulled in by `uv sync`), and — optionally — a CUDA GPU
with a matching PyTorch build for GPU paths (everything runs on CPU; the
determinism locks are pinned to small dims, so keep them on CPU).

```bash
uv sync --dev
```

### Quickstart: Forward-Forward vs Backprop in <2 Minutes

```bash
uv run scripts/quickstart.py
```

<details>
<summary><strong>Why Forward-Forward?</strong> ⋯</summary>

FF uses layer-local objectives and avoids conventional backward propagation through the network (layer-local objectives; no transport shortcut). The quickstart is a small reproducibility smoke test comparing FF with Backprop on MNIST—not a benchmark result. `scripts/quickstart.py` is the canonical entry point.
</details>

### Quickstart: Compose a Six-Axis System

<details>
<summary><strong>Demo test source</strong> ⋯</summary>

The block below is the opening of [`tests/integration/test_demo_compose_6axis.py`](tests/integration/test_demo_compose_6axis.py) — the demo test that shows it working, locked verbatim against it. Compose a system from all six ontology axes and train it on MNIST.
</details>

<!-- lock: composition_6axis -->
```python
import torch

from computronium import (
    DigitalSubstrate,
    EnergyMinimizationDynamics,
    EuclideanUpdate,
    GeometryConfig,
    NullPlasticity,
    RecurrentGeometry,
    StateDynamicsConfig,
    SubstrateConfig,
    SystemTrainer,
    SystemTrainerConfig,
    ThermodynamicContrast,
    compose_joint_system,
    create_task,
)


def _flatten(loader):
    for x, y in loader:
        yield x.view(x.size(0), -1), y


task = create_task("mnist", device="cpu", quick_mode=True)
task.setup()
train_loader = task.get_dataloader("train")

torch.manual_seed(0)
six_axis = compose_joint_system(
    substrate=DigitalSubstrate(SubstrateConfig.digital(device="cpu")),
    geometry=RecurrentGeometry(
        GeometryConfig.recurrent(input_dim=784, output_dim=10, hidden_dims=(32,))
    ),
    dynamics=EnergyMinimizationDynamics(
        StateDynamicsConfig.energy_minimization(max_steps=5, beta=0.5)
    ),
    plasticity=NullPlasticity(),
    credit=ThermodynamicContrast(),
    update=EuclideanUpdate(),
)
trainer = SystemTrainer(
    system=six_axis,
    config=SystemTrainerConfig(max_epochs=1, device="cpu", seed=42),
    train_data=_flatten(train_loader),
)
history = trainer.fit()
print(f"train accuracy: {history[-1]['train_acc']:.1%}")
```

<details>
<summary><strong>Expected result</strong> ⋯</summary>

One epoch on CPU trains this coordinate to ≈ 0.9 (chance 0.1). The same test goes on to demonstrate J1 (a 5-D build trained identically produces bitwise-equal θ) and the L6 config round-trip. Run `pytest tests/integration/ -k demo` to watch every capability demonstrate itself.
</details>

### Config-Driven Training

```bash
# Using preset YAML configs
comp run from-config --config configs/presets/eqprop_mnist.yaml
comp run from-config --config configs/presets/backprop_mnist.yaml
comp run from-config --config configs/presets/eqprop_routing_mnist.yaml
```

---

## 🏭 13 Model Factories — One-Line API

All factories are available via `from computronium import ...` and compose 6-axis ontology systems in one call (5-D systems are the `M = NullPlasticity` slice). Each has a matching YAML preset in `configs/presets/`.

<details>
<summary><strong>Provenance disclaimer</strong> ⋯</summary>

Implemented algorithms are generally literature-derived baselines or variants; the framework contribution is their common compositional representation and systematic comparison.
</details>

| Factory | Axis Coordinate (S × G × D × M × C × U) | Preset YAML | Description | Provenance |
|---------|-----------------------------------------|-------------|-------------|------------|
| `create_backprop_mlp` | Digital × Feedforward × Instantaneous × Null × Backprop × Euclidean | `backprop_mnist.yaml` | Standard backprop MLP — baseline | Rumelhart et al. (1986) |
| `create_eqprop_mlp` | Digital × Recurrent × EnergyMinimization × Null × ThermodynamicContrast × Euclidean | `eqprop_mnist.yaml` | Equilibrium Propagation: energy-based, local contrastive updates; requires reciprocal/symmetric interactions | Scellier & Bengio (2017) |
| `create_fa_mlp` | Digital × Feedforward × Instantaneous × Null × RandomProjections × Euclidean | `fa_mnist.yaml` | Feedback Alignment: fixed random feedback weights (no transport shortcut) | Lillicrap et al. (2016) |
| `create_ff_mlp` | Digital × Feedforward × Instantaneous × Null × LocalGoodness × Euclidean | `ff_mnist.yaml` | Forward-Forward: two forward passes (pos/neg), layer-local goodness objective | Hinton (2022) |
| `create_pepita_mlp` | Digital × Feedforward × Instantaneous × Null × PepitaCredit × Euclidean | `pepita_mnist.yaml` | Published PEPITA (arXiv 2201.11665): one fixed random B, error-modulated second forward pass, autograd update — distinct from Forward-Forward goodness (`create_lemma_mlp` composes the LEMMA rule) | Dellaferrera & Kreiman (2022) |
| `create_tp_mlp` | Digital × Feedforward × Instantaneous × Null × TargetInversion × Euclidean | `tp_mnist.yaml` | Target Propagation: learns inverse mappings layer-wise, target-based credit assignment | Bengio (2014); Lee et al. (2015) |
| `create_pc_mlp` | Digital × Feedforward × PredictiveSettling × Null × ThermodynamicContrast × Euclidean | `pc_mnist.yaml` | Predictive Coding: hierarchical prediction error minimization, convergent dynamics | Rao & Ballard (1999); Whittington & Bogacz (2017) |
| `create_hebbian_mlp` | Digital × Feedforward × Instantaneous × Null × TemporalTrace × Euclidean | `hebbian_mnist.yaml` | Hebbian/STDP: local correlation-based plasticity | Hebb (1949); Bi & Poo (1998) |
| `create_snn_mlp` | Digital × Feedforward × SpikeIntegration × Null × TemporalTrace × Euclidean | `snn_mnist.yaml` | Spiking Neural Network: LIF neurons, spike-timing-dependent plasticity | Maass (1997); Gerstner et al. (2014) |
| `create_tile_mlp` | Digital × TileMesh × Instantaneous × Null × (varies) × Euclidean | `tile_mnist.yaml` | TileNet: modular tiled architecture, supports all credit assignments | Framework implementation |
| `create_routing_mlp` | Digital × Recurrent × Instantaneous × RoutingPlasticity × Backprop × Euclidean | `routing_mnist.yaml` | **6-D Joint**: state-dependent gating, sparse pathway routing, dynamic compute | Framework implementation |
| `create_fast_weight_mlp` | Digital × Recurrent × Instantaneous × FastWeightPlasticity × Backprop × Euclidean | `fast_weight_mnist.yaml` | **6-D Joint**: episode-local associative memory via fast-weight matrices | Ba et al. (2016); framework impl. |
| `create_memristive_mlp` | Memristive × Feedforward × Instantaneous × Null × Backprop × Euclidean | `memristive_mnist.yaml` | **Substrate-aware**: IR-drop, conductance bounds, noise | Framework implementation |

### 5-D Factory Usage Examples

```python
from computronium import (
    create_backprop_mlp,
    create_eqprop_mlp,
    create_fa_mlp,
    create_ff_mlp,
    create_pepita_mlp,
    create_tp_mlp,
    create_pc_mlp,
    create_hebbian_mlp,
    create_snn_mlp,
    create_tile_mlp,
)

# All factories share the signature: input_dim, hidden_dims (tuple), output_dim, lr, device
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
input_dim, output_dim = 784, 10

# Backprop (baseline)
system = create_backprop_mlp(input_dim, (256, 128), output_dim, lr=0.001, device=device)

# Equilibrium Propagation (energy-based)
system = create_eqprop_mlp(
    input_dim,
    (512, 512, 512),
    output_dim,
    beta=0.1,
    inference_steps=20,
    lr=0.001,
    device=device,
)

# Feedback Alignment (fixed random feedback, no transport shortcut)
system = create_fa_mlp(input_dim, (256, 128), output_dim, lr=0.001, device=device)

# Forward-Forward (local layer-wise, 3 epochs)
system = create_ff_mlp(
    input_dim,
    (256, 256),
    output_dim,
    layer_lr=0.03,
    classifier_lr=0.01,
    threshold=2.0,
    num_layers=2,
    device=device,
)

# PEPITA (FF variant)
system = create_pepita_mlp(input_dim, (256, 128), output_dim, lr=0.01, device=device)

# Target Propagation
system = create_tp_mlp(input_dim, (256,), output_dim, lr=0.001, device=device)

# Predictive Coding
system = create_pc_mlp(input_dim, (256, 256), output_dim, lr=0.001, device=device)

# Hebbian
system = create_hebbian_mlp(input_dim, (256,), output_dim, lr=0.001, device=device)

# Spiking
system = create_snn_mlp(input_dim, (256,), output_dim, lr=0.001, device=device)

# TileNet (modular tiles)
system = create_tile_mlp(
    input_dim,
    (256,),
    output_dim,
    lr=0.001,
    neurons_per_tile=16,
    tiles_per_layer=2,
    device=device,
)
```

<details>
<summary><strong>Training wiring</strong> ⋯</summary>

Training wiring is identical for every factory — wrap in `SystemTrainer` as shown in the Compose a Six-Axis System quickstart above.
</details>

### 6-D Joint Factories (Non-Null Plasticity)

```python
from computronium import create_routing_mlp, create_fast_weight_mlp

# RoutingPlasticity: state-dependent gating, sparse pathway routing
system = create_routing_mlp(
    input_dim, (256,), output_dim, lr=0.001, gate_dim=32, device=device
)

# FastWeightPlasticity: episode-local associative memory
system = create_fast_weight_mlp(
    input_dim, (256,), output_dim, lr=0.001, fast_weight_dim=128, device=device
)
```

---

### Quickstart: Interactive Demo

```bash
uv run python demo/main.py
```

Launches a NiceGUI web dashboard at `http://localhost:8080` with:
- Model training across ontology coordinates
- Live loss/accuracy curves
- Hyperparameter controls
- Live Campaign tab: discovery report (𝒞-Pareto frontier, replication gate, counterfactual attribution) over commissioned campaign artifacts or in-progress campaigns
- AutoScientist hypothesis proposals

---

## 🏗️ Core Architecture

### 1. Ontology Protocols (`computronium/core/ontology.py`)

<details>
<summary><strong>Protocol details</strong> ⋯</summary>

Five `Protocol` classes with PEP 695 generics, frozen slotted config dataclasses, and reference implementations for every primitive — pure, composable infrastructure. See `computronium/core/ontology.py` for full Protocol definitions.
</details>

- `Substrate` — `forward_operator`, `weight_update_operator`
- `Geometry` — `forward`, `route`
- `StateDynamics` — `settle`
- `CreditAssignment` — `compute_pseudo_gradient`, `surrogate_objective`
- `ParameterUpdate` — `step`

### 2. Joint Architecture Protocols (`computronium/core/joint/`)

<details>
<summary><strong>Joint protocol details</strong> ⋯</summary>

The joint dynamical system elevates the computational rule to a dynamical variable via the **CoupledTransition** protocol operating on `CompositeState`. Key types defined in `computronium/core/joint/state.py`, `computronium/core/joint/context.py`, `computronium/core/joint/transition.py`.
</details>

- **CompositeState** — joint intra-episode state $z_t = (x_t, \psi_t, \sigma_t)$ with `activity`, `plastic`, `substrate` mappings
- **SystemContext** — immutable context: `theta`, `geometry`, `substrate_physics`, `registry`, `config` (6-axis)
- **StateVariable** — lifecycle metadata: `persistent`, `fast_plastic`, `substrate_owned`, `consolidatable`
- **StateRegistry** — registers variables, validates lifecycle, provides lifecycle groups; resolves ontological overlaps where one physical variable serves multiple roles (e.g., memristive conductance as both substrate state and plastic medium)
- **CoupledTransition** — linchpin protocol: `step(z, context) -> CompositeState` executing $z_{t+1} = F_\theta(z_t; G, S)$
- **PlasticityPrimitive** — P-axis protocol: `step(psi, z, context) -> updated psi`
- **StabilityMonitor** — `spectral_radius`, `lyapunov_exponent` estimation

**Key Architectural Rule**: *Plasticity must not become a weight preprocessor.* Plasticity receives the full joint state $z = (x, \psi, \sigma)$, returns updated plastic state (not modified weights), and the joint transition remains $z_{t+1} = F_\theta(z_t; G, S)$. Credit assignment receives the full trajectory $\tau = [z_0, ..., z_T]$. Parameter update touches only `persistent`/`consolidatable` variables.

### 3. System & Trainers

| Component | Purpose |
|-----------|---------|
| `System[TS, TG, TD, TM, TC, TU]` | Generic 6-layer composition; invalid combos caught at type-check |
| `compose_joint_system` | Composes a 6-axis joint system from primitives or configs; with `NullPlasticity` it delegates to the 5-D pipeline (J1 Zero-Extension) |
| `SystemTrainer` | **Single training loop**: duck-types the joint training surface — any system exposing `train_step`/`forward`; executes `Geometry.forward → StateDynamics.settle → …` for the 5-D pipeline |
| `DistributedSystemTrainer` | In-process P2P coordination; shards along Geometry (TileMesh), federates at ParameterUpdate; CreditAssignment stays local |
| `ModelAdapter` | Strangler Fig adapter: projects legacy Registry models → 5-D System via metadata inference with per-family tolerance calibration |
| `Registry.to_system()` | One-call projection of any registered component |

<details>
<summary><strong>Zero-Extension Invariant</strong> ⋯</summary>

$M=\text{Null}, \psi=\text{const}, \sigma=\sigma_0 \implies F_\theta(z)|_x = D_\theta(x)$. The 5-D system is formally a slice of the 6-D coupled dynamical system, not a parallel architecture; slow consolidation touches persistent θ only at episode boundaries, $\theta_{e+1} = U(\theta_e, C(\tau_e))$. J1 test certifies this equivalence within numerical tolerance.
</details>

### 4. Factories (`computronium/core/system_trainer/`)

Factory functions for composing systems from primitives or configs:

```python
from computronium.core.system_trainer import (
    compose_system,
    compose_system_from_configs,
    extract_config,
    compose_joint_system,
    compose_joint_system_from_configs,
    create_eqprop_system,
    create_backprop_system,
    create_fa_system,
)

# Config round-trip (L6 lock)
configs = extract_config(system)
system2 = compose_system_from_configs(**configs)
assert extract_config(system2) == configs  # identity verified

# Joint system composition
joint = compose_joint_system(
    substrate=DigitalSubstrate(SubstrateConfig.digital()),
    geometry=RecurrentGeometry(...),
    dynamics=EnergyMinimizationDynamics(...),
    plasticity=RoutingPlasticity(...),
    credit=ThermodynamicContrastCredit(),
    update=EuclideanUpdate(),
)
```

### 5. Substrate Models ✅

| Substrate Model | What Is Modeled | Simulation vs. Physical | Verification |
|-----------------|-----------------|-------------------------|--------------|
| `DigitalSubstrate` | CPU/GPU execution | Native execution | — |
| `MemristiveSubstrate` | Conductance matrices, bounded precision, IR-drop noise | Simulated energy / estimated energy | Gradient equivalence vs. digital; positive bounded conductance |
| `NeuromorphicSubstrate` | Async spike routing, strict sparsity, passivity | Simulated spikes, no physical neuromorphic hardware | Property test: deterministic noise cancels in diff (‖na-nb‖ ≤ ‖a-b‖) |
| `OpticalSubstrate` | Phase/amplitude encoding, coherent interference | Simulated phase; no physical optical hardware | Phase wrapping to [-π, π]; no NaN/inf outputs |
| `QuantumSubstrate` | Parameterized unitary gates, parameter-shift rule | Simulated unitaries; no quantum hardware | Parameter-shift matches finite-difference (cosine ≥ 0.999) |

<details>
<summary><strong>Simulation vs. physical disclaimer</strong> ⋯</summary>

Current substrate implementations are primarily computational models; physical-hardware validation is future work.
</details>

<details>
<summary><strong>Energy terminology precision</strong> ⋯</summary>

**Terminology:** *simulated energy*, *estimated energy*, *hardware-measured energy*. Avoid generic "energy efficiency" unless measurement methodology is stated.
</details>

---

## 🔬 Validation Framework: Property-Verified Hypercube

The framework enforces **correctness by construction** through a layered verification regime. The fast-CI gate validates the entire hypercube in seconds on CPU.

### Verification Status Markers

| Status | Meaning |
|--------|---------|
| **Implemented** | Code exists and runs |
| **Verified** | Property-lock tests pass (Hypothesis, numerical equivalence — Level 4 sampled numerical) |
| **Benchmarked** | Measured on tasks with reported metrics |
| **Hypothesized** | Research question; not yet empirically established |
| **Planned** | Future work; not yet implemented |

<details>
<summary><strong>Verification ≠ scientific superiority</strong> ⋯</summary>

A passing invariant or numerical-equivalence test demonstrates **implementation correctness**, not scientific superiority.
</details>

### ✅ Property Locks (L1–L7 + S/G/D/C/U/M Axes + J1–J7)

| Lock | Property | Key Assertions |
|------|----------|----------------|
| **L1** | Composed systems train & produce valid metrics | Backprop/FA/Tile systems train; loss≥0, accuracy∈[0,1] |
| **L2** | Pipeline stages pure functions of preceding axes | Geometry.forward deterministic; credit independent of update; substrate noise only effect |
| **L3** | Locality axioms: ThermodynamicContrast invariant to non-local perturb; FA feedback fixed at init & seed-independent | Layer-0 pseudo-gradient invariant; B matrices fixed; different seeds → different B |
| **L4** | Lyapunov/energy: energy non-increasing; Control-Lyapunov for PredictiveSettling | Energy monotonic (EqProp); free energy non-increasing (PredictiveCoding); convergence threshold |
| **L5** | Determinism: same seed + same device = bitwise equal params & metrics (CPU & GPU deterministic) | Parametrized over system factories |
| **L6** | Round-trip & totality: configs round-trip identity; Registry.to_system() projects all registered models | Identity on configs; protocol conformance on projected systems |
| **L7** | Distributed seam: SystemTrainer runs; fault tolerance | gRPC fault injection test captures lost workers, step, partial metrics |
| **S-axis** | Neuromorphic passivity; Quantum parameter-shift equivalence | Deterministic noise cancellation; cosine ≥ 0.999 vs FD |
| **D-axis** | SpikeIntegration Lyapunov (membrane bounded, non-diverging spike process); LazyStateDynamics | Spike counts tracked per (layer, settle step); bounded activations |
| **C-axis** | TemporalTrace STDP window (causal +, anti-causal -, antisymmetric, exponential decay); surrogate objectives | Sign matches timing; W(Δt) = -W(-Δt); FD cosine ≥ 0.95 |
| **U-axis** | Muon orthogonalizes gradient (G^T G ≈ I); SpectralConstrained SVD ≤ 1.0; Natural whitens; Elastic moves toward old params | Newton-Schulz converges; diagonal Fisher whitening; δ·(w-old_w) < 0 |
| **P-axis** | NullPlasticity Zero-Extension (`F_θ^Null = D_θ`); RoutingPlasticity gate entropy; FastWeightPlasticity decay bounds | Null ≡ 5-D; gate entropy ≥ 0; decay ∈ [0,1] |
| **J1** | NullPlasticity preserves 5-D dynamics (Zero-Extension Invariant) | $F_\theta^\text{Null} = D_\theta$ within numerical tolerance |
| **J2** | Persistent θ not mutated during intra-episode steps | θ data_ptr() unchanged during CoupledTransition.step |
| **J3** | fast_plastic variables mutate only through plasticity projection | ψ updates only via PlasticityPrimitive.step |
| **J4** | substrate_owned variables respect substrate physics constraints | σ updates only via Substrate.forward_operator |
| **J5** | consolidatable variables promoted only at episode boundaries | consolidate() only called at episode end |
| **J6** | Cross-adapters preserve joint transition shape & registry semantics | Adapter output is valid CompositeState projection |
| **J7** | Trajectory records contain full z = (x, ψ, σ) | JointTrajectory has activity, plastic, substrate at each step |

### 🧬 Biologically Motivated Property Tests (Hypothesis-based)

<details>
<summary><strong>Not established biological axioms</strong> ⋯</summary>

These are biologically motivated constraints/hypotheses encoded as property tests—not established biological axioms.
</details>

| Motivated Constraint | Test | Method | Threshold |
|------|------|--------|-----------|
| **EP Gradient Equivalence** | EqProp gradient aligns with BPTT | Cosine similarity | ≥ 0.5 |
| **Lyapunov Energy Descent** | Free energy monotonically non-increasing along relaxation | Hypothesis | Slack 1e-3; final < initial |
| **Contraction Mapping** | Relaxation operator Lipschitz < 1 | Pairwise distance ratio L < 1; directional amplification growth < 1 (`estimate_directional_amplification`) | Step sizes 0.1–0.5 |
| **Fixed-Point Reliability** | Unique attractor from random initializations | Relative diff < 1e-3; Idempotence ‖T(h*)-h*‖ < 1e-4 | |
| **Weight-Transport Freeness** | FA backward weights ≠ forward transpose; separate memory | ‖B - W^T‖ > 1e-3; data_ptr() distinct | standard_fa, adaptive_fa, DFA |
| **Adaptive-FA Alignment** | Feedback matrices align with forward weights over training | cos(B, W^T) improvement > 0.05 | biologically slow B regime |

### ✅ Integration Verification Gates (All Passing)

<details>
<summary><strong>Scope disclaimer</strong> ⋯</summary>

Scope: current CI / repository verification status — not evidence of scientific or benchmark superiority.
</details>

| Gate | Result |
|------|--------|
| Gradient equivalence (finite-difference) | CE families cos≥0.9: backprop, FA, DirectFA, StochasticFA, MEP-backprop; MSE families cos≥0.6: EqProp, MEP-EP, CHL |
| Ontology layer equivalence | ThermodynamicContrast=Backprop under InstantaneousDynamics; RiemannianOrthogonal preserves orthogonality; EnergyMinimization converges |
| Energy invariants (property-locked, Level 4) | Lyapunov descent, Control-Lyapunov, Substrate passivity, EqProp energy, Composition |
| Kernel equivalence (Triton vs PyTorch) | max_diff < 1e-5, rel_diff < 1e-4 |
| Kernel accuracy parity | FA, Backprop, PEPITA, DTP: kernel accuracy within 1% of reference on digits/synthetic |
| Registry audit | 0 missing critical fields |
| Reproducibility | Models bitwise reproducible |
| Backprop parity | Runs successfully |
| Static typing | 0 errors on `computronium/ontology` (pyright elevated-standard, pre-commit gated); repo-wide basic |
| Formatting | Clean |

### 🧪 Test Commands

```bash
# Property locks (fast CI gate) — 5-D
uv run pytest tests/property/test_ontology_locks.py -q

# Property locks (fast CI gate) — 6-D Joint Architecture
uv run pytest tests/property/joint/ -q

# Core ontology unit tests
uv run pytest tests/unit/core/test_ontology.py -q

# Integration: gradient equivalence + energy proofs
uv run pytest tests/integration/test_gradient_equivalence.py tests/integration/test_energy_invariants.py -q

# Kernel equivalence (Triton vs PyTorch)
uv run pytest tests/integration/test_kernel_equivalence.py -q

# Kernel accuracy parity (end-to-end learning)
uv run pytest tests/integration/test_kernel_accuracy_parity.py -q

# gRPC seam test
uv run pytest tests/integration/test_grpc_seam.py -q

# Demonstration suite (the evidence layer: compose, swap credit, swap
# plasticity, memory wall, frozen θ) + figure lock
uv run pytest tests/integration/ -k demo
uv run pytest tests/integration/test_gallery_lock.py -q

# Joint integration tests
uv run pytest tests/integration/joint/ -q

# Full suite
uv run pytest tests/ -q

# Type checking (strict)
uv run pyright .

# Formatting & linting
uv run ruff format --check . && uv run ruff check .
```

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

### Frontier Record

Defined in `computronium/core/campaign/frontier_record.py`:

```python
@dataclass(frozen=True, slots=True)
class FrontierRecord:
    coordinate: SystemCoordinate
    task_loss: float
    adaptation_time: int
    rho_jacobian: float
    lyapunov_local: float
    settling_time: float
    basin_stability: float
    resources: ResourceUsage
```

### 5-Level Benchmark Hierarchy

<details>
<summary><strong>Experimental questions, not established results</strong> ⋯</summary>

The five experimental questions — adaptation efficiency, compute efficiency, structural robustness, algorithm migration, Z3 fixed-weights — are specified once per experiment (question, toy task, comparison axes, file) in the *Experiment Suite* below, each with a runnable `comp benchmark run --suite …` command. They define experimental questions, not established results.
</details>

---

### ⚠️ Research Status

**Core abstractions, implementations, and verification infrastructure are under active development. Large-scale empirical campaigns and physical-hardware validation remain future work. The repository presents hypotheses and experimental machinery, not validated claims of superior learning efficiency.**

## 🤖 Automated Research: Hypercube Campaigns

The AutoScientist is an automated research agent that proposes, executes, and analyzes experiments across the 6-D ontology space. It uses chain-of-thought reasoning over ontology axes, retrieves prior art from arXiv, generates counterfactuals, and maintains a persistent knowledge base of experimental results.

The 6-axis decomposition gives the **AutoScientist** a **structured search space** instead of a flat model list:


| Campaign Type | Fixed Axes | Varied Axis | Example Hypothesis |
|---------------|------------|-------------|-------------------|
| Substrate Ablation | G, D, M, C, U | S: Digital → Memristive/Optical/Quantum | At what IR-drop does EqProp parity break? |
| Epistemology Swap | S=Optical, G=TileMesh, D=EnergyMinimization | C: ThermodynamicContrast ↔ RandomProjectionsCredit | Does optical hardware favor FA (lower settling energy)? |
| Kinetics Discovery | S, G, D, C | U: Euclidean ↔ Riemannian ↔ Spectral ↔ Natural | Can Spectral constraints stabilize Memristive settling? |
| Plasticity Search | S, G, D, C, U | M: Null ↔ Routing ↔ FastWeight | Does routing reduce compute at stability margin? |
| Composite | S=Memristive, D=EnergyMinimization, M=Routing | U=SpectralConstrained | "IR-drop (S) + Routing (M) + Spectral (U) → stable settling (D)" |
| Stability-Plasticity Trade-off | S, G, D, C, U | M + ρ(J_F) constraint | Maximize adaptation s.t. ρ(J_F) ≈ 0.99 |

**Key AutoScientist capabilities:**
- 🧠 Chain-of-thought templates operating on ontology axes
- 📚 arXiv retrieval + semantic search for prior art
- 🔀 Counterfactual generator: "What if β schedule changed?"
- 📊 Knowledge Base meta-analysis: scaling laws, algorithm fingerprinting, failure manifold clustering, algorithm phylogeny
- 💾 Campaign persistence/resume (YAML+SQLite, git-like branching) — **includes joint state z, θ, ψ, σ**
- 👁️ Human-in-the-loop dashboard (NiceGUI, WebSocket live updates)
- 🖥️ Local LLM support (Ollama auto-pull, llama.cpp quantization, speculative decoding)
- ⚡ **Joint Kernel Cache**: Persisted compiled kernels for `CoupledTransition.step`, plasticity updates, stability estimators
- 🛡️ **Fault Tolerance**: Checkpoint-based recovery for multi-hour campaigns on spot instances

---

## 🧪 Experiment Suite

| Status | Meaning |
|--------|---------|
| **Implemented** | Experiment code exists |
| **Run** | At least one reproducible execution exists |
| **Analyzed** | Results have been systematically analyzed |
| **Published** | Results reported externally |

### 5-D Experiment Implementations

| Experiment | File | Purpose |
|------------|------|---------|
| TileNet Scaling Sweep | `computronium/experiments/tile_scaling.py` | Depth/width scaling on MNIST/CIFAR-10 across tile algorithms + backprop |
| EqProp Vision Parity | `computronium/experiments/eqprop_vision_parity.py` | EqProp variants on MNIST/Fashion-MNIST/CIFAR-10/SVHN |
| MEP Preset Tournament | `computronium/experiments/mep_tournament.py` | Factorized ablation: gradient×update×constraint×feedback with ANOVA + Sobol |
| FA Depth Scaling | `computronium/experiments/fa_depth_scaling.py` | Extreme depth, MNIST + synthetic parity |
| MoT Ablation | `computronium/experiments/mot_ablation.py` | Dense vs sparse tile routing (top-k, random, learned) |
| Cross-Domain Transfer | `computronium/experiments/cross_domain_transfer.py` | Vision→LM/RL/graph transfer, local vs global learning |
| Tile Algorithm Comparison | `computronium/experiments/tile_algorithm_comparison.py` | Fair comparison of PC/EP/FA/TP/Hebbian/SNN/Backprop on same substrate |

### 6-D Joint Experiments — In Development

| Level | Experiment | File | Question | Toy Task / Constraint | Compare |
|-------|------------|------|----------|----------------------|---------|
| **1** | Adaptation Efficiency | `computronium/experiments/joint/adaptation_efficiency.py` | Does plasticity adapt faster than Null under matched compute? | Switching distribution (Phase A: y=f_A(x), Phase B: y=f_B(x)) | Null vs FastWeight vs Routing; adaptation time, energy |
| **2** | Compute Efficiency | `computronium/experiments/joint/compute_efficiency.py` | Does routing reduce effective operations (dynamic sparsity)? | Mixture-of-experts (one route needed per input) | Active units, gate entropy, effective matmul |
| **3** | Structural Robustness | `computronium/experiments/joint/structural_robustness.py` | Can the system recover after topology/device damage via autonomous rerouting? | Zeroed weights, removed nodes, dead channels, noisy memristive | Null vs Routing vs SubstrateCoupled; recovery |
| **3.5** | Algorithm Migration | `computronium/experiments/joint/algorithm_migration.py` | Can ψ switch strategy A₀→A₁ without changing θ? | Task A₀: cumulative sum → Task A₁: last symbol | time(A₀→A₁), energy; parameter invariance: ‖θ_after − θ_before‖ = 0 |
| **4** | Z3: Fixed Weights, Changing Algorithm | `computronium/experiments/joint/z3_fixed_weights.py` | Can frozen θ solve multiple tasks via ψ-mediated rule selection? | θ frozen. Tasks: parity, last-symbol, threshold. Operators: Identity, Threshold, Accumulate, LastSymbol, Parity, SparseTopKRoute, SignFlip, Delay | Adaptation time, energy, operator diversity; parameter invariance must be exact: ‖θ_after − θ_before‖ = 0 |

<details>
<summary><strong>Canonical 5-level benchmark hierarchy</strong> ⋯</summary>

Canonical specification of the 5-level benchmark hierarchy (see *Stability-Plasticity Trade-off Hypothesis* above). All questions remain open.
</details>

Commands:
```bash
comp benchmark run --suite adaptation_efficiency
comp benchmark run --suite compute_efficiency
comp benchmark run --suite structural_robustness
comp benchmark run --suite algorithm_migration
comp benchmark run --suite z3_fixed_weights
```

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
# Run vision benchmark (all models, all vision tasks)
comp lab benchmark --domain vision --quick

# Run specific model on MNIST
comp lab core-train --model eqprop_mlp --task mnist --epochs 10

# Cross-domain transfer: vision → LM
uv run python -m computronium.experiments.cross_domain_transfer --source vision --target lm
```

### 📝 Language Modeling Domain

**Tasks**: `tiny_shakespeare` (char), `char_ngram`; `wikitext2`, `penn_treebank` (planned)

**Key Experiments**
```bash
# Run LM benchmark
comp lab benchmark --domain lm --quick
```

### 🎮 Reinforcement Learning Domain

**Tasks**: `cartpole`, `pendulum`, `acrobot` (implemented); `mountain_car`, `lunar_lander` (planned) — Gymnasium classic control + Box2D

**Key Experiments**
```bash
# RL benchmark across algorithms
comp lab benchmark --domain rl --quick
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

---

## 🌐 Distributed Training & P2P

### Multi-GPU Training

PyTorch Lightning with DDP, FSDP, DeepSpeed. `TileShardedBackend` with NCCL `all_reduce_gradients`/`broadcast_params` supports distributed TileNet sharding for large models.

### P2P Coordinator System (gRPC + Kademlia)

Decentralized coordination at `computronium/p2p/`:
- 🔑 **Kademlia DHT** (`dht.py`): Peer discovery, KV storage, bootstrap nodes, async background operation. Integration test: 2-node connectivity + best-model propagation with score-based optimistic locking
- 🔗 **gRPC Service** (`proto/tile_mesh.proto`, `grpc_service.py`): `TileMeshService` with `ExecuteStep`, `BroadcastParams`, `AggregateGradients`
- 🏊 **Connection Pool** (`GRPCConnectionPool`): Peer lifecycle, health checks, retry/backoff
- 🔀 **DistributedSystemTrainer**: In-process multi-worker coordination; shards along TileGeometry, federates at ParameterUpdate
- 🛡️ **Fault Tolerance**: `DistributedTrainingError` captures lost workers, step, partial metrics on gRPC failure

P2P workers run as modules (`computronium/p2p/grpc_worker.py`, `p2p_worker.py` — the P2P layer is algorithm-agnostic).

```bash
# Start a gRPC TileMesh worker
uv run python -m computronium.p2p.grpc_worker --node-id worker_0 --port 50051 --device cpu
```

---

## 🚀 Deployment & Inference

### Model Export (`computronium/deployment.py`)

- 📦 **ONNX**: dynamic axes, opset 17+, TileNet deployment models export with 0 diff vs PyTorch
- 🔗 **TorchScript**: trace method works for all TileNet models
- 🔢 **INT8 Quantization**: dynamic PTQ, static PTQ, QAT preparation
- ⚖️ **Ternary Quantization**: Post-training conversion to `TernaryLinear` ({-1, 0, +1}), STE-based, bit-operation counting
- 🔬 **HLS/Verilog/NxSDK/SPICE**: FPGA/neuromorphic export via `acceleration/export.py`

### Inference Engine

`InferenceServer` — async inference service:
- 📦 Dynamic batching (configurable max batch size/timeout)
- ⚡ TensorRT optimization (fp16/int8, dynamic shapes)
- 🌐 FastAPI endpoints: `/predict` (async batched), `/predict/sync`, `/health`, `/metrics`
- 🔄 Graceful startup/shutdown via lifespan events

---

## 📊 Analysis & Visualization (`computronium/analysis/`)

| Module | Purpose |
|--------|---------|
| `dynamics.py` | Energy trajectories, gradient alignment, tile heatmaps, convergence — interactive Plotly |
| `scaling.py` | Power-law fitting, Chinchilla laws, `ScalingLawFitter`, bootstrap CIs, extrapolation |
| `pareto.py` | Multi-objective Pareto frontier (accuracy, FLOPs, memory, energy, time), knee detection, 3D Plotly |
| `ablation.py` | Leave-one-out, Sobol sensitivity indices, automated HTML/Markdown/JSON/CSV reports |
| `genealogy.py` | Hyperparameter fingerprinting, PCA/t-SNE/UMAP, phylogenetic trees, algorithm maps |
| `interpretability.py` | Weight spectra (SVD, condition number, effective rank), receptive fields, MI, concept alignment, causal mediation |
| `energy_landscape.py` | 2D loss/energy slices (gradient-random, PCA, top-eigen), Hessian spectrum (Lanczos), 3D viz, minima detection |
| `failure_manifesto.py` | Structured negative result docs: what failed, why, search space, partial successes, future hypotheses |
| `tile_dynamics.py` | Tile settling trajectories, utilization, routing patterns |
| `tile_profiler.py` | Per-tile compute/memory profiling |

---

## ⚡ Hardware Acceleration (`computronium/acceleration/`)

| Module | Purpose |
|--------|---------|
| `kernels.py` | Pure NumPy/CuPy reference for correctness |
| `triton_kernels.py` | Triton JIT fused ops for EqProp/MEP |
| `fa_kernels.py` | Fused feedback projection, activation derivative, batched outer product |
| `pc_kernels.py` | Fused prediction, error update, contrastive update (Predictive Coding) |
| `hebbian_kernels.py` | Hebbian/Oja's rule, 3-factor, contrastive Hebbian |
| `snn_kernels.py` | LIF step, STDP, contrastive STDP |
| `ff_kernels.py` | Goodness threshold, contrastive FF/PEPITA updates |
| `tp_kernels.py` | Target propagation inverse + target computation |
| `tile_kernels.py` | Complete TileNet suite: 6 algorithms activity/weight update, routing (top-k/random/learned), multi-GPU NCCL sharding |
| `mep_kernels.py` | Muon orthogonalization, Dion SVD, Fisher whitening, EP settle |
| `backprop_kernels.py` | Fused BPTT baseline |
| `contrastive_kernels.py` | Memory-efficient contrastive primitives (no stored activations; 10 algorithm families) |
| `backends.py` | Auto-dispatch (TRITON > CUDA > CuPy > CPU > NumPy), `AutoDispatcher`, `KernelProfiler` |
| `compile.py` | `torch.compile` integration: custom `EqPropFunction`/`EqPropTritonFunction` autograd, dynamic shapes, compile presets |
| `kernel_backend.py` | `KernelRegistry` with shape-specific auto-tuning cache |

- ⚡ Triton kernels for all tile algorithms + MEP + FA + PC + Hebbian + SNN + FF + TP
- 🔄 Auto-dispatch with profile-guided backend selection
- 🚀 Custom EqProp autograd Function enabling `torch.compile` on settle loops (2–3× speedup)
- 🌐 Multi-GPU tile sharding support for large TileNet models
- ✅ Gradient equivalence CI gate (Triton vs CuPy vs PyTorch on every commit)

---

## 🧭 CEEC Epistemic Operating System (`computronium/ceec/`)

Governs research claims via the CEEC-Core chain (TODO19 Epistemic Foundry):
`Experiment → Artifact → Evidence → Derived → Belief → Gated Status → Decision`.

| Module | Purpose |
|--------|---------|
| `store.py` | Append-only SQLite ledger; content-addressed artifacts; DB-trigger immutability |
| `gates.py` | Promotion/boundary gate engine, quarantine propagation, effective-status resolution |
| `selection.py` | EV/cost experiment selection with pre-scoring hard-constraint filter and audited decisions |
| `calibration.py` | Brier/log-score calibration tracker and report |
| `audit.py` | Ledger integrity audit (evidence-less beliefs, ungated promotions, …) |
| `bootstrap.py` | Seeds instruments, hypotheses, goals, pre-registered experiments from `configs/ceec/` |
| `cli.py` | `uv run python -m computronium.ceec.cli init\|bootstrap\|decide\|audit\|calibration-report\|export` |

Ledger lives at `ceec/ceec.sqlite3`; policies in `docs/ceec/`.

---

## 📜 License

MIT
