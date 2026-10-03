# TODO49: Minimal High-Signal End-to-End Validation Procedure

## Purpose
Expose failures that **only emerge from interaction, wiring, state, lifecycle, configuration, or real execution across subsystem boundaries** — not local correctness (covered by unit tests).

Each iteration tests the **smallest meaningful end-to-end slice**, produces a concrete pass/fail signal, and enables immediate correction. No redundant tests, no unnecessary scale, no repeated setup.

## Critical Path First, Breadth Second

**Principle**: Validate the *entire critical path* (config → construct → execute → train → measure → persist → replay) on the **simplest possible task** before expanding to real datasets or component breadth.

| Phase | Task | Why |
|-------|------|-----|
| **Critical Path** | Synthetic 2D linearly separable (4 samples, 2 features, 2 classes) | Fastest possible feedback; exposes wiring/config/execution bugs without data complexity |
| **Sanity** | Digits (sklearn `load_digits`, 1797 samples, 64 features, 10 classes) | Real-ish data, still tiny, verifies input reshaping, batching, multi-class |
| **Breadth** | Domain presets (vision/LM/graph/RL) | Only after critical path + sanity pass |

**All iterations below use the synthetic task unless explicitly noted.** This keeps each iteration ≤30s.

---

## What's ALREADY COVERED (Do Not Duplicate)

| Existing Test | Covers | Status |
|---------------|--------|--------|
| `test_validation_all.py` | All native models (backprop, eqprop, fa, lemma, tile_ep/fa/tp/hebbian) train 5 epochs on synthetic (20 samples), loss decreases | ✅ Complete |
| `test_trainer_resume.py` | Bitwise-identical resume for JointSystem (recurrent, energy_minimization, backprop) | ✅ Complete |
| `test_lazy_dynamics.py` | LazyStateDynamics registry round-trip, settle monotonicity, end-to-end MNIST | ✅ Complete |
| `test_pt2_export_roundtrip.py` | PT2 export/load for FeedforwardGeometry & RecurrentGeometry | ✅ Complete |
| `test_ceec_store.py` (ceec-core) | Artifact hash stability, append-only, duplicate rejection | ✅ Complete (but different store) |
| `test_smoke_all_tasks.py` | Domain task creation + 1 epoch training (vision/LM/RL) | ✅ Complete |
| `test_quickstart.py` | Backprop vs EqProp on MNIST (slow, gpu) | ✅ Complete |
| `test_gallery_lock.py` | Figure lock: data checksums match manifest | ✅ Complete |
| `test_wheel_acceptance.py` | Wheel install + smoke in clean venv | ✅ Complete |
| `test_demo_*.py` | Demo runs producing gallery records | ✅ Complete |

---

## Iteration 0: Environment & Fixture Sanity (30s)

**Hypothesis**: The dev environment, fixtures, and deterministic seeds are functional.

| Step | Command | Success Signal |
|------|---------|----------------|
| 0.1 | `uv run python -c "import optuna, scipy, torchvision, pytest"` | Imports succeed |
| 0.2 | `uv run python -c "from computronium import compose_system; print('import ok')"` | Core import works |
| 0.3 | `uv run python -m pytest tests/integration/test_quickstart.py -q --tb=line -x` | Quickstart integration passes |

**On failure**: Fix env / deps / broken import. Do not proceed.

---

## Synthetic Task Fixture (Shared by Iterations 1–5, 7, 9–10)

```python
# tests/conftest.py or inline in each test
import torch
from torch.utils.data import DataLoader, TensorDataset

def synthetic_task(batch_size=4, seed=42):
    """Linearly separable 2D: 4 samples, 2 features, 2 classes.
    Class 0: x1 + x2 < 0  |  Class 1: x1 + x2 >= 0
    """
    torch.manual_seed(seed)
    x = torch.randn(4, 2)
    y = (x.sum(dim=1) >= 0).long()  # Perfectly separable
    return DataLoader(TensorDataset(x, y), batch_size=batch_size, shuffle=True)
```

---

## Iteration 1: SystemConfig Cross-Axis Validation & Factory Round-Trip (10s)

**Hypothesis**: `SystemConfig.validate()` enforces cross-axis constraints; `compose_system_from_configs` round-trips via `extract_config`. **NOT covered by existing tests** (they use factories directly, not config validation).

| Slice | Test | Success Signal |
|-------|------|----------------|
| 1.1 Valid coordinate | `SystemConfig(digital, ff, instantaneous, gradient, euclidean).validate()` | No exception |
| 1.2 Invalid coordinate | `SystemConfig(recurrent, spike_integration, gradient).validate()` | `ValueError` raised |
| 1.3 Round-trip | `system = compose_system_from_configs(...); cfg = extract_config(system); system2 = compose_system_from_configs(**cfg)` | `system.to_spec() == system2.to_spec()` |

