## 11. FAQ / Troubleshooting + Glossary

**FAQ**

- *`ModuleNotFoundError` after a sync* — run `uv sync --dev --all-extras` (bare `uv sync` strips dev extras) and the dev-env smoke command.
- *DuckDB store is locked* — the evidence store is **single-writer**: all writes flow through `RecordStore.append()` under a threading lock, enforced by `tests/property/test_single_writer_enforcement.py`. Do not open a second writer process against the same file; readers are fine, cross-process writers are not supported.
- *`UnsupportedSchemaVersionError`* — a record was written by a newer kernel than the reader. Upgrade the reader; unknown-field tolerance is fail-closed by design.
- *GPU* — optional. `uv run comp benchmark` runs on CPU.

**Glossary**

- **Coordinate** — a point in the 6-axis space; the unit of comparison.
- **RunSpec** — the serialized specification of a run: question, space, stages, budget.
- **SearchSpace** — the legality-checked subspace a policy proposes within.
- **Policy** — the proposal strategy; the only varying part between kernel experiments.
- **Stage** — one step S1–S11 of the pipeline.
- **Record** — one measured row in the evidence store (identity, provenance, status, payload).
- **Claim** — a governed statement derived from records, with a verification level.

---
