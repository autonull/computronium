# CEEC Ledger (Epistemic Foundry)

This directory is the primary CEEC ledger of the Epistemic Foundry.

- `ceec.sqlite3` — append-only SQLite ledger (objects, gates, decisions, calibration)
- `artifacts/<hash[:2]>/<hash>` — content-addressed immutable artifacts
- `exports/` — human-readable exports (derived, not primary)

## Commands

```
uv run python -m computronium.ceec.cli init
uv run python -m computronium.ceec.cli bootstrap                 # configs/ceec/
uv run python -m computronium.ceec.cli migrate                   # TODO18 records
uv run python -m computronium.ceec.cli propose --limit 16
uv run python -m computronium.ceec.cli decide --rationale "..."
uv run python -m computronium.ceec.cli audit
uv run python -m computronium.ceec.cli calibration-report
uv run python -m computronium.ceec.cli status-history --belief B-...
uv run python -m computronium.ceec.cli quarantine-report
uv run python -m computronium.ceec.cli export
```

## Policy

Append-only; corrections create new artifacts linked with `supersedes`
relations. See `docs/ceec/LEDGER_POLICY.md`. The ledger is audit-clean at
bootstrap (8 instruments, 5 hypotheses, 5 goals, 5 pre-registered
experiments, 4 migrated TODO18 records).
