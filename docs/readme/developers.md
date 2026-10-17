## For developers

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

**Adding an ontology primitive** — the whole ramp is in this README:

1. add the class to the layer's registry (`DYNAMICS_REGISTRY` in `computronium/ontology/dynamics/__init__.py` for `StateDynamics`);
2. add a `StateDynamicsConfig.<primitive>()` classmethod whose `dynamics_type` matches the registry key;
3. run `tests/property/test_dynamics_wiring_lock.py` — it proves registry ↔ config ↔ root `__all__`/`_LAZY` ↔ `TYPE_CHECKING` stay in sync;
4. export it on the root surface (`__all__` + `_LAZY` + the `TYPE_CHECKING` block) and in `ontology/__init__.py`;
5. read the `StateDynamics` protocol docstring for the activation, settle-mutation/autograd and free/nudged contracts;
6. whitelist the new `dynamics_type` in every `SystemConfig.validate()` credit/substrate branch;
7. if shipping a demo, add one `DEMOS` row in `computronium/visualization/gallery.py` and re-pin `docs/figures/manifest.json`.

**Adding a kernel policy** — subclass the `Policy` protocol in `computronium/experiment/execution/policy.py` and register it in `POLICY_CATALOG`; the interchangeability guarantees then apply for free.

**Good first additions** (designed, not built): `capabilities` command · per-stage timing fields · silent-drop detector · C12 ruler-geometry fallback · `defect revoke` re-probe · policy-aware compatibility sampling. Each is a named row in [Status and scope](#status-and-scope), not a silent absence.

### Two Entry Points, One Config Surface

The kernel exposes two entry points that share the **same `ExperimentConfig`** (via `schema/unified_config.py`):

| Entry Point | Use Case | Flow |
|-------------|----------|------|
| `question_first()` | Single-question exploration (U1) | Question → `RunSpec` → Synthesis policy → Pipeline → Store → Report |
| `LoopDriver` | Continuous multi-round campaigns | `ExperimentConfig` → `LoopConfig` → Explore/Exploit cycles → Allocator (S10) → CEEC export |

- **`question_first`** (in `surface/profiles.py`) is the documented U1 flow: call it with a natural-language question and a profile, it builds a `RunSpec`, runs the pipeline once, and returns governed evidence.
- **`LoopDriver`** (in `registry/loop.py`) is the continuous engine: it reads an `ExperimentConfig`, runs explore/exploit rounds, uses `EvidenceDrivenAllocator` for successive-halving allocation (S10), and can export claims to the standalone CEEC (`packages/ceec-core`).

Both paths delegate to the same `PipelineRunner` (stages S1–S11), `RecordStore`, and `SearchSpace`. They do not drift because `ExperimentConfig` is the single source of truth for: search `policy`, `use_icu_guided`, `task_schedule`/domains, objectives, fidelity ladder, budget, and device.

### 🛠️ Kernel Development Workflow

Tooling to promote kernels through the ladder with parity + microbench evidence at each rung.

#### `scaffold_kernel.py` — Generate Kernel Stubs

```bash
# Torch.compile rung (default first rung for StateDynamics primitives)
uv run python scripts/scaffold_kernel.py \
    --primitive primitive.state_dynamics.energy_minimization \
    --technology compile

# Triton rung (for credit primitives, or where compile insufficient)
uv run python scripts/scaffold_kernel.py \
    --primitive primitive.credit_assignment.random_projections \
    --technology triton
```

Generates `kernel.py` with:
- `is_available()` — runtime capability check
- `step(case)` — kernel entrypoint delegating to reference when unavailable
- Parity tolerance pulled from spec's `ParityTolerance`

#### `kernel_dev.py` — Watch & Re-test

```bash
# Watch mode: re-runs parity on file change (polling, no deps)
uv run python scripts/kernel_dev.py \
    --primitive primitive.credit_assignment.random_projections \
    --watch

# Single run
uv run python scripts/kernel_dev.py \
    --primitive primitive.credit_assignment.random_projections \
    --once
```

#### `validate_composition.py` — Algorithm Dependency Audit

```bash
# Validate all 21 algorithm specs
uv run python scripts/validate_composition.py --all-algorithms

# Validate single algorithm
uv run python scripts/validate_composition.py --algorithm algorithm.backprop
```

Static check: each algorithm's `uses_primitives ⊆ actually-imported primitives`. Wired into CI (`.github/workflows/ci.yml`).


### 📚 Documentation & Bench Tools from Specs

#### `generate_docs.py` — Render Spec Metadata

```bash
# Generate all docs + implementation matrix
uv run python scripts/generate_docs.py --all --output docs/generated/

# Single implementation
uv run python scripts/generate_docs.py --id primitive.state_dynamics.energy_minimization
```

Outputs:
- `docs/generated/primitives/<axis>/<name>.md` — Purpose, Mathematics (equations), Invariants, Reference, Kernel, Parity tolerance, Status, Tags
- `docs/generated/algorithms/<name>.md`
- `docs/generated/IMPLEMENTATION_MATRIX.md` — from `matrix.py --format github-markdown`

#### `generate_property_tests.py` — Hypothesis Tests from Invariants

```bash
uv run python scripts/generate_property_tests.py --all --output tests/property/generated/
```

Generates 73 tests for 48 specs (excludes geometry/substrate with different interfaces):
- **Deterministic seed**: same seed → bitwise-equal outputs
- **Finite state**: no NaN/Inf in outputs (covers `state remains finite`, `activations remain finite`, `parameters remain finite`, etc.)

#### `bench_dashboard.py` — Latency/Memory vs Commit

```bash
# Generate dashboard plots from microbench JSONL artifacts
uv run python scripts/bench_dashboard.py --input artifacts/benchmarks/ --png artifacts/bench_dashboard.png

# Text summary only
uv run python scripts/bench_dashboard.py --input artifacts/benchmarks/ --summary-only

# Filter to specific spec
uv run python scripts/bench_dashboard.py --input artifacts/benchmarks/ --spec primitive.state_dynamics.energy_minimization
```

Plots median/p95 latency and peak memory across git commits from microbench JSONL (which embeds git SHA via `--tag`).


### 🧪 Enhanced CLI Tools

#### `microbench.py` — Microbenchmark Runner

```bash
# Single implementation with full options
uv run python -m computronium.acceleration.microbench \
    --id primitive.state_dynamics.energy_minimization \
    --backend kernel \
    --device cuda \
    --steps 10 \
    --dtype float32 \
    --seed 42 \
    --warmup 3 \
    --iterations 10 \
    --format jsonl \
    --output artifacts/benchmarks/energy_minimization.jsonl \
    --tag $(git rev-parse HEAD)

# All implementations (CI-friendly)
uv run python -m computronium.acceleration.microbench --all --format csv --output bench.csv
```

**New flags**:
- `--iterations` / `--warmup` — statistical measurement
- `--output bench.jsonl` — resumable JSONL artifact (one line per iteration)
- `--format csv` — summary CSV (median, p95, throughput, peak_mem_mb)
- `--tag` — git SHA stamped into each row for regression tracking
- Peak memory capture: `torch.cuda.max_memory_allocated` / CPU RSS delta

#### `matrix.py` — Implementation Matrix

```bash
# GitHub-flavored markdown (renders in PR comments)
uv run python -m computronium.acceleration.matrix --format github-markdown

# Composable filters for CI subsets
uv run python -m computronium.acceleration.matrix \
    --filter axis=state_dynamics,kind=primitive,status=kernel_unverified \
    --format json
```


### 🧪 Registry Integrity Locks (Extended Verification Framework)

These locks protect the 64-spec registry from silent drift — extending TODO32's `test_dynamics_wiring_lock.py` doctrine.

| Lock | File | Purpose |
|------|------|---------|
| **Completeness** | `tests/property/test_registry_completeness_lock.py` | Every ontology class ↔ exactly one primitive spec; every spec resolves to live class (13 tests) |
| **Scaffolder round-trip** | Template rendering verified | `scaffold_primitive.py`/`scaffold_algorithm.py` output passes own tests |
| **Structural equivalence** | Geometry/Substrate primitives | Factory determinism: same config → bitwise-equal state tensors; spec round-trip |
| **Promotion rule** | `tests/property/test_kernel_verified_promotion_rule.py` | `kernel_verified` requires: (a) parity on CPU+GPU, (b) microbench JSONL evidence, (c) dispatch `auto` routes to kernel (25 tests) |