**Command**:
```bash
uv run python -m pytest tests/integration/test_lazy_dynamics.py::test_lazy_registry_round_trip -q --tb=line
# Add new test for cross-axis validation (see below)
```

**New test needed**: `tests/integration/test_system_config_validation.py` with parametrized valid/invalid combos from `SystemConfig.valid_combinations()`.

**On failure**: Fix the specific validation rule or factory wiring. Re-run only this slice.

---

## Iteration 2: Configuration → Construction → Single Step on Synthetic (15s)

**Hypothesis**: A system composed from **configs** (not factories) executes one `train_step` on synthetic data and returns the canonical metric schema. **NOT covered** (existing tests use `create_native_*` factories directly).

| Slice | Test | Success Signal |
|-------|------|----------------|
| 2.1 5-D from configs | `compose_system_from_configs(digital, ff, instantaneous, gradient, euclidean).train_step(x, y)` | Returns dict with keys `loss, energy, nudged_fit_accuracy, free_loss, free_energy, free_accuracy` |
| 2.2 6-D from configs (null plasticity) | `compose_joint_system_from_configs(..., plasticity=null)` | Behaves identically to 5-D equivalent |
| 2.3 6-D from configs (routing plasticity) | `compose_joint_system_from_configs(..., plasticity=routing).train_step(x, y)` | Metrics include `plasticity_*` keys; `psi` state advances |

**Command**:
```bash
# New test needed: tests/integration/test_config_composed_single_step.py
uv run python -m pytest tests/integration/test_config_composed_single_step.py -q --tb=line
```

**On failure**: Debug `run_train_step` pipeline for that coordinate. Fix settle/credit/update wiring.

---

## Iteration 3: ExperimentConfig → SystemConfig → Trainer on Synthetic (45s)

**Hypothesis**: `ExperimentConfig` preset factories produce valid, trainable systems when wired through `SystemConfig` and `SystemTrainer`. **NOT covered** (existing tests use domain tasks or factories directly, not ExperimentConfig presets).

| Stage | Test | Success Signal |
|-------|------|----------------|
| 3.1 Synthetic (critical path) | `config = ExperimentConfig(model=ModelConfig(input_dim=2, output_dim=2, hidden_dims=(4,), model_type="mlp", ...), system=SystemConfig(...), ...); trainer = SystemTrainer.from_configs(config)` | `trainer.fit()` 2 epochs on synthetic; loss → 0 |
| 3.2 Digits (sanity) | Same config but `input_dim=64, output_dim=10, hidden_dims=(32,)` on `load_digits()` | `trainer.fit()` 2 epochs; `train_loss` decreases |
| 3.3 Vision preset | `make_vision_preset(hidden_dims=(32,), epochs=2)` → override to synthetic data | Runs 2 epochs on synthetic |
| 3.4 LM preset | `make_lm_preset(hidden_dims=(32,), epochs=2)` → override to synthetic data | Runs 2 epochs on synthetic |
| 3.5 Graph preset | `make_graph_preset(hidden_dims=(32,), epochs=2)` → override to synthetic data | Runs 2 epochs on synthetic |
| 3.6 RL preset | `make_rl_preset(hidden_dims=(32,), epochs=2)` → override to synthetic data | Runs 2 epochs on synthetic |

**Command**:
```bash
# New test needed: tests/integration/test_experiment_config_presets.py
uv run python -m pytest tests/integration/test_experiment_config_presets.py -q --tb=line
```

**On failure**: Trace to `SystemConfig.validate()` branch or `to_system_trainer_config` mapping. Fix at the failing stage before proceeding.

---

## Iteration 4: Configuration Persistence & Reproducibility (20s)

**Hypothesis**: `to_spec` / `from_spec` round-trips produce bitwise-identical training dynamics on **synthetic** data. **NOT fully covered** (PT2 export round-trip tested, but not `to_spec`/`from_spec` for 5-D/6-D Systems).

| Slice | Test | Success Signal |
|-------|------|----------------|
| 4.1 5-D spec round-trip | `spec = system.to_spec(); system2 = System.from_spec(spec)` | `system2.to_spec() == spec` |
| 4.2 6-D spec round-trip | Same for `JointSystem` (schema_version 2.0) | Identical spec |
| 4.3 Deterministic replay | Train 3 epochs on synthetic with `seed=42, deterministic=True` → record metrics → repeat | All metric values bitwise identical (including `free_accuracy`) |
| 4.4 Cross-process replay | Subprocess: `python -c "..."` with same seed/config on synthetic | Same metrics as in-process |

