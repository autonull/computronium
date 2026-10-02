---

## 🏗️ Core Architecture

### 1. Ontology Protocols (`computronium/ontology/`)

<details>
<summary><strong>Protocol details</strong> ⋯</summary>

Five `Protocol` classes with PEP 695 generics, frozen slotted config dataclasses, and reference implementations for every primitive — pure, composable infrastructure. See `computronium/ontology/` for the full Protocol definitions.
</details>

- `Substrate` — `forward_operator`, `weight_update_operator`
- `Geometry` — `forward`, `route`
- `StateDynamics` — `settle`
- `CreditAssignment` — `compute_pseudo_gradient`, `surrogate_objective`
- `ParameterUpdate` — `step`

### 2. Joint Architecture Protocols (`computronium/core/joint/`)

<details>
<summary><strong>Joint protocol details</strong> ⋯</summary>

The joint dynamical system elevates the computational rule to a dynamical variable via the **CoupledTransition** protocol operating on `CompositeState`. Key types defined in `computronium/core/joint/state.py` and `computronium/core/joint/transition.py`.
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