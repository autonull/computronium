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

**Adding an ontology primitive** — follow the checklist in [`AGENTS.md`](AGENTS.md) (registry row, config classmethod, wiring lockstep lock, export surfaces, contract invariants). **Adding a kernel policy** — subclass the `Policy` protocol in `computronium/experiment/execution/policy.py` and register it in `POLICY_CATALOG`; the interchangeability guarantees then apply for free.

---