**Command**:
```bash
# test_pt2_export_roundtrip covers export; add test for to_spec/from_spec
uv run python -m pytest tests/integration/test_spec_roundtrip.py -q --tb=line
uv run python -m pytest tests/integration/test_deterministic_replay.py -q --tb=line
```

**On failure**: Check `geometry.params` serialization, `SubstrateConfig.device`, RNG state in `SystemTrainer._begin_epoch`.

---

## Iteration 5: RecordStore (New) Atomic Append + Artifacts + Query (25s)

**Hypothesis**: `RecordStore.append_with_artifacts` atomically persists records + artifacts; query filters return identical data. **NOT covered** (ceec-core store tested, but this is the new `computronium.experiment.evidence.store.RecordStore`).

| Slice | Test | Success Signal |
|-------|------|----------------|
| 5.1 Inline artifact | Store record with small config artifact (role=CONFIG) from synthetic run | `artifacts.get(digest)` returns original bytes |
| 5.2 External artifact | Store record with large artifact (>10MB) | `artifacts.get(digest)` returns original bytes from filesystem |
| 5.3 Atomicity | Fail mid-transaction (simulate) → store unchanged | No partial records; `DuplicateMeasurementError` on retry |
| 5.4 Query filters | `query_records(run_id=..., gate_verdict=PASS, fidelity=L2)` | Returns only matching records |
| 5.5 Vector search | `add_embedding` + `vector_search_brute_force` | Returns correct nearest neighbors |

**Command**:
```bash
# New test needed: tests/integration/test_record_store.py
uv run python -m pytest tests/integration/test_record_store.py -q --tb=line
```

**On failure**: Check DuckDB schema, `ArtifactStore.put` size routing, transaction boundaries, vector index.

---

## Iteration 6: CLI `validate` Command & Config Schema (15s)

**Hypothesis**: The `comp validate` CLI command validates config schema. **NOT covered** (wheel acceptance tests `comp run` smoke, not `validate`).

| Slice | Test | Success Signal |
|-------|------|----------------|
| 6.1 `comp validate` valid | `uv run comp validate --config minimal_synthetic.yaml` | Exit 0, no errors |
| 6.2 `comp validate` invalid | `uv run comp validate --config invalid.yaml` | Exit non-zero, validation error printed |

**Command**:
```bash
uv run comp validate --config tests/fixtures/minimal_synthetic.yaml
# Add invalid config fixture and test
```

**On failure**: Fix `computronium/cli/validate.py` schema validation.

---

## Iteration 7: Cross-Axis Composition Matrix (120s)

**Hypothesis**: All valid (credit × dynamics × geometry) combinations from `SystemConfig.valid_combinations()` construct and train on **synthetic** data. **NOT covered** (existing tests cover specific factories, not the full Cartesian product of valid combinations).

| Slice | Test | Success Signal |
|-------|------|----------------|
| 7.1 Enumerate valid combos | `for combo in SystemConfig.valid_combinations(): compose_system_from_configs(**combo)` | All construct without error |
| 7.2 Train 1 epoch each | Subset: backprop/ff, eqprop/recurrent, fa/ff, pepita/ff, tile/ep on synthetic | Each completes 1 epoch; `train_loss` finite |
| 7.3 Invalid combos rejected | Sample invalid combos from Cartesian product | `SystemConfig.validate()` raises `ValueError` |

**Command**:
```bash
# New test needed: tests/integration/test_cross_axis_matrix.py
uv run python -m pytest tests/integration/test_cross_axis_matrix.py -q --tb=line
```

**On failure**: Add missing validation rule or fix factory for that coordinate.

---

## Iteration 8: Verification Suite Quick Mode on Synthetic (60s)

**Hypothesis**: The `Verifier` runs validation tracks in quick mode on **synthetic** tasks and produces a notebook. **NOT covered** (existing tests run demos/integration; Verifier tracks not exercised in CI).

| Slice | Test | Success Signal |
|-------|------|----------------|
| 8.1 Quick verification | `Verifier(quick_mode=True).run_tracks([0])` | Track 0 (Framework Validation) passes |
| 8.2 All tracks smoke | `Verifier(quick_mode=True).run_tracks()` | All tracks complete; `verification_notebook.md` written |

**Command**:
```bash
uv run python -c "
from computronium.validation import Verifier
v = Verifier(quick_mode=True, seed=42)
results = v.run_tracks()
assert all(r.status == 'pass' for r in results.values())
"
```

**On failure**: Debug the specific failing track; usually a missing import or config mismatch.

---

## Execution Protocol

