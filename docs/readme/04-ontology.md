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
