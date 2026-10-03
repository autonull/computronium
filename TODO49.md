# TODO49: Minimal High-Signal End-to-End Validation Procedure

## Purpose
Expose failures that **only emerge from interaction, wiring, state, lifecycle, configuration, or real execution across subsystem boundaries** — not local correctness (covered by unit tests).

Each iteration tests the **smallest meaningful end-to-end slice**, produces a concrete pass/fail signal, and enables immediate correction. No redundant tests, no unnecessary scale, no repeated setup.

---

## Device Policy: GPU is the default, not a variant

**Runs on CUDA by default. CPU is the reference, not the target.**

`Schedule.device` and `RunSpec.device` already exist (`cpu` / `cuda` / `auto`) and this plan mentioned `device` exactly once, in a failure hint. That is the wrong shape: a device is a *seam*, and device-dependent divergence is exactly the class this document exists to find.

Three reasons this is not optional:

1. **The expensive hardware is where the untested code lives.** `acceleration/backends.py`
   and `eqprop_kernel_backend.py` both branch on `torch.cuda.is_available()`, and
   `availability.py` gates Triton behind it. A plan that runs CPU-only never
   executes those branches — so a green CPU plan says nothing about them.
2. **Determinism claims differ by device, and only one of them is exact.**
   Iteration 4.3 asserts *bitwise* identical replay. On GPU with TF32 enabled that
   is **false by construction** — reduced-precision matmul reassociates sums. So
   the plan must assert bitwise on CPU and *within tolerance* on GPU, and say so,
   or Iteration 4 becomes a coin flip dressed as a lock. (E4 already recorded the
   same shape of problem: "the evaluator is not seed-deterministic across
   invocations.")
3. **Silent CPU fallback is the failure mode worth catching.** `device="cuda"` on a
   box without CUDA should **fail loudly**, not quietly run on CPU. A test that
   "passes on GPU" while executing on CPU is worse than no test, because it
   retires the question.

**Fixture** (`tests/integration/conftest.py`):

```python
@pytest.fixture(scope="session")
def device() -> str:
    """`cuda` when this box has it, else `cpu` — asserted, never assumed."""
    if not torch.cuda.is_available():
        return "cpu"
    return "cuda"

@pytest.fixture(scope="session")
def gpu_required() -> None:
    """Skip loudly when CUDA is absent; never let a GPU slice run on CPU."""
    if not torch.cuda.is_available():
        pytest.skip("CUDA unavailable: this slice is a GPU claim")
```

**Rules:**
- Every iteration runs on `device`. Slices that assert *bitwise* determinism
  (4.3, 4.4) run on **both** and assert per-device semantics.
- No slice silently accepts a CPU fallback. A GPU claim on a CPU-only box is
  **skipped with a reason**, never passed.
- Iteration 0 gains a CUDA probe (0.4) so "we are on GPU" is a measured fact
  before any slice depends on it.
- `--device cpu` remains a supported full pass for CI, which has no GPU. It is
  reported as a *different, weaker* pass, never as equivalent.

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

**These "✅ Complete" statuses are the plan author's assertions, not verified
facts** — this file has never been executed. Each row is cheap to confirm
(`pytest <file> -q`) and doing so in Iteration 0 is worth it: a row that is
actually red invalidates the *premise* of the iteration meant to fix it, and
that is worth knowing before writing any new test.
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
| 0.4 | `uv run python -c "import torch; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0))"` | GPU present and named |
| 0.5 | Confirm the "already covered" rows | `pytest <each file> -q` for the 10 rows in the coverage table — they are **unverified assertions** in this file |
| 0.6 | **Build `device` / `seed` / `sample_data` / `gpu_required`** in `tests/integration/conftest.py` | They do not exist yet; 0.6 is what makes "reuse" true |
| 0.7 | Price every iteration with `--co -q` + one timed run | Real seconds per iteration, replacing the estimates in the headings |

**0.4 is a fork, not a formality.** On a GPU box, every later slice runs on CUDA
and 0.4 is what makes that legible. On a CPU-only box (CI), 0.4 fails and the
remaining iterations run with `--device cpu` as a *weaker, separately reported*
pass — never as an equivalent one.

**0.5–0.7 are cheap and they are the difference between a plan and a guess.** 0.6
in particular: without it every iteration referencing `sample_data` fails on a
fixture that was never written, which reads as a wiring bug in the system rather
than a gap in the plan.

**On failure**: Fix env / deps / broken import. Do not proceed.

---

## Synthetic Task Fixture (Shared by Iterations 1–5, 7, 9–10)

**This fixture does not exist yet, and the plan previously said it did.**
`tests/integration/conftest.py` exists but carries **none** of the three fixtures
this plan names (`sample_data`, `device`, `seed`) — it is the demo-record fixture
for TODO10. A plan that says "reuse" about fixtures it has never checked is how a
session loses its first twenty minutes. **Iteration 0 must therefore *build* these
before anything can reuse them.**

```python
# tests/integration/conftest.py — ADD (do not assume present)
import torch
from torch.utils.data import DataLoader, TensorDataset


@pytest.fixture(scope="session")
def device() -> str:
    """`cuda` when this box has it, else `cpu` — asserted, never assumed."""
    return "cuda" if torch.cuda.is_available() else "cpu"


@pytest.fixture(scope="session")
def gpu_required() -> None:
    """Skip loudly when CUDA is absent; never let a GPU slice run on CPU."""
    if not torch.cuda.is_available():
        pytest.skip("CUDA unavailable: this slice is a GPU claim")


@pytest.fixture(scope="session")
def seed() -> int:
    return 42


@pytest.fixture(scope="session")
def sample_data(device: str, seed: int):
    """Linearly separable 2D, resident on `device`.

    4 samples, 2 features, 2 classes: class 0 where ``x1 + x2 < 0``, class 1
    otherwise. Perfectly separable, so any optimiser succeeds and a failure is
    unambiguously wiring rather than optimisation.

    The tensors are moved to the device **here** (2.5 asserts this) rather than by
    each test, so no slice can accidentally exercise the CPU path by loading on
    CPU and calling it a GPU test.
    """
    generator = torch.Generator().manual_seed(seed)
    x = torch.randn(4, 2, generator=generator).to(device)
    y = (x.sum(dim=1) >= 0).long()
    return DataLoader(
        TensorDataset(x, y), batch_size=4, shuffle=False, generator=generator
    )
```

**On the fixture's size.** 4 samples is right for *wiring* and wrong for
*throughput*: it is 8 floats, so a GPU slice measures launch overhead and nothing
else. Slices that claim something about the device (2.4, 2.5, 4.6, 7.4) use
`sample_data` for correctness and a larger batch for the timing claim, and say
which they are. Do not inflate the shared fixture to make a timing number look
better — that trades a real signal for a green check.

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
| 2.1 5-D from configs | `compose_system_from_configs(digital, ff, instantaneous, gradient, euclidean, device=device).train_step(x, y)` | Returns dict with keys `loss, energy, nudged_fit_accuracy, free_loss, free_energy, free_accuracy` |
| 2.2 6-D from configs (null plasticity) | `compose_joint_system_from_configs(..., plasticity=null, device=device)` | Behaves identically to 5-D equivalent |
| 2.3 6-D from configs (routing plasticity) | `compose_joint_system_from_configs(..., plasticity=routing, device=device).train_step(x, y)` | Metrics include `plasticity_*` keys; `psi` state advances |
| 2.4 **Metrics are on the right device** | Every tensor in the metric dict | `.device.type == device` — a metric silently resident on CPU is a *staging* bug, and the cheapest GPU defect there is |
| 2.5 **Data actually moved to the GPU** | `x.device.type` after the loader hands it over | `== device`; a loader pinned to CPU makes every GPU slice test the CPU path |

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
| 4.3 Deterministic replay (CPU) | Train 3 epochs on synthetic with `seed=42, deterministic=True` → record metrics → repeat, on **CPU** | All metric values **bitwise** identical (including `free_accuracy`) |
| 4.4 Deterministic replay (GPU) | Same, on **CUDA** | Identical **within a registered tolerance**, not bitwise — TF32/cuDNN reassociate reductions, so a bitwise GPU lock is false by construction and would be a flaky gate, not a lock |
| 4.5 Cross-process replay | Subprocess: `python -c "..."` with same seed/config/device on synthetic | Same metrics as in-process, under the same per-device rule |
| 4.6 **CPU↔GPU agreement** | Same config on both devices | Metrics agree within the registered tolerance. A kernel that is *right on CPU and wrong on CUDA* is the defect class this whole policy exists to find |
| 4.7 **No silent fallback** | `device="cuda"` with CUDA hidden (`CUDA_VISIBLE_DEVICES=""`) | Raises. It must **not** quietly train on CPU and report success |

**Command**:
```bash
# test_pt2_export_roundtrip covers export; add test for to_spec/from_spec
uv run python -m pytest tests/integration/test_spec_roundtrip.py -q --tb=line
uv run python -m pytest tests/integration/test_deterministic_replay.py -q --tb=line
```

**Tolerance, not vibes:** 4.4/4.6 need a *registered* number (the
`REPLAY_METRIC_TOLERANCE = 0.25` pattern, or a tighter dtype-specific one in
`registries.py`) — two tolerances typed in a test file is how they drift apart.

**On failure**: Check `geometry.params` serialization, `SubstrateConfig.device`, RNG state in `SystemTrainer._begin_epoch`, and `torch.use_deterministic_algorithms` — a 4.4 failure on GPU with TF32 on is expected behaviour, not a regression.

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
| 7.4 **Same result on both devices** | Each combo from 7.2, CPU vs CUDA | Metrics agree within tolerance. 7.2 alone would pass on both devices while the two disagreed — the comparison is the claim, not the two runs |

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
DEVICE=$(uv run python -c "import torch;print('cuda' if torch.cuda.is_available() else 'cpu')")
echo "device: $DEVICE"

for i in {0..8}; do
  echo "=== ITERATION $i (device=$DEVICE) ==="
  # Run the iteration's command(s)
  # If any command fails: debug, fix, re-run ONLY that iteration
done

# Cross-device agreement (4.6, 7.4) needs both, on a GPU box.
if [ "$DEVICE" = "cuda" ]; then
  uv run python -m pytest tests/integration/test_cpu_gpu_agreement.py -q --tb=line
fi
```

### Timeouts

Every iteration carries an explicit `pytest.mark.timeout(...)` sized to its
measured cost, **not** the repo default of 120 s where the estimate is larger. A
hung CUDA kernel or a stalled data loader should fail the iteration in seconds,
not hold the session open — the single largest time cost in this repo's history
was a run that never returned a verdict.

### Task Progression (Critical Path First)

| Iterations | Task | Samples | Features | Classes | Purpose |
|------------|------|---------|----------|---------|---------|
| 0 | — | — | — | — | Env sanity |
| 1–4 | **Synthetic 2D** | 4 | 2 | 2 | Critical path: config→train→replay |
| 3.2 | **Digits** | 1797 | 64 | 10 | Sanity: real-ish data, reshaping, multi-class |
| 3.3–3.6 | **Presets (overridden to synthetic)** | 4 | varies | varies | Breadth: all preset factories |
| 5 | **Synthetic** | 4 | 2 | 2 | RecordStore persistence |
| 6 | **Synthetic** | 4 | 2 | 2 | CLI validate |
| 7 | **Synthetic** | 4 | 2 | 2 | Cross-axis matrix (7.4 = CPU↔GPU agreement) |
| 8 | **Synthetic** | 4 | 2 | 2 | Verification suite |

### Failure Handling
1. **Stop immediately** on any failure in the current iteration.
2. **Fix the smallest broken layer** (validation rule, factory, pipeline, config mapping).
3. **Re-run ONLY the failed iteration** until it passes.
4. **Then continue** to the next iteration.

### Running an Iteration Without the Wrong Signal

`addopts` carries `-n 4`, which spreads a *whole directory* across workers. Three
consequences this plan must handle, each of which has already cost a session
somewhere in this repo:

| Trap | What actually happens | What to do |
|---|---|---|
| `pytest tests/integration/test_x.py` | Still fans out to 4 workers; ~10 s of worker startup can exceed a 15 s iteration | Add `-p no:xdist` **or** `-n0` for single-slice iterations |
| A missing new test file | Collection error, not a hypothesis failure | Create the file before running it |
| A green run with no device named | Unstated assumption (see the device policy) | Print the device in the iteration banner |

**Never run `pytest tests/integration/` wholesale** for a gate. It pulls in the
demo suite (hundreds of tests, the `demo` marker) and will be hard-killed with no
verdict — the same trap TODO45 §12.1 recorded. Iterations are run **by file**.

### Priced, Not Guessed

**Every "(Ns)" in the iteration headings is an estimate, and none has been
measured.** TODO48b's founding lesson applies directly: a cost nobody measured is
a cost nobody can plan around, and an estimate quoted as a budget is how a
session discovers it is 10x over.

| Iteration | Stated | Reality |
|---|---|---|
| 7 — cross-axis matrix | 120s | **Unpriced and unbounded.** It enumerates `valid_combinations()` × train 1 epoch. Nothing caps the count, so this is the iteration most likely to run long. |
| 3 — presets | 45s | 4 presets × 2 epochs + digits. Plausible, unmeasured. |
| 8 — Verifier | 60s | *"All tracks"* is not a price. Unknown track count. |

**Rules:**
- Iteration 7 must **cap** its own work (`-k` / a combination limit / a
  `--max-combos` argument) and print what it skipped. An uncapped matrix is the
  one slice here that can eat a session.
- Before any full run, price each iteration with `pytest --co -q` and one timed
  execution. **Do not quote these numbers until they are measured** — and when
  they are measured, correct the table above rather than the memory.

### Reuse & Efficiency
- **Fixtures**: `tests/integration/conftest.py` provides `sample_data`, `device`, `seed`, and `gpu_required`. `device` is a **session** fixture so every slice in a run agrees on one device and the report can name it.
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
- ~~**GPU/CUDA paths**~~ — **no longer excluded.** Promoted into the plan: the device policy above threads `device` through every iteration, Iteration 0.4 makes GPU presence a measured fact, 2.4/2.5 catch CPU-resident staging, and 4.4/4.6/7.4 assert cross-device agreement. CI still runs CPU-only (no GPU) and that pass is reported separately as weaker, never as equivalent.
- **Distributed training** (separate validation)
- **Performance benchmarks** (separate `benchmark` marker)
- **LLM / vision / RL full tasks** (domain presets tested at smoke scale only)

---

## Success Criteria for TODO49 Completion

1. All 9 iterations (0–8) pass consecutively without manual intervention.
2. The final `Verifier(quick_mode=True).run_tracks()` produces a notebook with all tracks `status == "pass"`.
3. **The pass names its device.** A result is `(iterations green, device=cuda)` or `(iterations green, device=cpu, weaker)`. A green run that does not say which device it exercised is not a pass — it is an unstated assumption, and the next reader cannot tell CPU coverage from GPU coverage.
4. **Cross-device agreement is measured, not assumed** (4.6, 7.4), against a registered tolerance.

**What this still does not claim.** All 9 green on synthetic data with 2–3 epochs proves the *wires connect*, not that the system works. It excludes full convergence, distributed training, and real-data scale by design. A learning claim at a real regime remains separate work — see TODO48b §6.

---

## New Test Files Needed (One per Iteration)

**Several "New test needed" commands below name files that do not exist yet**
(`test_record_store.py`, `test_spec_roundtrip.py`, …). That is the intent, but it
means **the first iteration to reference a missing file fails on collection, not
on its hypothesis** — a confusing signal that costs a debugging cycle. Create the
file (even with one placeholder assertion) in the same commit that writes the
slice, so a failure means the hypothesis is wrong rather than the file is absent.

## New Test Files Needed (One per Iteration)

| Iteration | Test File | Purpose |
|-----------|-----------|---------|
| 1 | `tests/integration/test_system_config_validation.py` | Cross-axis validation + config round-trip |
| 2 | `tests/integration/test_config_composed_single_step.py` | Config-composed systems execute train_step |
| 3 | `tests/integration/test_experiment_config_presets.py` | ExperimentConfig presets → trainer on synthetic/digits |
| 4 | `tests/integration/test_spec_roundtrip.py` | to_spec/from_spec bitwise identical |
| 4 | `tests/integration/test_deterministic_replay.py` | Deterministic replay — bitwise on CPU, tolerance on GPU |
| 4 | `tests/integration/test_cpu_gpu_agreement.py` | Same config, both devices, within registered tolerance; and no silent CPU fallback |
| 5 | `tests/integration/test_record_store.py` | RecordStore atomic append, artifacts, queries, vector search |
| 6 | `tests/integration/test_cli_validate.py` | CLI validate command |
| 7 | `tests/integration/test_cross_axis_matrix.py` | Full valid_combinations() enumeration + train |
| 8 | (uses existing `Verifier` class) | Verification suite quick mode |