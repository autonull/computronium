# ceec-core

Standalone epistemic governance ledger — evidence, beliefs, gates, quarantine,
calibration, and audit — extracted from the Computronium project (CEEC-Core
v1.0 semantics). No Computronium dependency.

## What it does

CEEC-Core is an append-only SQLite ledger for rigorous ML experimentation.
It records artifacts, evidence, beliefs, goals, experiments, and decisions;
enforces promotion/boundary/quarantine gates; tracks calibration; and audits
the ledger for epistemic defects.

## Install

```bash
pip install -e packages/ceec-core
ceec init --ledger-dir ./ledger
ceec audit --ledger-dir ./ledger
```

## Usage

```python
from ceec import CEECStore, models
from ceec.audit import run_audit

with CEECStore("ledger/ceec.sqlite3", "ledger/artifacts") as store:
    artifact = store.ingest_artifact(b"results", "blob")
    scope = models.Scope(domain="credit", credit=("gradient",))
    evidence = store.record_evidence(kind="vector", scope=scope,
        artifact_refs=[artifact.id], axes=["acc"], values_ref=artifact.id)
    findings = run_audit(store)  # [] means clean
```

## Validated scope

CEEC-Core semantics are the ones exercised by the internal Computronium
ledger (single-writer SQLite, quick-budget probes, 2026-09 ledger at 26+
evidence records, audit clean). No concurrent-writer hardening; no network
or multi-process guarantees.

## Known limitations

- Single-process, single-writer SQLite (`_next_id` is not concurrency-safe).
- Hard-constraint validation is a generic interface (`ceec.constraints`);
  project-specific constraints must be supplied by the caller.
- No CLI daemon or server; commands are one-shot.

## Evidence references

Internal ledger: `computronium` repo `ceec/ceec.sqlite3` (E-000001..E-000026);
gate semantics tested in `tests/test_gates.py`; audit checks in
`computronium/ceec/audit.py` (identical extraction).

## Verification level

Unit-tested + quickstart regression; semantics parity with the internal
CEEC enforced by `tests/platform/test_ceec_core_compat.py` in the parent repo.

## Dependencies

Python standard library + `pydantic` (validation at the I/O boundary).
The TODO20 plan nominally specifies stdlib-only; pydantic v2 is a documented
deviation chosen over rewriting validated models.