"""Command Palette — ⌘K search for panels, lenses, and actions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nicegui import ui

if TYPE_CHECKING:
    from collections.abc import Callable

from computronium.ui.lenses import PanelLenses


def _build_palette_items(current_panel: str) -> list[dict[str, str]]:
    """Build searchable palette items."""
    items: list[dict[str, str]] = []

    panel_items = {
        PanelLenses.MAP: ("Map", "Explore & compare (UMAP, Pareto, Gallery)"),
        PanelLenses.REPAIR: ("Repair", "Fix & mature (Defects, Maturation)"),
        PanelLenses.CONSOLE: ("Console", "Run & monitor (live stream, controls)"),
        PanelLenses.COMPOSER: ("Composer", "Build (recipes, dial composer)"),
        PanelLenses.RECORD: ("Record", "Trust & remember (History, Ledger, Lessons)"),
    }

    for idx, (key, (label, desc)) in enumerate(panel_items.items(), 1):
        items.append({
            "id": f"panel:{key}",
            "title": label,
            "subtitle": desc,
            "category": "Panel",
            "keys": str(idx),
        })

    lens_map = {
        PanelLenses.MAP: [
            ("map:map", "Map", "UMAP scatter with region labels"),
            ("map:tradeoffs", "Trade-offs", "Pareto front with objective selector"),
            ("map:gallery", "Gallery", "Figure cards with thumbnails"),
        ],
        PanelLenses.REPAIR: [
            ("repair:defects", "Defects", "Defect funnel table with copy commands"),
            ("repair:maturation", "Maturation", "Campaign → maturity → cells tree"),
        ],
        PanelLenses.RECORD: [
            ("record:history", "History", "Timeline of milestones and cells"),
            ("record:ledger", "Ledger", "Experiment → belief → evidence chains"),
            ("record:lessons", "Lessons", "Negative results, one-line summaries"),
        ],
    }

    if current_panel in lens_map:
        for link, label, desc in lens_map[current_panel]:
            items.append({
                "id": f"lens:{link}",
                "title": label,
                "subtitle": desc,
                "category": "Lens",
            })

    actions = [
        ("refresh", "Refresh", "Reload all panels from artifacts"),
        ("atlas", "Refit Atlas", "Recompute UMAP embedding"),
        ("quiet", "Toggle Quiet", "Compact text-only status chip"),
    ]
    for action_id, label, desc in actions:
        items.append({
            "id": f"action:{action_id}",
            "title": label,
            "subtitle": desc,
            "category": "Action",
        })

    return items


def _category_icon(cat: str) -> str:
    return {
        "Panel": "dashboard",
        "Lens": "zoom_out_map",
        "Action": "flash_on",
    }.get(cat, "help")


def _render_palette_results(
    results_container: ui.column,
    items: list[dict[str, str]],
    query: str,
    on_select: Callable[[str], None],
    dialog: ui.dialog,
) -> None:
    results_container.clear()
    q = query.lower()
    with results_container:
        for item in items:
            haystack = f"{item['title']} {item['subtitle']} {item['category']}".lower()
            if q and q not in haystack:
                continue
            with ui.item(
                on_click=lambda _, i=item: _select_item(i, on_select, dialog)
            ).classes("w-full cursor-pointer"):
                with ui.item_section().props("avatar"):
                    ui.icon(_category_icon(item["category"]))
                with ui.item_section():
                    ui.item_label(item["title"])
                    ui.item_label(item["subtitle"]).props("caption")
                with ui.item_section().props("side"):
                    if item.get("keys"):
                        ui.label(f"⌘{item['keys']}").classes("text-caption text-grey")


def _select_item(
    item: dict[str, str],
    on_select: Callable[[str], None],
    dialog: ui.dialog,
) -> None:
    dialog.close()
    on_select(item["id"])


def open_palette(
    *,
    current_panel: str,
    current_lens: str,
    on_select: Callable[[str], None],
) -> None:
    """Open the command palette dialog."""
    items = _build_palette_items(current_panel)

    dialog = ui.dialog().props("wide persistent")
    with dialog, ui.card().classes("w-full max-w-2xl"):
        ui.label("Command Palette").classes("text-h6 mb-2")
        ui.label(
            "⌘K to open • Type to search • Enter to select • Esc to close"
        ).classes("text-caption text-grey mb-4")

        search = (
            ui
            .input(placeholder="Search panels, lenses, actions…")
            .props("dense outlined autofocus")
            .classes("w-full mb-4")
        )

        results_container = ui.column().classes("w-full max-h-96 overflow-auto")

        search.on_value_change(
            lambda e: _render_palette_results(
                results_container, items, e.value or "", on_select, dialog
            )
        )
        _render_palette_results(results_container, items, "", on_select, dialog)

        def _on_key(e: Any) -> None:
            if e.key == "Escape":
                dialog.close()
            elif e.key == "Enter":
                pass

        dialog.on("keydown", _on_key)
        dialog.open()


__all__ = ["open_palette"]
