"""Render the SEC map document from ``map.json`` (TODO95 P5).

The document is a projection of the map, never a second tally: every row, its
status, box, ruler, control and replay hash come from the one artifact. The
method cards are the same rows, and the extension recipe is the check a stranger
runs — ``comp verify`` — so the document cannot disagree with the screen.

Run:
    uv run python -m computronium.experiment.documentation.sec_map \
        --map results/sec/map.json --out docs/sec/map.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any, Final

from computronium.experiment.sec_census import MAP_VERSION

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = ["render_map", "write_map_document"]

_STATUS_COLUMNS: Final[tuple[str, ...]] = (
    "measured",
    "defect",
    "refused",
    "unmeasured",
)


def _val_acc(row: Mapping[str, Any]) -> float | None:
    value = (row.get("measurement") or {}).get("val_acc")
    return None if value is None else float(value)


def _resource(row: Mapping[str, Any], key: str) -> Any:
    return (row.get("resource") or {}).get(key)


def _number(value: Any, digits: int = 4) -> str:
    """A number at the ruler's resolution, or an em dash when unmeasured."""
    return "—" if value is None else f"{float(value):.{digits}f}"


def _short(value: Any, width: int = 12) -> str:
    if value is None:
        return "—"
    text = str(value)
    return text if len(text) <= width else f"{text[:width]}…"


def _base_line(map_data: Mapping[str, Any]) -> str:
    base = map_data.get("base") or {}
    inventory = map_data.get("inventory") or {}
    parts = [
        str(base.get("task", "—")),
        f"{base.get('batch_size', '—')} samples/step",
        f"{base.get('batch_limit', '—')} batches",
        f"{base.get('epochs', '—')} epoch",
        f"{base.get('param_budget', '—')} ceiling",
        f"control {_number(inventory.get('control_val_acc'))}",
        f"bar {_number(inventory.get('bar'))}",
    ]
    return " · ".join(parts)


