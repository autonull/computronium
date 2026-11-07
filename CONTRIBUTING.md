# Contributing to Computronium

## Prerequisites

- Python 3.14+
- uv (for dependency management)
- 16+ GB RAM recommended
- CUDA 12+ (optional, for GPU runs)

## Quick Start

```bash
# Clone and install
git clone https://github.com/your-org/computronium.git
cd computronium
uv sync --dev --all-extras

# Verify environment
uv run python -c "import optuna, scipy, torchvision, pytest"
uv run comp doctor
```

## Development Workflow

### 1. Code Style & Quality

```bash
# Format (always run)
uv run ruff format .

# Lint changed files only (fast)
uv run ruff check --fix .

# Type check changed files (strict on new modules)
uv run pyright

# Full repo-wide check (slow, run before PR)
uv run ruff check .
uv run pyright --project .
```

### 2. Testing Tiers

| Tier | Command | When |
|------|---------|------|
| **Targeted** | `uv run python -m pytest tests/<path> -k <symbol> -q` | Default for changes |
| **Fast Gate** | `uv run python -m pytest tests/integration/ -m demo -q` | Demo/lock-adjacent changes |
| **Directory Shard** | `uv run python -m pytest tests/<shard> -q` | Round close (primitives 14s, algorithms 88s, unit 117s, property 166s) |
| **Full Suite** | `uv run python -m pytest --cov` | Release candidate |

**Never run `pytest tests/` directly** — it bypasses `testpaths` and pulls in demos.

### 3. Pre-Commit Checklist (Per Commit)

- [ ] `uv run python -c "import optuna, scipy, torchvision, pytest"` (dev-env smoke)
- [ ] `uv run ruff format && uv run ruff check --fix` (changed files)
- [ ] `uv run pyright` (changed files, strict for new modules)
- [ ] Targeted tests for touched modules — output + walltime visible

**Deferred to hygiene pass / round close:**
- [ ] Repo-wide `ruff check` / `pyright`
- [ ] Full `pytest` run with `--cov`
- [ ] `pip-audit`

## Run Gates (Experiment Campaigns)

Before merging experiment-affecting changes, run the appropriate gate:

### Gate 0: Environment Sanity (always)
```bash
uv run comp doctor
uv run comp run demo --dry-run
```

### Gate 1: Ladder Smoke Test (~2 min)
```bash
# CPU, 2 workers, 0.05h budget, ladder promotion
./experiment_shallow.sh 0.05 --ladder --device cpu --workers 2 \
  --axes '{"credit":["gradient"],"update":["euclidean"]}'
# Expect: 0 crashes, L0→L1→L2 promotion works, exit 0
```

### Gate 2: Single-Axis Sweep (~15 min)
```bash
# Test one axis with ladder
./experiment_shallow.sh 0.2 --ladder --device cpu --workers 4 \
  --axes '{"credit":["gradient","homeostatic"],"update":["euclidean","lion"]}'
# Expect: >0 claim-eligible cells, FAIL rate < 25%
```

### Gate 3: Full Hypothesis Suite (~3h)
```bash
# H1: Credit × Update
./experiment_shallow.sh 0.5 --ladder --policy tpe --device cpu --workers 6 \
  --axes '{"credit":["gradient","homeostatic","pc_alm","target_inversion","thermodynamic_contrast"],"update":["euclidean","lion","mean_norm","muon","elastic_consolidation","natural_gradient"]}'

# H2: Dynamics × Substrate
./experiment_shallow.sh 0.5 --ladder --policy tpe --device cpu --workers 6 \
  --axes '{"dynamics":["instantaneous","energy_minimization","lazy","error_predictive_coding"],"substrate":["digital","memristive","optical"]}'

# H3: Plasticity × Credit
./experiment_shallow.sh 0.5 --ladder --policy tpe --device cpu --workers 6 \
  --axes '{"plasticity":["null","temporal_psi","rule_state","fast_weights"],"credit":["gradient","homeostatic","pc_alm","target_inversion"]}'

# Success: 6+ cells reach L1/L2 with 3/5 seed replication, power_achieved verdicts
```

### GPU Rule (Measured 2026-11-07)
| Config | Workers | Result | Use For |
|--------|---------|--------|---------|
| `--device cuda` | 1 | ✅ Works | Quick single-worker tests |
| `--device cuda` | 2+ | ❌ Hangs | Never |
| `--device cpu` | 1-6 | ✅ Works | All parallel runs |

## Adding a New Ontology Primitive

1. **Registry row** — add class to layer's single-source registry (e.g., `DYNAMICS_REGISTRY` in `computronium/ontology/dynamics/__init__.py`)
2. **Config classmethod** — `StateDynamicsConfig.<primitive>()` returns config with matching `dynamics_type`
3. **Run wiring lockstep test** — `tests/property/test_dynamics_wiring_lock.py`
4. **Export surfaces** — root `__all__` + `_LAZY`, `TYPE_CHECKING` imports, `ontology/__init__.py`
5. **Contract invariants** — read `StateDynamics` Protocol docstring (activation layout, settle mutation/autograd, free/nudged semantics)
6. **Validation** — whitelist new `dynamics_type` in `SystemConfig.validate()` consistently
7. **Demo (if shipping)** — follow static `_ARMS` table pattern, add to `computronium/visualization/gallery.py`, re-pin `docs/figures/manifest.json`
8. **Probe conventions** — throwaway scripts in `scripts/probes/` with measured-regime numbers

## Commit Messages

Follow Conventional Commits:
```
<type>(<scope>): <subject>

<body>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`
Subject ≤ 50 chars, imperative mood.

## Pull Requests

- Small, focused changes preferred
- Include test output + walltime for experiment-affecting changes
- Update TODO84.md if modifying the plan
- Run Gate 0 + Gate 1 minimum before requesting review

## Architecture Notes

- **Immutability**: Default to frozen dataclasses, tuples, frozensets
- **Async**: Use `asyncio.TaskGroup`, avoid `gather` for complex flows
- **Thread Safety**: No GIL reliance (PEP 703); use explicit locks
- **Errors**: Custom hierarchy per domain, always chain (`raise ... from`), use `except*` for concurrent failures
- **Resources**: Context managers for all lifecycles
- **Logging**: Standard `logging` with `extra={"task_id": id}`, never `print()`

## Useful Commands

```bash
# Generate validation artifacts (B10)
uv run python -m computronium.experiment.validation.generate

# Show capabilities
uv run comp capabilities list
uv run comp capabilities verify
uv run comp capabilities matrix

# Check alerts on a run
uv run python -m computronium.experiment.monitoring.alerts <store_path> [run_id]

# Run demo
uv run comp demo --store demo.duckdb

# Report on experiment
uv run comp report --store <path> --format text
```