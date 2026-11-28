# Code Guidelines

- Elegant
- Consolidated
- Consistent
- Organized
- Deeply deduplicated: Don't repeat yourself (DRY)
- Abstract
- Modularized
- Parameterized
- Backwards compatibility: NONE
- Few comments: rely on self-documenting code.
- Purpose: professional, not explanatory/educational
- Prefer use of GPU over CPU where appropriate.

## Toolchain
*   Language: **Python 3.14+**
*   **uv**: For dependency management, virtualenvs, and task running (`uv run`, `uv add`). Single lockfile (`uv.lock`); no `requirements.txt`.
*   **Ruff**: For formatting, linting, and import sorting. All config in `pyproject.toml`. Format always (cheap). Lint **changed files only** during development — findings in legacy modules are queued work (Register C / hygiene pass), never commit blockers.
*   **Pyright** (or mypy): **Strict on new/rewritten modules.** Repo-wide checking stays basic until the dedicated hygiene pass closes; type fixes in legacy modules ride that pass, not feature work.
*   **pre-commit**: Runs ruff format + lint on changed files only.
*   **Line Length**: Ruff default (88). Relax per-line with `# noqa: <code>` and a reason, never globally.
*   Rules are enforced by tooling — if a rule can be a config or pre-commit hook, it is one.

## Type System
*   **Modern Syntax**: Built-in generics (`list[str]`), PEP 604 unions (`X | None`). Never import `List`, `Dict`, `Optional`, or `Union`.
*   **PEP 695**: Use `class Cache[T]: ...` and `type UserId = int` for generics and aliases.
*   **Interfaces & Narrowing**: Prefer `Protocol` over ABCs. Use `Self` for fluent returns. Use **`TypeIs`** for custom type narrowing to preserve original type context on failure.
*   **Value Sets**: Use `Literal` / `StrEnum` instead of bare strings.
*   **Data Modeling**:
    *   `@dataclass(frozen=True, slots=True)` for internal value objects.
    *   `TypedDict` for unvalidated structured dicts.
    *   **Pydantic v2** at I/O boundaries for runtime validation.
*   **No `Any`**: Replace with `object`, generics, or `Protocol`. If unavoidable, isolate and document why.

## Architecture & Control Flow
*   **Pattern Matching**: Use `match`/`case` for complex state/data routing, favoring it over chained `if/elif`.
*   **Complexity**: Let Ruff rules (`C901`, `PLR09xx`) enforce function size. Extract `_`-prefixed helpers rather than nesting deeper.
*   **Control Flow**: Flatten with guard clauses (`if not condition: return`). 
*   **Finally Blocks**: **Never** use `return`, `break`, or `continue` inside a `finally` block (PEP 765). This is a hard `SyntaxError` and silently swallows exceptions.
*   **Composition over Inheritance**: Favor small pure functions. Isolate side effects so core logic stays testable.
*   **One Source of Truth per Rule**: legality, pricing, measurement identity, dispatch and capability flags each live in exactly one place. A second table, filter or cache that re-derives one is a defect, not a fallback: feed the first or delete it, and count what the second one used to drop. Capability flags are declared (config field, `ClassVar`, registry row), never inferred by reflection or by shape.
*   **Immutability**: Default to immutable structures (`tuple`, `frozenset`, frozen dataclasses) unless mutation is strictly required.

## Async Concurrency & Thread Safety
*   **Structured Concurrency**: Use `asyncio.TaskGroup` for concurrent tasks. Avoid `asyncio.gather` for complex flows.
*   **Event Loop Hygiene**: Never mix blocking I/O/CPU tasks with `async` code. Use `asyncio.to_thread` for legacy blocking calls.
*   **Thread Safety (PEP 703)**: With free-threaded CPython, **do not rely on the GIL**. Use explicit locks (`threading.Lock`), thread-local storage, or immutable data for shared mutable state.

## Documentation & Modules
*   **Docstrings**: **Google-style** on all public APIs. Type hints replace argument type documentation — focus on behavior, side effects, and invariants.
*   **Comments**: Explain *why*, not *what*. Delete dead code; use `# TODO(name): ...` for deferred work.
*   **Import Hygiene**: Avoid heavy computations or I/O at the module level. Prevent circular imports via local imports or dependency injection.

