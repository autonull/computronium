"""Gate commands: predicates the repository evaluates, never prose.

A gate's acceptance is its exit code. ``comp gate breadth`` is the AGENTS
breadth exit: every error-aware credit holds a legal, above-chance L2/n>=5 cell
on at least two task families. A credit below two families is red: the exit
names it, and the plan files the row that would measure it.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from computronium.experiment.evidence.breadth import BreadthGate

__all__ = ["_cmd_gate"]


def _cmd_gate(args) -> int:
    """Dispatch a gate subcommand and return its exit code."""
    if args.gate_command == "breadth":
        return _cmd_breadth(args)
    return 2


def _breadth_corpus(root: Path):
    """Every read record, plus the stores the corpus could not read."""
    from computronium.experiment.evidence.corpus import default_store_paths
    from computronium.experiment.evidence.store import RecordStore, StoreConfig

    records = []
    unreadable: list[tuple[str, str]] = []
    for path in default_store_paths(root):
        try:
            with RecordStore(StoreConfig(path=path, read_only=True)) as store:
                records.extend(store.query_records())
        except Exception as exc:  # ruff: ignore[blind-except] - data boundary
            unreadable.append((path.name, str(exc)))
    return records, unreadable


def _breadth_payload(gate: BreadthGate, unreadable: list[tuple[str, str]]) -> dict:
    """The gate as JSON: one row per credit and its families."""
    return {
        "green": gate.green,
        "credits": [
            {
                "credit": row.credit,
                "families": dict(row.families),
                "keys": row.keys,
                "green": row.green,
            }
            for row in gate.credits
        ],
        "failing": list(gate.failing),
        "assessed_legacy": gate.assessed_legacy,
        "excluded_unbarred": gate.excluded_unbarred,
        "excluded_refused": gate.excluded_refused,
        "unreadable": dict(unreadable),
    }


def _breadth_verdict(row) -> str:
    """One row's verdict: measured on two families, or failing."""
    return "PASS" if row.green else "FAIL (needs another family)"


def _render_breadth(gate: BreadthGate, unreadable: list[tuple[str, str]]) -> None:
    """The text report: the table and the exclusions."""
    print(
        "Breadth exit (AGENTS): every error-aware credit needs >=2 task families\n"
        "with a legal, bar-cleared L2/n>=5 measurement. Family = a family the\n"
        "task declares (TaskSpecEnriched.task_families)."
    )
    print(f"{'credit':24} {'families':44} {'keys':>5}  verdict")
    for row in gate.credits:
        families = ", ".join(name for name, _ in row.families) or "-"
        print(f"{row.credit:24} {families:44} {row.keys:>5}  {_breadth_verdict(row)}")
    print(
        f"assessed: {gate.assessed_legacy} legacy records against their task bar; "
        f"excluded: {gate.excluded_unbarred} unbarred/below-bar, "
        f"{gate.excluded_refused} refused cells"
    )
    if unreadable:
        print(f"unreadable stores: {len(unreadable)}")
        for name, reason in unreadable:
            print(f"  {name}: {reason}")
    if gate.green:
        print(f"gate: PASS ({len(gate.credits)} error-aware credits)")
        return
    print(
        f"gate: FAIL ({len(gate.failing)} of {len(gate.credits)} credits below "
        f"2 families: {', '.join(gate.failing)})"
    )


def _cmd_breadth(args) -> int:
    """Evaluate the AGENTS breadth exit over the corpus."""
    from computronium.experiment.evidence.breadth import breadth_gate
    from computronium.experiment.registry.task_registry import (
        TaskRegistry,
        primary_pass_bar,
    )

    registry = TaskRegistry()
    records, unreadable = _breadth_corpus(Path(args.root))
    gate = breadth_gate(
        records,
        lambda task: registry.get(task).task_families,
        lambda task: primary_pass_bar(registry.get(task)),
    )
    if args.format == "json":
        print(json.dumps(_breadth_payload(gate, unreadable), indent=2))
    else:
        _render_breadth(gate, unreadable)
    return 0 if gate.green else 1
