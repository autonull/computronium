"""Gate commands: predicates the repository evaluates, never prose.

A gate's acceptance is its exit code. ``comp gate breadth`` is the AGENTS
breadth exit: every error-aware credit holds a legal, above-chance L2/n>=5 cell
on at least two task families.
"""

from __future__ import annotations

import json
from pathlib import Path

__all__ = ["_cmd_gate"]


def _cmd_gate(args) -> int:
    """Dispatch a gate subcommand and return its exit code."""
    if args.gate_command == "breadth":
        return _cmd_breadth(args)
    return 2


def _cmd_breadth(args) -> int:
    """Evaluate the AGENTS breadth exit over the corpus."""
    from computronium.experiment.evidence.breadth import breadth_gate
    from computronium.experiment.evidence.corpus import default_store_paths
    from computronium.experiment.evidence.store import RecordStore, StoreConfig
    from computronium.experiment.registry.task_registry import (
        TaskRegistry,
        primary_pass_bar,
    )

    root = Path(args.root)
    registry = TaskRegistry()

    def family_of(task: str) -> str:
        return registry.get(task).domain.value

    def bar_of(task: str):
        return primary_pass_bar(registry.get(task))

    records = []
    unreadable: list[tuple[str, str]] = []
    for path in default_store_paths(root):
        try:
            with RecordStore(StoreConfig(path=path, read_only=True)) as store:
                records.extend(store.query_records())
        except Exception as exc:  # ruff: ignore[blind-except] - data boundary
            unreadable.append((path.name, str(exc)))

    gate = breadth_gate(records, family_of, bar_of)
    failing = [row.credit for row in gate.credits if not row.green]

    if args.format == "json":
        print(
            json.dumps(
                {
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
                    "assessed_legacy": gate.assessed_legacy,
                    "excluded_unbarred": gate.excluded_unbarred,
                    "excluded_refused": gate.excluded_refused,
                    "unreadable": dict(unreadable),
                },
                indent=2,
            )
        )
        return 0 if gate.green else 1

    print(
        "Breadth exit (AGENTS): every error-aware credit needs >=2 task families\n"
        "with a legal, bar-cleared L2/n>=5 measurement. Family = registered "
        "task domain."
    )
    print(f"{'credit':24} {'families':44} {'keys':>5}  verdict")
    for row in gate.credits:
        families = ", ".join(name for name, _ in row.families) or "-"
        verdict = "PASS" if row.green else "FAIL (needs another family)"
        print(f"{row.credit:24} {families:44} {row.keys:>5}  {verdict}")
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
    else:
        print(
            f"gate: FAIL ({len(failing)} of {len(gate.credits)} credits below "
            f"2 families: {', '.join(failing)})"
        )
    return 0 if gate.green else 1
