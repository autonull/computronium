# CEEC Ledger Policy

## Backend

SQLite at `ceec/ceec.sqlite3` (stdlib, relational integrity, auditable, no external service).

## Append-only rules

Append-only tables: `artifacts`, `evidence`, `derived`, `decisions`, `gate_outcomes`, `status_changes`, `calibration_records`, plus junction tables. The public API exposes no update or delete for these. Beliefs and goals are identity + revision: `beliefs`/`goals` rows are immutable identity; probability/utility changes append `belief_revisions`/`goal_revisions`. Previous revisions remain recoverable.

## Artifact hashing and storage

- Content-addressed: artifact id is `sha256:<hex>`.
- Files stored at `ceec/artifacts/<hash[:2]>/<hash>`.
- Ingestion refuses to overwrite an existing hash (idempotent re-ingest returns the existing record).
- Corrections create a new artifact linked via a derived `supersedes` relation; never overwrite.

## Correction procedure

1. Ingest corrected artifact (new hash).
2. Record a `derived` object of type `correction` with `supersedes` inputs.
3. If the correction invalidates a measurement, quarantine or reopen the affected belief with the correction as trigger evidence.

## Export procedure

`uv run python -m computronium.ceec.cli export --output ceec/exports/` writes human-readable JSON/markdown summaries of beliefs, statuses, decisions, gates, and calibration. Exports are derived artifacts, not primary records.

## Retention

No garbage collection. The ledger is small relative to experiment outputs; large tensors live in artifact files, with evidence storing only references.