## Errors, Logging & Resources
*   **Safe Interpolation**: Use **t-strings** (PEP 750) for logging and templating to enable safe, deferred interpolation. Never use f-strings for database queries (use driver parameterization) or untrusted log inputs.
*   **Logging**: Standard `logging` (or `structlog`). Never `print()`. Include context: `logger.error("msg", extra={"task_id": id})`.
*   **Exceptions**: Define a small custom hierarchy per domain. Always chain: `raise DomainError("msg") from original_exception`. Use `except*` (PEP 654) for concurrent independent failures.
*   **Resources**: Use context managers (`with` / `async with`) for all resource lifecycles.

## Environment (binding)
*   **Env restore**: `uv sync --dev --all-extras` — bare `uv sync` strips dev
    extras and produces `ModuleNotFoundError` mid-landing.
*   **Dev-env smoke** (run before any gate): `uv run python -c "import optuna, scipy, torchvision, pytest"` —
    a stripped env fails here in seconds instead of mid-gate.
*   **`UV_LINK_MODE=copy`**: set in the shell env (or `.env`) on this
    filesystem layout — the uv cache hardlink falls back to copy with a
    warning on every `uv run` otherwise (cosmetic, R4.3).

## Testing

Everything about testing — the tiers, the per-commit and round-close
duties, the coverage ratchet, the test-writing rules and the primitive
testing requirements — lives in [`AGENTS.testing.md`](AGENTS.testing.md).

## Experimenting

Everything about experiments — the SEC loop, the rungs, the evidence rules,
the log template and the cell walltime rule — lives in
[`AGENTS.experimenting.md`](AGENTS.experimenting.md).

## Security & Project Structure
*   **Dependency Scanning**: Run `pip-audit` in CI.
*   **Static Analysis**: Enable Ruff's `S` (bandit) rule set. Never hardcode secrets.
*   **Project Structure**: `pyproject.toml` is the single source of truth. `__init__.py` exposes only the public API via `__all__`; internal modules are `_`-prefixed.
*   **CI Gate Order** (what CI runs when adopted — agent per-commit duties are the scoped checklist below, not this list): `ruff format --check` → `ruff check` → `pyright` → `pytest --cov` → `pip-audit`.

## Agent Commit Checklist
**Per commit — scoped and fast:**
- [ ] Dev-env smoke (see Environment): `uv run python -c "import optuna, scipy, torchvision, pytest"`
- [ ] `ruff format` && `ruff check --fix` on changed files
- [ ] `pyright` on changed files (strict for new modules)

**Deferred — hygiene pass / round close (never per-commit):**
- [ ] Repo-wide `ruff check` / `pyright` (Register C scope)

## Checklist: Adding a New Ontology Primitive

1. **Registry row** — add the class to the layer's single-source registry
   (`DYNAMICS_REGISTRY` in `computronium/ontology/dynamics/__init__.py` for
   StateDynamics). Two wiring edits total: class def + registry entry.
2. **Config classmethod** — `StateDynamicsConfig.<primitive>()` returns a
   config whose `dynamics_type` matches the registry key.
3. **Run the wiring lockstep lock** — `tests/property/test_dynamics_wiring_lock.py`
   proves registry ↔ config classmethods ↔ root `__all__`/`_LAZY` ↔ root
   `TYPE_CHECKING` imports stay in sync. Fix what it flags; never bypass it.
4. **Export surfaces** — root `__all__` + `_LAZY` (and the `TYPE_CHECKING`
   import block), `ontology/__init__.py` imports + `__all__`.
5. **Contract invariants** — read the `StateDynamics` Protocol docstring
   (activation layout, settle mutation/autograd contract, free/nudged
   semantics) before writing `settle`/`compute_energy`.
6. **Validation** — if `SystemConfig.validate()` needs a new compatibility
   branch, whitelist the new `dynamics_type` consistently in *all* credit/
   substrate branches (see R5.2 retro: the PC family divergence).
6b. **Target kind** — if the new law reads the target, declare
   `AxisSpec.target_kind` on its axis row. A law written over one-hot targets
   (a label channel, a centred one-hot residual, argmax agreement) must say
   `"class_index"`, so the declared space refuses it on a continuous-target
   task instead of raising inside the cell (TODO91 S9).
7. **Demo (if shipping one)** — demo test follows the static `_ARMS` table
   pattern (module scope, `_train_arm`/`_probe_arm` extracted, walltime
   printed never recorded), one `DEMOS` registry row in
   `computronium/visualization/gallery.py`, then re-pin
   `docs/figures/manifest.json` via the gallery lock.
8. **Probe conventions** — throwaway probe scripts live in `scripts/probes/`
   with their measured-regime numbers and a docstring citing the demo they
   informed.

## Documentation
- Don't edit README.md directly; in `docs/readme/*`, edit individual sections or the generator script
