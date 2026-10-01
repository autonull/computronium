# 🌌 Computronium: A Composable Laboratory for Learning Mechanisms

**Computronium** is a composable ML library and an experiment kernel for studying how learning mechanisms interact with dynamics, writable state, communication, precision, and resource constraints. Its six-axis interface makes controlled comparisons mechanical; the kernel turns questions into measured, governed evidence.

The name ([Wikipedia](https://en.wikipedia.org/wiki/Computronium)) refers to the theoretical limit of physical computation — the framework bridges abstract learning algorithms and physical constraint models (optical, memristive, neuromorphic, biological, quantum).

## Contents

1. [What is Computronium](#1-what-is-computronium)
2. [Install](#2-install)
3. [60-second quickstart](#3-60-second-quickstart)
4. [The 6-axis ontology](#4-the-6-axis-ontology)
5. [The Experiment Kernel](#5-the-experiment-kernel)
6. [CLI reference](#6-cli-reference)
7. [Demonstrations](#7-demonstrations)
8. [Evidence & claims](#8-evidence--claims)
9. [For developers](#9-for-developers)
10. [Research program](#10-research-program)
11. [FAQ / Troubleshooting + Glossary](#11-faq--troubleshooting--glossary)

---

## 1. What is Computronium

Computronium ships three layers, each usable independently:

| Layer | What it is | What you get |
|---|---|---|
| **ML Library** (`computronium` core) | Composable 6-axis learning systems behind one training API | Train and compare Backprop, EqProp, FA, FF, PEPITA, Target Prop, Predictive Coding, Hebbian/STDP, SNN, TileNet, and 6-D joint variants under a single `SystemTrainer` interface |
| **Experiment Kernel** (`computronium.experiment`) | Question → RunSpec → policy → pipeline → evidence store → claims | Reproducible, resumable, policy-interchangeable experiments with a single DuckDB evidence store and fail-closed schema versioning |
| **Scientific Program** (hypotheses + governance) | Motivating hypotheses on locality, plasticity, stability, and physical constraints; CEEC epistemic governance | Ongoing empirical investigation — claims below are labeled by verification level, never asserted beyond their evidence |

**Claim-strength discipline.** Every claim in this README is labeled by its verification level: (1) analytical, (2) machine-checked, (3) certified numerical, (4) sampled numerical, (5) empirical. Levels are defined in `computronium.verification` and enforced against banned overclaim phrases. The motivating hypothesis — that learning systems native to physical constraints (asynchrony, locality, limited precision, energy budgets) offer measurable benefits — is an *agenda*, not a result.

---

## 2. Install

```bash
git clone <repository-url> && cd computronium
uv sync --dev --all-extras
```

Requirements: Python 3.14+, [uv](https://docs.astral.sh/uv/). GPU (CUDA/Triton) is optional — the CPU path is fully functional.

Dev-environment smoke (run this before any gate; a stripped env fails here in seconds):

```bash
uv run python -c "import optuna, scipy, torchvision, pytest"
```

---

## 3. 60-second quickstart

Compose a 6-axis system and train it on MNIST. This block is locked verbatim against its source demo test ([`tests/integration/test_demo_compose_6axis.py`](tests/integration/test_demo_compose_6axis.py)):

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

Expected result (Level 4 — sampled numerical): one CPU epoch reaches ≈ 0.9 train accuracy (chance 0.1).

---

## 4. The 6-axis ontology

```text
System = Substrate × Geometry × StateDynamics × Plasticity × CreditAssignment × ParameterUpdate
```

A system is a 6-axis coordinate; 5-D systems are the `P = NullPlasticity` subspace. `SystemConfig.validate()` whitelists compatible combinations — the compatible region is the kernel's search space. The ontology is a design abstraction, not an established law.

| Axis | Symbol | Role | Primitives |
|------|:------:|------|------------|
| **Substrate** | $S$ | Physical state space: precision, noise, sparsity | `Digital`, `Memristive` (conductance, IR-drop), `Neuromorphic` (async spikes), `Photonic` (phase/amplitude), `Quantum` (unitary gates), `Noisy`, `Complex`, `Sparse`, `Ternary` |
| **Geometry** | $G$ | Topology & routing | `FeedforwardDAG` (MLP/CNN), `RecurrentAttractor` (Hopfield/EqProp), `TileMesh` (TileNet), `FabricPC` (node-edge), `SpatialLattice3D`, `NTM` (external-memory tape), `NCA` (neural cellular automaton) |
| **StateDynamics** | $D$ | Forward evolution & settling | `EnergyMinimization` (EqProp), `PredictiveSettling` (Predictive Coding), `SpikeIntegration` (LIF/Izhikevich), `InstantaneousPass` (FF/Backprop), `LazyStateDynamics`, `Diffusion` |
| **Plasticity** | $P$ | MetaDynamics: the rule as a writable variable (ψ) | `NullPlasticity`, `RoutingPlasticity`, `FastWeightPlasticity`, `SubstrateCoupledPlasticity`, `RuleStatePlasticity` (Z3), `ClosedFormRidgePlasticity`, `TemporalPsiPlasticity` |
| **CreditAssignment** | $C$ | Error routing & pseudo-gradient | `ThermodynamicContrast` (EqProp), `RandomProjectionsCredit` (FA/DFA), `LocalGoodnessCredit` (FF/PEPITA), `TemporalTraceCredit` (STDP), `TargetInversionCredit`, `HomeostaticCredit` |
| **ParameterUpdate** | $U$ | Slow parameter consolidation Δθ | `EuclideanUpdate` (SGD/Adam), `RiemannianOrthogonalUpdate` (Muon), `SpectralConstrainedUpdate`, `NaturalGradientUpdate` (Fisher), `ElasticConsolidationUpdate` (EWC) |

**Substrate specs.** A substrate is a structured `SubstrateSpec` (execution model, device model, numeric representation, noise, constraints, cost) — not a string tag. Specs compose: "noisy, sparse, complex-valued" is one spec with three facets (`computronium/ontology/substrate/spec.py`, factory `make_substrate`).

**Identity cards.** Every Credit, Update, and Plasticity primitive carries an `AlgorithmIdentityCard` class attribute: reference equation, deviations from the literature, pseudo-gradient definition, validated limits, verification level. Rendered cards: [`docs/IDENTITY_CARDS.md`](docs/IDENTITY_CARDS.md); the strict generator (`scripts/generate_identity_cards.py --strict`) runs in pre-commit.

### One trainer, every credit rule

The same coordinate trained through byte-identical wiring with a single swapped constructor argument — locked verbatim against [`tests/integration/test_demo_swap_credit.py`](tests/integration/test_demo_swap_credit.py); all three arms learn:

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

**Research-direction models.** Formerly hardcoded families (holomorphic/directed/finite-nudge/ternary/momentum/sparse/diffusion EqProp) are coordinates in this space, available via `computronium.models.native`. They are framework-native expressions, not claims of novel algorithms.

---

## 5. The Experiment Kernel

`computronium.experiment` turns a question into governed evidence:

```text
Question ──► RunSpec ──► SearchSpace ──► ProposalPolicy ──► Stages S1–S11 ──► RecordStore ──► Claims
```

- **`schema/`** — `RunSpec`, `Coordinate`, `Schedule`, and the `AXES` / `OBJECTIVES` / `PRIORS` registries (single source of truth for every axis primitive, objective, and prior).
- **`legality/`** — an expression DSL + engine; measurements are only legal where the spec says they are, identically for every policy.
- **`execution/`** — `SearchSpace`, the policy catalog, `PipelineRunner` (stages S1–S11), and `ContrastDesign` (OFAT/factorial DOE with `DataOrigin` provenance).
- **`evidence/`** — `RecordStore` (DuckDB, single-writer under a threading lock), artifacts, failure linkage, three-tier claim status, fail-closed schema versioning with a forward-tolerant `unknown` column.
- **`learning/`** — surrogates, priors, ICU model, reasoning over accumulated evidence.
- **`surface/`** — the `report`/`export`/`conformance`/`status` CLI, run profiles, conformance audit.

**Policy catalog.** Experiments differ only in proposal policy; space, measurement identity, legality, store, and claims machinery are shared:

| Policy | Key | Behavior |
|---|---|---|
| Synthesis | `synthesis` | Question-first entry: resolves coordinate/objective from a natural question (U1) |
| StratifiedRandom | `stratified_random` | Coverage-biased random proposal over the space |
| RoundRobinGrid | `round_robin_grid` | Systematic grid sweep |
| UniformRandom | `uniform_random` | Plain uniform sampling |
| ModelBased (TPE/NSGA-II) | `model_based` | Surrogate-guided search (Optuna TPE, NSGA-II for multi-objective) |
| Evolution | `evolution` | Population-based refinement |
| StrategyProgression | `strategy_progression` | Progresses proposal strategies across rounds |
| TrainerDriven | `trainer_driven` | Defers proposals to the trainer driver |

**Kernel guarantees (locked in [`tests/acceptance/test_unified_kernel.py`](tests/acceptance/test_unified_kernel.py)):**

| ID | Guarantee |
|---|---|
| U1 | Question → `question_first()` → RunSpec → Synthesis → pipeline → store: end-to-end |
| U2 | Same RunSpec under TPE (`ModelBasedPolicy`) → identical record schema/store |
| U3 | Multi-round allocation with pause/resume by `run_id` — no re-measurement |
| U4 | Policy interchangeability: swap policy per round, same RunSpec/Space/Store |
| U5 | Cross-policy evidence reuse: one store, no migration, same legality/claims |

**Measurement identity & provenance.** Every record carries a deterministic `measurement_key` (from coordinate + schedule), full provenance (code SHA, dataset, policy), a three-tier status (gate verdict / defect cause / maturity), and a schema version. Unsupported schema versions fail closed (`UnsupportedSchemaVersionError`); fields the current schema does not model survive bumps verbatim in the `unknown` column.

**ContrastDesign.** WP18 adds design-of-experiments (OFAT/factorial) with explicit `DataOrigin` labels, so contrasted arms carry known structure rather than incidental variation.

---

## 6. CLI reference

`comp <command>` — every subcommand either works end-to-end or does not exist in the dispatcher:

| Command | Purpose |
|---|---|
| `report` | Kernel surface CLI: run/report/export/conformance/status on the evidence store |
| `parity` | Kernel-vs-PyTorch accuracy parity benchmark |
| `repro` | Library reproducibility checks |
| `validate` | Library verification suite |
| `joint-validate` | 6-axis joint-architecture validation |
| `benchmark` | ML library benchmark suite (5-level hierarchy) |

This table is locked against the dispatcher by `tests/property/test_cli_readme_lock.py` — set and purpose lines must match exactly.

Kernel operations via `comp report`:

```bash
uv run comp report --help            # report/export/conformance/status subcommands
uv run comp report run --profile default --store experiment.duckdb
uv run comp report status --store experiment.duckdb
```

---

## 7. Demonstrations

Programmatic demos built on the same kernel APIs as the acceptance suite live in `scripts/demos/`:

| Demo | Shows |
|---|---|
| `demo_unified_pipeline.py` | U1 end-to-end: question → RunSpec → Synthesis → pipeline → store → report |
| `demo_policy_swap.py` | U4: four policies, same RunSpec/Space/Store, identical schema |
| `demo_pause_resume.py` | U3: pause + resume by `run_id`, no re-measurement, monotonic seq |
| `demo_multi_objective.py` | Pareto over accuracy/walltime/params via the OBJECTIVES registry |
| `demo_cross_policy_reuse.py` | U5: evidence reuse across policies, one store |
| `demo_contrast_design.py` | WP18: OFAT/factorial DOE + DataOrigin, known effect recovered |

---

## 8. Evidence & claims

Claims are labeled by verification level (§1) and governed by CEEC ([`packages/ceec-core`](packages/ceec-core)).

| Claim | Level | Evidence |
|---|---|---|
| Seeded axis effect (E3): credit-axis manipulation shifts outcomes, d ≈ −1.5, p < 0.01 | 5 | `scripts/probes/e3_seeded_axis_effect.py`, conformance audit |
| Transfer provenance (E4): provenance-tagged records support transfer, d ≈ −1.52 | 5 | `scripts/probes/e4_transfer_provenance.py` |
| Effect-size protocol (E2) | 5 | conformance evidence audit (46 pass / 42 skip / 0 fail) |
| Kernel guarantees U1–U5 | 4 | `tests/acceptance/test_unified_kernel.py` |
| Locked demo blocks (§3, §4) | 4 | `tests/integration/test_demo_compose_6axis.py`, `test_demo_swap_credit.py` |
| Conformance audit C1–C88 | 2–3 | `comp report conformance` |

The effect-size protocol: seeded, paired comparisons with preregistered objectives from the PRIORS registry; only Level-4/5 measurements may enter Class E claims, and they are reported at measured strength.

---

## 9. For developers

**Layout** — see the tree at the top of [`AGENTS.md`](AGENTS.md): `computronium/` (library + `experiment/` kernel), `packages/` (standalone platforms), `scripts/` (quickstart, identity cards, probes, demos), `tests/` (property / acceptance / integration / unit / platform / ceec).

**Toolchain** — uv (single `uv.lock`), ruff (format always; lint changed files), pyright (strict on new modules), pre-commit, pytest. Config lives in `pyproject.toml`.

**Testing tiers** — run the cheapest tier that can catch your change:

```bash
uv run python -m pytest tests/<path> -k <signature> -q      # targeted (default)
uv run python -m pytest tests/integration/ -k "demo or gallery_lock" -q   # fast gate
uv run python -m pytest                                     # round close only
```

**Kernel locks** — these tests must stay green and are never bypassed:

```bash
uv run python -m pytest tests/property/test_kernel_isolation_lock.py \
    tests/property/test_full_import_isolation_lock.py \
    tests/property/test_schema_forward_tolerance.py \
    tests/property/test_single_writer_enforcement.py \
    tests/property/test_cli_readme_lock.py \
    tests/property/test_atomic_append_kill_proof.py -q
```

**Commit checklist** (per commit, scoped): dev-env smoke → `ruff format` + `ruff check --fix` on changed files → `pyright` on changed files → targeted tests. Full suite, repo-wide lint/type, and `pip-audit` are round-close work only.

**Adding an ontology primitive** — follow the checklist in [`AGENTS.md`](AGENTS.md) (registry row, config classmethod, wiring lockstep lock, export surfaces, contract invariants). **Adding a kernel policy** — subclass the `Policy` protocol in `computronium/experiment/execution/policy.py` and register it in `POLICY_CATALOG`; the interchangeability guarantees then apply for free.

---

## 10. Research program

The motivating hypothesis: learning systems native to physical constraints — asynchronous operation, local interactions, adaptation, noise tolerance, energy/resource efficiency — offer measurable benefits over global-clock, backprop-centric training under those constraints.

Open questions: when does the plasticity axis (writable ψ on frozen θ) beat standard recurrent memory; how far do local credit rules scale on digital substrates; which substrate constraints actually bind. Historical campaign records and research notes live in git history; methodology and Z3 material in `docs/reference/`.

---

## 11. FAQ / Troubleshooting + Glossary

**FAQ**

- *`ModuleNotFoundError` after a sync* — run `uv sync --dev --all-extras` (bare `uv sync` strips dev extras) and the dev-env smoke command.
- *DuckDB store is locked* — the evidence store is **single-writer**: all writes flow through `RecordStore.append()` under a threading lock, enforced by `tests/property/test_single_writer_enforcement.py`. Do not open a second writer process against the same file; readers are fine, cross-process writers are not supported.
- *`UnsupportedSchemaVersionError`* — a record was written by a newer kernel than the reader. Upgrade the reader; unknown-field tolerance is fail-closed by design.
- *GPU* — optional. `uv run comp benchmark` runs on CPU.

**Glossary**

- **Coordinate** — a point in the 6-axis space; the unit of comparison.
- **RunSpec** — the serialized specification of a run: question, space, stages, budget.
- **SearchSpace** — the legality-checked subspace a policy proposes within.
- **Policy** — the proposal strategy; the only varying part between kernel experiments.
- **Stage** — one step S1–S11 of the pipeline.
- **Record** — one measured row in the evidence store (identity, provenance, status, payload).
- **Claim** — a governed statement derived from records, with a verification level.

---

## License

See [`LICENSE`](LICENSE).
