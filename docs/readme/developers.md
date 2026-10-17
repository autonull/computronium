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

**Good first additions** (designed, not built): `capabilities` command · per-stage timing fields · silent-drop detector · C12 ruler-geometry fallback · `defect revoke` re-probe · policy-aware compatibility sampling. Each is a named row in the readiness ledger, not a silent absence.

### Two Entry Points, One Config Surface

The kernel exposes two entry points that share the **same `ExperimentConfig`** (via `schema/unified_config.py`):

| Entry Point | Use Case | Flow |
|-------------|----------|------|
| `question_first()` | Single-question exploration (U1) | Question → `RunSpec` → Synthesis policy → Pipeline → Store → Report |
| `LoopDriver` | Continuous multi-round campaigns | `ExperimentConfig` → `LoopConfig` → Explore/Exploit cycles → Allocator (S10) → CEEC export |

- **`question_first`** (in `surface/profiles.py`) is the documented U1 flow: call it with a natural-language question and a profile, it builds a `RunSpec`, runs the pipeline once, and returns governed evidence.
- **`LoopDriver`** (in `registry/loop.py`) is the continuous engine: it reads an `ExperimentConfig`, runs explore/exploit rounds, uses `EvidenceDrivenAllocator` for successive-halving allocation (S10), and can export claims to the standalone CEEC (`packages/ceec-core`).

Both paths delegate to the same `PipelineRunner` (stages S1–S11), `RecordStore`, and `SearchSpace`. They do not drift because `ExperimentConfig` is the single source of truth for: search `policy`, `use_icu_guided`, `task_schedule`/domains, objectives, fidelity ladder, budget, and device.

