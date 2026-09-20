# TODO32b: Continuation of TODO32 — Polish, Drift Repairs & Force-Multiplier Enablement

**Continues**: `TODO32.md` (Primitive/Algorithm Structure with a Shared Acceleration Layer — **complete**: 64 implementations, 43 primitives + 21 algorithms, 741 tests passing).

**Context**: TODO32 built the `acceleration/` shared layer, the `primitives/` and `algorithms/` registries, scaffolding, CI parity gates, and lazy loading. TODO32b does not add primitives — it (a) repairs drift the completed work surfaced, (b) finishes the CLI/docs tooling TODO32 sketched, (c) enables the Phase 8 Triton roadmap, and (d) leverages the completed registry for new verification capabilities.

---

## Phase A: Drift Repairs (Fix First — Small, Real Bugs in Completed Work)

TODO32 standardized the `StateDynamics` protocol (uniform `settle(..., on_step=...)` signature) and the `test_<name>_*.py` test-naming scheme. The type checker and LSP confirm residual drift:

| Task | File | Problem | Fix |
|------|------|---------|-----|
| A1 | `computronium/ontology/dynamics/_dynamics.py:2167` (`DiffusionDynamics`) | `settle` lacks the `on_step` callback parameter — protocol-incompatible; `compose_system` rejects it (confirmed pyright error) | Add `on_step: ((int, float) -> None) \| None = None`, mirroring `InstantaneousDynamics`/`SpikeIntegrationDynamics` (steps 48/250 of TODO32) |
| A2 | `computronium/core/presets.py:498,500` | `.weight`/`.bias` accessed on values typed `Tensor \| Module` | Narrow with `isinstance(..., nn.Linear)` or type the container precisely; strict-mode clean |
| A3 | Stale test artifacts | LSP reports `unknown import symbol` against non-renamed paths (`tests/primitives/substrate/memristive/test_reference.py`, `.../elastic_consolidation/test_kernel_parity.py`, `.../rule_state/test_kernel_parity.py`) that no longer exist on disk | Confirm files are gone (`git status`), purge `__pycache__`/`.pytest_cache` if needed; verify `uv run python -m pytest tests/primitives -q` collects cleanly |
| A4 | `computronium/primitives/substrate/memristive/__init__.py` | `make_case_noisy` exported but unused by renamed tests — verify consumers or drop | Grep for consumers; keep only if referenced |

**Acceptance**: `pyright computronium/ontology/dynamics/_dynamics.py computronium/core/presets.py` → 0 errors; full primitive suite still passes.

**Effort**: ~1 hour.

---

## Phase B: Microbench & Matrix CLI Enhancements (Finish TODO32's Sketched Tooling)