def _rows(map_data: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = list((map_data.get("primitives") or {}).values())
    return sorted(
        rows, key=lambda row: (str(row.get("axis")), str(row.get("primitive")))
    )


def _inventory_table(map_data: Mapping[str, Any]) -> list[str]:
    inventory = map_data.get("inventory") or {}
    totals: dict[str, int] = {status: 0 for status in _STATUS_COLUMNS}
    by_axis: dict[str, dict[str, int]] = {}
    for row in _rows(map_data):
        status = str(row.get("status"))
        totals[status] = totals.get(status, 0) + 1
        counts = by_axis.setdefault(str(row.get("axis")), {})
        counts[status] = counts.get(status, 0) + 1
    lines = [
        "| axis | " + " | ".join(_STATUS_COLUMNS) + " |",
        "|---|" + "---|" * len(_STATUS_COLUMNS),
    ]
    for axis, counts in sorted(by_axis.items()):
        cells = " | ".join(str(counts.get(status, 0)) for status in _STATUS_COLUMNS)
        lines.append(f"| {axis} | {cells} |")
    cells = " | ".join(str(totals.get(status, 0)) for status in _STATUS_COLUMNS)
    lines.append(f"| **total {inventory.get('total')}** | {cells} |")
    return lines


def _census_table(map_data: Mapping[str, Any]) -> list[str]:
    lines = [
        "| primitive | status | binding | task | val_acc | seconds | replay |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in _rows(map_data):
        val_acc = _val_acc(row)
        lines.append(
            "| {primitive} | {status} | {binding} | {task} | {val_acc} | "
            "{seconds} | {replay} |".format(
                primitive=row.get("primitive"),
                status=row.get("status"),
                binding=row.get("binding") or "—",
                task=row.get("task") or "—",
                val_acc="—" if val_acc is None else f"{val_acc:.4f}",
                seconds=_short(_resource(row, "walltime_s"), 6),
                replay=_short(row.get("replay_hash"), 12),
            )
        )
    return lines


def _notes(map_data: Mapping[str, Any]) -> list[str]:
    lines: list[str] = []
    defects = [row for row in _rows(map_data) if row.get("status") == "defect"]
    if defects:
        lines.append("### Defects (execution facts, with their mechanism)")
        for row in defects:
            lines.append(f"- `{row.get('primitive')}` — {row.get('defect') or '—'}")
    refused = [row for row in _rows(map_data) if row.get("status") == "refused"]
    if refused:
        lines.append("")
        lines.append("### Refused (rule and reopen trigger)")
        for row in refused:
            lines.append(f"- `{row.get('primitive')}` — {row.get('trigger') or '—'}")
    return lines


def _interaction(map_data: Mapping[str, Any]) -> list[str]:
    layer = map_data.get("interaction")
    if not layer:
        return ["The interaction slice is not measured at this box."]
    lines = [
        f"Pair: **{' × '.join(layer.get('pair') or [])}** — "
        f"status={layer.get('status')}",
        "",
        f"- levels: {layer.get('levels')}",
        f"- control val_acc: {_number(layer.get('control_val_acc'))}",
    ]
    effect = layer.get("effect")
    if effect is None:
        lines.append(f"- effect: none ({layer.get('stop_reason')})")
    elif effect.get("lower") is None:
        lines.append(f"- effect: {effect['effect']:.4f} (no interval, one seed)")
    else:
        lines.append(
            f"- effect: {effect['effect']:.4f} "
            f"[{effect['lower']:.4f}, {effect['upper']:.4f}] "
            f"at {effect['seeds']} seeds — a difference in differences"
        )
    return lines


def _deep_dive(map_data: Mapping[str, Any]) -> list[str]:
    layer = map_data.get("deep_dive")
    if not layer:
        return ["The deep dive is not measured at this box."]
    candidate = layer["candidate"]
    claim = layer.get("claim") or {}
    lines = [
        f"Primitive: **{candidate['primitive']}** — verdict={layer['verdict']}",
        "",
        f"- margin over the bar: {candidate['margin']:.4f} "
        f"(val_acc {candidate['val_acc']:.4f})",
        f"- knob: `{candidate['knob']}` at its declared default "
        f"{candidate['default']:g}",
        f"- knob binds: {layer.get('knob_binds')}; "
        f"pair has power: {not layer.get('no_power', False)}",
        f"- claim: {claim.get('claim', '—')}",
        f"- margin {claim.get('threshold')}, alpha {claim.get('alpha')}, "
        f"fixed n={claim.get('min_seeds')}",
        "",
        "| factor | knob value | status | val_acc | seconds |",
        "|---|---|---|---|---|",
    ]
    for rung in layer.get("ladder") or []:
        lines.append(
            f"| {rung['factor']:g}× | {rung['value']:g} | {rung['status']} | "
            f"{rung['val_acc']} | {_short(rung.get('walltime_s'), 6)} |"
        )
    effect = layer.get("effect")
    if effect is not None:
        lines += [
            "",
            f"Paired: {effect['mean_diff']:.4f} "
            f"[{effect['ci_lower']:.4f}, {effect['ci_upper']:.4f}] "
            f"at {effect['n']} paired seeds, p={effect['p_value']:.4f}, "
            f"dz={effect['cohens_dz']:.2f}",
        ]
    lines += ["", f"Stop: {layer.get('stop_reason')}."]
    return lines


def render_map(map_data: Mapping[str, Any]) -> str:
    """The document, projected from the map and nothing else."""
    inventory = map_data.get("inventory") or {}
    lines = [
        "# SEC map — the census of learning primitives",
        "",
        f"Version {MAP_VERSION}, updated {map_data.get('updated', '—')}. "
        f"{inventory.get('total')} primitives, {inventory.get('available')} "
        "available, all rows at one base box:",
        "",
        f"`{_base_line(map_data)}`",
        "",
        "Generated from `results/sec/map.json`; regenerate with "
        "`uv run python -m computronium.experiment.documentation.sec_map "
        "--map results/sec/map.json --out docs/sec/map.md`. Do not edit by hand.",
        "",
        "## Inventory",
        "",
        *_inventory_table(map_data),
        "",
        "## Census (the method cards)",
        "",
        "Each row is a method card: its box, ruler, control, number and replay",
        "hash. A card is a result only when its row is measured.",
        "",
        *_census_table(map_data),
        "",
        *_notes(map_data),
        "",
        "## Interaction (which axes change together)",
        "",
        *_interaction(map_data),
        "",
        "## Deep dive (one surprising row, one box)",
        "",
        *_deep_dive(map_data),
        "",
        "## Adding a primitive (the recipe)",
        "",
        "1. Declare the axis spec in its `primitives/<axis>/spec.py`; the "
        "registry derives from the specs, never a second list.",
        "2. Add the config classmethod on the axis's config class.",
        "3. Export it from the root `__all__`/`_LAZY` and "
        "`ontology/__init__.py`; the wiring lock proves the four surfaces agree.",
        "4. Declare the binding condition in `sec_binding.py`: an axis that "
        "does not bind is `inert`, not a result.",
        "5. Run `uv run python -m computronium.experiment.sec_census --out "
        "results/sec`, then `comp verify --primitive <id> --slice <family>`; "
        "a row without its box, ruler, control or replay hash is refused.",
        "",
        "The recipe is a test: `tests/acceptance/test_extension_path.py` adds "
        "a credit and holds a map row end to end.",
        "",
    ]
    return "\n".join(lines)


def write_map_document(map_path: Path, out_path: Path) -> Path:
    """Render the map document from ``map_path`` at ``out_path``."""
    map_data = json.loads(map_path.read_text(encoding="utf-8"))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_map(map_data), encoding="utf-8")
    return out_path


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Render the SEC map document")
    parser.add_argument(
        "--map", type=Path, default=Path("results/sec/map.json"), help="Map document"
    )
    parser.add_argument(
        "--out", type=Path, default=Path("docs/sec/map.md"), help="Markdown output"
    )
    args = parser.parse_args()
    path = write_map_document(args.map, args.out)
    print(f"Map document: {path}")


if __name__ == "__main__":
    main()
