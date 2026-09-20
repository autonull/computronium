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
| B6 | Peak-memory capture: `torch.cuda.max_memory_allocated` / CPU RSS delta alongside latency (memory_mb is a first-class research objective in this repo) | JSONL rows carry `peak_mem_mb`; CSV gains the column |

**Effort**: ~2 hours. Independent.

---

## Phase C: Kernel Development Workflow (Unlocks TODO32 Phase 8)

Highest-leverage item: TODO32's Triton roadmap (12 kernels) is blocked on tooling. **Registry reality (2026-09-20): 41 `reference_only`, 22 `kernel_unverified`, 1 `kernel_verified` — `dispatch.select_backend(spec, "auto")` returns `"reference"` for ~98% of the fleet. The dispatch plumbing is wired into every generated factory; this phase is what makes it route somewhere.**

| Task | Description | Acceptance |
|------|-------------|------------|
| C0 | **Kernel ladder** (new, before any Triton): each primitive's `kernel.py` promotes through `reference → torch.compile → Triton`, with microbench evidence at each rung. `predictive_settling` and `energy_minimization` already prove the `torch.compile` rung works. Measure compile gains **before** writing Triton; skip Triton where compile achieves parity + speedup (be skeptical of low-performing experiments — an unprofitable Triton kernel is a defect, not a deliverable). GPU-first per AGENTS.md | Each promoted kernel: parity passes, `spec.status` promoted to `kernel_verified`, microbench JSONL attached as evidence |
| C1 | `scripts/scaffold_kernel.py --primitive <id> --technology {compile,triton}` (compile is the default first rung) | Generates kernel stub, `is_available()`, reference delegate, tolerance pulled from spec's `ParityTolerance`; `--technology compile` emits the torch.compile wrapper |
| C2 | `scripts/kernel_dev.py --primitive <id> --watch` | Re-runs parity on file change (watchdog/polling); prints pass/fail + max abs diff |
| C3 | `scripts/validate_composition.py --all-algorithms` | Static check: each algorithm's `uses_primitives` ⊆ actually-imported primitives; exits nonzero on drift; first run is expected to surface drift in the 21 scaffolded algorithms — record findings |
| C4 | Wire C3 into `.github/workflows/ci.yml` alongside existing parity gate | CI fails on undeclared primitive dependencies |

**Effort**: C0-C1 ~3 hours, C2 ~2 hours, C3–C4 ~2 hours.

**Then** execute the TODO32 Phase 8 kernel order **through the ladder (C0), Triton only where compile insufficient**:
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

## Phase F: Registry Integrity Locks (Protect the Completed Work — TODO32's Own Doctrine, Extended)

TODO32 built `test_dynamics_wiring_lock.py` for the ontology registry; the new 64-spec registry has **no equivalent lock** and can drift silently.

| Task | Description | Acceptance |
|------|-------------|------------|
| F1 | **Ontology ↔ primitive completeness lock**: every concrete ontology class across all 6 axes has exactly one primitive spec (id, ontology class, config classmethod), and every primitive spec resolves to a live ontology class. Extends `test_dynamics_wiring_lock` doctrine to `primitives/` + `algorithms/` | `tests/property/test_registry_completeness_lock.py`; fails on orphan ontology classes or dead specs |
| F2 | **Scaffolder self-test (round-trip)**: run `scaffold_primitive.py` + `scaffold_algorithm.py` into a tmpdir and collect the generated tests. The 90%-boilerplate claim (TODO32 §Force Multiplier 1) is now critical path for Phase 8 — if the scaffolder rots, every future addition suffers | Scaffolder output passes its own tests in CI; regression caught immediately |
| F3 | **Skipped-test audit**: the 32 skips are geometry/substrate structural-parity gaps TODO32 deferred. Replace blanket skips with real structural-equivalence assertions (factory determinism: two `make_substrate()`/`make_geometry()` calls with same config → bitwise-equal state tensors; spec round-trip) | Skips drop from 32 toward 0; each remaining skip carries a documented reason |
| F4 | **Status-promotion rule**: `kernel_verified` requires (a) parity green on CPU + GPU where available, (b) microbench JSONL evidence, (c) dispatch `auto` routes to kernel. Encode as a check in `test_all_implementations.py` so the 22 `kernel_unverified` specs can't silently claim verified | Count of `kernel_verified` only grows via the C0 ladder |

**Effort**: F1 ~2 hours, F2 ~1 hour, F3 ~3 hours, F4 ~1 hour. F1–F2 are the highest-value guards.

---

## Deferred (Unchanged Policy from TODO32)

- **Legacy `acceleration/` lint debt** (`fa_kernels.py`, `triton_kernels.py`, etc. — invalid `# noqa` directives, ~283 pyright errors in `triton_kernels.py`): fix **only when touched** for real work. Never a proactive sweep.
- **Test coverage floors**: none until API stabilizes (AGENTS.md).
- **Repo-wide gates**: full `pytest --cov` + `pip-audit` only at round close.

---

## Execution Order & Rationale

1. **A (drift repairs)** — the completed protocol standardization is incomplete until `DiffusionDynamics` conforms; everything downstream assumes it.
2. **F1–F2 (integrity locks)** — cheap, permanent guards installed *before* Phase 8 churns the registry; F4's promotion rule makes C0's ladder auditable.
3. **C (kernel ladder + workflow)** — unblocks Phase 8; `validate_composition.py` is the cheapest CI guard; C0 makes ~98%-dormant dispatch actually route.
4. **B (bench/matrix CLI)** — independent; do in spare cycles; B5/B6 make C's kernel work measurable.
5. **D (docs from specs)** — pure leverage: metadata already exists, rendering is mechanical.
6. **E** — small polish; E2 is the one item with regression value.
7. **F3–F4 / Phase 8 kernels** — interleave: each ladder rung (C0) exercises F4; skip audit lands once kernels stop changing structural primitives.

## Housekeeping (G)

| Task | Description |
|------|-------------|
| G1 | Append a pointer row to `TODO32.md`'s progress tables: "Continued by TODO32b.md" so future sessions find the active plan |
| G2 | Mark TODO32.md's "New Improvement Opportunities" / "Force Multipliers" sections as superseded by this file |

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
| Triton kernels | 0 (all reference fallback); dispatch resolves to reference for ~98% of fleet | kernel ladder (C0): compile rung measured first, Triton only where insufficient |
| Tests | 741 passed, **32 skipped** | + invariant property tests (D5); skips audited → structural assertions (F3) |
| Registry locks | dynamics wiring lock only | completeness lock for 64-spec registry (F1), scaffolder round-trip (F2), status-promotion rule (F4) |
| Docs | IDENTITY_CARDS only | per-implementation rendered docs (D) |
| CI | parity gate + matrix | + composition validation (C4) |
| Registry | lazy loading, ~5ms | import-time lock (E2) |

*Created 2026-09-20. Continues TODO32.md; supersedes its "New Improvement Opportunities" and "Force Multipliers" sections as the active plan.*