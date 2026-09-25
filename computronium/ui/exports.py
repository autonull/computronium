"""Dashboard exports (§4.7 minimal) — pure bytes builders for downloads.

CSV of plotted cells and standalone HTML of Plotly figures. Both are
dependency-free (stdlib csv, plotly ``write_html``); PNG/SVG waits on a
kaleido-class renderer and stays a follow-up.
"""

from __future__ import annotations

import csv
import io
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plotly.graph_objects import Figure as go_Figure

    from computronium.ui.adapters import ObjectiveExplorerData


def explorer_csv(data: ObjectiveExplorerData) -> bytes:
    """Cells CSV: one row per plotted cell, one column per axis."""
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["cell_key", *data.axes, "pareto"])
    for index, key in enumerate(data.cell_keys):
        writer.writerow([
            key,
            *(f"{column[index]:.6g}" for column in data.columns),
            "1" if data.pareto_mask[index] else "0",
        ])
    return buffer.getvalue().encode("utf-8")


def figure_html(fig: go_Figure) -> bytes:
    """Standalone HTML for a Plotly figure (no server needed to view)."""
    return fig.to_html(full_html=True, include_plotlyjs="cdn").encode("utf-8")
