# Release Notes — v3.0.0 (Unified Experiment Kernel)

## Headline

Computronium 3.0.0 is the **unified kernel release**: the six-axis ML library is joined by a governed experiment kernel (`computronium.experiment`), and every legacy pillar that predated the kernel is deleted — wholesale, per the no-backwards-compatibility directive.

## Deleted (legacy pillars)

- `computronium/autoscientist/`, `hyperopt/`, `execution/`, `lightning_/`, `experiments/` (pre-kernel layer), `core/campaign/`
- Legacy-era orphans: `knowledge/`, `analysis/`, `papers/`, `p2p/` evolution/grpc workers, `resources.py`, `utils.py`, `tracking.py`, `sklearn_interface.py`, and remaining pillar-importing tests (52 total across phases B + F)
- Root doc set reduced to `README.md`, `AGENTS.md`, `TODO43.plan3.md`, `TODO44.md`; historical plans and campaign records live in `docs/archive/`
- All DuckDB writes now flow through a single writer: `RecordStore.append()` under a threading lock

## Kernel guarantees (locked)

| ID | Guarantee |
|---|---|
| U1 | Question → RunSpec → Synthesis policy → pipeline → store, end-to-end |
| U2 | Same RunSpec under TPE → identical record schema/store |
| U3 | Multi-round allocation with pause/resume by `run_id` — no re-measurement |
| U4 | Policy interchangeability — same RunSpec/Space/Store, only the policy changes |
| U5 | Cross-policy evidence reuse — one store, no migration, same legality/claims |

Enforced by `tests/acceptance/unified_kernel.py` plus new locks: full-tree import isolation, schema forward tolerance (fail-closed + `unknown` column), single-writer enforcement, CLI↔README drift lock, allocator promotion lock.

## WP18 ContrastDesign

OFAT / fractional-factorial DOE with `contrast_id`, matched groups, and explicit `DataOrigin` labels (exploration / policy-selected / calibration / test / control / contrast) — contrasted arms carry known structure.

## Class E evidence

- Conformance audit C1–C88: **46 pass / 42 skip / 0 fail** (`scripts/probes/conformance_evidence_audit.py`)
- E3 seeded axis effect: **d = −1.4991, p = 0.0011** (reproduces: true)
- E4 transfer provenance: **d = −1.5186, p = 0.00097** (transfers: true)

## Canonical README

Complete rewrite: 11 reference sections, every code block runnable, the two demo blocks locked verbatim against their tests, the CLI table locked against the dispatcher (`tests/property/test_cli_readme_lock.py`), and every claim labeled with its verification level.

## Demonstrations

`scripts/demos/` — six kernel demos (U1 pipeline, policy swap, pause/resume, multi-objective Pareto, cross-policy reuse, contrast design), each built on the same APIs as the acceptance suite.

## Toolchain

Python 3.14+, uv single lockfile, ruff, pyright (venvPath fixed so `duckdb` resolves), pre-commit, pytest. Version bumped 1.0.0 → 3.0.0 to reflect the kernel boundary (no compatibility shims).
