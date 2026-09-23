"""Row virtualization caps (D2): unbounded table paths render at most
MAX_RENDERED_ROWS rows plus a "showing first" caption (UX-L4 key)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def test_discovery_map_table_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    from nicegui import ui

    from computronium.ui.components.discovery_map import (
        MAX_RENDERED_ROWS,
        DiscoveryMap,
        MapSpecimen,
    )

    captured: list[int] = []
    real_table = ui.table

    def _spy(*, rows: list | None = None, **kwargs: object) -> object:
        captured.append(len(rows or []))
        return real_table(rows=rows, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(ui, "table", _spy)

    specimens = [
        MapSpecimen(
            key=f"k{i}",
            x=0.1,
            y=0.2,
            dynamics="energy_minimization",
            credit="prediction",
            update="euclidean",
            topology="feedforward",
            accuracy=0.5,
            bp_deficit=0.1,
            outcome="learned",
        )
        for i in range(MAX_RENDERED_ROWS + 500)
    ]
    panel = DiscoveryMap(specimens=specimens)
    panel._show_table = True
    panel.render()

    assert captured, "ui.table rendered"
    assert captured[-1] == MAX_RENDERED_ROWS
    assert len(panel._table_rows()) == MAX_RENDERED_ROWS


def test_repair_bench_rows_capped(monkeypatch: pytest.MonkeyPatch) -> None:
    from computronium.ui.components.repair_bench import (
        MAX_RENDERED_ROWS,
        DefectRow,
        RepairBench,
    )

    rendered: list[str] = []
    original = RepairBench._render_defect_row

    def _spy(self: RepairBench, row: DefectRow) -> None:
        rendered.append(row.defect_id)
        original(self, row)

    monkeypatch.setattr(RepairBench, "_render_defect_row", _spy)

    rows = [
        DefectRow(
            defect_id=f"d{i}",
            count=1,
            cells=1,
            status="open",
            error_class="RuntimeError",
            last_seen=float(i),
            message="boom",
        )
        for i in range(MAX_RENDERED_ROWS + 500)
    ]
    RepairBench(rows=rows).render()

    assert len(rendered) == MAX_RENDERED_ROWS


def test_showing_first_glossary_key_exists() -> None:
    from computronium.ui.glossary_service import get_glossary_service

    service = get_glossary_service()
    assert service.has("showing_first")
    explorer, lab = service.get_both("showing_first")
    assert explorer and lab and explorer != "showing_first"
