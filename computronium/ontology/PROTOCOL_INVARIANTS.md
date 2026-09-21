# StateDynamics Protocol Invariants

This document specifies the canonical contract for all `StateDynamics` implementations.
Every implementation **must** satisfy these invariants to be compatible with the
computronium ontology's composition engine, credit assignment, and training pipeline.

---

## 1. Activation Layout

**Invariant**: Layered states are `[input, hidden1, ..., hiddenN, output]`

- Element `0` is the input tensor (flattened to 2-D: `[batch, features]`)
- Element `-1` is the network output (logits/pre-activations)
- Intermediate elements `1:-1` are hidden layer activations
- All layers share the same batch dimension
- Consumers that depend on this layout:
  - `_state_energy_vector` (reads output energy from element `-1`)
  - `SubstrateSettleKernel.step` (1:1 alignment with `extract_layered_params` transitions)
  - CreditAssignment's per-layer correlation walks

---

## 2. Phase Loop and Energy Timing

**Invariant**: `settle` runs the free phase when `target is None` and the nudged phase otherwise.
`compute_energy` is called by the pipeline **after** `settle` returns, reading the settled state — never mid-settle.

| Phase | `target` | State Field Written | Energy Semantics |
|-------|----------|---------------------|------------------|
| Free | `None` | `free_state` + `activations` | Free energy (Lyapunov function) |
| Nudged | `Tensor` | `nudged_state` + `activations` | Nudged energy (free energy + β·nudge) |

**Critical**: Callers must sequence as:
```python
settled = dynamics.settle(state, geometry, substrate, target)
energy = dynamics.compute_energy(settled, geometry)  # AFTER settle
```

---

## 3. Autograd Context

**Invariant**: `settle` runs under the caller's `no_grad` by default.

Implementations needing internal differentiation (ePC error gradients, diffusion Langevin steps, PC-ALM primal-dual updates) **must**:
- Open `with torch.enable_grad():` around the reverse/gradient sweep
- Detach tensors before returning them to the caller
- Use out-of-place tensor adds (`a + b`) rather than in-place (`a += b`) on state tensors

The gradient-safety idiom:
```python
# BAD: in-place on state tensors breaks graph
acts[i] += delta

# GOOD: out-of-place preserves graph
acts[i] = acts[i] + delta
```

---

## 4. Input Flattening

**Invariant**: Implementations flatten non-2-D inputs themselves:
```python
x = x.flatten(1) if x.dim() > 2 else x
```
Geometry may hand over raw image-shaped inputs (`[B, C, H, W]`). The dynamics owns flattening.

---

## 5. Free/Nudged Target Semantics

**Invariant**:
- `target is None` → write settled activations to `free_state`
- `target` provided → nudge toward it (`beta * (one_hot - out)` at output layer) and write to `nudged_state`
- **Both phases** populate `activations` with the final settled activations
- Metrics schema: imp-46

```python
# Free phase
state = dynamics.settle(state, geometry, substrate, target=None)
assert state.free_state is not None
assert state.nudged_state is None
assert state.activations is state.free_state

# Nudged phase
state = dynamics.settle(state, geometry, substrate, target=target)
assert state.nudged_state is not None
assert state.free_state is None  # not overwritten
assert state.activations is state.nudged_state
```

---

## 6. Mutation Contract

**Invariant**: `settle` **always returns the state to use** — implementations may rebuild rather than mutate.

Callers **must** bind and use the returned state:
```python
# CORRECT
settled = dynamics.settle(state, geometry, substrate, target)
acts = settled.activations  # Use returned state

# INCORRECT - reads pre-settle activations
dynamics.settle(state, geometry, substrate, target)
acts = state.activations  # STALE!
```

This contract is enforced by the AST census lock:
`tests/property/test_settle_caller_census.py`

---

## 7. `on_step` Callback

**Invariant**: If `on_step: Callable[[int, float], None]` is provided, it is invoked at each settle step with `(step_index, current_energy)`.

Used for live telemetry and convergence monitoring. Implementations should call it after computing the step's energy (if tracking energy) or after the step completes.

---

## 8. Convergence and Early Stopping

**Invariant**: Implementations should respect `config.convergence_threshold` and `config.convergence_start` for early stopping, but **must** honor `config.max_steps` as a hard ceiling.

The protocol does not mandate a specific convergence criterion (inf-norm, relative p-norm, energy delta), but the implementation's `_settle_steps_used` should reflect actual steps taken.

---

## 9. `compute_energy` Contract

**Invariant**: Returns a **scalar tensor** (`ndim == 0`) representing the energy of the current state.

For energy-based dynamics (EqProp, Hopfield, PC): returns the Lyapunov function value.
For non-energy dynamics: returns a proxy (e.g., mean squared activity).

Priority order for state source:
1. `state.free_state` (if available)
2. `state.nudged_state` (if available)
3. `state.activations` (fallback)
4. Returns `tensor(0.0)` if none available

---

## 10. Implementation Registry

All implementations are registered in `DYNAMICS_REGISTRY` and instantiated via `StateDynamicsConfig.<primitive>()`:

| Dynamics Type | Config Classmethod | Dynamics Class |
|---------------|-------------------|----------------|
| Energy Minimization | `energy_minimization()` | `EnergyMinimizationDynamics` |
| Predictive Settling | `predictive_settling()` | `PredictiveSettlingDynamics` |
| Error Predictive Coding | `error_predictive_coding()` | `ErrorPredictiveCodingDynamics` |
| Spike Integration | `spike_integration()` | `SpikeIntegrationDynamics` |
| Instantaneous | `instantaneous()` | `InstantaneousDynamics` |
| Diffusion | `diffusion()` | `DiffusionDynamics` |
| Lazy State | `lazy()` | `LazyStateDynamics` |
| PC-ALM | `pc_alm()` | `PCALMDynamics` |

The wiring lock (`tests/property/test_dynamics_wiring_lock.py`) ensures registry ↔ config ↔ exports stay in sync.

---

## 11. Property Tests

The protocol invariants are validated by property tests in:
- `tests/property/test_state_dynamics_protocol.py` — protocol contract tests
- `tests/property/test_settle_caller_census.py` — mutation contract enforcement
- `tests/property/generated/test_primitive_state_dynamics_*_invariants.py` — per-primitive generated tests

Run all protocol tests:
```bash
uv run python -m pytest tests/property/test_state_dynamics_protocol.py -v
uv run python -m pytest tests/property/test_settle_caller_census.py -v
```