| Task | Description | Acceptance |
|------|-------------|------------|
| B1 | `microbench.py`: `--iterations`, `--warmup`, `--device cpu,cuda`, `--output bench.jsonl` | One invocation produces a resumable JSONL artifact |
| B2 | `microbench.py`: `--format csv` (median, p95, throughput; columns `id,backend,device,median_ms,p95_ms,throughput`) | CSV importable into pandas for regression diffs |
| B3 | `matrix.py`: `--format github-markdown` | Table renders natively in PR comments |
| B4 | `matrix.py`: `--filter axis=state_dynamics kind=primitive status=kernel_unverified` | Composable filters for CI subsets |
| B5 | Git-SHA stamping: `--tag ${GIT_SHA}` written into JSONL rows (Force Multiplier #9 from TODO32) | Benchmarks become comparative-regression trackable |

**Effort**: ~2 hours. Independent.

---

## Phase C: Kernel Development Workflow (Unlocks TODO32 Phase 8)

Highest-leverage item: TODO32's Triton roadmap (12 kernels) is blocked on tooling.

| Task | Description | Acceptance |
|------|-------------|------------|
| C1 | `scripts/scaffold_kernel.py --primitive <id> --technology triton` | Generates Triton stub, `is_available()`, reference delegate, tolerance pulled from spec's `ParityTolerance` |
| C2 | `scripts/kernel_dev.py --primitive <id> --watch` | Re-runs parity on file change (watchdog/polling); prints pass/fail + max abs diff |
| C3 | `scripts/validate_composition.py --all-algorithms` | Static check: each algorithm's `uses_primitives` ⊆ actually-imported primitives; exits nonzero on drift; wired into CI gate |
| C4 | Wire C3 into `.github/workflows/ci.yml` alongside existing parity gate | CI fails on undeclared primitive dependencies |

**Effort**: C1–C2 ~3 hours, C3–C4 ~2 hours.

**Then** execute the TODO32 Phase 8 kernel order (first three maximize reuse):
1. `random_projections` (batched matmul) → 2. `local_goodness` (layer reduction) → 3. `energy_minimization` (gradient+settle) → 4. `thermodynamic_contrast` (reuses #3) → remaining per TODO32 §"Kernel Development Order".

---

## Phase D: Documentation from Specs (Leverage Spec Metadata Already Captured)

Every `ImplementationSpec` already carries `summary`, `equations`, `invariants`, `notes`, `tags`, `evidence_ids` — TODO32 captured this metadata but never rendered it.

| Task | Description | Acceptance |
|------|-------------|------------|
| D1 | `scripts/generate_docs.py --all --output docs/generated/` | Renders `docs/generated/primitives/<axis>/<name>.md` + `docs/generated/algorithms/<name>.md` from spec fields |
| D2 | Jinja2 template: Purpose, Mathematics (equations), Invariants, Reference, Kernel, Parity tolerance, Status, Tags | Matches TODO32's sketched README template |
| D3 | Generate `docs/generated/IMPLEMENTATION_MATRIX.md` from `matrix.py --format markdown` | Single rendered source of truth for registry status |
| D4 | Scaffolders gain `--docs` flag: new primitives/algorithms get doc stubs automatically | `scaffold_primitive.py --docs` emits README alongside the 6 files |
| D5 | Optional: property tests from `invariants` tuples (Force Multiplier #10) — deterministic-seed and finiteness invariants are mechanically checkable | Hypothesis tests generated per spec |

**Effort**: D1–D4 ~4 hours; D5 optional, ~2 hours.

---

## Phase E: Registry & Bench Dashboard (Smaller Follow-ons)

| Task | Description | Acceptance |
|------|-------------|------------|
| E1 | `registry.list_by_axis()` helper | `{axis: [spec_ids]}` dict; used by CLI/docs filters |
| E2 | Import-time lock: cold `import computronium.primitives` < 10ms (currently ~5ms — pin it) | A test asserting the bound, so lazy loading can't silently regress |
| E3 | `scripts/bench_dashboard.py` | Matplotlib/plotly latency-vs-commit plot from B5's JSONL artifacts |
| E4 | `pyproject.toml` entry points for explicit registration (alternative to `__getattr__` scan) — **evaluate only if** lazy loading proves limiting | Decision recorded either way |

---

## Deferred (Unchanged Policy from TODO32)

- **Legacy `acceleration/` lint debt** (`fa_kernels.py`, `triton_kernels.py`, etc. — invalid `# noqa` directives, ~283 pyright errors in `triton_kernels.py`): fix **only when touched** for real work. Never a proactive sweep.
- **Test coverage floors**: none until API stabilizes (AGENTS.md).
- **Repo-wide gates**: full `pytest --cov` + `pip-audit` only at round close.

---

## Execution Order & Rationale

1. **A (drift repairs)** — the completed protocol standardization is incomplete until `DiffusionDynamics` conforms; everything downstream assumes it.
2. **C1–C4 (kernel workflow)** — unblocks the entire Phase 8 roadmap; `validate_composition.py` is the cheapest permanent guard.
3. **B (bench/matrix CLI)** — independent; do in spare cycles; B5 makes C's kernel work measurable.
4. **D (docs from specs)** — pure leverage: metadata already exists, rendering is mechanical.
5. **E** — small polish; E2 is the one item with regression value.
6. **Phase 8 kernels** — now unblocked by C; follow TODO32's reuse-maximizing order.

## Per-Commit Checklist (Scoped & Fast — per AGENTS.md)

- [ ] Dev-env smoke: `uv run python -c "import optuna, scipy, torchvision, pytest"`
- [ ] `ruff format` && `ruff check --fix` on **changed files only**
- [ ] `pyright` on **changed files only** (strict for new modules)
- [ ] Targeted tests: `uv run python -m pytest tests/<touched_path> -q` — **always `python -m pytest`** (bare `pytest` resolves to the system pytest at `~/.local/bin/pytest`, which caused the `PytestRemovedIn10Warning` + `ModuleNotFoundError` incident on 2026-09-20)

---

## State Table (Start of TODO32b)

| Category | TODO32 Result | TODO32b Target |
|----------|---------------|----------------|
| Primitives | 43/43 ✅ | no additions |
| Algorithms | 21/21 ✅ | no additions |
| Protocol conformance | `DiffusionDynamics` non-conforming ❌ | A1 fixes → all 6 axes conform ✅ |
| Triton kernels | 0 (all reference fallback) | workflow (C) + first 3 kernels |
| Tests | 741 passed, 32 skipped | + invariant property tests (D5) |
| Docs | IDENTITY_CARDS only | per-implementation rendered docs (D) |
| CI | parity gate + matrix | + composition validation (C4) |
| Registry | lazy loading, ~5ms | import-time lock (E2) |

*Created 2026-09-20. Continues TODO32.md; supersedes its "New Improvement Opportunities" and "Force Multipliers" sections as the active plan.*