```bash
# Run iterations sequentially; STOP on first failure
for i in {0..8}; do
  echo "=== ITERATION $i ==="
  # Run the iteration's command(s)
  # If any command fails: debug, fix, re-run ONLY that iteration
done
```

### Task Progression (Critical Path First)

| Iterations | Task | Samples | Features | Classes | Purpose |
|------------|------|---------|----------|---------|---------|
| 0 | — | — | — | — | Env sanity |
| 1–4 | **Synthetic 2D** | 4 | 2 | 2 | Critical path: config→train→replay |
| 3.2 | **Digits** | 1797 | 64 | 10 | Sanity: real-ish data, reshaping, multi-class |
| 3.3–3.6 | **Presets (overridden to synthetic)** | 4 | varies | varies | Breadth: all preset factories |
| 5 | **Synthetic** | 4 | 2 | 2 | RecordStore persistence |
| 6 | **Synthetic** | 4 | 2 | 2 | CLI validate |
| 7 | **Synthetic** | 4 | 2 | 2 | Cross-axis matrix |
| 8 | **Synthetic** | 4 | 2 | 2 | Verification suite |

### Failure Handling
1. **Stop immediately** on any failure in the current iteration.
2. **Fix the smallest broken layer** (validation rule, factory, pipeline, config mapping).
3. **Re-run ONLY the failed iteration** until it passes.
4. **Then continue** to the next iteration.

### Reuse & Efficiency
- **Fixtures**: `tests/integration/conftest.py` provides `sample_data`, `device`, `seed`.
- **Deterministic seeds**: All smoke tests use `seed=42`, `deterministic=True`.
- **Minimal scale**: 2-3 epochs, batch_size=4, hidden_dim=16, sample_size=4 (synthetic) / 1797 (digits).
- **Parallelism**: `-n 4` (already in `addopts`) for independent slices.

---

## Coverage Map (Critical Path — Only New Coverage)

| Subsystem Boundary | Iteration(s) |
|--------------------|--------------|
| Config validation ↔ Factory wiring | 1, 7 |
| Configs → Factory → Pipeline (`run_train_step`) | 2 |
| ExperimentConfig → SystemConfig → Trainer | 3 |
| System ↔ Spec serialization (to_spec/from_spec) | 4 |
| Record ↔ Artifact store (new RecordStore) | 5 |
| CLI validate ↔ Config schema | 6 |
| Cross-axis matrix ↔ Valid combinations | 7 |
| Verification tracks ↔ Notebook | 8 |

---

## What This Does NOT Cover (Intentional — Already Covered Elsewhere)

- **Unit-level correctness** (thousands of existing tests)
- **Native model training** (`test_validation_all.py`)
- **Trainer resume** (`test_trainer_resume.py`)
- **LazyStateDynamics** (`test_lazy_dynamics.py`)
- **PT2 export round-trip** (`test_pt2_export_roundtrip.py`)
- **CEEC store** (`test_ceec_store.py` in ceec-core)
- **Domain task smoke** (`test_smoke_all_tasks.py`)
- **MNIST full training** (`test_quickstart.py`)
- **Gallery figure lock** (`test_gallery_lock.py`)
- **Wheel acceptance** (`test_wheel_acceptance.py`)
- **Full training convergence** (expensive; smoke-scale only)
- **GPU/CUDA paths** (CI runs CPU; GPU is separate gate)
- **Distributed training** (separate validation)
- **Performance benchmarks** (separate `benchmark` marker)
- **LLM / vision / RL full tasks** (domain presets tested at smoke scale only)

---

## Success Criteria for TODO49 Completion

All 9 iterations (0–8) pass consecutively without manual intervention. The final `Verifier(quick_mode=True).run_tracks()` produces a notebook with all tracks `status == "pass"`.

---

## New Test Files Needed (One per Iteration)

| Iteration | Test File | Purpose |
|-----------|-----------|---------|
| 1 | `tests/integration/test_system_config_validation.py` | Cross-axis validation + config round-trip |
| 2 | `tests/integration/test_config_composed_single_step.py` | Config-composed systems execute train_step |
| 3 | `tests/integration/test_experiment_config_presets.py` | ExperimentConfig presets → trainer on synthetic/digits |
| 4 | `tests/integration/test_spec_roundtrip.py` | to_spec/from_spec bitwise identical |
| 4 | `tests/integration/test_deterministic_replay.py` | Cross-process deterministic replay |
| 5 | `tests/integration/test_record_store.py` | RecordStore atomic append, artifacts, queries, vector search |
| 6 | `tests/integration/test_cli_validate.py` | CLI validate command |
| 7 | `tests/integration/test_cross_axis_matrix.py` | Full valid_combinations() enumeration + train |
| 8 | (uses existing `Verifier` class) | Verification suite quick mode |